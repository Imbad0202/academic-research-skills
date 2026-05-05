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
    # Anchored in shared/templates/codex_audit_multifile_template.md §3 "Patterns
    # surfaced" lines per dimension. Brief drift in earlier draft was caught by
    # codex review round 1 F-002.
    "A1": "3.4",  # legal-effect drift / cross-section coherence
    "A2": "3.2",  # pending-source assumed as fact / hallucination
    "A3": "3.1",  # mis-anchored citation / cross-reference integrity
    "A4": "3.3",  # quote scope creep / primary-source integrity
    "A5": "3.2",  # sibling-document fabrication / hallucination
    "B1": "3.5",  # IRB terminology
    "B2": "3.5",  # pseudo-reverse-coded
    "B3": "3.5",  # event-anchor missing
    "B4": "3.5",  # leading items
    "B5": "3.1",  # primary-source list mismatch — audit template §3.1 explicitly lists B5 (line 76); §3.5 enumerates B1-B4 only (line 100)
    "C1": "4(f)",  # compression overclaim — 4(f) sub-check (ii) protected hedge
    "C2": "3.7",  # temporal ambiguity / COI disclosure
    "C3": "3.2",  # output metadata audit-passed claim / hallucination
    "D1": "3.4",  # multi-file deliverable cross-file inconsistency / coherence
    "D3": "3.6",  # PARTIAL ≠ CLOSED / round framing
    "D4": "4(f)",  # word-count cap bust — 4(f) sub-check (i)
    # D2 is convergence theatre — no finding, special handling.
}

# §7.4 criterion 4 — inventory-driven passport mutation rule.
# Mirrors the §5.6 verification failure state inventory (24 rows: 7 P-PA-* + 17 P-PB-*)
# plus the two happy-path phases (A7, B10). When §5.6's inventory grows in v3.6.8+,
# new rows MUST extend this map; the inventory_coverage test below enforces sync.
# Closes codex F-003: inventory was previously partial (omitted P-PB-dup-* / consume / crash).
PHASE_TO_PASSPORT_MUTATION = {
    # Happy paths
    "A7": "none",          # Path A success — entry already there
    "B10": "appended",     # Path B success — fresh proposal merged
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
    # Duplicate / consume / crash phases (continuation rows — final state checked,
    # not intermediate). Each may yield "none" or "appended" depending on whether
    # a subsequent candidate succeeds; the rule is the orchestrator commits at most
    # one new persisted entry per successful merge, and B1a-recovery branches do NOT
    # double-append. For success-path completion these reach B10 → "appended"; for
    # short-circuit (B1a tuple-match supersession-false A3-A6 success) reach A7 →
    # "none" reading the pre-existing entry.
    "P-PB-dup-early": "conditional",     # depends on A3-A6 outcome + supersession_required
    "P-PB-dup-other": "conditional",     # continues B1a/B2 with remaining candidates
    "P-PB-dup-late": "conditional",      # GO TO B10 reading pre-existing entry; no new append in current session
    "P-PB-consume-fail": "appended",     # B9 atomic-rename succeeded → entry committed
    "P-PB-crash": "conditional",         # depends on whether B9 atomic-rename fired
    # Round-cap escalation phase (§5.4 / B11) — append still happens (B10 ran
    # for round-N MATERIAL) but the orchestrator additionally emits the
    # escalation prompt and awaits user choice. Integration round_3 fixtures
    # use this phase explicitly per F-201 closure.
    "B11": "appended",                   # round == target_rounds MATERIAL → escalation
}

# Total enumerated phases (must equal 24 §5.6 inventory rows + 2 happy-path
# B10/A7 + 1 round-cap escalation B11 = 27).
EXPECTED_PHASE_COUNT = 27

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
        if expected_mutation not in (None, "conditional"):
            actual_mutation = expected_action.get("expected_passport_mutation")
            assert actual_mutation == expected_mutation, (
                f"{pattern_id} BAD: expected_phase={expected_phase} maps to "
                f"passport mutation {expected_mutation!r}, but fixture declares "
                f"{actual_mutation!r}"
            )

    # F-006 closure: assert expected_path matches phase semantics.
    # Phases starting with "P-PA-" or "A" are Path A; "P-PB-" / "B" are Path B.
    expected_path = expected_action.get("expected_path")
    assert expected_path in {"A", "B"}, (
        f"{pattern_id} BAD expected_path must be 'A' or 'B' (got {expected_path!r})"
    )
    if expected_phase:
        if expected_phase.startswith("P-PA-") or expected_phase == "A7":
            assert expected_path == "A", (
                f"{pattern_id} BAD expected_phase={expected_phase} requires expected_path=A"
            )
        elif expected_phase.startswith("P-PB-") or expected_phase == "B10":
            assert expected_path == "B", (
                f"{pattern_id} BAD expected_phase={expected_phase} requires expected_path=B"
            )

    # F-006 closure: assert block_message non-empty for BLOCKING verdicts (MATERIAL/AUDIT_FAILED)
    # and empty for non-blocking (PASS micro fixtures use Path B B10 with passport append + ship).
    if pattern_id != "D2" and bad_verdict["verdict_status"] in {"MATERIAL", "AUDIT_FAILED"}:
        msg = expected_action.get("expected_block_message", "")
        assert "[AUDIT GATE" in msg, (
            f"{pattern_id} BAD expected_block_message must include '[AUDIT GATE' "
            f"substring per §5.6 BLOCK message format; got {msg!r}"
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
        if expected_mutation not in (None, "conditional"):
            assert actual_mutation == expected_mutation

    # F-006 closure: GOOD case Path-B with PASS verdict should have empty block_message.
    block_msg = expected_action.get("expected_block_message", "")
    assert block_msg == "", (
        f"{pattern_id} GOOD expected_block_message must be empty (PASS does not block); "
        f"got {block_msg!r}"
    )
    expected_path = expected_action.get("expected_path")
    assert expected_path in {"A", "B"}, (
        f"{pattern_id} GOOD expected_path must be 'A' or 'B' (got {expected_path!r})"
    )


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


# F-004 closure: drive the §7.3 round/escalation scenario end-to-end against
# the fixture's expected verdicts and pipeline state.

@pytest.mark.parametrize("round_n", [1, 2, 3])
def test_integration_round_per_agent_verdicts_validate(round_n):
    """Each per-round per-agent expected_audit_findings.yaml validates against
    audit_verdict.schema.json AND its declared verdict_status matches the
    round's manifest.expected_verdict for at least one agent (since not every
    agent fails in every round)."""
    base = _integration_dir() / f"round_{round_n}"
    seen_verdicts = set()
    for agent in ("synthesis_agent", "research_architect_agent", "report_compiler_agent"):
        verdict_file = base / agent / "expected_audit_findings.yaml"
        action_file = base / agent / "expected_orchestrator_action.yaml"
        assert verdict_file.exists(), f"missing round {round_n}/{agent}/expected_audit_findings.yaml"
        assert action_file.exists(), f"missing round {round_n}/{agent}/expected_orchestrator_action.yaml"
        verdict = _load_yaml(verdict_file)
        _validate_status_count_consistency(verdict)
        _validate_finding_counts_match(verdict)
        assert verdict["round"] == round_n, (
            f"round {round_n}/{agent} verdict.round={verdict['round']} mismatches directory"
        )
        assert verdict["target_rounds"] == 3
        seen_verdicts.add(verdict["verdict_status"])
    integration = _load_json(_integration_dir() / "manifest.json")
    expected_round = next(r for r in integration["rounds"] if r["round"] == round_n)
    assert expected_round["expected_verdict"] in seen_verdicts, (
        f"round {round_n}: manifest declares verdict={expected_round['expected_verdict']} "
        f"but no agent emits it (saw {seen_verdicts})"
    )


@pytest.mark.parametrize("round_n", [1, 2, 3])
def test_integration_round_pipeline_state_consistent(round_n):
    """expected_pipeline_state.yaml's audit_artifact_appended[].run_id must
    match the per-agent expected_audit_findings.yaml run_ids for the same round."""
    base = _integration_dir() / f"round_{round_n}"
    state = _load_yaml(base / "expected_pipeline_state.yaml")
    state_run_ids = {entry["run_id"] for entry in state["audit_artifact_appended"]}
    actual_run_ids = set()
    for agent in ("synthesis_agent", "research_architect_agent", "report_compiler_agent"):
        verdict = _load_yaml(base / agent / "expected_audit_findings.yaml")
        actual_run_ids.add(verdict["run_id"])
    assert state_run_ids == actual_run_ids, (
        f"round {round_n} pipeline_state.run_ids != per-agent run_ids: "
        f"state={state_run_ids} actual={actual_run_ids}"
    )


def test_integration_escalation_passport_consistent():
    """§7.3 escalation: expected_passport_state.yaml acknowledgement entries'
    finding_ids must match user_response.acknowledged_finding_ids AND the
    manifest's escalation.expected_acknowledgement_finding_ids."""
    base = _integration_dir()
    user_response = _load_yaml(base / "escalation" / "user_response.yaml")
    passport = _load_yaml(base / "escalation" / "expected_passport_state.yaml")
    manifest = _load_json(base / "manifest.json")

    user_ids = set(user_response["acknowledged_finding_ids"])
    manifest_ids = set(manifest["escalation"]["expected_acknowledgement_finding_ids"])
    assert user_ids == manifest_ids, (
        f"user_response acks {user_ids} != manifest acks {manifest_ids}"
    )

    passport_ack_ids = set()
    for entry in passport["audit_artifact"]:
        ack = entry.get("acknowledgement")
        if ack:
            passport_ack_ids.update(ack["finding_ids"])
    assert passport_ack_ids == user_ids, (
        f"passport acks {passport_ack_ids} != user_response acks {user_ids}"
    )

    assert user_response["user_choice"] == manifest["escalation"]["user_choice"]
    assert user_response["user_choice"] == "ship_with_known_residue"


def test_integration_acknowledged_findings_exist_in_round_3():
    """§5.4: acknowledged finding_ids MUST appear as finding.id in the round-3
    MATERIAL verdicts. Acknowledging a non-existent finding is a hand-edit
    attack surface (§3.7 family A row A4 + B10 finding_ids cross-reference)."""
    base = _integration_dir()
    user_response = _load_yaml(base / "escalation" / "user_response.yaml")
    acked = set(user_response["acknowledged_finding_ids"])

    round_3_finding_ids = set()
    for agent in ("synthesis_agent", "research_architect_agent", "report_compiler_agent"):
        verdict = _load_yaml(base / "round_3" / agent / "expected_audit_findings.yaml")
        for f in verdict.get("findings", []):
            round_3_finding_ids.add(f["id"])
    missing = acked - round_3_finding_ids
    assert not missing, (
        f"acknowledged finding_ids {missing} do not appear in any round-3 verdict; "
        f"round 3 emits {round_3_finding_ids}"
    )


def test_integration_finding_id_lineage_carry_forward():
    """Audit template Section 6 contract (line 157): cumulative numbered findings
    carry forward IDs from round 1; new findings get next available ID. Closes codex F-202.

    For the curated A3+C2+D4+C1 subset:
    - A3 (synthesis_agent) round-1 finding gets ID X; same A3 partial-fix surfaces
      at round 2 and 3 → MUST carry the same ID X. (A3 is the lineage with rounds 1+2+3.)
    - D4 (report_compiler_agent) round-1 finding gets ID Y; same D4 word-cap residue
      at rounds 2 and 3 → MUST carry the same ID Y.
    - C2 / C1 close in round 2 (acknowledged by upstream fix) and never recur.
    """
    base = _integration_dir()
    by_round_agent: dict[tuple[int, str], list[dict]] = {}
    for r in (1, 2, 3):
        for agent in ("synthesis_agent", "report_compiler_agent"):
            verdict = _load_yaml(base / f"round_{r}" / agent / "expected_audit_findings.yaml")
            by_round_agent[(r, agent)] = verdict.get("findings", [])

    a3_round_ids = [
        next((f["id"] for f in by_round_agent.get((r, "synthesis_agent"), []) if f), None)
        for r in (1, 2, 3)
    ]
    a3_seen = [i for i in a3_round_ids if i]
    assert len(set(a3_seen)) == 1, (
        f"A3 (synthesis_agent) finding ID must be carried forward across rounds 1→2→3; "
        f"got rounds {a3_round_ids}"
    )

    # D4 lineage: every D4 finding across rounds 1+2+3 (matched by description-substring
    # 'word' or 'cap') shares one ID.
    d4_round_ids = []
    for r in (1, 2, 3):
        for f in by_round_agent.get((r, "report_compiler_agent"), []):
            if "word" in f.get("description", "").lower() or "cap" in f.get("description", "").lower():
                d4_round_ids.append((r, f["id"]))
    d4_unique_ids = set(fid for _, fid in d4_round_ids)
    assert len(d4_unique_ids) == 1, (
        f"D4 (report_compiler_agent) finding ID must be carried forward across rounds 1→2→3; "
        f"got {d4_round_ids}"
    )


# F-201 closure: state runner driving the §7.3 5-step procedure.

def _simulate_round(
    base: Path,
    round_n: int,
    target_rounds: int,
    accumulated_passport: list,
) -> dict:
    """Drive one round through §5.6 Path B for each of three agents.

    Returns a dict carrying the round's overall outcome + per-agent decisions
    + any escalation signal. Mutates accumulated_passport in-place by appending
    each agent's persisted entry per §5.6 B10 (or B11 for round==target MATERIAL).
    """
    round_dir = base / f"round_{round_n}"
    per_agent_decisions = {}
    overall_findings = {"P1": 0, "P2": 0, "P3": 0}
    any_blocking = False
    for agent in ("synthesis_agent", "research_architect_agent", "report_compiler_agent"):
        verdict = _load_yaml(round_dir / agent / "expected_audit_findings.yaml")
        action = _load_yaml(round_dir / agent / "expected_orchestrator_action.yaml")

        # B10/B11 always appends to passport per §5.6 — the harness emulates this.
        accumulated_passport.append({
            "run_id": verdict["run_id"],
            "agent": agent,
            "verdict_status": verdict["verdict_status"],
            "round": verdict["round"],
        })
        for f in verdict.get("findings", []):
            overall_findings[f["severity"]] += 1
        if verdict["verdict_status"] in {"MATERIAL", "AUDIT_FAILED"}:
            any_blocking = True

        decision = _simulate_orchestrator_decision(verdict, action.get("expected_phase"))
        per_agent_decisions[agent] = {
            "verdict_status": verdict["verdict_status"],
            "expected_phase": action["expected_phase"],
            "decision": decision,
        }

    final_round = round_n == target_rounds
    if any_blocking:
        if final_round:
            ship_or_block = "escalation_prompt"  # §5.4 + B11
        else:
            ship_or_block = "block"
    else:
        ship_or_block = "ship"
    return {
        "round": round_n,
        "target_rounds": target_rounds,
        "overall_findings": overall_findings,
        "ship_or_block": ship_or_block,
        "per_agent": per_agent_decisions,
    }


def test_integration_state_runner_drives_full_pipeline():
    """§7.3 lines 2085-2092: 5-step harness procedure drives each round's verdict
    through orchestrator §5.6, accumulates passport state, verifies expected
    pipeline state, feeds round-3 escalation user_response, asserts final passport
    matches expected_passport_state.yaml. Closes codex F-201.
    """
    base = _integration_dir()
    manifest = _load_json(base / "manifest.json")
    target_rounds = manifest["rounds"][0]["target_rounds"]

    accumulated_passport: list = []

    # Step 1+2: load each round's verdicts + drive §5.6 procedure.
    rounds_outcome = []
    for round_n in (1, 2, 3):
        outcome = _simulate_round(base, round_n, target_rounds, accumulated_passport)
        rounds_outcome.append(outcome)

        # Step 3: assert expected_pipeline_state.yaml matches actual.
        expected_state = _load_yaml(base / f"round_{round_n}" / "expected_pipeline_state.yaml")
        actual_run_ids = {entry["run_id"] for entry in accumulated_passport if entry["round"] == round_n}
        expected_run_ids = {entry["run_id"] for entry in expected_state["audit_artifact_appended"]}
        assert actual_run_ids == expected_run_ids, (
            f"round {round_n}: run_id mismatch — actual={actual_run_ids} expected={expected_run_ids}"
        )

        expected_outcome_label = expected_state.get("ship_or_block")
        if expected_outcome_label:
            assert outcome["ship_or_block"] == expected_outcome_label, (
                f"round {round_n}: ship_or_block actual={outcome['ship_or_block']} "
                f"vs declared={expected_outcome_label}"
            )

    # Step 4: at round-3 escalation, feed user_response.yaml.
    final_round = rounds_outcome[-1]
    assert final_round["ship_or_block"] == "escalation_prompt", (
        "round 3 with MATERIAL must emit escalation prompt per §5.4"
    )
    user_response = _load_yaml(base / "escalation" / "user_response.yaml")
    assert user_response["user_choice"] == "ship_with_known_residue"
    acked_ids = set(user_response["acknowledged_finding_ids"])

    # Append acknowledgement entries per §5.4 mechanics. The orchestrator
    # appends a NEW persisted entry mirroring each acknowledged round-3 MATERIAL
    # entry's run_id with an acknowledgement{} block.
    for agent in ("synthesis_agent", "report_compiler_agent"):
        round_3_verdict = _load_yaml(base / "round_3" / agent / "expected_audit_findings.yaml")
        agent_finding_ids = {f["id"] for f in round_3_verdict.get("findings", [])}
        agent_acked = acked_ids & agent_finding_ids
        if agent_acked:
            accumulated_passport.append({
                "run_id": round_3_verdict["run_id"],
                "agent": agent,
                "verdict_status": "MATERIAL",
                "round": 3,
                "acknowledgement": {
                    "finding_ids": sorted(agent_acked),
                    "acknowledged_at": user_response["acknowledged_at"],
                    "acknowledged_by": user_response["acknowledged_by"],
                },
            })

    # Step 5: assert expected_passport_state.yaml matches actual.
    expected_passport = _load_yaml(base / "escalation" / "expected_passport_state.yaml")
    expected_run_id_seq = [e["run_id"] for e in expected_passport["audit_artifact"]]
    actual_run_id_seq = [e["run_id"] for e in accumulated_passport]
    assert actual_run_id_seq == expected_run_id_seq, (
        f"final passport run_id sequence mismatch:\nactual={actual_run_id_seq}\nexpected={expected_run_id_seq}"
    )

    expected_ack_pairs = [
        (e["run_id"], tuple(e["acknowledgement"]["finding_ids"]))
        for e in expected_passport["audit_artifact"]
        if e.get("acknowledgement")
    ]
    actual_ack_pairs = [
        (e["run_id"], tuple(e["acknowledgement"]["finding_ids"]))
        for e in accumulated_passport
        if e.get("acknowledgement")
    ]
    assert actual_ack_pairs == expected_ack_pairs, (
        f"acknowledgement entries mismatch:\nactual={actual_ack_pairs}\nexpected={expected_ack_pairs}"
    )

    # Final outcome check.
    expected_outcome = _load_yaml(base / "escalation" / "expected_pipeline_outcome.yaml")
    assert expected_outcome["stage_outcome"] == "shipped_with_known_residue"
    assert expected_outcome["audit_gate_outcome"] == "ship_with_known_residue"


# ---------------------------------------------------------------------------
# §7.5 coverage cross-check (defense in depth — also covered by manifest validator)
# ---------------------------------------------------------------------------


def test_inventory_coverage_17_of_17():
    """All 17 numbered pattern IDs have exactly one micro-fixture."""
    seen = set(_all_micro_fixtures())
    assert seen == set(PATTERN_IDS), (
        f"missing: {set(PATTERN_IDS) - seen}; extra: {seen - set(PATTERN_IDS)}"
    )


def test_phase_inventory_complete():
    """§5.6 verification failure state inventory has 24 rows + 2 happy paths.
    PHASE_TO_PASSPORT_MUTATION must enumerate all 26 phases. Closes codex F-003.
    """
    assert len(PHASE_TO_PASSPORT_MUTATION) == EXPECTED_PHASE_COUNT, (
        f"PHASE_TO_PASSPORT_MUTATION has {len(PHASE_TO_PASSPORT_MUTATION)} rows; "
        f"§5.6 inventory + happy paths require {EXPECTED_PHASE_COUNT}. "
        "Either §5.6 grew (extend the map) or this assertion is stale."
    )


def test_every_fixture_phase_in_inventory():
    """Every fixture's expected_phase must be a known §5.6 inventory row."""
    fixture_root = FIXTURE_ROOT
    if not fixture_root.exists():
        pytest.skip("fixture root not present")
    bad_phases = []
    for verdict_file in sorted(fixture_root.rglob("expected_orchestrator_action.yaml")):
        action = _load_yaml(verdict_file)
        phase = action.get("expected_phase")
        if phase and phase not in PHASE_TO_PASSPORT_MUTATION:
            bad_phases.append(
                f"{verdict_file.relative_to(REPO_ROOT)}: unknown expected_phase={phase!r}"
            )
    assert not bad_phases, "fixtures reference phases not in §5.6 inventory:\n" + "\n".join(bad_phases)
