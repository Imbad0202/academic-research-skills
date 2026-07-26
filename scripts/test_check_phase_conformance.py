"""Tests for the six Schema 13.2 phase-conformance check families."""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from scripts import check_panel_synthesis as panel
from scripts import check_phase_conformance as phase

REPO = Path(__file__).resolve().parents[1]
FULL_PATH = REPO / "shared/contracts/reviewer/full.json"
FULL = json.loads(FULL_PATH.read_text(encoding="utf-8"))


def phase1_text(role: str, overrides=None) -> str:
    overrides = overrides or {}
    lines = ["## Contract Paraphrase", "", "All dimensions understood.", "",
             "## Scoring Plan", ""]
    for dim in FULL["acceptance_dimensions"]:
        if role not in dim["eligible_roles"]:
            continue
        did = dim["id"]
        fields = {
            "dimension_id": did,
            "what_to_look_for": f"observable evidence relevant to {did}",
            "what_triggers_block":
                f"block evidence pattern for {did} requiring major repair",
            "what_triggers_warn":
                f"warn evidence pattern for {did} requiring clarification",
        }
        if dim["priority"] == "mandatory":
            fields["what_triggers_fatal"] = (
                f"fatal evidence pattern for {did} invalidating the core"
            )
        fields.update(overrides.get(did, {}))
        lines += [f"### {did}: {dim['name']}"]
        lines += [f"{key}: {value}" for key, value in fields.items()
                  if value is not None]
        lines.append("")
    lines.append("[CONTRACT-ACKNOWLEDGED]")
    return "\n".join(lines)


def phase2_text(role: str, overrides=None, body="", dissent=()) -> str:
    overrides = overrides or {}
    lines = [f"contract_role: {role}", ""]
    if dissent:
        lines += ["## Scoring Plan Dissent", ""]
        for did in dissent:
            lines += [f"dimension_id: {did}", "rationale: plan was inadequate"]
        lines.append("")
    lines += ["## Dimension Scores", ""]
    for dim in FULL["acceptance_dimensions"]:
        did = dim["id"]
        lines.append(f"### {did}: {dim['name']}")
        if role not in dim["eligible_roles"]:
            lines.append("score: not_assessed")
        else:
            value = overrides.get(did, "pass")
            if value == "warn":
                lines += [
                    "score: warn",
                    f'trigger: "warn evidence pattern for {did}"',
                ]
            elif value == "block":
                lines += [
                    "score: block", "block_class: repairable",
                    f'trigger: "block evidence pattern for {did}"',
                ]
            elif value == "fatal":
                lines += [
                    "score: block", "block_class: fatal",
                    f'trigger: "fatal evidence pattern for {did}"',
                ]
            elif value == "abstain":
                lines += [
                    "score: not_assessed",
                    "abstain_reason: materially inapplicable",
                ]
            else:
                lines.append("score: pass")
        lines.append("")
    lines += ["## Review Body", "", body]
    return "\n".join(lines)


def parse_plan(role="methodology", overrides=None):
    return phase.parse_phase1(
        "p1.md", phase1_text(role, overrides), FULL, role
    )


def parse_report(role="methodology", overrides=None, body="", dissent=()):
    text = phase2_text(role, overrides, body, dissent)
    return panel.parse_report("p2.md", text, FULL), text


def test_required_cli_flags_cannot_be_omitted():
    with pytest.raises(SystemExit) as exc:
        phase._parse_args(["--contract", str(FULL_PATH)])
    assert exc.value.code == 2


@pytest.mark.parametrize("missing", ["--role", "--manuscript", "--metadata"])
def test_each_required_context_flag_fails_closed(tmp_path, missing):
    args = write_cli_files(tmp_path, "methodology") + [
        "--role", "methodology"
    ]
    index = args.index(missing)
    del args[index:index + 2]
    with pytest.raises(SystemExit) as exc:
        phase._parse_args(args)
    assert exc.value.code == 2


def test_invalid_dispatch_role_is_contract_error(tmp_path):
    paths = write_cli_files(tmp_path, "methodology")
    assert phase.main(paths + ["--role", "writer"]) == 2


def test_role_swap_is_conformance_failure(tmp_path):
    paths = write_cli_files(tmp_path, "methodology")
    assert phase.main(paths + ["--role", "eic"]) == 3


def test_missing_fatal_trigger_fails():
    with pytest.raises(phase.ConformanceError, match="what_triggers_fatal"):
        parse_plan("methodology", {"D1": {"what_triggers_fatal": None}})


@pytest.mark.parametrize(
    "overrides",
    [
        {"what_triggers_warn": "same", "what_triggers_block": "same"},
        {"what_triggers_fatal": "same", "what_triggers_block": "same"},
        {"what_triggers_fatal": "same", "what_triggers_warn": "same"},
    ],
)
def test_all_three_trigger_collision_pairs_fail(overrides):
    with pytest.raises(phase.ConformanceError, match="TRIGGER-COLLISION"):
        parse_plan("methodology", {"D1": overrides})


def test_pairwise_distinct_triggers_pass():
    assert set(parse_plan().commitments) == {"D1", "D3"}


def test_short_trigger_is_advisory_not_failure():
    plan = parse_plan(
        "methodology",
        {"D1": {"what_triggers_warn": "short warning trigger"}},
    )
    assert any(
        "D1 what_triggers_warn has fewer than 8 words" in warning
        for warning in plan.warnings
    )


@pytest.mark.parametrize(
    "mutation",
    [
        lambda text: text.replace(
            "what_triggers_fatal:", "- what_triggers_fatal:", 1
        ),
        lambda text: text.replace(
            "what_triggers_fatal:", "what_triggers_fatal —", 1
        ),
    ],
)
def test_phase1_noncanonical_line_forms_fail(mutation):
    text = mutation(phase1_text("methodology"))
    with pytest.raises(phase.ConformanceError, match="PHASE1-GRAMMAR"):
        phase.parse_phase1("p1.md", text, FULL, "methodology")


def test_canonical_phase1_line_form_passes():
    parse_plan()


def test_manuscript_12_word_shingle_leaks():
    manuscript = (
        "alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu "
        "nu xi"
    )
    leaked = phase1_text("methodology") + (
        "\nalpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu"
    )
    with pytest.raises(phase.ConformanceError, match="MANUSCRIPT-LEAK"):
        phase.check_manuscript_leakage(leaked, manuscript, {}, FULL)


def test_metadata_title_shingle_is_exempt():
    title = "alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu"
    phase.check_manuscript_leakage(
        phase1_text("methodology") + "\n" + title,
        title + "\nBody words begin here.",
        {"title": title, "field": "testing", "word_count": 4},
        FULL,
    )


def test_trigger_text_absent_from_phase1_fails():
    report, _ = parse_report("methodology", {"D1": "warn"})
    report.scores["D1"] = panel.DimensionScore(
        "warn", trigger="a completely new threshold"
    )
    with pytest.raises(phase.ConformanceError, match="TRIGGER-DRIFT"):
        phase.check_trigger_binding(
            report, parse_plan(),
            {dim["id"]: dim for dim in FULL["acceptance_dimensions"]}, set()
        )


def test_fatal_block_cannot_bind_warn_trigger():
    report, _ = parse_report("methodology", {"D1": "fatal"})
    report.scores["D1"] = panel.DimensionScore(
        "block", "fatal", "warn evidence pattern for D1"
    )
    with pytest.raises(phase.ConformanceError, match="TRIGGER-DRIFT"):
        phase.check_trigger_binding(
            report, parse_plan(),
            {dim["id"]: dim for dim in FULL["acceptance_dimensions"]}, set()
        )


@pytest.mark.parametrize(
    "score,shared_fields",
    [
        ("fatal", ("what_triggers_block", "what_triggers_fatal")),
        ("block", ("what_triggers_block", "what_triggers_warn")),
        ("warn", ("what_triggers_warn", "what_triggers_fatal")),
    ],
)
def test_trigger_substring_must_bind_one_kind_only(score, shared_fields):
    shared = "shared evidence pattern appears"
    overrides = {
        "what_triggers_block":
            "repairable evidence pattern requires bounded revision",
        "what_triggers_warn":
            "warning evidence pattern requires clarification only",
        "what_triggers_fatal":
            "fatal evidence pattern proves the core cannot recover",
    }
    for field in shared_fields:
        overrides[field] = f"{shared} and then diverges for {field}"
    plan = parse_plan("methodology", {"D1": overrides})
    report, _ = parse_report("methodology", {"D1": score})
    report.scores["D1"] = panel.DimensionScore(
        "warn" if score == "warn" else "block",
        "fatal" if score == "fatal" else (
            "repairable" if score == "block" else None
        ),
        shared,
    )
    with pytest.raises(phase.ConformanceError, match="TRIGGER-AMBIGUOUS"):
        phase.check_trigger_binding(
            report, plan,
            {dim["id"]: dim for dim in FULL["acceptance_dimensions"]},
            set(),
        )


def test_dissent_cannot_mint_fatality():
    report, _ = parse_report(
        "methodology", {"D1": "fatal"}, dissent=("D1",)
    )
    with pytest.raises(phase.ConformanceError, match="DISSENT-FATALITY"):
        phase.check_trigger_binding(
            report, parse_plan(),
            {dim["id"]: dim for dim in FULL["acceptance_dimensions"]}, {"D1"}
        )


def test_dissent_requires_rationale():
    _, text = parse_report(
        "methodology", {"D1": "block"}, dissent=("D1",)
    )
    text = text.replace("rationale: plan was inadequate\n", "")
    with pytest.raises(phase.ConformanceError, match="requires one rationale"):
        phase.parse_dissent_dimensions(text)


def test_dissent_repairable_block_passes_binding_exemption():
    report, _ = parse_report(
        "methodology", {"D1": "block"}, dissent=("D1",)
    )
    phase.check_trigger_binding(
        report, parse_plan(),
        {dim["id"]: dim for dim in FULL["acceptance_dimensions"]}, {"D1"}
    )


def test_two_dissent_dimensions_fail():
    report, _ = parse_report(
        "methodology", dissent=("D1", "D3")
    )
    with pytest.raises(phase.ConformanceError, match="multi_dissent"):
        phase.check_trigger_binding(
            report, parse_plan(),
            {dim["id"]: dim for dim in FULL["acceptance_dimensions"]},
            {"D1", "D3"},
        )


def test_fatal_trigger_for_nonmandatory_dimension_fails():
    text = phase1_text("eic").replace(
        "what_triggers_warn: warn evidence pattern for D5 requiring clarification",
        "what_triggers_warn: warn evidence pattern for D5 requiring clarification\n"
        "what_triggers_fatal: forbidden fatal trigger",
    )
    with pytest.raises(phase.ConformanceError, match="forbidden"):
        phase.parse_phase1("p1.md", text, FULL, "eic")


def test_nonmandatory_block_class_fails_phase_checker(tmp_path):
    args = write_cli_files(tmp_path, "perspective")
    phase2_path = Path(args[args.index("--phase2") + 1])
    text = phase2_path.read_text(encoding="utf-8").replace(
        "### D4: cross_disciplinary_relevance\nscore: pass",
        "### D4: cross_disciplinary_relevance\n"
        "score: block\n"
        "block_class: repairable\n"
        'trigger: "block trigger"',
    )
    phase2_path.write_text(text, encoding="utf-8")
    assert phase.main(args + ["--role", "perspective"]) == 3


@pytest.mark.parametrize(
    "body",
    [
        "### W1\n**Severity**: Critical\n**Problem**: no anchor",
        "### W1\n**Severity**: Major\n**Evidence Anchor**: text: "
        "\"one two three four five six seven eight nine ten eleven twelve "
        "thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty "
        "twentyone twentytwo twentythree twentyfour twentyfive twentysix\"",
        "### W1\n**Severity**: Critical\n**Evidence Anchor**: absence:",
    ],
)
def test_critical_major_anchor_failures(body):
    report, _ = parse_report("eic", body=body)
    with pytest.raises(phase.ConformanceError):
        phase.check_scoring_seat_anchors(report)


@pytest.mark.parametrize(
    "body",
    [
        '### W1\n**Severity**: Critical\n'
        '**Evidence Anchor**: text: "short exact quote" p. 2',
        "### W1\n**Severity**: Major\n"
        "**Evidence Anchor**: absence: checked Methods, appendix, and supplement",
    ],
)
def test_compliant_critical_major_anchors_pass(body):
    report, _ = parse_report("eic", body=body)
    phase.check_scoring_seat_anchors(report)


def test_two_findings_cannot_share_one_anchor():
    body = (
        "### W1: first\n"
        "**Severity**: Critical\n"
        '**Evidence Anchor**: text: "first quote" p. 1\n'
        "**Severity**: Major\n"
        "### W2: second\n"
        "**Severity**: Major"
    )
    report, _ = parse_report("eic", body=body)
    with pytest.raises(phase.ConformanceError):
        phase.check_scoring_seat_anchors(report)


def test_two_independently_anchored_findings_pass():
    body = (
        "### W1: first\n"
        "**Severity**: Critical\n"
        '**Evidence Anchor**: text: "first quote" p. 1\n'
        "### W2: second\n"
        "**Severity**: Major\n"
        "**Evidence Anchor**: absence: checked Methods and appendix"
    )
    report, _ = parse_report("eic", body=body)
    phase.check_scoring_seat_anchors(report)


def test_multiple_minor_severities_in_one_finding_fail():
    body = """### W1: bundled minor findings
**Severity**: Minor
first
**Severity**: Minor
second"""
    report, _ = parse_report("eic", body=body)
    with pytest.raises(phase.ConformanceError, match="FINDING-GRAMMAR"):
        phase.check_scoring_seat_anchors(report)


def test_flat_severity_without_finding_heading_fails():
    report, _ = parse_report(
        "eic",
        body=(
            "**Severity**: Critical\n"
            '**Evidence Anchor**: text: "quote" p. 1'
        ),
    )
    with pytest.raises(phase.ConformanceError, match="own ### finding"):
        phase.check_scoring_seat_anchors(report)


def test_missing_review_body_fails_anchor_family():
    report, _ = parse_report("eic")
    report.text = report.text.replace("## Review Body", "## Commentary")
    with pytest.raises(phase.ConformanceError, match="REVIEW-BODY-MISSING"):
        phase.check_scoring_seat_anchors(report)


def da_text(ids=("C1",), anchors=None):
    anchors = anchors or {finding_id: 'text: "quote" p. 1' for finding_id in ids}
    rows = "\n".join(
        f"| {finding_id} | Issue | {anchors.get(finding_id, '')} |"
        for finding_id in ids
    )
    return phase2_text(
        "da",
        body=(
            "#### CRITICAL\n"
            "| # | Issue | Evidence Anchor |\n"
            "|---|-------|-----------------|\n" + rows + "\n\n"
            "#### MAJOR\n"
            "| # | Issue | Evidence Anchor |\n"
            "|---|-------|-----------------|"
        ),
    )


def test_da_empty_critical_anchor_fails():
    report = panel.parse_report("da.md", da_text(anchors={"C1": ""}), FULL)
    with pytest.raises(phase.ConformanceError, match="ANCHOR-MISSING"):
        phase.check_da_anchors(report)


def test_da_ids_must_be_dense():
    report = panel.parse_report("da.md", da_text(ids=("C2",)), FULL)
    with pytest.raises(phase.ConformanceError, match="dense"):
        phase.check_da_anchors(report)


def test_da_conforming_table_passes():
    report = panel.parse_report("da.md", da_text(ids=("C1", "C2")), FULL)
    phase.check_da_anchors(report)


@pytest.mark.parametrize(
    "old,new,fragment",
    [
        ("#### CRITICAL", "#### Critical", "DA-CRITICAL-PARSE"),
        ("#### MAJOR", "#### Major", "DA-MAJOR-PARSE"),
        ("#### MAJOR", "#### MAJOR\n\n#### MAJOR", "DA-MAJOR-PARSE"),
    ],
)
def test_da_required_sections_fail_closed(old, new, fragment):
    report = panel.parse_report(
        "da.md", da_text().replace(old, new, 1), FULL
    )
    with pytest.raises(
        (phase.ConformanceError, phase.panel.ReportError), match=re.escape(fragment)
    ):
        phase.check_da_anchors(report)


def write_cli_files(tmp_path: Path, role: str) -> list[str]:
    phase1 = tmp_path / "p1.md"
    phase2 = tmp_path / "p2.md"
    manuscript = tmp_path / "m.md"
    metadata = tmp_path / "meta.json"
    phase1.write_text(phase1_text(role), encoding="utf-8")
    phase2.write_text(phase2_text(role), encoding="utf-8")
    manuscript.write_text("short synthetic manuscript", encoding="utf-8")
    metadata.write_text(json.dumps({
        "title": "Synthetic", "field": "testing", "word_count": 3
    }), encoding="utf-8")
    return [
        "--contract", str(FULL_PATH),
        "--phase1", str(phase1),
        "--phase2", str(phase2),
        "--manuscript", str(manuscript),
        "--metadata", str(metadata),
    ]


def test_full_cli_pass(tmp_path):
    assert phase.main(
        write_cli_files(tmp_path, "methodology") + ["--role", "methodology"]
    ) == 0
