#!/usr/bin/env python3
"""Drift guard for the #678 bibliographic-integrity signal contract."""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator


DEFAULT_REPO_ROOT = Path(__file__).resolve().parent.parent

LEGACY_FIXTURE_SHA256 = {
    "retraction.json": "18b84b2988c4460e46c02de135b6b985b51251ca2c86ab33fb0f38b21654e93e",
    "retraction_check_attestation.json": "7d8acc7458128e3d58cb43fe7420bd7981d721437f1607de79ca9c2bffd428bf",
    "tortured_phrase.json": "162bcb749fb944dfeb9d51b9e81a166a201bebe9a289e93a9a07bec46dee113f",
}
V12_DETECTED_FIXTURE = "tortured_phrase_v1_2_detected.json"
V12_ABSTRACT_MISSING_FIXTURE = "tortured_phrase_v1_2_abstract_missing.json"
V12_FIXTURE_UNICODE_DATA_VERSION = "14.0.0"
CONTEXTS = (
    "author_prose",
    "quote",
    "cited_title",
    "reference_entry",
    "code_or_verbatim",
    "unknown",
    "cited_abstract",
)
BOUNDARY = {
    "list_match_only": True,
    "origin_inference": "not_performed",
    "contextual_judgment": "not_performed",
    "automatic_rewrite": False,
    "absence_is_clean_certificate": False,
    "native_pps_compatibility": "not_claimed",
    "sharing_scope": "local_only",
}
TERMINAL_LOCK = {
    "eligible": False,
    "owner": "none",
    "policy_key": None,
    "current_effect": "advisory_only",
}


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_text(value: str) -> str:
    return _sha256_bytes(value.encode("utf-8", errors="strict"))


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _signal_id(
    citation_key: str,
    surface: str,
    snapshot_sha256: str | None,
    content_sha256: str | None,
) -> str:
    payload = {
        "citation_key": citation_key,
        "surface": surface,
        "snapshot_sha256": snapshot_sha256,
        "content_sha256": content_sha256,
    }
    suffix = _sha256_text(_canonical_json(payload))[:20]
    surface_slug = "title" if surface == "cited_title" else "abstract"
    return f"bis:{citation_key}:tpm_{surface_slug}_{suffix}"


def _byte_offsets(value: str) -> list[int]:
    offsets = [0]
    total = 0
    for char in value:
        total += len(char.encode("utf-8", errors="strict"))
        offsets.append(total)
    return offsets


def _unique_instance_count(matches: list[dict[str, Any]]) -> int | None:
    by_segment: dict[str, list[tuple[int, int]]] = {}
    for match in matches:
        if not isinstance(match, dict):
            return None
        segment_id = match.get("segment_id")
        span = match.get("source_span")
        if not isinstance(segment_id, str) or not isinstance(span, dict):
            return None
        start = span.get("codepoint_start")
        end = span.get("codepoint_end")
        if (
            isinstance(start, bool)
            or isinstance(end, bool)
            or not isinstance(start, int)
            or not isinstance(end, int)
        ):
            return None
        by_segment.setdefault(segment_id, []).append((start, end))
    count = 0
    for intervals in by_segment.values():
        current_end: int | None = None
        for start, end in sorted(set(intervals)):
            if current_end is None or start >= current_end:
                count += 1
                current_end = end
            else:
                current_end = max(current_end, end)
    return count


def _load(path: Path, errors: list[str]) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"cannot load {path}: {exc}")
        return None
    if not isinstance(value, dict):
        errors.append(f"{path}: expected a JSON object")
        return None
    return value


def _load_fixture_material(
    repo_root: Path, errors: list[str]
) -> tuple[
    dict[str, Any] | None,
    dict[str, Any] | None,
    dict[str, dict[str, Any]],
    str | None,
    str | None,
]:
    fixture_root = repo_root / "scripts/fixtures/tortured_phrase_screening"
    snapshot_path = fixture_root / "snapshot.json"
    manifest_path = fixture_root / "snapshot_manifest.json"
    snapshot = _load(snapshot_path, errors)
    manifest = _load(manifest_path, errors)
    snapshot_sha256: str | None = None
    manifest_sha256: str | None = None
    try:
        snapshot_sha256 = _sha256_bytes(snapshot_path.read_bytes())
    except OSError as exc:
        errors.append(f"cannot hash {snapshot_path}: {exc}")
    try:
        manifest_sha256 = _sha256_bytes(manifest_path.read_bytes())
    except OSError as exc:
        errors.append(f"cannot hash {manifest_path}: {exc}")
    if (
        manifest is not None
        and snapshot_sha256 is not None
        and manifest.get("snapshot_sha256") != snapshot_sha256
    ):
        errors.append(
            "synthetic snapshot manifest does not bind the exact snapshot fixture bytes"
        )
    if snapshot is not None and manifest is not None:
        rules = snapshot.get("rules")
        if not isinstance(rules, list) or manifest.get("rule_count") != len(rules):
            errors.append("synthetic snapshot manifest rule_count drifted")
        for field in ("snapshot_id", "grammar_profile", "normalizer_profile"):
            if snapshot.get(field) != manifest.get(field):
                errors.append(
                    f"synthetic snapshot and manifest disagree on {field}"
                )
        if manifest.get("snapshot_schema_version") != snapshot.get("schema_version"):
            errors.append(
                "synthetic snapshot manifest snapshot_schema_version drifted"
            )

    corpus_path = fixture_root / "corpus_input.yaml"
    corpus_by_key: dict[str, dict[str, Any]] = {}
    try:
        document = yaml.safe_load(corpus_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        errors.append(f"cannot load {corpus_path}: {exc}")
    else:
        corpus = document.get("literature_corpus") if isinstance(document, dict) else None
        if not isinstance(corpus, list):
            errors.append(f"{corpus_path}: expected literature_corpus[]")
        else:
            for index, entry in enumerate(corpus):
                citation_key = entry.get("citation_key") if isinstance(entry, dict) else None
                if not isinstance(citation_key, str) or not citation_key:
                    errors.append(
                        f"{corpus_path}: literature_corpus[{index}] lacks citation_key"
                    )
                    continue
                if citation_key in corpus_by_key:
                    errors.append(
                        f"{corpus_path}: duplicate citation_key {citation_key!r}"
                    )
                    continue
                corpus_by_key[citation_key] = entry
    return snapshot, manifest, corpus_by_key, snapshot_sha256, manifest_sha256


def _check_v12_fixture(
    fixture_path: Path,
    fixture: dict[str, Any],
    *,
    snapshot: dict[str, Any] | None,
    manifest: dict[str, Any] | None,
    corpus_by_key: dict[str, dict[str, Any]],
    snapshot_sha256: str | None,
    manifest_sha256: str | None,
    errors: list[str],
) -> None:
    label = str(fixture_path)

    def problem(message: str) -> None:
        errors.append(f"{label}: {message}")

    locks = {
        "signal_type": "tortured_phrase_match",
        "epistemic_class": "heuristic_advisory",
        "epistemic_label": "HEURISTIC-INDICATOR",
    }
    for field, expected in locks.items():
        if fixture.get(field) != expected:
            problem(f"v1.2 advisory lock {field} drifted")
    if fixture.get("terminal_policy") != TERMINAL_LOCK:
        problem("v1.2 tortured-phrase signal escaped the non-terminal lock")
    if fixture.get("display") != {
        "carrier": "provenance_summary",
        "section": "Bibliographic Integrity Advisories",
        "summary_label": "Phrase-list screening advisory",
        "marker_token": None,
    }:
        problem("v1.2 advisory display lock drifted")

    context = fixture.get("tortured_phrase_context")
    if not isinstance(context, dict):
        problem("missing tortured_phrase_context object")
        return
    if context.get("layer") != "HEURISTIC-ADVISORY":
        problem("tortured_phrase_context.layer drifted")
    if context.get("evaluation_status") != "UNMEASURED":
        problem("tortured_phrase_context.evaluation_status drifted")
    if context.get("boundary") != BOUNDARY:
        problem("tortured_phrase_context advisory boundary drifted")

    snapshot_binding = context.get("snapshot")
    if not isinstance(snapshot_binding, dict):
        problem("missing snapshot binding")
        return
    if snapshot is not None and manifest is not None:
        expected_snapshot = {
            "status": "loaded",
            "reason_code": "CHECK_COMPLETED",
            "snapshot_sha256": snapshot_sha256,
            "manifest_sha256": manifest_sha256,
            "snapshot_id": manifest.get("snapshot_id"),
            "source": manifest.get("source"),
            "supply_mode": manifest.get("supply_mode"),
            "snapshot_schema_version": manifest.get("snapshot_schema_version"),
            "grammar_profile": manifest.get("grammar_profile"),
            "normalizer_profile": manifest.get("normalizer_profile"),
            "unicode_data_version": V12_FIXTURE_UNICODE_DATA_VERSION,
            "rule_count": manifest.get("rule_count"),
            "unsupported_rule_count": manifest.get("unsupported_rule_count"),
            "rights": manifest.get("rights"),
        }
        for field, expected in expected_snapshot.items():
            if snapshot_binding.get(field) != expected:
                problem(f"snapshot binding {field} does not replay fixture provenance")

    subject = fixture.get("subject")
    if not isinstance(subject, dict):
        problem("subject must be an object")
        return
    citation_key = subject.get("citation_key")
    if not isinstance(citation_key, str) or citation_key not in corpus_by_key:
        problem("subject citation_key does not join the synthetic corpus fixture")
        return
    entry = corpus_by_key[citation_key]
    if subject.get("source_pointer") != entry.get("source_pointer"):
        problem("subject source_pointer does not join the synthetic corpus fixture")

    surface = context.get("surface")
    if surface == "cited_title":
        value = entry.get("title")
        locator = "title"
        expected_disposition = "preserve_verbatim_review_context"
    elif surface == "cited_abstract":
        value = entry.get("abstract")
        locator = "abstract"
        expected_disposition = "review_cited_source_no_automatic_rewrite"
    else:
        problem("surface is not cited_title or cited_abstract")
        return
    if value is None or value == "":
        expected_content_sha256 = None
        expected_content_bytes = None
        source_text = ""
    elif isinstance(value, str):
        raw = value.encode("utf-8", errors="strict")
        expected_content_sha256 = _sha256_bytes(raw)
        expected_content_bytes = len(raw)
        source_text = value
    else:
        problem("bound synthetic corpus surface is not a string")
        return
    surface_binding = context.get("surface_binding")
    if not isinstance(surface_binding, dict):
        problem("surface_binding must be an object")
    else:
        if surface_binding.get("content_sha256") != expected_content_sha256:
            problem("surface content_sha256 is stale")
        if surface_binding.get("content_utf8_bytes") != expected_content_bytes:
            problem("surface content_utf8_bytes is stale")

    expected_id = _signal_id(
        citation_key,
        surface,
        snapshot_binding.get("snapshot_sha256"),
        expected_content_sha256,
    )
    if fixture.get("signal_id") != expected_id:
        problem("signal_id does not replay the exact surface/snapshot binding")

    provenance = fixture.get("provenance")
    if not isinstance(provenance, dict):
        problem("provenance must be an object")
    else:
        source = snapshot_binding.get("source")
        source = source if isinstance(source, dict) else {}
        expected_provenance = {
            "source_name": source.get("name"),
            "source_version": source.get("version"),
            "source_sha256": snapshot_binding.get("snapshot_sha256"),
            "stale_after": None,
            "freshness": "unknown",
        }
        for field, expected in expected_provenance.items():
            if provenance.get(field) != expected:
                problem(f"provenance {field} drifted from the exact snapshot binding")

    counts = context.get("counts")
    matches = context.get("matches")
    if not isinstance(counts, dict) or not isinstance(matches, list):
        problem("counts and matches must be present")
        return
    context_counts = counts.get("matches_by_context")
    if not isinstance(context_counts, dict) or set(context_counts) != set(CONTEXTS):
        problem("matches_by_context key set drifted")
        context_counts = {}
    if counts.get("rule_match_count") != len(matches):
        problem("rule_match_count does not equal the complete match array")
    pattern_ids = {
        match.get("pattern_id")
        for match in matches
        if isinstance(match, dict) and isinstance(match.get("pattern_id"), str)
    }
    if counts.get("matched_rule_count") != len(pattern_ids):
        problem("matched_rule_count does not equal unique pattern ids")
    instance_count = _unique_instance_count(matches)
    if counts.get("unique_instance_count") != instance_count:
        problem("unique_instance_count does not replay overlap components")
    expected_rules_evaluated = (
        snapshot_binding.get("rule_count")
        if context.get("reason_code") == "CHECK_COMPLETED"
        else 0
    )
    if counts.get("rules_evaluated") != expected_rules_evaluated:
        problem("rules_evaluated does not match the completed-check state")
    if counts.get("unknown_segments") != 0:
        problem("a structured cited surface reported unknown segments")
    expected_segments = 0 if expected_content_sha256 is None else 1
    if counts.get("segments_total") != expected_segments:
        problem("segments_total does not match surface availability")
    for context_name in CONTEXTS:
        expected_count = len(matches) if context_name == surface else 0
        if context_counts.get(context_name) != expected_count:
            problem(f"matches_by_context.{context_name} drifted")

    rules_by_id: dict[str, dict[str, Any]] = {}
    if snapshot is not None and isinstance(snapshot.get("rules"), list):
        rules_by_id = {
            rule["rule_id"]: rule
            for rule in snapshot["rules"]
            if isinstance(rule, dict) and isinstance(rule.get("rule_id"), str)
        }
    offsets = _byte_offsets(source_text)
    for index, match in enumerate(matches):
        if not isinstance(match, dict):
            problem(f"matches[{index}] is not an object")
            continue
        if match.get("context") != surface:
            problem(f"matches[{index}] context escaped its declared surface")
        if match.get("disposition") != expected_disposition:
            problem(f"matches[{index}] disposition drifted")
        span = match.get("source_span")
        if not isinstance(span, dict):
            problem(f"matches[{index}] lacks source_span")
            continue
        cp_start = span.get("codepoint_start")
        cp_end = span.get("codepoint_end")
        if (
            isinstance(cp_start, bool)
            or isinstance(cp_end, bool)
            or not isinstance(cp_start, int)
            or not isinstance(cp_end, int)
            or not 0 <= cp_start < cp_end <= len(source_text)
        ):
            problem(f"matches[{index}] codepoint span is stale")
            continue
        matched_text = source_text[cp_start:cp_end]
        if span.get("utf8_start") != offsets[cp_start] or span.get(
            "utf8_end"
        ) != offsets[cp_end]:
            problem(f"matches[{index}] UTF-8 span is stale")
        if match.get("matched_text") != matched_text:
            problem(f"matches[{index}] exact text is stale")
        if match.get("matched_text_sha256") != _sha256_text(matched_text):
            problem(f"matches[{index}] exact text hash is stale")
        rule = rules_by_id.get(match.get("pattern_id"))
        expected_pattern_sha = (
            _sha256_text(_canonical_json(rule)) if rule is not None else None
        )
        if match.get("pattern_sha256") != expected_pattern_sha:
            problem(f"matches[{index}] pattern hash does not replay the snapshot")
        match_key = {
            "artifact_sha256": expected_content_sha256,
            "snapshot_sha256": snapshot_binding.get("snapshot_sha256"),
            "surface": surface,
            "segment_id": match.get("segment_id"),
            "context": match.get("context"),
            "rule_id": match.get("pattern_id"),
            "codepoint_start": cp_start,
            "codepoint_end": cp_end,
        }
        expected_match_id = "tpm-" + _sha256_text(_canonical_json(match_key))[:24]
        if match.get("match_id") != expected_match_id:
            problem(f"matches[{index}] match_id binding drifted")

    evidence = fixture.get("evidence")
    if not isinstance(evidence, list) or len(evidence) != 1 or not isinstance(
        evidence[0], dict
    ):
        problem("v1.2 tortured-phrase carrier must contain one evidence row")
        evidence_row: dict[str, Any] = {}
    else:
        evidence_row = evidence[0]
    source = snapshot_binding.get("source")
    expected_source_name = (
        source.get("name")
        if isinstance(source, dict)
        else "tortured-phrase snapshot unavailable"
    )
    if evidence_row.get("source_name") != expected_source_name:
        problem("evidence source_name drifted from snapshot provenance")
    if evidence_row.get("record_locator") != locator:
        problem("evidence record_locator drifted from the declared surface")
    if evidence_row.get("evidence_sha256") != expected_content_sha256:
        problem("evidence_sha256 drifted from the exact surface binding")

    reason_code = context.get("reason_code")
    if reason_code == "CHECK_COMPLETED":
        expected_finding = "detected" if matches else "not_detected"
        expected_evidence_type = "phrase_match" if matches else "list_record"
        if expected_content_sha256 is None:
            problem("CHECK_COMPLETED cannot describe an absent cited surface")
        if fixture.get("check_status") != "checked":
            problem("CHECK_COMPLETED carrier is not checked")
        if fixture.get("finding") != expected_finding:
            problem("CHECK_COMPLETED finding does not follow match count")
        if evidence_row.get("evidence_type") != expected_evidence_type:
            problem("checked evidence_type does not follow finding")
        if evidence_row.get("observed_value") != len(matches):
            problem("checked evidence observed_value does not equal match count")
        if not isinstance(provenance, dict) or provenance.get("checked_at") is None:
            problem("checked carrier lacks checked_at")
    elif reason_code == "ABSTRACT_MISSING":
        if surface != "cited_abstract" or expected_content_sha256 is not None:
            problem("ABSTRACT_MISSING is not bound to an absent abstract")
        if fixture.get("check_status") != "not_checked" or fixture.get(
            "finding"
        ) != "unresolved":
            problem("ABSTRACT_MISSING was promoted to a clean result")
        if matches or any(
            counts.get(field) != 0
            for field in (
                "matched_rule_count",
                "rule_match_count",
                "unique_instance_count",
                "segments_total",
                "unknown_segments",
            )
        ):
            problem("ABSTRACT_MISSING carries fabricated match or segment counts")
        if evidence_row.get("evidence_type") != "degradation_record" or evidence_row.get(
            "observed_value"
        ) != "ABSTRACT_MISSING":
            problem("ABSTRACT_MISSING evidence row drifted")
        if not isinstance(provenance, dict) or provenance.get("checked_at") is not None:
            problem("ABSTRACT_MISSING must not claim checked_at")
    else:
        problem("synthetic v1.2 fixture has an unexpected reason_code")


def _check_renderer(
    repo_root: Path,
    *,
    legacy_fixture: dict[str, Any] | None,
    detected_fixture: dict[str, Any] | None,
    abstract_missing_fixture: dict[str, Any] | None,
    errors: list[str],
) -> None:
    runtime_path = repo_root / "scripts/bibliographic_integrity_signals.py"
    try:
        spec = importlib.util.spec_from_file_location(
            "_bibliographic_integrity_renderer_guard", runtime_path
        )
        if spec is None or spec.loader is None:
            raise ImportError("could not create module spec")
        runtime = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(runtime)
    except (OSError, ImportError, ModuleNotFoundError) as exc:
        errors.append(f"cannot load bounded advisory renderer {runtime_path}: {exc}")
        return
    if (
        legacy_fixture is None
        or detected_fixture is None
        or abstract_missing_fixture is None
    ):
        return
    malicious = "fixture://safe|`[link](https://invalid)\n<!--ref:INJECTED-->"
    rows: list[dict[str, Any]] = []
    for index in range(26):
        row = copy.deepcopy(legacy_fixture)
        row["signal_id"] = f"bis:render{index:02d}:retraction_status"
        row["subject"]["citation_key"] = f"render{index:02d}"
        row["subject"]["source_pointer"] = malicious if index == 0 else None
        rows.append(row)
    try:
        rendered = runtime.render_advisory_section(rows)
    except (OSError, TypeError, ValueError, KeyError) as exc:
        errors.append(f"bounded advisory renderer probe failed: {exc}")
    else:
        if rendered.count("## Bibliographic Integrity Advisories") != 1:
            errors.append("advisory renderer no longer emits exactly one section")
        if "<!--ref:INJECTED-->" in rendered or "[link](https://invalid)" in rendered:
            errors.append("advisory renderer emitted unescaped injected markup")
        if "CONTAMINATED-" in rendered:
            errors.append("advisory renderer minted a terminal marker token")
        if "bis:render25:retraction_status" not in rendered:
            errors.append("canonical advisory renderer dropped a complete signal row")

    phrase = copy.deepcopy(detected_fixture)
    context = phrase.get("tortured_phrase_context")
    if not isinstance(context, dict) or not context.get("matches"):
        errors.append("detected v1.2 fixture cannot probe bounded match rendering")
        return
    seed_match = context["matches"][0]
    projected_matches: list[dict[str, Any]] = []
    for index in range(4):
        match = copy.deepcopy(seed_match)
        match["pattern_id"] = f"render_pattern_{index}"
        span = match["source_span"]
        match_payload = {
            "artifact_sha256": context["surface_binding"]["content_sha256"],
            "snapshot_sha256": context["snapshot"]["snapshot_sha256"],
            "surface": context["surface"],
            "segment_id": match["segment_id"],
            "context": match["context"],
            "rule_id": match["pattern_id"],
            "codepoint_start": span["codepoint_start"],
            "codepoint_end": span["codepoint_end"],
        }
        match["match_id"] = "tpm-" + _sha256_text(
            _canonical_json(match_payload)
        )[:24]
        projected_matches.append(match)
    context["matches"] = projected_matches
    context["counts"]["rule_match_count"] = 4
    context["counts"]["matched_rule_count"] = 4
    context["counts"]["matches_by_context"][context["surface"]] = 4
    phrase["evidence"][0]["observed_value"] = 4
    try:
        phrase_rendered = runtime.render_advisory_section([phrase])
    except (OSError, TypeError, ValueError, KeyError) as exc:
        errors.append(f"bounded phrase-match renderer probe failed: {exc}")
    else:
        if "+1 more machine rows" not in phrase_rendered:
            errors.append("phrase evidence projection exceeded its three-match detail cap")
        if "phrase-list match requiring review" not in phrase_rendered:
            errors.append("detected phrase renderer outcome wording drifted")

    no_match = copy.deepcopy(detected_fixture)
    no_match_context = no_match["tortured_phrase_context"]
    no_match["finding"] = "not_detected"
    no_match_context["matches"] = []
    no_match_context["counts"]["matched_rule_count"] = 0
    no_match_context["counts"]["rule_match_count"] = 0
    no_match_context["counts"]["unique_instance_count"] = 0
    no_match_context["counts"]["matches_by_context"][
        no_match_context["surface"]
    ] = 0
    no_match["evidence"][0]["evidence_type"] = "list_record"
    no_match["evidence"][0]["observed_value"] = 0
    try:
        no_match_rendered = runtime.render_advisory_section([no_match])
    except (OSError, TypeError, ValueError, KeyError) as exc:
        errors.append(f"zero-match renderer probe failed: {exc}")
    else:
        if (
            "no phrase-list match observed on the checked surface" not in no_match_rendered
            or "absence is not a clean certificate" not in no_match_rendered
        ):
            errors.append("zero-match renderer clean-claim boundary drifted")

    try:
        unresolved_rendered = runtime.render_advisory_section(
            [abstract_missing_fixture]
        )
    except (OSError, TypeError, ValueError, KeyError) as exc:
        errors.append(f"unresolved renderer probe failed: {exc}")
    else:
        if (
            "phrase-list screening unresolved; no clean conclusion"
            not in unresolved_rendered
        ):
            errors.append("unresolved renderer clean-claim boundary drifted")


def run_checks(repo_root: Path) -> list[str]:
    errors: list[str] = []
    schema_path = (
        repo_root
        / "shared/contracts/passport/bibliographic_integrity_signal.schema.json"
    )
    schema = _load(schema_path, errors)
    if schema is None:
        return errors
    try:
        Draft202012Validator.check_schema(schema)
    except Exception as exc:  # pragma: no cover - exercised by the CLI guard
        errors.append(f"invalid canonical schema: {exc}")
        return errors
    validator = Draft202012Validator(
        schema, format_checker=Draft202012Validator.FORMAT_CHECKER
    )

    required = set(schema.get("required", []))
    expected = {
        "schema_version",
        "signal_id",
        "signal_type",
        "epistemic_class",
        "epistemic_label",
        "check_status",
        "finding",
        "evidence",
        "provenance",
        "subject",
        "terminal_policy",
        "display",
    }
    if required != expected:
        errors.append("canonical schema required-field set drifted")

    fixtures_dir = repo_root / "scripts/fixtures/bibliographic_integrity_signals"
    fixtures: list[dict[str, Any]] = []
    fixtures_by_name: dict[str, dict[str, Any]] = {}
    for fixture_path in sorted(fixtures_dir.glob("*.json")):
        fixture = _load(fixture_path, errors)
        if fixture is None:
            continue
        fixture_errors = sorted(validator.iter_errors(fixture), key=lambda err: list(err.path))
        for err in fixture_errors:
            errors.append(f"{fixture_path}: {err.message}")
        if json.loads(json.dumps(fixture, sort_keys=True)) != fixture:
            errors.append(f"{fixture_path}: JSON round-trip changed the fixture")
        fixtures.append(fixture)
        fixtures_by_name[fixture_path.name] = fixture
    for name, expected_sha256 in LEGACY_FIXTURE_SHA256.items():
        path = fixtures_dir / name
        try:
            actual_sha256 = _sha256_bytes(path.read_bytes())
        except OSError as exc:
            errors.append(f"cannot hash legacy fixture {path}: {exc}")
            continue
        if actual_sha256 != expected_sha256:
            errors.append(f"{path}: legacy fixture byte identity drifted")
    fixture_types = {fixture.get("signal_type") for fixture in fixtures}
    if not {"retraction_status", "tortured_phrase_match"}.issubset(fixture_types):
        errors.append("fixtures must cover both #651 retraction and #660 tortured phrase")
    fixture_classes = {fixture.get("epistemic_class") for fixture in fixtures}
    if fixture_classes != {
        "deterministic_fact",
        "heuristic_advisory",
        "process_attestation",
    }:
        errors.append("fixtures must cover all three epistemic classes")
    labels = {
        fixture.get("epistemic_class"): fixture.get("epistemic_label")
        for fixture in fixtures
    }
    if labels.get("deterministic_fact") == labels.get("heuristic_advisory"):
        errors.append("deterministic facts and heuristics share an epistemic label")
    if any(fixture.get("display", {}).get("marker_token") is not None for fixture in fixtures):
        errors.append("fixture minted a ref-marker advisory token")

    snapshot, manifest, corpus_by_key, snapshot_sha256, manifest_sha256 = (
        _load_fixture_material(repo_root, errors)
    )
    required_v12 = {
        V12_DETECTED_FIXTURE: ("checked", "detected", "CHECK_COMPLETED"),
        V12_ABSTRACT_MISSING_FIXTURE: (
            "not_checked",
            "unresolved",
            "ABSTRACT_MISSING",
        ),
    }
    for name, expected_state in required_v12.items():
        fixture = fixtures_by_name.get(name)
        if fixture is None:
            errors.append(f"missing required v1.2 tortured-phrase fixture {name}")
            continue
        context = fixture.get("tortured_phrase_context")
        actual_state = (
            fixture.get("check_status"),
            fixture.get("finding"),
            context.get("reason_code") if isinstance(context, dict) else None,
        )
        if actual_state != expected_state:
            errors.append(f"{fixtures_dir / name}: required v1.2 state drifted")
    for name, fixture in fixtures_by_name.items():
        if fixture.get("schema_version") != "bibliographic-integrity-signal/1.2":
            continue
        _check_v12_fixture(
            fixtures_dir / name,
            fixture,
            snapshot=snapshot,
            manifest=manifest,
            corpus_by_key=corpus_by_key,
            snapshot_sha256=snapshot_sha256,
            manifest_sha256=manifest_sha256,
            errors=errors,
        )
    _check_renderer(
        repo_root,
        legacy_fixture=fixtures_by_name.get("retraction.json"),
        detected_fixture=fixtures_by_name.get(V12_DETECTED_FIXTURE),
        abstract_missing_fixture=fixtures_by_name.get(
            V12_ABSTRACT_MISSING_FIXTURE
        ),
        errors=errors,
    )

    entry_schema = _load(
        repo_root / "shared/contracts/passport/literature_corpus_entry.schema.json",
        errors,
    )
    if entry_schema is not None:
        carrier = entry_schema.get("properties", {}).get(
            "bibliographic_integrity_signals"
        )
        if not isinstance(carrier, dict) or carrier.get("type") != "array":
            errors.append("literature corpus schema does not declare the canonical array")

    text_requirements = {
        "shared/bibliographic_integrity_signals.md": (
            "single schema authority",
            "NOT CLEAN — UNRESOLVED",
            "Pinned migration and deprecation path",
            "legacy `retraction_check: true`",
        ),
        "academic-pipeline/agents/pipeline_orchestrator_agent.md": (
            "Canonical bibliographic-integrity carrier (#678)",
            "The finalizer writes no",
            "`display.marker_token`",
            "never clean results",
        ),
        "academic-paper/agents/formatter_agent.md": (
            "Bibliographic Integrity Advisories (#678)",
            "sort rows lexically by `signal_id`",
            "Never mint",
            "NOT CLEAN — UNRESOLVED",
        ),
        "shared/handoff_schemas.md": (
            "Legacy execution attestation",
            "`true` never means",
        ),
    }
    for relative, needles in text_requirements.items():
        path = repo_root / relative
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"cannot read {path}: {exc}")
            continue
        normalized = " ".join(text.split())
        for needle in needles:
            if needle not in text and needle not in normalized:
                errors.append(f"{relative}: missing sync anchor {needle!r}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=DEFAULT_REPO_ROOT)
    args = parser.parse_args()
    errors = run_checks(args.repo_root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Bibliographic-integrity signal contract: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
