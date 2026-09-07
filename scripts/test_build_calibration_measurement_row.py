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
        "output_sha256": hashlib.sha256(output_for(label).encode()).hexdigest(),
    }


def output_for(label: str) -> str:
    return f"# {label}\n\n### Decision: [Major Revision]\n" if label == "synthesis" else f"{label} output\n"


def write_raw(raw_dir: Path, labels) -> None:
    raw_dir.mkdir(parents=True, exist_ok=True)
    for label in labels:
        (raw_dir / f"{label}.md").write_text(output_for(label))


def provenance(**over):
    base = {
        "model_id": "claude-fable-5-1", "effort": "xhigh", "substrate_plan": "primary_only",
        "attempt_id": "attempt-1", "suite_commit": HEAD, "suite_commit_dirty": False,
        "credential_preflight": "ok",
    }
    base.update(over)
    return base


PANEL_LABELS = [f"seat-{s}" for s in dispatcher.SEATS] + ["synthesis"]


def make_work(tmp_path: Path, *, dirty=False, blocked=True) -> Path:
    work = tmp_path / "work"
    cards = work / "cards" / "p1"
    write_raw(cards / "raw", ["field_analyst"])
    (cards / "frozen.json").write_text(json.dumps({
        "suite": "reviewer_calibration", "stage": "cards", "paper_id": "p1", "status": "complete",
        **provenance(suite_commit_dirty=dirty), "calls": [call_row("field_analyst", 0)],
        "raw_bundle": "cards/p1/raw",
    }))
    runs = work / "runs"
    write_raw(runs / "2026-09-06-p1-r1" / "raw", PANEL_LABELS)
    (runs / "2026-09-06-p1-r1.json").write_text(json.dumps({
        "suite": "reviewer_calibration", "stage": "panel", "paper_id": "p1", "replicate": 1,
        "status": "complete", **provenance(suite_commit_dirty=dirty),
        "calls": [call_row(label, 2 + 2 * i) for i, label in enumerate(PANEL_LABELS)],
        "raw_bundle": "runs/2026-09-06-p1-r1/raw",
    }))
    if blocked:
        (runs / "blocked-2026-09-06-p2-r1.json").write_text(json.dumps({
            "suite": "reviewer_calibration", "stage": "panel", "paper_id": "p2", "replicate": 1,
            "status": "aborted", "abort_reason": "TransportFailure: x",
            **provenance(suite_commit_dirty=dirty), "calls": [], "raw_bundle": "runs/2026-09-06-p2-r1/raw",
        }))
    return work


def make_manifest(work: Path) -> None:
    assert dispatcher.main([
        "--stage", "manifest", "--work-dir", str(work), "--generated-at", "2026-09-06T13:00:00Z",
    ]) == 0


def make_metrics(tmp_path: Path, replicates=3) -> Path:
    path = tmp_path / "metrics.json"
    gold = tmp_path / "gold.json"
    gold.write_text(json.dumps({"labels": [{"paper_id": "p1", "label": "accept"}]}))
    bindings = mod.scorer.input_bindings(tmp_path / "work" / "runs", gold)
    collected, unresolved = mod.scorer.collect(tmp_path / "work" / "runs", {})
    assert not unresolved
    (tmp_path / "class-a-audit.json").write_text(json.dumps({
        "schema": "calibration-class-a-audit/1", "adjudicator": "blind maintainer",
        "blinded_to": ["expected_label", "venue_partition"],
        "panels": {"p1-r1": {
            "synthesis_sha256": bindings["synthesis_sha256"]["p1-r1"],
            "decision": "Major Revision", "raw": "### Decision: [Major Revision]",
            "criterion_ref": "grammar_confirmed",
        }},
    }))
    path.write_text(json.dumps({
        "suite": "reviewer_calibration", "tier": "full", "n_papers": 1,
        "gold_composition": {"accept": 1, "reject": 0}, "runs_per_paper": replicates,
        "confusion_matrix": {"tp": 1, "fn": 0, "fp": 0, "tn": 0},
        "metrics": {"balanced_accuracy": None, "FNR_over_harsh": 0.0, "FPR_lenient": None},
        "bootstrap_95ci": {}, "exact_label_agreement": {"count": 1, "share": 1.0},
        "replicate_stability": {"side_agreement_share": 1.0, "exact_agreement_share": 1.0},
        "auc": "NOT REPORTED", "blocked_runs": ["blocked-2026-09-06-p2-r1.json"],
        "input_bindings": bindings,
        "per_panel": {k: {kk: v for kk, v in row.items() if kk != "paper_id"}
                      for k, row in collected["panels"].items()},
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
        "--gold", str(tmp_path / "gold.json"), "--class-a-audit", str(tmp_path / "class-a-audit.json"),
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
    assert row["adjudication"]["resolution_direction"] == "bidirectional"
    assert row["aggregate"]["headline"]["estimand_status"] == "point_estimate"
    assert row["aggregate"]["agreement"] == {
        "rate": 0.5, "divergent_items": ["w2"],
        "note": row["aggregate"]["agreement"]["note"],
    }
    assert row["execution_manifest"]["sha256"] == mod.sha256_file(work / "execution-manifest.json")
    assert row["execution_manifest"]["claims"] == ["ordering"]
    assert row["attempts"]["blocked_runs"] == ["blocked-2026-09-06-p2-r1.json"]
    assert row["adjudication"]["overrides"][0]["criterion_ref"] == "B3"
    assert row["caveats"][0].startswith("HARNESS REHEARSAL")
    assert not any("lower bound" in c for c in row["caveats"])
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
    with pytest.raises(mod.PreconditionFailure, match="stale or foreign"):
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


# --- codex round 2 (2026-09-06) --------------------------------------------

def test_foreign_metrics_are_refused(tmp_path, pinned):
    work = make_work(tmp_path)
    make_manifest(work)
    metrics = make_metrics(tmp_path)
    payload = json.loads(metrics.read_text())
    payload["per_panel"]["p9-r1"] = {"replicate": 1, "attempt_id": "attempt-1", "decision": "Accept"}
    metrics.write_text(json.dumps(payload))
    with pytest.raises(mod.PreconditionFailure, match="foreign or partial"):
        mod.main(argv(tmp_path, work, metrics, make_judges(tmp_path, diverge=False)))
    payload["per_panel"] = {"p1-r1": {"replicate": 1, "attempt_id": "attempt-9", "decision": "Accept"}}
    metrics.write_text(json.dumps(payload))
    with pytest.raises(mod.PreconditionFailure, match="attempt_id"):
        mod.main(argv(tmp_path, work, metrics, make_judges(tmp_path, diverge=False)))


def test_edited_raw_output_is_refused(tmp_path, pinned):
    work = make_work(tmp_path)
    make_manifest(work)
    synthesis = work / "runs" / "2026-09-06-p1-r1" / "raw" / "synthesis.md"
    synthesis.write_text(synthesis.read_text().replace("Major Revision", "Accept"))
    with pytest.raises(mod.PreconditionFailure, match="no longer hashes"):
        mod.main(argv(tmp_path, work, make_metrics(tmp_path), make_judges(tmp_path, diverge=False)))


def test_unsupported_claim_is_refused_before_writing(tmp_path, pinned):
    work = make_work(tmp_path)
    make_manifest(work)
    with pytest.raises(mod.PreconditionFailure, match="concurrency"):
        mod.main(argv(tmp_path, work, make_metrics(tmp_path), make_judges(tmp_path, diverge=False), ["--claim", "concurrency"]))
    assert not (tmp_path / "row.json").exists()


def test_non_finite_metrics_are_refused(tmp_path, pinned):
    work = make_work(tmp_path)
    make_manifest(work)
    metrics = make_metrics(tmp_path)
    metrics.write_text(metrics.read_text().replace('"FNR_over_harsh": 0.0', '"FNR_over_harsh": NaN'))
    with pytest.raises(mod.PreconditionFailure, match="strict JSON"):
        mod.main(argv(tmp_path, work, metrics, make_judges(tmp_path, diverge=False)))


def test_judge_failure_ledger_satisfies_partial_coverage(tmp_path, pinned, capsys):
    work = make_work(tmp_path)
    make_manifest(work)
    judges = make_judges(tmp_path, diverge=False)
    rows = json.loads(judges.read_text())
    rows[1]["per_item"] = rows[1]["per_item"][:1]  # judge-2 never returned w2
    judges.write_text(json.dumps(rows))
    assert mod.main(argv(tmp_path, work, make_metrics(tmp_path), judges)) == 1
    assert "I11" in capsys.readouterr().err
    ok = argv(tmp_path, work, make_metrics(tmp_path), judges, [
        "--blocked-run", "judge-2 exhausted its retry on item w2 (transport failure)",
    ])
    assert mod.main(ok) == 0
    row = json.loads((tmp_path / "row.json").read_text())
    assert any("w2" in b for b in row["attempts"]["blocked_runs"])


def test_sha256_at_commit_reads_the_named_commit(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    env = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@x", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@x"}
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    (repo / "plan.md").write_text("v1\n")
    subprocess.run(["git", "add", "plan.md"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "v1"], cwd=repo, check=True, env={**env, "PATH": "/usr/bin:/bin:/opt/homebrew/bin"})
    first = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True, check=True).stdout.strip()
    (repo / "plan.md").write_text("v2\n")
    subprocess.run(["git", "commit", "-q", "-am", "v2"], cwd=repo, check=True, env={**env, "PATH": "/usr/bin:/bin:/opt/homebrew/bin"})
    assert mod.sha256_at_commit(first, "plan.md", repo=repo) == hashlib.sha256(b"v1\n").hexdigest()
    assert mod.sha256_at_commit("HEAD", "plan.md", repo=repo) == hashlib.sha256(b"v2\n").hexdigest()
    assert mod.sha256_at_commit(first, "missing.md", repo=repo) is None


@pytest.mark.parametrize("mutation,match", [
    ("coverage", "complete panel coverage"), ("hash", "hash mismatch"),
    ("decision", "decision differs"), ("excerpt", "verbatim raw"),
    ("blinding", "blinding"), ("criterion", "criterion"),
])
def test_class_a_audit_must_cover_and_match_every_synthesis(tmp_path, pinned, mutation, match):
    work = make_work(tmp_path)
    make_manifest(work)
    metrics = make_metrics(tmp_path)
    audit_path = tmp_path / "class-a-audit.json"
    audit = json.loads(audit_path.read_text())
    entry = audit["panels"]["p1-r1"]
    if mutation == "coverage":
        audit["panels"] = {}
    elif mutation == "blinding":
        audit["blinded_to"] = ["expected_label"]
    else:
        field, value = {"hash": ("synthesis_sha256", SHA), "decision": ("decision", "Reject"),
                        "excerpt": ("raw", "absent"), "criterion": ("criterion_ref", "A2")}[mutation]
        entry[field] = value
    audit_path.write_text(json.dumps(audit))
    with pytest.raises(mod.PreconditionFailure, match=match):
        mod.main(argv(tmp_path, work, metrics, make_judges(tmp_path, diverge=False)))
    assert not (tmp_path / "row.json").exists()


@pytest.mark.parametrize("changed", ["gold", "overrides", "severity", "missing_binding"])
def test_same_panel_ids_cannot_hide_different_scoring_inputs(tmp_path, pinned, changed):
    work = make_work(tmp_path)
    make_manifest(work)
    metrics = make_metrics(tmp_path)
    extra = []
    if changed == "gold":
        (tmp_path / "gold.json").write_text(json.dumps({"labels": [{"paper_id": "p1", "label": "reject"}]}))
    elif changed in ("overrides", "severity"):
        path = tmp_path / "new-input.json"
        path.write_text("{}" if changed == "overrides" else "[]")
        extra = ["--decision-overrides" if changed == "overrides" else "--severity-classifications", str(path)]
    else:
        payload = json.loads(metrics.read_text())
        del payload["input_bindings"]
        metrics.write_text(json.dumps(payload))
    with pytest.raises(mod.PreconditionFailure, match="input bindings differ"):
        mod.main(argv(tmp_path, work, metrics, make_judges(tmp_path, diverge=False), extra))


def test_class_a_correction_builds_without_a_fictitious_severity_judge_item(tmp_path, pinned):
    work = make_work(tmp_path)
    synthesis = work / "runs" / "2026-09-06-p1-r1" / "raw" / "synthesis.md"
    synthesis.write_text("Quoted example:\n### Decision: [Reject]\n\nFinal decision: Accept.\n")
    record_path = work / "runs" / "2026-09-06-p1-r1.json"
    record = json.loads(record_path.read_text())
    record["calls"][-1]["output_sha256"] = mod.sha256_file(synthesis)
    record_path.write_text(json.dumps(record))
    make_manifest(work)
    metrics = make_metrics(tmp_path, replicates=1)
    override_path = tmp_path / "decisions.json"
    override_path.write_text(json.dumps({"p1-r1": {"decision": "Accept", "raw": "Final decision: Accept."}}))
    assert mod.scorer.main([
        "--runs-dir", str(work / "runs"), "--gold", str(tmp_path / "gold.json"),
        "--overrides", str(override_path), "--replicates", "1", "--out", str(metrics),
    ]) == 0
    audit_path = tmp_path / "class-a-audit.json"
    audit = json.loads(audit_path.read_text())
    audit["panels"]["p1-r1"].update(decision="Accept", raw="Final decision: Accept.", criterion_ref="A3")
    audit_path.write_text(json.dumps(audit))
    assert mod.main(argv(tmp_path, work, metrics, make_judges(tmp_path, diverge=False), [
        "--decision-overrides", str(override_path), "--replicate-exception", "one synthetic rehearsal replicate",
    ])) == 0
    row = json.loads((tmp_path / "row.json").read_text())
    assert row["adjudication"]["overrides"] == []
    assert row["results"]["class_a_audit"]["record"] == audit
    assert row["results"]["per_panel_decisions"]["p1-r1"]["raw_decision"] == "Reject"
    assert row["results"]["per_panel_decisions"]["p1-r1"]["decision"] == "Accept"
