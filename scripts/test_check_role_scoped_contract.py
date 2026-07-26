"""Mutation tests for check_role_scoped_contract.py."""
from __future__ import annotations

import shutil
from pathlib import Path

from scripts import check_role_scoped_contract as lint

REPO = Path(__file__).resolve().parents[1]
MIRROR_FILES = tuple(lint.CONTRACTS) + tuple(lint.AGENTS) + (
    lint.PROTOCOL, lint.SYNTH, lint.PANEL_CHECKER, lint.PHASE_CHECKER,
    lint.TEMPLATE,
) + tuple(lint.SHIPPED_EXAMPLES)


def mirror(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    for rel in MIRROR_FILES:
        destination = root / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(REPO / rel, destination)
    return root


def mutate(root: Path, rel: str, old: str, new: str):
    path = root / rel
    text = path.read_text(encoding="utf-8")
    assert old in text
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def mutate_last(root: Path, rel: str, old: str, new: str):
    path = root / rel
    text = path.read_text(encoding="utf-8")
    before, separator, after = text.rpartition(old)
    assert separator
    path.write_text(before + new + after, encoding="utf-8")


def test_unmutated_mirror_passes(tmp_path):
    assert lint.check(mirror(tmp_path)) == []


def test_eligibility_map_mutation_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root, "shared/contracts/reviewer/full.json",
        '"eligible_roles": ["methodology"]',
        '"eligible_roles": ["eic"]',
    )
    assert lint.check(root)


def test_delivered_phase1_literal_mutation_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root, next(iter(lint.AGENTS)),
        "`what_triggers_fatal: <single-line non-empty text>`",
        "`fatal_trigger: <single-line non-empty text>`",
    )
    assert lint.check(root)


def test_delivered_phase1_live_grammar_mutations_fail(tmp_path):
    for index, rel in enumerate(lint.AGENTS):
        root = mirror(tmp_path / str(index))
        mutate(
            root,
            rel,
            "omit the entire `what_triggers_fatal:` line",
            "emit a `what_triggers_fatal:` sentinel line",
        )
        assert lint.check(root)


def test_delivered_phase1_terminal_preflight_mutations_fail(tmp_path):
    mutations = (
        (
            "The only H2 sections are exactly one `## Contract Paraphrase`",
            "Additional H2 sections may precede one `## Contract Paraphrase`",
        ),
        (
            "The paraphrase meets `measurement_procedure.paraphrase_minimum_dimensions`",
            "The paraphrase may ignore `measurement_procedure.paraphrase_minimum_dimensions`",
        ),
        (
            "only dimensions eligible for your dispatch role appear",
            "all contract dimensions may appear",
        ),
        (
            "contains exactly one unbulleted `dimension_id:`",
            "contains any number of `dimension_id:` lines",
        ),
        (
            "`what_triggers_fatal:` occurs zero times",
            "`what_triggers_fatal:` may occur once",
        ),
        (
            "The final nonblank output line is exactly",
            "The acknowledgement may appear anywhere as",
        ),
        (
            "No `## Dimension Scores`, `## Review Body`",
            "A `## Dimension Scores` or `## Review Body` may appear",
        ),
        (
            "no manuscript-specific claim appears",
            "manuscript-specific claims may appear",
        ),
    )
    for agent_index, rel in enumerate(lint.AGENTS):
        for mutation_index, (old, new) in enumerate(mutations):
            root = mirror(tmp_path / f"{agent_index}-{mutation_index}")
            mutate(root, rel, old, new)
            errors = lint.check(root)
            assert f"{rel}: Phase 1 terminal-preflight witness missing" in errors


def test_delivered_phase1_terminal_preflight_relocation_fails(tmp_path):
    marker = "Do not send until every check holds."
    for index, rel in enumerate(lint.AGENTS):
        root = mirror(tmp_path / str(index))
        path = root / rel
        text = path.read_text(encoding="utf-8")
        marker_index = text.index(marker)
        insertion = marker_index + len(marker)
        text = text[:insertion] + "\nAdditional Phase 1 rule." + text[insertion:]
        path.write_text(text, encoding="utf-8")
        errors = lint.check(root)
        assert f"{rel}: Phase 1 terminal preflight is not terminal" in errors


def test_delivered_phase2_literal_mutation_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root, next(iter(lint.AGENTS)),
        "block_class: <fatal|repairable>",
        "block_kind: <fatal|repairable>",
    )
    assert lint.check(root)


def test_delivered_phase2_no_dissent_mutations_fail(tmp_path):
    for index, rel in enumerate(lint.AGENTS):
        root = mirror(tmp_path / str(index))
        mutate(
            root,
            rel,
            "omit the entire `## Scoring Plan Dissent` section",
            "emit a `## Scoring Plan Dissent` section containing `none`",
        )
        assert lint.check(root)


def test_delivered_phase2_terminal_preflight_mutations_fail(tmp_path):
    mutations = (
        (
            "If it differs on two or more, abort with",
            "If it differs on two or more, select one and continue with",
        ),
        (
            "emit exactly one `## Dimension Scores` followed by exactly one `## Review Body`",
            "emit `## Dimension Scores`; `## Review Body` is optional",
        ),
        (
            "Delete `## Failure Condition Checks`, `## Editorial Decision`",
            "Keep `## Failure Condition Checks` and `## Editorial Decision`",
        ),
        (
            "`## Dimension Scores` and nowhere else",
            "`## Dimension Scores` and inside each dimension",
        ),
        (
            "eligible `not_assessed` has exactly one non-empty `abstain_reason:`",
            "eligible `not_assessed` may omit `abstain_reason:`",
        ),
        (
            "ineligible dimension uses only `score: not_assessed` with no `abstain_reason:`",
            "ineligible dimensions may carry a real score or `abstain_reason:`",
        ),
        (
            "a character-for-character substring",
            "a semantic paraphrase",
        ),
        (
            "every mandatory `block` has exactly one `block_class:`",
            "a mandatory `block` may omit `block_class:`",
        ),
        (
            "every weakness is its own `### W<n>` subsection",
            "weaknesses may share one subsection",
        ),
        (
            "If either finding polarity is empty, include its required Coverage Receipt",
            "Empty finding polarities need no Coverage Receipt",
        ),
        (
            "Each table header contains exactly one column named `#`",
            "Table headers may omit the `#` column",
        ),
        (
            "CRITICAL IDs are unique and dense `C1..Cn`",
            "CRITICAL IDs may be sparse or duplicated",
        ),
        (
            "these tables are the terminal suffix of `## Review Body`",
            "these tables may be followed by additional Review Body content",
        ),
        (
            "quoted excerpt is at most 25 words",
            "quoted excerpt is at most 50 words",
        ),
        (
            "contains at least one balanced quoted verbatim excerpt",
            "may omit a balanced quoted verbatim excerpt",
        ),
        (
            "a Critical is singleton rejection-level",
            "a Critical may need sibling findings to reach rejection level",
        ),
    )
    for agent_index, rel in enumerate(lint.AGENTS):
        for mutation_index, (old, new) in enumerate(mutations):
            root = mirror(tmp_path / f"{agent_index}-{mutation_index}")
            mutate_last(root, rel, old, new)
            errors = lint.check(root)
            assert f"{rel}: Phase 2 live-grammar witness missing" in errors


def test_delivered_phase2_terminal_preflight_relocation_fails(tmp_path):
    marker = "Do not send until every check holds."
    for index, rel in enumerate(lint.AGENTS):
        root = mirror(tmp_path / str(index))
        path = root / rel
        text = path.read_text(encoding="utf-8")
        marker_index = text.rindex(marker)
        insertion = marker_index + len(marker)
        text = text[:insertion] + "\nAdditional Phase 2 rule." + text[insertion:]
        path.write_text(text, encoding="utf-8")
        errors = lint.check(root)
        assert f"{rel}: Phase 2 terminal preflight is not terminal" in errors


def test_delivered_phase2_role_placement_mutations_fail(tmp_path):
    for index, rel in enumerate(lint.AGENTS):
        root = mirror(tmp_path / str(index))
        mutate(
            root,
            rel,
            "never repeat it inside any dimension subsection",
            "repeat it inside each dimension subsection",
        )
        assert lint.check(root)


def test_delivered_phase2_role_token_mutations_fail(tmp_path):
    mutations = (
        (
            "academic-paper-reviewer/agents/eic_agent.md",
            "eic",
            "domain",
        ),
        (
            "academic-paper-reviewer/agents/methodology_reviewer_agent.md",
            "methodology",
            "domain",
        ),
        (
            "academic-paper-reviewer/agents/domain_reviewer_agent.md",
            "domain",
            "eic",
        ),
        (
            "academic-paper-reviewer/agents/perspective_reviewer_agent.md",
            "perspective",
            "domain",
        ),
        (
            "academic-paper-reviewer/agents/devils_advocate_reviewer_agent.md",
            "da",
            "domain",
        ),
    )
    for index, (rel, role, wrong_role) in enumerate(mutations):
        root = mirror(tmp_path / str(index))
        mutate(
            root,
            rel,
            f"`contract_role: {role}`",
            f"`contract_role: {wrong_role}`",
        )
        errors = lint.check(root)
        assert f"{rel}: Phase 2 live-grammar witness missing" in errors


def test_delivered_phase2_strength_severity_mutations_fail(tmp_path):
    non_da_agents = [
        rel for rel, role in lint.AGENTS.items() if role != "da"
    ]
    for index, rel in enumerate(non_da_agents):
        root = mirror(tmp_path / str(index))
        mutate(
            root,
            rel,
            "Strength subsections never carry a `**Severity**:` field",
            "Strength subsections may carry a `**Severity**:` field",
        )
        assert lint.check(root)


def test_delivered_phase2_quote_preflight_mutations_fail(tmp_path):
    for index, rel in enumerate(lint.AGENTS):
        root = mirror(tmp_path / str(index))
        mutate(
            root,
            rel,
            "Before output, confirm at least one quoted excerpt exists",
            "Before output, allow anchors with no quoted excerpt",
        )
        assert lint.check(root)


def test_delivered_phase2_per_finding_grammar_mutation_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root, next(iter(lint.AGENTS)),
        "Findings never share an anchor.",
        "Findings may share an anchor.",
    )
    assert lint.check(root)


def test_da_required_table_grammar_mutation_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root,
        "academic-paper-reviewer/agents/devils_advocate_reviewer_agent.md",
        "always present even when empty",
        "optional when empty",
    )
    assert lint.check(root)


def test_protocol_pattern_mutation_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root, lint.PROTOCOL,
        "any dimension scores '<score>' or worse",
        "some dimension scores '<score>' or worse",
    )
    assert lint.check(root)


def test_executable_regex_mutation_fails_even_when_identifier_remains(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root,
        lint.PANEL_CHECKER,
        r"^any (?P<p1>[a-z]+) dimension has a fatal block$",
        r"^any (?P<p1>[a-z]+) dimension has any fatal block$",
    )
    assert lint.check(root)


def test_shared_score_regex_mutation_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root,
        lint.PANEL_CHECKER,
        r'''_SCORE = r"'(?P<score>block|warn|pass)'"''',
        r'''_SCORE = r"'(?P<score>block|warn|pass|fail)'"''',
    )
    assert lint.check(root)


def test_phase_finding_regex_mutation_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root,
        lint.PHASE_CHECKER,
        r'_FINDING_H3_RE = re.compile(r"^W[1-9]\d*: \S.*$")',
        r'_FINDING_H3_RE = re.compile(r"^.*$")',
    )
    assert lint.check(root)


def test_severity_declaration_sentinel_mutation_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root,
        lint.PHASE_CHECKER,
        r'    r"\*\*Severity(?:\*\*)?\s*:",',
        r'    r"\*\*Severity\*\*:",',
    )
    assert lint.check(root)


def test_anchor_declaration_sentinel_mutation_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root,
        lint.PHASE_CHECKER,
        r'    r"\*\*Evidence Anchor(?:\*\*)?\s*:",',
        r'    r"\*\*Evidence Anchor\*\*:",',
    )
    assert lint.check(root)


def test_da_parser_witness_mutation_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root,
        lint.PANEL_CHECKER,
        'header.count("#") != 1 or header.count("Evidence Anchor") != 1',
        'header.count("#") < 1 or header.count("Evidence Anchor") < 1',
    )
    assert lint.check(root)


def test_da_first_nonblank_header_witness_mutation_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root,
        lint.PANEL_CHECKER,
        "header_index = nonblank[0] if nonblank else None",
        "header_index = nonblank[-1] if nonblank else None",
    )
    assert lint.check(root)


def test_da_standalone_severity_witness_mutation_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root,
        lint.PANEL_CHECKER,
        "_DA_SEVERITY_DECL_RE.search(line)",
        "_DA_SEVERITY_DECL_RE.match(line)",
    )
    assert lint.check(root)


def test_da_severity_regex_body_mutation_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root,
        lint.PANEL_CHECKER,
        r'r"\*\*Severity(?:\*\*)?\s*:",',
        r'r"^\*\*Severity(?:\*\*)?\s*:",',
    )
    assert lint.check(root)


def test_da_severity_regex_ignorecase_mutation_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root,
        lint.PANEL_CHECKER,
        r'    r"\*\*Severity(?:\*\*)?\s*:",' "\n"
        "    re.IGNORECASE,\n"
        ")",
        r'    r"\*\*Severity(?:\*\*)?\s*:",' "\n"
        ")",
    )
    assert lint.check(root)


def test_da_global_table_scan_witness_mutation_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root,
        lint.PANEL_CHECKER,
        "for candidate in lines:",
        "for candidate in review_lines:",
    )
    assert lint.check(root)


def test_da_header_whitespace_normalization_mutation_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root,
        lint.PANEL_CHECKER,
        'return re.sub(r"\\s+", " ", rendered).strip().casefold()',
        "return rendered.casefold()",
    )
    assert lint.check(root)


def test_da_header_inline_markup_normalization_mutation_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root,
        lint.PANEL_CHECKER,
        'rendered = re.sub(r"[*_~`]+", "", rendered)',
        "rendered = rendered",
    )
    assert lint.check(root)


def test_da_header_commonmark_reduction_mutations_fail(tmp_path):
    mutations = (
        (
            r'rendered = re.sub(r"\\([^\w\s])", r"\1", cell)',
            "rendered = cell",
        ),
        (
            r'r"!?\[([^\]]*)\](?:\([^)]+\)|\[[^\]]*\])", r"\1", rendered',
            r'r"never-match", r"\1", rendered',
        ),
        ("parser.feed(rendered)", 'parser.feed("")'),
    )
    for index, (old, new) in enumerate(mutations):
        root = mirror(tmp_path / str(index))
        mutate(root, lint.PANEL_CHECKER, old, new)
        assert lint.check(root)


def test_da_issue_payload_sentinel_mutations_fail(tmp_path):
    mutations = (
        (
            r'_DA_ISSUE_ID_RE = re.compile(r"^[CM][1-9]\d*$", re.IGNORECASE)',
            r'_DA_ISSUE_ID_RE = re.compile(r"^never$", re.IGNORECASE)',
        ),
        (
            r'r"^(?:text|table|figure|equation|dataset|absence)\s*:",',
            r'r"^never-match:",',
        ),
    )
    for index, (old, new) in enumerate(mutations):
        root = mirror(tmp_path / str(index))
        mutate(root, lint.PANEL_CHECKER, old, new)
        assert lint.check(root)


def test_da_issue_payload_normalized_iterator_mutation_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root,
        lint.PANEL_CHECKER,
        "issue_payload = any(\n"
        "            _DA_ISSUE_ID_RE.fullmatch(cell)\n"
        "            or _DA_TYPED_ANCHOR_RE.search(cell)\n"
        "            for cell in cells\n"
        "        )",
        "issue_payload = any(\n"
        "            _DA_ISSUE_ID_RE.fullmatch(cell)\n"
        "            or _DA_TYPED_ANCHOR_RE.search(cell)\n"
        "            for cell in raw_cells\n"
        "        )",
    )
    assert lint.check(root)


def test_da_gfm_escaped_pipe_splitter_mutation_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root,
        lint.PANEL_CHECKER,
        "if backslashes % 2 == 0:",
        "if True:",
    )
    assert lint.check(root)


def test_da_canonical_splitter_callsite_mutation_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root,
        lint.PANEL_CHECKER,
        "return _split_gfm_cells(stripped[1:-1])",
        'return [cell.strip() for cell in stripped[1:-1].split("|")]',
    )
    assert lint.check(root)


def test_da_unicode_format_normalization_mutations_fail(tmp_path):
    mutations = (
        (
            'rendered = unicodedata.normalize("NFKC", rendered)',
            "rendered = rendered",
        ),
        (
            "and not _is_default_ignorable(char)",
            "and True",
        ),
    )
    for index, (old, new) in enumerate(mutations):
        root = mirror(tmp_path / str(index))
        mutate(root, lint.PANEL_CHECKER, old, new)
        assert lint.check(root)


def test_da_default_ignorable_range_table_mutation_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root,
        lint.PANEL_CHECKER,
        "(0x202A, 0x202E)",
        "(0x202A, 0x202D)",
    )
    assert lint.check(root)


def test_da_nfkc_conditional_bypass_mutation_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root,
        lint.PANEL_CHECKER,
        'rendered = unicodedata.normalize("NFKC", rendered)',
        'rendered = unicodedata.normalize("NFKC", rendered) '
        "if False else rendered",
    )
    assert lint.check(root)


def test_da_raw_html_table_witness_mutation_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root,
        lint.PANEL_CHECKER,
        "_RAW_HTML_TABLE_RE.search(candidate)",
        "False",
    )
    assert lint.check(root)


def test_da_raw_html_pattern_body_mutation_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root,
        lint.PANEL_CHECKER,
        r"(?:table|thead|tbody|tr|th|td)",
        r"(?:table)",
    )
    assert lint.check(root)


def test_da_html_comment_guard_mutation_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root,
        lint.PANEL_CHECKER,
        "_HTML_COMMENT_RE.search(line)",
        "False",
    )
    assert lint.check(root)


def test_da_html_comment_pattern_mutation_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root,
        lint.PANEL_CHECKER,
        r'_HTML_COMMENT_RE = re.compile(r"<!--")',
        r'_HTML_COMMENT_RE = re.compile(r"<!--|-->")',
    )
    assert lint.check(root)


def test_da_fenced_block_sentinel_call_mutation_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root,
        lint.PANEL_CHECKER,
        "lines = strip_fences(text, preserve_fenced_blocks=True)",
        "lines = strip_fences(text)",
    )
    assert lint.check(root)


def test_da_fenced_block_sentinel_body_mutation_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root,
        lint.PANEL_CHECKER,
        "out.append(_DA_FENCED_BLOCK_SENTINEL)",
        "pass",
    )
    assert lint.check(root)


def test_da_major_terminal_boundary_mutation_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root,
        lint.PANEL_CHECKER,
        'review_lines, "MAJOR", path, major_start, len(review_lines)',
        'review_lines, "MAJOR", path, major_start, major_start + 1',
    )
    assert lint.check(root)


def test_da_terminal_table_guard_mutation_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root,
        lint.PANEL_CHECKER,
        (
            "if any(\n"
            "                trailing.strip() for trailing in "
            "table_tail[index + 1:]\n"
            "            ):"
        ),
        "if False:",
    )
    assert lint.check(root)


def test_da_detailed_terminal_delivery_mutation_fails(tmp_path):
    root = mirror(tmp_path)
    rel = "academic-paper-reviewer/agents/devils_advocate_reviewer_agent.md"
    mutate(
        root,
        rel,
        "These tables are the terminal suffix of `## Review Body`",
        "These tables may be followed by additional Review Body content",
    )
    assert lint.check(root)


def test_da_extra_band_table_witness_mutation_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root,
        lint.PANEL_CHECKER,
        'if "#" in cells or "evidence anchor" in cells or issue_payload:',
        'if "#" in cells and "evidence anchor" in cells and issue_payload:',
    )
    assert lint.check(root)


def test_phase_finding_declaration_ignorecase_mutations_fail(tmp_path):
    for name in ("Severity", "Evidence Anchor"):
        current = mirror(tmp_path / name.replace(" ", "-"))
        mutate(
            current,
            lint.PHASE_CHECKER,
            rf'    r"\*\*{name}(?:\*\*)?\s*:",' "\n"
            "    re.IGNORECASE,\n"
            ")",
            rf'    r"\*\*{name}(?:\*\*)?\s*:",' "\n"
            ")",
        )
        assert lint.check(current)


def test_da_separator_witness_mutation_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root,
        lint.PANEL_CHECKER,
        're.fullmatch(r":?-{3,}:?", cell)',
        're.fullmatch(r".*", cell)',
    )
    assert lint.check(root)


def test_template_field_variant_witness_mutation_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root,
        lint.TEMPLATE,
        "including its type and locator, may be bare, backtick-wrapped, or square-bracketed",
        "including only its type, may be bare, backtick-wrapped, or square-bracketed",
    )
    assert lint.check(root)


def test_delivered_anchor_value_grammar_mutations_fail(tmp_path):
    for rel in lint.AGENTS:
        root = mirror(tmp_path / Path(rel).stem)
        mutate(
            root,
            rel,
            "nothing may appear between the type and its colon",
            "content may appear between the type and its colon",
        )
        assert lint.check(root)


def test_template_anchor_value_grammar_mutation_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root,
        lint.TEMPLATE,
        "Every Evidence Anchor value begins with the literal `<type>: <locator>` grammar",
        "Every Evidence Anchor value should usually include a type and locator",
    )
    assert lint.check(root)


def test_protocol_anchor_value_grammar_mutation_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root,
        lint.PROTOCOL,
        "An `absence:` anchor uses the exact grammar",
        "An `absence:` anchor may use an approximate grammar",
    )
    assert lint.check(root)


def test_protocol_live_grammar_mutations_fail(tmp_path):
    mutations = (
        (
            "Copy each dimension ID and name exactly from the contract",
            "Paraphrase each dimension ID and name from the contract",
        ),
        (
            "omit the entire `what_triggers_fatal:` line",
            "emit a `what_triggers_fatal:` sentinel line",
        ),
        (
            "omit the whole section rather than emitting an empty or `none` placeholder",
            "emit the whole section with an empty or `none` placeholder",
        ),
        (
            "immediately before `## Dimension Scores`; never repeat that report-level line",
            "anywhere near `## Dimension Scores`; repeat that report-level line",
        ),
        (
            "Strength subsections never carry a `Severity` field",
            "Strength subsections may carry a `Severity` field",
        ),
        (
            "Before output, confirm at least one quoted excerpt exists",
            "Before output, allow anchors with no quoted excerpt",
        ),
        (
            "`what_triggers_fatal:` occurs zero times",
            "`what_triggers_fatal:` may occur once",
        ),
        (
            "The only H2 sections are exactly one `## Contract Paraphrase`",
            "Additional H2 sections may precede one `## Contract Paraphrase`",
        ),
        (
            "No `## Dimension Scores`, `## Review Body`",
            "A `## Dimension Scores` or `## Review Body` may appear",
        ),
        (
            "The final nonblank output line is exactly",
            "The acknowledgement may appear anywhere as",
        ),
        (
            "If it differs on two or more, abort with",
            "If it differs on two or more, select one and continue with",
        ),
        (
            "a character-for-character substring",
            "a semantic paraphrase",
        ),
        (
            "eligible `not_assessed` has exactly one non-empty `abstain_reason:`",
            "eligible `not_assessed` may omit `abstain_reason:`",
        ),
        (
            "Delete `## Failure Condition Checks`, `## Editorial Decision`",
            "Keep `## Failure Condition Checks` and `## Editorial Decision`",
        ),
        (
            "If either finding polarity is empty, include its required Coverage Receipt",
            "Empty finding polarities need no Coverage Receipt",
        ),
        (
            "Each table header contains exactly one column named `#`",
            "Table headers may omit the `#` column",
        ),
        (
            "CRITICAL IDs are unique and dense `C1..Cn`",
            "CRITICAL IDs may be sparse or duplicated",
        ),
        (
            "these tables are the terminal suffix of `## Review Body`",
            "these tables may be followed by additional Review Body content",
        ),
        (
            "The two tables are the terminal suffix of `## Review Body`",
            "The two tables may be followed by additional Review Body content",
        ),
    )
    for index, (old, new) in enumerate(mutations):
        root = mirror(tmp_path / str(index))
        mutate(root, lint.PROTOCOL, old, new)
        assert lint.check(root)


def test_template_live_grammar_mutations_fail(tmp_path):
    mutations = (
        (
            "Omit the Severity field entirely",
            "Emit the Severity field on strengths",
        ),
        (
            "Before output, confirm at least one quoted excerpt exists",
            "Before output, allow anchors with no quoted excerpt",
        ),
    )
    for index, (old, new) in enumerate(mutations):
        root = mirror(tmp_path / str(index))
        mutate(root, lint.TEMPLATE, old, new)
        assert lint.check(root)


def test_anchor_validator_colon_regex_mutation_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root,
        lint.PANEL_CHECKER,
        r'r"^(?P<type>text|table|figure|equation|dataset|absence):\s*"',
        r'r"^(?P<type>text|table|figure|equation|dataset|absence)(?::|-)\s*"',
    )
    assert lint.check(root)


def test_anchor_square_balance_helper_mutation_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root,
        lint.PANEL_CHECKER,
        lint.ANCHOR_SQUARE_BALANCE_WITNESS,
        lint.ANCHOR_SQUARE_BALANCE_WITNESS.replace(
            "if depth < 0:",
            "if False:",
            1,
        ),
    )
    assert lint.check(root)


def test_anchor_validator_quote_scanner_mutation_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root,
        lint.PANEL_CHECKER,
        lint.ANCHOR_QUOTE_SCANNER_WITNESS,
        lint.ANCHOR_QUOTE_SCANNER_WITNESS.replace(
            'if not stack or stack[-1][0] != "curly":',
            'if not stack:',
            1,
        ),
    )
    assert lint.check(root)


def test_anchor_validator_quote_scanner_usage_mutation_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root,
        lint.PANEL_CHECKER,
        lint.ANCHOR_QUOTE_USAGE_WITNESS,
        "quote_texts = []",
    )
    assert lint.check(root)


def test_anchor_validator_quote_pair_limit_mutation_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root,
        lint.PANEL_CHECKER,
        lint.ANCHOR_QUOTE_LIMIT_WITNESS,
        (
            "not quote_texts[0].strip() "
            "or len(quote_texts[0].split()) > 25"
        ),
    )
    assert lint.check(root)


def test_anchor_validator_absence_parser_mutation_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root,
        lint.PANEL_CHECKER,
        lint.ANCHOR_ABSENCE_PARSER_WITNESS,
        lint.ANCHOR_ABSENCE_PARSER_WITNESS.replace(
            "text.count(expected_separator) != 1",
            "text.count(expected_separator) >= 1",
            1,
        ),
    )
    assert lint.check(root)


def test_anchor_validator_absence_parser_usage_mutation_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root,
        lint.PANEL_CHECKER,
        lint.ANCHOR_ABSENCE_USAGE_WITNESS,
        "if False:",
    )
    assert lint.check(root)


def test_shipped_example_absence_separator_mutation_fails(tmp_path):
    for index, rel in enumerate(lint.SHIPPED_EXAMPLES):
        root = mirror(tmp_path / str(index))
        mutate(root, rel, "; checked", ";checked")
        assert lint.check(root)


def test_anchor_validator_wrapper_mutations_fail(tmp_path):
    replacements = (
        (
            'if value.startswith("["):',
            'if False and value.startswith("["):',
        ),
        (
            'if not value.endswith("]"):',
            'if False and not value.endswith("]"):',
        ),
        (
            "square_inner = value[1:-1]",
            "square_inner = value[1:-1].strip()",
        ),
        (
            "if square_inner != square_inner.strip():",
            "if False:",
        ),
        (
            'if value.startswith("`"):',
            'if False and value.startswith("`"):',
        ),
        (
            'if not value.endswith("`"):',
            'if False and not value.endswith("`"):',
        ),
        (
            "backtick_inner = value[1:-1]",
            "backtick_inner = value[1:-1].strip()",
        ),
        (
            "if backtick_inner != backtick_inner.strip():",
            "if False:",
        ),
    )
    for index, (old, new) in enumerate(replacements):
        root = mirror(tmp_path / str(index))
        mutate(root, lint.PANEL_CHECKER, old, new)
        assert lint.check(root)


def test_anchor_validator_content_balance_mutations_fail(tmp_path):
    replacements = (
        (
            "if not _balanced_square_brackets(tail) or tail.count(\"`\") % 2:",
            "if False:",
        ),
    )
    for index, (old, new) in enumerate(replacements):
        root = mirror(tmp_path / str(index))
        mutate(root, lint.PANEL_CHECKER, old, new)
        assert lint.check(root)


def test_template_anchor_placeholder_tail_mutations_fail(tmp_path):
    for index, witness in enumerate(lint.TEMPLATE_ANCHOR_PLACEHOLDER_WITNESSES):
        root = mirror(tmp_path / str(index))
        mutate(
            root,
            lint.TEMPLATE,
            witness,
            witness.replace("]\n[Replace", "] — Replace", 1),
        )
        assert lint.check(root)


def test_template_canonical_anchor_example_mutation_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root,
        lint.TEMPLATE,
        (
            "Evidence Anchor: absence: Methods — expected a consent/ethics "
            "statement; checked §3, §6, appendix"
        ),
        "Evidence Anchor: absence: checked §3, §6, appendix",
    )
    assert lint.check(root)


def test_template_canonical_anchor_type_substitutions_fail(tmp_path):
    substitutions = (
        ("Evidence Anchor: text:", "Evidence Anchor: figure:"),
        ("Evidence Anchor: table:", "Evidence Anchor: dataset:"),
        ("Evidence Anchor: absence:", "Evidence Anchor: equation:"),
    )
    for index, (old, new) in enumerate(substitutions):
        root = mirror(tmp_path / str(index))
        mutate(root, lint.TEMPLATE, old, new)
        assert lint.check(root)


def test_da_old_no_scoring_clause_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root,
        "academic-paper-reviewer/agents/devils_advocate_reviewer_agent.md",
        "Score any dimension outside the contract's `eligible_roles` for `da`",
        "Score the paper — your job is to challenge, not score.",
    )
    assert lint.check(root)
