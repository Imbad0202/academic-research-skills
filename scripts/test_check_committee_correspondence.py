#!/usr/bin/env python3
"""Schema, mutation, and end-to-end tests for #668 correspondence accounting."""
from __future__ import annotations

import copy
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from check_committee_correspondence import (
    BOUNDARY_LINE,
    DEFAULT_SCHEMA,
    validate_bundle,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "scripts" / "fixtures" / "committee_correspondence" / "16fd83f6aec7"
TRACKER_NAME = "concern_tracker.json"
CHECKER = REPO_ROOT / "scripts" / "check_committee_correspondence.py"


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, value: dict[str, object]) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _bundle(tmp_path: Path) -> tuple[Path, dict[str, object]]:
    target = tmp_path / FIXTURE.name
    shutil.copytree(FIXTURE, target)
    tracker_path = target / TRACKER_NAME
    return tracker_path, _load(tracker_path)


def _save_skeleton(tracker_path: Path, tracker: dict[str, object], text: str) -> None:
    skeleton_path = tracker_path.parent / "response_skeleton.md"
    skeleton_path.write_text(text, encoding="utf-8")
    tracker["response_skeleton"]["sha256"] = hashlib.sha256(text.encode()).hexdigest()  # type: ignore[index]
    _write(tracker_path, tracker)


def _schema() -> Draft202012Validator:
    schema = _load(DEFAULT_SCHEMA)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def test_fixture_schema_and_bundle_pass() -> None:
    tracker = _load(FIXTURE / TRACKER_NAME)
    _schema().validate(tracker)
    assert validate_bundle(FIXTURE / TRACKER_NAME) == []


def test_revision_coach_entrypoint_and_protocol_are_wired() -> None:
    requirements = {
        "academic-paper/agents/revision_coach_agent.md": (
            "Committee-Correspondence Variant (#668)",
            "references/committee_correspondence_protocol.md",
            "never emits",
        ),
        "academic-paper/SKILL.md": (
            "Committee-correspondence routing:",
            "separate #668 concern tracker",
        ),
        "commands/ars-revision-coach.md": (
            "committee-correspondence variant",
            "Never infer committee authority from tone",
        ),
        "academic-paper/references/committee_correspondence_protocol.md": (
            "source_letter.txt",
            "committee-correspondence/1.0",
            BOUNDARY_LINE,
        ),
    }
    for relative, needles in requirements.items():
        text = (REPO_ROOT / relative).read_text(encoding="utf-8")
        for needle in needles:
            assert needle in text, f"{relative}: missing {needle!r}"


def test_fixture_proves_compound_multi_label_and_degraded_mode() -> None:
    tracker = _load(FIXTURE / TRACKER_NAME)
    first = tracker["concerns"][0]  # type: ignore[index]
    assert first["action_type"] == ["design", "revise_artifact"]  # type: ignore[index]
    assert tracker["profile_context"] == {
        "state": "not_selected",
        "selected_profile_ids": [],
        "artifact_resolution_state": "artifact_agnostic",
    }


def test_fixture_has_no_priority_or_severity_field() -> None:
    encoded = json.dumps(_load(FIXTURE / TRACKER_NAME), sort_keys=True)
    assert '"priority"' not in encoded
    assert '"severity"' not in encoded


def test_source_segments_cover_every_byte_and_preserve_noncomments() -> None:
    tracker = _load(FIXTURE / TRACKER_NAME)
    segments = tracker["source_artifact"]["segments"]  # type: ignore[index]
    assert segments[0]["byte_start"] == 0  # type: ignore[index]
    assert segments[-1]["byte_end"] == tracker["source_artifact"]["byte_length"]  # type: ignore[index]
    assert [item["kind"] for item in segments] == ["non_comment", "comment", "comment", "non_comment"]  # type: ignore[index]


def test_dropped_concern_fails_complete_accounting(tmp_path: Path) -> None:
    path, tracker = _bundle(tmp_path)
    tracker["concerns"].pop()  # type: ignore[union-attr]
    _write(path, tracker)
    assert any("every comment segment" in item for item in validate_bundle(path))


def test_duplicated_concern_fails(tmp_path: Path) -> None:
    path, tracker = _bundle(tmp_path)
    tracker["concerns"].append(copy.deepcopy(tracker["concerns"][0]))  # type: ignore[index,union-attr]
    _write(path, tracker)
    errors = validate_bundle(path)
    assert any("concern ids must be unique" in item for item in errors)


@pytest.mark.parametrize("delta", [-1, 1])
def test_segment_gap_or_overlap_fails(tmp_path: Path, delta: int) -> None:
    path, tracker = _bundle(tmp_path)
    tracker["source_artifact"]["segments"][1]["byte_start"] += delta  # type: ignore[index]
    _write(path, tracker)
    assert any("previous segment end" in item for item in validate_bundle(path))


def test_source_mutation_breaks_hash_and_bundle_binding(tmp_path: Path) -> None:
    path, _ = _bundle(tmp_path)
    source = path.parent / "source_letter.txt"
    source.write_text(source.read_text(encoding="utf-8") + "Changed\n", encoding="utf-8")
    errors = validate_bundle(path)
    assert any("source_artifact.sha256" in item for item in errors)
    assert any("bundle directory name" in item for item in errors)


def test_verbatim_and_locator_must_match_exact_source(tmp_path: Path) -> None:
    path, tracker = _bundle(tmp_path)
    tracker["concerns"][0]["verbatim_text"] = "Paraphrased"  # type: ignore[index]
    tracker["concerns"][1]["source_locator"]["byte_start"] = 0  # type: ignore[index]
    _write(path, tracker)
    errors = validate_bundle(path)
    assert any("verbatim_text" in item for item in errors)
    assert any("source locator" in item for item in errors)


def test_committee_authority_basis_must_be_exact_source_text(tmp_path: Path) -> None:
    path, tracker = _bundle(tmp_path)
    tracker["concerns"][0]["authority_basis"]["exact_text"] = "The committee commands"  # type: ignore[index]
    _write(path, tracker)
    assert any("authority basis" in item for item in validate_bundle(path))


def test_source_order_reordering_fails(tmp_path: Path) -> None:
    path, tracker = _bundle(tmp_path)
    tracker["concerns"].reverse()  # type: ignore[union-attr]
    _write(path, tracker)
    assert any("canonical source-comment order" in item for item in validate_bundle(path))


def test_incomplete_working_view_fails(tmp_path: Path) -> None:
    path, tracker = _bundle(tmp_path)
    tracker["working_views"][0]["concern_ids"] = ["CC-001"]  # type: ignore[index]
    _write(path, tracker)
    assert any("full concern-id permutation" in item for item in validate_bundle(path))


def test_missing_response_marker_fails_even_when_hash_is_updated(tmp_path: Path) -> None:
    path, tracker = _bundle(tmp_path)
    skeleton = (path.parent / "response_skeleton.md").read_text(encoding="utf-8")
    skeleton = skeleton.replace("<!-- concern:CC-002 -->\n", "", 1)
    _save_skeleton(path, tracker, skeleton)
    assert any("markers must cover" in item for item in validate_bundle(path))


def test_duplicate_response_marker_fails_even_when_hash_is_updated(tmp_path: Path) -> None:
    path, tracker = _bundle(tmp_path)
    skeleton = (path.parent / "response_skeleton.md").read_text(encoding="utf-8")
    skeleton = skeleton.replace("<!-- concern:CC-002 -->", "<!-- concern:CC-001 -->\n<!-- concern:CC-002 -->")
    _save_skeleton(path, tracker, skeleton)
    assert any("markers must cover" in item for item in validate_bundle(path))


def test_response_resolution_claim_fails_even_when_hash_is_updated(tmp_path: Path) -> None:
    path, tracker = _bundle(tmp_path)
    skeleton = (path.parent / "response_skeleton.md").read_text(encoding="utf-8")
    skeleton += "\nConcern CC-001 is resolved.\n"
    _save_skeleton(path, tracker, skeleton)
    assert any("resolution/approval/readiness claim" in item for item in validate_bundle(path))


def test_missing_665_boundary_fails_even_when_hash_is_updated(tmp_path: Path) -> None:
    path, tracker = _bundle(tmp_path)
    skeleton = (path.parent / "response_skeleton.md").read_text(encoding="utf-8")
    skeleton = skeleton.replace(BOUNDARY_LINE, "")
    _save_skeleton(path, tracker, skeleton)
    assert any("fixed #665 boundary" in item for item in validate_bundle(path))


@pytest.mark.parametrize("field", ["priority", "severity", "estimated_hours"])
def test_schema_rejects_model_ranking_and_effort_fields(tmp_path: Path, field: str) -> None:
    path, tracker = _bundle(tmp_path)
    tracker["concerns"][0][field] = "high"  # type: ignore[index]
    _write(path, tracker)
    assert any("Additional properties" in item and field in item for item in validate_bundle(path))


def test_no_profile_cannot_emit_profile_derived_fields(tmp_path: Path) -> None:
    path, tracker = _bundle(tmp_path)
    tracker["concerns"][0]["profile_requirement_ids"] = ["profile.req-1"]  # type: ignore[index]
    _write(path, tracker)
    assert any("require a selected profile" in item for item in validate_bundle(path))


def test_selected_profile_enrichment_is_explicit_and_valid(tmp_path: Path) -> None:
    path, tracker = _bundle(tmp_path)
    tracker["profile_context"] = {
        "state": "selected",
        "selected_profile_ids": ["synthetic.profile"],
        "artifact_resolution_state": "profile_enriched",
    }
    tracker["concerns"][0]["profile_requirement_ids"] = ["synthetic.req-1"]  # type: ignore[index]
    tracker["concerns"][0]["affected_artifacts"].append(  # type: ignore[index,union-attr]
        {"name": "Synthetic profile attachment", "provenance": "profile_resolved"}
    )
    _write(path, tracker)
    assert validate_bundle(path) == []


def test_documented_authorization_requires_accounted_comment_pointer(tmp_path: Path) -> None:
    path, tracker = _bundle(tmp_path)
    status = tracker["human_subjects_status"]  # type: ignore[assignment]
    status["authorization_status"] = "documented"  # type: ignore[index]
    status["authorization_source_comment_id"] = "SC-001"  # type: ignore[index]
    _write(path, tracker)
    assert any("authorization source" in item for item in validate_bundle(path))


def test_invalid_dependency_fails(tmp_path: Path) -> None:
    path, tracker = _bundle(tmp_path)
    tracker["concerns"][0]["dependencies"] = [  # type: ignore[index]
        {"concern_id": "CC-999", "provenance": "author_confirmed"}
    ]
    _write(path, tracker)
    assert any("dependency does not resolve" in item for item in validate_bundle(path))


def test_bundle_path_traversal_is_rejected(tmp_path: Path) -> None:
    path, tracker = _bundle(tmp_path)
    tracker["source_artifact"]["path"] = "../source_letter.txt"  # type: ignore[index]
    _write(path, tracker)
    assert any("normalized relative path" in item for item in validate_bundle(path))


def test_bundle_symlink_is_rejected(tmp_path: Path) -> None:
    path, _ = _bundle(tmp_path)
    source = path.parent / "source_letter.txt"
    real = path.parent / "source_real.txt"
    source.rename(real)
    source.symlink_to(real.name)
    assert any("cannot traverse a symlink" in item for item in validate_bundle(path))


def test_duplicate_json_key_is_rejected(tmp_path: Path) -> None:
    path, _ = _bundle(tmp_path)
    path.write_text('{"schema_version":"a","schema_version":"b"}', encoding="utf-8")
    assert any("duplicate JSON key" in item for item in validate_bundle(path))


def test_cli_pass_and_fail(tmp_path: Path) -> None:
    passing = subprocess.run(
        [sys.executable, str(CHECKER), str(FIXTURE / TRACKER_NAME)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert passing.returncode == 0
    path, tracker = _bundle(tmp_path)
    tracker["concerns"].pop()  # type: ignore[union-attr]
    _write(path, tracker)
    failing = subprocess.run(
        [sys.executable, str(CHECKER), str(path)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert failing.returncode == 1
    assert "every comment segment" in failing.stderr
