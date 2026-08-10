"""Tests for the #678 canonical bibliographic-integrity signal carrier."""
from __future__ import annotations

import copy
import hashlib
import json
import shutil
import sys
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator


SCRIPTS = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))

import bibliographic_integrity_signals as signals  # noqa: E402
import check_bibliographic_integrity_signals as checker  # noqa: E402
import tortured_phrase_screening as screening  # noqa: E402


def _fixture(name: str) -> dict:
    path = SCRIPTS / "fixtures/bibliographic_integrity_signals" / name
    return json.loads(path.read_text(encoding="utf-8"))


def _validator() -> Draft202012Validator:
    return Draft202012Validator(
        signals.load_schema(), format_checker=Draft202012Validator.FORMAT_CHECKER
    )


def _screening_state() -> screening.SnapshotState:
    fixture_root = SCRIPTS / "fixtures/tortured_phrase_screening"
    bundle = screening.load_snapshot(
        fixture_root / "snapshot.json", fixture_root / "snapshot_manifest.json"
    )
    return screening.SnapshotState(
        status="loaded",
        reason_code="CHECK_COMPLETED",
        bundle=bundle,
        snapshot_sha256=bundle.snapshot_sha256,
        manifest_sha256=bundle.manifest_sha256,
        detail=None,
    )


def _rendered_row(signal: dict) -> dict[str, str]:
    lines = signals.render_advisory_section([signal]).splitlines()
    headings = lines[2].strip("|").split(" | ")
    values = lines[4].strip("|").split(" | ")
    assert len(values) == len(headings)
    return dict(zip(headings, values, strict=True))


def test_all_epistemic_class_fixtures_round_trip() -> None:
    for name in (
        "retraction.json",
        "retraction_check_attestation.json",
        "tortured_phrase.json",
        "tortured_phrase_v1_2_detected.json",
        "tortured_phrase_v1_2_abstract_missing.json",
    ):
        fixture = _fixture(name)
        assert not list(_validator().iter_errors(fixture))
        assert json.loads(json.dumps(fixture)) == fixture


def test_v1_2_fixtures_replay_except_frozen_unicode_provenance() -> None:
    corpus_path = SCRIPTS / "fixtures/tortured_phrase_screening/corpus_input.yaml"
    corpus = yaml.safe_load(corpus_path.read_text(encoding="utf-8"))[
        "literature_corpus"
    ]
    by_key = {entry["citation_key"]: entry for entry in corpus}
    cases = (
        (
            "tortured_phrase_v1_2_detected.json",
            "fixture_complete_2026",
            "cited_title",
        ),
        (
            "tortured_phrase_v1_2_abstract_missing.json",
            "fixture_missing_2026",
            "cited_abstract",
        ),
    )
    state = _screening_state()
    for fixture_name, citation_key, surface in cases:
        expected = screening.build_cited_signal(
            by_key[citation_key],
            surface=surface,
            state=state,
            checked_at="2026-08-10T01:00:00Z",
            recorded_at="2026-08-10T01:00:01Z",
        )
        fixture = _fixture(fixture_name)
        runtime_version = expected["tortured_phrase_context"]["snapshot"][
            "unicode_data_version"
        ]
        assert runtime_version == state.bundle.unicode_data_version
        fixture_version = fixture["tortured_phrase_context"]["snapshot"][
            "unicode_data_version"
        ]
        assert fixture_version == checker.V12_FIXTURE_UNICODE_DATA_VERSION
        expected["tortured_phrase_context"]["snapshot"][
            "unicode_data_version"
        ] = fixture_version
        assert fixture == expected
        screening.validate_cited_signal_binding(fixture, by_key[citation_key])


def test_legacy_fixture_byte_identity_is_frozen() -> None:
    fixture_root = SCRIPTS / "fixtures/bibliographic_integrity_signals"
    for name, expected_sha256 in checker.LEGACY_FIXTURE_SHA256.items():
        assert hashlib.sha256((fixture_root / name).read_bytes()).hexdigest() == expected_sha256


def test_closed_schema_rejects_undeclared_field() -> None:
    fixture = _fixture("retraction.json")
    fixture["undeclared"] = True
    assert any("Additional properties" in err.message for err in _validator().iter_errors(fixture))


def test_heuristic_cannot_use_deterministic_label() -> None:
    fixture = _fixture("tortured_phrase.json")
    fixture["epistemic_label"] = "RESOLVER-OR-LIST-OBSERVATION"
    assert list(_validator().iter_errors(fixture))


def test_unknown_or_degraded_can_never_be_clean() -> None:
    fixture = _fixture("retraction.json")
    fixture["check_status"] = "degraded"
    fixture["finding"] = "not_detected"
    assert list(_validator().iter_errors(fixture))


def test_legacy_migration_preserves_epistemic_boundaries() -> None:
    entry = {
        "citation_key": "legacy2024",
        "source_pointer": "zotero://select/items/0_LEGACY",
        "obtained_at": "2026-08-01T00:00:00Z",
        "contamination_signals": {
            "preprint_post_llm_inflection": True,
            "semantic_scholar_unmatched": False,
        },
        "contamination_signal_omissions": {"openalex_unmatched": "api_degraded"},
        "retraction_check": True,
    }
    migrated = signals.migrate_legacy_entry(
        entry, recorded_at="2026-08-08T00:00:00Z"
    )
    by_type = {item["signal_type"]: item for item in migrated}
    assert by_type["preprint_post_llm_inflection"]["epistemic_class"] == "heuristic_advisory"
    assert by_type["semantic_scholar_unmatched"]["epistemic_class"] == "deterministic_fact"
    assert by_type["openalex_unmatched"]["check_status"] == "degraded"
    assert by_type["openalex_unmatched"]["finding"] == "unresolved"
    assert by_type["retraction_status"]["epistemic_class"] == "process_attestation"
    assert by_type["retraction_status"]["finding"] == "unresolved"
    assert all(not signals.validation_errors(item) for item in migrated)
    assert "contamination_signals" in entry
    assert "retraction_check" in entry


def test_multiple_signals_compose_in_one_section_without_marker_token() -> None:
    fixtures = [_fixture("retraction.json"), _fixture("tortured_phrase.json")]
    rendered = signals.render_advisory_section(fixtures)
    assert rendered.count("## Bibliographic Integrity Advisories") == 1
    assert "CONTAMINATED-" not in rendered
    assert "<!--ref:" not in rendered
    assert rendered.index("bis:jones2025") < rendered.index("bis:smith2024")
    for heading in (
        "signal type",
        "source version",
        "source sha256",
        "checked at",
        "recorded at",
        "stale after",
        "source pointer",
    ):
        assert heading in rendered


def test_v1_2_renderer_projects_complete_neutral_metadata_for_all_states() -> None:
    corpus = yaml.safe_load(
        (SCRIPTS / "fixtures/tortured_phrase_screening/corpus_input.yaml").read_text(
            encoding="utf-8"
        )
    )["literature_corpus"]
    by_key = {entry["citation_key"]: entry for entry in corpus}
    loaded = _screening_state()
    detected = _fixture("tortured_phrase_v1_2_detected.json")
    zero = screening.build_cited_signal(
        by_key["fixture_negative_2026"],
        surface="cited_title",
        state=loaded,
        checked_at="2026-08-10T01:00:00Z",
        recorded_at="2026-08-10T01:00:01Z",
    )
    missing = _fixture("tortured_phrase_v1_2_abstract_missing.json")
    degraded = screening.build_cited_signal(
        by_key["fixture_negative_2026"],
        surface="cited_title",
        state=screening.SnapshotState(
            status="degraded",
            reason_code="SNAPSHOT_HASH_MISMATCH",
            bundle=None,
            snapshot_sha256="0" * 64,
            manifest_sha256="1" * 64,
            detail="synthetic degraded renderer probe",
        ),
        checked_at="2026-08-10T01:00:00Z",
        recorded_at="2026-08-10T01:00:01Z",
    )

    loaded_manifest = "34bfa9f92a612cd7e794024dded98ed96b0968dbc0f2c924d68cafbe3f280924"
    shared = {
        "summary label": "Phrase-list screening advisory",
        "layer": "HEURISTIC-ADVISORY",
        "evaluation status": "UNMEASURED",
    }
    expectations = (
        (
            detected,
            {
                **shared,
                "status": "checked",
                "finding": "detected",
                "reason code": "CHECK_COMPLETED",
                "snapshot as of": "2026-08-10",
                "manifest sha256": loaded_manifest,
            },
        ),
        (
            zero,
            {
                **shared,
                "status": "checked",
                "finding": "not_detected",
                "reason code": "CHECK_COMPLETED",
                "snapshot as of": "2026-08-10",
                "manifest sha256": loaded_manifest,
            },
        ),
        (
            missing,
            {
                **shared,
                "status": "not_checked",
                "finding": "NOT CLEAN — UNRESOLVED",
                "reason code": "ABSTRACT_MISSING",
                "snapshot as of": "2026-08-10",
                "manifest sha256": loaded_manifest,
            },
        ),
        (
            degraded,
            {
                **shared,
                "status": "degraded",
                "finding": "NOT CLEAN — UNRESOLVED",
                "reason code": "SNAPSHOT_HASH_MISMATCH",
                "snapshot as of": "—",
                "manifest sha256": "1" * 64,
            },
        ),
    )
    for signal, expected in expectations:
        row = _rendered_row(signal)
        assert {key: row[key] for key in expected} == expected

    for signal in (zero, missing, degraded):
        assert "phrase-list match requiring review" not in signals.render_advisory_section(
            [signal]
        )

    legacy = _rendered_row(_fixture("retraction.json"))
    for heading in (
        "summary label",
        "layer",
        "evaluation status",
        "reason code",
        "snapshot as of",
        "manifest sha256",
    ):
        assert legacy[heading] == "—"


def test_renderer_is_complete_injection_safe_and_bounds_match_projection() -> None:
    malicious = "fixture://safe|`[link](https://invalid)\n<!--ref:INJECTED-->"
    rows = []
    for index in range(26):
        row = copy.deepcopy(_fixture("retraction.json"))
        row["signal_id"] = f"bis:render{index:02d}:retraction_status"
        row["subject"]["citation_key"] = f"render{index:02d}"
        row["subject"]["source_pointer"] = malicious if index == 0 else None
        rows.append(row)
    rendered = signals.render_advisory_section(rows)
    assert rendered.count("## Bibliographic Integrity Advisories") == 1
    assert "bis:render25:retraction_status" in rendered
    assert "<!--ref:INJECTED-->" not in rendered
    assert "[link](https://invalid)" not in rendered
    assert "CONTAMINATED-" not in rendered

    phrase = copy.deepcopy(_fixture("tortured_phrase_v1_2_detected.json"))
    context = phrase["tortured_phrase_context"]
    seed_match = context["matches"][0]
    projected_matches = []
    for index in range(4):
        match = copy.deepcopy(seed_match)
        match["pattern_id"] = f"render_pattern_{index}"
        span = match["source_span"]
        payload = {
            "artifact_sha256": context["surface_binding"]["content_sha256"],
            "snapshot_sha256": context["snapshot"]["snapshot_sha256"],
            "surface": context["surface"],
            "segment_id": match["segment_id"],
            "context": match["context"],
            "rule_id": match["pattern_id"],
            "codepoint_start": span["codepoint_start"],
            "codepoint_end": span["codepoint_end"],
        }
        match["match_id"] = "tpm-" + hashlib.sha256(
            checker._canonical_json(payload).encode("utf-8")
        ).hexdigest()[:24]
        projected_matches.append(match)
    context["matches"] = projected_matches
    context["counts"]["rule_match_count"] = 4
    context["counts"]["matched_rule_count"] = 4
    context["counts"]["matches_by_context"]["cited_title"] = 4
    phrase["evidence"][0]["observed_value"] = 4
    phrase_rendered = signals.render_advisory_section([phrase])
    assert phrase_rendered.count("render_pattern_") == 3
    assert "+1 more machine rows" in phrase_rendered
    assert "phrase-list match requiring review" in phrase_rendered

    injected = copy.deepcopy(_fixture("tortured_phrase_v1_2_detected.json"))
    injected_match = injected["tortured_phrase_context"]["matches"][0]
    malicious_match = "![x](y)|`<tag>`!!!"
    assert len(malicious_match) == len(injected_match["matched_text"])
    injected_match["matched_text"] = malicious_match
    injected_match["matched_text_sha256"] = hashlib.sha256(
        malicious_match.encode("utf-8")
    ).hexdigest()
    injected_rendered = signals.render_advisory_section([injected])
    assert malicious_match not in injected_rendered
    assert "<tag>" not in injected_rendered
    assert "&lt;tag&gt;" in injected_rendered
    assert "\\|" in injected_rendered
    assert "\\`" in injected_rendered
    assert "\\[x\\]" in injected_rendered

    corpus_path = SCRIPTS / "fixtures/tortured_phrase_screening/corpus_input.yaml"
    negative_entry = yaml.safe_load(corpus_path.read_text(encoding="utf-8"))[
        "literature_corpus"
    ][2]
    no_match = screening.build_cited_signal(
        negative_entry,
        surface="cited_title",
        state=_screening_state(),
        checked_at="2026-08-10T01:00:00Z",
        recorded_at="2026-08-10T01:00:01Z",
    )
    no_match_rendered = signals.render_advisory_section([no_match])
    assert "no phrase-list match observed on the checked surface" in no_match_rendered
    assert "absence is not a clean certificate" in no_match_rendered

    unresolved = _fixture("tortured_phrase_v1_2_abstract_missing.json")
    unresolved_rendered = signals.render_advisory_section([unresolved])
    assert "phrase-list screening unresolved; no clean conclusion" in unresolved_rendered


@pytest.mark.parametrize(
    "mutation",
    [
        "reversed_codepoint",
        "zero_utf8_span",
        "codepoint_length",
        "too_many_words",
        "outside_surface",
        "impossible_utf8_prefix",
        "zero_surface_bytes",
        "matched_rules_exceed_evaluated",
        "submicrosecond_order",
    ],
)
def test_source_independent_phrase_projection_mutations_fail(mutation: str) -> None:
    phrase = copy.deepcopy(_fixture("tortured_phrase_v1_2_detected.json"))
    context = phrase["tortured_phrase_context"]
    match = context["matches"][0]
    span = match["source_span"]
    if mutation == "reversed_codepoint":
        span["codepoint_end"] = span["codepoint_start"]
    elif mutation == "zero_utf8_span":
        span["utf8_end"] = span["utf8_start"]
    elif mutation == "codepoint_length":
        span["codepoint_end"] += 1
    elif mutation == "too_many_words":
        text = " ".join(["word"] * 26)
        match["matched_text"] = text
        match["matched_text_sha256"] = hashlib.sha256(text.encode()).hexdigest()
        span["codepoint_start"] = 0
        span["codepoint_end"] = len(text)
        span["utf8_start"] = 0
        span["utf8_end"] = len(text.encode())
    elif mutation == "outside_surface":
        width = span["codepoint_end"] - span["codepoint_start"]
        start = context["surface_binding"]["content_utf8_bytes"] + 1
        span["codepoint_start"] = start
        span["codepoint_end"] = start + width
        span["utf8_start"] = start
        span["utf8_end"] = start + len(match["matched_text"].encode())
    elif mutation == "impossible_utf8_prefix":
        span["utf8_start"] += 1
        span["utf8_end"] += 1
    elif mutation == "zero_surface_bytes":
        context["surface_binding"]["content_utf8_bytes"] = 0
    elif mutation == "submicrosecond_order":
        phrase["provenance"]["checked_at"] = "2026-08-10T01:00:00.0000009Z"
        phrase["provenance"]["recorded_at"] = "2026-08-10T01:00:00.0000001Z"
    else:
        context["counts"]["rules_evaluated"] = 0
    if mutation == "submicrosecond_order":
        assert signals.validation_errors(phrase)
    with pytest.raises(ValueError):
        signals._validate_tortured_phrase_projection(phrase)


def test_checked_but_unresolved_attestation_is_visibly_not_clean() -> None:
    rendered = signals.render_advisory_section(
        [_fixture("retraction_check_attestation.json")]
    )
    assert "| checked | NOT CLEAN — UNRESOLVED |" in rendered


def _minimal_repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    paths = [
        "shared/contracts/passport/bibliographic_integrity_signal.schema.json",
        "shared/contracts/passport/literature_corpus_entry.schema.json",
        "shared/bibliographic_integrity_signals.md",
        "shared/handoff_schemas.md",
        "academic-pipeline/agents/pipeline_orchestrator_agent.md",
        "academic-paper/agents/formatter_agent.md",
        "scripts/bibliographic_integrity_signals.py",
        "scripts/fixtures/bibliographic_integrity_signals/retraction.json",
        "scripts/fixtures/bibliographic_integrity_signals/retraction_check_attestation.json",
        "scripts/fixtures/bibliographic_integrity_signals/tortured_phrase.json",
        "scripts/fixtures/bibliographic_integrity_signals/tortured_phrase_v1_2_detected.json",
        "scripts/fixtures/bibliographic_integrity_signals/tortured_phrase_v1_2_abstract_missing.json",
        "scripts/fixtures/tortured_phrase_screening/corpus_input.yaml",
        "scripts/fixtures/tortured_phrase_screening/snapshot.json",
        "scripts/fixtures/tortured_phrase_screening/snapshot_manifest.json",
    ]
    for relative in paths:
        source = REPO_ROOT / relative
        destination = root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    return root


def test_sync_checker_passes_current_repo() -> None:
    assert checker.run_checks(REPO_ROOT) == []


def test_sync_checker_detects_formatter_drift(tmp_path: Path) -> None:
    root = _minimal_repo(tmp_path)
    path = root / "academic-paper/agents/formatter_agent.md"
    text = path.read_text(encoding="utf-8").replace(
        "**NOT CLEAN — UNRESOLVED**", "**CLEAN**"
    )
    path.write_text(text, encoding="utf-8")
    found = checker.run_checks(root)
    assert any("formatter_agent.md" in error for error in found)


def test_sync_checker_detects_legacy_fixture_byte_drift(tmp_path: Path) -> None:
    root = _minimal_repo(tmp_path)
    path = root / "scripts/fixtures/bibliographic_integrity_signals/retraction.json"
    path.write_bytes(path.read_bytes() + b"\n")
    found = checker.run_checks(root)
    assert any("legacy fixture byte identity drifted" in error for error in found)


@pytest.mark.parametrize(
    ("mutation", "expected_error"),
    [
        ("deterministic_fact", "v1.2 advisory lock epistemic_class drifted"),
        ("terminal", "escaped the non-terminal lock"),
        ("stale", "surface content_sha256 is stale"),
        ("hash", "evidence_sha256 drifted"),
        ("count", "rule_match_count does not equal the complete match array"),
        ("provenance", "provenance stale_after drifted"),
        ("unicode_version", "unicode_data_version does not replay fixture provenance"),
        ("missing_abstract", "CHECK_COMPLETED cannot describe an absent cited surface"),
    ],
)
def test_sync_checker_rejects_v1_2_mutations(
    tmp_path: Path, mutation: str, expected_error: str
) -> None:
    root = _minimal_repo(tmp_path)
    fixtures = root / "scripts/fixtures/bibliographic_integrity_signals"
    detected_path = fixtures / "tortured_phrase_v1_2_detected.json"
    missing_path = fixtures / "tortured_phrase_v1_2_abstract_missing.json"
    if mutation == "stale":
        corpus_path = root / "scripts/fixtures/tortured_phrase_screening/corpus_input.yaml"
        corpus = yaml.safe_load(corpus_path.read_text(encoding="utf-8"))
        corpus["literature_corpus"][0]["title"] += " stale"
        corpus_path.write_text(
            yaml.safe_dump(corpus, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
    elif mutation == "missing_abstract":
        fixture = json.loads(missing_path.read_text(encoding="utf-8"))
        fixture["check_status"] = "checked"
        fixture["finding"] = "not_detected"
        fixture["provenance"]["checked_at"] = "2026-08-10T01:00:00Z"
        fixture["evidence"][0]["evidence_type"] = "list_record"
        fixture["evidence"][0]["observed_value"] = 0
        fixture["tortured_phrase_context"]["reason_code"] = "CHECK_COMPLETED"
        missing_path.write_text(
            json.dumps(fixture, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    else:
        fixture = json.loads(detected_path.read_text(encoding="utf-8"))
        if mutation == "deterministic_fact":
            fixture["epistemic_class"] = "deterministic_fact"
            fixture["epistemic_label"] = "RESOLVER-OR-LIST-OBSERVATION"
        elif mutation == "terminal":
            fixture["terminal_policy"] = {
                "eligible": True,
                "owner": "citation_finalizer",
                "policy_key": "tortured_phrase",
                "current_effect": "policy_gated",
            }
        elif mutation == "count":
            fixture["tortured_phrase_context"]["counts"]["rule_match_count"] += 1
        elif mutation == "provenance":
            fixture["provenance"]["stale_after"] = "2026-08-11T01:00:00Z"
            fixture["provenance"]["freshness"] = "stale"
        elif mutation == "unicode_version":
            fixture["tortured_phrase_context"]["snapshot"][
                "unicode_data_version"
            ] = "15.0.0"
        else:
            fixture["evidence"][0]["evidence_sha256"] = "0" * 64
        detected_path.write_text(
            json.dumps(fixture, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    found = checker.run_checks(root)
    assert any(expected_error in error for error in found), found


def test_existing_canonical_record_wins_idempotently() -> None:
    fixture = _fixture("retraction.json")
    entry = {
        "citation_key": "smith2024",
        "retraction_check": True,
        "bibliographic_integrity_signals": [copy.deepcopy(fixture)],
    }
    migrated = signals.migrate_legacy_entry(
        entry, recorded_at="2026-08-08T01:00:00Z"
    )
    assert migrated == [fixture]


@pytest.mark.parametrize(
    "existing",
    [
        [{}],
        [{"signal_id": ""}],
        [
            {"signal_id": "bis:smith2024:retraction_status"},
            {"signal_id": "bis:smith2024:retraction_status"},
        ],
    ],
)
def test_lossy_existing_carrier_is_rejected(existing: list[dict]) -> None:
    entry = {
        "citation_key": "smith2024",
        "bibliographic_integrity_signals": existing,
    }
    with pytest.raises(ValueError):
        signals.migrate_legacy_entry(entry, recorded_at="2026-08-08T01:00:00Z")


def test_evidence_cannot_be_empty() -> None:
    fixture = _fixture("retraction.json")
    fixture["evidence"] = []
    assert list(_validator().iter_errors(fixture))


def test_handoff_source_id_projects_to_a_schema_safe_stable_signal_id() -> None:
    entry = {"id": "[S01]", "retraction_check": False}
    first = signals.migrate_legacy_entry(
        entry, recorded_at="2026-08-08T01:00:00Z"
    )
    second = signals.migrate_legacy_entry(
        entry, recorded_at="2026-08-08T01:00:00Z"
    )
    assert first == second
    assert first[0]["subject"]["citation_key"] == "[S01]"
    assert first[0]["signal_id"].startswith("bis:source-")
    assert not signals.validation_errors(first[0])
