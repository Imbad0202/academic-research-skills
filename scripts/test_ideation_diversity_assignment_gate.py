from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

GATE_SPEC = importlib.util.spec_from_file_location(
    "ideation_assignment_gate", SCRIPTS / "ideation_diversity_assignment_gate.py"
)
assert GATE_SPEC and GATE_SPEC.loader
gate = importlib.util.module_from_spec(GATE_SPEC)
GATE_SPEC.loader.exec_module(gate)

fixtures_spec = importlib.util.spec_from_file_location(
    "ideation_no_call_test_fixtures", SCRIPTS / "test_run_ideation_diversity_no_call.py"
)
assert fixtures_spec and fixtures_spec.loader
fixtures = importlib.util.module_from_spec(fixtures_spec)
fixtures_spec.loader.exec_module(fixtures)
runner = fixtures.runner


@pytest.fixture(scope="module")
def finalized_bundle(tmp_path_factory) -> Path:
    base = tmp_path_factory.mktemp("finalized")
    run_dir, plan_sha, plan = fixtures._initialize(base)
    fixtures.runner.materialize(fixtures._command_args(run_dir, plan_sha))
    source = base / "external-transcript.json"
    authorization = fixtures._authorization_file(base, plan)
    for cell in plan["cells"]:
        source.unlink(missing_ok=True)
        source.write_bytes(
            fixtures.runner._json_bytes(fixtures._transcript(plan, cell))
        )
        fixtures.runner.ingest(
            fixtures._command_args(
                run_dir,
                plan_sha,
                transcript=source,
                authorization_record=authorization,
            )
        )
    outcome = fixtures.runner.prepare_blind_packet(
        fixtures._command_args(run_dir, plan_sha)
    )
    assert outcome["state"] == "blind_finalized"
    return run_dir


def _copy_bundle(finalized_bundle: Path, tmp_path: Path) -> Path:
    run_dir = tmp_path / "run"
    shutil.copytree(finalized_bundle, run_dir)
    os.chmod(run_dir / "blind" / "private", 0o700)
    os.chmod(run_dir / "blind" / "private" / "arm-map.json", 0o600)
    return run_dir


def _map_by_blind(run_dir: Path, field: str) -> dict[str, str]:
    private_map = json.loads(
        (run_dir / "blind" / "private" / "arm-map.json").read_bytes()
    )
    return {row["blind_session_id"]: row[field] for row in private_map["mapping"]}


def _valid_ledger(run_dir: Path) -> dict:
    pair_by_blind = _map_by_blind(run_dir, "pair_id")
    by_pair: dict[str, list[str]] = {}
    for blind_id, pair_id in pair_by_blind.items():
        by_pair.setdefault(pair_id, []).append(blind_id)
    judges = [f"judge-{index:02d}" for index in range(1, 33)]
    assignments: list[dict[str, str]] = []
    for pair_id in sorted(by_pair):
        blinds = sorted(by_pair[pair_id])
        assert len(blinds) == 16
        for slot, blind_id in enumerate(blinds):
            assignments.append(
                {"judge_id": judges[2 * slot], "blind_session_id": blind_id}
            )
            assignments.append(
                {"judge_id": judges[2 * slot + 1], "blind_session_id": blind_id}
            )
    assignments.sort(key=lambda row: (row["blind_session_id"], row["judge_id"]))
    return {
        "schema_version": "ideation-diversity-judge-assignment-ledger/1.0",
        "suite": runner.SUITE,
        "run_plan_sha256": hashlib.sha256(
            (run_dir / "run-plan.json").read_bytes()
        ).hexdigest(),
        "inventory_sha256": hashlib.sha256(
            (run_dir / "blind" / "inventory.json").read_bytes()
        ).hexdigest(),
        "blind_manifest_sha256": hashlib.sha256(
            (run_dir / "blind" / "manifest.json").read_bytes()
        ).hexdigest(),
        "private_map_sha256": hashlib.sha256(
            (run_dir / "blind" / "private" / "arm-map.json").read_bytes()
        ).hexdigest(),
        "identity_boundary": {
            "handles_are_pseudonymous": True,
            "person_distinctness_verified_by_gate": False,
            "independence_is_procedural_responsibility": True,
        },
        "judges": judges,
        "adjudicator_id": "adjudicator-01",
        "first_round_assignments": assignments,
    }


def _write_ledger(tmp_path: Path, ledger: dict) -> Path:
    path = tmp_path / "assignment-ledger.json"
    path.write_bytes(runner._json_bytes(ledger))
    return path


def _receipt_path(run_dir: Path) -> Path:
    return (
        run_dir.parent
        / f"{run_dir.name}-assignment-gate"
        / "assignment-gate-receipt.json"
    )


def _verify_args(run_dir: Path, ledger_path: Path) -> argparse.Namespace:
    return argparse.Namespace(run_dir=run_dir, ledger=ledger_path)


def _deliver_args(
    run_dir: Path, judge_id: str, blind_session_id: str, dest: Path
) -> argparse.Namespace:
    return argparse.Namespace(
        run_dir=run_dir,
        judge=judge_id,
        blind_session_id=blind_session_id,
        dest=dest,
    )


def test_gate_passes_valid_ledger_and_writes_write_once_receipt(
    finalized_bundle, tmp_path
):
    run_dir = _copy_bundle(finalized_bundle, tmp_path)
    ledger = _valid_ledger(run_dir)
    ledger_path = _write_ledger(tmp_path, ledger)
    result = gate.verify(_verify_args(run_dir, ledger_path))
    assert result["verdict"] == "pass"
    receipt_path = _receipt_path(run_dir)
    receipt_raw = receipt_path.read_bytes()
    receipt = json.loads(receipt_raw)
    assert receipt["verdict"] == "pass"
    assert receipt["ledger_sha256"] == hashlib.sha256(
        ledger_path.read_bytes()
    ).hexdigest()
    assert receipt["ledger"] == ledger
    assert (
        receipt["delivery_rule"]
        == "deliver_exactly_one_isolated_packet_per_first_round_judge_assignment"
    )
    # Idempotent re-verify with the identical ledger keeps the exact bytes.
    again = gate.verify(_verify_args(run_dir, ledger_path))
    assert again["verdict"] == "pass"
    assert receipt_path.read_bytes() == receipt_raw
    # A different ledger cannot replace the receipt.
    changed = _valid_ledger(run_dir)
    changed["adjudicator_id"] = "adjudicator-02"
    with pytest.raises(gate.GateError, match="RECEIPT-CONFLICT"):
        gate.verify(_verify_args(run_dir, _write_ledger(tmp_path, changed)))
    assert receipt_path.read_bytes() == receipt_raw


def test_receipt_and_ledger_never_carry_pair_or_arm_fields(
    finalized_bundle, tmp_path
):
    run_dir = _copy_bundle(finalized_bundle, tmp_path)
    ledger_path = _write_ledger(tmp_path, _valid_ledger(run_dir))
    gate.verify(_verify_args(run_dir, ledger_path))
    receipt_text = (_receipt_path(run_dir)).read_text("utf-8")
    for forbidden in (
        "pair_id",
        "arm_id",
        "scenario_id",
        "experiment_id",
        "replicate",
        "cell_id",
    ):
        assert forbidden not in receipt_text


def test_judge_sharing_a_pair_fails_closed_and_writes_nothing(
    finalized_bundle, tmp_path
):
    run_dir = _copy_bundle(finalized_bundle, tmp_path)
    ledger = _valid_ledger(run_dir)
    pair_by_blind = _map_by_blind(run_dir, "pair_id")
    rows = ledger["first_round_assignments"]
    first = rows[0]
    conflicting = next(
        row
        for row in rows
        if row["judge_id"] != first["judge_id"]
        and row["blind_session_id"] != first["blind_session_id"]
        and pair_by_blind[row["blind_session_id"]]
        == pair_by_blind[first["blind_session_id"]]
    )
    conflicting["judge_id"] = first["judge_id"]
    ledger_path = _write_ledger(tmp_path, ledger)
    with pytest.raises(gate.GateError, match="LEDGER-EXPOSURE"):
        gate.verify(_verify_args(run_dir, ledger_path))
    assert not (_receipt_path(run_dir)).exists()


def test_cross_experiment_same_scenario_exposure_is_also_blocked(
    finalized_bundle, tmp_path
):
    run_dir = _copy_bundle(finalized_bundle, tmp_path)
    ledger = _valid_ledger(run_dir)
    pair_by_blind = _map_by_blind(run_dir, "pair_id")
    experiment_by_blind = _map_by_blind(run_dir, "experiment_id")
    rows = ledger["first_round_assignments"]
    first = rows[0]
    cross = next(
        row
        for row in rows
        if row["judge_id"] != first["judge_id"]
        and pair_by_blind[row["blind_session_id"]]
        == pair_by_blind[first["blind_session_id"]]
        and experiment_by_blind[row["blind_session_id"]]
        != experiment_by_blind[first["blind_session_id"]]
    )
    cross["judge_id"] = first["judge_id"]
    ledger_path = _write_ledger(tmp_path, ledger)
    with pytest.raises(gate.GateError, match="LEDGER-EXPOSURE"):
        gate.verify(_verify_args(run_dir, ledger_path))


def test_every_packet_needs_two_distinct_judges(finalized_bundle, tmp_path):
    run_dir = _copy_bundle(finalized_bundle, tmp_path)
    ledger = _valid_ledger(run_dir)
    rows = ledger["first_round_assignments"]
    removed = rows.pop(0)
    survivor = next(
        row for row in rows if row["blind_session_id"] != removed["blind_session_id"]
    )
    rows.append(
        {"judge_id": "judge-33", "blind_session_id": survivor["blind_session_id"]}
    )
    ledger["judges"] = [*ledger["judges"], "judge-33"]
    ledger_path = _write_ledger(tmp_path, ledger)
    with pytest.raises(gate.GateError, match="LEDGER-COVERAGE"):
        gate.verify(_verify_args(run_dir, ledger_path))


def test_unknown_blind_id_or_unlisted_judge_fails(finalized_bundle, tmp_path):
    run_dir = _copy_bundle(finalized_bundle, tmp_path)
    ledger = _valid_ledger(run_dir)
    ledger["first_round_assignments"][0]["blind_session_id"] = "blind-" + "0" * 24
    with pytest.raises(gate.GateError, match="LEDGER-COVERAGE"):
        gate.verify(_verify_args(run_dir, _write_ledger(tmp_path, ledger)))
    ledger = _valid_ledger(run_dir)
    ledger["first_round_assignments"][0]["judge_id"] = "judge-99"
    with pytest.raises(gate.GateError, match="LEDGER-ROSTER"):
        gate.verify(_verify_args(run_dir, _write_ledger(tmp_path, ledger)))
    ledger = _valid_ledger(run_dir)
    ledger["judges"] = [*ledger["judges"], "judge-98"]
    with pytest.raises(gate.GateError, match="LEDGER-ROSTER"):
        gate.verify(_verify_args(run_dir, _write_ledger(tmp_path, ledger)))


def test_adjudicator_handle_cannot_take_a_first_round_packet(
    finalized_bundle, tmp_path
):
    run_dir = _copy_bundle(finalized_bundle, tmp_path)
    ledger = _valid_ledger(run_dir)
    ledger["first_round_assignments"][0]["judge_id"] = "adjudicator-01"
    with pytest.raises(gate.GateError, match="LEDGER-SCHEMA"):
        gate.verify(_verify_args(run_dir, _write_ledger(tmp_path, ledger)))


def test_binding_drift_or_loosened_private_map_fails(finalized_bundle, tmp_path):
    run_dir = _copy_bundle(finalized_bundle, tmp_path)
    ledger = _valid_ledger(run_dir)
    ledger["inventory_sha256"] = "0" * 64
    with pytest.raises(gate.GateError, match="LEDGER-BINDING"):
        gate.verify(_verify_args(run_dir, _write_ledger(tmp_path, ledger)))
    run_dir_loose = _copy_bundle(finalized_bundle, tmp_path / "loose")
    ledger_path = _write_ledger(tmp_path / "loose", _valid_ledger(run_dir_loose))
    os.chmod(run_dir_loose / "blind" / "private" / "arm-map.json", 0o644)
    with pytest.raises(gate.GateError, match="LEDGER-BINDING"):
        gate.verify(_verify_args(run_dir_loose, ledger_path))


def test_tampered_bundle_fails_replay_before_any_receipt(
    finalized_bundle, tmp_path
):
    run_dir = _copy_bundle(finalized_bundle, tmp_path)
    ledger = _valid_ledger(run_dir)
    packet_path = sorted((run_dir / "blind" / "sessions").glob("*.json"))[0]
    packet_path.write_bytes(b"TAMPERED PACKET\n")
    ledger_path = _write_ledger(tmp_path, ledger)
    with pytest.raises(gate.GateError):
        gate.verify(_verify_args(run_dir, ledger_path))
    assert not (_receipt_path(run_dir)).exists()


def test_delivery_requires_pass_receipt(finalized_bundle, tmp_path):
    run_dir = _copy_bundle(finalized_bundle, tmp_path)
    ledger = _valid_ledger(run_dir)
    row = ledger["first_round_assignments"][0]
    dest = tmp_path / "judge-desk"
    with pytest.raises(gate.GateError, match="DELIVERY-RECEIPT"):
        gate.deliver(
            _deliver_args(run_dir, row["judge_id"], row["blind_session_id"], dest)
        )


def test_delivery_copies_exactly_one_packet_once(finalized_bundle, tmp_path):
    run_dir = _copy_bundle(finalized_bundle, tmp_path)
    ledger = _valid_ledger(run_dir)
    ledger_path = _write_ledger(tmp_path, ledger)
    gate.verify(_verify_args(run_dir, ledger_path))
    row = ledger["first_round_assignments"][0]
    dest = tmp_path / "judge-desk"
    result = gate.deliver(
        _deliver_args(run_dir, row["judge_id"], row["blind_session_id"], dest)
    )
    assert result["delivered"] == 1
    delivered = list(dest.iterdir())
    assert [path.name for path in delivered] == [
        f"{row['blind_session_id']}.json"
    ]
    assert delivered[0].read_bytes() == (
        run_dir / "blind" / "sessions" / f"{row['blind_session_id']}.json"
    ).read_bytes()
    with pytest.raises(gate.GateError, match="DELIVERY-DUPLICATE"):
        gate.deliver(
            _deliver_args(
                run_dir, row["judge_id"], row["blind_session_id"], tmp_path / "again"
            )
        )
    own_blinds = {
        other["blind_session_id"]
        for other in ledger["first_round_assignments"]
        if other["judge_id"] == row["judge_id"]
    }
    unassigned = next(
        other
        for other in ledger["first_round_assignments"]
        if other["blind_session_id"] not in own_blinds
    )
    with pytest.raises(gate.GateError, match="DELIVERY-UNASSIGNED"):
        gate.deliver(
            _deliver_args(
                run_dir,
                row["judge_id"],
                unassigned["blind_session_id"],
                tmp_path / "misdirected",
            )
        )
    occupied = tmp_path / "occupied"
    occupied.mkdir()
    (occupied / "existing.txt").write_text("already here")
    second = ledger["first_round_assignments"][1]
    with pytest.raises(gate.GateError, match="DELIVERY-DEST"):
        gate.deliver(
            _deliver_args(
                run_dir, second["judge_id"], second["blind_session_id"], occupied
            )
        )
    inside = run_dir / "blind" / "inside-dest"
    with pytest.raises(gate.GateError, match="DELIVERY-DEST"):
        gate.deliver(
            _deliver_args(
                run_dir, second["judge_id"], second["blind_session_id"], inside
            )
        )


def test_delivery_refuses_when_bundle_drifts_after_receipt(
    finalized_bundle, tmp_path
):
    run_dir = _copy_bundle(finalized_bundle, tmp_path)
    ledger = _valid_ledger(run_dir)
    ledger_path = _write_ledger(tmp_path, ledger)
    gate.verify(_verify_args(run_dir, ledger_path))
    row = ledger["first_round_assignments"][0]
    packet_path = (
        run_dir / "blind" / "sessions" / f"{row['blind_session_id']}.json"
    )
    packet_path.write_bytes(b"TAMPERED AFTER RECEIPT\n")
    with pytest.raises(gate.GateError, match="DELIVERY-DRIFT"):
        gate.deliver(
            _deliver_args(
                run_dir, row["judge_id"], row["blind_session_id"], tmp_path / "late"
            )
        )


def test_exposure_diagnostic_carries_no_judge_or_blind_identifiers(
    finalized_bundle, tmp_path
):
    run_dir = _copy_bundle(finalized_bundle, tmp_path)
    ledger = _valid_ledger(run_dir)
    pair_by_blind = _map_by_blind(run_dir, "pair_id")
    rows = ledger["first_round_assignments"]
    first = rows[0]
    conflicting = next(
        row
        for row in rows
        if row["judge_id"] != first["judge_id"]
        and row["blind_session_id"] != first["blind_session_id"]
        and pair_by_blind[row["blind_session_id"]]
        == pair_by_blind[first["blind_session_id"]]
    )
    conflicting["judge_id"] = first["judge_id"]
    with pytest.raises(gate.GateError) as caught:
        gate.verify(_verify_args(run_dir, _write_ledger(tmp_path, ledger)))
    message = str(caught.value)
    assert "LEDGER-EXPOSURE" in message
    assert first["judge_id"] not in message
    assert "blind-" not in message


def test_fabricated_receipt_cannot_authorize_exposure_violating_delivery(
    finalized_bundle, tmp_path
):
    run_dir = _copy_bundle(finalized_bundle, tmp_path)
    ledger = _valid_ledger(run_dir)
    pair_by_blind = _map_by_blind(run_dir, "pair_id")
    rows = ledger["first_round_assignments"]
    first = rows[0]
    conflicting = next(
        row
        for row in rows
        if row["judge_id"] != first["judge_id"]
        and row["blind_session_id"] != first["blind_session_id"]
        and pair_by_blind[row["blind_session_id"]]
        == pair_by_blind[first["blind_session_id"]]
    )
    conflicting["judge_id"] = first["judge_id"]
    ledger_raw = runner._json_bytes(ledger)
    receipt = {
        "schema_version": "ideation-diversity-assignment-gate-receipt/1.0",
        "suite": runner.SUITE,
        "verdict": "pass",
        "ledger_sha256": hashlib.sha256(ledger_raw).hexdigest(),
        "ledger": ledger,
        "delivery_rule": (
            "deliver_exactly_one_isolated_packet_per_first_round_judge_assignment"
        ),
    }
    receipt_path = _receipt_path(run_dir)
    receipt_path.parent.mkdir(parents=True)
    receipt_path.write_bytes(runner._json_bytes(receipt))
    with pytest.raises(gate.GateError, match="LEDGER-EXPOSURE"):
        gate.deliver(
            _deliver_args(
                run_dir,
                first["judge_id"],
                first["blind_session_id"],
                tmp_path / "desk",
            )
        )


def test_fabricated_receipt_over_tampered_bundle_fails_delivery_replay(
    finalized_bundle, tmp_path
):
    run_dir = _copy_bundle(finalized_bundle, tmp_path)
    ledger = _valid_ledger(run_dir)
    map_path = run_dir / "blind" / "private" / "arm-map.json"
    private_map = json.loads(map_path.read_bytes())
    swap = private_map["mapping"][0]
    donor = next(
        row
        for row in private_map["mapping"]
        if row["pair_id"] != swap["pair_id"]
    )
    swap["pair_id"] = donor["pair_id"]
    tampered_raw = runner._json_bytes(private_map)
    map_path.write_bytes(tampered_raw)
    ledger["private_map_sha256"] = hashlib.sha256(tampered_raw).hexdigest()
    receipt = {
        "schema_version": "ideation-diversity-assignment-gate-receipt/1.0",
        "suite": runner.SUITE,
        "verdict": "pass",
        "ledger_sha256": hashlib.sha256(runner._json_bytes(ledger)).hexdigest(),
        "ledger": ledger,
        "delivery_rule": (
            "deliver_exactly_one_isolated_packet_per_first_round_judge_assignment"
        ),
    }
    receipt_path = _receipt_path(run_dir)
    receipt_path.parent.mkdir(parents=True)
    receipt_path.write_bytes(runner._json_bytes(receipt))
    row = ledger["first_round_assignments"][0]
    with pytest.raises(gate.GateError, match="DELIVERY-DRIFT"):
        gate.deliver(
            _deliver_args(
                run_dir, row["judge_id"], row["blind_session_id"], tmp_path / "desk"
            )
        )


def test_new_delivery_refuses_any_preexisting_destination(
    finalized_bundle, tmp_path
):
    run_dir = _copy_bundle(finalized_bundle, tmp_path)
    ledger = _valid_ledger(run_dir)
    gate.verify(_verify_args(run_dir, _write_ledger(tmp_path, ledger)))
    row = ledger["first_round_assignments"][0]
    empty_dest = tmp_path / "pre-existing-empty"
    empty_dest.mkdir()
    with pytest.raises(gate.GateError, match="DELIVERY-DEST"):
        gate.deliver(
            _deliver_args(
                run_dir, row["judge_id"], row["blind_session_id"], empty_dest
            )
        )


def test_concurrent_writer_racing_the_desk_fails_before_completion(
    finalized_bundle, tmp_path, monkeypatch
):
    run_dir = _copy_bundle(finalized_bundle, tmp_path)
    ledger = _valid_ledger(run_dir)
    gate.verify(_verify_args(run_dir, _write_ledger(tmp_path, ledger)))
    row = ledger["first_round_assignments"][0]
    dest = tmp_path / "desk"
    original = gate.envelope._ensure_exact_new

    def racing_writer(path, raw, **kwargs):
        original(path, raw, **kwargs)
        if path.parent == dest:
            (dest / "concurrent-other-packet.json").write_bytes(b"RACER\n")

    monkeypatch.setattr(gate.envelope, "_ensure_exact_new", racing_writer)
    with pytest.raises(gate.GateError, match="DELIVERY-DEST"):
        gate.deliver(
            _deliver_args(run_dir, row["judge_id"], row["blind_session_id"], dest)
        )
    monkeypatch.setattr(gate.envelope, "_ensure_exact_new", original)
    completion = (
        run_dir.parent
        / f"{run_dir.name}-assignment-gate"
        / "deliveries"
        / row["judge_id"]
        / f"{row['blind_session_id']}.completed.json"
    )
    assert not completion.exists()


def test_completed_delivery_is_never_reissued(finalized_bundle, tmp_path):
    run_dir = _copy_bundle(finalized_bundle, tmp_path)
    ledger = _valid_ledger(run_dir)
    gate.verify(_verify_args(run_dir, _write_ledger(tmp_path, ledger)))
    row = ledger["first_round_assignments"][0]
    dest = tmp_path / "desk"
    gate.deliver(
        _deliver_args(run_dir, row["judge_id"], row["blind_session_id"], dest)
    )
    delivered = dest / f"{row['blind_session_id']}.json"
    delivered.unlink()
    with pytest.raises(gate.GateError, match="DELIVERY-DUPLICATE"):
        gate.deliver(
            _deliver_args(run_dir, row["judge_id"], row["blind_session_id"], dest)
        )


def test_gate_artifacts_live_outside_the_run_and_keep_validate_run_green(
    finalized_bundle, tmp_path
):
    run_dir = _copy_bundle(finalized_bundle, tmp_path)
    ledger = _valid_ledger(run_dir)
    ledger_path = _write_ledger(tmp_path, ledger)
    gate.verify(_verify_args(run_dir, ledger_path))
    row = ledger["first_round_assignments"][0]
    gate.deliver(
        _deliver_args(run_dir, row["judge_id"], row["blind_session_id"], tmp_path / "desk")
    )
    assert _receipt_path(run_dir).is_file()
    assert not (run_dir / "assignment-gate-receipt.json").exists()
    plan_sha = hashlib.sha256((run_dir / "run-plan.json").read_bytes()).hexdigest()
    outcome = fixtures.runner.validate_run(
        fixtures._command_args(run_dir, plan_sha)
    )
    assert outcome["status"] == "blind_finalized"


def test_receipt_schema_validates_emitted_receipt(finalized_bundle, tmp_path):
    run_dir = _copy_bundle(finalized_bundle, tmp_path)
    ledger_path = _write_ledger(tmp_path, _valid_ledger(run_dir))
    gate.verify(_verify_args(run_dir, ledger_path))
    from jsonschema import Draft202012Validator

    schema = json.loads(
        (
            ROOT
            / "evals"
            / "heldout"
            / "within_session_ideation_diversity"
            / "assignment_gate_receipt.schema.json"
        ).read_bytes()
    )
    receipt = json.loads((_receipt_path(run_dir)).read_bytes())
    Draft202012Validator(schema).validate(receipt)
