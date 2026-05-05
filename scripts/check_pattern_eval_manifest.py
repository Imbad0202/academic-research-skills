#!/usr/bin/env python3
"""Validate ARS v3.6.7 Step 8 pattern-eval fixture manifests.

Spec: docs/design/2026-04-30-ars-v3.6.7-step-6-orchestrator-hooks-spec.md
      §7.2 (micro-fixture schema) + §7.3 (integration-fixture schema)
      + §7.5 (fixture-to-pattern coverage cross-check)

Walks `tests/fixtures/v3_6_7_pattern_eval/`, validates each `manifest.json`
against the matching JSON Schema (selected by `fixture_kind` discriminator),
and asserts the 17-pattern inventory is fully covered by exactly one
micro-fixture per ID.

Two manifest schemas:
- `fixture_kind: "micro"` validated against PATTERN_EVAL_MICRO_SCHEMA
  (the 17 per-pattern fixtures under `<pattern_id>/manifest.json`).
- `fixture_kind: "integration"` validated against PATTERN_EVAL_INTEGRATION_SCHEMA
  (the chapter-level integration fixture under
  `integration/chapter_level_run/manifest.json`).

Exit codes: 0 on pass, 1 on any validation or coverage failure.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError:
    sys.stderr.write(
        "error: jsonschema (Draft 2020-12 support) not installed; "
        "run `pip install jsonschema`\n"
    )
    raise

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "v3_6_7_pattern_eval"

PATTERN_IDS = (
    "A1", "A2", "A3", "A4", "A5",
    "B1", "B2", "B3", "B4", "B5",
    "C1", "C2", "C3",
    "D1", "D2", "D3", "D4",
)

AGENT_ENUM = (
    "synthesis_agent",
    "research_architect_agent",
    "report_compiler_agent",
)

PATTERN_EVAL_MICRO_SCHEMA: dict = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "pattern_eval_manifest.schema.json",
    "type": "object",
    "additionalProperties": False,
    "required": [
        "pattern_id",
        "agent",
        "pattern_scope",
        "stage",
        "fixture_kind",
        "upstream_context",
        "bad_run",
        "good_run",
    ],
    "properties": {
        "pattern_id": {"type": "string", "enum": list(PATTERN_IDS)},
        "agent": {"type": "string", "enum": list(AGENT_ENUM)},
        "pattern_scope": {
            "type": "string",
            "enum": ["agent_specific", "cross_cutting"],
        },
        "stage": {"type": "integer", "minimum": 1, "maximum": 6},
        "fixture_kind": {"const": "micro"},
        "upstream_context": {
            "type": "object",
            "additionalProperties": False,
            "required": ["passport_snippet_path", "prior_artifacts_dir"],
            "properties": {
                "passport_snippet_path": {"type": "string", "minLength": 1},
                "prior_artifacts_dir": {"type": "string", "minLength": 1},
            },
        },
        "bad_run": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "deliverable_path",
                "expected_audit_findings_path",
                "expected_orchestrator_action_path",
            ],
            "properties": {
                "deliverable_path": {"type": "string", "minLength": 1},
                "expected_audit_findings_path": {"type": "string", "minLength": 1},
                "expected_orchestrator_action_path": {"type": "string", "minLength": 1},
            },
        },
        "good_run": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "deliverable_path",
                "expected_audit_findings_path",
                "expected_orchestrator_action_path",
            ],
            "properties": {
                "deliverable_path": {"type": "string", "minLength": 1},
                "expected_audit_findings_path": {"type": "string", "minLength": 1},
                "expected_orchestrator_action_path": {"type": "string", "minLength": 1},
            },
        },
    },
}

PATTERN_EVAL_INTEGRATION_SCHEMA: dict = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "pattern_eval_integration_manifest.schema.json",
    "type": "object",
    "additionalProperties": False,
    "required": [
        "fixture_kind",
        "patterns_triggered",
        "rounds",
        "escalation",
        "rationale_doc",
    ],
    "properties": {
        "fixture_kind": {"const": "integration"},
        "patterns_triggered": {
            "type": "array",
            "minItems": 1,
            "items": {"type": "string", "enum": list(PATTERN_IDS)},
        },
        "rounds": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["round", "target_rounds", "expected_verdict"],
                "properties": {
                    "round": {"type": "integer", "minimum": 1},
                    "target_rounds": {"type": "integer", "minimum": 1},
                    "expected_verdict": {
                        "type": "string",
                        "enum": ["PASS", "MINOR", "MATERIAL", "AUDIT_FAILED"],
                    },
                },
            },
        },
        "escalation": {
            "type": "object",
            "additionalProperties": False,
            "required": ["user_choice"],
            "properties": {
                "user_choice": {
                    "type": "string",
                    "enum": ["ship_with_known_residue", "another_round", "abort_stage"],
                },
                "expected_acknowledgement_finding_ids": {
                    "type": "array",
                    "items": {"type": "string", "minLength": 1},
                },
            },
        },
        "rationale_doc": {"type": "string", "minLength": 1},
    },
}


def _validator(schema: dict) -> Draft202012Validator:
    return Draft202012Validator(schema, format_checker=FormatChecker())


def _validate_manifest(path: Path) -> list[str]:
    """Return list of error strings; empty list = pass."""
    try:
        with path.open("r", encoding="utf-8") as fp:
            doc = json.load(fp)
    except (OSError, json.JSONDecodeError) as exc:
        return [f"{path.relative_to(REPO_ROOT)}: cannot parse JSON: {exc}"]

    fixture_kind = doc.get("fixture_kind")
    if fixture_kind == "micro":
        schema = PATTERN_EVAL_MICRO_SCHEMA
    elif fixture_kind == "integration":
        schema = PATTERN_EVAL_INTEGRATION_SCHEMA
    else:
        return [
            f"{path.relative_to(REPO_ROOT)}: missing or unknown fixture_kind="
            f"{fixture_kind!r} (must be 'micro' or 'integration')"
        ]

    errors = []
    for err in sorted(_validator(schema).iter_errors(doc), key=lambda e: e.path):
        loc = "/".join(str(p) for p in err.absolute_path) or "<root>"
        errors.append(
            f"{path.relative_to(REPO_ROOT)}: schema violation at {loc}: {err.message}"
        )
    return errors


def _validate_micro_directory_id_match(
    manifest_path: Path, doc: dict
) -> list[str]:
    """Manifest's pattern_id must equal directory name."""
    expected = manifest_path.parent.name
    actual = doc.get("pattern_id")
    if expected in PATTERN_IDS and actual != expected:
        return [
            f"{manifest_path.relative_to(REPO_ROOT)}: pattern_id "
            f"{actual!r} does not match directory name {expected!r}"
        ]
    return []


def _validate_micro_paths_exist(manifest_path: Path, doc: dict) -> list[str]:
    """All path fields in a micro manifest must resolve under the fixture dir."""
    errors = []
    base = manifest_path.parent
    keys = [
        ("upstream_context", "passport_snippet_path"),
        ("upstream_context", "prior_artifacts_dir"),
        ("bad_run", "deliverable_path"),
        ("bad_run", "expected_audit_findings_path"),
        ("bad_run", "expected_orchestrator_action_path"),
        ("good_run", "deliverable_path"),
        ("good_run", "expected_audit_findings_path"),
        ("good_run", "expected_orchestrator_action_path"),
    ]
    for parent_key, child_key in keys:
        rel = doc.get(parent_key, {}).get(child_key)
        if not rel:
            continue
        target = base / rel
        if not target.exists():
            errors.append(
                f"{manifest_path.relative_to(REPO_ROOT)}: "
                f"{parent_key}.{child_key}={rel!r} does not exist at {target}"
            )
    return errors


def _coverage_check(micro_manifests: dict[str, Path]) -> list[str]:
    """§7.5 fixture-to-pattern coverage cross-check."""
    errors = []
    seen = set(micro_manifests.keys())
    expected = set(PATTERN_IDS)
    missing = sorted(expected - seen)
    extra = sorted(seen - expected)
    if missing:
        errors.append(
            "coverage gap: pattern IDs missing micro-fixture: " + ", ".join(missing)
        )
    if extra:
        errors.append(
            "coverage drift: micro-fixture present for non-enumerated pattern: "
            + ", ".join(extra)
        )
    return errors


def main() -> int:
    if not FIXTURE_ROOT.exists():
        sys.stderr.write(
            f"error: fixture root not found: {FIXTURE_ROOT.relative_to(REPO_ROOT)}\n"
        )
        return 1

    all_errors: list[str] = []

    micro_manifests: dict[str, Path] = {}
    for entry in sorted(FIXTURE_ROOT.iterdir()):
        if not entry.is_dir() or entry.name == "integration":
            continue
        manifest = entry / "manifest.json"
        if not manifest.exists():
            all_errors.append(
                f"{entry.relative_to(REPO_ROOT)}: missing manifest.json"
            )
            continue
        errors = _validate_manifest(manifest)
        if errors:
            all_errors.extend(errors)
            continue
        with manifest.open("r", encoding="utf-8") as fp:
            doc = json.load(fp)
        if doc.get("fixture_kind") != "micro":
            all_errors.append(
                f"{manifest.relative_to(REPO_ROOT)}: top-level fixture must be "
                f"fixture_kind='micro' (got {doc.get('fixture_kind')!r})"
            )
            continue
        all_errors.extend(_validate_micro_directory_id_match(manifest, doc))
        all_errors.extend(_validate_micro_paths_exist(manifest, doc))
        micro_manifests[doc["pattern_id"]] = manifest

    integration_manifest = FIXTURE_ROOT / "integration" / "chapter_level_run" / "manifest.json"
    if integration_manifest.exists():
        errors = _validate_manifest(integration_manifest)
        if errors:
            all_errors.extend(errors)
    else:
        all_errors.append(
            f"{integration_manifest.relative_to(REPO_ROOT)}: missing"
        )

    all_errors.extend(_coverage_check(micro_manifests))

    if all_errors:
        sys.stderr.write("\n".join(all_errors) + "\n")
        sys.stderr.write(f"\n{len(all_errors)} validation error(s)\n")
        return 1
    sys.stdout.write(
        f"OK: {len(micro_manifests)}/17 micro-fixture manifests valid; "
        "1 integration manifest valid; coverage 17/17.\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
