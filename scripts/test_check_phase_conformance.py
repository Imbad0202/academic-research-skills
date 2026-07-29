"""Tests for the six Schema 13.2 phase-conformance check families."""
from __future__ import annotations

import json
import re
import time
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
    with pytest.raises(
        phase.ConformanceError,
        match=r"what_triggers_fatal: line for dimension D1, found 0",
    ):
        parse_plan("methodology", {"D1": {"what_triggers_fatal": None}})


def test_duplicate_scoring_plan_diagnostic_names_dimension():
    text = phase1_text("methodology").replace(
        "\n[CONTRACT-ACKNOWLEDGED]",
        "\n### D3: argumentative_coherence\n[CONTRACT-ACKNOWLEDGED]",
    )
    with pytest.raises(
        phase.ConformanceError,
        match=r"duplicate scoring-plan subsection: D3: argumentative_coherence",
    ):
        phase.parse_phase1("p1.md", text, FULL, "methodology")


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


def phase2_with_dissent_section(
    body_lines, *, late=False, role="methodology", overrides=None
) -> str:
    """Splice a custom ## Scoring Plan Dissent section into a phase 2 card."""
    text = phase2_text(role, overrides)
    section = "\n".join(
        ["## Scoring Plan Dissent", "", *body_lines, ""]
    ) + "\n"
    anchor = "## Review Body" if late else "## Dimension Scores"
    return text.replace(anchor, f"{section}{anchor}", 1)


def test_empty_dissent_section_is_read_as_no_dissent():
    text = phase2_with_dissent_section([])
    assert phase.parse_dissent_dimensions(text).dimensions == set()


def test_empty_dissent_section_records_an_auditable_diagnostic():
    text = phase2_with_dissent_section([])
    diagnostics = phase.parse_dissent_dimensions(text).diagnostics
    assert len(diagnostics) == 1
    assert "[DISSENT-EMPTY-SECTION:" in diagnostics[0]


def test_observed_placeholder_retraction_prose_no_longer_aborts():
    # Verbatim shape of the 2026-07-27 perspective Phase 2 abort (#609).
    text = phase2_with_dissent_section([
        "*(omitted — Phase 1 plan holds)*",
        "",
        "Wait — that placeholder is not permitted. Removing it.",
    ])
    assert phase.parse_dissent_dimensions(text).dimensions == set()


@pytest.mark.parametrize(
    "placeholder", ["none", "omitted", "not applicable", "N/A"]
)
def test_placeholder_words_are_not_a_dissent(placeholder):
    text = phase2_with_dissent_section([placeholder])
    parsed = phase.parse_dissent_dimensions(text)
    assert parsed.dimensions == set()
    assert len(parsed.diagnostics) == 1


def test_empty_dissent_section_after_dimension_scores_is_tolerated():
    text = phase2_with_dissent_section([], late=True)
    parsed = phase.parse_dissent_dimensions(text)
    assert parsed.dimensions == set()
    assert len(parsed.diagnostics) == 1


def test_canonical_dissent_still_parses_without_a_diagnostic():
    _, text = parse_report("methodology", {"D1": "block"}, dissent=("D1",))
    parsed = phase.parse_dissent_dimensions(text)
    assert parsed.dimensions == {"D1"}
    assert parsed.diagnostics == []


def test_claimed_dissent_without_dimension_id_still_aborts():
    text = phase2_with_dissent_section(["rationale: plan was inadequate"])
    with pytest.raises(
        phase.ConformanceError, match="must name dimension_id"
    ):
        phase.parse_dissent_dimensions(text)


def test_duplicate_dissent_dimension_ids_still_abort():
    text = phase2_with_dissent_section([
        "dimension_id: D1",
        "rationale: plan was inadequate",
        "dimension_id: D1",
        "rationale: plan was inadequate again",
    ])
    with pytest.raises(
        phase.ConformanceError, match="duplicate dimension_id"
    ):
        phase.parse_dissent_dimensions(text)


def test_claimed_dissent_after_dimension_scores_still_aborts():
    text = phase2_with_dissent_section(
        ["dimension_id: D1", "rationale: plan was inadequate"], late=True
    )
    with pytest.raises(
        phase.ConformanceError, match="must precede"
    ):
        phase.parse_dissent_dimensions(text)


def test_duplicate_empty_dissent_headings_still_abort():
    text = phase2_with_dissent_section([])
    text = text.replace(
        "## Scoring Plan Dissent",
        "## Scoring Plan Dissent\n\n## Scoring Plan Dissent",
        1,
    )
    with pytest.raises(
        phase.ConformanceError, match="duplicate ## Scoring Plan Dissent"
    ):
        phase.parse_dissent_dimensions(text)


def test_absent_dissent_section_emits_no_diagnostic():
    parsed = phase.parse_dissent_dimensions(phase2_text("methodology"))
    assert parsed.dimensions == set()
    assert parsed.diagnostics == []


def test_empty_section_diagnostic_reports_the_non_blank_line_count():
    text = phase2_with_dissent_section(["prose one", "", "prose two"])
    diagnostic = phase.parse_dissent_dimensions(text).diagnostics[0]
    assert "2 non-blank line(s)" in diagnostic


@pytest.mark.parametrize("field_line", [
    "- dimension_id: D1",
    "* dimension_id: D1",
    "+ dimension_id: D1",
    "> dimension_id: D1",
    "1. dimension_id: D1",
    "**dimension_id**: D1",
    "`dimension_id`: D1",
    "  dimension_id: D1",
    "dimension_id：D1",
    "- [ ] dimension_id: D1",
    "- [x] dimension_id: D1",
    "* [X] rationale: the phase 1 plan was inadequate",
    "| dimension_id: D1 |",
    "[dimension_id]: D1",
    "_dimension_id_: D1",
    "dimension id: D1",
    "- rationale: the phase 1 plan was inadequate",
    "**rationale**: the phase 1 plan was inadequate",
    "| rationale: the phase 1 plan was inadequate |",
    "[dimension_id](#dissent): D1",
    "[rationale][note]: the phase 1 plan was inadequate",
    "<b>dimension_id</b>: D1",
    "[dimension_id](https://example.com/a:b): D1",
    "[rationale](https://example.com): the phase 1 plan was inadequate",
    "> | dimension_id: D1 |",
    "\tdimension_id: D1",
])
def test_non_canonical_dissent_field_shape_aborts(field_line):
    text = phase2_with_dissent_section([field_line])
    with pytest.raises(
        phase.ConformanceError, match="canonical unbulleted"
    ):
        phase.parse_dissent_dimensions(text)


@pytest.mark.parametrize("hidden", [
    ["```", "dimension_id: D1", "rationale: plan was inadequate", "```"],
    ["<!-- dimension_id: D1 -->", "<!-- rationale: plan was inadequate -->"],
    ["## dimension_id: D1", "## rationale: plan was inadequate"],
])
def test_a_dissent_hidden_from_the_sanitizers_still_aborts(hidden):
    """Fences, comments and headings must not launder a dissent field."""
    with pytest.raises(
        phase.ConformanceError, match="canonical unbulleted"
    ):
        phase.parse_dissent_dimensions(phase2_with_dissent_section(hidden))


@pytest.mark.parametrize("wrapper", [
    ("## dimension_id: D3", "## rationale: second plan was inadequate"),
    ("<!-- dimension_id: D3 -->", "<!-- rationale: second -->"),
    ("```", "dimension_id: D3", "rationale: second", "```"),
])
def test_a_canonical_dissent_cannot_hide_a_second_laundered_one(wrapper):
    text = phase2_with_dissent_section([
        "dimension_id: D1",
        "rationale: plan was inadequate",
        *wrapper,
    ])
    with pytest.raises(
        phase.ConformanceError, match="canonical unbulleted"
    ):
        phase.parse_dissent_dimensions(text)


@pytest.mark.parametrize("body", [
    ["```", "(omitted — the Phase 1 plan holds)", "```"],
    ["<!-- no dissent; the Phase 1 plan holds -->"],
])
def test_a_wrapper_carrying_no_field_stays_tolerated(body):
    parsed = phase.parse_dissent_dimensions(phase2_with_dissent_section(body))
    assert parsed.dimensions == set()
    assert len(parsed.diagnostics) == 1


def test_a_field_shaped_heading_outside_the_span_is_not_a_dissent():
    """parse_report permits extra H2 sections; they are not dissent fields."""
    text = phase2_with_dissent_section(["*(omitted)*"]).replace(
        "## Review Body", "## Rationale: Additional notes\n\nprose\n\n"
        "## Review Body", 1
    )
    parsed = phase.parse_dissent_dimensions(text)
    assert parsed.dimensions == set()
    assert len(parsed.diagnostics) == 1


def test_a_fenced_heading_does_not_end_the_scanned_span():
    text = phase2_with_dissent_section([
        "dimension_id: D1",
        "rationale: plan was inadequate",
        "```",
        "## Notes",
        "dimension_id: D3",
        "rationale: second plan was inadequate",
        "```",
    ])
    with pytest.raises(
        phase.ConformanceError, match="canonical unbulleted"
    ):
        phase.parse_dissent_dimensions(text)


@pytest.mark.parametrize("sample", [
    "a\n```\nb\n```\nc",
    "a\n~~~\nb\n~~~\nc",
    "a\n````\nb\n```\nc\n````\nd",
    "a\n```py`\nb\n",
    "a\n   ```\nb\n```\nc",
    "a\n```\nb",
    "x\r\ny\n```\nz\n```\n",
])
def test_local_fence_state_agrees_with_the_shared_stripper(sample):
    """Anti-drift: the mirrored bookkeeping must track panel.strip_fences."""
    unfenced = [
        line for line, fenced in phase._lines_with_fence_state(sample)
        if not fenced
    ]
    assert unfenced == panel.strip_fences(sample)


@pytest.mark.parametrize("fence", ["```", "~~~", "````"])
def test_a_fenced_structural_heading_does_not_end_the_scanned_span(fence):
    """A real section title inside a fence is inert, not a boundary."""
    text = phase2_with_dissent_section([
        "dimension_id: D1",
        "rationale: plan was inadequate",
        fence,
        "## Dimension Scores",
        "dimension_id: D3",
        "rationale: second plan was inadequate",
        fence,
    ])
    with pytest.raises(
        phase.ConformanceError, match="canonical unbulleted"
    ):
        phase.parse_dissent_dimensions(text)


def test_a_backtick_fence_with_a_backtick_info_string_is_not_a_fence():
    """CommonMark: it opens no fence, so its lines stay ordinary content.

    Treating it as one would hide the canonical dissent below it, which the
    raw-span scan would then report as a laundered field.
    """
    text = phase2_with_dissent_section([
        "```py`",
        "dimension_id: D1",
        "rationale: plan was inadequate",
    ])
    assert phase.parse_dissent_dimensions(text).dimensions == {"D1"}


def test_a_commented_heading_ends_the_span_and_credits_nothing():
    """Documents an ACCEPTED miss, not a desired behaviour.

    `split_sections` reads a commented heading as a real boundary, so the
    fields below it land in that other section. Teaching the raw walk to
    disagree cost four false aborts across review rounds and closed only this
    miss, which grants the seat nothing: no dissent is credited, so no
    trigger-binding exemption follows. Change deliberately, never incidentally.
    """
    text = phase2_with_dissent_section([
        "<!--",
        "## Notes",
        "dimension_id: D1",
        "rationale: plan was inadequate",
        "-->",
    ])
    assert phase.parse_dissent_dimensions(text).dimensions == set()


def test_a_comment_marker_inside_a_fence_does_not_leak_the_span():
    """Comment delimiters are inert inside a fence, as they are to Markdown.

    Treating one as real would swallow every later heading, run the span into
    ## Review Body, and abort a valid card on prose there.
    """
    text = phase2_with_dissent_section([
        "```", "<!-- an unmatched marker in an example", "```",
    ]).replace(
        "## Review Body\n\n",
        "## Review Body\n\nrationale: the seat explains itself here\n\n",
        1,
    )
    parsed = phase.parse_dissent_dimensions(text)
    assert parsed.dimensions == set()
    assert len(parsed.diagnostics) == 1


def test_an_inline_code_comment_marker_does_not_leak_the_span():
    """CommonMark reads it as code; only a line-initial opener hides a head."""
    text = phase2_with_dissent_section([
        "The literal `<!--` token is discussed here without a closer.",
    ]).replace(
        "## Review Body\n\n",
        "## Review Body\n\nrationale: the seat explains itself here\n\n",
        1,
    )
    parsed = phase.parse_dissent_dimensions(text)
    assert parsed.dimensions == set()
    assert len(parsed.diagnostics) == 1


def test_a_duplicate_field_hidden_in_a_fence_is_counted_not_matched():
    """Identical strings do not launder: occurrences are compared."""
    text = phase2_with_dissent_section([
        "dimension_id: D1",
        "rationale: plan was inadequate",
        "```",
        "dimension_id: D1",
        "rationale: plan was inadequate",
        "```",
    ])
    with pytest.raises(
        phase.ConformanceError, match="canonical unbulleted"
    ):
        phase.parse_dissent_dimensions(text)


def test_a_commented_out_dissent_is_not_credited_as_one():
    """Pre-existing hole: strip_fences leaves comments, so canonical fields
    inside `<!-- ... -->` were parsed as a real dissent and granted the
    trigger-binding exemption, letting a drifting trigger through."""
    text = phase2_with_dissent_section([
        "<!--", "dimension_id: D1", "rationale: plan was inadequate", "-->",
    ])
    with pytest.raises(
        phase.ConformanceError, match="canonical unbulleted"
    ):
        phase.parse_dissent_dimensions(text)


def test_a_commented_out_dissent_cannot_excuse_a_drifting_trigger(tmp_path):
    args = write_cli_files(tmp_path, "methodology")
    phase2_path = Path(args[args.index("--phase2") + 1])
    text = phase2_with_dissent_section(
        ["<!--", "dimension_id: D1", "rationale: plan was inadequate", "-->"],
        overrides={"D1": "block"},
    ).replace(
        'trigger: "block evidence pattern for D1"',
        'trigger: "novel post hoc trigger never committed in phase 1"',
        1,
    )
    phase2_path.write_text(text, encoding="utf-8")
    assert phase.main(args + ["--role", "methodology"]) == \
        phase.EXIT_CONFORMANCE


@pytest.mark.parametrize("opener_line", [
    "<!-- an aside --> <!--",
    "<!-- an aside --><!--",
])
def test_a_comment_reopened_on_its_opening_line_still_hides(opener_line):
    """Comment state is resolved by delimiter ORDER, not by presence.

    A line holding a closer AND a later opener leaves the comment open, so
    reading it as closed credited the fields below as a real dissent and
    handed back the trigger-binding exemption this scan exists to withhold.
    """
    text = phase2_with_dissent_section([
        opener_line,
        "dimension_id: D1",
        "rationale: plan was inadequate",
        "-->",
    ])
    with pytest.raises(
        phase.ConformanceError, match="canonical unbulleted"
    ):
        phase.parse_dissent_dimensions(text)


def test_a_comment_reopened_on_its_closing_line_still_hides():
    """Same order rule while already inside one: the closer does not win
    merely by appearing on a line that reopens after it."""
    text = phase2_with_dissent_section([
        "<!--",
        "an aside",
        "--> visible again <!--",
        "dimension_id: D1",
        "rationale: plan was inadequate",
        "-->",
    ])
    with pytest.raises(
        phase.ConformanceError, match="canonical unbulleted"
    ):
        phase.parse_dissent_dimensions(text)


@pytest.mark.parametrize("opener", [
    "- <!--", "* <!--", "+ <!--", "1. <!--", "1) <!--",
    "> <!--", "> - <!--", "  - <!--", "-   <!--",
    "-    <!--", ">   <!--", ">    <!--",
    "> \t<!--", " > \t<!--",
])
def test_a_container_prefixed_opener_still_hides(opener):
    """A block opener behind a list or quote marker is still a block opener.

    Rendered through CommonMark, `- <!--` puts the fields that follow inside
    raw HTML a reader never sees, and the bullet form needs no closer at all.
    Crediting them handed the trigger-binding exemption to a dissent invisible
    on the page, which is the hole the raw-span scan exists to close.
    """
    text = phase2_with_dissent_section([
        opener,
        "dimension_id: D1",
        "rationale: plan was inadequate",
    ])
    with pytest.raises(
        phase.ConformanceError, match="canonical unbulleted"
    ):
        phase.parse_dissent_dimensions(text)


@pytest.mark.parametrize("indented", [
    "    - <!-- a draft this seat withdrew",
    "     > <!--",
    "    1. <!--",
    "\t- <!--",
    "-     <!--",
    ">     <!--",
    "> - \t<!--",
    "  - \t<!--",
    " 1. \t<!--",
])
def test_an_indented_container_marker_is_code_not_a_comment(indented):
    """Four columns before the marker is indented code, so it hides nothing.

    Widening the opener to container prefixes must not let the outer and inner
    indentation allowances add up: `    - <!--` renders as a code example with
    the fields below it in the clear, and striking them aborts a valid card on
    a phase that permits no retry. A tab is measured to the next four-column
    stop, not counted as one character, so `  - \\t<!--` reaches column eight
    and is code while `> \\t<!--` reaches column four and is not.
    """
    text = phase2_with_dissent_section([
        indented,
        "dimension_id: D1",
        "rationale: plan was inadequate",
    ])
    assert phase.parse_dissent_dimensions(text).dimensions == {"D1"}


@pytest.mark.parametrize("marker", ["2.", "9)", "10.", "  2."])
def test_an_ordered_marker_cannot_interrupt_a_paragraph(marker):
    """Only an ordered list starting at 1 may interrupt an open paragraph.

    After a paragraph line, `2. <!--` is paragraph text: the marker is not a
    list, no raw-HTML block opens, and the fields below stay on the page.
    Striking them aborts a phase that permits no retry.
    """
    text = phase2_with_dissent_section([
        "Reviewed the plan and stand by it.",
        f"{marker} <!--",
        "dimension_id: D1",
        "rationale: plan was inadequate",
    ])
    assert phase.parse_dissent_dimensions(text).dimensions == {"D1"}


@pytest.mark.parametrize("marker", ["1.", "1)", "2.", "10.", "-", ">"])
def test_a_container_marker_at_a_block_start_still_opens(marker):
    """After a blank line every marker opens a list or quote, so the comment
    inside it hides the fields below and the card is refused.

    A block start reached some other way (a thematic break, a heading, a
    setext underline) is covered separately; one reached from an open
    paragraph is not a block start at all for a non-1 ordered marker.
    """
    text = phase2_with_dissent_section([
        f"{marker} <!--",
        "dimension_id: D1",
        "rationale: plan was inadequate",
    ])
    with pytest.raises(
        phase.ConformanceError, match="canonical unbulleted"
    ):
        phase.parse_dissent_dimensions(text)


@pytest.mark.parametrize("closer,marker", [
    ("---", "2."), ("***", "9)"), ("___", "10."),
    ("### an aside", "2."), ("#### deeper", "2."), ("#", "2."),
    ("-", "2."),
])
def test_a_paragraph_closing_line_restores_every_marker(closer, marker):
    """A thematic break or an ATX heading ends the paragraph above it.

    The line after one is at a genuine block start, where an ordered marker of
    any start number opens a list and so a raw-HTML comment. Reading it with
    the paragraph-restricted pattern credited fields no reader can see, a
    bypass neither `main` nor the pre-paragraph-fix commit had.
    """
    text = phase2_with_dissent_section([
        "Reviewed the plan and stand by it.",
        closer,
        f"{marker} <!--",
        "dimension_id: D1",
        "rationale: plan was inadequate",
        "<!-- -->",
    ])
    with pytest.raises(
        phase.ConformanceError, match="canonical unbulleted"
    ):
        phase.parse_dissent_dimensions(text)


def test_a_deeply_nested_quote_line_resolves_without_backtracking():
    """The opener test runs on every unfenced line, so it must stay linear.

    An earlier spelling let a single space be claimed by either of two
    adjacent optional-space groups, giving two ways to match each marker and
    doubling the work per level: 20 markers already cost 0.17s and 30 would
    have stalled the checker instead of returning a verdict.
    """
    line = "> " * 24 + "prose that never opens a comment"
    started = time.perf_counter()
    assert phase._opens_comment(line, paragraph_open=False) is False
    assert time.perf_counter() - started < 0.5


@pytest.mark.parametrize("comment_block", [
    ["<!-- an aside -->"],
    ["<!--", "an aside", "-->"],
    ["<!-- an aside", "-->"],
])
def test_a_comment_block_is_not_a_paragraph(comment_block):
    """Raw HTML is not a paragraph, so the line after a comment block is at a
    block start where any ordered marker opens a list.

    Recording the comment's own lines as an open paragraph read the next
    `2. <!--` with the restricted pattern and credited the fields it hides.
    """
    text = phase2_with_dissent_section([
        *comment_block,
        "2. <!--",
        "dimension_id: D1",
        "rationale: plan was inadequate",
    ])
    with pytest.raises(
        phase.ConformanceError, match="canonical unbulleted"
    ):
        phase.parse_dissent_dimensions(text)


@pytest.mark.parametrize("nested", ["- 2. <!--", "> 2. <!--", "> - 2. <!--"])
def test_a_nested_marker_after_a_paragraph_is_a_declared_limit(nested):
    """Documents an ACCEPTED miss, not a desired behaviour.

    An outer bullet or quote interrupts the paragraph, and inside the
    container it opens the nested ordered list may start at any number. The
    start-at-1 restriction is applied to every ordered marker in the prefix
    rather than only the interrupting one, because telling them apart means
    tracking which container each marker sits in. That is the block-structure
    modelling whose three earlier approximations cost 425, 77 and 154 false
    aborts on the render grid. Tracked in #613. Change deliberately.
    """
    text = phase2_with_dissent_section([
        "Standing by the plan.",
        nested,
        "dimension_id: D1",
        "rationale: plan was inadequate",
    ])
    assert phase.parse_dissent_dimensions(text).dimensions == {"D1"}


@pytest.mark.parametrize("orphan", ["==", "--", "=", "===="])
def test_an_orphan_setext_marker_is_paragraph_text(orphan):
    """A setext underline needs a paragraph above it to underline.

    With nothing above, `==` or `--` is ordinary paragraph text and OPENS a
    paragraph rather than closing one, so a non-1 ordered marker on the next
    line cannot interrupt it and the fields below stay on the page. Clearing
    the flag here refused a card the base branch accepted.
    """
    text = phase2_with_dissent_section([
        orphan,
        "2. <!--",
        "dimension_id: D1",
        "rationale: plan was inadequate",
    ])
    assert phase.parse_dissent_dimensions(text).dimensions == {"D1"}


@pytest.mark.parametrize("marker", ["-", "*", "+"])
def test_a_lone_bullet_at_a_block_start_is_an_empty_list_item(marker):
    """With no paragraph above it, a bullet alone is an empty list item, so the
    next line is at a block start where any ordered marker opens a comment."""
    text = phase2_with_dissent_section([
        marker,
        "2. <!--",
        "dimension_id: D1",
        "rationale: plan was inadequate",
        "<!-- -->",
    ])
    with pytest.raises(
        phase.ConformanceError, match="canonical unbulleted"
    ):
        phase.parse_dissent_dimensions(text)


@pytest.mark.parametrize("marker", ["*", "+", "2.", "10)"])
def test_a_lone_marker_cannot_interrupt_a_paragraph(marker):
    """An empty list item has a blank first line, so it cannot interrupt a
    paragraph: the line stays paragraph text and the paragraph stays open.

    `-` is the exception and is covered above, because after a paragraph it
    reads as a setext underline rather than a marker. Treating every lone
    marker as a paragraph-closer looked symmetrical and aborted valid cards.
    """
    text = phase2_with_dissent_section([
        "Standing by the plan.",
        marker,
        "2. <!--",
        "dimension_id: D1",
        "rationale: plan was inadequate",
    ])
    assert phase.parse_dissent_dimensions(text).dimensions == {"D1"}


def test_a_setext_underline_closes_the_paragraph_above_it():
    text = phase2_with_dissent_section([
        "An underlined heading",
        "===",
        "2. <!--",
        "dimension_id: D1",
        "rationale: plan was inadequate",
        "<!-- -->",
    ])
    with pytest.raises(
        phase.ConformanceError, match="canonical unbulleted"
    ):
        phase.parse_dissent_dimensions(text)


@pytest.mark.parametrize("whitespace", ["　", " ", " ", "\x0c"])
def test_a_line_of_exotic_whitespace_is_not_a_blank_line(whitespace):
    """CommonMark counts only spaces and tabs as blank.

    A line holding an ideographic space is a paragraph to the renderer, which
    is a live shape in zh-TW output. Treating it as blank put the next line at
    a block start, read `2. <!--` as an opener, struck the visible fields
    below it and aborted a phase that permits no retry.
    """
    text = phase2_with_dissent_section([
        "Reviewed the plan and stand by it.",
        whitespace,
        "2. <!--",
        "dimension_id: D1",
        "rationale: plan was inadequate",
    ])
    assert phase.parse_dissent_dimensions(text).dimensions == {"D1"}


@pytest.mark.parametrize("marker", ["1.", "1)", "-", "*", ">"])
def test_a_paragraph_interrupting_marker_still_opens(marker):
    """A bullet, a blockquote, and an ordered list starting at 1 DO interrupt
    a paragraph, so those keep hiding the fields below them."""
    text = phase2_with_dissent_section([
        "Reviewed the plan and stand by it.",
        f"{marker} <!--",
        "dimension_id: D1",
        "rationale: plan was inadequate",
    ])
    with pytest.raises(
        phase.ConformanceError, match="canonical unbulleted"
    ):
        phase.parse_dissent_dimensions(text)


def test_a_balanced_container_prefixed_comment_hides_nothing_after():
    """Same order rule behind a marker: a closed aside leaves the dissent."""
    text = phase2_with_dissent_section([
        "- <!-- drafted and withdrawn -->",
        "dimension_id: D1",
        "rationale: plan was inadequate",
    ])
    assert phase.parse_dissent_dimensions(text).dimensions == {"D1"}


@pytest.mark.parametrize("container,opener", [
    ("- an earlier note", "2. <!--"),
    ("- an earlier note", "    <!--"),
    ("- an earlier note", "\t<!--"),
    ("- an earlier note", "- 2. <!--"),
    ("> an earlier note", "> 2. <!--"),
    ("> an earlier note", ">     <!--"),
])
def test_an_opener_inside_an_open_container_is_a_declared_limit(
    container, opener
):
    """Documents an ACCEPTED miss, not a desired behaviour.

    An open list item or block quote shifts the column at which a block
    starts, and changing marker type starts a fresh list, so shapes that read
    as indented text at absolute column N are block openers relative to the
    container. Resolving them needs a container parser, and this walk refuses
    to grow one on measured grounds: over one 8064-shape render grid `main`
    credits 4552 hidden shapes and this parser 1424, both at zero false
    aborts, while the two interim spellings that approximated block structure
    scored 1112/144 and 1709/57. Cost stated in full: each miss grants a
    trigger-binding exemption for a dissent the page does not show. Tracked
    in #613, whose closure is a reviewer-output-grammar rule, not more
    parsing. Change deliberately.
    """
    text = phase2_with_dissent_section([
        container,
        opener,
        "dimension_id: D1",
        "rationale: plan was inadequate",
        "-->",
    ])
    assert phase.parse_dissent_dimensions(text).dimensions == {"D1"}


def test_an_angle_bracket_field_label_is_read_as_prose():
    """A `<dimension_id>: D1` placeholder is stripped as a markup span, so it
    reads as prose and the section is tolerated instead of aborting.

    Deliberate, and on the safe side of the asymmetry: nothing is credited, so
    no exemption follows, and leaving a template placeholder in is the very
    mistake #609 exists to stop from killing a panel.
    """
    text = phase2_with_dissent_section(["<dimension_id>: D1"])
    parsed = phase.parse_dissent_dimensions(text)
    assert parsed.dimensions == set()
    assert len(parsed.diagnostics) == 1


def test_an_indented_opener_continuing_a_paragraph_is_a_declared_limit():
    """Documents an ACCEPTED miss, not a desired behaviour.

    Four spaces makes an indented code block only when the line STARTS a
    block. After a paragraph line it is lazy continuation, so CommonMark does
    form the comment and the fields below are invisible to a reader while
    still credited here. Deciding that needs the surrounding block context,
    which the span walk deliberately does not model: every mechanism added to
    this walk has produced a false abort of its own, and an indented `<!--`
    that merely starts an example must stay inert. Cost stated in full: this
    grants a trigger-binding exemption for a dissent the page does not show.
    Change deliberately, never incidentally.
    """
    text = phase2_with_dissent_section([
        "Reviewed the plan and stand by it.",
        "    <!--",
        "dimension_id: D1",
        "rationale: plan was inadequate",
        "-->",
    ])
    assert phase.parse_dissent_dimensions(text).dimensions == {"D1"}


@pytest.mark.parametrize("line,entering,expected", [
    ("<!--", False, True),
    ("- <!--", False, True),
    ("> <!--", False, True),
    ("1. <!--", False, True),
    ("- <!-- a -->", False, False),
    ("- text <!--", False, False),
    ("    <!--", False, False),
    ("    - <!--", False, False),
    ("     > <!--", False, False),
    ("-     <!--", False, False),
    (">     <!--", False, False),
    ("   - <!--", False, True),
    (">    <!--", False, True),
    ("- `<!--`", False, False),
    ("<!-->", False, False),
    ("<!--->", False, False),
    ("<!-- -->", False, False),
    ("<!--x-->", False, False),
    ("<!-- a --> <!--", False, True),
    ("<!-- a --><!--", False, True),
    ("<!-- a --> <!-- b -->", False, False),
    ("   <!--", False, True),
    ("    <!--", False, False),
    ("prose <!--", False, False),
    ("plain prose", False, False),
    ("still inside", True, True),
    ("--> out", True, False),
    ("--> out <!--", True, True),
    ("-->", True, False),
])
def test_comment_state_after_resolves_by_order(line, entering, expected):
    """The state machine itself, pinned line by line.

    Both directions matter: a state left open credits fields the reader never
    saw, and a state closed too eagerly aborts a card whose fields are in the
    clear. Neither is visible from the parse-level tests alone.
    """
    assert phase._comment_state_after(line, commented=entering) is expected


@pytest.mark.parametrize("empty_comment", ["<!-->", "<!--->", "<!-- -->"])
def test_a_commonmark_empty_comment_hides_nothing_after(empty_comment):
    """CommonMark closes `<!-->` and `<!--->` on their own dashes.

    Ordering the delimiter scan must not read those as unterminated: doing so
    struck the fields below and aborted a card that presence-testing for a
    closer had passed, which is the failure this tolerance removes.
    """
    text = phase2_with_dissent_section([
        empty_comment,
        "dimension_id: D1",
        "rationale: plan was inadequate",
    ])
    assert phase.parse_dissent_dimensions(text).dimensions == {"D1"}


def test_a_comment_closed_and_reopened_then_closed_hides_nothing_after():
    """The order rule cuts both ways: a line that ends outside a comment
    leaves the fields below visible, so a balanced aside cannot abort a
    valid card."""
    text = phase2_with_dissent_section([
        "<!-- drafted --> <!-- reviewed -->",
        "dimension_id: D1",
        "rationale: plan was inadequate",
    ])
    assert phase.parse_dissent_dimensions(text).dimensions == {"D1"}


def test_a_comment_opened_after_prose_on_its_line_is_a_declared_limit():
    """Documents an ACCEPTED miss, not a desired behaviour.

    Only a block opener starts a comment, so a marker following text on its
    own line leaves the fields below credited. Cost stated in full, since it
    is not the free kind: CommonMark does form that comment, so this grants a
    trigger-binding exemption for a dissent the rendered page does not show
    (omitting the section grants no exemption at all, so the two are not
    equivalent). Refused anyway, because closing it deterministically means
    reading a bare `<!--` inside unrestricted `rationale:` text as an opener,
    which aborts the valid card pinned by the test below, and a Phase 2 abort
    is unretryable. A grammar rule requiring seats to write comment syntax in
    inline code would close it on the prompt side; that is a separate change
    to reviewer output, not to this parser. Change deliberately.
    """
    text = phase2_with_dissent_section([
        "an aside <!--",
        "dimension_id: D1",
        "rationale: plan was inadequate",
        "-->",
    ])
    assert phase.parse_dissent_dimensions(text).dimensions == {"D1"}


def test_an_unbackticked_marker_in_a_rationale_hides_no_later_dissent():
    """The false abort that keeps the opener rule at block start.

    `rationale:` text is unrestricted, so a seat discussing an unclosed
    marker is a plausible card, not decoration. Reading that mid-line opener
    as real strikes the second dissent below it and aborts an unretryable
    Phase 2 on a card that claimed both dissents in the clear.
    """
    text = phase2_with_dissent_section([
        "dimension_id: D1",
        "rationale: the card left an unclosed <!-- marker in its own output",
        "dimension_id: D2",
        "rationale: the second plan was inadequate too",
    ])
    assert phase.parse_dissent_dimensions(text).dimensions == {"D1", "D2"}


def test_a_canonical_rationale_may_mention_comment_syntax():
    """`rationale: <nonempty explanation>` permits any text, including the
    literal comment tokens; rewriting them broke equality with the canonical
    parse and aborted an unretryable Phase 2 on a valid card."""
    text = phase2_with_dissent_section([
        "dimension_id: D1",
        "rationale: the seat wrote `<!--` and `-->` in its explanation",
    ])
    assert phase.parse_dissent_dimensions(text).dimensions == {"D1"}


def test_a_comment_opened_before_the_heading_credits_no_dissent():
    """The bypass: the fields parse into the dissent body, so they must not
    be credited merely because the opener sits above the heading."""
    text = phase2_text("methodology").replace(
        "## Dimension Scores",
        "<!--\n\n## Scoring Plan Dissent\n\ndimension_id: D1\n"
        "rationale: plan was inadequate\n\n-->\n\n## Dimension Scores",
        1,
    )
    with pytest.raises(
        phase.ConformanceError, match="canonical unbulleted"
    ):
        phase.parse_dissent_dimensions(text)


def test_an_indented_comment_marker_is_code_not_a_comment():
    """CommonMark: four spaces STARTING a block makes it indented code.

    The lazy-continuation case, where the same indent follows a paragraph
    line and does form a comment, is the declared limit pinned above.
    """
    text = phase2_with_dissent_section([
        "    <!-- an indented example with no closer",
        "dimension_id: D1",
        "rationale: plan was inadequate",
    ])
    assert phase.parse_dissent_dimensions(text).dimensions == {"D1"}


def test_a_nested_paren_link_destination_is_a_declared_limit():
    """Documents an ACCEPTED miss, not a desired behaviour.

    Link destinations are unwrapped one nesting level deep. A deeper one
    leaves destination letters on the label, so the field reads as prose and
    is absorbed with the advisory diagnostic. Chasing it further is declined
    on the stated asymmetry: a miss costs one flagged record, while every
    broadening of the rule risks the false aborts this tolerance removes.
    Change this test deliberately, never incidentally.
    """
    for line in (
        "[dimension_id](https://e/x_(y_(z))w): D1",
        '<span title="x>y">dimension_id</span>: D1',
        "dimension_id&#58; D1",
    ):
        text = phase2_with_dissent_section([line])
        assert phase.parse_dissent_dimensions(text).dimensions == set()


def test_one_nesting_level_in_a_link_destination_still_aborts():
    text = phase2_with_dissent_section([
        "[dimension_id](https://e/x_(y)z): D1",
    ])
    with pytest.raises(
        phase.ConformanceError, match="canonical unbulleted"
    ):
        phase.parse_dissent_dimensions(text)


def test_the_diagnostic_counts_fenced_placeholder_prose():
    text = phase2_with_dissent_section([
        "```", "(omitted — the Phase 1 plan holds)", "```",
    ])
    diagnostic = phase.parse_dissent_dimensions(text).diagnostics[0]
    assert "0 non-blank line(s)" not in diagnostic


def test_a_fenced_block_elsewhere_leaves_the_dissent_section_alone():
    text = phase2_with_dissent_section(["*(omitted)*"]).replace(
        "## Review Body", "## Review Body\n\n```\ndimension_id: D1\n```", 1
    )
    parsed = phase.parse_dissent_dimensions(text)
    assert parsed.dimensions == set()
    assert len(parsed.diagnostics) == 1


def test_bulleted_multi_dissent_cannot_bypass_the_cardinality_gate():
    text = phase2_with_dissent_section([
        "- dimension_id: D1",
        "- rationale: first plan was inadequate",
        "- dimension_id: D3",
        "- rationale: second plan was inadequate",
    ])
    with pytest.raises(
        phase.ConformanceError, match="canonical unbulleted"
    ):
        phase.parse_dissent_dimensions(text)


@pytest.mark.parametrize("wrapper", [
    ("- dimension_id: D3", "- rationale: second plan was inadequate"),
    ("| dimension_id: D3 |", "| rationale: second plan was inadequate |"),
    ("- [ ] dimension_id: D3", "- [ ] rationale: second plan was inadequate"),
    ("[dimension_id](#d): D3", "[rationale](#d): second plan was inadequate"),
    ("[dimension_id](https://e.com): D3",
     "[rationale](https://e.com): second"),
])
def test_a_canonical_dissent_cannot_hide_a_second_decorated_one(wrapper):
    text = phase2_with_dissent_section([
        "dimension_id: D1",
        "rationale: plan was inadequate",
        *wrapper,
    ])
    with pytest.raises(
        phase.ConformanceError, match="canonical unbulleted"
    ):
        phase.parse_dissent_dimensions(text)


@pytest.mark.parametrize("prose", [
    "No dissent, so there is no dimension_id: line under this heading.",
    "I dissent from D1: the plan held after all, so nothing is claimed.",
    "Note: the Phase 1 plan holds.",
    "Dissent: none.",
    "無異議，dimension_id 已省略：Phase 1 計畫維持不變",
    "異議なし：dimension_id は省略しました。",
    "이견 없음: dimension_id 줄은 생략했습니다.",
])
def test_prose_carrying_a_colon_stays_tolerated(prose):
    parsed = phase.parse_dissent_dimensions(
        phase2_with_dissent_section([prose])
    )
    assert parsed.dimensions == set()
    assert len(parsed.diagnostics) == 1


def test_tolerated_empty_dissent_section_still_binds_every_trigger(tmp_path):
    args = write_cli_files(tmp_path, "methodology")
    phase2_path = Path(args[args.index("--phase2") + 1])
    text = phase2_with_dissent_section(
        ["*(omitted)*"], overrides={"D1": "block"}
    ).replace(
        'trigger: "block evidence pattern for D1"',
        'trigger: "novel post hoc trigger never committed in phase 1"',
        1,
    )
    phase2_path.write_text(text, encoding="utf-8")
    assert phase.main(args + ["--role", "methodology"]) == \
        phase.EXIT_CONFORMANCE


def test_cli_passes_and_prints_diagnostic_for_empty_dissent_section(
    tmp_path, capsys
):
    args = write_cli_files(tmp_path, "methodology")
    phase2_path = Path(args[args.index("--phase2") + 1])
    phase2_path.write_text(
        phase2_with_dissent_section([]), encoding="utf-8"
    )
    assert phase.main(args + ["--role", "methodology"]) == phase.EXIT_PASS
    assert "[DISSENT-EMPTY-SECTION:" in capsys.readouterr().out


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
        "### W1: incomplete absence\n**Severity**: Critical\n"
        "**Evidence Anchor**: absence: x",
        "### W1: missing expected item\n**Severity**: Critical\n"
        "**Evidence Anchor**: absence: Methods — expected ; checked appendix",
        "### W1: missing checked surfaces\n**Severity**: Critical\n"
        "**Evidence Anchor**: absence: Methods — expected ethics statement; checked",
        "### W1: missing literal separator space\n**Severity**: Critical\n"
        "**Evidence Anchor**: absence: Methods — expected ethics statement;checked appendix",
        "### W1: doubled separator space\n**Severity**: Critical\n"
        "**Evidence Anchor**: absence: Methods — expected ethics statement;  checked appendix",
        "### W1: repeated separators\n**Severity**: Critical\n"
        "**Evidence Anchor**: absence: Methods — expected ; checked appendix "
        "— expected ethics statement; checked supplement",
        "### W1: reversed separators\n**Severity**: Critical\n"
        "**Evidence Anchor**: absence: Methods; checked appendix — expected ethics statement",
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
        "**Evidence Anchor**: absence: Methods — expected an ethics statement; "
        "checked Methods, appendix, and supplement",
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
        "**Evidence Anchor**: absence: Methods — expected an ethics statement; "
        "checked Methods and appendix"
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


@pytest.mark.parametrize(
    "anchor",
    (
        '`text: §5 "short exact quote"`',
        '[`text: §5 "short exact quote"`]',
        '[text: §5 "short exact quote"]',
        "text: §5 “short exact quote”",
        "equation: Eq. [3]",
        "[equation: Eq. [3]]",
        'text: §5 "short exact quote" per `df`',
        '`text: §5 "short exact quote" per `df``',
        "text: §2 “the term “quality culture” is undefined”",
        'text: §2 "he said “quality culture” often"',
    ),
)
def test_whole_value_wrapped_template_anchor_is_normalised_and_accepted(anchor):
    body = (
        "### W1: template-shaped finding\n"
        "**Severity**: Critical\n"
        f"**Evidence Anchor**: {anchor}"
    )
    report, _ = parse_report("eic", body=body)
    phase.check_scoring_seat_anchors(report)


@pytest.mark.parametrize(
    "anchor",
    (
        '[`text`: §5 "short exact quote"]',
        '`text` — §5 "short exact quote"',
    ),
)
def test_type_only_wrapping_anchor_is_rejected(anchor):
    body = (
        "### W1: malformed type wrapping\n"
        "**Severity**: Critical\n"
        f"**Evidence Anchor**: {anchor}"
    )
    report, _ = parse_report("eic", body=body)
    with pytest.raises(phase.ConformanceError, match="ANCHOR-INVALID"):
        phase.check_scoring_seat_anchors(report)


@pytest.mark.parametrize(
    "anchor",
    (
        '`text: §5 "short exact quote"',
        'text: §5 "short exact quote"`',
        '[text: §5 "short exact quote"',
        'text: §5 "short exact quote"]',
        'text: §5 "short exact quote"`]',
        '[text: §5 "short exact quote"] trailing]',
        '[ text: §5 "short exact quote" ]',
        '[[text: §5 "short exact quote"]]',
        '``text: §5 "short exact quote"``',
        '` text: §5 "short exact quote" `',
        '[`text: §5 "short exact quote"]',
        '[text: §5 "short exact quote"`]',
        "equation: Eq. ]3[",
    ),
)
def test_unpaired_or_repeated_whole_value_wrappers_are_rejected(anchor):
    body = (
        "### W1: malformed whole-value wrapper\n"
        "**Severity**: Critical\n"
        f"**Evidence Anchor**: {anchor}"
    )
    report, _ = parse_report("eic", body=body)
    with pytest.raises(phase.ConformanceError, match="ANCHOR-INVALID"):
        phase.check_scoring_seat_anchors(report)


@pytest.mark.parametrize(
    "anchor",
    (
        'text: §5 "short exact quote”',
        'text: §5 “short exact quote"',
        'text: §5 "outer “inner”',
        'text: §5 “outer "inner”"',
    ),
)
def test_hybrid_double_quote_pairs_are_rejected(anchor):
    body = (
        "### W1: mismatched quote pair\n"
        "**Severity**: Critical\n"
        f"**Evidence Anchor**: {anchor}"
    )
    report, _ = parse_report("eic", body=body)
    with pytest.raises(phase.ConformanceError, match="ANCHOR-INVALID"):
        phase.check_scoring_seat_anchors(report)


def test_combined_template_fields_are_parsed():
    body = (
        "### W1: combined fields\n"
        "  - **Severity**: Major | **Evidence Anchor**: "
        "`absence: Methods — expected an ethics statement; "
        "checked Methods and appendix` | "
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
    with pytest.raises(phase.ConformanceError, match="HTML comments are forbidden"):
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


def test_da_pre_table_prose_passes_phase_checker():
    report = panel.parse_report(
        "da.md",
        da_text(
            major_rows=('| M1 | Issue | text: "short quote" |',)
        ).replace(
            "#### CRITICAL",
            "Ordinary adversarial commentary precedes the terminal tables.\n\n"
            "#### CRITICAL",
            1,
        ),
        FULL,
    )
    phase.check_da_anchors(report)


def test_da_bare_comment_closer_passes_phase_checker():
    text = da_text(ids=("C1",)).replace(
        "#### CRITICAL",
        "The reported N moves 41 --> 38 without explanation.\n\n"
        "#### CRITICAL",
        1,
    ).replace(
        'text: "quote" p. 1',
        'text: "N moves 41 --> 38" p. 1',
        1,
    )
    report = panel.parse_report("da.md", text, FULL)
    phase.check_da_anchors(report)


def test_da_post_critical_table_prose_fails_phase_checker():
    text = da_text(ids=()).replace(
        "\n\n#### MAJOR",
        "\n\n*None. Ordinary adversarial commentary.*\n\n#### MAJOR",
        1,
    )
    report = panel.parse_report("da.md", text, FULL)
    with pytest.raises(
        (panel.ReportError, phase.panel.ReportError, phase.ConformanceError),
        match="issue tables are terminal",
    ):
        phase.check_da_anchors(report)


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
def test_da_post_boundary_table_surfaces_fail_phase_checker(
    late_surface,
):
    text = da_text(ids=("C1",)).replace(
        "\n\n#### MAJOR",
        f"\n\n{late_surface}\n\n#### MAJOR",
        1,
    )
    report = panel.parse_report("da.md", text, FULL)
    with pytest.raises(
        (panel.ReportError, phase.panel.ReportError, phase.ConformanceError),
        match="issue tables are terminal",
    ):
        phase.check_da_anchors(report)


@pytest.mark.parametrize("late_surface", _DA_TERMINAL_LATE_SURFACES)
def test_da_post_major_table_surfaces_fail_phase_checker(
    late_surface,
):
    report = panel.parse_report(
        "da.md", da_text(ids=("C1",)) + f"\n\n{late_surface}", FULL
    )
    with pytest.raises(
        (panel.ReportError, phase.panel.ReportError, phase.ConformanceError),
        match="issue tables are terminal",
    ):
        phase.check_da_anchors(report)


def test_da_fenced_payload_after_major_fails_phase_checker():
    text = da_text(ids=("C1",)) + (
        "\n\n```markdown\n"
        '| C2 | Hidden critical issue | text: "hidden evidence" p. 2 |\n'
        "```"
    )
    report = panel.parse_report("da.md", text, FULL)
    with pytest.raises(
        (panel.ReportError, phase.panel.ReportError, phase.ConformanceError),
        match="issue tables are terminal",
    ):
        phase.check_da_anchors(report)


def test_da_html_comment_inside_fence_fails_phase_checker():
    text = da_text(ids=()) + (
        "\n\n```\n<!-- hidden adjudication payload -->\n```"
    )
    report = panel.parse_report("da.md", text, FULL)
    with pytest.raises(
        (panel.ReportError, phase.panel.ReportError, phase.ConformanceError),
        match="HTML comments are forbidden",
    ):
        phase.check_da_anchors(report)


def test_da_html_commented_tables_fail_phase_checker():
    text = da_text(ids=()).replace(
        "#### CRITICAL", "<!--\n#### CRITICAL", 1
    )
    text += "\n-->"
    report = panel.parse_report("da.md", text, FULL)
    with pytest.raises(
        (panel.ReportError, phase.panel.ReportError, phase.ConformanceError),
        match="HTML comments are forbidden",
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
