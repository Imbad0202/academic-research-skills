#!/usr/bin/env python3
"""Tests for scripts/extract_panel_claims.py (#1002). Synthetic bundles only."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

import extract_panel_claims as epc  # noqa: E402

PASS = "PHASE-CONFORMANCE: PASS\n"


def _seat_report(weaknesses: list[str]) -> str:
    body = ["## Dimension Scores", "", "### D1: methodology_rigor", "x", "", "## Review Body", "",
            "### S1: A strength", "Not a claim here.", "", "**Evidence Anchor**: text: §1 \"a\"", ""]
    for n, title in enumerate(weaknesses, start=1):
        body += [f"### W{n}: {title}", f"Body of {title}.", "",
                 f"**Evidence Anchor**: text: §2 \"{title}\"", ""]
    body += ["## Scoring Plan Dissent", "none"]
    return "\n".join(body) + "\n"


DA_REPORT = """## Dimension Scores

### D1: methodology_rigor
x

## Review Body

Prose before the tables.

#### CRITICAL

| # | Issue | Why it matters | Evidence Anchor | Confidence |
|---|---|---|---|---|
| C1 | Causal claim from a survey | The design forbids it | text: §5 "improved" | 5 |

#### MAJOR

| # | Issue | Evidence Anchor | Confidence (1-5) |
|---|---|---|---|
| M1 | Sampling described two ways | text: §3 "random" | 4 |
| M2 | Unreported attrition | absence: §3 — expected attrition counts; checked §3, §4 | 3 |
"""


def _bundle(runs: Path, name: str, *, eligible=True, seats=None, fail=()):
    bundle = runs / "raw" / name
    bundle.mkdir(parents=True)
    seats = seats or {s: _seat_report([f"{s} weakness {i}" for i in (1, 2)]) for s in epc.W_SEATS}
    for seat, text in seats.items():
        (bundle / f"{seat}.phase2.a1.md").write_text(text, encoding="utf-8")
        (bundle / f"{seat}.phase2.a1.gate.log").write_text(
            "[PHASE2-GRAMMAR: bad]\n" if seat in fail else PASS, encoding="utf-8")
    (bundle / "da.phase2.a1.md").write_text(DA_REPORT, encoding="utf-8")
    (bundle / "da.phase2.a1.gate.log").write_text(PASS, encoding="utf-8")
    record = {"score_eligible": eligible, "raw_bundle": f"raw/{name}/", "fixture": "ms00_clean",
              "condition": "baseline", "replicate": 1}
    (runs / f"{name}.json").write_text(json.dumps(record), encoding="utf-8")
    return bundle


def test_w_subsections_are_claims_and_strengths_are_not():
    claims = epc.w_claims(_seat_report(["Alpha", "Beta"]))
    assert [c[0] for c in claims] == ["W1", "W2"]
    assert claims[0][1] == 'Alpha\nBody of Alpha.\n\n**Evidence Anchor**: text: §2 "Alpha"'
    assert all("strength" not in text.lower() for _id, text in claims)


def test_da_rows_read_like_weaknesses():
    claims = epc.da_claims(DA_REPORT, "da.md")
    assert [c[0] for c in claims] == ["C1", "M1", "M2"]
    assert claims[0][1] == ('Causal claim from a survey\n\nThe design forbids it'
                            '\n\n**Evidence Anchor**: text: §5 "improved"')
    assert "Confidence" not in claims[1][1] and "Issue:" not in claims[1][1]
    assert claims[1][1].endswith('**Evidence Anchor**: text: §3 "random"')


def test_a_lower_heading_inside_a_weakness_does_not_end_it():
    text = _seat_report(["Alpha"]).replace("Body of Alpha.", "Body of Alpha.\n\n#### Detail\nMore text.")
    claims = epc.w_claims(text)
    assert len(claims) == 1 and "More text." in claims[0][1] and "**Evidence Anchor**" in claims[0][1]


def test_only_score_eligible_bundles_are_read(tmp_path):
    _bundle(tmp_path, "b1")
    _bundle(tmp_path, "b2", eligible=False)
    claims, key, summary = epc.extract(tmp_path)
    assert summary["bundles"] == 1 and {c["bundle"] for c in claims} == {"b1"}
    assert summary["by_seat"] == {"eic": 2, "methodology": 2, "domain": 2, "perspective": 2, "da": 3}
    assert summary["claims"] == len(claims) == len(key) == 11


def test_the_highest_passing_attempt_is_read(tmp_path):
    bundle = _bundle(tmp_path, "b1")
    (bundle / "eic.phase2.a2.md").write_text(_seat_report(["Second try"]), encoding="utf-8")
    (bundle / "eic.phase2.a2.gate.log").write_text(PASS, encoding="utf-8")
    (bundle / "eic.phase2.a3.md").write_text(_seat_report(["Failed third"]), encoding="utf-8")
    (bundle / "eic.phase2.a3.gate.log").write_text("[ANCHOR-INVALID: x]\n", encoding="utf-8")
    assert epc.passing_attempt(bundle, "eic").name == "eic.phase2.a2.md"
    _claims, key, _summary = epc.extract(tmp_path)
    assert [k["finding_id"] for k in key if k["seat"] == "eic"] == ["W1"]


def test_a_seat_with_no_passing_attempt_is_listed(tmp_path):
    _bundle(tmp_path, "b1", fail=("domain",))
    _claims, _key, summary = epc.extract(tmp_path)
    assert summary["seats_without_passing_attempt"] == ["b1/domain"]
    assert summary["by_seat"]["domain"] == 0


def test_an_unparsable_da_report_is_listed_not_fatal(tmp_path):
    bundle = _bundle(tmp_path, "b1")
    (bundle / "da.phase2.a1.md").write_text("## Review Body\n\nno tables\n", encoding="utf-8")
    _claims, _key, summary = epc.extract(tmp_path)
    assert summary["unparsed_da_reports"] == ["b1/da.phase2.a1.md"]


def test_the_auditor_file_hides_the_seat(tmp_path):
    _bundle(tmp_path, "b1")
    claims, key, _summary = epc.extract(tmp_path)
    assert set(claims[0]) == {"claim_id", "bundle", "fixture", "text"}
    assert [c["claim_id"] for c in claims] == [f"c{n:04d}" for n in range(1, 12)]
    seats_in_order = [k["seat"] for k in key]
    assert seats_in_order != sorted(seats_in_order)  # hash order, not grouped by seat
    for claim in claims:
        for seat in ("EIC", "Devil", "Domain Reviewer", "Perspective Reviewer"):
            assert seat not in claim["text"]


def test_order_is_stable_across_runs(tmp_path):
    _bundle(tmp_path, "b1")
    first = epc.extract(tmp_path)[1]
    assert epc.extract(tmp_path)[1] == first


def test_cli_writes_both_files_and_prints_counts_last(tmp_path, capsys):
    _bundle(tmp_path / "runs", "b1")
    out = tmp_path / "out"
    assert epc.main(["--runs", str(tmp_path / "runs"), "--out", str(out)]) == 0
    last = capsys.readouterr().out.strip().splitlines()[-1]
    assert json.loads(last)["claims"] == 11
    assert len((out / "claims.jsonl").read_text(encoding="utf-8").splitlines()) == 11
    assert epc.main(["--runs", str(tmp_path / "empty"), "--out", str(out)]) == 2


@pytest.mark.parametrize("seat", epc.W_SEATS)
def test_counts_match_a_plain_heading_count(tmp_path, seat):
    """The extractor finds every W heading a line count finds."""
    bundle = _bundle(tmp_path, "b1")
    text = (bundle / f"{seat}.phase2.a1.md").read_text(encoding="utf-8")
    expected = sum(1 for line in text.splitlines() if line.startswith("### W"))
    assert len(epc.w_claims(text)) == expected


def test_counts_must_match_the_expected_inventory(tmp_path, capsys):
    _bundle(tmp_path / "runs", "b1")
    out = tmp_path / "out"
    args = ["--runs", str(tmp_path / "runs"), "--out", str(out)]
    assert epc.main(args + ["--expect-bundles", "1", "--expect-claims", "11"]) == 0
    assert epc.main(args + ["--expect-bundles", "1", "--expect-claims", "12"]) == 1
    summary = json.loads((out / "summary.json").read_text(encoding="utf-8"))
    assert summary["problems"] == ["claims: 11 != expected 12"]
    capsys.readouterr()


def test_a_failed_seat_fails_the_run(tmp_path, capsys):
    _bundle(tmp_path / "runs", "b1", fail=("domain",))
    assert epc.main(["--runs", str(tmp_path / "runs"), "--out", str(tmp_path / "out")]) == 1
    capsys.readouterr()


def test_a_raw_bundle_outside_runs_raw_is_refused(tmp_path):
    runs = tmp_path / "suite" / "runs"
    _bundle(runs, "b1")
    secret = tmp_path / "suite" / "manifests" / "b2"
    secret.mkdir(parents=True)
    (secret / "eic.phase2.a1.md").write_text(_seat_report(["Leak"]), encoding="utf-8")
    (secret / "eic.phase2.a1.gate.log").write_text(PASS, encoding="utf-8")
    for name, raw in (("b2", "../manifests/b2/"), ("b3", str(secret))):
        (runs / f"{name}.json").write_text(json.dumps({"score_eligible": True, "raw_bundle": raw,
                                                       "fixture": "ms00_clean"}), encoding="utf-8")
    claims, _key, summary = epc.extract(runs)
    assert sorted(summary["refused_bundle_paths"]) == ["b2.json", "b3.json"]
    assert all("Leak" not in c["text"] for c in claims)


def test_a_symlinked_report_is_refused(tmp_path):
    runs = tmp_path / "runs"
    bundle = _bundle(runs, "b1")
    outside = tmp_path / "outside.md"
    outside.write_text(_seat_report(["Leak"]), encoding="utf-8")
    (bundle / "eic.phase2.a1.md").unlink()
    (bundle / "eic.phase2.a1.md").symlink_to(outside)
    claims, _key, summary = epc.extract(runs)
    assert summary["refused_bundle_paths"] == ["b1/eic.phase2.a1.md"]
    assert all("Leak" not in c["text"] for c in claims)


def test_the_manifests_directory_is_refused_as_runs(tmp_path):
    (tmp_path / "manifests").mkdir()
    with pytest.raises(SystemExit):
        epc.extract(tmp_path / "manifests" / ".." / "manifests" / "x" / "..")


def test_a_symlinked_gate_log_or_run_record_is_not_read(tmp_path):
    runs = tmp_path / "runs"
    bundle = _bundle(runs, "b1")
    outside = tmp_path / "outside.log"
    outside.write_text(PASS, encoding="utf-8")
    (bundle / "eic.phase2.a1.gate.log").unlink()
    (bundle / "eic.phase2.a1.gate.log").symlink_to(outside)
    record = tmp_path / "record.json"
    record.write_text(json.dumps({"score_eligible": True, "raw_bundle": "raw/b1/", "fixture": "ms00_clean"}),
                      encoding="utf-8")
    (runs / "b2.json").symlink_to(record)
    _claims, _key, summary = epc.extract(runs)
    assert summary["seats_without_passing_attempt"] == ["b1/eic"]
    assert summary["refused_bundle_paths"] == ["b2.json"]


def test_the_suite_manifests_directory_is_refused_whatever_runs_says():
    with pytest.raises(SystemExit):
        epc.extract(epc.MANIFESTS / "subdir")


def test_a_second_record_for_the_same_bundle_is_listed_not_read(tmp_path, capsys):
    runs = tmp_path / "runs"
    _bundle(runs, "b1")
    (runs / "b1-copy.json").write_text((runs / "b1.json").read_text(encoding="utf-8"), encoding="utf-8")
    claims, _key, summary = epc.extract(runs)
    assert summary["bundles"] == 1 and len(claims) == 11
    assert summary["duplicate_bundle_records"] == ["b1.json"]
    assert epc.main(["--runs", str(runs), "--out", str(tmp_path / "out")]) == 1
    capsys.readouterr()
