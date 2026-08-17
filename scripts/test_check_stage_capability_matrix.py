#!/usr/bin/env python3
"""Mutation tests for scripts/check_stage_capability_matrix.py (#745).

One failing witness per invariant branch (repo lint-test convention): each test
mutates a copy of a valid matrix and asserts the exact invariant fires. The
shipped matrix itself must pass (the zero-mutation baseline), and the shipped
generated view must be byte-identical to the renderer's output.
"""
from __future__ import annotations

import datetime
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

from check_stage_capability_matrix import (  # noqa: E402
    DEFAULT_MATRIX,
    DEFAULT_VIEW,
    TASK_FAMILIES,
    render,
    run,
)

TODAY = datetime.date(2026, 8, 17)


def _valid_matrix() -> dict:
    """Small synthetic matrix that satisfies every invariant."""
    rows = []
    for i, family in enumerate(TASK_FAMILIES):
        rows.append(
            {
                "row_id": f"{family}.core",
                "task_family": family,
                "mechanism": f"Synthetic mechanism {i}",
                "mechanism_status": "IMPLEMENTED",
                "deterministic_conformance": "CI_GATED",
                "conformance_pinned_by": [
                    "scripts/check_stage_capability_matrix.py::run"
                ],
                "behavioral_evidence": {"status": "NOT_RUN"},
                "external_outcome_evidence": "none",
                "known_exclusions": ["synthetic exclusion"],
                "transport_limits": ["single model family"],
                "max_licensed_claim": "A mechanism exists; no behavioral claim.",
                "next_required_evaluation": "run the seeded suite",
            }
        )
    rows[0]["behavioral_evidence"] = {
        "status": "MEASURED",
        "eval_ref": "evals/heldout/revision_claim_drift",
        "measurement_report": (
            "evals/heldout/revision_claim_drift/measurement-2026-08-07.json"
        ),
        "model": "claude-fable-5",
        "population": "synthetic fixtures",
        "measured_at": "2026-08-07",
        "result_summary": "3/8 baseline drift",
    }
    return {
        "schema_version": "stage-capability-matrix/1.0",
        "stale_after_days": 365,
        "task_families": list(TASK_FAMILIES),
        "rows": rows,
    }


def _write(tmp_path: Path, data) -> Path:
    p = tmp_path / "matrix.json"
    p.write_text(
        data if isinstance(data, str) else json.dumps(data), encoding="utf-8"
    )
    return p


def _errors_for(tmp_path: Path, data, today: datetime.date = TODAY) -> list[str]:
    return run(
        _write(tmp_path, data),
        check_view=False,
        today=today,
        inventory_lock=False,
    )


def _assert_fires(errors: list[str], fragment: str) -> None:
    assert any(fragment in e for e in errors), f"{fragment!r} not in {errors}"


# ---------- baseline ----------


def test_shipped_matrix_passes():
    assert run(DEFAULT_MATRIX, today=datetime.date.today()) == []


def test_shipped_view_is_in_sync():
    data = json.loads(DEFAULT_MATRIX.read_text(encoding="utf-8"))
    assert DEFAULT_VIEW.read_text(encoding="utf-8") == render(data)


def test_valid_synthetic_matrix_passes(tmp_path):
    assert _errors_for(tmp_path, _valid_matrix()) == []


# ---------- M1: parse / top-level shape ----------


def test_unparseable_matrix_fails_closed(tmp_path):
    _assert_fires(_errors_for(tmp_path, "{not json"), "M1")


def test_missing_matrix_file_fails_closed(tmp_path):
    errors = run(tmp_path / "absent.json", check_view=False, today=TODAY)
    _assert_fires(errors, "M1")


def test_duplicate_json_keys_rejected(tmp_path):
    raw = json.dumps(_valid_matrix())
    raw = raw.replace(
        '"stale_after_days": 365',
        '"stale_after_days": 365, "stale_after_days": 30',
        1,
    )
    _assert_fires(_errors_for(tmp_path, raw), "M1")


def test_wrong_schema_version_fires(tmp_path):
    data = _valid_matrix()
    data["schema_version"] = "stage-capability-matrix/0.9"
    _assert_fires(_errors_for(tmp_path, data), "M1")


def test_unknown_top_level_field_fires(tmp_path):
    data = _valid_matrix()
    data["surprise"] = True
    _assert_fires(_errors_for(tmp_path, data), "M1")


# ---------- M2: task-family vocabulary lock ----------


def test_task_family_list_drift_fires(tmp_path):
    data = _valid_matrix()
    data["task_families"] = list(TASK_FAMILIES)[:-1]
    _assert_fires(_errors_for(tmp_path, data), "M2")


def test_task_family_reorder_fires(tmp_path):
    data = _valid_matrix()
    data["task_families"] = list(reversed(TASK_FAMILIES))
    _assert_fires(_errors_for(tmp_path, data), "M2")


# ---------- M3: row shape ----------


def test_duplicate_row_id_fires(tmp_path):
    data = _valid_matrix()
    data["rows"][1]["row_id"] = data["rows"][0]["row_id"]
    _assert_fires(_errors_for(tmp_path, data), "M3")


def test_unknown_task_family_on_row_fires(tmp_path):
    data = _valid_matrix()
    data["rows"][0]["task_family"] = "vibes"
    _assert_fires(_errors_for(tmp_path, data), "M3")


def test_missing_row_field_fires(tmp_path):
    data = _valid_matrix()
    del data["rows"][0]["transport_limits"]
    _assert_fires(_errors_for(tmp_path, data), "M3")


def test_unknown_row_field_fires(tmp_path):
    data = _valid_matrix()
    data["rows"][0]["bonus"] = "x"
    _assert_fires(_errors_for(tmp_path, data), "M3")


def test_bad_mechanism_status_fires(tmp_path):
    data = _valid_matrix()
    data["rows"][0]["mechanism_status"] = "SHIPPED"
    _assert_fires(_errors_for(tmp_path, data), "M3")


def test_bad_conformance_fires(tmp_path):
    data = _valid_matrix()
    data["rows"][0]["deterministic_conformance"] = "MOSTLY"
    _assert_fires(_errors_for(tmp_path, data), "M3")


# ---------- M4: behavioral-evidence status discipline ----------


def test_unknown_behavioral_status_fires(tmp_path):
    data = _valid_matrix()
    data["rows"][0]["behavioral_evidence"]["status"] = "PROBABLY_FINE"
    _assert_fires(_errors_for(tmp_path, data), "M4")


def test_measured_without_provenance_fires(tmp_path):
    data = _valid_matrix()
    data["rows"][0]["behavioral_evidence"] = {"status": "MEASURED"}
    _assert_fires(_errors_for(tmp_path, data), "M4")


def test_not_run_with_result_numbers_fires(tmp_path):
    """An unrun eval can never carry a result — the collapse the roadmap bans."""
    data = _valid_matrix()
    data["rows"][1]["behavioral_evidence"] = {
        "status": "NOT_RUN",
        "result_summary": "0.94 recall",
    }
    _assert_fires(_errors_for(tmp_path, data), "M4")


def test_out_of_scope_requires_reason(tmp_path):
    data = _valid_matrix()
    data["rows"][1]["behavioral_evidence"] = {"status": "OUT_OF_SCOPE"}
    _assert_fires(_errors_for(tmp_path, data), "M4")


def test_bad_measured_at_date_fires(tmp_path):
    data = _valid_matrix()
    data["rows"][0]["behavioral_evidence"]["measured_at"] = "last summer"
    _assert_fires(_errors_for(tmp_path, data), "M4")


def test_measured_eval_ref_must_exist_in_repo(tmp_path):
    data = _valid_matrix()
    data["rows"][0]["behavioral_evidence"]["eval_ref"] = "evals/heldout/ghost"
    _assert_fires(_errors_for(tmp_path, data), "M4")


# ---------- M5: full stage coverage ----------


def test_uncovered_task_family_fires(tmp_path):
    data = _valid_matrix()
    data["rows"] = data["rows"][1:]
    _assert_fires(_errors_for(tmp_path, data), "M5")


# ---------- M6: claim-ceiling language discipline ----------


def test_empty_claim_ceiling_fires(tmp_path):
    data = _valid_matrix()
    data["rows"][0]["max_licensed_claim"] = ""
    _assert_fires(_errors_for(tmp_path, data), "M6")


def test_overclaim_stem_on_unmeasured_row_fires(tmp_path):
    data = _valid_matrix()
    data["rows"][1]["max_licensed_claim"] = "Improves reviewer accuracy."
    _assert_fires(_errors_for(tmp_path, data), "M6")


def test_overclaim_stem_allowed_when_measured(tmp_path):
    data = _valid_matrix()
    data["rows"][0]["max_licensed_claim"] = (
        "Improved the offlist miss rate on the recorded eval only."
    )
    assert _errors_for(tmp_path, data) == []


# ---------- M7: claim anchors ----------


def test_claim_anchor_missing_from_file_fires(tmp_path):
    data = _valid_matrix()
    data["rows"][0]["claim_anchors"] = [
        {"file": "README.md", "anchor": "this sentence is nowhere in the readme"}
    ]
    _assert_fires(_errors_for(tmp_path, data), "M7")


def test_claim_anchor_nonexistent_file_fires(tmp_path):
    data = _valid_matrix()
    data["rows"][0]["claim_anchors"] = [
        {"file": "docs/GHOST.md", "anchor": "any anchor at least sixteen chars"}
    ]
    _assert_fires(_errors_for(tmp_path, data), "M7")


def test_short_claim_anchor_fires(tmp_path):
    data = _valid_matrix()
    data["rows"][0]["claim_anchors"] = [{"file": "README.md", "anchor": "ARS"}]
    _assert_fires(_errors_for(tmp_path, data), "M7")


# ---------- M8: stale evidence ----------


def _measured_without_reports(data: dict) -> None:
    """Point row 0 at a suite that publishes no measurement reports."""
    ev = data["rows"][0]["behavioral_evidence"]
    ev["eval_ref"] = "evals/heldout/reviewer_seeded_defects"
    del ev["measurement_report"]


def test_stale_measurement_without_note_fires(tmp_path):
    data = _valid_matrix()
    _measured_without_reports(data)
    data["rows"][0]["behavioral_evidence"]["measured_at"] = "2024-01-01"
    _assert_fires(_errors_for(tmp_path, data), "M8")


def test_stale_measurement_with_note_passes(tmp_path):
    data = _valid_matrix()
    _measured_without_reports(data)
    data["rows"][0]["behavioral_evidence"]["measured_at"] = "2024-01-01"
    data["rows"][0]["behavioral_evidence"]["staleness_note"] = (
        "measured two model generations ago; re-run queued"
    )
    assert _errors_for(tmp_path, data) == []


def test_invalid_stale_after_days_skips_m8_but_fires_m1(tmp_path):
    """A bad staleness policy is an M1 error, never a fabricated default."""
    data = _valid_matrix()
    _measured_without_reports(data)
    data["stale_after_days"] = 0
    data["rows"][0]["behavioral_evidence"]["measured_at"] = "2024-01-01"
    errors = _errors_for(tmp_path, data)
    _assert_fires(errors, "M1")
    assert not any("M8" in e for e in errors)


# ---------- M11: measurement-report binding ----------


def test_measured_row_in_reporting_suite_requires_binding(tmp_path):
    data = _valid_matrix()
    del data["rows"][0]["behavioral_evidence"]["measurement_report"]
    _assert_fires(_errors_for(tmp_path, data), "M11")


def test_report_binding_date_mismatch_fires(tmp_path):
    data = _valid_matrix()
    data["rows"][0]["behavioral_evidence"]["measured_at"] = "2026-08-01"
    _assert_fires(_errors_for(tmp_path, data), "M11")


def test_superseded_report_binding_fires(tmp_path):
    data = _valid_matrix()
    ev = data["rows"][0]["behavioral_evidence"]
    ev["measurement_report"] = (
        "evals/heldout/revision_claim_drift/measurement-2026-07-22.json"
    )
    ev["measured_at"] = "2026-07-22"
    _assert_fires(_errors_for(tmp_path, data), "M11")


def test_superseded_report_binding_with_note_passes(tmp_path):
    data = _valid_matrix()
    ev = data["rows"][0]["behavioral_evidence"]
    ev["measurement_report"] = (
        "evals/heldout/revision_claim_drift/measurement-2026-07-22.json"
    )
    ev["measured_at"] = "2026-07-22"
    ev["staleness_note"] = "pre-guard baseline row kept deliberately"
    assert _errors_for(tmp_path, data) == []


def test_missing_report_file_fires(tmp_path):
    data = _valid_matrix()
    data["rows"][0]["behavioral_evidence"]["measurement_report"] = (
        "evals/heldout/revision_claim_drift/measurement-2099-01-01.json"
    )
    _assert_fires(_errors_for(tmp_path, data), "M11")


def test_report_binding_outside_eval_ref_fires(tmp_path):
    data = _valid_matrix()
    data["rows"][0]["behavioral_evidence"]["measurement_report"] = (
        "evals/heldout/tortured_phrase_conformance/measurement-2026-08-10.json"
    )
    _assert_fires(_errors_for(tmp_path, data), "M11")


# ---------- round-2 hardening witnesses ----------


def test_eval_ref_must_be_repo_directory(tmp_path):
    """A file (or anything but a contained suite directory) is refused."""
    data = _valid_matrix()
    _measured_without_reports(data)
    data["rows"][0]["behavioral_evidence"]["eval_ref"] = "README.md"
    _assert_fires(_errors_for(tmp_path, data), "M4")


def test_eval_ref_escape_fires(tmp_path):
    data = _valid_matrix()
    _measured_without_reports(data)
    data["rows"][0]["behavioral_evidence"]["eval_ref"] = "../"
    _assert_fires(_errors_for(tmp_path, data), "M4")


def test_report_binding_must_match_report_pattern(tmp_path):
    """Arbitrary same-directory JSON cannot stand in for a measurement report."""
    data = _valid_matrix()
    data["rows"][0]["behavioral_evidence"]["measurement_report"] = (
        "evals/heldout/revision_claim_drift/heldout_set.json"
    )
    _assert_fires(_errors_for(tmp_path, data), "M11")


def test_future_measured_at_fires(tmp_path):
    data = _valid_matrix()
    _measured_without_reports(data)
    data["rows"][0]["behavioral_evidence"]["measured_at"] = "2099-01-01"
    _assert_fires(_errors_for(tmp_path, data), "M4")


def test_bool_stale_after_days_fires(tmp_path):
    data = _valid_matrix()
    data["stale_after_days"] = True
    _assert_fires(_errors_for(tmp_path, data), "M1")


def test_non_object_behavioral_evidence_reports_not_crashes(tmp_path):
    data = _valid_matrix()
    data["rows"][1]["behavioral_evidence"] = "measured, trust me"
    _assert_fires(_errors_for(tmp_path, data), "M4")


def test_never_licensed_stem_fires_even_on_measured_row(tmp_path):
    data = _valid_matrix()
    data["rows"][0]["max_licensed_claim"] = (
        "Guaranteed state-of-the-art performance across every model."
    )
    _assert_fires(_errors_for(tmp_path, data), "M6")


def test_percentage_claim_on_unmeasured_row_fires(tmp_path):
    data = _valid_matrix()
    data["rows"][1]["max_licensed_claim"] = "Reduces errors by 99 percent."
    _assert_fires(_errors_for(tmp_path, data), "M6")


def test_percentage_in_mechanism_on_unmeasured_row_fires(tmp_path):
    data = _valid_matrix()
    data["rows"][1]["mechanism"] = "Synthetic mechanism achieving 99% accuracy"
    _assert_fires(_errors_for(tmp_path, data), "M6")


def _binding_errors(tmp_path, monkeypatch, sibling_text: str) -> list[str]:
    """Drive _check_report_binding against a synthetic suite directory."""
    import check_stage_capability_matrix as mod

    suite = tmp_path / "evals" / "suite"
    suite.mkdir(parents=True)
    (suite / "measurement-2026-08-07.json").write_text(
        '{"measurement_date": "2026-08-07"}', encoding="utf-8"
    )
    (suite / "measurement-2026-08-09.json").write_text(
        sibling_text, encoding="utf-8"
    )
    monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)
    errors: list[str] = []
    mod._check_report_binding(
        "r",
        {"measurement_report": "evals/suite/measurement-2026-08-07.json"},
        "evals/suite",
        datetime.date(2026, 8, 7),
        errors,
    )
    return errors


def test_non_object_sibling_report_fires_not_crashes(tmp_path, monkeypatch):
    errors = _binding_errors(tmp_path, monkeypatch, "[1, 2]")
    assert any("M11" in e for e in errors)


def test_unreadable_sibling_report_fires(tmp_path, monkeypatch):
    errors = _binding_errors(tmp_path, monkeypatch, "{not json")
    assert any("M11" in e and "unreadable" in e for e in errors)


def test_report_name_with_trailing_newline_fires(tmp_path, monkeypatch):
    import check_stage_capability_matrix as mod

    assert mod._REPORT_NAME_RE.fullmatch("measurement-x.json\n") is None


def test_malformed_claim_anchors_on_locked_row_reports_not_crashes(tmp_path):
    shipped = json.loads(DEFAULT_MATRIX.read_text(encoding="utf-8"))
    anchored = next(r for r in shipped["rows"] if r.get("claim_anchors"))
    anchored["claim_anchors"] = 1
    errors = run(_write(tmp_path, shipped), check_view=False, today=TODAY)
    assert any("M7" in e for e in errors)
    assert any("M13" in e and anchored["row_id"] in e for e in errors)


def test_percentage_claim_on_measured_row_passes(tmp_path):
    data = _valid_matrix()
    data["rows"][0]["max_licensed_claim"] = (
        "On the recorded set only, the miss rate was 9.4%."
    )
    assert _errors_for(tmp_path, data) == []


def test_render_includes_anchors():
    data = _valid_matrix()
    data["rows"][0]["claim_anchors"] = [
        {"file": "README.md", "anchor": "Academic Research Skills"}
    ]
    assert "Academic Research Skills" in render(data)


# ---------- co-consumer vocabulary pin (#742 §2) ----------


def test_task_families_match_the_742_design_doc_table():
    """The frozen vocabulary and the #742 §2 table ids stay in lockstep."""
    doc = (
        REPO_ROOT
        / "docs/design/2026-08-17-742-research-family-profile-contract-design.md"
    ).read_text(encoding="utf-8")
    section = doc.split("## 2. Shared stage and task-family vocabulary", 1)[1]
    section = section.split("## 3.", 1)[0]
    import re

    doc_ids = [
        m.group(1)
        for m in re.finditer(r"^\| `([a-z_]+)` \|", section, re.M)
    ]
    assert doc_ids == list(TASK_FAMILIES)


# ---------- shipped-inventory locks (D5 analog) ----------


def test_shipped_row_inventory_is_locked(tmp_path):
    """Silently deleting a shipped row fails even if its family stays covered."""
    shipped = json.loads(DEFAULT_MATRIX.read_text(encoding="utf-8"))
    victim = next(
        r["row_id"]
        for r in shipped["rows"]
        if sum(x["task_family"] == r["task_family"] for x in shipped["rows"]) > 1
    )
    shipped["rows"] = [r for r in shipped["rows"] if r["row_id"] != victim]
    errors = run(_write(tmp_path, shipped), check_view=False, today=TODAY)
    assert any("row inventory" in e for e in errors)


def test_shipped_anchor_minimums_are_locked(tmp_path):
    """Deleting a shipped row's claim anchors fails until the lock is edited."""
    shipped = json.loads(DEFAULT_MATRIX.read_text(encoding="utf-8"))
    anchored = next(r for r in shipped["rows"] if r.get("claim_anchors"))
    del anchored["claim_anchors"]
    errors = run(_write(tmp_path, shipped), check_view=False, today=TODAY)
    assert any("anchor" in e and anchored["row_id"] in e for e in errors)


# ---------- M12: falsifiable conformance pins ----------


def test_ci_gated_without_pins_fires(tmp_path):
    data = _valid_matrix()
    del data["rows"][1]["conformance_pinned_by"]
    _assert_fires(_errors_for(tmp_path, data), "M12")


def test_pin_missing_file_fires(tmp_path):
    data = _valid_matrix()
    data["rows"][1]["conformance_pinned_by"] = ["scripts/ghost_lint.py"]
    _assert_fires(_errors_for(tmp_path, data), "M12")


def test_pin_missing_function_fires(tmp_path):
    data = _valid_matrix()
    data["rows"][1]["conformance_pinned_by"] = [
        "scripts/check_stage_capability_matrix.py::no_such_function"
    ]
    _assert_fires(_errors_for(tmp_path, data), "M12")


def test_none_conformance_with_pins_fires(tmp_path):
    data = _valid_matrix()
    data["rows"][1]["deterministic_conformance"] = "NONE"
    _assert_fires(_errors_for(tmp_path, data), "M12")


def test_none_conformance_without_pins_passes(tmp_path):
    data = _valid_matrix()
    data["rows"][1]["deterministic_conformance"] = "NONE"
    del data["rows"][1]["conformance_pinned_by"]
    assert _errors_for(tmp_path, data) == []


# ---------- M7 hardening: path containment ----------


def test_anchor_path_escape_fires(tmp_path):
    data = _valid_matrix()
    data["rows"][0]["claim_anchors"] = [
        {"file": "../outside.md", "anchor": "an anchor of sufficient length"}
    ]
    _assert_fires(_errors_for(tmp_path, data), "M7")


def test_anchor_absolute_path_fires(tmp_path):
    data = _valid_matrix()
    data["rows"][0]["claim_anchors"] = [
        {"file": "/etc/hosts", "anchor": "an anchor of sufficient length"}
    ]
    _assert_fires(_errors_for(tmp_path, data), "M7")


# ---------- M9: next required evaluation ----------


def test_missing_next_evaluation_fires(tmp_path):
    data = _valid_matrix()
    data["rows"][1]["next_required_evaluation"] = ""
    _assert_fires(_errors_for(tmp_path, data), "M9")


def test_out_of_scope_row_may_omit_next_evaluation(tmp_path):
    data = _valid_matrix()
    data["rows"][1]["behavioral_evidence"] = {
        "status": "OUT_OF_SCOPE",
        "reason": "no behavioral surface; deterministic contract only",
    }
    data["rows"][1]["next_required_evaluation"] = ""
    errors = [e for e in _errors_for(tmp_path, data) if "M9" in e]
    assert errors == []


# ---------- M10: generated-view sync ----------


def test_view_drift_fires(tmp_path):
    data = _valid_matrix()
    matrix_path = _write(tmp_path, data)
    view_path = tmp_path / "view.md"
    view_path.write_text(render(data) + "tampered\n", encoding="utf-8")
    errors = run(
        matrix_path,
        check_view=True,
        view_path=view_path,
        today=TODAY,
        inventory_lock=False,
    )
    _assert_fires(errors, "M10")


def test_view_in_sync_passes(tmp_path):
    data = _valid_matrix()
    matrix_path = _write(tmp_path, data)
    view_path = tmp_path / "view.md"
    view_path.write_text(render(data), encoding="utf-8")
    assert (
        run(
            matrix_path,
            check_view=True,
            view_path=view_path,
            today=TODAY,
            inventory_lock=False,
        )
        == []
    )


def test_render_is_deterministic():
    data = _valid_matrix()
    assert render(data) == render(data)


def test_render_marks_generated():
    assert "GENERATED FILE" in render(_valid_matrix())


def test_render_never_collapses_statuses():
    """Every distinct behavioral status string appears verbatim in the view."""
    data = _valid_matrix()
    data["rows"][1]["behavioral_evidence"] = {
        "status": "OUT_OF_SCOPE",
        "reason": "no behavioral surface",
    }
    data["rows"][2]["behavioral_evidence"] = {"status": "DESIGNED"}
    view = render(data)
    for status in ("MEASURED", "NOT_RUN", "OUT_OF_SCOPE", "DESIGNED"):
        assert status in view


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
