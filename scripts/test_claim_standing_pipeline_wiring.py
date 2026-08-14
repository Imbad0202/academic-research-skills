"""#655 PR-C: pipeline-wiring noninterference and surface-alignment tests.

Gate 12 (§9): running the wiring layer changes no Phase E verdict, gate,
manuscript, citation, or read-ledger byte — proven here as (a) a static
capability scan of the three wiring modules (no network, subprocess, Phase E,
or read-ledger imports), and (b) an end-to-end run that creates no files and
mutates no inputs. The remaining tests pin the prose surfaces (Phase E
protocol offer section, candidate-ledger protocol, contracts README,
CHANGELOG, CI manifest) to the shipped wiring so the docs cannot silently
drift from the code.
"""
from __future__ import annotations

import ast
import copy
import json
from pathlib import Path

from scripts import build_claim_standing_candidate_ledger as substrate
from scripts import build_claim_standing_query_plan as plan_builder
from scripts import check_claim_standing_freshness as freshness
from scripts import check_claim_standing_transmissions as transmissions
from scripts import claim_standing_stance_runner as runner
from scripts.test_build_claim_standing_candidate_ledger import (
    _rehash_input,
    _rehash_plan,
    _retained,
)
from scripts.test_build_claim_standing_query_plan import (
    _bound_decisions,
    _decisions,
    _registry_row,
)
from scripts.test_claim_standing_stance_contracts import _plan_v1_1
from scripts.test_claim_standing_stance_runner import FakeTransport

ROOT = Path(__file__).resolve().parents[1]
WIRING_MODULES = (
    ROOT / "scripts/build_claim_standing_query_plan.py",
    ROOT / "scripts/check_claim_standing_freshness.py",
    ROOT / "scripts/check_claim_standing_transmissions.py",
)
ALLOWED_IMPORTS = {
    "__future__",
    "argparse",
    "json",
    "sys",
    "pathlib",
    "typing",
    "scripts",
    "build_claim_standing_candidate_ledger",
    "claim_standing_discovery",
    "claim_standing_stance_runner",
}
FORBIDDEN_CAPABILITY_MODULES = {
    "urllib",
    "http",
    "socket",
    "ssl",
    "subprocess",
    "ctypes",
    "importlib",
    "os",
}
PHASE_E_AND_READ_LEDGER_MODULES = {"evidence_rows", "retraction_status"}


def _imported_names(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.module is not None:
                names.add(node.module.split(".")[0])
            names.update(
                alias.name.split(".")[0]
                for alias in node.names
                if node.module == "scripts"
            )
    return names


# --- gate 12: static capability scan ----------------------------------------


def test_wiring_modules_import_only_the_declared_allowlist() -> None:
    for path in WIRING_MODULES:
        names = _imported_names(path)
        assert names <= ALLOWED_IMPORTS, (
            f"{path.name} imports outside the wiring allowlist: "
            f"{sorted(names - ALLOWED_IMPORTS)}"
        )


def test_wiring_modules_have_no_network_subprocess_or_read_ledger_reach() -> None:
    for path in WIRING_MODULES:
        names = _imported_names(path)
        assert not (names & FORBIDDEN_CAPABILITY_MODULES), path.name
        assert not (names & PHASE_E_AND_READ_LEDGER_MODULES), path.name
        source = path.read_text(encoding="utf-8")
        for marker in ("human_read_log", "human_read_source", "read_scope"):
            assert marker not in source, f"{path.name} touches {marker}"


# --- gate 12: end-to-end run leaves everything untouched --------------------


def test_end_to_end_wiring_creates_no_files_and_mutates_no_inputs(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.chdir(tmp_path)

    row = _registry_row()
    decisions = _bound_decisions(row, _decisions())
    row_before = copy.deepcopy(row)
    decisions_before = copy.deepcopy(decisions)
    built_plan = plan_builder.bind_plan(row, decisions)
    substrate.validate_plan(built_plan)

    stance_plan = _plan_v1_1(stance=True)
    stance_plan["stance_plan"]["prompt_contract_version"] = (
        runner.PROMPT_CONTRACT_VERSION
    )
    _rehash_plan(stance_plan)
    retained = _retained()
    _rehash_input(retained, stance_plan)
    ledger_value = substrate.build_ledger(stance_plan, retained)
    record, _, events = runner.run_stance(
        stance_plan, ledger_value, transport=FakeTransport()
    )
    inputs_before = copy.deepcopy((stance_plan, retained, ledger_value, record))

    transmissions.build_transmission_ledger(
        stance_plan, retained, stance_transmissions=events
    )
    freshness.assess_freshness(
        current_claim_text=stance_plan["claim"]["claim_text"],
        plan=stance_plan,
        candidate_ledger=ledger_value,
        stance_record=record,
    )

    assert row == row_before
    assert decisions == decisions_before
    assert (stance_plan, retained, ledger_value, record) == inputs_before
    assert list(tmp_path.iterdir()) == []


# --- prose surfaces stay aligned with the shipped wiring --------------------


def test_phase_e_surface_offers_the_probe_with_the_exact_trigger() -> None:
    text = (
        ROOT / "academic-pipeline/references/claim_verification_protocol.md"
    ).read_text(encoding="utf-8")
    for marker in (
        "## Claim-Standing Probe Offer (#655",
        "opt-in, advisory-only",
        "`HIGH-IMPACT`",
        "`RANDOM`, `TOP-UP`, and `NOT-SELECTED` rows are never eligible",
        "`ALL` is not permission to probe every claim",
        "ineligible until the researcher confirms",
        "never written back to the registry",
        "Eligibility never dispatches anything",
        "`not_checked` declination record",
        "scripts/build_claim_standing_query_plan.py",
        "shared/references/claim_standing_candidate_ledger_protocol.md",
        "STANCE CLASSIFICATION UNMEASURED",
        "gate_effect = none",
    ):
        assert marker in text, f"probe-offer marker missing: {marker}"


def test_protocol_doc_documents_the_wiring_and_transmission_contract() -> None:
    text = (
        ROOT / "shared/references/claim_standing_candidate_ledger_protocol.md"
    ).read_text(encoding="utf-8")
    for marker in (
        "claim-standing-transmission-ledger/1.0",
        "build_claim_standing_query_plan.py",
        "check_claim_standing_freshness.py",
        "check_claim_standing_transmissions.py",
    ):
        assert marker in text, f"protocol marker missing: {marker}"
    assert "deferred to the pipeline-wiring slice" not in text


def test_contracts_readme_lists_the_transmission_ledger() -> None:
    text = (ROOT / "shared/contracts/README.md").read_text(encoding="utf-8")
    assert "transmission_ledger.schema.json" in text
    assert "claim-standing-transmission-ledger/1.0" in text


def test_changelog_documents_the_pipeline_wiring() -> None:
    text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "Pipeline wiring for the #655 claim-standing probe" in text


def test_ci_manifest_registers_the_wiring_test_files() -> None:
    text = (ROOT / "scripts/_ci_pytest_manifest.toml").read_text(
        encoding="utf-8"
    )
    for entry_id in (
        "655-claim-standing-query-plan-builder",
        "655-claim-standing-freshness",
        "655-claim-standing-transmissions",
        "655-claim-standing-pipeline-wiring",
    ):
        assert f'id = "{entry_id}"' in text, entry_id


def test_declination_record_carries_no_verdict_or_gate_vocabulary() -> None:
    row = _registry_row()
    decisions = _bound_decisions(
        row, _decisions(decision="cancel", recorded_at="2026-08-14T01:05:00Z")
    )
    record = plan_builder.bind_plan(row, decisions)
    rendered = json.dumps(record).lower()
    for forbidden in ("verdict", "severity", "pass", "fail", "score"):
        assert forbidden not in rendered
