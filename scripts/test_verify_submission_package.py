#!/usr/bin/env python3
"""Tests for verify_submission_package — #394 Slice 1 (CLI skeleton + Family C).

Spec: docs/design/2026-06-10-394-submission-package-verifier-spec.md §3.3 / §5.1
/ §7.3 / §8. Mutation discipline per repo convention: every check has a fixture
that fails it and a test proving the failure fires.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import jsonschema
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES = REPO_ROOT / "scripts" / "fixtures" / "submission_package"
SCHEMA_PATH = (
    REPO_ROOT / "shared" / "contracts" / "submission"
    / "submission_verification_report.schema.json"
)
REPORT_BASENAME = "submission_verification_report.json"


def load_schema():
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def run_on(fixture_name, tmp_path, extra_args=()):
    """Copy a fixture package into tmp and run the CLI on the copy.

    Returns (exit_code, report_dict, package_dir). The copy keeps the repo
    fixture pristine (the CLI writes its report into the package dir).
    """
    from verify_submission_package import run

    package_dir = tmp_path / fixture_name
    shutil.copytree(FIXTURES / fixture_name, package_dir)
    rc = run([str(package_dir), *extra_args])
    report_path = package_dir / REPORT_BASENAME
    report = (
        json.loads(report_path.read_text(encoding="utf-8"))
        if report_path.is_file() else None
    )
    return rc, report, package_dir


def checks_by_id(report):
    return {c["id"]: c for c in report["checks"]}


# --- Round 1: clean package, joined marker path -----------------------------

def test_clean_package_all_pass_exit_0(tmp_path):
    rc, report, _ = run_on("clean", tmp_path)
    assert rc == 0
    by_id = checks_by_id(report)
    assert by_id["C1"]["status"] == "pass"
    assert by_id["C2"]["status"] == "pass"
    assert report["header"]["not_checked_count"] == 0


def test_clean_package_is_deterministic_joined_marker(tmp_path):
    _, report, _ = run_on("clean", tmp_path)
    assert report["header"]["extraction_path"] == "joined_marker"
    for c in report["checks"]:
        assert c["family"] == "reference_integrity"
        assert c["signal_class"] == "deterministic"
        assert c["strict_eligible"] is True


def test_clean_report_validates_against_schema(tmp_path):
    _, report, _ = run_on("clean", tmp_path)
    jsonschema.validate(report, load_schema())


def test_policy_slug_is_null_in_standalone_runs(tmp_path):
    # §5.2/§5.3: the script never reads terminal_policies; the slug is stamped
    # by the slice-4 orchestrator hook. A standalone run always emits null.
    _, report, _ = run_on("clean", tmp_path)
    assert report["header"]["policy_slug"] is None


def test_report_written_into_package_dir(tmp_path):
    _, _, package_dir = run_on("clean", tmp_path)
    assert (package_dir / REPORT_BASENAME).is_file()


# --- Round 2: fail / warn / NOT-CHECKED paths + exit codes -------------------

def test_orphan_intext_citation_fails_C1_exit_1(tmp_path):
    rc, report, _ = run_on("orphan_intext", tmp_path)
    assert rc == 1
    by_id = checks_by_id(report)
    assert by_id["C1"]["status"] == "fail"
    assert "ghost2024" in by_id["C1"]["detail"]
    assert by_id["C1"]["location"] == "paper.md"
    # The orphan is deterministic-classed on the joined marker path.
    assert by_id["C1"]["signal_class"] == "deterministic"
    assert by_id["C1"]["strict_eligible"] is True
    jsonschema.validate(report, load_schema())


def test_uncited_reference_entry_warns_C2_exit_0(tmp_path):
    # §3.3: uncited reference entry = warn (some venues allow further-reading
    # entries) — advisory, so the exit code stays 0.
    rc, report, _ = run_on("uncited_reference", tmp_path)
    assert rc == 0
    by_id = checks_by_id(report)
    assert by_id["C1"]["status"] == "pass"
    assert by_id["C2"]["status"] == "warn"
    assert "chenlee2023" in by_id["C2"]["detail"]


def test_markers_without_join_source_not_checked_exit_3(tmp_path):
    # §3.3 + §8 join test: markers present, passport supplies a corpus (a
    # reference list) but NO citation_verification_summary — never a guessed
    # comparison.
    passport = FIXTURES / "passports" / "corpus_only.yaml"
    rc, report, _ = run_on("marker_no_join", tmp_path,
                           extra_args=["--passport", str(passport)])
    assert rc == 3
    by_id = checks_by_id(report)
    for cid in ("C1", "C2"):
        assert by_id[cid]["status"] == "not_checked"
        assert "missing prose-reference join" in by_id[cid]["detail"]
    assert report["header"]["not_checked_count"] == 2
    assert report["header"]["extraction_path"] == "none"
    jsonschema.validate(report, load_schema())


def test_join_map_resolves_the_no_join_case(tmp_path):
    # The explicit scholar-supplied join map is a valid join source (§3.3) and
    # joins the prose slug to the corpus citation_key.
    passport = FIXTURES / "passports" / "corpus_only.yaml"
    join = tmp_path / "join.yaml"
    join.write_text("smith-feedback-2024: smith2024\n", encoding="utf-8")
    rc, report, _ = run_on(
        "marker_no_join", tmp_path,
        extra_args=["--passport", str(passport), "--join-map", str(join)])
    assert rc == 0
    by_id = checks_by_id(report)
    assert by_id["C1"]["status"] == "pass"
    assert by_id["C2"]["status"] == "pass"
    assert report["header"]["extraction_path"] == "joined_marker"


def test_missing_package_dir_is_usage_error(tmp_path):
    from verify_submission_package import run

    assert run([str(tmp_path / "does-not-exist")]) == 2


def test_unparseable_passport_is_usage_error(tmp_path):
    from verify_submission_package import run

    bad = tmp_path / "bad.yaml"
    bad.write_text("just a string\n", encoding="utf-8")
    package = tmp_path / "pkg"
    package.mkdir()
    (package / "paper.md").write_text("# x\n", encoding="utf-8")
    assert run([str(package), "--passport", str(bad)]) == 2


# --- Report schema structural contract --------------------------------------

def _minimal_report(**check_overrides):
    check = {
        "id": "C1",
        "family": "reference_integrity",
        "signal_class": "deterministic",
        "strict_eligible": True,
        "status": "pass",
        "detail": "ok",
        "location": None,
    }
    check.update(check_overrides)
    return {
        "header": {
            "extraction_path": "joined_marker",
            "not_checked_count": 0,
            "package_fingerprint": "0" * 64,
            "policy_slug": None,
        },
        "checks": [check],
    }


def test_schema_rejects_heuristic_strict_eligible():
    # §3.1/§6: heuristic checks are advisory-only STRUCTURALLY — the schema
    # itself forbids the promotion, not just the emitter.
    bad = _minimal_report(signal_class="heuristic", strict_eligible=True)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(bad, load_schema())
    ok = _minimal_report(signal_class="heuristic", strict_eligible=False)
    jsonschema.validate(ok, load_schema())


def test_schema_rejects_unknown_status():
    bad = _minimal_report(status="skipped")
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(bad, load_schema())
