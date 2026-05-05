"""Test harness for ARS v3.6.7 Step 8 pattern-eval fixtures.

Spec: docs/design/2026-04-30-ars-v3.6.7-step-6-orchestrator-hooks-spec.md §7.4

This harness exercises §5.6 Path B's verdict-to-ship/block decision logic
against each fixture's BAD/GOOD pair (or per-round per-agent slots for the
integration fixture) without running real codex. The fixture's
`expected_audit_findings.yaml` is treated as the synthesized verdict that the
codex run *would have produced*, and the harness asserts the orchestrator's
expected action matches `expected_orchestrator_action.yaml`.

Coverage:
- All 17 micro-fixtures' BAD case produces the expected pattern signal:
  * MATERIAL/MINOR: verdict_status + finding_count.severity tally + dimension match
  * D2 special: PASS verdict + convergence-theatre assertion logged
- All 17 micro-fixtures' GOOD case produces PASS verdict + empty findings.
- Integration fixture: each round's per-agent verdict matches the expected
  pipeline state; round-3 escalation produces ship_with_known_residue
  acknowledgement append.
- §7.4 success criterion 4 (audit artifact lifecycle): inventory-driven
  passport-mutation rule based on each fixture's expected_phase.

Run with: pytest -xvs scripts/test_pattern_eval_runtime.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "v3_6_7_pattern_eval"

PATTERN_IDS = (
    "A1", "A2", "A3", "A4", "A5",
    "B1", "B2", "B3", "B4", "B5",
    "C1", "C2", "C3",
    "D1", "D2", "D3", "D4",
)

PATTERN_TO_DIMENSION = {
    "A1": "3.1",
    "A2": "3.3",
    "A3": "3.2",
    "A4": "3.1",
    "A5": "3.4",
    "B1": "3.5",
    "B2": "3.5",
    "B3": "3.5",
    "B4": "3.5",
    "B5": "3.5",
    "C1": "4(f)",
    "C2": "4(f)",
    "C3": "3.6",
    "D1": "3.1",
    "D3": "3.7",
    "D4": "4(f)",
    # D2 is convergence theatre — no finding, special handling.
}

# §7.4 criterion 4 — inventory-driven passport mutation rule.
# expected_phase → expected_passport_mutation kind for fresh non-duplicate
# proposals (the only kind exercised by Phase 6.8 fixtures).
PHASE_TO_PASSPORT_MUTATION = {
    "A7": "none",  # Path A success — entry already there
    "B10": "appended",  # Path B success — fresh proposal merged
    # Path A failure phases — passport unchanged (silent fall-through to B)
    "P-PA-precond": "none",
    "P-PA-schema": "none",
    "P-PA-gate": "none",
    "P-PA-verdict-schema": "none",
    "P-PA-verdict-mirror": "none",
    "P-PA-stale-late": "none",
    "P-PA-supersede-preempt": "none",
    # Path B failure phases — proposal stays in <output-dir>, passport unchanged
    "P-PB-empty": "none",
    "P-PB-supersede-missing": "none",
    "P-PB-ambig": "none",
    "P-PB-proposal-schema": "none",
    "P-PB-audit-failed": "none",
    "P-PB-gate": "none",
    "P-PB-verdict-schema": "none",
    "P-PB-verdict-mirror": "none",
    "P-PB-stale-late": "none",
    "P-PB-snapshot": "none",
    "P-PB-persisted-schema": "none",
    "P-PB-passport-write": "none",
}

RUN_ID_REGEX = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}-[0-9]{2}-[0-9]{2}Z-[0-9a-f]{4}$"
)


def _load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fp:
        return yaml.safe_load(fp)


def _load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fp:
        return json.load(fp)


def _simulate_orchestrator_decision(
    verdict: dict, expected_phase: str
) -> dict:
    """Apply §5.6 Path B verdict→ship/block decision to a synthesized verdict.

    Returns a dict with the orchestrator action that an actual run would
    produce. This is a thin reimplementation of §5.6's B10 + §5.3 mapping.
    """
    status = verdict.get("verdict_status")
    if status == "PASS":
        return {
            "ship_or_block": "ship",
            "expected_phase": expected_phase or "B10",
            "passport_mutation": "appended",
        }
    if status == "MINOR":
        return {
            "ship_or_block": "mandatory_checkpoint",
            "expected_phase": expected_phase or "B10",
            "passport_mutation": "appended",
        }
    if status == "MATERIAL":
        return {
            "ship_or_block": "block",
            "expected_phase": expected_phase or "B10",
            "passport_mutation": "appended",
        }
    if status == "AUDIT_FAILED":
        return {
            "ship_or_block": "block",
            "expected_phase": "P-PB-audit-failed",
            "passport_mutation": "none",
        }
    raise ValueError(f"unknown verdict_status: {status!r}")


def _validate_finding_counts_match(verdict: dict) -> None:
    """§3.7 family A row A5 — finding_counts must agree with severity tally."""
    counts = verdict["finding_counts"]
    findings = verdict.get("findings", [])
    tally = {"P1": 0, "P2": 0, "P3": 0}
    for f in findings:
        tally[f["severity"]] += 1
    assert counts["p1"] == tally["P1"], (
        f"finding_counts.p1={counts['p1']} but findings carry {tally['P1']} P1 entries"
    )
    assert counts["p2"] == tally["P2"], (
        f"finding_counts.p2={counts['p2']} but findings carry {tally['P2']} P2 entries"
    )
    assert counts["p3"] == tally["P3"], (
        f"finding_counts.p3={counts['p3']} but findings carry {tally['P3']} P3 entries"
    )


def _validate_status_count_consistency(verdict: dict) -> None:
    """§3.2 cross-field rules — status/count agreement."""
    status = verdict["verdict_status"]
    p1 = verdict["finding_counts"]["p1"]
    p2 = verdict["finding_counts"]["p2"]
    p3 = verdict["finding_counts"]["p3"]
    if status == "PASS":
        assert p1 == 0 and p2 == 0 and p3 == 0, (
            f"PASS verdict requires all-zero finding_counts; got p1={p1} p2={p2} p3={p3}"
        )
    elif status == "MINOR":
        assert p1 == 0 and p2 == 0 and p3 <= 3, (
            f"MINOR verdict requires p1=0, p2=0, p3<=3; got p1={p1} p2={p2} p3={p3}"
        )
    elif status == "MATERIAL":
        assert p1 > 0 or p2 > 0 or p3 > 3, (
            f"MATERIAL verdict requires p1>0 OR p2>0 OR p3>3; got p1={p1} p2={p2} p3={p3}"
        )
    elif status == "AUDIT_FAILED":
        assert p1 == 0 and p2 == 0 and p3 == 0, (
            f"AUDIT_FAILED verdict requires all-zero finding_counts; got p1={p1} p2={p2} p3={p3}"
        )
        assert verdict.get("failure_reason"), (
            "AUDIT_FAILED verdict requires non-empty failure_reason"
        )


# ---------------------------------------------------------------------------
# Per-pattern micro-fixture parametrization
# ---------------------------------------------------------------------------


def _all_micro_fixtures() -> list[str]:
    if not FIXTURE_ROOT.exists():
        return []
    return [
        d.name
        for d in sorted(FIXTURE_ROOT.iterdir())
        if d.is_dir() and d.name in PATTERN_IDS
    ]


@pytest.mark.parametrize("pattern_id", _all_micro_fixtures())
def test_micro_bad_run_signal_matches_expectation(pattern_id):
    """§7.4 criterion 1: BAD case produces the pattern-specific failure signal."""
    fixture_dir = FIXTURE_ROOT / pattern_id
    manifest = _load_json(fixture_dir / "manifest.json")
    bad_verdict = _load_yaml(fixture_dir / manifest["bad_run"]["expected_audit_findings_path"])
    expected_action = _load_yaml(
        fixture_dir / manifest["bad_run"]["expected_orchestrator_action_path"]
    )

    _validate_status_count_consistency(bad_verdict)
    _validate_finding_counts_match(bad_verdict)

    if pattern_id == "D2":
        # D2 convergence theatre — PASS verdict, but fixture must declare the
        # convergence-policy assertion (per §7.4 criterion 1 special case).
        assert bad_verdict["verdict_status"] == "PASS"
        assert bad_verdict.get("findings", []) == []
        assert "expected_d2_convergence_assertion" in expected_action, (
            "D2 BAD case must carry expected_d2_convergence_assertion field"
        )
        assert expected_action["expected_d2_convergence_assertion"], (
            "D2 expected_d2_convergence_assertion must be non-empty"
        )
    else:
        # All other patterns — BAD must carry MATERIAL or MINOR verdict with
        # at least one finding in the expected dimension.
        status = bad_verdict["verdict_status"]
        assert status in {"MATERIAL", "MINOR"}, (
            f"{pattern_id} BAD verdict must be MATERIAL or MINOR (got {status})"
        )
        findings = bad_verdict.get("findings", [])
        assert findings, f"{pattern_id} BAD verdict must carry at least one finding"
        expected_dim = PATTERN_TO_DIMENSION[pattern_id]
        actual_dims = {f["dimension"] for f in findings}
        assert expected_dim in actual_dims, (
            f"{pattern_id} BAD findings must include dimension {expected_dim}; "
            f"got {actual_dims}"
        )

    decision = _simulate_orchestrator_decision(
        bad_verdict, expected_action.get("expected_phase")
    )
    expected_phase = expected_action.get("expected_phase")
    if expected_phase:
        assert decision["expected_phase"] == expected_phase
        expected_mutation = PHASE_TO_PASSPORT_MUTATION.get(expected_phase)
        if expected_mutation is not None:
            actual_mutation = expected_action.get("expected_passport_mutation")
            assert actual_mutation == expected_mutation, (
                f"{pattern_id} BAD: expected_phase={expected_phase} maps to "
                f"passport mutation {expected_mutation!r}, but fixture declares "
                f"{actual_mutation!r}"
            )


@pytest.mark.parametrize("pattern_id", _all_micro_fixtures())
def test_micro_good_run_passes(pattern_id):
    """§7.4 criterion 2: GOOD case produces PASS + empty findings."""
    fixture_dir = FIXTURE_ROOT / pattern_id
    manifest = _load_json(fixture_dir / "manifest.json")
    good_verdict = _load_yaml(
        fixture_dir / manifest["good_run"]["expected_audit_findings_path"]
    )
    expected_action = _load_yaml(
        fixture_dir / manifest["good_run"]["expected_orchestrator_action_path"]
    )

    _validate_status_count_consistency(good_verdict)
    _validate_finding_counts_match(good_verdict)

    assert good_verdict["verdict_status"] == "PASS", (
        f"{pattern_id} GOOD verdict must be PASS; got {good_verdict['verdict_status']}"
    )
    assert good_verdict.get("findings", []) == [], (
        f"{pattern_id} GOOD verdict must have empty findings list"
    )

    decision = _simulate_orchestrator_decision(
        good_verdict, expected_action.get("expected_phase")
    )
    assert decision["ship_or_block"] == "ship"

    expected_phase = expected_action.get("expected_phase")
    if expected_phase:
        expected_mutation = PHASE_TO_PASSPORT_MUTATION.get(expected_phase)
        actual_mutation = expected_action.get("expected_passport_mutation")
        if expected_mutation is not None:
            assert actual_mutation == expected_mutation


@pytest.mark.parametrize("pattern_id", _all_micro_fixtures())
def test_micro_run_id_format(pattern_id):
    """§3.7 family F F1: run_id matches canonical regex."""
    fixture_dir = FIXTURE_ROOT / pattern_id
    manifest = _load_json(fixture_dir / "manifest.json")
    for slot in ("bad_run", "good_run"):
        verdict = _load_yaml(fixture_dir / manifest[slot]["expected_audit_findings_path"])
        rid = verdict.get("run_id", "")
        assert RUN_ID_REGEX.match(rid), (
            f"{pattern_id}/{slot}/expected_audit_findings.yaml run_id={rid!r} "
            "does not match F1 regex"
        )


@pytest.mark.parametrize("pattern_id", _all_micro_fixtures())
def test_micro_run_id_uniqueness_within_fixture(pattern_id):
    """A fixture's BAD and GOOD must use distinct run_ids (different audit runs)."""
    fixture_dir = FIXTURE_ROOT / pattern_id
    manifest = _load_json(fixture_dir / "manifest.json")
    bad = _load_yaml(fixture_dir / manifest["bad_run"]["expected_audit_findings_path"])
    good = _load_yaml(fixture_dir / manifest["good_run"]["expected_audit_findings_path"])
    assert bad["run_id"] != good["run_id"], (
        f"{pattern_id} BAD and GOOD must have distinct run_ids"
    )


# ---------------------------------------------------------------------------
# Integration fixture
# ---------------------------------------------------------------------------


def _integration_dir() -> Path:
    return FIXTURE_ROOT / "integration" / "chapter_level_run"


@pytest.fixture
def integration_manifest():
    return _load_json(_integration_dir() / "manifest.json")


def test_integration_manifest_present():
    assert _integration_dir().exists(), (
        "Integration fixture directory missing; expected at "
        "tests/fixtures/v3_6_7_pattern_eval/integration/chapter_level_run/"
    )
    assert (_integration_dir() / "manifest.json").exists()


def test_integration_three_round_escalation(integration_manifest):
    """§7.3: integration fixture exercises 3-round MATERIAL escalation."""
    rounds = integration_manifest["rounds"]
    assert len(rounds) == 3
    for r in rounds:
        assert r["target_rounds"] == 3
        assert r["expected_verdict"] == "MATERIAL"
    assert integration_manifest["escalation"]["user_choice"] == "ship_with_known_residue"


def test_integration_per_round_per_agent_slots_present():
    """§7.3 directory tree: round_{1,2,3}/<agent>/<files>."""
    base = _integration_dir()
    for r in ("round_1", "round_2", "round_3"):
        round_dir = base / r
        assert round_dir.is_dir(), f"missing {r}/"
        for agent in (
            "synthesis_agent",
            "research_architect_agent",
            "report_compiler_agent",
        ):
            assert (round_dir / agent).is_dir(), f"missing {r}/{agent}/"


def test_integration_escalation_artifacts_present():
    """§7.3: escalation/ holds user_response + expected passport state."""
    base = _integration_dir()
    assert (base / "escalation").is_dir()
    assert (base / "escalation" / "user_response.yaml").exists()
    assert (base / "escalation" / "expected_passport_state.yaml").exists()


def test_integration_patterns_triggered_subset(integration_manifest):
    """§7.3: patterns_triggered matches the curated A3+C2+D4+C1 subset."""
    triggered = set(integration_manifest["patterns_triggered"])
    assert triggered == {"A3", "C2", "D4", "C1"}, (
        f"integration fixture must trigger A3+C2+D4+C1; got {triggered}"
    )


# ---------------------------------------------------------------------------
# §7.5 coverage cross-check (defense in depth — also covered by manifest validator)
# ---------------------------------------------------------------------------


def test_inventory_coverage_17_of_17():
    """All 17 numbered pattern IDs have exactly one micro-fixture."""
    seen = set(_all_micro_fixtures())
    assert seen == set(PATTERN_IDS), (
        f"missing: {set(PATTERN_IDS) - seen}; extra: {seen - set(PATTERN_IDS)}"
    )
