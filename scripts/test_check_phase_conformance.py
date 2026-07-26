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


def test_malformed_fence_closer_keeps_phase1_plan_hidden():
    text = "```text\n```not-a-close\n" + phase1_text("eic") + "\n```\n"
    with pytest.raises(phase.ConformanceError, match="Scoring Plan required"):
        phase.parse_phase1("p1.md", text, FULL, "eic")


@pytest.mark.parametrize("separator", ("\x85", "\u2028", "\u2029"))
def test_unicode_separator_keeps_phase1_plan_fenced(separator):
    text = "```text\n```" + separator + phase1_text("eic") + "\n```\n"
    with pytest.raises(phase.ConformanceError, match="Scoring Plan required"):
        phase.parse_phase1("hidden-p1.md", text, FULL, "eic")


def test_manuscript_12_word_shingle_leaks():
    manuscript = (
        "alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu "
        "nu xi"
    )
    leaked = phase1_text("methodology") + (
        "\nalpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu"
    )
    with pytest.raises(phase.ConformanceError, match="MANUSCRIPT-LEAK"):
        phase.check_manuscript_leakage(
            leaked,
            manuscript,
            {"title": "Synthetic", "field": "testing", "word_count": 14},
            FULL,
        )


def test_metadata_title_shingle_is_exempt():
    title = "alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu"
    phase.check_manuscript_leakage(
        phase1_text("methodology") + "\n" + title,
        title + "\nBody words begin here.",
        {"title": title, "field": "testing", "word_count": 4},
        FULL,
    )


@pytest.mark.parametrize(
    "metadata",
    [
        {
            "title": "Synthetic",
            "field": "testing",
            "word_count": 12,
            "unexpected_body": (
                "alpha beta gamma delta epsilon zeta eta theta iota "
                "kappa lambda mu"
            ),
        },
        {"title": "Synthetic", "field": "testing"},
        {"title": "Synthetic", "field": "testing", "word_count": True},
    ],
)
def test_metadata_envelope_shape_fails_closed(metadata):
    with pytest.raises(phase.panel.ContractError, match="METADATA-INVALID"):
        phase.validate_metadata_envelope(metadata)


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


def test_trigger_binding_rechecks_required_trigger_defence_in_depth():
    report, _ = parse_report("methodology", {"D1": "warn"})
    report.scores["D1"] = panel.DimensionScore("warn")
    with pytest.raises(phase.ConformanceError, match="TRIGGER-GRAMMAR"):
        phase.check_trigger_binding(
            report,
            parse_plan(),
            {dim["id"]: dim for dim in FULL["acceptance_dimensions"]},
            set(),
        )


@pytest.mark.parametrize(
    "role,did,value",
    (
        ("methodology", "D1", panel.DimensionScore(
            "pass", trigger="surplus post hoc trigger"
        )),
        ("eic", "D1", panel.DimensionScore(
            "not_assessed", trigger="surplus structural trigger"
        )),
    ),
)
def test_trigger_binding_rechecks_surplus_trigger_defence_in_depth(
    role, did, value
):
    report, _ = parse_report(role)
    report.scores[did] = value
    with pytest.raises(phase.ConformanceError, match="TRIGGER-GRAMMAR"):
        phase.check_trigger_binding(
            report,
            parse_plan(role),
            {dim["id"]: dim for dim in FULL["acceptance_dimensions"]},
            set(),
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


def test_late_dissent_fails_closed_at_cli_boundary(tmp_path):
    args = write_cli_files(tmp_path, "methodology")
    phase2_path = Path(args[args.index("--phase2") + 1])
    text = phase2_text(
        "methodology", {"D1": "block"}, dissent=("D1",)
    )
    dissent_block = (
        "## Scoring Plan Dissent\n\n"
        "dimension_id: D1\n"
        "rationale: plan was inadequate\n\n"
    )
    text = text.replace(dissent_block, "", 1).replace(
        "## Review Body",
        f"{dissent_block}## Review Body",
        1,
    ).replace(
        'trigger: "block evidence pattern for D1"',
        'trigger: "novel post hoc trigger"',
        1,
    )
    phase2_path.write_text(text, encoding="utf-8")
    assert phase.main(args + ["--role", "methodology"]) == \
        phase.EXIT_CONFORMANCE


def test_dissent_must_name_a_dimension_committed_by_the_seat():
    report, _ = parse_report("methodology", dissent=("D2",))
    with pytest.raises(
        phase.ConformanceError, match="not committed by this seat"
    ):
        phase.check_trigger_binding(
            report, parse_plan(),
            {dim["id"]: dim for dim in FULL["acceptance_dimensions"]},
            {"D2"},
        )


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
        "### W1: no anchor\n**Severity**: Critical\n**Problem**: no anchor",
        "### W1: long quote\n**Severity**: Major\n**Evidence Anchor**: text: "
        "\"one two three four five six seven eight nine ten eleven twelve "
        "thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty "
        "twentyone twentytwo twentythree twentyfour twentyfive twentysix\"",
        "### W1: empty absence\n**Severity**: Critical\n"
        "**Evidence Anchor**: absence:",
    ],
)
def test_critical_major_anchor_failures(body):
    report, _ = parse_report("eic", body=body)
    with pytest.raises(phase.ConformanceError):
        phase.check_scoring_seat_anchors(report)


@pytest.mark.parametrize(
    "body",
    [
        '### W1: quoted defect\n**Severity**: Critical\n'
        '**Evidence Anchor**: text: "short exact quote" p. 2',
        "### W1: missing surfaces\n**Severity**: Major\n"
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


def test_same_line_duplicate_severity_declarations_fail():
    body = (
        "### W1: hidden critical\n"
        "**Severity**: Minor and **Severity**: Critical"
    )
    report, _ = parse_report("eic", body=body)
    with pytest.raises(phase.ConformanceError, match="FINDING-GRAMMAR"):
        phase.check_scoring_seat_anchors(report)


def test_noncanonical_heading_and_severity_label_fail_together():
    body = (
        "### Weakness 1: fabricated denominators\n"
        "**Severity:** Critical"
    )
    report, _ = parse_report("eic", body=body)
    with pytest.raises(phase.ConformanceError, match="FINDING-GRAMMAR"):
        phase.check_scoring_seat_anchors(report)


def test_same_line_duplicate_anchor_declarations_fail():
    body = (
        "### W1: duplicate anchors\n"
        "**Severity**: Critical\n"
        '**Evidence Anchor**: text: "first" and '
        '**Evidence Anchor**: text: "second"'
    )
    report, _ = parse_report("eic", body=body)
    with pytest.raises(phase.ConformanceError, match="ANCHOR-MISSING"):
        phase.check_scoring_seat_anchors(report)


def test_same_line_duplicate_minor_anchor_declarations_fail():
    body = (
        "### W1: duplicate optional anchors\n"
        "**Severity**: Minor\n"
        '**Evidence Anchor**: text: "first" and '
        '**Evidence Anchor**: text: "second"'
    )
    report, _ = parse_report("eic", body=body)
    with pytest.raises(phase.ConformanceError, match="FINDING-GRAMMAR"):
        phase.check_scoring_seat_anchors(report)


def test_malformed_minor_anchor_declaration_fails():
    body = (
        "### W1: malformed optional anchor\n"
        "**Severity**: Minor\n"
        '**Evidence Anchor:** text: "quote"'
    )
    report, _ = parse_report("eic", body=body)
    with pytest.raises(phase.ConformanceError, match="FINDING-GRAMMAR"):
        phase.check_scoring_seat_anchors(report)


def test_indented_bullet_fields_still_enforce_anchor_gate():
    body = """### W1: indented finding
  - **Severity**: Critical
  - **Confidence**: 5 — core expertise"""
    report, _ = parse_report("eic", body=body)
    with pytest.raises(phase.ConformanceError, match="ANCHOR-MISSING"):
        phase.check_scoring_seat_anchors(report)


def test_backticked_template_anchor_is_normalised_and_accepted():
    body = (
        "### W1: template-shaped finding\n"
        "**Severity**: Critical\n"
        "**Evidence Anchor**: `text: §5 \"short exact quote\"`"
    )
    report, _ = parse_report("eic", body=body)
    phase.check_scoring_seat_anchors(report)


def test_combined_template_fields_are_parsed():
    body = (
        "### W1: combined fields\n"
        "  - **Severity**: Major | **Evidence Anchor**: "
        "`absence: checked Methods and appendix` | "
        "**Confidence**: 4 — core expertise"
    )
    report, _ = parse_report("eic", body=body)
    phase.check_scoring_seat_anchors(report)


def test_h4_finding_under_generic_h3_fails():
    body = (
        "### Commentary\n"
        "#### W1: hidden finding\n"
        "**Severity**: Critical\n"
        '**Evidence Anchor**: text: "quote" p. 1'
    )
    report, _ = parse_report("eic", body=body)
    with pytest.raises(phase.ConformanceError, match="own ### W<n>"):
        phase.check_scoring_seat_anchors(report)


def test_severity_outside_review_body_fails():
    report, text = parse_report("eic")
    report.text = text + (
        "\n## Appendix\n### W1: misplaced\n"
        "**Severity**: Critical\n"
        '**Evidence Anchor**: text: "quote" p. 1'
    )
    with pytest.raises(phase.ConformanceError, match="outside"):
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


@pytest.mark.parametrize("label", ("severity", "sEvErItY"))
def test_case_variant_severity_without_finding_heading_fails(label):
    report, _ = parse_report(
        "eic",
        body=f"Commentary line with **{label}**: Critical",
    )
    with pytest.raises(phase.ConformanceError, match="own ### finding"):
        phase.check_scoring_seat_anchors(report)


@pytest.mark.parametrize("label", ("evidence anchor", "eViDeNcE aNcHoR"))
def test_case_variant_optional_anchor_declaration_fails(label):
    report, _ = parse_report(
        "eic",
        body=(
            "### W1: malformed optional anchor\n"
            "**Severity**: Minor\n"
            f'**{label}**: text: "quote"'
        ),
    )
    with pytest.raises(phase.ConformanceError, match="FINDING-GRAMMAR"):
        phase.check_scoring_seat_anchors(report)


def test_missing_review_body_fails_anchor_family():
    report, _ = parse_report("eic")
    report.text = report.text.replace("## Review Body", "## Commentary")
    with pytest.raises(phase.ConformanceError, match="REVIEW-BODY-MISSING"):
        phase.check_scoring_seat_anchors(report)


def da_text(ids=("C1",), anchors=None, major_rows=()):
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
            "|---|-------|-----------------|\n" + "\n".join(major_rows)
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
        (
            "| # | Issue | Evidence Anchor |",
            "| # | # | Evidence Anchor |",
            "exactly one #",
        ),
        (
            "| # | Issue | Evidence Anchor |",
            "| # | Evidence Anchor | Evidence Anchor |",
            "exactly one #",
        ),
        (
            "| # | Issue | Evidence Anchor |",
            "| ID | Issue | Anchor |",
            "missing table header",
        ),
        ("| C2 | Issue |", "| C1 | Issue |", "duplicate CRITICAL ID"),
        ("| C2 | Issue |", "| X2 | Issue |", "invalid CRITICAL ID"),
    ],
)
def test_da_header_and_critical_id_gates_fail_phase_checker(
    old, new, fragment
):
    report = panel.parse_report(
        "da.md", da_text(ids=("C1", "C2")).replace(old, new, 1), FULL
    )
    with pytest.raises(
        (panel.ReportError, phase.panel.ReportError, phase.ConformanceError),
        match=fragment,
    ):
        phase.check_da_anchors(report)


def test_da_shadow_table_fails_phase_checker():
    canonical = (
        '| # | Issue | Evidence Anchor |\n'
        '|---|-------|-----------------|\n'
        '| C1 | Issue | text: "quote" p. 1 |'
    )
    shadowed = (
        '| ID | Issue | Anchor |\n'
        '|---|-------|--------|\n'
        '| C1 | Issue | text: "quoted evidence" p. 1 |\n\n'
        '| # | Issue | Evidence Anchor |\n'
        '|---|-------|-----------------|'
    )
    report = panel.parse_report(
        "da.md", da_text(ids=("C1",)).replace(canonical, shadowed, 1), FULL
    )
    with pytest.raises(phase.ConformanceError, match="first nonblank line"):
        phase.check_da_anchors(report)


def test_da_standalone_critical_fails_phase_checker():
    text = da_text().replace(
        "#### CRITICAL",
        "### Further adversarial challenge\n"
        "- **Severity**: Critical | **Confidence**: 5 (statistics)\n\n"
        "#### CRITICAL",
        1,
    )
    report = panel.parse_report("da.md", text, FULL)
    with pytest.raises(phase.ConformanceError, match="standalone Severity"):
        phase.check_da_anchors(report)


@pytest.mark.parametrize("label", ("severity", "sEvErItY"))
def test_da_case_variant_standalone_critical_fails_phase_checker(label):
    text = da_text().replace(
        "#### CRITICAL",
        "### Further adversarial challenge\n"
        f"This is **{label}**: Critical and no revision cures it.\n\n"
        "#### CRITICAL",
        1,
    )
    report = panel.parse_report("da.md", text, FULL)
    with pytest.raises(phase.ConformanceError, match="standalone Severity"):
        phase.check_da_anchors(report)


def test_da_extra_issue_table_band_fails_phase_checker():
    text = da_text().replace(
        "#### MAJOR",
        "#### ADDITIONAL CRITICAL FINDINGS\n"
        "| # | Issue | Evidence Anchor |\n"
        "|---|-------|-----------------|\n"
        '| C1 | impossible df | text: "n=41" p. 4 |\n\n'
        "#### MAJOR",
        1,
    )
    report = panel.parse_report("da.md", text, FULL)
    with pytest.raises(
        phase.ConformanceError, match="unexpected issue-table band"
    ):
        phase.check_da_anchors(report)


@pytest.mark.parametrize(
    ("lead_in", "header"),
    (
        ("The following issues invalidate the claim:\n\n",
         "| # | Issue | Evidence Anchor |"),
        ("", "| # | Issue | evidence anchor |"),
        ("", "# | Issue | Evidence Anchor"),
    ),
)
def test_da_disguised_extra_issue_table_band_fails_phase_checker(
    lead_in, header
):
    text = da_text().replace(
        "#### MAJOR",
        "#### ADDITIONAL CRITICAL FINDINGS\n"
        f"{lead_in}{header}\n"
        "|---|-------|-----------------|\n"
        '| C9 | impossible df | text: "n=41" p. 4 |\n\n'
        "#### MAJOR",
        1,
    )
    report = panel.parse_report("da.md", text, FULL)
    with pytest.raises(
        phase.ConformanceError, match="unexpected issue-table band"
    ):
        phase.check_da_anchors(report)


@pytest.mark.parametrize("placement", ("preamble", "extra_h2"))
def test_da_issue_table_outside_canonical_bands_fails_phase(placement):
    table = (
        "| # | Issue | Evidence Anchor |\n"
        "|---|-------|-----------------|\n"
        '| C9 | impossible df | text: "n=41" p. 4 |\n'
    )
    text = da_text()
    if placement == "preamble":
        text = text.replace("#### CRITICAL", table + "\n#### CRITICAL", 1)
    else:
        text += "\n## Appendix\n" + table
    report = panel.parse_report("da.md", text, FULL)
    with pytest.raises(phase.ConformanceError, match="unexpected issue-table"):
        phase.check_da_anchors(report)


def test_da_internal_header_whitespace_fails_phase_checker():
    text = da_text().replace(
        "#### MAJOR",
        "#### ADDITIONAL CRITICAL FINDINGS\n"
        "# | Issue | Evidence   Anchor\n"
        "---|-------|-----------------\n"
        'C9 | impossible df | text: "n=41" p. 4\n\n'
        "#### MAJOR",
        1,
    )
    report = panel.parse_report("da.md", text, FULL)
    with pytest.raises(phase.ConformanceError, match="unexpected issue-table"):
        phase.check_da_anchors(report)


@pytest.mark.parametrize(
    "header",
    (
        "| ID | Issue | Evidence Anchor |",
        "| # | Issue | Evidence |",
        "| **#** | Issue | **Evidence Anchor** |",
        "| `#` | Issue | `Evidence Anchor` |",
    ),
)
def test_da_partial_or_formatted_issue_header_fails_phase(header):
    text = da_text().replace(
        "#### MAJOR",
        "#### ADDITIONAL CRITICAL FINDINGS\n"
        f"{header}\n"
        "|---|-------|-----------------|\n"
        '| C9 | impossible df | text: "n=41" p. 4 |\n\n'
        "#### MAJOR",
        1,
    )
    report = panel.parse_report("da.md", text, FULL)
    with pytest.raises(phase.ConformanceError, match="unexpected issue-table"):
        phase.check_da_anchors(report)


@pytest.mark.parametrize(
    "header",
    (
        "| ID | Issue | [Evidence Anchor][anchor] |",
        r"| \# | Issue | Evidence |",
        '| ID | Issue | <span title="x>y">Evidence Anchor</span> |',
    ),
)
def test_da_commonmark_visible_issue_header_fails_phase(header):
    text = da_text().replace(
        "#### MAJOR",
        "#### ADDITIONAL CRITICAL FINDINGS\n"
        f"{header}\n"
        "|---|-------|-----------------|\n"
        '| C9 | impossible df | text: "n=41" p. 4 |\n\n'
        "#### MAJOR",
        1,
    )
    report = panel.parse_report("da.md", text, FULL)
    with pytest.raises(phase.ConformanceError, match="unexpected issue-table"):
        phase.check_da_anchors(report)


def test_da_balanced_link_destination_header_fails_phase():
    header = (
        r"| [\#](<https://x.test/a(b)>) | Issue | "
        r"[Evidence Anchor](<https://x.test/a(b)>) |"
    )
    text = da_text().replace(
        "#### MAJOR",
        "#### ADDITIONAL CRITICAL FINDINGS\n"
        f"{header}\n"
        "|---|-------|-----------------|\n"
        '| C9 | impossible df | text: "n=41" p. 4 |\n\n'
        "#### MAJOR",
        1,
    )
    report = panel.parse_report("da.md", text, FULL)
    with pytest.raises(phase.ConformanceError, match="unexpected issue-table"):
        phase.check_da_anchors(report)


def test_da_typed_anchor_payload_alone_fails_phase():
    header = (
        r"| [\#](<https://x.test/a(b)>) | Issue | "
        r"[Evidence Anchor](<https://x.test/a(b)>) |"
    )
    text = da_text().replace(
        "#### MAJOR",
        "#### ADDITIONAL CRITICAL FINDINGS\n"
        f"{header}\n"
        "|---|-------|-----------------|\n"
        '| 1 | impossible df | `text: "n=41" p. 4` |\n\n'
        "#### MAJOR",
        1,
    )
    report = panel.parse_report("da.md", text, FULL)
    with pytest.raises(phase.ConformanceError, match="unexpected issue-table"):
        phase.check_da_anchors(report)


def test_da_escaped_pipe_cell_evasion_fails_phase():
    block = (
        "#### ADDITIONAL CRITICAL FINDINGS\n"
        r"| [\#<!--\|-->](https://x.test) | Issue | "
        r"[Evidence<!--\|--> Anchor](https://x.test) |" "\n"
        "|---|---|---|\n"
        r"| [C<!--\|-->9](https://x.test) | impossible df | "
        r'[text<!--\|-->: "n=41" p. 4](https://x.test) |' "\n\n"
    )
    text = da_text().replace("#### MAJOR", block + "#### MAJOR", 1)
    report = panel.parse_report("da.md", text, FULL)
    with pytest.raises(phase.ConformanceError, match="unexpected issue-table"):
        phase.check_da_anchors(report)


@pytest.mark.parametrize(
    "invisible", ("\u0600", "\u200b", "\u034f", "\ufe0e", "\u3164", "\ufff0")
)
def test_da_invisible_issue_payload_fails_phase(invisible):
    block = (
        "#### ADDITIONAL CRITICAL FINDINGS\n"
        f"| #{invisible} | Issue | Evidence{invisible} Anchor |\n"
        "|---|---|---|\n"
        f'| C{invisible}9 | impossible df | text{invisible}: "n=41" p. 4 |\n\n'
    )
    text = da_text().replace("#### MAJOR", block + "#### MAJOR", 1)
    report = panel.parse_report("da.md", text, FULL)
    with pytest.raises(phase.ConformanceError, match="unexpected issue-table"):
        phase.check_da_anchors(report)


def test_da_fullwidth_issue_payload_fails_phase():
    block = (
        "#### ADDITIONAL CRITICAL FINDINGS\n"
        "| ＃ | Issue | Ｅｖｉｄｅｎｃｅ Ａｎｃｈｏｒ |\n"
        "|---|---|---|\n"
        '| Ｃ９ | impossible df | ｔｅｘｔ： "n=41" p. 4 |\n\n'
    )
    text = da_text().replace("#### MAJOR", block + "#### MAJOR", 1)
    report = panel.parse_report("da.md", text, FULL)
    with pytest.raises(phase.ConformanceError, match="unexpected issue-table"):
        phase.check_da_anchors(report)


def test_da_raw_html_issue_table_fails_phase():
    block = (
        "#### ADDITIONAL CRITICAL FINDINGS\n"
        "<table><tr><th>ID</th><th>Evidence</th></tr>"
        "<tr><td>C9</td><td>text: n=41</td></tr></table>\n\n"
    )
    text = da_text().replace("#### MAJOR", block + "#### MAJOR", 1)
    report = panel.parse_report("da.md", text, FULL)
    with pytest.raises(phase.ConformanceError, match="raw HTML issue-table"):
        phase.check_da_anchors(report)


def test_da_nested_html_issue_table_in_canonical_row_fails_phase():
    nested = (
        "real issue <table><tr><th>#</th><th>Evidence Anchor</th></tr>"
        '<tr><td>C9</td><td>text: "impossible df" p. 4</td></tr></table>'
    )
    text = da_text().replace("Issue | text:", nested + " | text:", 1)
    report = panel.parse_report("da.md", text, FULL)
    with pytest.raises(phase.ConformanceError, match="raw HTML issue-table"):
        phase.check_da_anchors(report)


def test_da_bare_html_row_fails_phase():
    block = (
        "#### ADDITIONAL CRITICAL FINDINGS\n"
        "<tr><td>C9</td><td>text: n=41</td></tr>\n\n"
    )
    text = da_text().replace("#### MAJOR", block + "#### MAJOR", 1)
    report = panel.parse_report("da.md", text, FULL)
    with pytest.raises(phase.ConformanceError, match="raw HTML issue-table"):
        phase.check_da_anchors(report)


@pytest.mark.parametrize(
    "row,fragment",
    [
        ("| M1 | Issue |  |", "ANCHOR-MISSING"),
        ("| M1 | Issue | see page 3 |", "ANCHOR-INVALID"),
        ('|  | Issue | text: "quote" |', "empty MAJOR # cell"),
    ],
)
def test_da_major_row_gates_fail_phase_checker(row, fragment):
    report = panel.parse_report("da.md", da_text(major_rows=(row,)), FULL)
    with pytest.raises(
        (panel.ReportError, phase.panel.ReportError, phase.ConformanceError),
        match=fragment,
    ):
        phase.check_da_anchors(report)


def test_da_valid_major_row_passes_phase_checker():
    report = panel.parse_report(
        "da.md",
        da_text(major_rows=('| M1 | Issue | text: "short quote" |',)),
        FULL,
    )
    phase.check_da_anchors(report)


@pytest.mark.parametrize(
    "old,new",
    [
        ("|---|-------|-----------------|", ""),
        ("|---|-------|-----------------|", "|--|-------|-----------------|"),
    ],
)
def test_da_separator_drift_fails_phase_checker(old, new):
    report = panel.parse_report(
        "da.md", da_text().replace(old, new, 1), FULL
    )
    with pytest.raises(
        (panel.ReportError, phase.panel.ReportError, phase.ConformanceError),
        match="separator",
    ):
        phase.check_da_anchors(report)


def test_da_row_without_outer_pipes_fails_phase_checker():
    report = panel.parse_report(
        "da.md",
        da_text().replace(
            '| C1 | Issue | text: "quote" p. 1 |',
            'C1 | Issue | text: "quote" p. 1',
            1,
        ),
        FULL,
    )
    with pytest.raises(
        (panel.ReportError, phase.panel.ReportError, phase.ConformanceError),
        match="outer-pipe-delimited",
    ):
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
