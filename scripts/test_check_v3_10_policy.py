"""Tests for the v3.10 policy-layer lint (#127 PR-B).

Two halves:
  A. Marker-grammar parser fixtures (spec §3 PR-B item 6): terminal co-emit /
     non-terminal advisory / non-terminal clean / legacy-no-stamp /
     bare-prose-HIGH-BLOCK-does-not-refuse.
  B. Lint mutation tests: each rule fails when the contract is violated, so the
     lint is not trivially-passing (feedback_schema_mutation_test_for_constraints).
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.check_v3_10_policy import (
    parse_ref_marker,
    marker_triggers_refusal,
    any_marker_triggers_refusal,
    assert_venue_type_source_clean,
    check_entry_schema,
    check_terminal_policies_schema,
    check_finalizer_prompt,
    check_formatter_prompt,
    DEFAULT_ENTRY_SCHEMA,
    DEFAULT_TP_SCHEMA,
    DEFAULT_FORMATTER,
    DEFAULT_ORCHESTRATOR,
)


# ===========================================================================
# A. Marker-grammar parser fixtures (spec §3 PR-B item 6)
# ===========================================================================

def test_marker_terminal_co_emit_parses_and_refuses():
    """The canonical co-emitted form: advisory suffix in its slot AND a terminal
    block token, parseable and refusing."""
    marker = ("<!--ref:smith2024 ok CONTAMINATED-PREPRINT+TRIANGULATION-UNMATCHED "
              "TERMINAL-BLOCK severity=HIGH-BLOCK policy=contamination_triangulation "
              "reason=k3_all_indexes_unmatched mode=strict "
              "policy_hash=contamination_triangulation.strict-->")
    pm = parse_ref_marker(marker)
    assert pm is not None
    assert pm.slug == "smith2024"
    assert pm.base_status == "ok"
    assert pm.advisory_suffix == "CONTAMINATED-PREPRINT+TRIANGULATION-UNMATCHED"
    assert pm.terminal is True
    assert pm.is_high_block is True
    assert pm.policy == "contamination_triangulation"
    assert pm.reason == "k3_all_indexes_unmatched"
    assert pm.mode == "strict"
    assert pm.policy_hash == "contamination_triangulation.strict"
    assert pm.is_legacy is False
    assert marker_triggers_refusal(marker) is True


def test_marker_terminal_without_advisory_suffix_parses():
    """A terminal marker need not carry an advisory suffix."""
    marker = ("<!--ref:smith2024 ok TERMINAL-BLOCK severity=HIGH-BLOCK "
              "policy=contamination_triangulation reason=k3_all_indexes_unmatched "
              "mode=strict_articles_only policy_hash=contamination_triangulation.strict_articles_only-->")
    pm = parse_ref_marker(marker)
    assert pm.advisory_suffix is None
    assert pm.terminal is True
    assert pm.mode == "strict_articles_only"
    assert marker_triggers_refusal(marker) is True


def test_marker_non_terminal_advisory_parses_no_refuse():
    """A non-terminal advisory marker under a NON-advisory passport: advisory suffix
    + a non-advisory policy_hash slug, NO terminal token → does not refuse. (Under an
    all-advisory passport the marker would be stampless — see the legacy test.)"""
    marker = ("<!--ref:smith2024 LOW-WARN CONTAMINATED-TRIANGULATION-UNMATCHED "
              "policy_hash=contamination_triangulation.strict-->")
    pm = parse_ref_marker(marker)
    assert pm.advisory_suffix == "CONTAMINATED-TRIANGULATION-UNMATCHED"
    assert pm.terminal is False
    assert pm.is_high_block is False
    assert pm.policy_hash == "contamination_triangulation.strict"
    assert pm.is_legacy is False
    assert marker_triggers_refusal(marker) is False


def test_marker_non_terminal_clean_parses_no_refuse():
    """A clean non-terminal marker under a non-advisory passport: base status +
    a non-advisory policy_hash slug, no suffix."""
    marker = "<!--ref:smith2024 ok policy_hash=contamination_triangulation.strict-->"
    pm = parse_ref_marker(marker)
    assert pm.base_status == "ok"
    assert pm.advisory_suffix is None
    assert pm.terminal is False
    assert pm.policy_hash == "contamination_triangulation.strict"
    assert marker_triggers_refusal(marker) is False


def test_marker_legacy_no_stamp_recognized():
    """A legacy v3.9.0 marker carries NO policy_hash and NO terminal token —
    it is version-distinguished, not malformed."""
    marker = "<!--ref:smith2024 LOW-WARN CONTAMINATED-TRIANGULATION-UNMATCHED-->"
    pm = parse_ref_marker(marker)
    assert pm.policy_hash is None
    assert pm.terminal is False
    assert pm.is_legacy is True
    assert marker_triggers_refusal(marker) is False


def test_bare_prose_high_block_does_not_refuse():
    """A HIGH-BLOCK token in plain prose, outside any <!--ref:...-->, MUST NOT
    trigger a refusal (anti-false-refuse, Invariant 12)."""
    prose = "The reviewer wrote: this section is a HIGH-BLOCK risk for the argument."
    assert parse_ref_marker(prose) is None
    assert marker_triggers_refusal(prose) is False


def test_stripped_stamp_but_high_block_still_refuses():
    """R4-P1 bypass guard: a marker whose policy_hash was stripped but that still
    carries a TERMINAL-BLOCK severity=HIGH-BLOCK token must still be detected as a
    refusal trigger (gate 2 applies regardless of gate-1 outcome)."""
    marker = ("<!--ref:smith2024 ok TERMINAL-BLOCK severity=HIGH-BLOCK "
              "policy=contamination_triangulation reason=k3_all_indexes_unmatched mode=strict-->")
    pm = parse_ref_marker(marker)
    assert pm.policy_hash is None  # stamp stripped
    assert pm.is_high_block is True
    assert marker_triggers_refusal(marker) is True


# --- marker well-formedness (codex P1: a marker with no base-status is malformed) ---

def test_marker_without_base_status_is_malformed():
    """A marker lacking a base-status (ok / LOW-WARN) is malformed — the v3.7.3
    5-cell resolution always produces one. It still parses (so a lint can flag it)
    but is_well_formed is False."""
    pm = parse_ref_marker("<!--ref:smith2024 policy_hash=contamination_triangulation.strict-->")
    assert pm is not None
    assert pm.base_status is None
    assert pm.is_well_formed is False


def test_marker_with_unknown_residual_token_is_malformed():
    pm = parse_ref_marker(
        "<!--ref:smith2024 ok bogus_token policy_hash=contamination_triangulation.strict-->"
    )
    assert pm.unknown_tokens == ["bogus_token"]
    assert pm.is_well_formed is False


def test_terminal_marker_without_high_block_is_malformed():
    pm = parse_ref_marker("<!--ref:smith2024 ok TERMINAL-BLOCK policy_hash=x-->")
    assert pm.terminal is True
    assert pm.severity is None
    assert pm.is_well_formed is False


def test_well_formed_markers_pass():
    assert parse_ref_marker("<!--ref:smith2024 ok policy_hash=contamination_triangulation.strict-->").is_well_formed
    assert parse_ref_marker("<!--ref:smith2024 LOW-WARN-->").is_well_formed  # legacy, no stamp


# --- any_marker_triggers_refusal scans ALL markers (codex P1) ---

def test_any_marker_refusal_catches_later_terminal_marker():
    """A clean first marker followed by a terminal marker still refuses — the
    single-marker helper would miss the second one."""
    doc = (
        "Some prose. <!--ref:a ok policy_hash=contamination_triangulation.strict--> more prose. "
        "<!--ref:b ok TERMINAL-BLOCK severity=HIGH-BLOCK policy=contamination_triangulation "
        "reason=k3_all_indexes_unmatched mode=strict policy_hash=contamination_triangulation.strict-->"
    )
    # The single-marker helper only sees the first (clean) marker → False.
    assert marker_triggers_refusal(doc) is False
    # The whole-document scan catches the later terminal marker → True.
    assert any_marker_triggers_refusal(doc) is True


def test_any_marker_refusal_false_when_all_clean():
    doc = "<!--ref:a ok--> text <!--ref:b LOW-WARN CONTAMINATED-PREPRINT-->"
    assert any_marker_triggers_refusal(doc) is False


# ===========================================================================
# A'. Laundering guard semantic check (rule 4)
# ===========================================================================

def test_laundering_guard_rejects_lookup_index_source():
    for bad in ["OpenAlex", "crossref registry", "Semantic Scholar", "semantic_scholar"]:
        problems = assert_venue_type_source_clean(bad, "trusted_source_declared")
        assert problems, f"{bad!r} should be rejected as a laundered source"


def test_laundering_guard_rejects_empty_source():
    assert assert_venue_type_source_clean("", "trusted_source_declared")
    assert assert_venue_type_source_clean("   ", "trusted_source_declared")


def test_laundering_guard_accepts_legitimate_source():
    assert assert_venue_type_source_clean("publisher metadata feed", "trusted_source_declared") == []


def test_laundering_guard_inert_for_non_trusted_provenance():
    # When provenance isn't trusted_source_declared, the source field isn't checked.
    assert assert_venue_type_source_clean("OpenAlex", "adapter_declared") == []


def test_laundering_guard_word_boundary_no_false_positive():
    """codex P2: word-boundary matching must NOT flag a legitimate source that
    merely CONTAINS a lookup-index name as a substring."""
    for ok in [
        "OpenAlexandria University Press",
        "crossreference publisher feed",
        "Semantic Scholarship Quarterly (a real journal)",
    ]:
        assert assert_venue_type_source_clean(ok, "trusted_source_declared") == [], (
            f"{ok!r} should pass — the index name only appears as a substring"
        )
    # But the real index names (with separators) are still caught.
    assert assert_venue_type_source_clean("the OpenAlex API", "trusted_source_declared")
    assert assert_venue_type_source_clean("Semantic-Scholar record", "trusted_source_declared")


# ===========================================================================
# B. Lint passes on the real repo
# ===========================================================================

def test_lint_passes_on_real_files():
    entry_schema = json.loads(DEFAULT_ENTRY_SCHEMA.read_text())
    tp_schema = json.loads(DEFAULT_TP_SCHEMA.read_text())
    orchestrator = DEFAULT_ORCHESTRATOR.read_text()
    formatter = DEFAULT_FORMATTER.read_text()
    assert check_entry_schema(entry_schema) == []
    assert check_terminal_policies_schema(tp_schema) == []
    assert check_finalizer_prompt(orchestrator) == []
    assert check_formatter_prompt(formatter) == []


# ===========================================================================
# B'. Lint mutation tests — each rule fails when violated (not trivially-passing)
# ===========================================================================

@pytest.fixture()
def entry_schema():
    return json.loads(DEFAULT_ENTRY_SCHEMA.read_text())


@pytest.fixture()
def tp_schema():
    return json.loads(DEFAULT_TP_SCHEMA.read_text())


def test_mutation_inferred_provenance_fails(entry_schema):
    entry_schema["properties"]["venue_type_provenance"]["enum"].append("openalex_inferred")
    fails = check_entry_schema(entry_schema)
    assert any("openalex_inferred" in f for f in fails)


def test_mutation_terminal_policies_in_entry_schema_fails(entry_schema):
    entry_schema["properties"]["terminal_policies"] = {"type": "object"}
    fails = check_entry_schema(entry_schema)
    assert any("terminal_policies MUST NOT appear" in f for f in fails)


def test_mutation_missing_unknown_member_fails(entry_schema):
    entry_schema["properties"]["venue_type"]["enum"].remove("unknown")
    fails = check_entry_schema(entry_schema)
    assert any("unknown" in f for f in fails)


def test_mutation_dropping_pair_branch_fails(entry_schema):
    # Remove the trusted_source-required branch.
    entry_schema["allOf"] = [
        b for b in entry_schema["allOf"]
        if not (isinstance(b, dict) and "trusted_source_declared" in b.get("description", ""))
    ]
    fails = check_entry_schema(entry_schema)
    assert any("trusted_source required" in f for f in fails)


def test_mutation_temporal_strict_accepted_fails(tp_schema):
    tp_schema["properties"]["temporal_integrity"]["enum"].append("strict")
    fails = check_terminal_policies_schema(tp_schema)
    assert any("temporal_integrity must accept ONLY 'advisory'" in f for f in fails)


def test_mutation_contamination_enum_drift_fails(tp_schema):
    tp_schema["properties"]["contamination_triangulation"]["enum"].append("HIGH-BLOCK")
    fails = check_terminal_policies_schema(tp_schema)
    assert any("contamination_triangulation enum mismatch" in f for f in fails)


def test_mutation_strict_articles_only_missing_by_design_fn_fails():
    """If the strict_articles_only by-design false-negative disclosure is dropped,
    the lint must fail (§4.4 recall-limit protection — a future edit cannot silently
    widen strict_articles_only into all-journal hard-block)."""
    text = ("## Cite-Time Provenance Finalizer — v3.10 extension\n\n"
            "TERMINAL-BLOCK severity=HIGH-BLOCK policy_hash, sole policy evaluator, "
            "MUST NOT infer venue_type from index fields.\n\n"
            "strict_articles_only requires DOI present AND venue_type in "
            "{journal-article, conference-paper}.\n\n## Next")
    # by-design FN disclosure is absent → must fail rule 8.
    fails = check_finalizer_prompt(text)
    assert any("by-design false-negative" in f or "STAYS ADVISORY" in f for f in fails)


def test_mutation_finalizer_missing_terminal_block_fails():
    text = "## Cite-Time Provenance Finalizer — v3.10 extension\n\nNo terminal token here. policy_hash present, sole policy evaluator, severity=HIGH-BLOCK, MUST NOT infer venue_type from index fields.\n\n## Next"
    text = text.replace("severity=HIGH-BLOCK", "").replace("TERMINAL-BLOCK", "")
    fails = check_finalizer_prompt(text)
    assert any("TERMINAL-BLOCK" in f or "severity=HIGH-BLOCK" in f for f in fails)


def test_mutation_formatter_missing_stamp_only_fails():
    text = ("## Cite-Time Terminal Policy Gate (v3.10)\n\n"
            "Gate 1 freshness, Gate 2 refusal, STALE-POLICY-EVALUATION, severity=HIGH-BLOCK, "
            "in plain prose.\n\n## Next")
    # Missing STAMP-ONLY + MUST NOT re-evaluate → should fail.
    fails = check_formatter_prompt(text)
    assert any("STAMP-ONLY" in f or "MUST NOT re-evaluate" in f for f in fails)


# --- v3.11 / C-V6 citation_existence lint mutations ---

def test_mutation_citation_existence_enum_drift_fails(tp_schema):
    """Rule 9 (C-V6): if citation_existence accepts strict_articles_only (or any
    member outside {advisory, strict}), the lint must fail."""
    tp_schema["properties"]["citation_existence"]["enum"].append("strict_articles_only")
    fails = check_terminal_policies_schema(tp_schema)
    assert any("citation_existence enum mismatch" in f for f in fails)


def test_mutation_citation_existence_json_schema_default_fails(tp_schema):
    """Rule 9 (C-V6): a JSON-Schema `default` on citation_existence is non-operational
    false safety — the lint must reject it."""
    tp_schema["properties"]["citation_existence"]["default"] = "advisory"
    fails = check_terminal_policies_schema(tp_schema)
    assert any("citation_existence MUST NOT carry a JSON-Schema `default`" in f for f in fails)


def test_mutation_finalizer_missing_citation_existence_token_fails():
    """Rule 9 (C-V6): if the finalizer section drops the citation_existence terminal
    token grammar, the lint must fail (the writer/grammar pin)."""
    text = ("## Cite-Time Provenance Finalizer — v3.10 extension\n\n"
            "TERMINAL-BLOCK severity=HIGH-BLOCK policy_hash present, sole policy "
            "evaluator, MUST NOT infer venue_type from index fields. Recompute each "
            "pass.\n\n## Next")
    # citation_existence terminal token + reason absent → must fail rule 9.
    fails = check_finalizer_prompt(text)
    assert any("policy=citation_existence" in f or "reason=lookup_verified_false" in f
               for f in fails)


def test_mutation_finalizer_citation_existence_without_recompute_fails():
    """Rule 9 (C-V6(h)): a finalizer that documents citation_existence but drops the
    recompute-each-pass / no-cache property must fail."""
    text = ("## Cite-Time Provenance Finalizer — v3.10 extension\n\n"
            "TERMINAL-BLOCK severity=HIGH-BLOCK policy=citation_existence "
            "reason=lookup_verified_false policy_hash present, sole policy evaluator, "
            "MUST NOT infer venue_type from index fields.\n\n## Next")
    # citation_existence present but no "Recompute each pass" → must fail rule 9(h).
    fails = check_finalizer_prompt(text)
    assert any("recompute-each-pass" in f for f in fails)
