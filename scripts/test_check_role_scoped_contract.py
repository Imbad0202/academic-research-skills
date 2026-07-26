"""Mutation tests for check_role_scoped_contract.py."""
from __future__ import annotations

import shutil
from pathlib import Path

from scripts import check_role_scoped_contract as lint

REPO = Path(__file__).resolve().parents[1]
MIRROR_FILES = tuple(lint.CONTRACTS) + tuple(lint.AGENTS) + (
    lint.PROTOCOL, lint.SYNTH, lint.PANEL_CHECKER, lint.PHASE_CHECKER,
    lint.TEMPLATE,
)


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


def test_delivered_phase2_literal_mutation_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root, next(iter(lint.AGENTS)),
        "block_class: <fatal|repairable>",
        "block_kind: <fatal|repairable>",
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
        r'_SEVERITY_DECL_RE = re.compile(r"\*\*Severity(?:\*\*)?\s*:")',
        r'_SEVERITY_DECL_RE = re.compile(r"\*\*Severity\*\*:")',
    )
    assert lint.check(root)


def test_anchor_declaration_sentinel_mutation_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root,
        lint.PHASE_CHECKER,
        r'_ANCHOR_DECL_RE = re.compile(r"\*\*Evidence Anchor(?:\*\*)?\s*:")',
        r'_ANCHOR_DECL_RE = re.compile(r"\*\*Evidence Anchor\*\*:")',
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
        "may be bare or backtick-wrapped",
        "must always be bare",
    )
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
