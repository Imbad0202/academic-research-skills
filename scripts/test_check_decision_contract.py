"""Mutation tests for check_decision_contract.py."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from scripts import check_decision_contract as lint

REPO = Path(__file__).resolve().parents[1]
MIRROR_FILES = lint.LIVE_FILES + lint.CONTRACTS + (
    lint.QUALITY, lint.STANDARDS, lint.SKILL,
)


def mirror(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    # The checker intentionally scans these live rule trees recursively.
    for rel in lint.LIVE_ROOTS:
        shutil.copytree(REPO / rel, root / rel)
    for rel in MIRROR_FILES:
        destination = root / rel
        if destination.exists():
            continue
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


def test_schema_enum_mutation_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root, lint.SCHEMA,
        '"editorial_decision=minor_revision"',
        '"editorial_decision=revise"',
    )
    assert lint.check(root)


def test_action_enum_extra_value_mutation_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root,
        lint.PANEL,
        '    "editorial_decision=reject",',
        '    "editorial_decision=reject",\n    "editorial_decision=revise",',
    )
    assert lint.check(root)


def test_schema6_enum_extra_value_mutation_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root,
        lint.HANDOFF,
        '`"Major Revision"` / `"Reject"` |',
        '`"Major Revision"` / `"Reject"` / `"Revise"` |',
    )
    assert lint.check(root)


@pytest.mark.parametrize(
    ("field", "replacement"),
    (
        ("condition_id", "FX"),
        ("severity", 61),
        ("cross_reviewer_quantifier", "all"),
        ("expression", "any normal dimension scores 'block'"),
        ("action", "editorial_decision=minor_revision"),
    ),
)
def test_shipped_condition_tuple_field_mutation_fails(
    tmp_path, field, replacement
):
    root = mirror(tmp_path)
    path = root / lint.CONTRACTS[0]
    contract = json.loads(path.read_text(encoding="utf-8"))
    condition = next(
        item for item in contract["failure_conditions"]
        if item["condition_id"] == "F4"
    )
    condition[field] = replacement
    path.write_text(json.dumps(contract), encoding="utf-8")
    assert lint.check(root)


def test_hybrid_token_on_live_agent_surface_fails(tmp_path):
    root = mirror(tmp_path)
    rel = "academic-paper-reviewer/agents/eic_agent.md"
    mutate(
        root, rel,
        "## Expertise Configuration",
        "reject_or_major_revision\n\n## Expertise Configuration",
    )
    assert lint.check(root)


def test_authority_row_mutation_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(root, lint.STANDARDS, "`quick`", "`fast`")
    assert lint.check(root)


@pytest.mark.parametrize(
    ("old", "new"),
    (
        ("`full` (sprint contract)", "`complete` (sprint contract)"),
        (
            "Mechanical synthesizer over reviewer contract v2; the matrix "
            "below never overrides it",
            "The qualitative matrix overrides the mechanical synthesizer",
        ),
        ("`block/warn/pass` + `block_class`", "reviewer recommendations"),
        (
            "| Accept / Minor Revision / Major Revision / Reject |",
            "| advisory signal |",
        ),
    ),
)
def test_authority_table_cell_mutation_fails(tmp_path, old, new):
    root = mirror(tmp_path)
    mutate(root, lint.STANDARDS, old, new)
    assert lint.check(root)


@pytest.mark.parametrize(
    "extra_row",
    (
        "`full` (sprint contract) | The matrix overrides mechanics | "
        "reviewer recommendations | four-value enum",
        "| `full` (sprint contract) | The matrix overrides mechanics | "
        "reviewer recommendations | four-value enum | ignored |",
    ),
)
def test_authority_table_extra_gfm_row_fails(tmp_path, extra_row):
    root = mirror(tmp_path)
    mutate(
        root,
        lint.STANDARDS,
        "| `calibration` |",
        f"{extra_row}\n| `calibration` |",
    )
    assert lint.check(root)


def test_retired_threshold_row_is_prohibited_in_quality_rubric(tmp_path):
    root = mirror(tmp_path)
    path = root / lint.QUALITY
    path.write_text(
        path.read_text(encoding="utf-8") + "\n| 65-79 | Minor Revision |\n",
        encoding="utf-8",
    )
    assert lint.check(root)


def test_retired_accept_mapping_is_prohibited_in_quality_rubric(tmp_path):
    root = mirror(tmp_path)
    path = root / lint.QUALITY
    path.write_text(
        path.read_text(encoding="utf-8") + "\n| >= 80 | Accept |\n",
        encoding="utf-8",
    )
    assert lint.check(root)


def test_retired_mapping_prose_is_prohibited_in_quality_rubric(tmp_path):
    root = mirror(tmp_path)
    path = root / lint.QUALITY
    path.write_text(
        path.read_text(encoding="utf-8")
        + "\nA rubric score of 80 or higher means Accept.\n",
        encoding="utf-8",
    )
    assert lint.check(root)


def test_threshold_duplicated_on_other_live_surface_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root,
        lint.STANDARDS,
        "## 0. Decision Authority by Mode",
        "Minor Revision threshold: 65-79\n\n## 0. Decision Authority by Mode",
    )
    assert lint.check(root)


@pytest.mark.parametrize(
    "wording",
    (
        "Accept applies to scores of 80 points or higher.",
        "Accept applies to a score of 80 or higher.",
        "Minor Revision applies to 65 points and above.",
        "Minor Revision begins with 65 or above.",
        "Major Revision applies to 50 points and above.",
        "Major Revision covers 50 and higher.",
        "Minor Revision starts at 65.",
        "Accept requires a composite of 80 out of 100.",
        "Accept: 80 points.",
        "Minor Revision = 65.",
        "Major Revision — 50 points.",
        "Reject applies below 50 points.",
        "| ≥ 80 | Accept |",
        "| 80-100 | Accept |",
        "A score of 80 or higher leads to Accept.",
        "A result of 50 out of 100 means Major Revision.",
        "Scores of 80 and above map to Accept.",
        "80 or higher is the Accept band.",
        "A composite of 65 or more earns Minor Revision.",
        "Accept requires 80 or more.",
        "Accept requires 80 points.",
        "At or above 80, the decision is Accept.",
        "The Accept band opens at 80 points.",
        "| Accept | 80 or better |",
        "Accept: no lower than 80.",
        "Minor Revision spans 65 through 79.",
        "Major Revision covers the 50 to 64 band.",
        "Accept 80/100 and above the line.",
        "Reject when the score falls beneath 50.",
        "A rubric score of 80 qualifies for Accept.",
    ),
)
def test_equivalent_threshold_wording_on_live_surface_fails(tmp_path, wording):
    root = mirror(tmp_path)
    mutate(
        root,
        lint.STANDARDS,
        "## 0. Decision Authority by Mode",
        f"{wording}\n\n## 0. Decision Authority by Mode",
    )
    assert lint.check(root)


@pytest.mark.parametrize(
    "wording",
    (
        "### Accept\n**Criteria**:\n- Weighted average ≥ 80",
        "### Major Revision\n#### Criteria\n- Weighted average 50–64",
    ),
)
def test_threshold_in_decision_heading_section_fails(tmp_path, wording):
    root = mirror(tmp_path)
    mutate(
        root,
        lint.STANDARDS,
        "## 0. Decision Authority by Mode",
        f"{wording}\n\n## 0. Decision Authority by Mode",
    )
    assert lint.check(root)


@pytest.mark.parametrize(
    "wording",
    (
        "**Accept**\n- Weighted average of 80 or higher",
        "**Minor Revision**\n- 65 points and above",
        "- Accept\n  - score of 80 or higher",
        (
            "| Accept | Minor Revision | Major Revision | Reject |\n"
            "|---|---|---|---|\n"
            "| 80 or higher | 65 or higher | 50 or higher | below 50 |"
        ),
    ),
)
def test_cross_line_threshold_relocation_fails(tmp_path, wording):
    root = mirror(tmp_path)
    mutate(
        root,
        lint.STANDARDS,
        "## 0. Decision Authority by Mode",
        f"{wording}\n\n## 0. Decision Authority by Mode",
    )
    assert lint.check(root)


def test_unrelated_decision_count_does_not_false_positive(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root,
        lint.STANDARDS,
        "## 0. Decision Authority by Mode",
        "The calibration decision reviewed at least 80 submissions.\n\n"
        "## 0. Decision Authority by Mode",
    )
    assert lint.check(root) == []


def test_decision_label_with_unrelated_count_does_not_false_positive(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root,
        lint.STANDARDS,
        "## 0. Decision Authority by Mode",
        "Accept reviewers examined 80 submissions.\n\n"
        "## 0. Decision Authority by Mode",
    )
    assert lint.check(root) == []


def test_unrelated_numeric_range_does_not_false_positive(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root,
        lint.STANDARDS,
        "## 0. Decision Authority by Mode",
        "The panel reviewed 50 - 64 submissions before making a decision.\n\n"
        "## 0. Decision Authority by Mode",
    )
    assert lint.check(root) == []


def test_unrelated_word_range_does_not_false_positive(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root,
        lint.STANDARDS,
        "## 0. Decision Authority by Mode",
        "The audit covered 50 to 64 submissions before deliberation.\n\n"
        "## 0. Decision Authority by Mode",
    )
    assert lint.check(root) == []


@pytest.mark.parametrize(
    "wording",
    (
        "Minor Revision spans 65 - 79 points.",
        "Major Revision covers 50–64 points.",
        "Scores of 50 — 64 require Major Revision.",
    ),
)
def test_decision_linked_numeric_range_fails(tmp_path, wording):
    root = mirror(tmp_path)
    mutate(
        root,
        lint.STANDARDS,
        "## 0. Decision Authority by Mode",
        f"{wording}\n\n## 0. Decision Authority by Mode",
    )
    assert lint.check(root)


def test_retired_one_to_five_threshold_in_standards_fails(tmp_path):
    root = mirror(tmp_path)
    mutate(
        root, lint.STANDARDS,
        "Every applicable core criterion is positively verified",
        "Average score >= 4.0",
    )
    assert lint.check(root)


def test_re_review_reintroduced_score_rule_still_fails(tmp_path):
    """#576 exemption is literal-scoped, not file-scoped: masking the
    sanctioned §6 item-proportion literals must NOT exempt the re-review
    protocol from the 0-100 score-scale residency rule."""
    root = mirror(tmp_path)
    mutate(
        root, lint.RE_REVIEW_PROTOCOL,
        "### Legacy Mode",
        "Accept requires a composite score of 80 or higher.\n\n### Legacy Mode",
    )
    errors = lint.check(root)
    assert any(lint.RE_REVIEW_PROTOCOL in e for e in errors), errors


def test_re_review_sanctioned_literals_alone_pass(tmp_path):
    """The shipped protocol (sanctioned literals present, nothing else)
    passes — pinned separately so the masking list cannot silently shrink."""
    root = mirror(tmp_path)
    text = (root / lint.RE_REVIEW_PROTOCOL).read_text(encoding="utf-8")
    for literal in lint.RE_REVIEW_SANCTIONED_LITERALS:
        assert literal in text, f"sanctioned literal missing from protocol: {literal!r}"
    assert lint.check(root) == []
