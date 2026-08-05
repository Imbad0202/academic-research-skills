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


@pytest.mark.parametrize(
    "anchor",
    (
        "absence: x",
        "absence: Methods — expected ethics;checked appendix",
        "absence: Methods — expected ethics;  checked appendix",
        "absence: Methods — expected ; checked appendix — expected ethics; checked supplement",
        "absence: Methods; checked appendix — expected ethics",
        "equation: Eq. ]3[",
        "absence: Methods — expected ethics; checked appendix]",
        "[absence: Methods — expected ethics; checked appendix",
        "text: §References, six DOI strings in list order",
        '[ text: §5 "short exact quote" ]',
        '` text: §5 "short exact quote" `',
        '`text: §5 "short exact quote"',
        'text: §5 "short exact quote"`',
        'text: §5 "short exact quote"]',
        'text: §5 "short exact quote"`]',
        '[text: §5 "short exact quote"] trailing]',
        '[[text: §5 "short exact quote"]]',
        '``text: §5 "short exact quote"``',
        'text: §5 "short exact quote”',
        'text: §5 “short exact quote"',
        'text: §5 "outer “inner”',
        'text: §5 “outer "inner”"',
        "text: §5 “outer “” tail”",
    ),
)
def test_shared_anchor_validator_rejects_incomplete_or_unpaired_shapes(anchor):
    with pytest.raises(cps.ReportError, match="ANCHOR-INVALID"):
        cps.validate_evidence_anchor(anchor, "probe")


@pytest.mark.parametrize(
    "anchor",
    (
        "absence: Methods — expected an ethics statement; checked Methods, appendix",
        '`text: §5 "short exact quote"`',
        "text: §5 “short exact quote”",
        "equation: Eq. [3]",
        "table: Table 2 [Panel B]",
        "[equation: Eq. [3]]",
        'text: §4 "short quote" [emphasis added]',
        'text: §3 "short quote" per `df`',
        '`text: §3 "short quote" per `df``',
        "text: §2 “the term “quality culture” is undefined”",
        'text: §2 "he said “quality culture” often"',
    ),
)
def test_shared_anchor_validator_accepts_complete_paired_shapes(anchor):
    cps.validate_evidence_anchor(anchor, "inverse")


def test_shared_anchor_validator_checks_nested_quote_word_limit_per_pair():
    words_25 = " ".join(["word"] * 25)
    words_26 = " ".join(["word"] * 26)
    cps.validate_evidence_anchor(
        f"text: §2 ““{words_25}””",
        "nested-25-word-boundary",
    )
    with pytest.raises(cps.ReportError, match="at most 25 words"):
        cps.validate_evidence_anchor(
            f"text: §2 ““{words_26}””",
            "nested-26-word-boundary",
        )
    outer_words = " ".join(["outer"] * 24)
    with pytest.raises(cps.ReportError, match="at most 25 words"):
        cps.validate_evidence_anchor(
            f"text: §2 “{outer_words} “inner” tail”",
            "nested-differential-outer-26-inner-1",
        )


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
    if role == "methodology":
        # #610: a methodology card without its Arithmetic Receipts section
        # stopped being phase-conformant; the synthesis parser itself
        # tolerates the extra H2 either way.
        lines += [
            "## Arithmetic Receipts",
            "",
            "no_recomputable_statistics: the fixture manuscript reports no "
            "statistic covered by a bounded procedure",
            "",
        ]
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


def test_majority_n2_requires_both_eligible_seats():
    assert cps.quantifier_fires("majority", [True, False], []) is False
    assert cps.quantifier_fires("majority", [True, True], []) is True


@pytest.mark.parametrize(
    "actions",
    (
        ("editorial_decision=minor_revision", "editorial_decision=reject"),
        ("editorial_decision=reject", "editorial_decision=minor_revision"),
    ),
)
def test_equal_severity_tie_uses_earliest_condition(actions):
    conditions = [
        {"condition_id": "F1", "severity": 50, "action": actions[0]},
        {"condition_id": "F2", "severity": 50, "action": actions[1]},
    ]
    assert cps.resolve_decision(conditions, {"F1", "F2"}) == actions[0]


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


@pytest.mark.parametrize(
    "action",
    (
        "reject", "Reject", "reject-or-major-revision", "unknown_v1_value",
        "mixed_key_case",
    ),
)
def test_v1_bare_decision_line_fails_loudly(action):
    key = "Editorial_Decision" if action == "mixed_key_case" else "editorial_decision"
    text = report_text("eic") + f"\n{key}={action}\n"
    with pytest.raises(cps.ReportError, match="V1-GRAMMAR-RETIRED"):
        cps.parse_report("eic.md", text, FULL)


@pytest.mark.parametrize("indent", ("  ", "\t"))
def test_indented_v1_bare_decision_line_fails_loudly(indent):
    text = report_text("eic") + f"\n{indent}editorial_decision=accept\n"
    with pytest.raises(cps.ReportError, match="V1-GRAMMAR-RETIRED"):
        cps.parse_report("eic.md", text, FULL)


def test_fenced_v1_bare_decision_decoy_is_ignored():
    text = (
        report_text("eic")
        + "\n```text\neditorial_decision=Reject\n```\n"
    )
    cps.parse_report("eic.md", text, FULL)


@pytest.mark.parametrize("fence", ("```", "~~~"))
def test_malformed_fence_closer_does_not_expose_bare_decision(fence):
    text = (
        report_text("eic")
        + f"\n{fence}text\n{fence}not-a-close\n"
        "editorial_decision=accept\n"
        f"{fence}\n"
    )
    cps.parse_report("eic.md", text, FULL)


def test_malformed_fence_closer_keeps_reviewer_report_hidden():
    text = "```text\n```not-a-close\n" + report_text("eic") + "\n```\n"
    with pytest.raises(cps.ReportError, match="Dimension Scores"):
        cps.parse_report("eic.md", text, FULL)


def test_malformed_fence_closer_synthesis_parses_as_fenced_content():
    """The fence never closes (`~~~not-a-close` is content, not a closer),
    so the whole synthesis stays fenced — and fenced audit lines are
    candidates since #637. Fence-STATE correctness stays pinned by the
    parse_report twins above, whose grammars remain fence-blind."""
    synthesis, _ = synthesis_for(reports())
    text = "~~~text\n~~~not-a-close\n" + synthesis + "\n~~~\n"
    parsed = cps.parse_synthesis("s.md", text, FULL)
    assert parsed.decision == "editorial_decision=accept"


@pytest.mark.parametrize("separator", ("\x85", "\u2028", "\u2029"))
def test_unicode_separator_cannot_close_commonmark_fence(separator):
    text = (
        "```text\n```"
        + separator
        + report_text("methodology", {"D1": "fatal"})
        + "\n```\n"
    )
    with pytest.raises(cps.ReportError, match="Dimension Scores"):
        cps.parse_report("hidden-methodology.md", text, FULL)


@pytest.mark.parametrize("separator", ("\x85", "\u2028", "\u2029"))
def test_unicode_separator_synthesis_parses_as_fenced_content(separator):
    """A Unicode separator is not a CommonMark line end: it can neither
    close the fence nor split the line, so the glued `~~~<sep>note` stays
    one content line. The rest of the synthesis is ordinary fenced content \u2014
    a candidate since #637 \u2014 and parses."""
    synthesis, _ = synthesis_for(reports())
    text = "~~~text\n~~~" + separator + "note\n" + synthesis + "\n~~~\n"
    parsed = cps.parse_synthesis("fenced-synthesis.md", text, FULL)
    assert parsed.decision == "editorial_decision=accept"


def test_fenced_audit_block_parses_as_observed_in_637_cohort():
    """Every synthesis first attempt of the 2026-08-03 baseline cohort (6/6)
    emitted the four audit lines inside a plain code fence."""
    synthesis, _ = synthesis_for(reports())
    parsed = cps.parse_synthesis(
        "s.md", "```\n" + synthesis + "\n```\n", FULL
    )
    assert parsed.fired == ["F0"]
    assert parsed.decision == "editorial_decision=accept"


def test_inline_code_wrapped_audit_lines_parse():
    """ms01_quant baseline r2's a2 retry wrapped each audit line whole in an
    inline code span, defeating the line-anchored grammar (#637)."""
    synthesis, _ = synthesis_for(reports())
    text = "\n".join(f"`{line}`" for line in synthesis.split("\n"))
    parsed = cps.parse_synthesis("s.md", text, FULL)
    assert parsed.decision == "editorial_decision=accept"


def test_identical_duplicate_audit_lines_collapse():
    """A byte-identical re-statement (plain line plus its fenced copy) is
    one candidate, not a duplicate abort."""
    synthesis, _ = synthesis_for(reports())
    fired_line = next(line for line in synthesis.split("\n")
                      if line.startswith("fired_conditions:"))
    text = synthesis + "\n```\n" + fired_line + "\n```\n"
    parsed = cps.parse_synthesis("s.md", text, FULL)
    assert parsed.fired == ["F0"]


def test_conflicting_fenced_audit_line_still_aborts():
    """A fenced decoy that disagrees with the operative line stays a loud
    abort \u2014 tolerance collapses identical values only."""
    synthesis, _ = synthesis_for(reports())
    text = synthesis + "\n```\nfired_conditions: [F1]\n```\n"
    with pytest.raises(cps.SynthesisError, match="found 2"):
        cps.parse_synthesis("s.md", text, FULL)


def test_prose_quoted_checker_diagnostic_is_not_a_candidate():
    """The a2 remediation notes of the #637 cohort quote the checker error
    inside longer prose lines; anchored grammars must not see those."""
    synthesis, _ = synthesis_for(reports())
    note = (
        "**Checker remediation:** the prior emission failed "
        "`[SYNTHESIS-PARSE: expected exactly one fired_conditions line, "
        "found 0]` and the canonical block is re-emitted plainly above."
    )
    parsed = cps.parse_synthesis(
        "s.md", synthesis + "\n" + note + "\n", FULL
    )
    assert parsed.fired == ["F0"]


def test_blockquoted_audit_line_documents_an_accepted_miss():
    """Documents an ACCEPTED miss: a blockquoted audit line renders as
    quotation and is deliberately not a candidate. Change deliberately."""
    synthesis, _ = synthesis_for(reports())
    text = synthesis.replace("fired_conditions:", "> fired_conditions:", 1)
    with pytest.raises(cps.SynthesisError, match="fired_conditions"):
        cps.parse_synthesis("s.md", text, FULL)


def test_inline_span_inside_fence_documents_an_accepted_miss():
    """Documents an ACCEPTED miss: backticks inside a fence are literal
    rendered content, so a wrapped line there is not unwrapped. Change
    deliberately."""
    synthesis, _ = synthesis_for(reports())
    fenced = "\n".join(f"`{line}`" for line in synthesis.split("\n"))
    with pytest.raises(cps.SynthesisError, match="fired_conditions"):
        cps.parse_synthesis("s.md", "```\n" + fenced + "\n```\n", FULL)


def test_fenced_rationale_and_marker_document_an_accepted_miss():
    """Documents an ACCEPTED miss: rationales and the DA marker keep the
    plain-line source \u2014 their fenced occurrences read as quotation. Change
    deliberately."""
    synthesis, _ = synthesis_for(reports())
    text = (
        synthesis
        + "\n```\nC9 rejection rationale: quoted example\n"
        "[DA-CRITICAL-VS-ACCEPT: 2 validated/unresolved]\n```\n"
    )
    parsed = cps.parse_synthesis("s.md", text, FULL)
    assert "C9" not in parsed.rejection_rationales
    assert parsed.marker_count is None
    # The forbidden-marker asymmetry is part of the same accepted boundary:
    # with no active DA-critical adjudications a stated marker is forbidden,
    # and this fenced one stays invisible rather than aborting — the
    # decision channel is pinned independently by the layer-2 recompute.
    assert not any(
        "marker forbidden" in diag
        for diag in cps.check_da_terminal_gate(reports(), parsed)
    )


def test_padded_inline_code_wrapped_audit_lines_parse():
    """CommonMark renders `` ` body ` `` with one padding space stripped
    from each side, so a padded span displays the audit line verbatim and
    must be a candidate in its DISPLAYED form."""
    synthesis, _ = synthesis_for(reports())
    text = "\n".join(f"` {line} `" for line in synthesis.split("\n"))
    parsed = cps.parse_synthesis("s.md", text, FULL)
    assert parsed.decision == "editorial_decision=accept"


def test_padded_span_conflicting_value_still_aborts():
    """Rendering normalization must not weaken the distinct-value guard: a
    padded-span decoy that disagrees with the operative line still aborts."""
    synthesis, _ = synthesis_for(reports())
    text = synthesis + "\n` fired_conditions: [F1] `\n"
    with pytest.raises(cps.SynthesisError, match="found 2"):
        cps.parse_synthesis("s.md", text, FULL)


def test_all_space_span_body_is_not_stripped():
    """CommonMark strips padding only when the body is not all spaces; an
    all-space span stays as-is and is simply a non-candidate."""
    synthesis, _ = synthesis_for(reports())
    parsed = cps.parse_synthesis(
        "s.md", synthesis + "\n`   `\n", FULL
    )
    assert parsed.decision == "editorial_decision=accept"


def test_indented_fence_content_parses_dedented():
    """A fence opened with up to 3 leading spaces renders its content
    dedented by the opener's indent, so indented fenced audit lines are
    candidates in their displayed (dedented) form."""
    synthesis, _ = synthesis_for(reports())
    indented = "\n".join("  " + line for line in synthesis.split("\n"))
    text = "  ```\n" + indented + "\n  ```\n"
    parsed = cps.parse_synthesis("s.md", text, FULL)
    assert parsed.decision == "editorial_decision=accept"


def test_crlf_fenced_audit_block_parses():
    """CRLF line endings are CommonMark line ends; the fenced audit block
    parses identically under them."""
    synthesis, _ = synthesis_for(reports())
    text = ("```\n" + synthesis + "\n```\n").replace("\n", "\r\n")
    parsed = cps.parse_synthesis("s.md", text, FULL)
    assert parsed.decision == "editorial_decision=accept"


def test_malformed_closer_fence_state_pins_wrapped_decoy_hidden():
    """Pins fence STATE through the candidate walker: `~~~not-a-close` does
    not close the fence, so a wrapped decoy after it is fenced — backticks
    render literally, the decoy is never unwrapped, and the plain synthesis
    before the fence parses. A mutation that accepts the malformed closer
    unwraps the decoy and flips this to a found-2 abort."""
    synthesis, _ = synthesis_for(reports())
    text = (
        synthesis
        + "\n~~~text\n~~~not-a-close\n`fired_conditions: [F1]`\n~~~\n"
    )
    parsed = cps.parse_synthesis("s.md", text, FULL)
    assert parsed.fired == ["F0"]


def test_short_closer_fence_state_pins_wrapped_decoy_hidden():
    """A prospective closer shorter than the opener does not close the
    fence (CommonMark length rule), so the wrapped decoy after it stays
    fenced and hidden."""
    synthesis, _ = synthesis_for(reports())
    text = (
        synthesis
        + "\n````\n```\n`fired_conditions: [F1]`\n````\n"
    )
    parsed = cps.parse_synthesis("s.md", text, FULL)
    assert parsed.fired == ["F0"]


def test_mismatched_closer_fence_state_pins_wrapped_decoy_hidden():
    """A backtick closer cannot close a tilde fence; the wrapped decoy
    after it stays fenced and hidden."""
    synthesis, _ = synthesis_for(reports())
    text = (
        synthesis
        + "\n~~~\n```\n`fired_conditions: [F1]`\n~~~\n"
    )
    parsed = cps.parse_synthesis("s.md", text, FULL)
    assert parsed.fired == ["F0"]


@pytest.mark.parametrize("separator", ("\x85", "\u2028", "\u2029"))
def test_unicode_separator_fence_state_pins_wrapped_decoy_hidden(separator):
    """A Unicode separator is not a CommonMark line end: `~~~<sep>note`
    stays one content line and cannot close the fence, so the wrapped
    decoy after it stays fenced and hidden. A mutation that splits on the
    separator closes the fence and flips this to a found-2 abort."""
    synthesis, _ = synthesis_for(reports())
    text = (
        synthesis
        + "\n~~~text\n~~~" + separator + "note\n"
        "`fired_conditions: [F1]`\n~~~\n"
    )
    parsed = cps.parse_synthesis("s.md", text, FULL)
    assert parsed.fired == ["F0"]


def test_unterminated_fence_content_stays_candidate():
    """An unterminated fence retains (not grows) its content, and fenced
    audit lines remain candidates to end-of-input."""
    synthesis, _ = synthesis_for(reports())
    parsed = cps.parse_synthesis("s.md", "```\n" + synthesis, FULL)
    assert parsed.decision == "editorial_decision=accept"


@pytest.mark.parametrize("score", ("warn", "block"))
def test_eligible_nonpass_score_requires_trigger(score):
    text = report_text("methodology", {"D1": score}).replace(
        f'trigger: "{score} trigger"\n', "", 1
    )
    with pytest.raises(cps.ReportError, match="TRIGGER-GRAMMAR"):
        cps.parse_report("methodology.md", text, FULL)


@pytest.mark.parametrize(
    "role,did,score_line",
    (
        ("methodology", "D1", "score: pass"),
        ("eic", "D1", "score: not_assessed"),
    ),
)
def test_nontriggering_score_forbids_trigger(role, did, score_line):
    text = report_text(role).replace(
        f"### {did}:", f'### {did}:', 1
    ).replace(
        score_line, score_line + '\ntrigger: "post hoc trigger"', 1
    )
    with pytest.raises(cps.ReportError, match="TRIGGER-GRAMMAR"):
        cps.parse_report(f"{role}.md", text, FULL)


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


@pytest.mark.parametrize(
    "old,new",
    [
        ("|---|-------|-----------------|", ""),
        ("|---|-------|-----------------|", "|--|-------|-----------------|"),
        ("|---|-------|-----------------|", "|---|-------|"),
    ],
)
def test_da_separator_drift_fails_in_synthesis_path(old, new):
    panel_reports = reports(da_ids=("C1",))
    da_report = next(report for report in panel_reports if report.role == "da")
    da_report.text = da_report.text.replace(old, new, 1)
    text, expressions = synthesis_for(
        panel_reports, {"C1": "VALIDATED"}, marker_count=1
    )
    synthesis = cps.parse_synthesis("s.md", text, FULL)
    with pytest.raises(cps.ReportError, match="separator"):
        cps.layer2_check(panel_reports, FULL, expressions, synthesis, [])


def test_da_trailing_row_without_outer_pipes_fails_in_synthesis_path():
    panel_reports = reports(da_ids=("C1", "C2"))
    da_report = next(report for report in panel_reports if report.role == "da")
    da_report.text = da_report.text.replace(
        '| C2 | Issue | text: "quoted evidence" p. 1 |',
        'C2 | Issue | text: "quoted evidence" p. 1',
        1,
    )
    synthesis_text, expressions = synthesis_for(
        panel_reports, {"C1": "VALIDATED", "C2": "VALIDATED"}, marker_count=2
    )
    synthesis = cps.parse_synthesis("s.md", synthesis_text, FULL)
    with pytest.raises(cps.ReportError, match="outer-pipe-delimited"):
        cps.layer2_check(panel_reports, FULL, expressions, synthesis, [])


def test_da_pre_table_prose_passes_in_synthesis_path():
    panel_reports = reports(da_ids=("C1",))
    da_report = next(report for report in panel_reports if report.role == "da")
    da_report.text = da_report.text.replace(
        "#### CRITICAL",
        "Ordinary adversarial commentary precedes the terminal tables.\n\n"
        "#### CRITICAL",
        1,
    )
    synthesis_text, expressions = synthesis_for(
        panel_reports, {"C1": "VALIDATED"}, marker_count=1
    )
    synthesis = cps.parse_synthesis("s.md", synthesis_text, FULL)
    assert cps.layer2_check(
        panel_reports, FULL, expressions, synthesis, []
    ) == []


def test_da_bare_comment_closer_passes_in_synthesis_path():
    panel_reports = reports(da_ids=("C1",))
    da_report = next(report for report in panel_reports if report.role == "da")
    da_report.text = da_report.text.replace(
        "#### CRITICAL",
        "The reported N moves 41 --> 38 without explanation.\n\n"
        "#### CRITICAL",
        1,
    ).replace(
        'text: "quoted evidence" p. 1',
        'text: "N moves 41 --> 38" p. 1',
        1,
    )
    synthesis_text, expressions = synthesis_for(
        panel_reports, {"C1": "VALIDATED"}, marker_count=1
    )
    synthesis = cps.parse_synthesis("s.md", synthesis_text, FULL)
    assert cps.layer2_check(
        panel_reports, FULL, expressions, synthesis, []
    ) == []


def test_da_post_critical_table_prose_fails_in_synthesis_path():
    panel_reports = reports()
    da_report = next(report for report in panel_reports if report.role == "da")
    da_report.text = da_report.text.replace(
        "\n\n#### MAJOR",
        "\n\n*None. Ordinary adversarial commentary.*\n\n#### MAJOR",
        1,
    )
    synthesis_text, expressions = synthesis_for(panel_reports)
    synthesis = cps.parse_synthesis("s.md", synthesis_text, FULL)
    with pytest.raises(cps.ReportError, match="issue tables are terminal"):
        cps.layer2_check(panel_reports, FULL, expressions, synthesis, [])


_DA_TERMINAL_LATE_SURFACES = (
    '| C2 | Late issue | text: "late quoted evidence" p. 2 |',
    "| X9 | Bogus issue |  |",
    (
        "| # | Issue | Evidence Anchor |\n"
        "|---|-------|-----------------|\n"
        "| C9 | Shadow issue |  |"
    ),
    'C2 | Late issue | text: "late quoted evidence" p. 2',
    '— | Late issue | text: "late quoted evidence"',
    "# | Issue | Evidence Anchor",
    "C2\nLate issue without pipes\nfigure: Figure 2",
    "- C2\n- Late critical issue\n- figure: Figure 2",
    "> Ordinary post-table commentary",
    "##### Additional commentary",
    "### Closing note\nOrdinary late prose",
)


@pytest.mark.parametrize(
    "late_surface",
    _DA_TERMINAL_LATE_SURFACES,
)
def test_da_post_boundary_table_surfaces_fail_in_synthesis_path(
    late_surface,
):
    panel_reports = reports(da_ids=("C1",))
    da_report = next(report for report in panel_reports if report.role == "da")
    da_report.text = da_report.text.replace(
        "\n\n#### MAJOR",
        f"\n\n{late_surface}\n\n#### MAJOR",
        1,
    )
    synthesis_text, expressions = synthesis_for(
        panel_reports, {"C1": "VALIDATED"}, marker_count=1
    )
    synthesis = cps.parse_synthesis("s.md", synthesis_text, FULL)
    with pytest.raises(cps.ReportError, match="issue tables are terminal"):
        cps.layer2_check(panel_reports, FULL, expressions, synthesis, [])


@pytest.mark.parametrize("late_surface", _DA_TERMINAL_LATE_SURFACES)
def test_da_post_major_table_surfaces_fail_in_synthesis_path(
    late_surface,
):
    panel_reports = reports(da_ids=("C1",))
    da_report = next(report for report in panel_reports if report.role == "da")
    da_report.text += f"\n\n{late_surface}"
    synthesis_text, expressions = synthesis_for(
        panel_reports, {"C1": "VALIDATED"}, marker_count=1
    )
    synthesis = cps.parse_synthesis("s.md", synthesis_text, FULL)
    with pytest.raises(cps.ReportError, match="issue tables are terminal"):
        cps.layer2_check(panel_reports, FULL, expressions, synthesis, [])


def test_da_fenced_payload_after_major_fails_in_synthesis_path():
    panel_reports = reports(da_ids=("C1",))
    da_report = next(report for report in panel_reports if report.role == "da")
    da_report.text += (
        "\n\n```markdown\n"
        '| C2 | Hidden critical issue | text: "hidden evidence" p. 2 |\n'
        "```"
    )
    synthesis_text, expressions = synthesis_for(
        panel_reports, {"C1": "VALIDATED"}, marker_count=1
    )
    synthesis = cps.parse_synthesis("s.md", synthesis_text, FULL)
    with pytest.raises(cps.ReportError, match="issue tables are terminal"):
        cps.layer2_check(panel_reports, FULL, expressions, synthesis, [])


def test_da_html_comment_inside_fence_fails_in_synthesis_path():
    panel_reports = reports()
    da_report = next(report for report in panel_reports if report.role == "da")
    da_report.text += "\n\n```\n<!-- hidden adjudication payload -->\n```"
    synthesis_text, expressions = synthesis_for(panel_reports)
    synthesis = cps.parse_synthesis("s.md", synthesis_text, FULL)
    with pytest.raises(cps.ReportError, match="HTML comments are forbidden"):
        cps.layer2_check(panel_reports, FULL, expressions, synthesis, [])


def test_da_html_commented_tables_fail_in_synthesis_path():
    panel_reports = reports()
    da_report = next(report for report in panel_reports if report.role == "da")
    da_report.text = da_report.text.replace(
        "#### CRITICAL", "<!--\n#### CRITICAL", 1
    )
    da_report.text += "\n-->"
    synthesis_text, expressions = synthesis_for(panel_reports)
    synthesis = cps.parse_synthesis("s.md", synthesis_text, FULL)
    with pytest.raises(cps.ReportError, match="HTML comments are forbidden"):
        cps.layer2_check(panel_reports, FULL, expressions, synthesis, [])


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
        (
            "| C2 | Issue |",
            "| C1 | Issue |",
            "duplicate CRITICAL ID",
        ),
        (
            "| C2 | Issue |",
            "| X2 | Issue |",
            "invalid CRITICAL ID",
        ),
    ],
)
def test_da_header_and_critical_id_gates_fail_in_synthesis_path(
    old, new, fragment
):
    panel_reports = reports(da_ids=("C1", "C2"))
    da_report = next(report for report in panel_reports if report.role == "da")
    da_report.text = da_report.text.replace(old, new, 1)
    text, expressions = synthesis_for(
        panel_reports,
        {"C1": "VALIDATED", "C2": "VALIDATED"},
        marker_count=2,
    )
    synthesis = cps.parse_synthesis("s.md", text, FULL)
    with pytest.raises(cps.ReportError, match=fragment):
        cps.layer2_check(panel_reports, FULL, expressions, synthesis, [])


def test_da_shadow_table_fails_in_synthesis_path():
    panel_reports = reports(da_ids=("C1",))
    da_report = next(report for report in panel_reports if report.role == "da")
    canonical = (
        '| # | Issue | Evidence Anchor |\n'
        '|---|-------|-----------------|\n'
        '| C1 | Issue | text: "quoted evidence" p. 1 |'
    )
    shadowed = (
        '| ID | Issue | Anchor |\n'
        '|---|-------|--------|\n'
        '| C1 | Issue | text: "quoted evidence" p. 1 |\n\n'
        '| # | Issue | Evidence Anchor |\n'
        '|---|-------|-----------------|'
    )
    da_report.text = da_report.text.replace(canonical, shadowed, 1)
    text, expressions = synthesis_for(panel_reports)
    synthesis = cps.parse_synthesis("s.md", text, FULL)
    with pytest.raises(cps.ReportError, match="first nonblank line"):
        cps.layer2_check(panel_reports, FULL, expressions, synthesis, [])


def test_da_standalone_critical_fails_in_synthesis_path():
    panel_reports = reports()
    da_report = next(report for report in panel_reports if report.role == "da")
    da_report.text = da_report.text.replace(
        "#### CRITICAL",
        "### Further adversarial challenge\n"
        "- **Severity**: Critical | **Confidence**: 5 (statistics)\n\n"
        "#### CRITICAL",
        1,
    )
    text, expressions = synthesis_for(panel_reports)
    synthesis = cps.parse_synthesis("s.md", text, FULL)
    with pytest.raises(cps.ReportError, match="standalone Severity"):
        cps.layer2_check(panel_reports, FULL, expressions, synthesis, [])


@pytest.mark.parametrize("label", ("severity", "sEvErItY"))
def test_da_case_variant_standalone_critical_fails_in_synthesis_path(label):
    panel_reports = reports()
    da_report = next(report for report in panel_reports if report.role == "da")
    da_report.text = da_report.text.replace(
        "#### CRITICAL",
        "### Further adversarial challenge\n"
        f"This is **{label}**: Critical and no revision cures it.\n\n"
        "#### CRITICAL",
        1,
    )
    text, expressions = synthesis_for(panel_reports)
    synthesis = cps.parse_synthesis("s.md", text, FULL)
    with pytest.raises(cps.ReportError, match="standalone Severity"):
        cps.layer2_check(panel_reports, FULL, expressions, synthesis, [])


def test_da_extra_issue_table_band_fails_in_synthesis_path():
    panel_reports = reports()
    da_report = next(report for report in panel_reports if report.role == "da")
    da_report.text = da_report.text.replace(
        "#### MAJOR",
        "#### ADDITIONAL CRITICAL FINDINGS\n"
        "| # | Issue | Evidence Anchor |\n"
        "|---|-------|-----------------|\n"
        '| C1 | impossible df | text: "n=41" p. 4 |\n\n'
        "#### MAJOR",
        1,
    )
    text, expressions = synthesis_for(panel_reports)
    synthesis = cps.parse_synthesis("s.md", text, FULL)
    with pytest.raises(cps.ReportError, match="unexpected issue-table band"):
        cps.layer2_check(panel_reports, FULL, expressions, synthesis, [])


@pytest.mark.parametrize(
    ("lead_in", "header"),
    (
        ("The following issues invalidate the claim:\n\n",
         "| # | Issue | Evidence Anchor |"),
        ("", "| # | Issue | evidence anchor |"),
        ("", "# | Issue | Evidence Anchor"),
    ),
)
def test_da_disguised_extra_issue_table_band_fails_in_synthesis_path(
    lead_in, header
):
    panel_reports = reports()
    da_report = next(report for report in panel_reports if report.role == "da")
    da_report.text = da_report.text.replace(
        "#### MAJOR",
        "#### ADDITIONAL CRITICAL FINDINGS\n"
        f"{lead_in}{header}\n"
        "|---|-------|-----------------|\n"
        '| C9 | impossible df | text: "n=41" p. 4 |\n\n'
        "#### MAJOR",
        1,
    )
    text, expressions = synthesis_for(panel_reports)
    synthesis = cps.parse_synthesis("s.md", text, FULL)
    with pytest.raises(cps.ReportError, match="unexpected issue-table band"):
        cps.layer2_check(panel_reports, FULL, expressions, synthesis, [])


@pytest.mark.parametrize("placement", ("preamble", "extra_h2"))
def test_da_issue_table_outside_canonical_bands_fails_synthesis(placement):
    panel_reports = reports()
    da_report = next(report for report in panel_reports if report.role == "da")
    table = (
        "| # | Issue | Evidence Anchor |\n"
        "|---|-------|-----------------|\n"
        '| C9 | impossible df | text: "n=41" p. 4 |\n'
    )
    if placement == "preamble":
        da_report.text = da_report.text.replace(
            "#### CRITICAL", table + "\n#### CRITICAL", 1
        )
    else:
        da_report.text += "\n## Appendix\n" + table
    text, expressions = synthesis_for(panel_reports)
    synthesis = cps.parse_synthesis("s.md", text, FULL)
    with pytest.raises(cps.ReportError, match="unexpected issue-table"):
        cps.layer2_check(panel_reports, FULL, expressions, synthesis, [])


def test_da_internal_header_whitespace_fails_in_synthesis_path():
    panel_reports = reports()
    da_report = next(report for report in panel_reports if report.role == "da")
    da_report.text = da_report.text.replace(
        "#### MAJOR",
        "#### ADDITIONAL CRITICAL FINDINGS\n"
        "# | Issue | Evidence   Anchor\n"
        "---|-------|-----------------\n"
        'C9 | impossible df | text: "n=41" p. 4\n\n'
        "#### MAJOR",
        1,
    )
    text, expressions = synthesis_for(panel_reports)
    synthesis = cps.parse_synthesis("s.md", text, FULL)
    with pytest.raises(cps.ReportError, match="unexpected issue-table"):
        cps.layer2_check(panel_reports, FULL, expressions, synthesis, [])


@pytest.mark.parametrize(
    "header",
    (
        "| ID | Issue | Evidence Anchor |",
        "| # | Issue | Evidence |",
        "| **#** | Issue | **Evidence Anchor** |",
        "| `#` | Issue | `Evidence Anchor` |",
    ),
)
def test_da_partial_or_formatted_issue_header_fails_synthesis(header):
    panel_reports = reports()
    da_report = next(report for report in panel_reports if report.role == "da")
    da_report.text = da_report.text.replace(
        "#### MAJOR",
        "#### ADDITIONAL CRITICAL FINDINGS\n"
        f"{header}\n"
        "|---|-------|-----------------|\n"
        '| C9 | impossible df | text: "n=41" p. 4 |\n\n'
        "#### MAJOR",
        1,
    )
    text, expressions = synthesis_for(panel_reports)
    synthesis = cps.parse_synthesis("s.md", text, FULL)
    with pytest.raises(cps.ReportError, match="unexpected issue-table"):
        cps.layer2_check(panel_reports, FULL, expressions, synthesis, [])


@pytest.mark.parametrize(
    "header",
    (
        "| ID | Issue | [Evidence Anchor][anchor] |",
        r"| \# | Issue | Evidence |",
        '| ID | Issue | <span title="x>y">Evidence Anchor</span> |',
    ),
)
def test_da_commonmark_visible_issue_header_fails_synthesis(header):
    panel_reports = reports()
    da_report = next(report for report in panel_reports if report.role == "da")
    da_report.text = da_report.text.replace(
        "#### MAJOR",
        "#### ADDITIONAL CRITICAL FINDINGS\n"
        f"{header}\n"
        "|---|-------|-----------------|\n"
        '| C9 | impossible df | text: "n=41" p. 4 |\n\n'
        "#### MAJOR",
        1,
    )
    text, expressions = synthesis_for(panel_reports)
    synthesis = cps.parse_synthesis("s.md", text, FULL)
    with pytest.raises(cps.ReportError, match="unexpected issue-table"):
        cps.layer2_check(panel_reports, FULL, expressions, synthesis, [])


def test_da_balanced_link_destination_header_fails_synthesis():
    panel_reports = reports()
    da_report = next(report for report in panel_reports if report.role == "da")
    header = (
        r"| [\#](<https://x.test/a(b)>) | Issue | "
        r"[Evidence Anchor](<https://x.test/a(b)>) |"
    )
    da_report.text = da_report.text.replace(
        "#### MAJOR",
        "#### ADDITIONAL CRITICAL FINDINGS\n"
        f"{header}\n"
        "|---|-------|-----------------|\n"
        '| C9 | impossible df | text: "n=41" p. 4 |\n\n'
        "#### MAJOR",
        1,
    )
    text, expressions = synthesis_for(panel_reports)
    synthesis = cps.parse_synthesis("s.md", text, FULL)
    with pytest.raises(cps.ReportError, match="unexpected issue-table"):
        cps.layer2_check(panel_reports, FULL, expressions, synthesis, [])


def test_da_typed_anchor_payload_alone_fails_synthesis():
    panel_reports = reports()
    da_report = next(report for report in panel_reports if report.role == "da")
    header = (
        r"| [\#](<https://x.test/a(b)>) | Issue | "
        r"[Evidence Anchor](<https://x.test/a(b)>) |"
    )
    da_report.text = da_report.text.replace(
        "#### MAJOR",
        "#### ADDITIONAL CRITICAL FINDINGS\n"
        f"{header}\n"
        "|---|-------|-----------------|\n"
        '| 1 | impossible df | `text: "n=41" p. 4` |\n\n'
        "#### MAJOR",
        1,
    )
    text, expressions = synthesis_for(panel_reports)
    synthesis = cps.parse_synthesis("s.md", text, FULL)
    with pytest.raises(cps.ReportError, match="unexpected issue-table"):
        cps.layer2_check(panel_reports, FULL, expressions, synthesis, [])


def test_da_escaped_pipe_cell_evasion_fails_synthesis():
    panel_reports = reports()
    da_report = next(report for report in panel_reports if report.role == "da")
    block = (
        "#### ADDITIONAL CRITICAL FINDINGS\n"
        r"| [\#<!--\|-->](https://x.test) | Issue | "
        r"[Evidence<!--\|--> Anchor](https://x.test) |" "\n"
        "|---|---|---|\n"
        r"| [C<!--\|-->9](https://x.test) | impossible df | "
        r'[text<!--\|-->: "n=41" p. 4](https://x.test) |' "\n\n"
    )
    da_report.text = da_report.text.replace(
        "#### MAJOR", block + "#### MAJOR", 1
    )
    text, expressions = synthesis_for(panel_reports)
    synthesis = cps.parse_synthesis("s.md", text, FULL)
    with pytest.raises(cps.ReportError, match="HTML comments are forbidden"):
        cps.layer2_check(panel_reports, FULL, expressions, synthesis, [])


def test_da_canonical_rows_allow_escaped_pipes():
    text = report_text("da", da_ids=("C1",)).replace(
        "| C1 | Issue |",
        r"| C1 | Issue \| detail |",
        1,
    )
    text += "\n" + r'| M1 | Issue \| detail | text: "quoted evidence" p. 1 |'
    critical, major = cps.parse_da_tables(text, "da.md")
    assert list(critical) == ["C1"]
    assert major == ['text: "quoted evidence" p. 1']


def test_da_repeated_absence_separators_fail_in_synthesis_path():
    malformed = (
        "absence: Methods — expected ; checked appendix "
        "— expected ethics; checked supplement"
    )
    text = report_text("da", da_ids=("C1",)).replace(
        'text: "quoted evidence" p. 1',
        malformed,
        1,
    )
    with pytest.raises(cps.ReportError, match="ANCHOR-INVALID"):
        cps.parse_da_tables(text, "da.md")


@pytest.mark.parametrize(
    "malformed",
    (
        "absence: Methods; checked appendix — expected ethics",
        '[ text: §5 "short exact quote" ]',
        "equation: Eq. ]3[",
    ),
)
def test_da_misordered_absence_or_padded_wrapper_fails_synthesis(malformed):
    text = report_text("da", da_ids=("C1",)).replace(
        'text: "quoted evidence" p. 1',
        malformed,
        1,
    )
    with pytest.raises(cps.ReportError, match="ANCHOR-INVALID"):
        cps.parse_da_tables(text, "da.md")


@pytest.mark.parametrize(
    "invisible", ("\u0600", "\u200b", "\u034f", "\ufe0e", "\u3164", "\ufff0")
)
def test_da_invisible_issue_payload_fails_synthesis(invisible):
    panel_reports = reports()
    da_report = next(report for report in panel_reports if report.role == "da")
    block = (
        "#### ADDITIONAL CRITICAL FINDINGS\n"
        f"| #{invisible} | Issue | Evidence{invisible} Anchor |\n"
        "|---|---|---|\n"
        f'| C{invisible}9 | impossible df | text{invisible}: "n=41" p. 4 |\n\n'
    )
    da_report.text = da_report.text.replace(
        "#### MAJOR", block + "#### MAJOR", 1
    )
    text, expressions = synthesis_for(panel_reports)
    synthesis = cps.parse_synthesis("s.md", text, FULL)
    with pytest.raises(cps.ReportError, match="unexpected issue-table"):
        cps.layer2_check(panel_reports, FULL, expressions, synthesis, [])


def test_da_fullwidth_issue_payload_fails_synthesis():
    panel_reports = reports()
    da_report = next(report for report in panel_reports if report.role == "da")
    block = (
        "#### ADDITIONAL CRITICAL FINDINGS\n"
        "| ＃ | Issue | Ｅｖｉｄｅｎｃｅ Ａｎｃｈｏｒ |\n"
        "|---|---|---|\n"
        '| Ｃ９ | impossible df | ｔｅｘｔ： "n=41" p. 4 |\n\n'
    )
    da_report.text = da_report.text.replace(
        "#### MAJOR", block + "#### MAJOR", 1
    )
    text, expressions = synthesis_for(panel_reports)
    synthesis = cps.parse_synthesis("s.md", text, FULL)
    with pytest.raises(cps.ReportError, match="unexpected issue-table"):
        cps.layer2_check(panel_reports, FULL, expressions, synthesis, [])


def test_da_raw_html_issue_table_fails_synthesis():
    panel_reports = reports()
    da_report = next(report for report in panel_reports if report.role == "da")
    block = (
        "#### ADDITIONAL CRITICAL FINDINGS\n"
        "<table><tr><th>ID</th><th>Evidence</th></tr>"
        "<tr><td>C9</td><td>text: n=41</td></tr></table>\n\n"
    )
    da_report.text = da_report.text.replace(
        "#### MAJOR", block + "#### MAJOR", 1
    )
    text, expressions = synthesis_for(panel_reports)
    synthesis = cps.parse_synthesis("s.md", text, FULL)
    with pytest.raises(cps.ReportError, match="raw HTML issue-table"):
        cps.layer2_check(panel_reports, FULL, expressions, synthesis, [])


def test_da_nested_html_issue_table_in_canonical_row_fails_synthesis():
    panel_reports = reports()
    da_report = next(report for report in panel_reports if report.role == "da")
    nested = (
        "real issue <table><tr><th>#</th><th>Evidence Anchor</th></tr>"
        '<tr><td>C9</td><td>text: "impossible df" p. 4</td></tr></table>'
    )
    da_report.text = da_report.text.replace(
        "#### MAJOR\n"
        "| # | Issue | Evidence Anchor |\n"
        "|---|-------|-----------------|",
        "#### MAJOR\n"
        "| # | Issue | Evidence Anchor |\n"
        "|---|-------|-----------------|\n"
        f'| M1 | {nested} | text: "quote" p. 1 |',
        1,
    )
    text, expressions = synthesis_for(panel_reports)
    synthesis = cps.parse_synthesis("s.md", text, FULL)
    with pytest.raises(cps.ReportError, match="raw HTML issue-table"):
        cps.layer2_check(panel_reports, FULL, expressions, synthesis, [])


def test_da_bare_html_row_fails_synthesis():
    panel_reports = reports()
    da_report = next(report for report in panel_reports if report.role == "da")
    block = (
        "#### ADDITIONAL CRITICAL FINDINGS\n"
        "<tr><td>C9</td><td>text: n=41</td></tr>\n\n"
    )
    da_report.text = da_report.text.replace(
        "#### MAJOR", block + "#### MAJOR", 1
    )
    text, expressions = synthesis_for(panel_reports)
    synthesis = cps.parse_synthesis("s.md", text, FULL)
    with pytest.raises(cps.ReportError, match="raw HTML issue-table"):
        cps.layer2_check(panel_reports, FULL, expressions, synthesis, [])


def test_da_empty_major_id_fails_in_synthesis_path():
    panel_reports = reports()
    da_report = next(report for report in panel_reports if report.role == "da")
    marker = "|---|-------|-----------------|"
    before, trailing = da_report.text.rsplit(marker, 1)
    da_report.text = (
        before + marker + '\n|  | Issue | text: "quote" |' + trailing
    )
    text, expressions = synthesis_for(panel_reports)
    synthesis = cps.parse_synthesis("s.md", text, FULL)
    with pytest.raises(
        (cps.ReportError, cps.SynthesisError), match="empty MAJOR # cell"
    ):
        cps.layer2_check(panel_reports, FULL, expressions, synthesis, [])


def test_da_empty_critical_anchor_fails_in_synthesis_path():
    panel_reports = reports(da_ids=("C1",))
    da_report = next(report for report in panel_reports if report.role == "da")
    da_report.text = da_report.text.replace(
        '| C1 | Issue | text: "quoted evidence" p. 1 |',
        "| C1 | Issue |  |",
        1,
    )
    text, expressions = synthesis_for(
        panel_reports, {"C1": "VALIDATED"}, marker_count=1
    )
    synthesis = cps.parse_synthesis("s.md", text, FULL)
    with pytest.raises(cps.ReportError, match="ANCHOR-MISSING"):
        cps.layer2_check(panel_reports, FULL, expressions, synthesis, [])


@pytest.mark.parametrize(
    "anchor,fragment",
    [
        ("", "ANCHOR-MISSING"),
        ("see page 3", "ANCHOR-INVALID"),
    ],
)
def test_da_major_anchor_fails_in_synthesis_path(anchor, fragment):
    panel_reports = reports()
    da_report = next(report for report in panel_reports if report.role == "da")
    marker = "|---|-------|-----------------|"
    before, trailing = da_report.text.rsplit(marker, 1)
    da_report.text = (
        before + marker + f"\n| M1 | Issue | {anchor} |" + trailing
    )
    text, expressions = synthesis_for(panel_reports)
    synthesis = cps.parse_synthesis("s.md", text, FULL)
    with pytest.raises(cps.ReportError, match=fragment):
        cps.layer2_check(panel_reports, FULL, expressions, synthesis, [])


def test_da_valid_major_anchor_passes_in_synthesis_path():
    panel_reports = reports()
    da_report = next(report for report in panel_reports if report.role == "da")
    marker = "|---|-------|-----------------|"
    before, trailing = da_report.text.rsplit(marker, 1)
    da_report.text = (
        before + marker
        + '\n| M1 | Issue | text: "short quote" |'
        + trailing
    )
    text, expressions = synthesis_for(panel_reports)
    synthesis = cps.parse_synthesis("s.md", text, FULL)
    assert cps.layer2_check(
        panel_reports, FULL, expressions, synthesis, []
    ) == []


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


def test_methodology_focus_d1_warn_is_major_revision():
    contract, expressions = cps.load_contract(MF_PATH)
    fired, decision = _evaluate_profile(
        contract,
        expressions,
        {"D1": [state("warn")], "D2": [state("pass")]},
    )
    assert fired == ["F3"]
    assert decision == "editorial_decision=major_revision"


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

    high_block = {**base, "D4": [state("block")]}
    assert _evaluate_profile(contract, expressions, high_block)[1] == \
        "editorial_decision=major_revision"

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


def test_n2_majority_split_cannot_harden_the_decision():
    contract, expressions = cps.load_contract(FULL_PATH)
    assessed = {
        "D1": [state("warn")],
        "D2": [state("pass")],
        "D3": [state("warn"), state("pass")],
        "D4": [state("pass")],
        "D5": [state("pass")],
        "D6": [state("pass")],
    }
    fired, decision = _evaluate_profile(contract, expressions, assessed)
    assert fired == ["F5"]
    assert decision == "editorial_decision=minor_revision"
