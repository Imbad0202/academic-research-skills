#!/usr/bin/env python3
"""Regression and adversarial tests for #737 Claim Registry coverage."""
from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator


SCRIPTS = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))

import claim_registry_coverage as coverage  # noqa: E402


def _claim(draft: bytes, claim_id: str, text: str, *, tier: str = "ALL") -> dict:
    encoded = text.encode("utf-8")
    start = draft.index(encoded)
    return {
        "claim_id": claim_id,
        "claim_text": text,
        "draft_span": {"start_byte": start, "end_byte": start + len(encoded)},
        "claim_kinds": ["quantitative"] if any(ch.isdigit() for ch in text) else ["other_factual"],
        "ref_slugs": [],
        "writer_anchors": [f"byte:{start}-{start + len(encoded)}"],
        "paper_section": None,
        "selection_tier": tier,
    }


def _registry_raw(draft: bytes, claims: list[dict]) -> bytes:
    value = {
        "schema_version": coverage.REGISTRY_VERSION,
        "draft_raw_sha256": hashlib.sha256(draft).hexdigest(),
        "claims": claims,
    }
    return (json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")


def test_classifies_exact_span_match_and_unregistered_candidate() -> None:
    draft = (
        "The intervention improved completion by 12% (Smith, 2024).\n"
        "A second outcome affected 30 participants [2].\n"
    ).encode()
    registry = _registry_raw(
        draft,
        [_claim(draft, "C1", "The intervention improved completion by 12% (Smith, 2024).")],
    )
    report = coverage.build_report(draft, registry)
    assert [row["coverage_state"] for row in report["candidates"]] == [
        "registry_span_matched",
        "candidate_unregistered",
    ]
    assert report["candidate_unregistered_count"] == 1
    assert report["semantic_extraction_coverage"] == "not_machine_detectable"


def test_registry_claim_outside_candidate_classes_is_not_called_unlocated() -> None:
    draft = b"X causes Y.\nNo quantitative or cited surface appears here.\n"
    registry = _registry_raw(draft, [_claim(draft, "C1", "X causes Y.")])
    report = coverage.build_report(draft, registry)
    assert report["candidates"] == []
    assert report["registered_claims_outside_candidate_classes"] == ["C1"]


@pytest.mark.parametrize(
    ("sentence", "expected_kind"),
    (
        ("Smith (2024) reports a stable association.", "citation_bearing_sentence"),
        ("The association was replicated [@smith2024].", "citation_bearing_sentence"),
        ("The analytic sample was N=30.", "quantitative_sentence"),
        ("The standardized effect was Cohen's d = 0.45.", "quantitative_sentence"),
        ("The adjusted odds ratio was OR = 1.80.", "quantitative_sentence"),
        ("The coefficient was β = .31.", "quantitative_sentence"),
    ),
)
def test_common_scholarly_surface_syntax_is_detected(
    sentence: str, expected_kind: str
) -> None:
    draft = (sentence + "\n").encode("utf-8")
    report = coverage.build_report(draft, _registry_raw(draft, []))
    assert len(report["candidates"]) == 1
    assert expected_kind in report["candidates"][0]["candidate_kinds"]
    assert report["candidates"][0]["coverage_state"] == "candidate_unregistered"


def test_short_text_elsewhere_cannot_create_substring_false_coverage() -> None:
    draft = b"A result affected 30 participants [2].\nA separate premise.\n"
    registry = _registry_raw(draft, [_claim(draft, "C1", "A separate premise.")])
    report = coverage.build_report(draft, registry)
    assert report["candidates"][0]["coverage_state"] == "candidate_unregistered"
    assert report["registered_claims_outside_candidate_classes"] == ["C1"]


def test_tiny_registered_span_cannot_hide_other_trigger_in_same_sentence() -> None:
    draft = (
        b"A result affected 30 participants [2] and a second result affected "
        b"45 participants [3].\n"
    )
    registry = _registry_raw(draft, [_claim(draft, "C1", "30 participants [2]")])
    report = coverage.build_report(draft, registry)

    candidate = report["candidates"][0]
    assert candidate["coverage_state"] == "mixed_or_partial_registry_coverage"
    assert candidate["matched_claim_ids"] == ["C1"]
    assert candidate["uncovered_trigger_count"] >= 2
    assert report["candidate_unregistered_count"] == 1
    assert any(
        row["coverage_state"] == "trigger_unregistered"
        for row in candidate["triggers"]
    )


def test_tiny_span_covering_only_trigger_is_still_partial_not_clean() -> None:
    draft = b"Context qualifies a reported sample of 30 participants.\n"
    registry = _registry_raw(draft, [_claim(draft, "C1", "30 participants")])
    report = coverage.build_report(draft, registry)

    candidate = report["candidates"][0]
    assert candidate["uncovered_trigger_count"] == 0
    assert candidate["coverage_state"] == "mixed_or_partial_registry_coverage"
    assert report["candidate_unregistered_count"] == 1


def test_full_sentence_span_and_all_triggers_is_clean() -> None:
    sentence = "A result affected 30 participants [2]."
    draft = (sentence + "\n").encode()
    registry = _registry_raw(draft, [_claim(draft, "C1", sentence)])
    report = coverage.build_report(draft, registry)

    candidate = report["candidates"][0]
    assert candidate["coverage_state"] == "registry_span_matched"
    assert candidate["uncovered_trigger_count"] == 0
    assert report["candidate_unregistered_count"] == 0


def test_raw_crlf_and_unicode_bytes_are_bound_exactly() -> None:
    draft = "前測有 42 participants。\r\n第二行。\r\n".encode("utf-8")
    text = "前測有 42 participants。"
    registry = _registry_raw(draft, [_claim(draft, "C-UTF8", text)])
    report = coverage.build_report(draft, registry)
    assert report["draft_raw_sha256"] == hashlib.sha256(draft).hexdigest()
    assert report["registry_raw_sha256"] == hashlib.sha256(registry).hexdigest()
    assert report["candidates"][0]["text"] == text
    assert report["candidates"][0]["start_byte"] == 0


def test_registry_draft_hash_mismatch_fails() -> None:
    draft = b"A result affected 30 participants.\n"
    registry = json.loads(_registry_raw(draft, []).decode())
    registry["draft_raw_sha256"] = "0" * 64
    with pytest.raises(coverage.CoverageError, match="exact draft bytes"):
        coverage.build_report(draft, json.dumps(registry).encode())


def test_claim_text_must_equal_exact_utf8_span() -> None:
    draft = b"A result affected 30 participants.\n"
    claim = _claim(draft, "C1", "A result affected 30 participants.")
    claim["draft_span"]["end_byte"] -= 1
    registry = _registry_raw(draft, [claim])
    with pytest.raises(coverage.CoverageError, match="exact draft span"):
        coverage.build_report(draft, registry)


def test_duplicate_yaml_key_is_rejected() -> None:
    draft = b"A result affected 30 participants.\n"
    raw = (
        f"schema_version: {coverage.REGISTRY_VERSION}\n"
        f"draft_raw_sha256: {hashlib.sha256(draft).hexdigest()}\n"
        "claims: []\nclaims: []\n"
    ).encode()
    with pytest.raises(coverage.CoverageError, match="duplicate key"):
        coverage.build_report(draft, raw)


def test_replay_rejects_tampered_candidate_and_summary() -> None:
    draft = b"A result affected 30 participants.\n"
    registry = _registry_raw(draft, [])
    report = coverage.build_report(draft, registry)
    tampered = copy.deepcopy(report)
    tampered["candidates"][0]["text"] = "Forged 30 participants."
    assert coverage.validate_report(tampered, draft, registry)
    tampered = copy.deepcopy(report)
    tampered["candidate_unregistered_count"] = 0
    assert coverage.validate_report(tampered, draft, registry)


def test_schema_rejects_state_match_contradiction() -> None:
    draft = b"A result affected 30 participants.\n"
    registry = _registry_raw(draft, [])
    report = coverage.build_report(draft, registry)
    report["candidates"][0]["coverage_state"] = "registry_span_matched"
    schema = coverage._load_schema(coverage.REPORT_SCHEMA_PATH)
    assert list(Draft202012Validator(schema).iter_errors(report))

    report = coverage.build_report(draft, registry)
    report["candidates"][0]["triggers"][0]["coverage_state"] = (
        "registry_span_matched"
    )
    assert list(Draft202012Validator(schema).iter_errors(report))


def test_schemas_are_valid_and_closed() -> None:
    for path in (coverage.REGISTRY_SCHEMA_PATH, coverage.REPORT_SCHEMA_PATH):
        schema = coverage._load_schema(path)
        Draft202012Validator.check_schema(schema)
        assert schema["additionalProperties"] is False


def test_skips_fenced_code_and_headings() -> None:
    draft = b"# 50% heading\n```text\nA 30% fixture [1].\n```\n"
    report = coverage.build_report(draft, _registry_raw(draft, []))
    assert report["candidates"] == []


def test_cli_build_then_replay_validate(tmp_path: Path) -> None:
    draft = b"A result affected 30 participants.\n"
    registry = _registry_raw(draft, [])
    draft_path = tmp_path / "draft.md"
    registry_path = tmp_path / "registry.json"
    report_path = tmp_path / "report.json"
    draft_path.write_bytes(draft)
    registry_path.write_bytes(registry)
    script = SCRIPTS / "claim_registry_coverage.py"
    built = subprocess.run(
        [sys.executable, str(script), "--draft", str(draft_path), "--registry", str(registry_path), "--output", str(report_path)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert built.returncode == 0, built.stderr
    replayed = subprocess.run(
        [sys.executable, str(script), "--draft", str(draft_path), "--registry", str(registry_path), "--validate-report", str(report_path)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert replayed.returncode == 0, replayed.stderr
    assert "PASS" in replayed.stdout
