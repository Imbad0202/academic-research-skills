"""Mutation tests for build_calibration_measurement_row.py (#653 / #828)."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_calibration_measurement_row as mod
import dispatch_calibration_panel as dispatcher

pytest.importorskip("jsonschema")

HEAD = subprocess.run(
    ["git", "rev-parse", "HEAD"], cwd=mod.REPO, capture_output=True, text=True, check=True
).stdout.strip()
SHA = "0" * 64


def call_row(label, start, attempt=1):
    return {
        "call": label, "attempt": attempt, "started_at": f"2026-09-06T12:{start:02d}:00.000000Z",
        "completed_at": f"2026-09-06T12:{start + 1:02d}:00.000000Z", "outcome": "completed",
        "prompt_sha256": hashlib.sha256(label.encode()).hexdigest(),
        "output_sha256": hashlib.sha256((label + "out").encode()).hexdigest(),
    }


def provenance(**over):
    base = {
        "model_id": "claude-fable-5-1", "effort": "xhigh", "substrate_plan": "primary_only",
        "attempt_id": "attempt-1", "suite_commit": HEAD, "suite_commit_dirty": False,
        "credential_preflight": "ok",
    }
    base.update(over)
    return base


def make_work(tmp_path: Path, *, dirty=False, blocked=True) -> Path:
    work = tmp_path / "work"
    cards = work / "cards" / "p1"
    cards.mkdir(parents=True)
    (cards / "frozen.json").write_text(json.dumps({
        "suite": "reviewer_calibration", "stage": "cards", "paper_id": "p1", "status": "complete",
        **provenance(suite_commit_dirty=dirty), "calls": [call_row("field_analyst", 0)],
    }))
    runs = work / "runs"
    runs.mkdir()
    labels = [f"seat-{s}" for s in dispatcher.SEATS] + ["synthesis"]
    (runs / "2026-09-06-p1-r1.json").write_text(json.dumps({
        "suite": "reviewer_calibration", "stage": "panel", "paper_id": "p1", "replicate": 1,
        "status": "complete", **provenance(suite_commit_dirty=dirty),
        "calls": [call_row(label, 2 + 2 * i) for i, label in enumerate(labels)],
    }))
    if blocked:
        (runs / "blocked-2026-09-06-p2-r1.json").write_text(json.dumps({
            "suite": "reviewer_calibration", "stage": "panel", "status": "aborted",
            **provenance(suite_commit_dirty=dirty), "calls": [],
        }))
    return work


def make_manifest(work: Path) -> None:
    assert dispatcher.main([
        "--stage", "manifest", "--work-dir", str(work), "--generated-at", "2026-09-06T13:00:00Z",
    ]) == 0


def make_metrics(tmp_path: Path, replicates=3) -> Path:
    path = tmp_path / "metrics.json"
    path.write_text(json.dumps({
        "suite": "reviewer_calibration", "tier": "full", "n_papers": 1,
        "gold_composition": {"accept": 1, "reject": 0}, "runs_per_paper": replicates,
        "confusion_matrix": {"tp": 1, "fn": 0, "fp": 0, "tn": 0},
        "metrics": {"balanced_accuracy": None, "FNR_over_harsh": 0.0, "FPR_lenient": None},
        "bootstrap_95ci": {}, "exact_label_agreement": {"count": 1, "share": 1.0},
        "replicate_stability": {"side_agreement_share": 1.0, "exact_agreement_share": 1.0},
        "auc": "NOT REPORTED", "blocked_runs": ["blocked-2026-09-06-p2-r1.json"],
    }))
    return path


def make_judges(tmp_path: Path, families=("anthropic", "openai"), diverge=True) -> Path:
    rows = []
    for idx, family in enumerate(families):
        second = "med" if (diverge and idx == 1) else "low"
        rows.append({
            "judge_id": f"judge-{idx + 1}", "model_id": f"model-{family}", "model_family": family,
            "prompt_ref": "judge_template_v1", "evidence_provided": "seat weakness text only",
            "judging_budget": "1 call per item", "blinded_to": ["expected_label"],
            "per_item": [
                {"item_id": "w1", "severity_class": "high"},
                {"item_id": "w2", "severity_class": second},
            ],
        })
    path = tmp_path / "judges.json"
    path.write_text(json.dumps(rows))
    return path


def make_overrides(tmp_path: Path) -> Path:
    path = tmp_path / "overrides.json"
    path.write_text(json.dumps([{
        "item_id": "w2", "judge_id": "judge-2", "raw": "severity_class: med",
        "adjudicated": "low", "criterion_ref": "B3",
        "note": "seat cited an external checkable standard",
    }]))
    return path


def argv(tmp_path: Path, work: Path, metrics: Path, judges: Path, extra=()):
    return [
        "--work-dir", str(work), "--metrics", str(metrics), "--judges", str(judges),
        "--judge-template-version", "judge_template_v1", "--measurement-date", "2026-09-06",
        "--runs-ref", "evals/heldout/reviewer_calibration/runs/2026-09-06-attempt-1",
        "--verdict", "harness rehearsal", "--out", str(tmp_path / "row.json"), *extra,
    ]


@pytest.fixture()
def pinned(monkeypatch):
    """The plan/rubric at frozen_commit == the working tree (tree state is not a test input)."""
    monkeypatch.setattr(mod, "sha256_at_commit", lambda commit, rel: mod.sha256_file(mod.REPO / rel))


def test_row_builds_validates_and_is_write_once(tmp_path, pinned):
    work = make_work(tmp_path)
    make_manifest(work)
    args = argv(tmp_path, work, make_metrics(tmp_path), make_judges(tmp_path), [
        "--rehearsal", "--claim", "ordering", "--overrides", str(make_overrides(tmp_path)),
    ])
    assert mod.main(args) == 0
    row = json.loads((tmp_path / "row.json").read_text())
    assert row["measurement_contract"] == "heldout-measurement/1.1"
    assert row["preregistration"]["frozen_commit"] == HEAD == row["subject"]["config"]["suite_commit"]
    assert row["preregistration"]["plan_sha256"] == mod.sha256_file(mod.REPO / mod.PLAN_REF)
    assert row["adjudication"]["rubric_sha256"] == row["preregistration"]["rubric_sha256"]
    assert row["adjudication"]["resolution_direction"] == "flags_only"
    assert row["aggregate"]["headline"]["estimand_status"] == "lower_bound"
    assert row["aggregate"]["agreement"] == {
        "rate": 0.5, "divergent_items": ["w2"],
        "note": row["aggregate"]["agreement"]["note"],
    }
    assert row["execution_manifest"]["sha256"] == mod.sha256_file(work / "execution-manifest.json")
    assert row["execution_manifest"]["claims"] == ["ordering"]
    assert row["attempts"]["blocked_runs"] == ["blocked-2026-09-06-p2-r1.json"]
    assert row["adjudication"]["overrides"][0]["criterion_ref"] == "B3"
    assert row["caveats"][0].startswith("HARNESS REHEARSAL")
    assert any("lower bound" in c for c in row["caveats"])
    assert row["results"]["auc"] == "NOT REPORTED"
    with pytest.raises(mod.PreconditionFailure, match="write-once"):
        mod.main(args)


def test_dirty_commit_refuses(tmp_path, pinned):
    work = make_work(tmp_path, dirty=True)
    make_manifest(work)
    with pytest.raises(mod.PreconditionFailure, match="dirty"):
        mod.main(argv(tmp_path, work, make_metrics(tmp_path), make_judges(tmp_path)))
    assert not (tmp_path / "row.json").exists()


def test_plan_drift_since_freeze_refuses(tmp_path, monkeypatch):
    work = make_work(tmp_path)
    make_manifest(work)
    monkeypatch.setattr(mod, "sha256_at_commit", lambda commit, rel: SHA)
    with pytest.raises(mod.PreconditionFailure, match="changed since frozen_commit"):
        mod.main(argv(tmp_path, work, make_metrics(tmp_path), make_judges(tmp_path)))


def test_stale_manifest_refuses(tmp_path, pinned):
    work = make_work(tmp_path)
    make_manifest(work)
    manifest = json.loads((work / "execution-manifest.json").read_text())
    manifest["calls"] = manifest["calls"][:-1]
    (work / "execution-manifest.json").write_text(json.dumps(manifest))
    with pytest.raises(mod.PreconditionFailure, match="stale"):
        mod.main(argv(tmp_path, work, make_metrics(tmp_path), make_judges(tmp_path)))


def test_missing_manifest_refuses(tmp_path, pinned):
    work = make_work(tmp_path)
    with pytest.raises(mod.PreconditionFailure, match="manifest stage"):
        mod.main(argv(tmp_path, work, make_metrics(tmp_path), make_judges(tmp_path)))


def test_divergent_item_without_override_fails_contract(tmp_path, pinned, capsys):
    work = make_work(tmp_path)
    make_manifest(work)
    assert mod.main(argv(tmp_path, work, make_metrics(tmp_path), make_judges(tmp_path))) == 1
    assert "I10" in capsys.readouterr().err
    assert not (tmp_path / "row.json").exists()


def test_single_family_judges_fail_contract_and_write_nothing(tmp_path, pinned, capsys):
    work = make_work(tmp_path)
    make_manifest(work)
    judges = make_judges(tmp_path, families=("anthropic", "anthropic"), diverge=False)
    assert mod.main(argv(tmp_path, work, make_metrics(tmp_path), judges)) == 1
    assert "I2" in capsys.readouterr().err
    assert not (tmp_path / "row.json").exists()


def test_single_replicate_needs_written_exception(tmp_path, pinned, capsys):
    work = make_work(tmp_path)
    make_manifest(work)
    metrics = make_metrics(tmp_path, replicates=1)
    judges = make_judges(tmp_path, diverge=False)
    assert mod.main(argv(tmp_path, work, metrics, judges)) == 1
    assert "I6" in capsys.readouterr().err
    ok = argv(tmp_path, work, metrics, judges, [
        "--replicate-exception", "harness rehearsal: one replicate exercises the pipeline only",
    ])
    assert mod.main(ok) == 0


def test_empty_or_missing_judges_refuse(tmp_path, pinned):
    work = make_work(tmp_path)
    make_manifest(work)
    empty = tmp_path / "empty.json"
    empty.write_text("[]")
    with pytest.raises(mod.PreconditionFailure, match="judges"):
        mod.main(argv(tmp_path, work, make_metrics(tmp_path), empty))
