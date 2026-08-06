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
    # One paragraph per contract dimension: §4 reads
    # `paraphrase_minimum_dimensions` ("all" in the full contract), and
    # the real dispatch outputs carry exactly this shape, so a fixture
    # with fewer paragraphs would stop being a valid Phase 1 at all.
    lines = ["## Contract Paraphrase", ""]
    for dim in FULL["acceptance_dimensions"]:
        lines += [f"{dim['id']} concerns {dim['name']} as the contract "
                  "defines it.", ""]
    lines += ["## Scoring Plan", ""]
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


def phase2_text(
    role: str, overrides=None, body="", dissent=(), receipts=None
) -> str:
    """Build a Phase 2 card; a methodology card carries its #610 receipt
    section (default: the no-recomputable-statistics attestation), because a
    methodology card without one stopped being conformant when the receipt
    gate landed. Pass a list of section lines via ``receipts`` to override.
    """
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
    if role == "methodology":
        if receipts is None:
            receipts = [
                "no_recomputable_statistics: the fixture manuscript reports "
                "no statistic covered by a bounded procedure",
            ]
        lines += ["", "## Arithmetic Receipts", "", *receipts]
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
    """Unchanged by #637: a mid-line second declaration is a declaration
    (`_SEVERITY_DECL_RE`) whose value cannot parse mid-prose, so the
    declared-but-unparseable guard still aborts. Only cross-line
    supersession takes last-wins."""
    body = (
        "### W1: hidden critical\n"
        "**Severity**: Minor and **Severity**: Critical"
    )
    report, _ = parse_report("eic", body=body)
    with pytest.raises(phase.ConformanceError, match="FINDING-GRAMMAR"):
        phase.check_scoring_seat_anchors(report)


def test_same_line_pipe_separated_severity_pair_fails():
    """`_SEVERITY_RE` also parses after a table-cell pipe, so both halves
    of `Minor | Critical` on ONE line are parseable — but two parseable
    declarations on one line are not a reading-order self-correction and
    must not enter the supersession path (which could otherwise waive the
    anchor requirement via `Critical | Minor`)."""
    for pair in ("Minor | **Severity**: Critical",
                 "Critical | **Severity**: Minor"):
        body = (
            "### W1: table smuggle\n"
            f"**Severity**: {pair}"
        )
        report, _ = parse_report("eic", body=body)
        with pytest.raises(
            phase.ConformanceError, match="exactly one parseable Severity"
        ):
            phase.check_scoring_seat_anchors(report)


def test_cross_line_severity_supersession_takes_last(capsys):
    """#637 ms01_quant baseline r1: the domain seat declared Major, then
    self-corrected to Critical with explicit supersession prose. The card
    passes with the last value operative and the trail in the gate log."""
    body = (
        "### W1: construct mismatch\n"
        "**Severity**: Major\n"
        "Correction: recording this as Critical; the Severity line below "
        "supersedes the line above.\n"
        "**Severity**: Critical\n"
        '**Evidence Anchor**: text: "quote" p. 1'
    )
    report, _ = parse_report("eic", body=body)
    phase.check_scoring_seat_anchors(report)
    assert (
        "[SEVERITY-SUPERSEDED: p2.md: W1: construct mismatch: "
        "Major -> Critical]"
    ) in capsys.readouterr().out


def test_unparseable_severity_declaration_still_fails():
    body = (
        "### W1: bad value\n"
        "**Severity**: High"
    )
    report, _ = parse_report("eic", body=body)
    with pytest.raises(
        phase.ConformanceError, match="exactly one parseable Severity"
    ):
        phase.check_scoring_seat_anchors(report)


def test_revisited_severity_value_still_fails():
    """A chain that revisits a value (Minor -> Major -> Minor) is not a
    supersession — a non-escalating chain keeps the anti-bundling abort."""
    body = (
        "### W1: bundled pair\n"
        "**Severity**: Minor\n"
        "first\n"
        "**Severity**: Major\n"
        "second\n"
        "**Severity**: Minor"
    )
    report, _ = parse_report("eic", body=body)
    with pytest.raises(
        phase.ConformanceError, match="strictly escalating"
    ):
        phase.check_scoring_seat_anchors(report)


def test_deescalating_severity_pair_still_fails():
    """Critical -> Minor must abort: last-wins de-escalation would waive
    the Critical Evidence-Anchor hard gate with one appended line. Only
    the observed self-correction direction (escalation) is tolerated."""
    body = (
        "### W1: fabricated denominators\n"
        "**Severity**: Critical\n"
        "The paper invents denominators.\n"
        "**Severity**: Minor"
    )
    report, _ = parse_report("eic", body=body)
    with pytest.raises(
        phase.ConformanceError, match="strictly escalating"
    ):
        phase.check_scoring_seat_anchors(report)


def test_distinct_severity_bundle_still_fails():
    """Three findings bundled under one W heading with distinct descending
    severities are not a supersession chain and keep the loud abort."""
    body = (
        "### W1: bundled triple\n"
        "**Severity**: Critical\n"
        "first\n"
        "**Severity**: Major\n"
        "second\n"
        "**Severity**: Minor"
    )
    report, _ = parse_report("eic", body=body)
    with pytest.raises(
        phase.ConformanceError, match="strictly escalating"
    ):
        phase.check_scoring_seat_anchors(report)


def test_escalating_supersession_operative_value_needs_anchor():
    """Minor -> Major with NO anchor must abort at ANCHOR-MISSING: the
    LAST value (Major) is operative. Pins last-wins — if the first value
    (Minor) were operative the card would take the no-anchor branch and
    pass."""
    body = (
        "### W1: upgraded finding\n"
        "**Severity**: Minor\n"
        "on reflection this forecloses the design claim\n"
        "**Severity**: Major"
    )
    report, _ = parse_report("eic", body=body)
    with pytest.raises(phase.ConformanceError, match="ANCHOR-MISSING"):
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


def phase1_only_args(tmp_path: Path, role: str) -> list[str]:
    """CLI arguments for the gate that runs before Phase 2 exists."""
    args = write_cli_files(tmp_path, role)
    del args[args.index("--phase2"):args.index("--phase2") + 2]
    return args + ["--phase1-only", "--role", role]


def test_phase1_only_cli_passes_before_phase2_exists(tmp_path, capsys):
    """The dispatch harness needs a verdict on Phase 1 alone.

    A retry decision is taken while Phase 2 has not been requested yet, so
    requiring `--phase2` forced the harness to invent one or to reimplement
    the gate, and a reimplemented gate is not the checker's own output.
    """
    assert phase.main(phase1_only_args(tmp_path, "methodology")) == \
        phase.EXIT_PASS
    assert "PHASE1-CONFORMANCE: PASS" in capsys.readouterr().out


def test_phase1_only_cli_rejects_a_malformed_plan(tmp_path, capsys):
    args = phase1_only_args(tmp_path, "methodology")
    phase1_path = Path(args[args.index("--phase1") + 1])
    phase1_path.write_text(
        phase1_text("methodology").replace(
            "what_triggers_fatal: fatal evidence pattern for D3", "", 1
        ),
        encoding="utf-8",
    )
    assert phase.main(args) == phase.EXIT_CONFORMANCE
    assert "[PHASE1-GRAMMAR:" in capsys.readouterr().out


def test_phase1_only_cli_still_checks_manuscript_blindness(tmp_path, capsys):
    args = phase1_only_args(tmp_path, "methodology")
    phase1_path = Path(args[args.index("--phase1") + 1])
    manuscript = Path(args[args.index("--manuscript") + 1])
    leak = " ".join(f"leaked{index}" for index in range(14))
    manuscript.write_text(leak, encoding="utf-8")
    phase1_path.write_text(
        phase1_text("methodology") + "\n" + leak + "\n", encoding="utf-8"
    )
    assert phase.main(args) == phase.EXIT_CONFORMANCE
    assert "LEAK" in capsys.readouterr().out


def test_phase1_only_and_phase2_are_mutually_exclusive(tmp_path):
    args = write_cli_files(tmp_path, "methodology")
    with pytest.raises(SystemExit):
        phase.main(args + ["--role", "methodology", "--phase1-only"])


def test_one_of_phase1_only_or_phase2_is_required(tmp_path):
    args = write_cli_files(tmp_path, "methodology")
    del args[args.index("--phase2"):args.index("--phase2") + 2]
    with pytest.raises(SystemExit):
        phase.main(args + ["--role", "methodology"])


def test_multi_dissent_emits_its_machine_token_on_the_violation_line(
    tmp_path, capsys
):
    """Pinned as an interface, not prose.

    The dispatch harness routes §5's one permitted Phase 2 retry on this exact
    token, matched inside this exact line prefix. A reword must fail here
    rather than silently turn a permitted retry into an aborted fleet.
    """
    args = write_cli_files(tmp_path, "methodology")
    Path(args[args.index("--phase2") + 1]).write_text(
        phase2_with_dissent_section([
            "dimension_id: D1",
            "rationale: the plan understated the risk here",
            "dimension_id: D3",
            "rationale: the plan understated a second risk here",
        ]),
        encoding="utf-8",
    )
    assert phase.main(args + ["--role", "methodology"]) == \
        phase.EXIT_CONFORMANCE
    violations = [
        line for line in capsys.readouterr().out.splitlines()
        if line.lstrip().startswith("[PROTOCOL-VIOLATION:")
    ]
    assert len(violations) == 1, violations
    assert "multi_dissent=true" in violations[0]


def test_phase1_requires_the_paraphrase_section():
    """§4 names three requirements; a valid plan alone must not pass."""
    text = re.sub(r"## Contract Paraphrase.*?(?=## Scoring Plan)", "",
                  phase1_text("methodology"), flags=re.S)
    with pytest.raises(phase.ConformanceError,
                       match="Contract Paraphrase"):
        phase.parse_phase1("p1.md", text, FULL, "methodology")


def test_phase1_requires_the_terminal_acknowledgement():
    text = phase1_text("methodology").replace(
        "[CONTRACT-ACKNOWLEDGED]", "").rstrip() + "\n"
    with pytest.raises(phase.ConformanceError,
                       match="CONTRACT-ACKNOWLEDGED"):
        phase.parse_phase1("p1.md", text, FULL, "methodology")


def test_phase1_requires_the_paraphrase_paragraph_floor():
    """A bare heading over one line is not the paraphrase the contract's
    `paraphrase_minimum_dimensions` names; the count is the
    machine-checkable lower bound (real dispatch outputs carry exactly
    one paragraph per dimension).
    """
    text = re.sub(
        r"## Contract Paraphrase.*?(?=## Scoring Plan)",
        "## Contract Paraphrase\n\nAll dimensions understood.\n\n",
        phase1_text("methodology"), flags=re.S)
    with pytest.raises(phase.ConformanceError, match="fewer than"):
        phase.parse_phase1("p1.md", text, FULL, "methodology")


def test_phase1_requires_the_exact_h2_sequence():
    """§4: exactly `## Contract Paraphrase` then `## Scoring Plan`, in
    that order and nothing else at H2 -- presence alone let a reordered
    or extra-sectioned precommitment pass. All four real dispatch
    outputs carry exactly this sequence.
    """
    good = phase1_text("methodology")
    reordered = good.replace("## Contract Paraphrase", "## ZZZ", 1)
    reordered = reordered.replace("## Scoring Plan",
                                  "## Contract Paraphrase", 1)
    reordered = reordered.replace("## ZZZ", "## Scoring Plan", 1)
    with pytest.raises(phase.ConformanceError, match="H2 sections"):
        phase.parse_phase1("p1.md", reordered, FULL, "methodology")
    extra = good.replace("## Scoring Plan",
                         "## Reviewer Notes\n\nan extra section\n\n"
                         "## Scoring Plan", 1)
    with pytest.raises(phase.ConformanceError, match="H2 sections"):
        phase.parse_phase1("p1.md", extra, FULL, "methodology")


def test_phase1_heading_only_paraphrase_fails_the_paragraph_floor():
    """codex r41: six bare `### Dn` headings separated by blank lines
    counted as six paragraphs, so a precommitment with no paraphrase
    prose at all satisfied the floor. A heading is a heading, not a
    paragraph, and it separates paragraphs rather than joining them.
    """
    headings = "\n\n".join(
        f"### {dim['id']}" for dim in FULL["acceptance_dimensions"])
    text = re.sub(
        r"## Contract Paraphrase.*?(?=## Scoring Plan)",
        f"## Contract Paraphrase\n\n{headings}\n\n",
        phase1_text("methodology"), flags=re.S)
    with pytest.raises(phase.ConformanceError, match="fewer than"):
        phase.parse_phase1("p1.md", text, FULL, "methodology")


def test_phase1_headings_do_not_join_two_prose_paragraphs():
    """A heading between two prose lines separates them; treating it as
    transparent would count `prose / ### H / prose` as one paragraph
    and undercount, while counting it as prose overcounts.
    """
    dims = FULL["acceptance_dimensions"]
    body = "\n\n".join(
        f"### {dim['id']}\n{dim['id']} concerns {dim['name']} as the "
        "contract defines it." for dim in dims)
    text = re.sub(
        r"## Contract Paraphrase.*?(?=## Scoring Plan)",
        f"## Contract Paraphrase\n\n{body}\n\n",
        phase1_text("methodology"), flags=re.S)
    parsed = phase.parse_phase1("p1.md", text, FULL, "methodology")
    assert parsed is not None


def test_phase1_zero_content_blocks_do_not_satisfy_the_floor():
    """codex r42: six `---` thematic breaks (or six single-line HTML
    comments) counted as six paragraphs. Zero-content lines separate;
    they never count.
    """
    for filler in ("---", "- - -", "***", "<!-- noted -->"):
        blocks = "\n\n".join([filler] * len(FULL["acceptance_dimensions"]))
        text = re.sub(
            r"## Contract Paraphrase.*?(?=## Scoring Plan)",
            f"## Contract Paraphrase\n\n{blocks}\n\n",
            phase1_text("methodology"), flags=re.S)
        with pytest.raises(phase.ConformanceError, match="fewer than"):
            phase.parse_phase1("p1.md", text, FULL, "methodology")


def test_phase1_a_bulleted_paraphrase_still_counts_as_content():
    """The zero-content list is CLOSED: a bulleted six-point paraphrase
    is real content, and refusing it would abort a panel over
    formatting -- the false-abort channel #609 exists to remove. A
    dash-led bullet must not be confused with a `---` thematic break.
    """
    dims = FULL["acceptance_dimensions"]
    bullets = "\n\n".join(
        f"- {dim['id']} concerns {dim['name']} as the contract defines "
        "it." for dim in dims)
    text = re.sub(
        r"## Contract Paraphrase.*?(?=## Scoring Plan)",
        f"## Contract Paraphrase\n\n{bullets}\n\n",
        phase1_text("methodology"), flags=re.S)
    parsed = phase.parse_phase1("p1.md", text, FULL, "methodology")
    assert parsed is not None


def test_phase1_multiline_html_comments_do_not_satisfy_the_floor():
    """codex r43: only same-line comments matched the separator, so six
    multi-line `<!-- ... -->` blocks counted as six paragraphs -- an
    entirely hidden §4 with no rendered paraphrase at all.
    """
    block = "<!--\nhidden not-a-paraphrase\n-->"
    blocks = "\n\n".join([block] * len(FULL["acceptance_dimensions"]))
    text = re.sub(
        r"## Contract Paraphrase.*?(?=## Scoring Plan)",
        f"## Contract Paraphrase\n\n{blocks}\n\n",
        phase1_text("methodology"), flags=re.S)
    with pytest.raises(phase.ConformanceError, match="fewer than"):
        phase.parse_phase1("p1.md", text, FULL, "methodology")


def test_phase1_prose_mentioning_a_comment_opener_still_counts():
    """The comment-state entry is conservative: a paragraph that merely
    mentions `<!--` mid-line (or contains a closed comment) must not be
    swallowed as hidden.
    """
    dims = FULL["acceptance_dimensions"]
    body = "\n\n".join(
        f"{dim['id']} concerns {dim['name']}; authors sometimes hide "
        "text with <!-- markers --> in drafts." for dim in dims)
    text = re.sub(
        r"## Contract Paraphrase.*?(?=## Scoring Plan)",
        f"## Contract Paraphrase\n\n{body}\n\n",
        phase1_text("methodology"), flags=re.S)
    parsed = phase.parse_phase1("p1.md", text, FULL, "methodology")
    assert parsed is not None


def test_phase1_lone_list_markers_do_not_satisfy_the_floor():
    """codex r46: six lone `-` (or `*`, `+`) list markers are empty
    Markdown constructs, each counted as a paragraph. A bare marker
    joins the closed separator list; a marker WITH text still counts.
    """
    for marker in ("-", "*", "+"):
        blocks = "\n\n".join([marker] * len(FULL["acceptance_dimensions"]))
        text = re.sub(
            r"## Contract Paraphrase.*?(?=## Scoring Plan)",
            f"## Contract Paraphrase\n\n{blocks}\n\n",
            phase1_text("methodology"), flags=re.S)
        with pytest.raises(phase.ConformanceError, match="fewer than"):
            phase.parse_phase1("p1.md", text, FULL, "methodology")


# --- #610 methodology arithmetic-receipt gate ----------------------------


W1_BACKREF_BODY = (
    "### W1: reported mean is unreachable\n"
    "**Severity**: Critical\n"
    "**Evidence Anchor**: table: Table 2, M=3.847 with N=87\n"
    "**Confidence**: 5 — quantitative methods reviewer\n"
    "**Arithmetic Receipt**: AR1\n"
)


def grim_receipt(**overrides) -> list[str]:
    fields = {
        "procedure_id": "grim",
        "evidence_anchor": "table: Table 2, M=3.847 with N=87",
        "reported_inputs": "single 1-5 integer item, N=87, M=3.847, "
                           "three-decimal precision",
        "assumptions": "unweighted single-item mean as stated in §3.2",
        "derivation": "integer sums 334 and 335 bracket 87 * 3.847",
        "derived_value_or_range": "334/87 = 3.8390...; 335/87 = 3.8505...",
        "comparison_rule": "an achievable sum must round to 3.847 at three "
                           "decimals",
        "rounding_interval": "[3.8465, 3.8475)",
        "nearest_achievable": "334/87 = 3.8390...; 335/87 = 3.8505...",
        "status": "mismatch",
        "finding_ref": "W1",
    }
    fields.update(overrides)
    return [f"{key}: {value}" for key, value in fields.items()
            if value is not None]


def p_receipt(**overrides) -> list[str]:
    fields = {
        "procedure_id": "p_from_test_statistic",
        "evidence_anchor": 'text: §4.1 "t(140) = 1.31, p = .008"',
        "reported_inputs": "independent t, t=1.31, df=140, p=.008, no tail "
                           "stated",
        "assumptions": "central t distribution; no paper-licensed tail",
        "tail_convention": "unstated",
        "derivation": "p from t=1.31 at df=140 under both tail readings",
        "derived_value_or_range": "two-tailed p ≈ .192; one-tailed p ≈ .096",
        "comparison_rule": "reported .008 must match either tail value at "
                           "reported precision",
        "status": "mismatch",
        "finding_ref": "W1",
    }
    fields.update(overrides)
    return [f"{key}: {value}" for key, value in fields.items()
            if value is not None]


def n_from_df_receipt(**overrides) -> list[str]:
    fields = {
        "procedure_id": "n_from_df",
        "evidence_anchor": 'text: §4.2 "t(156)" against the stated maximum '
                           'analytic sample',
        "reported_inputs": "independent-groups t with df=156; stated maximum "
                           "analytic N=142",
        "assumptions": "equal-variance independent t as the paper names",
        "df_identity": "df = N1 + N2 - 2",
        "derivation": "df=156 requires total N=158 under the named identity",
        "derived_value_or_range": "required N = 158",
        "comparison_rule": "required N must not exceed the stated analytic "
                           "ceiling of 142",
        "status": "mismatch",
        "finding_ref": "W1",
    }
    fields.update(overrides)
    return [f"{key}: {value}" for key, value in fields.items()
            if value is not None]


def receipt_section(*receipts: list[str]) -> list[str]:
    lines: list[str] = []
    for index, fields in enumerate(receipts, start=1):
        lines += [f"### AR{index}", *fields, ""]
    return lines


def methodology_report(receipts=None, body=W1_BACKREF_BODY):
    text = phase2_text("methodology", body=body, receipts=receipts)
    return panel.parse_report("p2.md", text, FULL)


def check_receipts(receipts=None, body=W1_BACKREF_BODY):
    phase.check_methodology_receipts(methodology_report(receipts, body))


def test_receipt_attestation_card_passes():
    check_receipts(receipts=None, body="prose review body without findings")


def test_valid_grim_mismatch_receipt_passes():
    check_receipts(receipt_section(grim_receipt()))


def test_valid_p_unstated_both_tails_receipt_passes():
    check_receipts(receipt_section(p_receipt()))


def test_valid_n_from_df_receipt_passes():
    check_receipts(receipt_section(n_from_df_receipt()))


def test_valid_consistent_receipt_needs_no_finding():
    check_receipts(
        receipt_section(
            grim_receipt(status="consistent", finding_ref=None)
        ),
        body="prose only",
    )


def test_valid_not_computable_receipt_passes():
    check_receipts(
        receipt_section(p_receipt(
            status="not_computable",
            not_computable_reason="tail_ambiguous",
            finding_ref=None,
            derived_value_or_range="not derived; tail choice flips the "
                                   "verdict",
        )),
        body="prose only",
    )


def test_receipt_lines_tolerate_bold_and_list_decoration():
    decorated = [
        line if ":" not in line else "- **" + line.replace(": ", "**: ", 1)
        for line in grim_receipt()
    ]
    check_receipts(receipt_section(decorated))


def test_missing_receipt_section_fails():
    text = phase2_text("methodology", body=W1_BACKREF_BODY)
    text = text[: text.index("\n## Arithmetic Receipts")]
    report = panel.parse_report("p2.md", text, FULL)
    with pytest.raises(phase.ConformanceError, match=r"RECEIPT-MISSING"):
        phase.check_methodology_receipts(report)


def test_duplicate_receipt_section_fails():
    text = phase2_text("methodology", body="prose") + \
        "\n\n## Arithmetic Receipts\n\nno_recomputable_statistics: twice\n"
    report = panel.parse_report("p2.md", text, FULL)
    with pytest.raises(phase.ConformanceError, match="duplicate"):
        phase.check_methodology_receipts(report)


def test_receipt_section_before_review_body_fails():
    text = phase2_text("methodology", body="prose", receipts=())
    text = text[: text.index("\n## Arithmetic Receipts")]
    text = text.replace(
        "## Review Body",
        "## Arithmetic Receipts\n\nno_recomputable_statistics: early\n\n"
        "## Review Body",
        1,
    )
    report = panel.parse_report("p2.md", text, FULL)
    with pytest.raises(
        phase.ConformanceError, match="must be the final section"
    ):
        phase.check_methodology_receipts(report)


def test_empty_receipt_section_without_attestation_fails():
    with pytest.raises(phase.ConformanceError, match="exactly one"):
        check_receipts(receipts=(), body="prose")


def test_attestation_alongside_receipts_fails():
    lines = receipt_section(grim_receipt())
    lines.append("no_recomputable_statistics: but also receipts")
    with pytest.raises(phase.ConformanceError, match="forbidden when"):
        check_receipts(lines)


def test_non_dense_receipt_ids_fail():
    lines = ["### AR2", *grim_receipt(), ""]
    with pytest.raises(phase.ConformanceError, match="dense"):
        check_receipts(lines)


def test_invalid_receipt_heading_fails():
    lines = ["### AR0", *grim_receipt(), ""]
    with pytest.raises(phase.ConformanceError, match="invalid receipt"):
        check_receipts(lines)


def test_duplicate_receipt_heading_fails():
    lines = [
        "### AR1", *grim_receipt(), "",
        "### AR1", *grim_receipt(), "",
    ]
    with pytest.raises(phase.ConformanceError, match="duplicate receipt"):
        check_receipts(lines)


def test_unknown_procedure_id_fails():
    with pytest.raises(
        phase.ConformanceError, match="not a bounded procedure"
    ):
        check_receipts(
            receipt_section(grim_receipt(procedure_id="effect_size_check"))
        )


@pytest.mark.parametrize("key", [
    "procedure_id", "evidence_anchor", "reported_inputs", "assumptions",
    "derivation", "derived_value_or_range", "comparison_rule", "status",
])
def test_each_missing_canonical_receipt_field_fails(key):
    with pytest.raises(phase.ConformanceError, match="RECEIPT-GRAMMAR"):
        check_receipts(receipt_section(grim_receipt(**{key: None})))


def test_duplicated_receipt_field_fails():
    lines = receipt_section(grim_receipt())
    lines.insert(2, "status: consistent")
    with pytest.raises(phase.ConformanceError, match="found 2"):
        check_receipts(lines)


def test_unknown_status_fails():
    with pytest.raises(phase.ConformanceError, match="closed status enum"):
        check_receipts(
            receipt_section(grim_receipt(status="plausible"))
        )


def test_not_computable_without_reason_fails():
    with pytest.raises(phase.ConformanceError, match="not_computable_reason"):
        check_receipts(
            receipt_section(grim_receipt(
                status="not_computable", finding_ref=None
            )),
            body="prose",
        )


def test_reason_on_verdict_status_fails():
    with pytest.raises(phase.ConformanceError, match="forbidden unless"):
        check_receipts(
            receipt_section(grim_receipt(
                not_computable_reason="rounding_rule_ambiguous"
            ))
        )


def test_unknown_not_computable_reason_fails():
    with pytest.raises(phase.ConformanceError, match="closed v1 enum"):
        check_receipts(
            receipt_section(grim_receipt(
                status="not_computable",
                not_computable_reason="model_was_unsure",
                finding_ref=None,
            )),
            body="prose",
        )


def test_p_receipt_without_tail_convention_fails():
    with pytest.raises(phase.ConformanceError, match="tail_convention"):
        check_receipts(receipt_section(p_receipt(tail_convention=None)))


def test_tail_convention_on_grim_is_forbidden():
    with pytest.raises(phase.ConformanceError, match="forbidden for"):
        check_receipts(
            receipt_section(grim_receipt(tail_convention="two-tailed"))
        )


def test_unknown_tail_convention_fails():
    with pytest.raises(phase.ConformanceError, match="closed enum"):
        check_receipts(
            receipt_section(p_receipt(tail_convention="lower-tail"))
        )


@pytest.mark.parametrize("derived", [
    "two-tailed p ≈ .192 only",
    "one-tailed p ≈ .096 only",
    "p ≈ .192 under the default reading",
])
def test_unstated_tail_verdict_must_show_both_tails(derived):
    with pytest.raises(phase.ConformanceError, match="RECEIPT-TAILS"):
        check_receipts(
            receipt_section(p_receipt(derived_value_or_range=derived))
        )


def test_stated_tail_needs_no_both_tail_display():
    check_receipts(
        receipt_section(p_receipt(
            tail_convention="two-tailed",
            reported_inputs="paired t, t=1.31, df=140, p=.008, two-tailed "
                            "stated in §4.1",
            derived_value_or_range="two-tailed p ≈ .192",
        ))
    )


@pytest.mark.parametrize("key", ["rounding_interval", "nearest_achievable"])
def test_grim_verdict_without_reachability_fields_fails(key):
    with pytest.raises(phase.ConformanceError, match=key):
        check_receipts(receipt_section(grim_receipt(**{key: None})))


def test_grim_not_computable_may_omit_reachability_fields():
    check_receipts(
        receipt_section(grim_receipt(
            status="not_computable",
            not_computable_reason="scale_granularity_unknown",
            rounding_interval=None,
            nearest_achievable=None,
            finding_ref=None,
        )),
        body="prose",
    )


def test_rounding_interval_on_p_procedure_is_forbidden():
    with pytest.raises(phase.ConformanceError, match="forbidden for"):
        check_receipts(
            receipt_section(p_receipt(rounding_interval="[.0075, .0085)"))
        )


def test_n_from_df_verdict_without_identity_fails():
    with pytest.raises(phase.ConformanceError, match="df_identity"):
        check_receipts(receipt_section(n_from_df_receipt(df_identity=None)))


def test_df_identity_on_grim_is_forbidden():
    with pytest.raises(phase.ConformanceError, match="forbidden for"):
        check_receipts(
            receipt_section(grim_receipt(df_identity="df = N - 1"))
        )


def test_invalid_receipt_anchor_fails():
    with pytest.raises(phase.ConformanceError):
        check_receipts(
            receipt_section(grim_receipt(evidence_anchor="somewhere in §4"))
        )


def test_mismatch_without_finding_ref_fails():
    with pytest.raises(phase.ConformanceError, match="finding_ref"):
        check_receipts(receipt_section(grim_receipt(finding_ref=None)))


def test_finding_ref_on_consistent_receipt_fails():
    with pytest.raises(phase.ConformanceError, match="RECEIPT-LINKAGE"):
        check_receipts(
            receipt_section(grim_receipt(status="consistent"))
        )


def test_malformed_finding_ref_fails():
    with pytest.raises(phase.ConformanceError, match="must name one W<n>"):
        check_receipts(receipt_section(grim_receipt(finding_ref="C1")))


def test_finding_ref_to_absent_weakness_fails():
    with pytest.raises(phase.ConformanceError, match="no matching"):
        check_receipts(receipt_section(grim_receipt(finding_ref="W9")))


def test_two_receipts_sharing_a_finding_ref_fail():
    with pytest.raises(phase.ConformanceError, match="share a finding_ref"):
        check_receipts(
            receipt_section(grim_receipt(), n_from_df_receipt())
        )


def test_mismatch_weakness_without_backref_fails():
    body = W1_BACKREF_BODY.replace("**Arithmetic Receipt**: AR1\n", "")
    with pytest.raises(phase.ConformanceError, match="back-reference"):
        check_receipts(receipt_section(grim_receipt()), body=body)


def test_backref_naming_wrong_receipt_fails():
    body = W1_BACKREF_BODY.replace(
        "**Arithmetic Receipt**: AR1", "**Arithmetic Receipt**: AR2"
    )
    with pytest.raises(phase.ConformanceError, match="RECEIPT-LINKAGE"):
        check_receipts(receipt_section(grim_receipt()), body=body)


def test_stale_backref_without_mismatch_receipt_fails():
    with pytest.raises(
        phase.ConformanceError, match="does not correspond"
    ):
        check_receipts(
            receipt_section(
                grim_receipt(status="consistent", finding_ref=None)
            ),
            body=W1_BACKREF_BODY,
        )


def test_fenced_receipt_content_is_read_not_dropped():
    # #610 round-1 fix 3, false-abort direction (#637 family): a model that
    # fences its receipt block still wrote the receipts, so the section is
    # read fence-transparently and a well-formed fenced block passes.
    lines = ["```", *receipt_section(grim_receipt()), "```"]
    check_receipts(lines)


def test_fenced_receipts_beside_unfenced_attestation_abort():
    # #610 round-1 fix 3, hiding direction: a fenced AR block cannot vanish
    # and launder the section into an attestation-only card.
    lines = [
        "no_recomputable_statistics: nothing recomputable here",
        "",
        "```",
        *receipt_section(grim_receipt()),
        "```",
    ]
    with pytest.raises(phase.ConformanceError, match="forbidden when"):
        check_receipts(lines)


def test_fenced_malformed_receipt_still_fails_its_field_counts():
    lines = ["```", *receipt_section(grim_receipt(status=None)), "```"]
    with pytest.raises(phase.ConformanceError, match="exactly one"):
        check_receipts(lines)


def test_fenced_h2_inside_receipt_section_does_not_delimit():
    lines = receipt_section(grim_receipt()) + [
        "```",
        "## Not A Real Section",
        "```",
    ]
    check_receipts(lines)


def test_receipt_section_must_be_the_final_h2():
    # #610 round-1 fix 6: the prompt says "final section"; the checker
    # enforces exactly that, not merely "after Review Body".
    text = phase2_text(
        "methodology",
        body=W1_BACKREF_BODY,
        receipts=receipt_section(grim_receipt()),
    ) + "\n\n## Trailing Notes\n\nnothing\n"
    report = panel.parse_report("p2.md", text, FULL)
    with pytest.raises(
        phase.ConformanceError, match="must be the final section"
    ):
        phase.check_methodology_receipts(report)


@pytest.mark.parametrize("derived", [
    "two-tailed; one-tailed p ≈ .096",
    "two-tailed p ≈ .192; one-tailed",
    "two-tailed and one-tailed; both p ≈ .192",
])
def test_unstated_tail_label_without_value_in_segment_fails(derived):
    # #610 round-1 fix 1: a bare label is not a shown value — each label
    # needs a digit inside its own `;`-delimited segment.
    with pytest.raises(phase.ConformanceError, match="RECEIPT-TAILS"):
        check_receipts(
            receipt_section(p_receipt(derived_value_or_range=derived))
        )


@pytest.mark.parametrize("derived", [
    "two–tailed p ≈ .192; one–tailed p ≈ .096",
    "two‐tailed p = 0.192; one tailed p = 0.096",
    "TWO-TAILED p ≈ .192; One-Tailed p ≈ .096",
])
def test_unstated_tail_hyphen_and_case_variants_pass(derived):
    check_receipts(
        receipt_section(p_receipt(derived_value_or_range=derived))
    )


def test_attestation_pass_prints_declaration_only_advisory(capsys):
    # #610 round-1 fix 2: the attestation is declaration-only; the pass is
    # annotated so the run record cannot read it as machine-verified
    # applicability.
    check_receipts(receipts=None, body="prose review body without findings")
    out = capsys.readouterr().out
    assert "[RECEIPT-ATTESTATION: declaration-only" in out


def test_receipt_pass_prints_no_attestation_advisory(capsys):
    check_receipts(receipt_section(grim_receipt()))
    assert "[RECEIPT-ATTESTATION" not in capsys.readouterr().out


@pytest.mark.parametrize("decorated", [
    "**status:** mismatch",
    "| status: mismatch |",
    "1. status: mismatch",
    "> status: mismatch",
    "  status: mismatch",
    "`status`: mismatch",
    "sTaTus: mismatch",
    "ｓｔａｔｕｓ: mismatch",
])
def test_decorated_status_line_aborts_loudly(decorated):
    # #610 round-1 fix 4: an unenumerated decoration of a machine field is a
    # loud declaration, never a silently starved required-field count.
    lines = receipt_section(grim_receipt(status=None))
    lines.insert(lines.index("finding_ref: W1"), decorated)
    with pytest.raises(
        phase.ConformanceError, match="decorated or non-canonical"
    ):
        check_receipts(lines)


def test_decorated_forbidden_field_cannot_pass_silently():
    # A decorated spelling of a field the procedure forbids used to sail
    # through the forbidden-field guard unseen; it now aborts.
    lines = receipt_section(grim_receipt())
    lines.insert(
        lines.index("finding_ref: W1"), "**tail_convention:** two-tailed"
    )
    with pytest.raises(
        phase.ConformanceError, match="decorated or non-canonical"
    ):
        check_receipts(lines)


def test_prose_naming_a_field_mid_sentence_stays_tolerated():
    lines = receipt_section(grim_receipt())
    lines.insert(
        lines.index("finding_ref: W1"),
        "The reported status: a value the paper never reconciles.",
    )
    check_receipts(lines)


@pytest.mark.parametrize("backref", [
    "**Arithmetic Receipt**: AR1, AR2",
    "**Arithmetic Receipt**: AR1 which shows the mismatch",
    "**Arithmetic Receipt:** AR1",
    "**Arithmetic Receipt**: see AR1",
])
def test_non_exact_backref_value_aborts(backref):
    # #610 round-1 fix 5: the back-reference value is exactly AR<n> to end
    # of line or next pipe; list values and trailing prose abort.
    body = W1_BACKREF_BODY.replace("**Arithmetic Receipt**: AR1", backref)
    with pytest.raises(phase.ConformanceError, match="RECEIPT-LINKAGE"):
        check_receipts(receipt_section(grim_receipt()), body=body)


def test_fenced_backref_declaration_aborts():
    body = W1_BACKREF_BODY.replace(
        "**Arithmetic Receipt**: AR1\n",
        "```\n**Arithmetic Receipt**: AR1\n```\n",
    )
    with pytest.raises(phase.ConformanceError, match="RECEIPT-LINKAGE"):
        check_receipts(receipt_section(grim_receipt()), body=body)


def test_prose_mentioning_the_receipts_section_stays_tolerated():
    body = W1_BACKREF_BODY + (
        "\nSee the Arithmetic Receipts section: AR1 documents the "
        "reachability check.\n"
    )
    check_receipts(receipt_section(grim_receipt()), body=body)


def grimmer_receipt(**overrides) -> list[str]:
    # Spec §5.3 prospective MS01 v0.2 worked case: N=10, M=3.00, SD=0.10.
    fields = {
        "procedure_id": "grimmer",
        "evidence_anchor": "table: Table 3, SD=0.10 with N=10, M=3.00",
        "reported_inputs": "single 1-5 integer item, N=10, M=3.00, SD=0.10, "
                           "sample SD, two-decimal precision",
        "assumptions": "sample SD as stated in §3.4; integer responses on "
                       "the published 1-5 scale",
        "derivation": "sum fixed at 30; all-3s give SD 0; any deviation "
                      "pair gives squared-deviation sum >= 2, so minimum "
                      "nonzero sample SD is sqrt(2/9)",
        "derived_value_or_range": "attainable sample SDs: 0 or >= 0.4714...",
        "comparison_rule": "an attainable SD must round to 0.10 at two "
                           "decimals",
        "rounding_interval": "[0.095, 0.105)",
        "nearest_achievable": "0 and sqrt(2/9) = 0.4714... straddle the "
                              "reported 0.10",
        "status": "mismatch",
        "finding_ref": "W1",
    }
    fields.update(overrides)
    return [f"{key}: {value}" for key, value in fields.items()
            if value is not None]


def test_valid_grimmer_mismatch_receipt_passes():
    check_receipts(receipt_section(grimmer_receipt()))


@pytest.mark.parametrize("key", [
    "rounding_interval", "nearest_achievable", "derivation",
])
def test_grimmer_verdict_missing_field_fails(key):
    with pytest.raises(phase.ConformanceError, match=key):
        check_receipts(receipt_section(grimmer_receipt(**{key: None})))


# --- #610 round-2 pins: comment visibility, preamble, cells, tails ---------


def test_comment_hidden_receipt_block_aborts():
    # Round-2 P1 (both tracks): a receipt the rendered card does not show
    # cannot satisfy an auditability gate.
    lines = ["<!--", *receipt_section(grim_receipt()), "-->"]
    with pytest.raises(phase.ConformanceError, match="HTML comment"):
        check_receipts(lines)


def test_comment_hidden_attestation_aborts():
    lines = ["<!--", "no_recomputable_statistics: nothing", "-->"]
    with pytest.raises(phase.ConformanceError, match="HTML comment"):
        check_receipts(lines, body="prose")


def test_unclosed_comment_cannot_swallow_the_receipts():
    lines = ["<!--", *receipt_section(grim_receipt())]
    with pytest.raises(phase.ConformanceError, match="HTML comment"):
        check_receipts(lines)


def test_visible_receipts_with_hidden_duplicate_field_abort():
    lines = receipt_section(grim_receipt()) + [
        "<!--", "status: consistent", "-->",
    ]
    with pytest.raises(phase.ConformanceError, match="HTML comment"):
        check_receipts(lines)


def test_comment_markup_in_receipt_section_aborts():
    # Round-3 adjudication supersedes the round-2 commented-prose
    # tolerance: the receipt section is a comment-free zone, because a
    # paragraph-inline `prose <!--` opener the block visibility model
    # cannot read would otherwise launder the receipts below it.
    lines = receipt_section(grim_receipt()) + [
        "<!--", "internal note, no machine fields", "-->",
    ]
    with pytest.raises(phase.ConformanceError, match="HTML comment markup"):
        check_receipts(lines)


def test_inline_comment_opener_in_receipt_section_aborts():
    lines = [
        "visible explanation <!--",
        *receipt_section(grim_receipt()),
        "-->",
    ]
    with pytest.raises(phase.ConformanceError, match="HTML comment markup"):
        check_receipts(lines)


def test_fenced_comment_markup_in_receipts_is_literal_text():
    lines = receipt_section(grim_receipt()) + [
        "```", "<!-- rendered literally inside the fence -->", "```",
    ]
    check_receipts(lines)


def test_inline_comment_span_hidden_backref_aborts():
    # Round-3 P1 (codex track): `prose <!--` inside a paragraph hides the
    # following lines until `-->` without the block model seeing it.
    body = W1_BACKREF_BODY.replace(
        "**Arithmetic Receipt**: AR1\n",
        "prose lead-in <!--\n**Arithmetic Receipt**: AR1\n-->\n",
    )
    with pytest.raises(phase.ConformanceError, match="paragraph-inline"):
        check_receipts(receipt_section(grim_receipt()), body=body)


def test_inline_comment_span_dies_at_a_blank_line():
    # A blank line ends the paragraph and with it the raw-HTML span, so a
    # backref in the NEXT paragraph is live and the card conforms.
    body = W1_BACKREF_BODY.replace(
        "**Arithmetic Receipt**: AR1\n",
        "prose mentioning <!-- an unclosed marker\n\n"
        "**Arithmetic Receipt**: AR1\n",
    )
    check_receipts(receipt_section(grim_receipt()), body=body)


@pytest.mark.parametrize("entity_line", [
    "tail_convention&#xFF1A; two-tailed",
    "status&#65306; mismatch",
])
def test_fullwidth_colon_entity_field_spelling_aborts(entity_line):
    # Round-3 P1 (codex track): unescape must run BEFORE the NFKC fold so
    # a fullwidth-colon entity decodes and then folds to `:`.
    lines = receipt_section(grim_receipt())
    lines.insert(lines.index("finding_ref: W1"), entity_line)
    with pytest.raises(
        phase.ConformanceError, match="decorated or non-canonical"
    ):
        check_receipts(lines)


def test_fullwidth_colon_entity_backref_aborts():
    body = W1_BACKREF_BODY.replace(
        "**Arithmetic Receipt**: AR1",
        "**Arithmetic Receipt**: AR1\n**Arithmetic Receipt**&#xFF1A; AR2",
    )
    with pytest.raises(phase.ConformanceError, match="RECEIPT-LINKAGE"):
        check_receipts(receipt_section(grim_receipt()), body=body)


def test_pipe_inside_link_destination_is_not_a_cell(  # codex round-3 P2
):
    lines = receipt_section(grim_receipt())
    lines.insert(
        lines.index("finding_ref: W1"),
        "Quoted source: [record](https://example.org/a|status:pending)",
    )
    check_receipts(lines)


def test_escaped_pipe_and_code_span_pipes_are_not_cells():
    lines = receipt_section(grim_receipt())
    lines.insert(
        lines.index("finding_ref: W1"),
        "See the raw marker \\| and the cited `a|status:pending` token.",
    )
    check_receipts(lines)


def test_comment_hidden_backref_aborts():
    body = W1_BACKREF_BODY.replace(
        "**Arithmetic Receipt**: AR1\n",
        "<!--\n**Arithmetic Receipt**: AR1\n-->\n",
    )
    with pytest.raises(phase.ConformanceError, match="commented-out"):
        check_receipts(receipt_section(grim_receipt()), body=body)


def test_indented_code_backref_is_not_credited():
    # Round-3 (security track): a 4-column-indented back-reference renders
    # as literal indented code, not a field line, and must not earn the
    # linkage credit its fenced twin is denied.
    body = W1_BACKREF_BODY.replace(
        "**Arithmetic Receipt**: AR1\n",
        "\n    **Arithmetic Receipt**: AR1\n",
    )
    with pytest.raises(phase.ConformanceError, match="indented-code"):
        check_receipts(receipt_section(grim_receipt()), body=body)


def test_four_space_paragraph_continuation_backref_still_counts():
    # A 4-space-indented line CONTINUING an open paragraph is prose to
    # CommonMark, not code; the backref on it renders with its bold applied
    # and stays a live declaration.
    body = W1_BACKREF_BODY.replace(
        "**Arithmetic Receipt**: AR1\n",
        "prose lead-in line\n    **Arithmetic Receipt**: AR1\n",
    )
    check_receipts(receipt_section(grim_receipt()), body=body)


@pytest.mark.parametrize("bad", [
    "procedure_id: cohen_d_check",
    "finding_ref: W9",
    "not_computable_reason: bogus_reason",
    "status: not_applicable",
])
def test_machine_line_in_section_preamble_aborts(bad):
    # Round-2 P1 (security track): the preamble is not a parking lot — a
    # canonical machine line the enum/linkage gates never inspect aborts.
    lines = [bad, "", *receipt_section(grim_receipt())]
    with pytest.raises(
        phase.ConformanceError, match="outside every ### AR<n>"
    ):
        check_receipts(lines)


def test_attestation_card_with_stray_machine_line_aborts():
    lines = [
        "no_recomputable_statistics: nothing recomputable",
        "status: consistent",
    ]
    with pytest.raises(
        phase.ConformanceError, match="outside every ### AR<n>"
    ):
        check_receipts(lines, body="prose")


def test_forbidden_field_in_a_later_table_cell_aborts():
    # Round-2 P1 (codex track): the head-of-line shape test alone let a
    # decorated forbidden field hide in a later GFM cell.
    lines = receipt_section(grim_receipt())
    lines.insert(
        lines.index("finding_ref: W1"),
        "| note | **tail_convention:** two-tailed |",
    )
    with pytest.raises(
        phase.ConformanceError, match="decorated or non-canonical"
    ):
        check_receipts(lines)


def test_entity_colon_field_spelling_aborts():
    lines = receipt_section(grim_receipt())
    lines.insert(
        lines.index("finding_ref: W1"), "tail_convention&#58; two-tailed"
    )
    with pytest.raises(
        phase.ConformanceError, match="decorated or non-canonical"
    ):
        check_receipts(lines)


def test_cjk_prose_in_a_table_cell_stays_tolerated():
    lines = receipt_section(grim_receipt())
    lines.insert(lines.index("finding_ref: W1"), "| 註記 | 狀態說明:如上 |")
    check_receipts(lines)


@pytest.mark.parametrize("half_bold", ["**status: mismatch", "status**: mismatch"])
def test_half_bold_field_is_not_canonical(half_bold):
    lines = receipt_section(grim_receipt(status=None))
    lines.insert(lines.index("finding_ref: W1"), half_bold)
    with pytest.raises(
        phase.ConformanceError, match="decorated or non-canonical"
    ):
        check_receipts(lines)


def test_canonical_plus_malformed_backref_on_one_line_aborts():
    # Round-2 P1 (codex track): a canonical match must not launder a second
    # malformed declaration on the same line.
    body = W1_BACKREF_BODY.replace(
        "**Arithmetic Receipt**: AR1",
        "**Arithmetic Receipt**: AR1 | **Arithmetic Receipt:** see AR2",
    )
    with pytest.raises(phase.ConformanceError, match="RECEIPT-LINKAGE"):
        check_receipts(receipt_section(grim_receipt()), body=body)


def test_indented_trailing_h2_still_violates_terminal_rule():
    # Round-2 (security track): a 1-3-space-indented `##` renders as a
    # heading even though the section grammar ignores it.
    text = phase2_text(
        "methodology",
        body=W1_BACKREF_BODY,
        receipts=receipt_section(grim_receipt()),
    ) + "\n\n   ## Trailing Section\n\ntext\n"
    report = panel.parse_report("p2.md", text, FULL)
    with pytest.raises(
        phase.ConformanceError, match="must be the final section"
    ):
        phase.check_methodology_receipts(report)


def test_three_space_indented_fence_is_read_dedented():
    # Round-2 (codex track): CommonMark strips the opener's indent from the
    # displayed content of an indented fence; the gate reads display form.
    lines = ["   ```"] + [
        "   " + line for line in receipt_section(grim_receipt())
    ] + ["   ```"]
    check_receipts(lines)


def test_indented_fence_hiding_direction_still_aborts():
    lines = [
        "no_recomputable_statistics: nothing",
        "",
        "   ```",
        *("   " + line for line in receipt_section(grim_receipt())),
        "   ```",
    ]
    with pytest.raises(phase.ConformanceError, match="forbidden when"):
        check_receipts(lines)


def test_tail_value_before_label_in_segment_passes():
    check_receipts(receipt_section(p_receipt(
        derived_value_or_range="p = .192 (two-tailed); p = .096 (one-tailed)",
    )))


def test_embedded_word_tail_labels_do_not_satisfy_the_rule():
    with pytest.raises(phase.ConformanceError, match="RECEIPT-TAILS"):
        check_receipts(receipt_section(p_receipt(
            derived_value_or_range="notwo-tailed note 2; someone-tailed 1",
        )))


def test_fused_tail_label_with_value_still_counts():
    # A `twotailed` typo carries its value; rejecting it would be a false
    # abort on an unretryable phase (declared boundary).
    check_receipts(receipt_section(p_receipt(
        derived_value_or_range="twotailed p=.192; onetailed p=.096",
    )))


def test_field_name_leading_prose_abort_is_a_declared_boundary():
    # Security-track P2, adjudicated as documented cost: a prose line whose
    # head spells a field name is indistinguishable from a decorated
    # machine line, and the fragment now warns the seat not to write one.
    lines = receipt_section(grim_receipt()) + [
        "Assumptions: none beyond what the paper licenses.",
    ]
    with pytest.raises(
        phase.ConformanceError, match="decorated or non-canonical"
    ):
        check_receipts(lines)


# --- #610 round-4 pins: display-form parity, spans, code semantics ---------


def test_code_span_backref_cannot_outrank_the_rendered_one():
    # Round-4 P1 (security track): canonical parsing and the declaration
    # count run on the same display form, so a code-span declaration can
    # never be credited over the rendered field beside it.
    body = W1_BACKREF_BODY.replace(
        "**Arithmetic Receipt**: AR1",
        "`| **Arithmetic Receipt**: AR1 |` **Arithmetic Receipt**: AR7",
    )
    with pytest.raises(phase.ConformanceError, match="exactly one"):
        check_receipts(receipt_section(grim_receipt()), body=body)


def test_inert_code_span_beside_a_canonical_backref_is_harmless():
    body = W1_BACKREF_BODY.replace(
        "**Arithmetic Receipt**: AR1",
        "`inert` **Arithmetic Receipt**: AR1",
    )
    check_receipts(receipt_section(grim_receipt()), body=body)


def test_backref_after_a_closing_comment_on_the_same_line_is_live():
    # Round-4 (security track): the span ends at `-->`; the rendered
    # remainder of the line is parsed, not dropped.
    body = W1_BACKREF_BODY.replace(
        "**Arithmetic Receipt**: AR1\n",
        "open <!-- note\nclosed --> **Arithmetic Receipt**: AR1\n",
    )
    check_receipts(receipt_section(grim_receipt()), body=body)


def test_spurious_backref_after_a_closing_comment_still_aborts():
    body = W1_BACKREF_BODY.replace(
        "**Arithmetic Receipt**: AR1\n",
        "**Arithmetic Receipt**: AR1\n"
        "open <!-- x\nclosed --> **Arithmetic Receipt**: AR2\n",
    )
    with pytest.raises(phase.ConformanceError, match="exactly one"):
        check_receipts(receipt_section(grim_receipt()), body=body)


def test_backref_behind_an_opener_on_its_own_line_is_not_credited():
    # Round-4 P1 (codex track), tightened in round 5: content after `<!--`
    # on the opener line is inside the span; since round 5 the hidden
    # declaration itself aborts at the hiding site rather than surfacing
    # later as a missing linkage.
    body = W1_BACKREF_BODY.replace(
        "**Arithmetic Receipt**: AR1\n",
        "prose <!-- | **Arithmetic Receipt**: AR1\n-->\n",
    )
    with pytest.raises(phase.ConformanceError, match="paragraph-inline"):
        check_receipts(receipt_section(grim_receipt()), body=body)


def test_unequal_code_ticks_do_not_hide_a_later_cell_field():
    # Round-4 P1 (codex track): a 1-backtick opener with a 2-backtick
    # closer is NOT a code span to the renderer; the pipe still makes a
    # cell and the forbidden field in it still aborts.
    lines = receipt_section(grim_receipt())
    lines.insert(
        lines.index("finding_ref: W1"),
        "| `note | **tail_convention:** two-tailed`` |",
    )
    with pytest.raises(
        phase.ConformanceError, match="decorated or non-canonical"
    ):
        check_receipts(lines)


def test_equal_code_ticks_with_pipes_stay_tolerated():
    lines = receipt_section(grim_receipt())
    lines.insert(
        lines.index("finding_ref: W1"),
        "raw `|status: pending` token cited here.",
    )
    check_receipts(lines)


def test_second_line_of_an_indented_code_block_is_still_code():
    # Round-4 P2 (codex track): an indented-code line never opens a
    # paragraph, so the next code line is not a paragraph continuation.
    body = W1_BACKREF_BODY.replace(
        "**Arithmetic Receipt**: AR1\n",
        "\n    note\n    **Arithmetic Receipt**: AR1\n",
    )
    with pytest.raises(phase.ConformanceError, match="indented-code"):
        check_receipts(receipt_section(grim_receipt()), body=body)


def test_literal_comment_marker_in_a_code_span_opens_nothing():
    # Round-4 P2 (codex track): code spans outrank raw HTML, so a quoted
    # `<!--` cannot open an inline span and abort the next backref.
    body = W1_BACKREF_BODY.replace(
        "**Arithmetic Receipt**: AR1\n",
        "prose `<!--` literal\n**Arithmetic Receipt**: AR1\n",
    )
    check_receipts(receipt_section(grim_receipt()), body=body)


def test_hidden_declaration_beside_a_visible_one_still_aborts():
    # Round-5 P2 (codex track): a declaration inside the hidden span
    # aborts even when the same line also carries a visible, credited one.
    body = W1_BACKREF_BODY.replace(
        "**Arithmetic Receipt**: AR1\n",
        "**Arithmetic Receipt**: AR1 <!-- | **Arithmetic Receipt**: AR2\n"
        "-->\n",
    )
    with pytest.raises(phase.ConformanceError, match="paragraph-inline"):
        check_receipts(receipt_section(grim_receipt()), body=body)


def test_prose_span_cannot_shield_a_declaration_in_the_next_span():
    # Round-6 P2 (codex track): hidden spans are checked one by one, so a
    # harmless first span cannot prefix-shield a declaration in the next.
    body = W1_BACKREF_BODY.replace(
        "**Arithmetic Receipt**: AR1\n",
        "**Arithmetic Receipt**: AR1 <!-- reviewer note --> "
        "<!-- **Arithmetic Receipt**: AR2 -->\n",
    )
    with pytest.raises(phase.ConformanceError, match="paragraph-inline"):
        check_receipts(receipt_section(grim_receipt()), body=body)


def test_fragments_across_spans_cannot_synthesize_a_declaration():
    body = W1_BACKREF_BODY.replace(
        "**Arithmetic Receipt**: AR1\n",
        "**Arithmetic Receipt**: AR1 <!-- Arithmetic --> "
        "<!-- Receipt: typo -->\n",
    )
    check_receipts(receipt_section(grim_receipt()), body=body)


def test_hidden_prose_beside_a_visible_declaration_is_harmless():
    body = W1_BACKREF_BODY.replace(
        "**Arithmetic Receipt**: AR1\n",
        "**Arithmetic Receipt**: AR1 <!-- reviewer note\n-->\n",
    )
    check_receipts(receipt_section(grim_receipt()), body=body)


def test_any_atx_heading_ends_an_inline_comment_span():
    body = W1_BACKREF_BODY.replace(
        "**Arithmetic Receipt**: AR1\n",
        "prose <!-- open\n#### Detail\n**Arithmetic Receipt**: AR1\n",
    )
    check_receipts(receipt_section(grim_receipt()), body=body)


def test_grimmer_grim_inconsistent_mean_is_not_computable():
    check_receipts(
        receipt_section(grimmer_receipt(
            status="not_computable",
            not_computable_reason="mean_grim_inconsistent",
            rounding_interval=None,
            nearest_achievable=None,
            finding_ref=None,
        )),
        body="prose",
    )


@pytest.mark.parametrize("role", ["eic", "domain", "perspective", "da"])
def test_receipt_section_is_forbidden_on_other_seats(role):
    text = phase2_text(role) + \
        "\n\n## Arithmetic Receipts\n\nno_recomputable_statistics: rogue\n"
    report = panel.parse_report("p2.md", text, FULL)
    with pytest.raises(
        phase.ConformanceError, match="RECEIPT-SECTION-FORBIDDEN"
    ):
        phase.check_receipt_section_forbidden(report)


def test_full_cli_pass_with_real_receipts(tmp_path):
    args = write_cli_files(tmp_path, "methodology")
    phase2_path = Path(args[args.index("--phase2") + 1])
    phase2_path.write_text(
        phase2_text(
            "methodology",
            body=W1_BACKREF_BODY,
            receipts=receipt_section(grim_receipt()),
        ),
        encoding="utf-8",
    )
    assert phase.main(args + ["--role", "methodology"]) == phase.EXIT_PASS


def test_full_cli_rejects_missing_receipt_section(tmp_path, capsys):
    args = write_cli_files(tmp_path, "methodology")
    phase2_path = Path(args[args.index("--phase2") + 1])
    text = phase2_text("methodology", body="prose")
    phase2_path.write_text(
        text[: text.index("\n## Arithmetic Receipts")], encoding="utf-8"
    )
    assert phase.main(args + ["--role", "methodology"]) == \
        phase.EXIT_CONFORMANCE
    assert "[RECEIPT-MISSING:" in capsys.readouterr().out


# --- #610 step-5 extraction gate + injected-receipt identity gate ---------


from scripts import recompute_receipts as recompute  # noqa: E402


GRIM_EXTRACTION = (
    "## Recompute Extraction\n"
    "\n"
    "### RR1\n"
    "procedure_id: grim\n"
    "evidence_anchor: table: Table 2, M=3.847 with N=87\n"
    "reported_inputs: single 1-5 integer item, N=87, M=3.847\n"
    "assumptions: unweighted single-item mean as stated in §3.2\n"
    "n: 87\n"
    "reported_mean: 3.847\n"
    "scale_min: 1\n"
    "scale_max: 5\n"
    "rounding_rule: unstated\n"
)
ATTESTATION_EXTRACTION = (
    "## Recompute Extraction\n"
    "\n"
    "no_recomputable_statistics: the manuscript reports no statistic a "
    "bounded procedure covers\n"
)


def extraction_args(tmp_path: Path, extraction_text: str,
                    role: str = "methodology") -> list[str]:
    args = write_cli_files(tmp_path, role)
    del args[args.index("--phase2"):args.index("--phase2") + 2]
    extraction = tmp_path / "extraction.md"
    extraction.write_text(extraction_text, encoding="utf-8")
    return args + ["--extraction", str(extraction), "--role", role]


def test_extraction_stage_passes_on_rr_grammar(tmp_path, capsys):
    assert phase.main(extraction_args(tmp_path, GRIM_EXTRACTION)) == \
        phase.EXIT_PASS
    assert "EXTRACTION-CONFORMANCE: PASS" in capsys.readouterr().out


def test_extraction_stage_passes_on_attestation_with_advisory(tmp_path,
                                                              capsys):
    assert phase.main(extraction_args(tmp_path, ATTESTATION_EXTRACTION)) == \
        phase.EXIT_PASS
    out = capsys.readouterr().out
    assert "EXTRACTION-CONFORMANCE: PASS" in out
    assert "[RECEIPT-ATTESTATION:" in out


def test_extraction_stage_is_methodology_only(tmp_path, capsys):
    assert phase.main(
        extraction_args(tmp_path, GRIM_EXTRACTION, role="eic")
    ) == phase.EXIT_CONTRACT
    assert "[ROLE-BINDING:" in capsys.readouterr().out


def test_extraction_preamble_prose_is_nonconforming(tmp_path, capsys):
    assert phase.main(extraction_args(
        tmp_path, "I will now extract the statistics.\n\n" + GRIM_EXTRACTION
    )) == phase.EXIT_CONFORMANCE
    assert "[EXTRACTION-GRAMMAR:" in capsys.readouterr().out


def test_extraction_extra_section_is_nonconforming(tmp_path, capsys):
    assert phase.main(extraction_args(
        tmp_path, GRIM_EXTRACTION + "\n## Notes\n\nsome prose\n"
    )) == phase.EXIT_CONFORMANCE
    assert "[EXTRACTION-GRAMMAR:" in capsys.readouterr().out


def test_extraction_missing_section_is_nonconforming(tmp_path, capsys):
    assert phase.main(extraction_args(
        tmp_path, "## Wrong Heading\n\nn: 87\n"
    )) == phase.EXIT_CONFORMANCE
    assert "[EXTRACTION-GRAMMAR:" in capsys.readouterr().out


def test_extraction_unknown_field_is_nonconforming(tmp_path, capsys):
    assert phase.main(extraction_args(
        tmp_path, GRIM_EXTRACTION + "surprise_field: value\n"
    )) == phase.EXIT_CONFORMANCE
    assert "unknown field" in capsys.readouterr().out


def test_extraction_prose_line_inside_section_is_nonconforming(tmp_path,
                                                               capsys):
    assert phase.main(extraction_args(
        tmp_path, GRIM_EXTRACTION + "This mean looks impossible to me.\n"
    )) == phase.EXIT_CONFORMANCE
    assert "not a machine line" in capsys.readouterr().out


def test_extraction_invalid_anchor_is_nonconforming(tmp_path, capsys):
    bad = GRIM_EXTRACTION.replace(
        "evidence_anchor: table: Table 2, M=3.847 with N=87",
        "evidence_anchor: somewhere in the paper",
    )
    assert phase.main(extraction_args(tmp_path, bad)) == \
        phase.EXIT_CONFORMANCE
    assert "ANCHOR" in capsys.readouterr().out


def test_extraction_and_phase2_stages_are_mutually_exclusive(tmp_path):
    args = write_cli_files(tmp_path, "methodology")
    extraction = tmp_path / "extraction.md"
    extraction.write_text(GRIM_EXTRACTION, encoding="utf-8")
    with pytest.raises(SystemExit) as exc:
        phase._parse_args(
            args + ["--extraction", str(extraction), "--role", "methodology"]
        )
    assert exc.value.code == 2


def test_injected_receipts_flag_requires_phase2(tmp_path):
    args = phase1_only_args(tmp_path, "methodology")
    with pytest.raises(SystemExit) as exc:
        phase._parse_args(args + ["--injected-receipts", "x.md"])
    assert exc.value.code == 2


def injected_receipts_text() -> str:
    return recompute.compute_receipts(
        recompute.parse_extraction(GRIM_EXTRACTION)
    )


def injected_cli(tmp_path: Path, card_receipt_lines: list[str],
                 injected_text: str, body: str = W1_BACKREF_BODY,
                 role: str = "methodology") -> list[str]:
    args = write_cli_files(tmp_path, role)
    (tmp_path / "p2.md").write_text(
        phase2_text(role, body=body, receipts=card_receipt_lines),
        encoding="utf-8",
    )
    injected = tmp_path / "injected.md"
    injected.write_text(injected_text, encoding="utf-8")
    return args + ["--role", role, "--injected-receipts", str(injected)]


def faithful_card_lines(injected_text: str) -> list[str]:
    # The seat's only permitted addition: the finding_ref linkage line on
    # the (single, mismatch) receipt.
    lines = [line for line in injected_text.splitlines()[1:] if line]
    return lines + ["finding_ref: W1"]


def test_injected_identity_passes_on_verbatim_copy(tmp_path):
    injected = injected_receipts_text()
    assert phase.main(injected_cli(
        tmp_path, faithful_card_lines(injected), injected
    )) == phase.EXIT_PASS


def test_injected_identity_rejects_an_altered_line(tmp_path, capsys):
    injected = injected_receipts_text()
    lines = [
        line.replace("status: mismatch", "status: consistent")
        if line == "status: mismatch" else line
        for line in faithful_card_lines(injected)
        if line != "finding_ref: W1"
    ]
    assert phase.main(injected_cli(
        tmp_path, lines, injected, body="clean methodology review prose"
    )) == phase.EXIT_CONFORMANCE
    assert "[RECEIPT-IDENTITY:" in capsys.readouterr().out


def test_injected_identity_rejects_a_paraphrased_line(tmp_path, capsys):
    # A reworded derivation still satisfies the receipt GRAMMAR (the line
    # exists and parses), so only the identity gate can catch it — the
    # incremental value this gate exists for.
    injected = injected_receipts_text()
    lines = [
        "derivation: I re-derived this my own way" if
        line.startswith("derivation: ") else line
        for line in faithful_card_lines(injected)
    ]
    assert phase.main(injected_cli(tmp_path, lines, injected)) == \
        phase.EXIT_CONFORMANCE
    assert "[RECEIPT-IDENTITY:" in capsys.readouterr().out


def test_injected_identity_rejects_an_extra_receipt(tmp_path, capsys):
    injected = injected_receipts_text()
    extra = [
        "### AR2",
        "procedure_id: n_from_df",
        "evidence_anchor: table: Table 3, t(156) with N at most 142",
        "reported_inputs: df=156, stated analytic N at most 142",
        "assumptions: independent-groups t as stated",
        "derivation: df=N1+N2-2 gives N = 158",
        "derived_value_or_range: implied N = 158",
        "comparison_rule: implied N must not exceed 142",
        "status: consistent",
        "df_identity: df=N1+N2-2",
    ]
    assert phase.main(injected_cli(
        tmp_path, faithful_card_lines(injected) + extra, injected
    )) == phase.EXIT_CONFORMANCE
    assert "[RECEIPT-IDENTITY:" in capsys.readouterr().out


def test_injected_identity_survives_added_blank_lines(tmp_path):
    injected = injected_receipts_text()
    spaced = []
    for line in faithful_card_lines(injected):
        spaced += [line, ""]
    assert phase.main(injected_cli(tmp_path, spaced, injected)) == \
        phase.EXIT_PASS


def test_injected_receipts_are_methodology_only(tmp_path, capsys):
    injected = injected_receipts_text()
    args = write_cli_files(tmp_path, "eic")
    injected_path = tmp_path / "injected.md"
    injected_path.write_text(injected, encoding="utf-8")
    assert phase.main(
        args + ["--role", "eic", "--injected-receipts", str(injected_path)]
    ) == phase.EXIT_CONTRACT
    assert "[ROLE-BINDING:" in capsys.readouterr().out


def test_injected_file_without_heading_is_a_contract_error(tmp_path, capsys):
    injected = injected_receipts_text()
    assert phase.main(injected_cli(
        tmp_path, faithful_card_lines(injected),
        "### AR1\nprocedure_id: grim\n",
    )) == phase.EXIT_CONTRACT
    assert "[INJECTED-RECEIPTS-INVALID:" in capsys.readouterr().out


def test_injected_identity_pass_emits_its_witness_marker(tmp_path, capsys):
    injected = injected_receipts_text()
    assert phase.main(injected_cli(
        tmp_path, faithful_card_lines(injected), injected
    )) == phase.EXIT_PASS
    assert "RECEIPT-IDENTITY: PASS" in capsys.readouterr().out


def test_injected_identity_rejects_a_decorated_finding_ref(tmp_path, capsys):
    # codex round 1, P2-4: the receipt GRAMMAR tolerates a decorated
    # finding_ref, but under injection only the plain spelling is the
    # permitted addition.
    injected = injected_receipts_text()
    lines = [
        "- **finding_ref**: W1" if line == "finding_ref: W1" else line
        for line in faithful_card_lines(injected)
    ]
    assert phase.main(injected_cli(tmp_path, lines, injected)) == \
        phase.EXIT_CONFORMANCE
    assert "[RECEIPT-IDENTITY:" in capsys.readouterr().out
