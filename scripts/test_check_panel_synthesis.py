"""Schema 13.2 panel checker tests, including exhaustive decision profiles."""
from __future__ import annotations

import itertools
import json
from pathlib import Path

import pytest

from scripts import check_panel_synthesis as cps

REPO = Path(__file__).resolve().parents[1]
FULL_PATH = REPO / "shared/contracts/reviewer/full.json"
MF_PATH = REPO / "shared/contracts/reviewer/methodology_focus.json"
FULL = json.loads(FULL_PATH.read_text(encoding="utf-8"))
ROLES = ("eic", "methodology", "domain", "perspective", "da")


def state(value: str) -> cps.DimensionScore:
    if value == "fatal":
        return cps.DimensionScore("block", "fatal", "fatal trigger")
    if value == "block":
        return cps.DimensionScore("block", "repairable", "block trigger")
    if value == "warn":
        return cps.DimensionScore("warn", trigger="warn trigger")
    if value == "abstain":
        return cps.DimensionScore("not_assessed", abstain_reason="not applicable")
    return cps.DimensionScore(value)


def report_text(role: str, overrides=None, da_ids=()) -> str:
    overrides = overrides or {}
    lines = [f"contract_role: {role}", "", "## Dimension Scores", ""]
    for dim in FULL["acceptance_dimensions"]:
        did = dim["id"]
        lines.append(f"### {did}: {dim['name']}")
        if role not in dim["eligible_roles"]:
            lines.append("score: not_assessed")
        else:
            value = overrides.get(did, "pass")
            if value == "warn":
                lines += ["score: warn", 'trigger: "warn trigger"']
            elif value == "block":
                lines += [
                    "score: block", "block_class: repairable",
                    'trigger: "block trigger"',
                ]
            elif value == "fatal":
                lines += [
                    "score: block", "block_class: fatal",
                    'trigger: "fatal trigger"',
                ]
            elif value == "abstain":
                lines += [
                    "score: not_assessed",
                    "abstain_reason: materially inapplicable",
                ]
            else:
                lines.append("score: pass")
        lines.append("")
    lines += ["## Review Body", "", "No scored findings.", ""]
    if role == "da":
        lines += [
            "#### CRITICAL",
            "| # | Issue | Evidence Anchor |",
            "|---|-------|-----------------|",
        ]
        for finding_id in da_ids:
            lines.append(
                f'| {finding_id} | Issue | text: "quoted evidence" p. 1 |'
            )
        lines += [
            "",
            "#### MAJOR",
            "| # | Issue | Evidence Anchor |",
            "|---|-------|-----------------|",
        ]
    return "\n".join(lines)


def reports(overrides=None, da_ids=()):
    overrides = overrides or {}
    return [
        cps.parse_report(
            f"{role}.md",
            report_text(role, overrides.get(role), da_ids if role == "da" else ()),
            FULL,
        )
        for role in ROLES
    ]


def synthesis_for(
    panel_reports, adjudications=None, decision_override=None,
    marker_count=None, rationales=None,
):
    contract, expressions = cps.load_contract(FULL_PATH)
    assessed, fired, decision = cps.recompute_panel(
        panel_reports, contract, expressions, []
    )
    verdicts = cps.compute_dimension_verdicts(assessed)
    adjudications = adjudications or {}
    rationales = rationales or {}
    lines = [
        "dimension_verdicts: [" + ", ".join(
            f"{did}={value}" for did, value in verdicts.items()
        ) + "]",
        "fired_conditions: [" + ", ".join(fired) + "]",
        "da_critical_adjudications: [" + ", ".join(
            f"{finding_id}={value}"
            for finding_id, value in adjudications.items()
        ) + "]",
    ]
    lines += [
        f"{finding_id} rejection rationale: {text}"
        for finding_id, text in rationales.items()
    ]
    lines.append(decision_override or decision)
    if marker_count is not None:
        lines.append(
            f"[DA-CRITICAL-VS-ACCEPT: {marker_count} validated/unresolved]"
        )
    return "\n".join(lines), expressions


def test_majority_n1_is_owner_decides():
    assert cps.quantifier_fires("majority", [True], []) is True
    assert cps.quantifier_fires("majority", [False], []) is False


@pytest.mark.parametrize(
    "expression",
    [
        "any mandatory dimension scores 'block'",
        "two or more mandatory dimensions score 'warn' or worse",
        "every mandatory dimension scores 'pass'",
        "D1 scores 'block'",
        "D1 scores 'warn' AND every high dimension scores 'pass'",
        "any mandatory dimension has a fatal block",
        "D1 has a fatal block",
        "any dimension scores 'warn' or worse",
        "D2 scores 'warn' or worse",
        "every dimension scores 'pass'",
    ],
)
def test_expression_patterns_parse(expression):
    dimensions = {d["id"]: d for d in FULL["acceptance_dimensions"]}
    assert cps.parse_expression(expression, dimensions, "Fx")


@pytest.mark.parametrize(
    "expression",
    ["some dimension fails", "D99 scores 'pass'",
     "any high dimension has a fatal block", "D4 has a fatal block"],
)
def test_expression_fail_closed(expression):
    dimensions = {d["id"]: d for d in FULL["acceptance_dimensions"]}
    with pytest.raises(cps.ContractError):
        cps.parse_expression(expression, dimensions, "Fx")


def test_parse_report_role_scope_and_structural_abstention():
    report = cps.parse_report("eic.md", report_text("eic"), FULL)
    assert report.scores["D1"].score == "not_assessed"
    assert report.scores["D5"].score == "pass"


def test_out_of_role_real_score_rejected():
    text = report_text("eic").replace(
        "### D1: methodology_rigor\nscore: not_assessed",
        "### D1: methodology_rigor\nscore: pass",
    )
    with pytest.raises(cps.ReportError, match="OUT-OF-ROLE"):
        cps.parse_report("eic.md", text, FULL)


def test_eligible_abstention_requires_reason():
    text = report_text("eic", {"D5": "abstain"}).replace(
        "\nabstain_reason: materially inapplicable", "", 1
    )
    with pytest.raises(cps.ReportError, match="abstain_reason"):
        cps.parse_report("eic.md", text, FULL)


def test_v1_sections_fail_loudly():
    text = report_text("eic") + "\n## Failure Condition Checks\n"
    with pytest.raises(cps.ReportError, match="V1-GRAMMAR-RETIRED"):
        cps.parse_report("eic.md", text, FULL)


def test_nonmandatory_block_cannot_carry_block_class():
    text = report_text("perspective", {"D4": "pass"}).replace(
        "### D4: cross_disciplinary_relevance\nscore: pass",
        "### D4: cross_disciplinary_relevance\nscore: block\n"
        "block_class: repairable\ntrigger: \"block trigger\"",
    )
    with pytest.raises(cps.ReportError, match="BLOCK-CLASS"):
        cps.parse_report("p.md", text, FULL)


def test_denominator_excludes_ineligible_seats():
    panel_reports = reports({"methodology": {"D1": "warn"}})
    _, expressions = cps.load_contract(FULL_PATH)
    _, fired, decision = cps.recompute_panel(
        panel_reports, FULL, expressions, []
    )
    assert "F5" in fired
    assert decision == "editorial_decision=minor_revision"


def test_denominator_exclusion_ignores_decision_flipping_ineligible_score():
    panel_reports = reports()
    eic_report = next(report for report in panel_reports if report.role == "eic")
    eic_report.scores["D1"] = state("fatal")
    contract, expressions = cps.load_contract(FULL_PATH)
    assessed, fired, decision = cps.recompute_panel(
        panel_reports, contract, expressions, []
    )
    assert len(assessed["D1"]) == 1
    assert assessed["D1"][0].score == "pass"
    assert fired == ["F0"]
    assert decision == "editorial_decision=accept"


def test_roles_cross_check_rejects_dispatch_role_swap(tmp_path, capsys):
    report_path = tmp_path / "eic.md"
    report_path.write_text(report_text("eic"), encoding="utf-8")
    result = cps.main([
        "--contract", str(FULL_PATH),
        "--report", str(report_path),
        "--roles", "methodology",
        "--layer1-only",
    ])
    assert result == cps.EXIT_REVIEWER
    assert "[ROLE-BINDING:" in capsys.readouterr().out


def test_roles_cross_check_accepts_matching_dispatch_role(tmp_path, capsys):
    report_path = tmp_path / "eic.md"
    report_path.write_text(report_text("eic"), encoding="utf-8")
    result = cps.main([
        "--contract", str(FULL_PATH),
        "--report", str(report_path),
        "--roles", "eic",
        "--layer1-only",
    ])
    assert result == cps.EXIT_PASS
    assert "LAYER1-ONLY: PASS" in capsys.readouterr().out


def test_dimension_unassessed_aborts():
    panel_reports = reports({
        "methodology": {"D3": "abstain"},
        "da": {"D3": "abstain"},
    })
    _, expressions = cps.load_contract(FULL_PATH)
    with pytest.raises(cps.ContractError, match="DIMENSION-UNASSESSED: D3"):
        cps.recompute_panel(panel_reports, FULL, expressions, [])


def test_dimension_verdict_mismatch_is_synthesis_failure():
    panel_reports = reports()
    text, expressions = synthesis_for(panel_reports)
    text = text.replace("D1=pass", "D1=warn")
    synthesis = cps.parse_synthesis("s.md", text, FULL)
    assert any("PANEL-SYNTHESIS-MISMATCH" in item for item in
               cps.layer2_check(panel_reports, FULL, expressions, synthesis, []))


def test_fatal_precedence_over_repairable():
    panel_reports = reports({
        "methodology": {"D1": "fatal"},
        "domain": {"D2": "block"},
    })
    text, expressions = synthesis_for(panel_reports)
    synthesis = cps.parse_synthesis("s.md", text, FULL)
    assert synthesis.fired[:2] == ["F1", "F2"]
    assert synthesis.decision == "editorial_decision=reject"
    assert cps.layer2_check(panel_reports, FULL, expressions, synthesis, []) == []


@pytest.mark.parametrize("adjudication", ["VALIDATED", "UNRESOLVED"])
def test_da_accept_conflict_requires_counted_marker(adjudication):
    panel_reports = reports(da_ids=("C1",))
    text, expressions = synthesis_for(
        panel_reports, {"C1": adjudication}, marker_count=1
    )
    synthesis = cps.parse_synthesis("s.md", text, FULL)
    assert cps.layer2_check(panel_reports, FULL, expressions, synthesis, []) == []
    missing = cps.parse_synthesis(
        "s.md", text.replace(
            "\n[DA-CRITICAL-VS-ACCEPT: 1 validated/unresolved]", ""
        ), FULL
    )
    assert any("MARKER" in item for item in
               cps.layer2_check(panel_reports, FULL, expressions, missing, []))


def test_da_rejected_with_rationale_accepts_without_marker():
    panel_reports = reports(da_ids=("C1",))
    text, expressions = synthesis_for(
        panel_reports,
        {"C1": "REJECTED"},
        rationales={"C1": "The quoted sentence does not support the claim."},
    )
    synthesis = cps.parse_synthesis("s.md", text, FULL)
    assert cps.layer2_check(panel_reports, FULL, expressions, synthesis, []) == []


@pytest.mark.parametrize(
    "adjudications,rationales,marker,fragment",
    [
        ({}, {}, None, "MISMATCH"),  # omitted C1
        ({"C1": "REJECTED", "C3": "VALIDATED"},
         {"C1": "rationale"}, 1, "MISMATCH"),  # phantom C3
        ({"C1": "REJECTED"}, {}, None, "RATIONALE"),
        ({"C1": "VALIDATED"}, {}, 2, "MARKER"),
    ],
)
def test_da_gate_negative_fixtures(
    adjudications, rationales, marker, fragment
):
    panel_reports = reports(da_ids=("C1",))
    text, expressions = synthesis_for(
        panel_reports, adjudications, marker_count=marker,
        rationales=rationales,
    )
    synthesis = cps.parse_synthesis("s.md", text, FULL)
    assert any(fragment in item for item in
               cps.layer2_check(panel_reports, FULL, expressions, synthesis, []))


@pytest.mark.parametrize(
    "mutation",
    [
        lambda text: text.replace("#### CRITICAL", "#### Critical", 1),
        lambda text: text.replace("#### CRITICAL", "#### CRITICAL ISSUES", 1),
        lambda text: text.replace(
            "#### CRITICAL",
            "#### CRITICAL\n"
            "| # | Issue | Evidence Anchor |\n"
            "|---|-------|-----------------|\n\n"
            "#### CRITICAL",
            1,
        ),
    ],
)
def test_da_critical_section_drift_fails_closed(mutation):
    da_report = next(report for report in reports() if report.role == "da")
    with pytest.raises(cps.ReportError, match="exactly one #### CRITICAL"):
        cps.parse_da_critical_table(mutation(da_report.text), da_report.path)


@pytest.mark.parametrize(
    "mutation",
    [
        lambda text: text.replace("#### MAJOR", "#### Major", 1),
        lambda text: text.replace("#### MAJOR", "", 1),
        lambda text: text.replace(
            "#### MAJOR",
            "#### MAJOR\n"
            "| # | Issue | Evidence Anchor |\n"
            "|---|-------|-----------------|\n\n"
            "#### MAJOR",
            1,
        ),
    ],
)
def test_da_major_section_drift_fails_in_synthesis_path(mutation):
    panel_reports = reports()
    da_report = next(report for report in panel_reports if report.role == "da")
    da_report.text = mutation(da_report.text)
    text, expressions = synthesis_for(panel_reports)
    synthesis = cps.parse_synthesis("s.md", text, FULL)
    with pytest.raises(cps.ReportError, match="DA-MAJOR-PARSE"):
        cps.layer2_check(panel_reports, FULL, expressions, synthesis, [])


def test_marker_forbidden_under_nonaccept():
    panel_reports = reports({"methodology": {"D1": "warn"}}, da_ids=("C1",))
    text, expressions = synthesis_for(
        panel_reports, {"C1": "VALIDATED"}, marker_count=1
    )
    synthesis = cps.parse_synthesis("s.md", text, FULL)
    assert synthesis.decision == "editorial_decision=minor_revision"
    assert any("forbidden" in item for item in
               cps.layer2_check(panel_reports, FULL, expressions, synthesis, []))


def _evaluate_profile(contract, expressions, assessed):
    fired = [
        condition["condition_id"]
        for condition in contract["failure_conditions"]
        if cps.evaluate_expression(
            expressions[condition["condition_id"]],
            assessed,
            condition["cross_reviewer_quantifier"],
            [],
        )
    ]
    return fired, cps.resolve_decision(
        contract["failure_conditions"], set(fired)
    )


def test_full_contract_exhaustive_13824_profiles():
    contract, expressions = cps.load_contract(FULL_PATH)
    mandatory_single = ("pass", "warn", "block", "fatal")
    nonmandatory_single = ("pass", "warn", "block")
    d3_states = [
        pair for pair in itertools.product(
            ("pass", "warn", "block", "fatal", "abstain"), repeat=2
        ) if pair != ("abstain", "abstain")
    ]
    count = 0
    decisions = set()
    for d1, d2, d6, d3, d4, d5 in itertools.product(
        mandatory_single, mandatory_single, mandatory_single, d3_states,
        nonmandatory_single, nonmandatory_single,
    ):
        assessed = {
            "D1": [state(d1)],
            "D2": [state(d2)],
            "D3": [state(value) for value in d3 if value != "abstain"],
            "D4": [state(d4)],
            "D5": [state(d5)],
            "D6": [state(d6)],
        }
        fired, decision = _evaluate_profile(contract, expressions, assessed)
        assert fired
        assert decision in cps.ACTION_ENUM
        decisions.add(decision)
        count += 1
    assert count == 13_824
    assert decisions == cps.ACTION_ENUM


def test_methodology_focus_exhaustive_12_profiles():
    contract, expressions = cps.load_contract(MF_PATH)
    count = 0
    decisions = set()
    for d1, d2 in itertools.product(
        ("pass", "warn", "block", "fatal"),
        ("pass", "warn", "block"),
    ):
        fired, decision = _evaluate_profile(
            contract, expressions, {"D1": [state(d1)], "D2": [state(d2)]}
        )
        assert fired
        decisions.add(decision)
        count += 1
    assert count == 12
    assert decisions == cps.ACTION_ENUM


def test_methodology_focus_layer2_has_empty_da_gate():
    contract, expressions = cps.load_contract(MF_PATH)
    panel_reports = []
    for role in ("eic", "methodology"):
        lines = [f"contract_role: {role}", "", "## Dimension Scores", ""]
        for dim in contract["acceptance_dimensions"]:
            lines += [
                f"### {dim['id']}: {dim['name']}",
                "score: pass" if role in dim["eligible_roles"]
                else "score: not_assessed",
                "",
            ]
        lines += ["## Review Body", "", "No scored findings.", ""]
        panel_reports.append(cps.parse_report(
            f"{role}.md", "\n".join(lines), contract
        ))
    synthesis = cps.parse_synthesis(
        "s.md",
        "dimension_verdicts: [D1=pass, D2=pass]\n"
        "fired_conditions: [F0]\n"
        "da_critical_adjudications: []\n"
        "editorial_decision=accept\n",
        contract,
    )
    assert cps.layer2_check(
        panel_reports, contract, expressions, synthesis, []
    ) == []


def test_boundary_decisions_and_d3_split_dynamic_majority():
    contract, expressions = cps.load_contract(FULL_PATH)
    base = {did: [state("pass")] for did in ("D1", "D2", "D4", "D5", "D6")}
    base["D3"] = [state("pass"), state("pass")]

    one_warn = {**base, "D1": [state("warn")]}
    assert _evaluate_profile(contract, expressions, one_warn)[1] == \
        "editorial_decision=minor_revision"

    normal_block = {**base, "D5": [state("block")]}
    assert _evaluate_profile(contract, expressions, normal_block)[1] == \
        "editorial_decision=minor_revision"

    fatal_venue = {**base, "D6": [state("fatal")]}
    assert _evaluate_profile(contract, expressions, fatal_venue)[1] == \
        "editorial_decision=reject"

    split = {**base, "D3": [state("block"), state("pass")]}
    fired, _ = _evaluate_profile(contract, expressions, split)
    assert "F2" in fired and "F3" not in fired

    for assessed_d3 in ([state("warn")], [state("pass")]):
        dynamic = {**base, "D3": assessed_d3}
        fired, _ = _evaluate_profile(contract, expressions, dynamic)
        assert ("F5" in fired) == (assessed_d3[0].score == "warn")
