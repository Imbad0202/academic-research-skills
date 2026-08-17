#!/usr/bin/env python3
"""Pin Schema 13.2 role-scoped reviewer delivery surfaces.

Threat model: accidental well-intentioned drift. Adversarial repository editors
are out of scope because they can edit this lint too. Witnesses are hardcoded
and parent-bound to the sprint-delivered Phase 1/Phase 2 subsections.

Exit 0 pass / 1 drift / 2 missing input.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from _skill_lint import heading_section, norm_ws, read_or_exit2
from check_panel_synthesis import ReportError, validate_evidence_anchor

REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = {
    "shared/contracts/reviewer/full.json": {
        "D1": (["methodology"], "methodology"),
        "D2": (["domain"], "domain"),
        "D3": (["da", "methodology"], "da"),
        "D4": (["perspective"], "perspective"),
        "D5": (["eic"], "eic"),
        "D6": (["eic"], "eic"),
    },
    "shared/contracts/reviewer/methodology_focus.json": {
        "D1": (["methodology"], "methodology"),
        "D2": (["eic"], "eic"),
    },
}
AGENTS = {
    "academic-paper-reviewer/agents/eic_agent.md": "eic",
    "academic-paper-reviewer/agents/methodology_reviewer_agent.md": "methodology",
    "academic-paper-reviewer/agents/domain_reviewer_agent.md": "domain",
    "academic-paper-reviewer/agents/perspective_reviewer_agent.md": "perspective",
    "academic-paper-reviewer/agents/devils_advocate_reviewer_agent.md": "da",
}
PROTOCOL = "academic-paper-reviewer/references/sprint_contract_protocol.md"
SYNTH = "academic-paper-reviewer/agents/editorial_synthesizer_agent.md"
PANEL_CHECKER = "scripts/check_panel_synthesis.py"
PHASE_CHECKER = "scripts/check_phase_conformance.py"
TEMPLATE = "academic-paper-reviewer/templates/peer_review_report_template.md"
SHIPPED_EXAMPLES = (
    "academic-paper-reviewer/examples/subclaim_decomposition_example.md",
    "academic-paper-reviewer/examples/hei_paper_review_example.md",
    "academic-paper-reviewer/examples/interdisciplinary_review_example.md",
)
SHIPPED_EXAMPLE_ANCHOR_COUNTS = {
    SHIPPED_EXAMPLES[0]: 10,
    SHIPPED_EXAMPLES[1]: 38,
    SHIPPED_EXAMPLES[2]: 38,
}
SHIPPED_EXAMPLE_ANCHOR_RE = re.compile(
    r"`(?P<anchor>(?:text|table|figure|equation|dataset|absence): [^`\n]+)`",
    re.IGNORECASE,
)
TEMPLATE_EXAMPLE_ANCHOR_COUNT = 3
TEMPLATE_EXAMPLE_ANCHOR_TYPES = ("text", "table", "absence")
TEMPLATE_EXAMPLE_ANCHOR_RE = re.compile(
    r"^Evidence Anchor: "
    r"(?P<anchor>(?:text|table|figure|equation|dataset|absence): \S.*)$",
    re.IGNORECASE | re.MULTILINE,
)
SPRINT = "## v3.6.2 Sprint Contract Protocol"
PHASE1 = "### Phase 1 — Paper-content-blind pre-commitment"
PHASE2 = "### Phase 2 — Paper-visible review"
PHASE1_FIELDS = (
    "`dimension_id: <Dn>`",
    "`what_to_look_for: <single-line non-empty text>`",
    "`what_triggers_block: <single-line non-empty text>`",
    "`what_triggers_warn: <single-line non-empty text>`",
    "`what_triggers_fatal: <single-line non-empty text>`",
)
PHASE1_LIVE_GRAMMAR_WITNESS = (
    "For every scoring-plan heading, copy the exact dimension ID and name from "
    "the contract. For a non-mandatory dimension, omit the entire "
    "`what_triggers_fatal:` line; never emit that key with `NOT_APPLICABLE`, "
    "`none`, or any other sentinel"
)
PHASE1_TERMINAL_PREFLIGHT_WITNESS = (
    "Terminal Phase 1 structural preflight (mandatory). Silently inspect the "
    "exact text you are about to send: "
    "1. The only H2 sections are exactly one `## Contract Paraphrase` followed "
    "by exactly one `## Scoring Plan`. The paraphrase meets "
    "`measurement_procedure.paraphrase_minimum_dimensions`: `\"all\"` means "
    "one paragraph per contract dimension; integer `k` means at least `k` "
    "paragraphs tied to distinct dimensions. "
    "2. Every `### <Dn>: <name>` heading copies the contract ID and name "
    "exactly, and only dimensions eligible for your dispatch role appear. "
    "3. Each scoring-plan subsection contains exactly one unbulleted "
    "`dimension_id:`, `what_to_look_for:`, `what_triggers_block:`, and "
    "`what_triggers_warn:` line; its block and warn texts are distinct. "
    "4. In every non-mandatory subsection, the literal key "
    "`what_triggers_fatal:` occurs zero times; delete the entire line and any "
    "sentinel if it appears. In every mandatory subsection, that key occurs "
    "exactly once and its text is distinct from block and warn. "
    "5. No `## Dimension Scores`, `## Review Body`, "
    "`## Failure Condition Checks`, `## Editorial Decision`, "
    "`dimension_scores`, `review_body`, or bare `editorial_decision=` "
    "appears, and no manuscript-specific claim appears. "
    "6. Binding: a criteria-aware call contains exactly the supplied marker "
    "and one `criteria_parallel_conflicts:` line matching the brief; an "
    "unbound call contains exactly `criteria_binding_unavailable`. Neither "
    "form states manuscript applicability. "
    "7. The final nonblank output line is exactly "
    "`[CONTRACT-ACKNOWLEDGED]`. "
    "Do not send until every check holds."
)
PHASE2_WITNESSES = (
    "`dimension_id: <Dn>` and `rationale: <nonempty explanation>`",
    "score: <block|warn|pass|not_assessed>",
    "abstain_reason: <one line>",
    'trigger: "<verbatim substring of the matching Phase 1 trigger>"',
    "block_class: <fatal|repairable>",
    "Do not emit `## Failure Condition Checks`, `## Editorial Decision`",
)
PHASE2_NO_DISSENT_WITNESS = (
    "If no dimension needs dissent, omit the entire `## Scoring Plan Dissent` "
    "section; never emit an empty section or a `none` placeholder"
)
PHASE2_TERMINAL_PREFLIGHT_WITNESS = (
    "Terminal Phase 2 structural preflight (mandatory). Silently inspect the "
    "exact text you are about to send against your supplied Phase 1: "
    "1. Dissent: if your Phase 2 view differs on exactly one dimension, "
    "include `## Scoring Plan Dissent` with exactly one unbulleted "
    "`dimension_id: <Dn>` line and exactly one unbulleted "
    "`rationale: <nonempty explanation>` line. If it differs on two or more, "
    "abort with `[PROTOCOL-VIOLATION: multi_dissent=true]` instead of drafting "
    "a card. If none differs, delete the heading and every placeholder beneath "
    "it; `none`, `omitted`, and `not applicable` are never a dissent. "
    "No bare `<!--` or `-->` — nor any other raw HTML — anywhere in the card "
    "outside inline code. "
    "2. Sections and role: emit exactly one `## Dimension Scores` followed by "
    "exactly one `## Review Body`. Put exactly one report-level "
    "`contract_role: <your dispatch role>` immediately before "
    "`## Dimension Scores` and nowhere else. Delete "
    "`## Failure Condition Checks`, `## Editorial Decision`, and every bare "
    "`editorial_decision=` line. "
    "3. Dimensions and abstentions: emit every contract dimension exactly "
    "once with its exact ID/name. An eligible dimension uses `block`, `warn`, "
    "`pass`, or `not_assessed`; eligible `not_assessed` has exactly one "
    "non-empty `abstain_reason:`, while an ineligible dimension uses only "
    "`score: not_assessed` with no `abstain_reason:`. No other score carries "
    "`abstain_reason:`. "
    "4. Trigger binding: for every `warn` or `block`, the quoted `trigger:` "
    "text is a character-for-character substring of the matching Phase 1 "
    "trigger kind for the same dimension. Never paraphrase it. `pass` and "
    "`not_assessed` have no `trigger:`. "
    "5. Fatality: every mandatory `block` has exactly one `block_class:`; "
    "`fatal` binds to the Phase 1 fatal trigger, a dissented dimension cannot "
    "be fatal, and a non-mandatory dimension has no `block_class:`. "
    "6. Finding grammar: apply the role-specific grammar above. For a scoring "
    "seat, every weakness is its own `### W<n>` subsection with exactly one "
    "parseable Severity, one typed Evidence Anchor, and one Confidence; every "
    "strength has a typed Evidence Anchor and no Severity. If either finding "
    "polarity is empty, include its required Coverage Receipt. For the DA, "
    "emit exactly one `#### CRITICAL` table and one `#### MAJOR` table, both "
    "present even when empty, with no standalone Severity. Each table header "
    "contains exactly one column named `#` and exactly one named "
    "`Evidence Anchor`; every row is outer-pipe-delimited with the header's "
    "column count, and CRITICAL IDs are unique and dense `C1..Cn`. For the "
    "DA, these tables are the terminal suffix of `## Review Body`: put every "
    "prose paragraph before `#### CRITICAL`; after the CRITICAL table emit "
    "only blank lines until `#### MAJOR`, and after the MAJOR table emit only "
    "blank lines to the end of Review Body. Do not emit HTML comments anywhere "
    "in a DA report. "
    "7. Anchors: no findings share an anchor. Every anchor uses a valid typed "
    "`<type>: <locator>` value with balanced wrappers. Every `text:` anchor "
    "contains at least one balanced quoted verbatim excerpt, and each quoted "
    "excerpt is at most 25 words. Every `absence:` anchor uses the exact "
    "required separators and non-empty fields. "
    "8. Bands: assign each weakness by its own decision impact, never by a "
    "target distribution or bundled cluster; a Critical is singleton "
    "rejection-level. Do not send until every check holds."
)
PHASE2_ROLE_PLACEMENT_WITNESS_SUFFIX = (
    "Place this single report-level line immediately before "
    "`## Dimension Scores`; never repeat it inside any dimension subsection"
)
SCORING_FINDING_WITNESS = (
    "each finding with a Severity has its own `### W<n>: <title>` subsection, "
    "exactly one `**Severity**:` line, and its own `**Evidence Anchor**:` line "
    "when Critical or Major. Findings never share an anchor"
)
SCORING_STRENGTH_SEVERITY_WITNESS = (
    "Strength subsections never carry a `**Severity**:` field or a "
    "`Severity: Strength` sentinel; Severity is weakness-only"
)
SCORING_FIELD_VARIANT_WITNESS = (
    "Finding fields may be unindented or Markdown-list-indented, and may be "
    "separate lines or pipe-delimited on one line. The complete typed anchor "
    "value, including its type and locator, may be bare, backtick-wrapped, or "
    "square-bracketed; these presentation variants do not weaken the "
    "one-finding/one-Severity/one-anchor gate"
)
ANCHOR_VALUE_GRAMMAR_WITNESS = (
    "Every Evidence Anchor value begins with the literal `<type>: <locator>` "
    "grammar. An opening backtick or `[` immediately before `<type>` starts an "
    "outer wrapper and requires its matching closer; nothing may appear "
    "between the type and its colon, so `` `text`: §3 `` and `` `text` — §3 `` "
    "are both invalid. Wrapper-like characters inside a locator are content "
    "and must be locally balanced — a bracketed locator such as "
    "`equation: Eq. [3]` and a locator naming inline code such as "
    "``text: §3 \"quote\" per `df``` are valid. A `text:` anchor contains one "
    "or more verbatim excerpts, each inside a balanced pair of straight or "
    "curly double quotes, and every quoted excerpt is at most 25 words. Before "
    "output, confirm at least one quoted excerpt exists, count each quoted "
    "excerpt in a `text:` anchor, and shorten any excerpt over 25 words; never "
    "place commentary inside the quotation. An `absence:` anchor uses the "
    "exact grammar "
    "`absence: <where> — expected <item>; checked <surfaces>`, including the "
    "literal single space after the semicolon and non-empty content for every "
    "placeholder. The reserved ` — expected ` and `; checked ` separator "
    "sequences each occur exactly once"
)
PROTOCOL_PHASE1_LIVE_WITNESSES = (
    "Copy each dimension ID and name exactly from the contract",
    "For a non-mandatory dimension, omit the entire `what_triggers_fatal:` "
    "line; never emit that key with `NOT_APPLICABLE`, `none`, or another "
    "sentinel",
)
PROTOCOL_PHASE2_LIVE_WITNESSES = (
    "`## Scoring Plan Dissent` is optional only when a dimension actually "
    "dissents; when there is no dissent, omit the whole section rather than "
    "emitting an empty or `none` placeholder",
    "Each report declares its dispatch role exactly once on one "
    "`contract_role: <role>` line immediately before `## Dimension Scores`; "
    "never repeat that report-level line inside dimension subsections",
    "Strength subsections never carry a `Severity` field or a "
    "`Severity: Strength` sentinel",
)
PROTOCOL_DA_TABLE_GATE_WITNESS = (
    "The two tables are the terminal suffix of `## Review Body`: every prose "
    "paragraph precedes `#### CRITICAL`; only blank lines may separate the end "
    "of CRITICAL from `#### MAJOR` or follow MAJOR to the end of Review Body. "
    "DA reports may not contain HTML comments"
)
TEMPLATE_STRENGTH_SEVERITY_WITNESS = (
    "Omit the Severity field entirely — never emit `Severity: Strength`; "
    "Severity is weakness-only"
)
ANCHOR_VALIDATOR_REGEX_WITNESS = (
    r'r"^(?P<type>text|table|figure|equation|dataset|absence):\s*"' "\n"
    r'        r"(?P<tail>\S.*)$"'
)
ANCHOR_SQUARE_BALANCE_WITNESS = '''def _balanced_square_brackets(text: str) -> bool:
    """Return whether square brackets are ordered and balanced in locator text."""
    depth = 0
    for char in text:
        if char == "[":
            depth += 1
        elif char == "]":
            depth -= 1
            if depth < 0:
                return False
    return depth == 0'''
ANCHOR_QUOTE_SCANNER_WITNESS = '''def _quoted_excerpts(text: str) -> list[str] | None:
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
    return None if stack else excerpts'''
ANCHOR_QUOTE_USAGE_WITNESS = (
    "quote_texts = _quoted_excerpts(tail)"
)
ANCHOR_QUOTE_LIMIT_WITNESS = (
    "any(not text.strip() or len(text.split()) > 25\n"
    "                   for text in quote_texts)"
)
ANCHOR_ABSENCE_PARSER_WITNESS = '''def _absence_parts(text: str) -> tuple[str, str, str] | None:
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
    return parts if all(part.strip() for part in parts) else None'''
ANCHOR_ABSENCE_USAGE_WITNESS = "if _absence_parts(tail) is None:"
ANCHOR_WRAPPER_WITNESSES = (
    'if value.startswith("["):',
    'if not value.endswith("]"):',
    "square_inner = value[1:-1]\n",
    "if square_inner != square_inner.strip():",
    'if value.startswith("`"):',
    'if not value.endswith("`"):',
    "backtick_inner = value[1:-1]\n",
    "if backtick_inner != backtick_inner.strip():",
)
ANCHOR_CONTENT_BALANCE_WITNESSES = (
    "if not _balanced_square_brackets(tail) or tail.count(\"`\") % 2:",
)
TEMPLATE_ANCHOR_PLACEHOLDER_WITNESSES = (
    "**Evidence Anchor**: [`<type>: <locator>`]\n"
    "[Replace the complete backticked value above; never wrap `<type>` alone. "
    "See § Evidence Anchor Types.]",
    "**Evidence Anchor**: [`<type>: <locator>`]\n"
    "[Replace the complete backticked value above; never wrap `<type>` alone. "
    "Critical/Major findings require an adequate, applicable type (#574 A2); "
    "see § Evidence Anchor Types.]",
)
DA_FINDING_WITNESS = (
    "emit exactly one `#### CRITICAL` section and exactly one `#### MAJOR` "
    "section, always present even when empty. Each is a Markdown table whose "
    "header includes exact `#` and `Evidence Anchor` columns; every data row "
    "is outer-pipe-delimited and has exactly the header column count; CRITICAL "
    "IDs are unique and dense `C1..Cn`, and are the synthesizer's "
    "machine-addressable adjudication keys. Standalone `**Severity**:` "
    "declarations are forbidden: every DA Critical or Major issue must be a "
    "row in its matching band table. Do not create any other H4 issue-table "
    "band. These tables are the terminal suffix of `## Review Body`: put "
    "every prose paragraph before `#### CRITICAL`; after the CRITICAL table "
    "emit only blank lines until `#### MAJOR`, and after the MAJOR table emit "
    "only blank lines to the end of Review Body. Do not emit HTML comments "
    "anywhere in a DA report"
)
DEFAULT_IGNORABLE_RANGES_WITNESS = (
    "_DEFAULT_IGNORABLE_RANGES = (\n"
    "    (0x00AD, 0x00AD), (0x034F, 0x034F), (0x061C, 0x061C),\n"
    "    (0x115F, 0x1160), (0x17B4, 0x17B5), (0x180B, 0x180F),\n"
    "    (0x200B, 0x200F), (0x202A, 0x202E), (0x2060, 0x206F),\n"
    "    (0x3164, 0x3164), (0xFE00, 0xFE0F), (0xFEFF, 0xFEFF),\n"
    "    (0xFFA0, 0xFFA0), (0xFFF0, 0xFFF8), (0x1BCA0, 0x1BCA3),\n"
    "    (0x1D173, 0x1D17A),\n"
    "    (0xE0000, 0xE0FFF),\n"
    ")"
)
PATTERNS = (
    "any <priority> dimension scores '<score>'",
    "any dimension with priority=<priority> scores '<score>'",
    "any <priority>-priority dimension scores '<score>'",
    "two or more <priority> dimensions score '<score>' or worse",
    "two or more dimensions with priority=<priority> score '<score>' or worse",
    "every <priority> dimension scores '<score>'",
    "<Dn> scores '<score>'",
    "any <priority> dimension has a fatal block",
    "<Dn> has a fatal block",
    "any dimension scores '<score>' or worse",
    "<Dn> scores '<score>' or worse",
    "every dimension scores '<score>'",
)
# Hardcoded textual witnesses for the executable regex bodies. Identifiers alone
# are insufficient: an editor could preserve ``fatal_priority`` while widening
# or otherwise changing the grammar it executes.
EXECUTABLE_PATTERN_WITNESSES = (
    r'''_SCORE = r"'(?P<score>block|warn|pass)'"''',
    r'r"^any (?:(?P<p1>[a-z]+) dimension|dimension with priority="',
    r'r"(?P<p2>[a-z]+)|(?P<p3>[a-z]+)-priority dimension) scores "',
    r'r"^two or more (?:(?P<p1>[a-z]+) dimensions|dimensions with priority="',
    r'r"(?P<p2>[a-z]+)) score " + _SCORE + r" or worse$"',
    r'r"^every (?P<p1>[a-z]+) dimension scores " + _SCORE + r"$"',
    r'r"^(?P<dim>D\d+) scores " + _SCORE + r"$"',
    r'r"^any (?P<p1>[a-z]+) dimension has a fatal block$"',
    r'r"^(?P<dim>D\d+) has a fatal block$"',
    r'r"^any dimension scores " + _SCORE + r" or worse$"',
    r'r"^(?P<dim>D\d+) scores " + _SCORE + r" or worse$"',
    r'r"^every dimension scores " + _SCORE + r"$"',
)
PHASE_FINDING_REGEX_WITNESSES = (
    r'r"(?:^|\|\s*)\s*(?:[-*]\s*)?\*\*Severity\*\*:\s*"',
    r'r"(?:^|\|\s*)\s*(?:[-*]\s*)?\*\*Evidence Anchor\*\*:\s*"',
    '_SEVERITY_DECL_RE = re.compile(\n'
    r'    r"\*\*Severity(?:\*\*)?\s*:",' "\n"
    "    re.IGNORECASE,\n"
    ")",
    '_ANCHOR_DECL_RE = re.compile(\n'
    r'    r"\*\*Evidence Anchor(?:\*\*)?\s*:",' "\n"
    "    re.IGNORECASE,\n"
    ")",
    r'_FINDING_H3_RE = re.compile(r"^W[1-9]\d*: \S.*$")',
)
DA_PARSER_WITNESSES = (
    '_DA_SEVERITY_DECL_RE = re.compile(\n'
    r'    r"\*\*Severity(?:\*\*)?\s*:",' "\n"
    "    re.IGNORECASE,\n"
    ")",
    "_DA_SEVERITY_DECL_RE.search(line)",
    "def _split_gfm_cells(row: str) -> list[str]:",
    'if char == "|":',
    "if backslashes % 2 == 0:",
    "return _split_gfm_cells(stripped[1:-1])",
    "return _split_gfm_cells(stripped)",
    "for candidate in lines:",
    'current_h2 == "Review Body"',
    "raw_cells = _possible_markdown_cells(candidate)",
    "for cell in raw_cells",
    "_rendered_header_cell(cell)",
    r'rendered = re.sub(r"\\([^\w\s])", r"\1", cell)',
    r'r"!?\[([^\]]*)\](?:\([^)]+\)|\[[^\]]*\])", r"\1", rendered',
    r'rendered = re.sub(r"\[([^\]]+)\]", r"\1", rendered)',
    "parser = _VisibleTextHTMLParser()",
    "parser.feed(rendered)",
    'rendered = unicodedata.normalize("NFKC", rendered)\n'
    '    rendered = "".join(',
    "def _is_default_ignorable(char: str) -> bool:",
    "for start, end in _DEFAULT_IGNORABLE_RANGES",
    DEFAULT_IGNORABLE_RANGES_WITNESS,
    'unicodedata.category(char) != "Cf"',
    "and not _is_default_ignorable(char)",
    'rendered = re.sub(r"[*_~`]+", "", rendered)',
    'return re.sub(r"\\s+", " ", rendered).strip().casefold()',
    r'_DA_ISSUE_ID_RE = re.compile(r"^[CM][1-9]\d*$", re.IGNORECASE)',
    r'r"^(?:text|table|figure|equation|dataset|absence)\s*:",',
    "issue_payload = any(\n"
    "            _DA_ISSUE_ID_RE.fullmatch(cell)\n"
    "            or _DA_TYPED_ANCHOR_RE.search(cell)\n"
    "            for cell in cells\n"
    "        )",
    '_RAW_HTML_TABLE_RE = re.compile(\n'
    '    r"<\\s*/?\\s*(?:table|thead|tbody|tr|th|td)\\b", re.IGNORECASE\n'
    ")",
    "_RAW_HTML_TABLE_RE.search(candidate)",
    r'_HTML_COMMENT_RE = re.compile(r"<!--")',
    r'_DA_FENCED_BLOCK_SENTINEL = "\0DA_FENCED_BLOCK\0"',
    "if preserve_fenced_blocks:\n"
    "                    out.append(_DA_FENCED_BLOCK_SENTINEL)",
    "raw_lines = _COMMONMARK_LINE_END_RE.split(text)",
    "_HTML_COMMENT_RE.search(line)",
    "lines = strip_fences(text, preserve_fenced_blocks=True)",
    'if "#" in cells or "evidence anchor" in cells or issue_payload:',
    "block = review_lines[start + 1:end]",
    "if any(\n"
    "                trailing.strip() for trailing in table_tail[index + 1:]\n"
    "            ):",
    "if critical_start >= major_start:",
    'f"[DA-TABLE-PARSE: {path}: #### CRITICAL must precede #### MAJOR]"',
    'review_lines, "MAJOR", path, major_start, len(review_lines)',
    "header_index = nonblank[0] if nonblank else None",
    'header.count("#") != 1 or header.count("Evidence Anchor") != 1',
    're.fullmatch(r":?-{3,}:?", cell)',
    're.fullmatch(r"C[1-9]\\d*", finding_id)',
    "if finding_id in rows:",
    "if not cells[major_id_col]:",
    "validate_evidence_anchor(anchor, f\"{path}:{finding_id}\")",
    "validate_evidence_anchor(anchor, f\"{path}:DA MAJOR\")",
)


def _read(root: Path, rel: str) -> str:
    return read_or_exit2(root, rel)


def check(root: Path) -> list[str]:
    errors: list[str] = []
    for rel, expected in CONTRACTS.items():
        contract = json.loads(_read(root, rel))
        actual = {
            dim["id"]: (dim.get("eligible_roles"), dim.get("owner_role"))
            for dim in contract["acceptance_dimensions"]
        }
        if actual != expected:
            errors.append(
                f"{rel}: eligibility map drift; expected={expected}, actual={actual}"
            )

    for rel, role in AGENTS.items():
        raw = _read(root, rel)
        sprint = heading_section(raw, SPRINT)
        phase1 = heading_section(sprint, PHASE1) if sprint is not None else None
        phase2 = heading_section(sprint, PHASE2) if sprint is not None else None
        if phase1 is None or phase2 is None:
            errors.append(f"{rel}: delivered Phase 1/Phase 2 subsection missing")
            continue
        phase1_norm, phase2_norm = norm_ws(phase1), norm_ws(phase2)
        scope = (
            "per dimension whose `eligible_roles` includes "
            f"`{role}`; do not plan a score for any other dimension"
        )
        if norm_ws(scope) not in phase1_norm:
            errors.append(f"{rel}: Phase 1 eligible-only scope witness missing")
        for field in PHASE1_FIELDS:
            if norm_ws(field) not in phase1_norm:
                errors.append(f"{rel}: Phase 1 field witness missing: {field}")
        if norm_ws(PHASE1_LIVE_GRAMMAR_WITNESS) not in phase1_norm:
            errors.append(f"{rel}: Phase 1 live-grammar witness missing")
        if norm_ws(PHASE1_TERMINAL_PREFLIGHT_WITNESS) not in phase1_norm:
            errors.append(f"{rel}: Phase 1 terminal-preflight witness missing")
        if not phase1_norm.endswith(
            norm_ws(PHASE1_TERMINAL_PREFLIGHT_WITNESS)
        ):
            errors.append(f"{rel}: Phase 1 terminal preflight is not terminal")
        score_scope = (
            "Score only dimensions whose `eligible_roles` includes "
            f"`{role}`; every other dimension must say `score: not_assessed`"
        )
        if norm_ws(score_scope) not in phase2_norm:
            errors.append(f"{rel}: Phase 2 role-scoped score witness missing")
        for witness in PHASE2_WITNESSES:
            if norm_ws(witness) not in phase2_norm:
                errors.append(f"{rel}: Phase 2 grammar witness missing: {witness}")
        role_placement_witness = (
            "Declare your panel role exactly once, on its own line: "
            f"`contract_role: {role}`. {PHASE2_ROLE_PLACEMENT_WITNESS_SUFFIX}"
        )
        for witness in (
            PHASE2_NO_DISSENT_WITNESS,
            PHASE2_TERMINAL_PREFLIGHT_WITNESS,
            role_placement_witness,
        ):
            if norm_ws(witness) not in phase2_norm:
                errors.append(f"{rel}: Phase 2 live-grammar witness missing")
        finding_witness = (
            DA_FINDING_WITNESS if role == "da" else SCORING_FINDING_WITNESS
        )
        if norm_ws(finding_witness) not in phase2_norm:
            errors.append(f"{rel}: Phase 2 per-finding grammar witness missing")
        if role != "da" and norm_ws(SCORING_FIELD_VARIANT_WITNESS) not in phase2_norm:
            errors.append(f"{rel}: Phase 2 finding-field variant witness missing")
        if (
            role != "da"
            and norm_ws(SCORING_STRENGTH_SEVERITY_WITNESS) not in phase2_norm
        ):
            errors.append(f"{rel}: Phase 2 strength-Severity witness missing")
        if norm_ws(ANCHOR_VALUE_GRAMMAR_WITNESS) not in phase2_norm:
            errors.append(f"{rel}: Phase 2 anchor-value grammar witness missing")
        phase2_content_norm = phase2_norm.removesuffix(" ---")
        if not phase2_content_norm.endswith(
            norm_ws(PHASE2_TERMINAL_PREFLIGHT_WITNESS)
        ):
            errors.append(f"{rel}: Phase 2 terminal preflight is not terminal")

    da = _read(root, "academic-paper-reviewer/agents/devils_advocate_reviewer_agent.md")
    if "Score the paper — your job is to challenge, not score." in da:
        errors.append("DA retired no-scoring clause returned")
    if "Score any dimension outside the contract's `eligible_roles` for `da`" not in da:
        errors.append("DA role-scoped Phase Boundary clause missing")

    protocol_raw = _read(root, PROTOCOL)
    protocol = heading_section(protocol_raw, "## 9. Recognised expression vocabulary")
    protocol_phase1 = heading_section(protocol_raw, "## 4. Phase 1 output lint")
    protocol_phase2 = heading_section(protocol_raw, "## 5. Phase 2 output lint")
    synth = heading_section(_read(root, SYNTH), SPRINT.replace("Protocol", "Synthesizer Protocol"))
    checker = _read(root, PANEL_CHECKER)
    phase_checker = _read(root, PHASE_CHECKER)
    if protocol is None or synth is None:
        errors.append("protocol/synthesizer expression section missing")
    else:
        for pattern in PATTERNS:
            if pattern not in protocol:
                errors.append(f"{PROTOCOL}: expression pattern missing: {pattern}")
            if pattern not in synth:
                errors.append(f"{SYNTH}: expression pattern missing: {pattern}")
    # A third, independent surface witness: pin executable regex source, not
    # merely the stable tuple identifiers surrounding it.
    for token in (
        '"fatal_priority"', '"fatal_dim"', '"any_all"',
        '"dim_threshold"', '"every_all"',
    ):
        if token not in checker:
            errors.append(f"{PANEL_CHECKER}: executable pattern token missing: {token}")
    for witness in EXECUTABLE_PATTERN_WITNESSES:
        if witness not in checker:
            errors.append(
                f"{PANEL_CHECKER}: executable regex witness missing: {witness}"
            )
    for witness in PHASE_FINDING_REGEX_WITNESSES:
        if witness not in phase_checker:
            errors.append(
                f"{PHASE_CHECKER}: finding regex witness missing: {witness}"
            )
    for witness in DA_PARSER_WITNESSES:
        if witness not in checker:
            errors.append(
                f"{PANEL_CHECKER}: DA parser witness missing: {witness}"
            )
    if ANCHOR_VALIDATOR_REGEX_WITNESS not in checker:
        errors.append(f"{PANEL_CHECKER}: anchor-validator regex witness missing")
    if ANCHOR_SQUARE_BALANCE_WITNESS not in checker:
        errors.append(f"{PANEL_CHECKER}: square-balance helper witness missing")
    if ANCHOR_QUOTE_SCANNER_WITNESS not in checker:
        errors.append(f"{PANEL_CHECKER}: anchor-quote scanner witness missing")
    if ANCHOR_QUOTE_USAGE_WITNESS not in checker:
        errors.append(f"{PANEL_CHECKER}: anchor-quote scanner usage missing")
    if ANCHOR_QUOTE_LIMIT_WITNESS not in checker:
        errors.append(f"{PANEL_CHECKER}: anchor-quote pair limit missing")
    if ANCHOR_ABSENCE_PARSER_WITNESS not in checker:
        errors.append(f"{PANEL_CHECKER}: anchor-absence parser witness missing")
    if ANCHOR_ABSENCE_USAGE_WITNESS not in checker:
        errors.append(f"{PANEL_CHECKER}: anchor-absence parser usage missing")
    for witness in ANCHOR_WRAPPER_WITNESSES:
        if witness not in checker:
            errors.append(
                f"{PANEL_CHECKER}: anchor-wrapper witness missing: {witness}"
            )
    for witness in ANCHOR_CONTENT_BALANCE_WITNESSES:
        if witness not in checker:
            errors.append(
                f"{PANEL_CHECKER}: anchor-content-balance witness missing: {witness}"
            )
    if (
        protocol_phase2 is None
        or norm_ws(ANCHOR_VALUE_GRAMMAR_WITNESS) not in norm_ws(protocol_phase2)
    ):
        errors.append(f"{PROTOCOL}: Phase 2 anchor-value grammar witness missing")
    if protocol_phase1 is None:
        errors.append(f"{PROTOCOL}: Phase 1 output-lint section missing")
    else:
        for witness in (
            *PROTOCOL_PHASE1_LIVE_WITNESSES,
            PHASE1_TERMINAL_PREFLIGHT_WITNESS,
        ):
            if norm_ws(witness) not in norm_ws(protocol_phase1):
                errors.append(f"{PROTOCOL}: Phase 1 live-grammar witness missing")
    if protocol_phase2 is not None:
        for witness in (
            *PROTOCOL_PHASE2_LIVE_WITNESSES,
            PROTOCOL_DA_TABLE_GATE_WITNESS,
            PHASE2_TERMINAL_PREFLIGHT_WITNESS,
        ):
            if norm_ws(witness) not in norm_ws(protocol_phase2):
                errors.append(f"{PROTOCOL}: Phase 2 live-grammar witness missing")
    template = _read(root, TEMPLATE)
    if norm_ws(SCORING_FIELD_VARIANT_WITNESS) not in norm_ws(template):
        errors.append(f"{TEMPLATE}: finding-field variant witness missing")
    if norm_ws(ANCHOR_VALUE_GRAMMAR_WITNESS) not in norm_ws(template):
        errors.append(f"{TEMPLATE}: anchor-value grammar witness missing")
    if norm_ws(TEMPLATE_STRENGTH_SEVERITY_WITNESS) not in norm_ws(template):
        errors.append(f"{TEMPLATE}: strength-Severity witness missing")
    for witness in TEMPLATE_ANCHOR_PLACEHOLDER_WITNESSES:
        if witness not in template:
            errors.append(f"{TEMPLATE}: anchor placeholder witness missing")
    template_anchors = [
        match.group("anchor")
        for match in TEMPLATE_EXAMPLE_ANCHOR_RE.finditer(template)
    ]
    if len(template_anchors) != TEMPLATE_EXAMPLE_ANCHOR_COUNT:
        errors.append(
            f"{TEMPLATE}: expected {TEMPLATE_EXAMPLE_ANCHOR_COUNT} canonical "
            f"anchor examples, found {len(template_anchors)}"
        )
    template_anchor_types = tuple(
        anchor.partition(":")[0].lower() for anchor in template_anchors
    )
    if template_anchor_types != TEMPLATE_EXAMPLE_ANCHOR_TYPES:
        errors.append(
            f"{TEMPLATE}: expected ordered canonical anchor types "
            f"{TEMPLATE_EXAMPLE_ANCHOR_TYPES}, found {template_anchor_types}"
        )
    for index, anchor in enumerate(template_anchors, 1):
        try:
            validate_evidence_anchor(anchor, f"{TEMPLATE}:example-{index}")
        except ReportError as exc:
            errors.append(str(exc))
    for rel in SHIPPED_EXAMPLES:
        example = _read(root, rel)
        anchors = [
            match.group("anchor")
            for match in SHIPPED_EXAMPLE_ANCHOR_RE.finditer(example)
        ]
        expected_count = SHIPPED_EXAMPLE_ANCHOR_COUNTS[rel]
        if len(anchors) != expected_count:
            errors.append(
                f"{rel}: expected {expected_count} shipped typed anchors, "
                f"found {len(anchors)}"
            )
        for index, anchor in enumerate(anchors, 1):
            try:
                validate_evidence_anchor(anchor, f"{rel}:anchor-{index}")
            except ReportError as exc:
                errors.append(str(exc))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    args = parser.parse_args()
    errors = check(args.root)
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("check_role_scoped_contract: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
