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

from verify_submission_package import run

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES = REPO_ROOT / "scripts" / "fixtures" / "submission_package"
SCHEMA_PATH = (
    REPO_ROOT / "shared" / "contracts" / "submission"
    / "submission_verification_report.schema.json"
)
REPORT_BASENAME = "submission_verification_report.json"


def load_schema():
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def run_dir(package_dir, extra_args=()):
    """Run the CLI on a package dir; returns (exit_code, report_dict)."""
    rc = run([str(package_dir), *extra_args])
    report_path = package_dir / REPORT_BASENAME
    report = (
        json.loads(report_path.read_text(encoding="utf-8"))
        if report_path.is_file() else None
    )
    return rc, report


def run_on(fixture_name, tmp_path, extra_args=()):
    """Copy a fixture package into tmp and run the CLI on the copy.

    Returns (exit_code, report_dict, package_dir). The copy keeps the repo
    fixture pristine (the CLI writes its report into the package dir).
    """
    package_dir = tmp_path / fixture_name
    shutil.copytree(FIXTURES / fixture_name, package_dir)
    rc, report = run_dir(package_dir, extra_args)
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
    # strict_eligible is class-level: C1 promotable, C2 (warn-only) never —
    # asserted in test_C2_is_never_strict_eligible.


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
    assert run([str(tmp_path / "does-not-exist")]) == 2


def test_unparseable_passport_is_usage_error(tmp_path):

    bad = tmp_path / "bad.yaml"
    bad.write_text("just a string\n", encoding="utf-8")
    package = tmp_path / "pkg"
    package.mkdir()
    (package / "paper.md").write_text("# x\n", encoding="utf-8")
    assert run([str(package), "--passport", str(bad)]) == 2


# --- Round 3: fallback extraction, summary join, fingerprint -----------------

def test_fallback_latex_cite_extraction_is_heuristic_best_effort(tmp_path):
    # §3.3: post-converted sources fall back to \cite{} extraction; the header
    # downgrades to best-effort and the whole path is heuristic-classed
    # (advisory-only) — even a true orphan fail is NOT strict-eligible.
    rc, report, _ = run_on("fallback_latex", tmp_path)
    assert rc == 1
    assert report["header"]["extraction_path"] == "best_effort"
    by_id = checks_by_id(report)
    assert by_id["C1"]["status"] == "fail"
    assert "ghost2024" in by_id["C1"]["detail"]
    assert "smith2024" not in by_id["C1"]["detail"]
    for cid in ("C1", "C2"):
        assert by_id[cid]["signal_class"] == "heuristic"
        assert by_id[cid]["strict_eligible"] is False
    assert by_id["C2"]["status"] == "pass"
    jsonschema.validate(report, load_schema())


def test_fallback_authoryear_extraction_matches_bib_metadata(tmp_path):
    rc, report, _ = run_on("fallback_authoryear", tmp_path)
    assert rc == 1
    assert report["header"]["extraction_path"] == "best_effort"
    by_id = checks_by_id(report)
    # Only the unmatched (Nowhere, 2020) is an orphan; Smith (2024) narrative
    # and (Chen & Lee, 2023) parenthetical both join to bib metadata.
    assert by_id["C1"]["status"] == "fail"
    assert "nowhere" in by_id["C1"]["detail"].lower()
    assert "smith" not in by_id["C1"]["detail"].lower()
    assert "chen" not in by_id["C1"]["detail"].lower()
    # Both bib entries were cited, so C2 passes — and the references section
    # itself was not scanned as in-text prose.
    assert by_id["C2"]["status"] == "pass"
    assert by_id["C1"]["signal_class"] == "heuristic"


def test_summary_join_consumes_real_prose_join(tmp_path):
    # The prose slug (smith-feedback-2024) differs from the citation_key
    # (smith2024): a pass proves the citation_verification_summary join was
    # consumed, not an identity guess (§3.3).
    passport = FIXTURES / "passports" / "summary_join.yaml"
    rc, report, _ = run_on("summary_join", tmp_path,
                           extra_args=["--passport", str(passport)])
    assert rc == 0
    by_id = checks_by_id(report)
    assert by_id["C1"]["status"] == "pass"
    assert by_id["C2"]["status"] == "pass"
    assert report["header"]["extraction_path"] == "joined_marker"
    for cid in ("C1", "C2"):
        assert by_id[cid]["signal_class"] == "deterministic"


def test_no_machine_readable_reference_list_not_checked(tmp_path):
    package = tmp_path / "pkg"
    package.mkdir()
    (package / "paper.md").write_text(
        "Smith (2024) said things.\n", encoding="utf-8")
    rc = run([str(package)])
    report = json.loads(
        (package / REPORT_BASENAME).read_text(encoding="utf-8"))
    assert rc == 3
    for c in report["checks"]:
        assert c["status"] == "not_checked"
        assert "no machine-readable reference list" in c["detail"]


def test_fingerprint_follows_audit_snapshot_convention_excluding_report(tmp_path):
    # §10 open item 3 (adjudicated at slice 1): `<relative-path>:<sha256>`
    # lines, byte-sorted, trailing newline, fingerprint = sha256 of the
    # manifest text; the report file itself is excluded. Pinned here by an
    # independent reimplementation.
    import hashlib

    _, report, package_dir = run_on("clean", tmp_path)
    lines = []
    for p in sorted(package_dir.rglob("*")):
        if not p.is_file() or p.name == REPORT_BASENAME:
            continue
        digest = hashlib.sha256(p.read_bytes()).hexdigest()
        lines.append(f"{p.relative_to(package_dir).as_posix()}:{digest}")
    lines.sort()
    expected = hashlib.sha256(
        ("\n".join(lines) + "\n").encode("utf-8")).hexdigest()
    assert report["header"]["package_fingerprint"] == expected


def test_fingerprint_stable_across_reruns_with_report_present(tmp_path):
    # Second run sees the first run's report inside the package dir; the
    # exclusion keeps the fingerprint stable (freshness guard usable, §5.2).

    _, first, package_dir = run_on("clean", tmp_path)
    run([str(package_dir)])
    second = json.loads(
        (package_dir / REPORT_BASENAME).read_text(encoding="utf-8"))
    assert (second["header"]["package_fingerprint"]
            == first["header"]["package_fingerprint"])


# --- Codex review round: P1 partial-join identity guess + P2s ----------------

def test_partial_summary_join_never_falls_back_to_identity(tmp_path):
    # P1: a marker slug ABSENT from the join source must never be compared via
    # an identity guess — even (especially) when the slug coincidentally equals
    # a citation_key in the reference list (§3.3 "never a guessed comparison").
    package = tmp_path / "pkg"
    package.mkdir()
    (package / "paper.md").write_text(
        "Joined (Smith, 2024) <!--ref:smith-feedback-2024-->.\n"
        "Unjoined but key-shaped (Smith, 2024) <!--ref:smith2024-->.\n",
        encoding="utf-8")
    passport = FIXTURES / "passports" / "summary_join.yaml"
    rc = run([str(package), "--passport", str(passport)])
    report = json.loads(
        (package / REPORT_BASENAME).read_text(encoding="utf-8"))
    assert rc == 1
    by_id = checks_by_id(report)
    assert by_id["C1"]["status"] == "fail"
    assert "no join entry" in by_id["C1"]["detail"]
    assert "smith2024" in by_id["C1"]["detail"]


def test_C2_is_never_strict_eligible(tmp_path):
    # P2: C2's worst outcome is warn, which is advisory-only and never
    # policy-promotable (§5.3) — so the check itself is not strict-eligible,
    # even on the deterministic path.
    _, report, _ = run_on("clean", tmp_path)
    by_id = checks_by_id(report)
    assert by_id["C1"]["strict_eligible"] is True
    assert by_id["C2"]["strict_eligible"] is False


def test_custom_report_out_inside_package_excluded_from_fingerprint(tmp_path):
    # P2: a --report-out path inside the package must be excluded from the
    # fingerprint like the default basename, or reruns self-reference.

    package = tmp_path / "clean"
    shutil.copytree(FIXTURES / "clean", package)
    out = package / "custom_report.json"
    run([str(package), "--report-out", str(out)])
    first = json.loads(out.read_text(encoding="utf-8"))
    run([str(package), "--report-out", str(out)])
    second = json.loads(out.read_text(encoding="utf-8"))
    assert (first["header"]["package_fingerprint"]
            == second["header"]["package_fingerprint"])


def test_authoryear_fallback_tolerates_page_locators(tmp_path):
    # P3: `Smith (2024, p. 12)` / `(Chen & Lee, 2023, pp. 45–67)` are common
    # locator forms; missing them creates avoidable fallback false orphans.
    package = tmp_path / "pkg"
    package.mkdir()
    (package / "paper.md").write_text(
        "Smith (2024, p. 12) framed it; details follow "
        "(Chen & Lee, 2023, pp. 45–67).\n", encoding="utf-8")
    shutil.copy(FIXTURES / "fallback_authoryear" / "references.bib",
                package / "references.bib")
    rc = run([str(package)])
    report = json.loads(
        (package / REPORT_BASENAME).read_text(encoding="utf-8"))
    by_id = checks_by_id(report)
    assert rc == 0
    assert by_id["C1"]["status"] == "pass"
    assert by_id["C2"]["status"] == "pass"


def test_schema_rejects_warn_with_strict_eligible():
    # P2: warn is advisory-only and never policy-promotable — tightened
    # structurally like the heuristic exclusion.
    bad = _minimal_report(status="warn", strict_eligible=True)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(bad, load_schema())
    ok = _minimal_report(status="warn", strict_eligible=False)
    jsonschema.validate(ok, load_schema())


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


def test_schema_binds_check_id_prefix_to_family():
    # The id prefix encodes the family (spec §3 tables); the contract binds
    # them so a later-slice emitter cannot ship mismatched pairs.
    bad = _minimal_report(id="C1", family="blind_review_residue")
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(bad, load_schema())
    bad2 = _minimal_report(id="A1", family="reference_integrity")
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(bad2, load_schema())


def test_schema_rejects_unknown_status():
    bad = _minimal_report(status="skipped")
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(bad, load_schema())
