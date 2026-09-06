"""Mutation tests for score_calibration_run.py (#653). Synthetic runs, offline."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import score_calibration_run as mod


def write_panel(runs_dir: Path, paper: str, replicate: int, decision: str,
                synthesis: str | None = None) -> None:
    stem = f"2026-08-07-{paper}-r{replicate}"
    raw = runs_dir / stem / "raw"
    raw.mkdir(parents=True)
    (runs_dir / f"{stem}.json").write_text(
        json.dumps(
            {
                "suite": "reviewer_calibration",
                "stage": "panel",
                "paper_id": paper,
                "replicate": replicate,
                "raw_bundle": f"runs/{stem}/raw",
                "status": "complete",
            }
        ),
        encoding="utf-8",
    )
    (raw / "synthesis.md").write_text(
        synthesis if synthesis is not None else f"### Decision: [{decision}]\n",
        encoding="utf-8",
    )
    for seat in ("eic", "methodology", "domain", "perspective", "da"):
        (raw / f"seat-{seat}.md").write_text("categorical seat report\n", encoding="utf-8")


def write_gold(tmp_path: Path, labels: dict[str, str]) -> Path:
    path = tmp_path / "gold_labels.json"
    path.write_text(
        json.dumps({"labels": [{"paper_id": k, "label": v} for k, v in labels.items()]}),
        encoding="utf-8",
    )
    return path


def run(tmp_path: Path, runs_dir: Path, gold: Path, **kw) -> tuple[int, dict | None]:
    out = tmp_path / "metrics.json"
    argv = ["--runs-dir", str(runs_dir), "--gold", str(gold), "--out", str(out),
            "--replicates", str(kw.pop("replicates", 3))]
    for flag, value in kw.items():
        argv += [f"--{flag.replace('_', '-')}", str(value)]
    rc = mod.main(argv)
    return rc, json.loads(out.read_text()) if out.is_file() else None


@pytest.fixture()
def standard(tmp_path):
    """4 papers x 3 replicates: a1 harsh-miss, a2 correct, j1 lenient-miss, j2 correct."""
    runs = tmp_path / "runs"
    plan = {
        "a1": ["Major Revision", "Major Revision", "Accept"],   # majority negative, gold accept -> FN
        "a2": ["Accept", "Minor Revision", "Accept"],           # positive, gold accept -> TP
        "j1": ["Minor Revision", "Accept", "Minor Revision"],   # positive, gold reject -> FP
        "j2": ["Reject", "Major Revision", "Reject"],           # negative, gold reject -> TN
    }
    for paper, decisions in plan.items():
        for i, decision in enumerate(decisions, start=1):
            write_panel(runs, paper, i, decision)
    gold = write_gold(tmp_path, {"a1": "accept", "a2": "accept", "j1": "reject", "j2": "reject"})
    return {"tmp": tmp_path, "runs": runs, "gold": gold}


def test_confusion_and_metrics(standard):
    rc, result = run(standard["tmp"], standard["runs"], standard["gold"])
    assert rc == 0
    assert result["confusion_matrix"] == {"TP": 1, "FN": 1, "TN": 1, "FP": 1}
    assert result["metrics"]["balanced_accuracy"] == 0.5
    assert result["metrics"]["FNR_over_harsh"] == 0.5
    assert result["metrics"]["FPR_lenient"] == 0.5
    assert result["gold_composition"] == {"accept": 2, "reject": 2}


def test_exact_agreement_and_stability_are_categorical(standard):
    rc, result = run(standard["tmp"], standard["runs"], standard["gold"])
    # exact modes: a1 Major Revision, a2 Accept (=gold), j1 Minor Revision, j2 Reject (=gold)
    assert result["exact_label_agreement"]["count"] == 2
    assert result["exact_label_agreement"]["share"] == 0.5
    # side agreement: a1 splits (neg,neg,pos), a2 all positive, j1 all positive, j2 all negative
    assert result["replicate_stability"]["side_agreement_share"] == 0.75
    assert result["replicate_stability"]["exact_agreement_share"] == 0.0
    assert result["auc"].startswith("NOT REPORTED")
    assert "panel_score" not in next(iter(result["per_panel"].values()))


def test_bootstrap_is_deterministic(standard):
    _, first = run(standard["tmp"], standard["runs"], standard["gold"])
    _, second = run(standard["tmp"], standard["runs"], standard["gold"])
    assert first["bootstrap_95ci"] == second["bootstrap_95ci"]
    ci = first["bootstrap_95ci"]["balanced_accuracy"]
    assert 0 <= ci["lo"] <= ci["hi"] <= 1


def test_honest_gaps_are_printed(standard):
    _, result = run(standard["tmp"], standard["runs"], standard["gold"])
    assert result["minor_major_boundary_submatrix"].startswith("NOT ESTIMABLE")
    assert result["per_dimension_calibration_error"].startswith("NOT COMPUTABLE")
    assert result["severity_miscalibration_histogram"]["status"] == "pending"


def test_ambiguous_decision_blocks_metrics(standard, capsys):
    write_panel(standard["runs"], "a3", 1, "", synthesis="no decision line here\n")
    rc, _ = run(standard["tmp"], standard["runs"], standard["gold"])
    assert rc == 1
    assert "a3-r1" in capsys.readouterr().err


def test_override_resolves_ambiguity(tmp_path):
    runs = tmp_path / "runs"
    write_panel(runs, "p1", 1, "Accept")
    write_panel(runs, "p1", 2, "", synthesis="prose without a verdict\n")
    write_panel(runs, "p1", 3, "Accept")
    write_panel(runs, "n1", 1, "Reject")
    write_panel(runs, "n1", 2, "Reject")
    write_panel(runs, "n1", 3, "Reject")
    gold = write_gold(tmp_path, {"p1": "accept", "n1": "reject"})
    overrides = tmp_path / "overrides.json"
    overrides.write_text(
        json.dumps({"p1-r2": {"decision": "Minor Revision", "raw": "prose without a verdict"}}),
        encoding="utf-8",
    )
    rc, result = run(tmp_path, runs, gold, overrides=str(overrides))
    assert rc == 0
    assert result["per_panel"]["p1-r2"]["decision_status"] == "adjudicated"
    assert result["confusion_matrix"] == {"TP": 1, "FN": 0, "TN": 1, "FP": 0}


def test_partial_ensemble_refused(standard):
    write_panel(standard["runs"], "a3", 1, "Accept")
    gold = write_gold(
        standard["tmp"],
        {"a1": "accept", "a2": "accept", "j1": "reject", "j2": "reject", "a3": "accept"},
    )
    with pytest.raises(SystemExit, match="partial ensemble"):
        run(standard["tmp"], standard["runs"], gold)


def test_multiple_distinct_decisions_flagged(standard, capsys):
    write_panel(
        standard["runs"], "a4", 1, "",
        synthesis="### Decision: [Accept]\n...\n### Decision: [Reject]\n",
    )
    rc, _ = run(standard["tmp"], standard["runs"], standard["gold"])
    assert rc == 1
    assert "multiple_distinct_decisions" in capsys.readouterr().err


def test_severity_histogram_computed(standard):
    rows = [{"panel": "a1-r1", "weakness_id": "w1", "risk": "high"},
            {"panel": "a1-r1", "weakness_id": "w2", "risk": "low"},
            {"panel": "a2-r2", "weakness_id": "w1", "risk": "low"}]
    path = standard["tmp"] / "severity.json"
    path.write_text(json.dumps(rows), encoding="utf-8")
    _, result = run(
        standard["tmp"], standard["runs"], standard["gold"],
        severity_classifications=str(path),
    )
    hist = result["severity_miscalibration_histogram"]
    assert hist["counts"] == {"low": 2, "med": 0, "high": 1}
    assert hist["shares"]["high"] == round(1 / 3, 4)


def test_missing_gold_label_refused(standard):
    gold = write_gold(standard["tmp"], {"a1": "accept", "a2": "accept", "j1": "reject"})
    with pytest.raises(SystemExit, match="without gold labels"):
        run(standard["tmp"], standard["runs"], gold)


def test_blocked_records_listed_not_scored(standard):
    (standard["runs"] / "blocked-2026-08-07-a9-r1.json").write_text(
        json.dumps({"suite": "reviewer_calibration", "status": "aborted"}), encoding="utf-8"
    )
    rc, result = run(standard["tmp"], standard["runs"], standard["gold"])
    assert rc == 0
    assert result["blocked_runs"] == ["blocked-2026-08-07-a9-r1.json"]


def test_decision_extraction_grammar():
    assert mod.extract_decision("### Decision: Accept\n") == ("Accept", "extracted")
    assert mod.extract_decision("### Decision: [Minor Revision]\n")[0] == "Minor Revision"
    assert mod.extract_decision("## Decision: Reject\n")[0] == "Reject"
    assert mod.extract_decision("Decision: Accept\n")[0] is None  # needs a heading line
    assert mod.extract_decision("### Decision: Weak Accept\n")[0] is None  # closed set


def test_gold_paper_without_results_blocks_full_tier(tmp_path):
    runs = tmp_path / "runs"
    for r in (1, 2, 3):
        write_panel(runs, "p1", r, "Accept")
    gold = write_gold(tmp_path, {"p1": "accept", "n1": "reject"})
    with pytest.raises(SystemExit, match="without a complete scored ensemble"):
        run(tmp_path, runs, gold)


def test_duplicate_panel_record_refused(tmp_path):
    runs = tmp_path / "runs"
    for r in (1, 2, 3):
        write_panel(runs, "p1", r, "Accept")
    stem = "2026-08-09-p1-r1"  # a second record for p1-r1 under another stem
    raw = runs / stem / "raw"
    raw.mkdir(parents=True)
    (runs / f"{stem}.json").write_text(json.dumps({
        "suite": "reviewer_calibration", "stage": "panel", "paper_id": "p1",
        "replicate": 1, "raw_bundle": f"runs/{stem}/raw", "status": "complete",
    }), encoding="utf-8")
    (raw / "synthesis.md").write_text("### Decision: [Reject]\n", encoding="utf-8")
    gold = write_gold(tmp_path, {"p1": "accept"})
    with pytest.raises(SystemExit, match="duplicate panel record"):
        run(tmp_path, runs, gold)


def test_override_without_raw_excerpt_is_not_accepted(tmp_path):
    runs = tmp_path / "runs"
    write_panel(runs, "p1", 1, "Accept")
    write_panel(runs, "p1", 2, "", synthesis="prose without a verdict\n")
    write_panel(runs, "p1", 3, "Accept")
    gold = write_gold(tmp_path, {"p1": "accept"})
    overrides = tmp_path / "overrides.json"
    overrides.write_text(json.dumps({"p1-r2": {"decision": "Minor Revision"}}), encoding="utf-8")
    rc, result = run(tmp_path, runs, gold, overrides=str(overrides))
    assert rc == 1 and result is None
