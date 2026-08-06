"""Tests for the #610 step-5 deterministic arithmetic-receipt calculator.

Three families: (1) distribution-tail accuracy pinned against published
critical values and cross-family identities; (2) verdict logic pinned
against the parent spec's §5 worked cases plus every sentinel ->
``not_computable`` mapping; (3) grammar compatibility — every emitted
machine line must parse under the #644 receipt gate's own field regexes,
because the injected-receipt identity gate makes these exact bytes the
card's receipt section.
"""
from __future__ import annotations

import pytest

from scripts import check_phase_conformance as phase
from scripts import recompute_receipts as rr


def build(body: str) -> str:
    return "## Recompute Extraction\n\n" + body


def one_request(procedure: str, fields: dict[str, str]) -> str:
    lines = [
        "### RR1",
        f"procedure_id: {procedure}",
        "evidence_anchor: table: Table 1, reported statistics under test",
        "reported_inputs: the manuscript values under test",
        "assumptions: only what the paper licenses",
    ]
    lines += [f"{key}: {value}" for key, value in fields.items()]
    return build("\n".join(lines) + "\n")


P_FIELDS = {
    "test_family": "t",
    "statistic_value": "1.31",
    "df": "140",
    "reported_p_comparator": "equals",
    "reported_p_value": ".008",
    "tail_convention": "unstated",
}
GRIM_FIELDS = {
    "n": "87",
    "reported_mean": "3.847",
    "scale_min": "1",
    "scale_max": "5",
    "rounding_rule": "unstated",
}
GRIMMER_FIELDS = {
    "n": "10",
    "reported_mean": "3.00",
    "scale_min": "1",
    "scale_max": "5",
    "rounding_rule": "unstated",
    "reported_sd": "0.10",
    "sd_convention": "sample",
}
N_FROM_DF_FIELDS = {
    "df_reported": "156",
    "df_identity_candidate": "df=N1+N2-2",
    "stated_n": "142",
    "stated_n_relation": "at_most",
}


def receipt_lines(procedure: str, fields: dict[str, str]) -> dict[str, str]:
    text = rr.compute_receipts(
        rr.parse_extraction(one_request(procedure, fields))
    )
    parsed = {}
    for line in text.splitlines():
        if not line or line.startswith("#"):
            continue
        key, value = line.split(": ", 1)
        parsed[key] = value
    return parsed


# --- distribution accuracy ------------------------------------------------

def test_t_two_tailed_critical_value():
    assert rr.t_tail_two(2.228, 10) == pytest.approx(0.05, abs=2e-4)


def test_spec_worked_t_values():
    assert round(rr.t_tail_two(1.31, 140), 3) == 0.192
    assert round(rr.t_tail_two(1.31, 140) / 2.0, 3) == 0.096


def test_z_two_tailed_critical_value():
    assert rr.z_tail_two(1.96) == pytest.approx(0.05, abs=1e-4)


def test_chi_square_critical_value():
    assert rr.chi2_tail_upper(3.841, 1) == pytest.approx(0.05, abs=2e-4)


def test_f_critical_value():
    assert rr.f_tail_upper(4.965, 1, 10) == pytest.approx(0.05, abs=3e-4)


def test_f_of_squared_t_matches_two_tailed_t():
    for t_value, df in ((1.31, 140), (2.5, 7), (0.4, 33)):
        assert rr.f_tail_upper(t_value * t_value, 1, df) == pytest.approx(
            rr.t_tail_two(t_value, df), abs=1e-10
        )


def test_chi_square_of_squared_z_matches_two_tailed_z():
    for z_value in (0.5, 1.96, 3.2):
        assert rr.chi2_tail_upper(z_value * z_value, 1) == pytest.approx(
            rr.z_tail_two(z_value), abs=1e-10
        )


# --- p_from_test_statistic verdicts --------------------------------------

def test_spec_p_case_is_mismatch_with_both_tails_shown():
    fields = receipt_lines("p_from_test_statistic", P_FIELDS)
    assert fields["status"] == "mismatch"
    assert fields["tail_convention"] == "unstated"
    derived = fields["derived_value_or_range"]
    assert "0.192 (two-tailed)" in derived
    assert "0.0962 (one-tailed)" in derived
    assert ";" in derived


def test_p_consistent_under_stated_tail():
    fields = receipt_lines("p_from_test_statistic", {
        **P_FIELDS, "tail_convention": "two-tailed",
        "reported_p_value": ".192",
    })
    assert fields["status"] == "consistent"


def test_p_tail_ambiguous_when_only_one_tail_fits():
    # One-tailed 0.0962 rounds to .10; two-tailed 0.192 does not.
    fields = receipt_lines("p_from_test_statistic", {
        **P_FIELDS, "reported_p_value": ".10",
    })
    assert fields["status"] == "not_computable"
    assert fields["not_computable_reason"] == "tail_ambiguous"


def test_p_inequality_mismatch_when_both_tails_fail():
    fields = receipt_lines("p_from_test_statistic", {
        **P_FIELDS, "reported_p_comparator": "less_than",
        "reported_p_value": ".05",
    })
    assert fields["status"] == "mismatch"


def test_p_inequality_consistent_when_both_tails_pass():
    fields = receipt_lines("p_from_test_statistic", {
        **P_FIELDS, "statistic_value": "3.5",
        "reported_p_comparator": "less_than", "reported_p_value": ".05",
    })
    assert fields["status"] == "consistent"


def test_p_inequality_threshold_graze_is_unresolvable():
    # z = 1.9599639845... has a two-tailed p of exactly .05 to well inside
    # the 1e-9 guard.
    fields = receipt_lines("p_from_test_statistic", {
        "test_family": "z", "statistic_value": "1.9599639845400545",
        "df": "none", "reported_p_comparator": "less_than",
        "reported_p_value": ".05", "tail_convention": "unstated",
    })
    assert fields["status"] == "not_computable"
    assert fields["not_computable_reason"] == "inequality_unresolvable"


def test_p_rounding_boundary_graze_is_ambiguous():
    # The same z against `p = .1` at one decimal: the rounding interval is
    # [.05, .15) and the derived two-tailed value sits on its lower endpoint.
    fields = receipt_lines("p_from_test_statistic", {
        "test_family": "z", "statistic_value": "1.9599639845400545",
        "df": "none", "reported_p_comparator": "equals",
        "reported_p_value": ".1", "tail_convention": "unstated",
    })
    assert fields["status"] == "not_computable"
    assert fields["not_computable_reason"] == "rounding_boundary_ambiguous"


def test_f_receipt_normalizes_tail_to_family_rule():
    fields = receipt_lines("p_from_test_statistic", {
        "test_family": "F", "statistic_value": "3.316", "df": "2,30",
        "reported_p_comparator": "equals", "reported_p_value": ".05",
        "tail_convention": "unstated",
    })
    assert fields["status"] == "consistent"
    assert fields["tail_convention"] == "upper-tail"
    assert "two-tailed" not in fields["derived_value_or_range"]


def test_f_with_paper_stated_two_tail_is_nonstandard():
    fields = receipt_lines("p_from_test_statistic", {
        "test_family": "F", "statistic_value": "3.316", "df": "2,30",
        "reported_p_comparator": "equals", "reported_p_value": ".05",
        "tail_convention": "two-tailed",
    })
    assert fields["not_computable_reason"] == "nonstandard_p_procedure"


def test_p_sentinel_mappings():
    cases = (
        ({"test_family": "unavailable"}, "test_family_ambiguous"),
        ({"statistic_value": "unavailable"}, "missing_reported_value"),
        ({"df": "unavailable"}, "missing_reported_value"),
        # A family-inconsistent df shape (a t with an F pair) is refused at
        # the gate as a retryable transcription slip, not mapped here.
    )
    for override, reason in cases:
        fields = receipt_lines(
            "p_from_test_statistic", {**P_FIELDS, **override}
        )
        assert fields["status"] == "not_computable"
        assert fields["not_computable_reason"] == reason
        # tail_convention is required on every p receipt, verdict or not.
        assert "tail_convention" in fields


# --- grim verdicts --------------------------------------------------------

def test_spec_grim_case_is_mismatch_with_neighbors():
    fields = receipt_lines("grim", GRIM_FIELDS)
    assert fields["status"] == "mismatch"
    assert "334/87 = 3.8391" in fields["nearest_achievable"]
    assert "335/87 = 3.8506" in fields["nearest_achievable"]
    assert fields["rounding_interval"].startswith(
        "3.8465 <= mean <= 3.8475")


def test_grim_consistent_mean():
    fields = receipt_lines("grim", {**GRIM_FIELDS, "reported_mean": "3.851"})
    assert fields["status"] == "consistent"
    assert "335" in fields["derived_value_or_range"]


def test_grim_rounding_rule_disagreement_is_ambiguous():
    # 5/4 = 1.25 is the only candidate sum for a reported 1.3: half-up
    # reaches it, ties-to-even does not, and 1.3 itself is unattainable.
    fields = receipt_lines("grim", {
        "n": "4", "reported_mean": "1.3", "scale_min": "1",
        "scale_max": "5", "rounding_rule": "unstated",
    })
    assert fields["status"] == "not_computable"
    assert fields["not_computable_reason"] == "rounding_rule_ambiguous"


def test_grim_stated_rule_resolves_the_tie():
    consistent = receipt_lines("grim", {
        "n": "4", "reported_mean": "1.3", "scale_min": "1",
        "scale_max": "5", "rounding_rule": "half-up",
    })
    mismatch = receipt_lines("grim", {
        "n": "4", "reported_mean": "1.3", "scale_min": "1",
        "scale_max": "5", "rounding_rule": "half-even",
    })
    assert consistent["status"] == "consistent"
    assert mismatch["status"] == "mismatch"


def test_grim_sentinel_mappings():
    for override, reason in (
        ({"n": "unavailable"}, "analytic_n_ambiguous"),
        ({"scale_min": "unavailable"}, "scale_support_unknown"),
        ({"scale_max": "unavailable"}, "scale_support_unknown"),
    ):
        fields = receipt_lines("grim", {**GRIM_FIELDS, **override})
        assert fields["status"] == "not_computable"
        assert fields["not_computable_reason"] == reason
        # Conditional verdict fields are absent under not_computable.
        assert "rounding_interval" not in fields
        assert "nearest_achievable" not in fields


# --- grimmer verdicts -----------------------------------------------------

def test_spec_grimmer_case_is_mismatch():
    fields = receipt_lines("grimmer", GRIMMER_FIELDS)
    assert fields["status"] == "mismatch"
    assert "SD = 0.0000" in fields["nearest_achievable"]
    assert "SD = 0.4714" in fields["nearest_achievable"]


def test_grimmer_consistent_sd():
    fields = receipt_lines(
        "grimmer", {**GRIMMER_FIELDS, "reported_sd": "0.47"}
    )
    assert fields["status"] == "consistent"


def test_grimmer_convention_disagreement_is_ambiguous():
    # Sample SD sqrt(2/9)=0.4714 rounds to 0.47; no attainable population
    # SD does.
    fields = receipt_lines("grimmer", {
        **GRIMMER_FIELDS, "reported_sd": "0.47",
        "sd_convention": "unstated",
    })
    assert fields["status"] == "not_computable"
    assert fields["not_computable_reason"] == "sd_convention_unknown"


def test_grimmer_grim_inconsistent_mean_stops_first():
    fields = receipt_lines("grimmer", {
        **GRIMMER_FIELDS, "n": "87", "reported_mean": "3.847",
    })
    assert fields["status"] == "not_computable"
    assert fields["not_computable_reason"] == "mean_grim_inconsistent"


def test_grimmer_budget_exhaustion_is_honest(monkeypatch):
    monkeypatch.setattr(rr, "_STATE_BUDGET", 3)
    fields = receipt_lines("grimmer", {
        **GRIMMER_FIELDS, "n": "40", "reported_mean": "3.00",
        "reported_sd": "0.50",
    })
    assert fields["status"] == "not_computable"
    assert fields["not_computable_reason"] == "reachability_not_completed"


def test_attainable_sumsq_matches_brute_force():
    from itertools import combinations_with_replacement
    n, lo, hi, total = 5, 1, 4, 12
    expected = {
        sum(v * v for v in combo)
        for combo in combinations_with_replacement(range(lo, hi + 1), n)
        if sum(combo) == total
    }
    assert set(rr._attainable_sumsq(n, lo, hi, total)) == expected


# --- n_from_df verdicts ---------------------------------------------------

def test_spec_n_from_df_case_is_mismatch_with_ceiling_argument():
    fields = receipt_lines("n_from_df", N_FROM_DF_FIELDS)
    assert fields["status"] == "mismatch"
    assert fields["derived_value_or_range"] == "implied N = 158"
    assert fields["df_identity"] == "df=N1+N2-2"
    assert "Welch-Satterthwaite" in fields["derivation"]


def test_n_from_df_consistent_equals():
    fields = receipt_lines("n_from_df", {
        "df_reported": "39", "df_identity_candidate": "df=N-1",
        "stated_n": "40", "stated_n_relation": "equals",
    })
    assert fields["status"] == "consistent"
    assert fields["df_identity"] == "df=N-1"


def test_n_from_df_sentinel_mappings():
    for override, reason in (
        ({"df_identity_candidate": "other_or_corrected"},
         "model_correction_or_pooling"),
        ({"df_identity_candidate": "unavailable"}, "df_identity_ambiguous"),
        ({"stated_n": "unavailable"}, "missing_reported_value"),
        ({"stated_n_relation": "unavailable"}, "missing_reported_value"),
    ):
        fields = receipt_lines("n_from_df", {**N_FROM_DF_FIELDS, **override})
        assert fields["status"] == "not_computable"
        assert fields["not_computable_reason"] == reason
        assert "df_identity" not in fields


# --- extraction parsing ---------------------------------------------------

def test_attestation_passes_through_verbatim():
    text = rr.compute_receipts(rr.parse_extraction(build(
        "no_recomputable_statistics: the manuscript reports no test "
        "statistics, means with N, or dfs\n"
    )))
    assert text == (
        "## Arithmetic Receipts\n\n"
        "no_recomputable_statistics: the manuscript reports no test "
        "statistics, means with N, or dfs\n"
    )


def test_decorated_and_fenced_machine_lines_parse():
    body = one_request("n_from_df", N_FROM_DF_FIELDS).replace(
        "procedure_id: n_from_df", "- **procedure_id**: n_from_df"
    ).replace(
        "df_reported: 156", "```\ndf_reported: 156\n```"
    )
    extraction = rr.parse_extraction(body)
    assert extraction.requests[0]["procedure_id"] == "n_from_df"
    assert extraction.requests[0]["df_reported"] == "156"


@pytest.mark.parametrize("mutate,fragment", [
    (lambda t: t.replace("### RR1", "### RR2"), "contiguous"),
    (lambda t: t.replace("procedure_id: grim", "procedure_id: grimm"),
     "procedure_id"),
    (lambda t: t + "bogus_field: value\n", "unknown field"),
    (lambda t: t + "reported_sd: 0.10\n", "do not belong"),
    (lambda t: t + "n: 87\n", "duplicate field"),
    (lambda t: t + "no_recomputable_statistics: nothing\n", "attestation"),
    (lambda t: t.replace("n: 87\n", ""), "missing field n"),
    (lambda t: t.replace("reported_mean: 3.847", "reported_mean: 3,847"),
     "plain decimal"),
    (lambda t: t + "This mean looks impossible to me.\n",
     "not a machine line"),
    (lambda t: t.replace("## Recompute Extraction", "## Something Else"),
     "no ## Recompute Extraction"),
])
def test_extraction_rejections(mutate, fragment):
    with pytest.raises(rr.ExtractionError, match=fragment):
        rr.parse_extraction(mutate(one_request("grim", GRIM_FIELDS)))


def test_empty_section_is_rejected():
    with pytest.raises(rr.ExtractionError, match="neither"):
        rr.parse_extraction(build(""))


# --- grammar compatibility with the #644 receipt gate ---------------------

def full_worked_extraction() -> str:
    parts = ["## Recompute Extraction", ""]
    for index, (procedure, fields) in enumerate((
        ("p_from_test_statistic", P_FIELDS),
        ("grim", GRIM_FIELDS),
        ("grimmer", GRIMMER_FIELDS),
        ("n_from_df", N_FROM_DF_FIELDS),
        ("grim", {**GRIM_FIELDS, "n": "unavailable"}),
    ), start=1):
        parts.append(f"### RR{index}")
        parts.append(f"procedure_id: {procedure}")
        parts.append(
            "evidence_anchor: table: Table 1, reported statistics under test"
        )
        parts.append("reported_inputs: the manuscript values under test")
        parts.append("assumptions: only what the paper licenses")
        parts += [f"{key}: {value}" for key, value in fields.items()]
        parts.append("")
    return "\n".join(parts)


def test_every_emitted_line_parses_under_the_gate_grammar():
    text = rr.compute_receipts(rr.parse_extraction(full_worked_extraction()))
    assert text.startswith("## Arithmetic Receipts\n")
    for line in text.splitlines()[1:]:
        if not line:
            continue
        if line.startswith("### "):
            assert phase._RECEIPT_H3_RE.fullmatch(line[4:]), line
            continue
        matched = [
            key for key, pattern in phase._RECEIPT_FIELD_RES.items()
            if pattern.fullmatch(line)
        ]
        assert len(matched) == 1, line
    # The calculator never links: finding_ref stays the seat's judgment.
    assert "finding_ref:" not in text


def test_emitted_enums_are_gate_enums():
    text = rr.compute_receipts(rr.parse_extraction(full_worked_extraction()))
    for line in text.splitlines():
        if line.startswith("status: "):
            assert line[len("status: "):] in phase._RECEIPT_STATUSES
            assert line[len("status: "):] != "not_applicable"
        if line.startswith("not_computable_reason: "):
            reason = line[len("not_computable_reason: "):]
            assert reason in phase._NOT_COMPUTABLE_REASONS
        if line.startswith("procedure_id: "):
            assert line[len("procedure_id: "):] in phase._RECEIPT_PROCEDURES


def test_determinism_same_bytes_in_same_bytes_out():
    text = full_worked_extraction()
    first = rr.compute_receipts(rr.parse_extraction(text))
    second = rr.compute_receipts(rr.parse_extraction(text))
    assert first == second


# --- CLI ------------------------------------------------------------------

def test_cli_roundtrip(tmp_path):
    extraction = tmp_path / "extraction.md"
    output = tmp_path / "receipts.md"
    extraction.write_text(one_request("grim", GRIM_FIELDS), encoding="utf-8")
    assert rr.main([
        "--extraction", str(extraction), "--output", str(output),
    ]) == 0
    text = output.read_text(encoding="utf-8")
    assert text.startswith("## Arithmetic Receipts\n")
    assert "status: mismatch" in text


def test_cli_rejects_invalid_extraction(tmp_path, capsys):
    extraction = tmp_path / "extraction.md"
    output = tmp_path / "receipts.md"
    extraction.write_text("no section here\n", encoding="utf-8")
    assert rr.main([
        "--extraction", str(extraction), "--output", str(output),
    ]) == 2
    assert not output.exists()
    assert "extraction rejected" in capsys.readouterr().err


# --- dual-track review round 1 hardening ----------------------------------


import math


def test_near_zero_t_keeps_complement_precision():
    # codex P1-1: t=1e-8 at df=1 (Cauchy) has two-tailed p = 1 - 2e-8/pi;
    # a naive 1-x beta argument collapses this to exactly 1.0.
    p = rr.t_tail_two(1e-8, 1)
    assert p < 1.0
    assert (1.0 - p) == pytest.approx(2e-8 / math.pi, rel=1e-6)


def test_near_zero_f_keeps_complement_precision():
    assert rr.f_tail_upper(1e-16, 1, 1) < 1.0


def test_truncation_interval_text_is_truncation_shaped():
    # codex P1-2: sum 5 gives 5/4 = 1.25, which truncates to 1.2; the
    # receipt interval must be [1.2, 1.3), not a half-up shape that
    # excludes the achieving value.
    fields = receipt_lines("grim", {
        "n": "4", "reported_mean": "1.2", "scale_min": "1",
        "scale_max": "5", "rounding_rule": "truncation",
    })
    assert fields["status"] == "consistent"
    assert fields["rounding_interval"].startswith("1.20 <= mean < 1.30")
    assert "truncation" in fields["rounding_interval"]


def test_half_even_interval_text_names_its_tie_rule():
    fields = receipt_lines("grim", {
        "n": "4", "reported_mean": "1.2", "scale_min": "1",
        "scale_max": "5", "rounding_rule": "half-even",
    })
    assert "ties-to-even" in fields["rounding_interval"]


def test_negative_reported_sd_is_a_mismatch():
    # codex P1-3: an SD is nonnegative by definition; clamping only the
    # lower endpoint before squaring inverted the interval and declared a
    # negative SD consistent.
    fields = receipt_lines("grimmer", {
        "n": "2", "reported_mean": "0.5", "scale_min": "0",
        "scale_max": "1", "rounding_rule": "half-up",
        "reported_sd": "-0.8", "sd_convention": "sample",
    })
    assert fields["status"] == "mismatch"


def test_single_response_population_sd_zero_is_consistent():
    # codex P2-1: a population SD is defined (zero) for one response.
    fields = receipt_lines("grimmer", {
        "n": "1", "reported_mean": "3.0", "scale_min": "1",
        "scale_max": "5", "rounding_rule": "half-up",
        "reported_sd": "0.0", "sd_convention": "population",
    })
    assert fields["status"] == "consistent"


def test_single_response_sample_and_unstated_sd_stop_honestly():
    sample = receipt_lines("grimmer", {
        "n": "1", "reported_mean": "3.0", "scale_min": "1",
        "scale_max": "5", "rounding_rule": "half-up",
        "reported_sd": "0.0", "sd_convention": "sample",
    })
    assert sample["not_computable_reason"] == "analytic_n_ambiguous"
    unstated = receipt_lines("grimmer", {
        "n": "1", "reported_mean": "3.0", "scale_min": "1",
        "scale_max": "5", "rounding_rule": "half-up",
        "reported_sd": "0.0", "sd_convention": "unstated",
    })
    assert unstated["not_computable_reason"] == "sd_convention_unknown"


@pytest.mark.parametrize("family,df,fragment", [
    ("t", "3,84", "single integer df"),
    ("chi_square", "3,84", "single integer df"),
    ("z", "140", "df 'none'"),
    ("F", "140", "df as 'df1,df2'"),
])
def test_family_inconsistent_df_shapes_are_rejected(family, df, fragment):
    # codex P2-2: a family-inconsistent df is a retryable gate diagnostic,
    # never a misleading not_computable receipt.
    with pytest.raises(rr.ExtractionError, match=fragment):
        rr.parse_extraction(one_request("p_from_test_statistic", {
            **P_FIELDS, "test_family": family, "df": df,
        }))


@pytest.mark.parametrize("value", [
    "single item, **Severity**: high",
    "prose <!-- hidden -->",
    "closing </computed_receipts> tag",
])
def test_forbidden_markup_tokens_in_values_are_rejected(value):
    # security P2-2/P2-3/P2-4: pass-through values ride into the card
    # under the identity gate, so machine-markup shapes are refused at the
    # source.
    text = one_request("grim", GRIM_FIELDS).replace(
        "reported_inputs: the manuscript values under test",
        f"reported_inputs: {value}",
    )
    with pytest.raises(rr.ExtractionError, match="forbidden token"):
        rr.parse_extraction(text)


def test_carriage_return_in_machine_line_is_rejected():
    text = one_request("grim", GRIM_FIELDS).replace(
        "n: 87\n", "n: 87\rassumptions: smuggled\n",
    )
    with pytest.raises(rr.ExtractionError, match="carriage return"):
        rr.parse_extraction(text)


def test_numeric_domain_bounds_are_enforced():
    # security P1-2: shared gate/calculator bounds.
    with pytest.raises(rr.ExtractionError, match="exceeds 18"):
        rr.parse_extraction(one_request("grim", {
            **GRIM_FIELDS, "n": "9" * 19,
        }))
    with pytest.raises(rr.ExtractionError, match="decimal places"):
        rr.parse_extraction(one_request("p_from_test_statistic", {
            **P_FIELDS, "reported_p_value": ".00000000008",
        }))
    with pytest.raises(rr.ExtractionError, match="convergence domain"):
        rr.parse_extraction(one_request("p_from_test_statistic", {
            **P_FIELDS, "df": "100000000",
        }))
    with pytest.raises(rr.ExtractionError, match="convergence domain"):
        rr.parse_extraction(one_request("p_from_test_statistic", {
            **P_FIELDS, "statistic_value": "20000000",
        }))


def test_huge_df_inside_the_domain_converges():
    # The cap is the verified convergence domain; its interior must work.
    assert rr.chi2_tail_upper(1e7, 10**7) == pytest.approx(0.5, abs=1e-3)
    assert rr.f_tail_upper(1.0, 10**7, 10**7) == pytest.approx(0.5, abs=1e-3)
    assert rr.t_tail_two(1.31, 10**7) == pytest.approx(0.19, abs=1e-2)


def test_grim_window_budget_refuses_honestly():
    # security P1-2: a zero-decimal mean over a huge N would iterate a
    # ~2N-wide candidate window; the budget refuses instead.
    fields = receipt_lines("grim", {
        "n": "10000000", "reported_mean": "3", "scale_min": "1",
        "scale_max": "5", "rounding_rule": "half-up",
    })
    assert fields["status"] == "not_computable"
    assert fields["not_computable_reason"] == "reachability_not_completed"


def test_grimmer_element_budget_refuses_honestly(monkeypatch):
    monkeypatch.setattr(rr, "_ELEMENT_BUDGET", 1)
    fields = receipt_lines("grimmer", {
        **GRIMMER_FIELDS, "n": "12",
    })
    assert fields["status"] == "not_computable"
    assert fields["not_computable_reason"] == "reachability_not_completed"


def test_fence_info_string_with_backtick_is_content_not_a_fence():
    # codex P2-3: a backtick fence's info string may not contain a
    # backtick (CommonMark), so this line is a paragraph — and inside the
    # section a paragraph is a loud abort, never a silent drop.
    text = one_request("grim", GRIM_FIELDS) + "````bad`tick\n"
    with pytest.raises(rr.ExtractionError, match="not a machine line"):
        rr.parse_extraction(text)


def test_stateful_fence_keeps_interior_and_drops_delimiters():
    text = one_request("grim", GRIM_FIELDS).replace(
        "n: 87\n", "```python\nn: 87\n```\n",
    )
    extraction = rr.parse_extraction(text)
    assert extraction.requests[0]["n"] == "87"


def test_receipts_never_carry_crlf(tmp_path):
    # codex P2-5: artifact bytes are pinned LF regardless of platform
    # newline translation defaults.
    extraction = tmp_path / "extraction.md"
    output = tmp_path / "receipts.md"
    extraction.write_text(one_request("grim", GRIM_FIELDS), encoding="utf-8")
    assert rr.main([
        "--extraction", str(extraction), "--output", str(output),
    ]) == 0
    assert b"\r" not in output.read_bytes()


def test_cli_output_is_write_once(tmp_path):
    extraction = tmp_path / "extraction.md"
    output = tmp_path / "receipts.md"
    extraction.write_text(one_request("grim", GRIM_FIELDS), encoding="utf-8")
    output.write_text("already here", encoding="utf-8")
    assert rr.main([
        "--extraction", str(extraction), "--output", str(output),
    ]) == 2
    assert output.read_text(encoding="utf-8") == "already here"


# --- dual-track review round 2 hardening ----------------------------------


def test_ten_decimal_places_are_in_domain():
    # codex round 2 NEW P1: `.0000008` is a legal printed p and must be
    # transcribable; ultra-fine comparisons degrade to the boundary guard,
    # never to an unsatisfiable gate rejection.
    fields = receipt_lines("p_from_test_statistic", {
        **P_FIELDS, "reported_p_value": ".0000008",
    })
    assert fields["status"] == "mismatch"  # .192/.096 vs 8e-7


def test_near_one_p_displays_below_one():
    # codex round 2 NEW P2: the displayed value must sit on the same side
    # of 1 as the compared one.
    fields = receipt_lines("p_from_test_statistic", {
        "test_family": "t", "statistic_value": ".00000001", "df": "1",
        "reported_p_comparator": "less_than", "reported_p_value": "1",
        "tail_convention": "two-tailed",
    })
    assert fields["status"] == "consistent"
    assert "p = 1 (" not in fields["derived_value_or_range"]
    assert "0.99999999" in fields["derived_value_or_range"]


def test_half_even_interval_endpoints_follow_target_parity():
    # codex round 2: an odd target owns neither tie endpoint; an even one
    # owns both.
    odd = receipt_lines("grim", {
        "n": "4", "reported_mean": "1.3", "scale_min": "1",
        "scale_max": "5", "rounding_rule": "half-even",
    })
    assert odd["rounding_interval"].startswith("1.25 < mean < 1.35")
    even = receipt_lines("grim", {
        "n": "4", "reported_mean": "1.2", "scale_min": "1",
        "scale_max": "5", "rounding_rule": "half-even",
    })
    assert even["rounding_interval"].startswith("1.15 <= mean <= 1.25")


def test_truncation_interval_at_zero_covers_both_sides():
    fields = receipt_lines("grim", {
        "n": "4", "reported_mean": "0", "scale_min": "-2",
        "scale_max": "2", "rounding_rule": "truncation",
    })
    assert fields["rounding_interval"].startswith("-1.0 < mean < 1.0")


def test_work_budget_bounds_infeasible_spinning(monkeypatch):
    # security round 2 NEW-2: iterations are bounded, not just retained
    # states.
    monkeypatch.setattr(rr, "_WORK_BUDGET", 5)
    fields = receipt_lines("grimmer", {**GRIMMER_FIELDS, "n": "30"})
    assert fields["not_computable_reason"] == "reachability_not_completed"


def test_tail_functions_terminate_at_domain_corners():
    # security round 2 NEW-3: the declared 1e7 convergence domain, swept at
    # its corners — termination and range, not reference values.
    corners = [
        rr.t_tail_two(1e7, 10**7), rr.t_tail_two(1e7, 1),
        rr.t_tail_two(1e-7, 10**7),
        rr.z_tail_two(1e7), rr.z_tail_two(1e-7),
        rr.chi2_tail_upper(1e7, 10**7), rr.chi2_tail_upper(1e-7, 10**7),
        rr.chi2_tail_upper(1e7, 1),
        rr.f_tail_upper(1e7, 10**7, 10**7), rr.f_tail_upper(1e7, 1, 1),
        rr.f_tail_upper(1e-7, 10**7, 10**7), rr.f_tail_upper(1e-7, 1, 1),
    ]
    for value in corners:
        assert 0.0 <= value <= 1.0
