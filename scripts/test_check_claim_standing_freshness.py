"""#655 PR-C: §7 freshness tests (gate 13: drift makes an old result stale).

The probe identity binds claim text, consent receipt, query plan, adapter
registry, candidate ledger, and stance configuration. Any drift in those
bindings must surface as an explicit stale verdict with closed reason
tokens; a stale result stays inspectable but is never presented as current.
Hermetic: synthetic fixtures and the injected fake transport only.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from scripts import build_claim_standing_candidate_ledger as substrate
from scripts import build_claim_standing_query_plan as plan_builder
from scripts import check_claim_standing_freshness as freshness
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


def _setup() -> tuple[dict, dict, dict]:
    plan = _plan_v1_1(stance=True)
    plan["stance_plan"]["prompt_contract_version"] = runner.PROMPT_CONTRACT_VERSION
    _rehash_plan(plan)
    retained = _retained()
    _rehash_input(retained, plan)
    ledger_value = substrate.build_ledger(plan, retained)
    record, _, _ = runner.run_stance(
        plan, ledger_value, transport=FakeTransport()
    )
    return plan, ledger_value, record


def _assess(plan: dict, ledger_value: dict | None, record: dict | None, **kw):
    return freshness.assess_freshness(
        current_claim_text=kw.pop(
            "current_claim_text", plan["claim"]["claim_text"]
        ),
        plan=plan,
        candidate_ledger=ledger_value,
        stance_record=record,
        **kw,
    )


# --- current ----------------------------------------------------------------


def test_unchanged_probe_is_current() -> None:
    plan, ledger_value, record = _setup()
    verdict = _assess(plan, ledger_value, record)
    assert verdict["status"] == "current"
    assert verdict["stale_reasons"] == []
    assert verdict["probe_id"] == plan["probe_id"]
    assert "stance_configuration" in verdict["assessed"]
    assert "candidate_ledger" in verdict["assessed"]


def test_plan_only_assessment_declares_what_it_did_not_compare() -> None:
    # Gate 13 honesty: a claim-text-only comparison must not present itself
    # as a complete freshness assessment.
    plan, _, _ = _setup()
    verdict = _assess(plan, None, None)
    assert verdict["status"] == "current"
    assert verdict["assessed"] == ["claim_text"]
    assert "current_adapter_registry" in verdict["unassessed"]
    assert "candidate_ledger" in verdict["unassessed"]
    assert "artifact_semantic_validation" in verdict["unassessed"]


def test_stance_record_without_its_ledger_cannot_be_assessed() -> None:
    plan, _, record = _setup()
    with pytest.raises(freshness.FreshnessError, match="ledger"):
        _assess(plan, None, record)


def test_resealed_runtime_identity_swap_is_stale() -> None:
    plan, ledger_value, record = _setup()
    swapped = copy.deepcopy(record)
    swapped["stance_runtime"]["model_identity"] = "synthetic-stance-model-9"
    swapped["stance_record_sha256"] = substrate.bound_digest(
        swapped, "stance_record_sha256"
    )
    verdict = _assess(plan, ledger_value, swapped)
    assert verdict["status"] == "stale"
    assert "stance_configuration_changed" in verdict["stale_reasons"]


# --- gate 13: each drift axis becomes visibly stale -------------------------


def test_claim_text_revision_is_stale() -> None:
    plan, ledger_value, record = _setup()
    verdict = _assess(
        plan,
        ledger_value,
        record,
        current_claim_text=plan["claim"]["claim_text"] + " Revised.",
    )
    assert verdict["status"] == "stale"
    assert "claim_text_changed" in verdict["stale_reasons"]
    assert "inspectable" in verdict["presentation_rule"]
    assert "current" in verdict["presentation_rule"]


def test_query_edit_after_the_run_is_stale() -> None:
    plan, ledger_value, record = _setup()
    edited = copy.deepcopy(plan)
    edited["queries"][0]["accepted_query_text"] = "an edited query"
    edited["queries"][0]["construction"] = "researcher_authored"
    _rehash_plan(edited)
    verdict = _assess(edited, ledger_value, record)
    assert verdict["status"] == "stale"
    assert "query_plan_changed" in verdict["stale_reasons"]


def test_reaccepted_consent_is_stale_against_the_old_record() -> None:
    plan, ledger_value, record = _setup()
    reaccepted = copy.deepcopy(plan)
    reaccepted["consent"]["accepted_at"] = "2026-08-14T09:00:00Z"
    _rehash_plan(reaccepted)
    verdict = _assess(reaccepted, ledger_value, record)
    assert verdict["status"] == "stale"
    assert "consent_receipt_changed" in verdict["stale_reasons"]


def test_changed_candidate_ledger_is_stale() -> None:
    plan, ledger_value, record = _setup()
    mutated = copy.deepcopy(ledger_value)
    mutated["completed_at"] = "2026-08-14T09:00:00Z"
    mutated["candidate_ledger_sha256"] = substrate.bound_digest(
        mutated, "candidate_ledger_sha256"
    )
    verdict = _assess(plan, mutated, record)
    assert verdict["status"] == "stale"
    assert "candidate_ledger_changed" in verdict["stale_reasons"]


def test_stance_configuration_change_is_stale() -> None:
    plan, ledger_value, record = _setup()
    changed = copy.deepcopy(plan)
    changed["stance_plan"]["model_identity"] = "synthetic-stance-model-2"
    _rehash_plan(changed)
    verdict = _assess(changed, ledger_value, record)
    assert verdict["status"] == "stale"
    assert "stance_configuration_changed" in verdict["stale_reasons"]


def test_prompt_contract_drift_is_stale() -> None:
    plan, ledger_value, record = _setup()
    drifted = copy.deepcopy(record)
    drifted["stance_runtime"]["prompt_contract_version"] = "legacy-prompt-0.9"
    drifted["stance_record_sha256"] = substrate.bound_digest(
        drifted, "stance_record_sha256"
    )
    verdict = _assess(plan, ledger_value, drifted)
    assert verdict["status"] == "stale"
    assert "stance_configuration_changed" in verdict["stale_reasons"]


# --- corruption is an error, not a silent verdict ---------------------------


def test_corrupt_record_digest_cannot_be_assessed() -> None:
    plan, ledger_value, record = _setup()
    corrupt = copy.deepcopy(record)
    corrupt["completed_at"] = "2026-08-14T09:00:00Z"  # digest left stale
    with pytest.raises(freshness.FreshnessError, match="digest"):
        _assess(plan, ledger_value, corrupt)


def test_corrupt_ledger_digest_cannot_be_assessed() -> None:
    plan, ledger_value, record = _setup()
    corrupt = copy.deepcopy(ledger_value)
    corrupt["completed_at"] = "2026-08-14T09:00:00Z"  # digest left stale
    with pytest.raises(freshness.FreshnessError, match="digest"):
        _assess(plan, corrupt, record)


# --- runtime adapter drift (opt-in) -----------------------------------------


def test_runtime_check_flags_unknown_or_drifted_adapters() -> None:
    plan, _, _ = _setup()  # fixture roster uses synthetic index ids
    verdict = _assess(plan, None, None, runtime_check=True)
    assert verdict["status"] == "stale"
    assert "adapter_registry_changed" in verdict["stale_reasons"]


def test_runtime_check_passes_for_currently_declared_adapters() -> None:
    row = _registry_row()
    plan = plan_builder.bind_plan(row, _bound_decisions(row, _decisions()))
    verdict = freshness.assess_freshness(
        current_claim_text=row["claim_text"],
        plan=plan,
        candidate_ledger=None,
        stance_record=None,
        runtime_check=True,
    )
    assert verdict["status"] == "current"


# --- inputs stay unmutated (gate 12 support) --------------------------------


def test_assessment_does_not_mutate_inputs() -> None:
    plan, ledger_value, record = _setup()
    plan_before = copy.deepcopy(plan)
    ledger_before = copy.deepcopy(ledger_value)
    record_before = copy.deepcopy(record)
    _assess(plan, ledger_value, record)
    assert plan == plan_before
    assert ledger_value == ledger_before
    assert record == record_before


# --- CLI --------------------------------------------------------------------


def _write_json(path: Path, value: object) -> Path:
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
    return path


def test_cli_prints_verdict_for_stale_probe(tmp_path, capsys) -> None:
    plan, ledger_value, record = _setup()
    claim_file = tmp_path / "claim.txt"
    claim_file.write_text(
        plan["claim"]["claim_text"] + " Revised.", encoding="utf-8"
    )
    rc = freshness.main(
        [
            "--current-claim-file", str(claim_file),
            "--query-plan", str(_write_json(tmp_path / "plan.json", plan)),
            "--candidate-ledger",
            str(_write_json(tmp_path / "ledger.json", ledger_value)),
            "--stance-record", str(_write_json(tmp_path / "record.json", record)),
        ]
    )
    assert rc == 0
    verdict = json.loads(capsys.readouterr().out)
    assert verdict["status"] == "stale"
    assert "claim_text_changed" in verdict["stale_reasons"]


def test_cli_errors_on_corrupt_record(tmp_path, capsys) -> None:
    plan, ledger_value, record = _setup()
    corrupt = copy.deepcopy(record)
    corrupt["completed_at"] = "2026-08-14T09:00:00Z"
    claim_file = tmp_path / "claim.txt"
    claim_file.write_text(plan["claim"]["claim_text"], encoding="utf-8")
    rc = freshness.main(
        [
            "--current-claim-file", str(claim_file),
            "--query-plan", str(_write_json(tmp_path / "plan.json", plan)),
            "--candidate-ledger",
            str(_write_json(tmp_path / "ledger.json", ledger_value)),
            "--stance-record",
            str(_write_json(tmp_path / "record.json", corrupt)),
        ]
    )
    assert rc == 1
    assert "digest" in capsys.readouterr().err
