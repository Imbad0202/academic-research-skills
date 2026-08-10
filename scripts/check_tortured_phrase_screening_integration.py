#!/usr/bin/env python3
"""Check the hermetic #660 tortured-phrase screening integration boundary.

The matcher tests own behavioral replay.  This static guard prevents the four
contract layers from drifting independently: closed schemas, runtime
epistemics and execution boundaries, byte-bound synthetic fixtures, and
documentation/CI wiring.  It deliberately does not fetch a phrase list, run a
model or judge, or manufacture a held-out score.

Exit 0 on success, 1 on integration errors, and 2 on invocation errors.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import sys
import tomllib
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


REPO_ROOT = Path(__file__).resolve().parent.parent

SNAPSHOT_SCHEMA = Path("shared/contracts/audit/tortured_phrase_snapshot.schema.json")
MANIFEST_SCHEMA = Path(
    "shared/contracts/audit/tortured_phrase_snapshot_manifest.schema.json"
)
ADVISORY_SCHEMA = Path("shared/contracts/audit/tortured_phrase_advisory.schema.json")
SIGNAL_SCHEMA = Path(
    "shared/contracts/passport/bibliographic_integrity_signal.schema.json"
)
RUNTIME = Path("scripts/tortured_phrase_screening.py")
RUNTIME_TEST = Path("scripts/test_tortured_phrase_screening.py")
FIXTURE_ROOT = Path("scripts/fixtures/tortured_phrase_screening")
SNAPSHOT_FIXTURE = FIXTURE_ROOT / "snapshot.json"
MANIFEST_FIXTURE = FIXTURE_ROOT / "snapshot_manifest.json"
EXPECTATIONS_FIXTURE = FIXTURE_ROOT / "seed_expectations.json"
CITED_DETECTED_FIXTURE = Path(
    "scripts/fixtures/bibliographic_integrity_signals/tortured_phrase_v1_2_detected.json"
)
CITED_MISSING_FIXTURE = Path(
    "scripts/fixtures/bibliographic_integrity_signals/"
    "tortured_phrase_v1_2_abstract_missing.json"
)
DESIGN_SPEC = Path("docs/design/2026-08-10-660-tortured-phrase-screening-spec.md")
SIGNAL_PROTOCOL = Path("shared/bibliographic_integrity_signals.md")
CONTRACT_README = Path("shared/contracts/README.md")
INTEGRITY_PROTOCOL = Path("academic-pipeline/references/integrity_review_protocol.md")
CORPUS_CONSUMER_PROTOCOL = Path(
    "academic-pipeline/references/literature_corpus_consumers.md"
)
BIBLIOGRAPHY_AGENT = Path("deep-research/agents/bibliography_agent.md")
PIPELINE_SKILL = Path("academic-pipeline/SKILL.md")
PIPELINE_ORCHESTRATOR = Path(
    "academic-pipeline/agents/pipeline_orchestrator_agent.md"
)
FORMATTER_AGENT = Path("academic-paper/agents/formatter_agent.md")
HANDOFF_SCHEMAS = Path("shared/handoff_schemas.md")
SIGNAL_RUNTIME = Path("scripts/bibliographic_integrity_signals.py")
CORPUS_CHECKER = Path("scripts/check_literature_corpus_schema.py")
CI_MANIFEST = Path("scripts/_ci_pytest_manifest.toml")
WORKFLOW = Path(".github/workflows/spec-consistency.yml")
HELDOUT_ROOT = Path("evals/heldout")
CONFORMANCE_README = HELDOUT_ROOT / "tortured_phrase_conformance/README.md"
MEASUREMENT_PLAN = HELDOUT_ROOT / "tortured_phrase_conformance/measurement_plan.md"
SUITE_REGISTRY = HELDOUT_ROOT / "suite_registry.json"
MEASUREMENT_CONTRACT = HELDOUT_ROOT / "MEASUREMENT_CONTRACT.md"
MEASUREMENT_REPORT = (
    HELDOUT_ROOT / "tortured_phrase_conformance/measurement-2026-08-10.json"
)
MEASUREMENT_TRANSCRIPT = (
    HELDOUT_ROOT
    / "tortured_phrase_conformance/runs/2026-08-10/raw/pytest-transcript.json"
)
MEASUREMENT_EXECUTION_MANIFEST = (
    HELDOUT_ROOT
    / "tortured_phrase_conformance/runs/2026-08-10/execution-manifest.json"
)

FROZEN_MAIN_SHA = "86bf0e5c2cedb300d6d1c6428470cdcedfbf97df"
FROZEN_PLAN_SHA256 = (
    "c5ca307f2e5941d8b6ed411169d7dc956d0290de7c75a54b25b8e04e070e0792"
)
MEASUREMENT_COMMAND = "python -m pytest -q scripts/test_tortured_phrase_screening.py"
MEASUREMENT_COMMAND_SHA256 = (
    "3c85403d49ddbe4907b6277d2664c006b364c045fb1c1db412a817dcd855c110"
)
MEASUREMENT_TRANSCRIPT_SHA256 = (
    "62252493e7c5b04e5a7276e60d54696c6df251f704f6237980f4932b9bb76541"
)
MEASUREMENT_EXECUTION_MANIFEST_SHA256 = (
    "a3801e22c2482a3fba05e65b520ceeedacf7e4d8fdc57f8fce1bfd111d05e6c1"
)
MEASUREMENT_REPORT_SHA256 = (
    "fdb3f4b1300dbe10a9982c7663668e997556868507e4bfcf7cd088f10990fd11"
)
MEASUREMENT_STARTED_AT = "2026-08-10T04:31:45.398248Z"
MEASUREMENT_COMPLETED_AT = "2026-08-10T04:31:50.553009Z"

SNAPSHOT_VERSION = "tortured-phrase-snapshot/1.0"
MANIFEST_VERSION = "tortured-phrase-snapshot-manifest/1.0"
ADVISORY_VERSION = "tortured-phrase-advisory/1.0"
SIGNAL_VERSION = "bibliographic-integrity-signal/1.2"
GRAMMAR_PROFILE = "ars-tortured-phrase-canonical-ast/1.0"
NORMALIZER_PROFILE = "ars-nfkc-casefold-token/1.0"
ADVISORY_LABEL = "Phrase-list screening advisory"

FROZEN_RUNTIME_SHA256 = {
    RUNTIME: "4bb5290194d76f253ba2a23c41ce928d31a6953d73ad3a8686505710e44290c4",
    SIGNAL_RUNTIME: "9c12c9cb426b62d36c88b344067a68b1ce5a17d114d2cbde4390f57eb4cbf2d8",
    CORPUS_CHECKER: "8a1044f6fd6993ee5087b5bb395dcbc6a8b0a73be2d678897c875480332136de",
}

SNAPSHOT_ROOT_KEYS = {
    "schema_version",
    "snapshot_id",
    "grammar_profile",
    "normalizer_profile",
    "rules",
}
MANIFEST_ROOT_KEYS = {
    "schema_version",
    "snapshot_id",
    "source",
    "supply_mode",
    "snapshot_schema_version",
    "snapshot_sha256",
    "grammar_profile",
    "normalizer_profile",
    "preprocessor",
    "unsupported_rule_count",
    "rule_count",
    "rights",
}
ADVISORY_ROOT_KEYS = {
    "schema_version",
    "layer",
    "evaluation_status",
    "surface",
    "input_binding",
    "check_status",
    "finding",
    "reason_code",
    "counts",
    "matches",
    "boundary",
    "report_sha256",
}
COUNTS_KEYS = {
    "rules_evaluated",
    "matched_rule_count",
    "rule_match_count",
    "unique_instance_count",
    "segments_total",
    "unknown_segments",
    "matches_by_context",
}
MATCH_KEYS = {
    "match_id",
    "pattern_id",
    "pattern_sha256",
    "segment_id",
    "context",
    "disposition",
    "source_span",
    "matched_text",
    "matched_text_sha256",
}
BOUNDARY_VALUES = {
    "list_match_only": True,
    "origin_inference": "not_performed",
    "contextual_judgment": "not_performed",
    "automatic_rewrite": False,
    "absence_is_clean_certificate": False,
    "native_pps_compatibility": "not_claimed",
    "sharing_scope": "local_only",
}
CONTEXTS = {
    "author_prose",
    "quote",
    "cited_title",
    "reference_entry",
    "code_or_verbatim",
    "unknown",
    "cited_abstract",
}

FORBIDDEN_IMPORT_ROOTS = {
    "aiohttp",
    "anthropic",
    "cohere",
    "http",
    "httpx",
    "mistralai",
    "multiprocessing",
    "openai",
    "requests",
    "socket",
    "subprocess",
    "urllib",
    "urllib3",
}
FORBIDDEN_IMPORT_PREFIXES = {"http.client", "urllib.request"}
FORBIDDEN_CALLS = {
    "__import__",
    "compile",
    "eval",
    "exec",
    "os.getenv",
    "os.popen",
    "os.system",
    "subprocess.Popen",
    "subprocess.call",
    "subprocess.check_call",
    "subprocess.check_output",
    "subprocess.run",
    "urllib.request.urlopen",
}
FORBIDDEN_PROCESS_CALL_TAILS = {
    "create_subprocess_exec",
    "create_subprocess_shell",
    "execv",
    "execve",
    "spawnl",
    "spawnle",
    "spawnlp",
    "spawnlpe",
    "spawnv",
    "spawnve",
    "spawnvp",
    "spawnvpe",
}
FORBIDDEN_FILE_TIME_TAILS = {"getctime", "getmtime", "lstat", "stat", "touch"}
FORBIDDEN_CLOCK_CALLS = {
    "datetime.date.today",
    "datetime.datetime.now",
    "datetime.datetime.today",
    "datetime.datetime.utcnow",
    "time.monotonic",
    "time.monotonic_ns",
    "time.perf_counter",
    "time.perf_counter_ns",
    "time.process_time",
    "time.time",
    "time.time_ns",
    "uuid.uuid1",
}
FORBIDDEN_SCAN_TAILS = {
    "fwalk",
    "glob",
    "iglob",
    "iterdir",
    "listdir",
    "rglob",
    "scandir",
    "walk",
}
FORBIDDEN_CLI_OPTIONS = {"--all", "--page", "--page-size"}

REQUIRED_DOC_TOKENS = {
    DESIGN_SPEC: (
        "DESIGN-FROZEN / UNMEASURED",
        "HEURISTIC-INDICATOR",
        "HEURISTIC-ADVISORY",
        "one prior v1.2 row for the same",
        "`literal`, `all`, `any`, and `near`",
        "rule-level segment-scoped `exclude_if`",
        "ABSTRACT_EMPTY",
        "DOCUMENT_EMPTY",
        "MAX_CORPUS_ENTRIES = 512",
        "MAX_CORPUS_EXISTING_SIGNALS = 8192",
        "MAX_STRUCTURE_DEPTH = 64",
        "MAX_STRUCTURE_NODES = 200_000",
        "MAX_PARSE_WORK_UNITS = 100_000",
        "pre-normalization maximum of 4,096 raw code points per token",
        "Opaque constructs are lexed strictly in source order",
        "preceded by an odd run of backslashes are literal",
        "`N+1` raises the resource-limit failure",
        "leaves a pre-existing output byte-identical",
        "category label is the neutral **“Phrase-list screening",
        "advisory”**; positive wording appears only on a `detected` row",
        "No #654 measurement row may be manufactured",
        "no traversal flags",
        "native PPS parser",
    ),
    SIGNAL_PROTOCOL: (
        "Version 1.2 carries one current `tortured_phrase_match` row per",
        "heuristic_advisory",
        "HEURISTIC-INDICATOR",
        "evaluation_status: UNMEASURED",
        "ABSTRACT_MISSING",
        "display.marker_token` is always `null",
    ),
    CONTRACT_README: (
        "audit/tortured_phrase_snapshot.schema.json",
        "audit/tortured_phrase_snapshot_manifest.schema.json",
        "audit/tortured_phrase_advisory.schema.json",
        "scripts/tortured_phrase_screening.py",
        "no native PPS importer",
        "ambient clock",
    ),
    INTEGRITY_PROTOCOL: (
        "tortured-phrase-advisory/1.0",
        "HEURISTIC-ADVISORY` / `UNMEASURED",
        "Stage 2.5 or Stage 4.5 PASS/FAIL decision",
        "ABSTRACT_MISSING",
    ),
    CORPUS_CONSUMER_PROTOCOL: (
        "bibliographic-integrity-signal/1.2",
        "each have one current row",
        "Phase 1 consumers do not build, fetch, import, repair, or",
        "redistribute a PPS list",
        "HEURISTIC-ADVISORY` / `UNMEASURED",
    ),
    BIBLIOGRAPHY_AGENT: (
        "scripts/tortured_phrase_screening.py enrich-passport",
        "exactly one current v1.2 `tortured_phrase_match` row",
        "no live model, external API, human or model judge, ambient clock",
        "phrase-list match requiring review",
    ),
    PIPELINE_SKILL: (
        "### Tortured-phrase advisory (#660)",
        "one current v1.2 advisory row per `cited_title` and `cited_abstract`",
        "HEURISTIC-ADVISORY` / `UNMEASURED",
        "timestamps are explicit inputs",
    ),
    PIPELINE_ORCHESTRATOR: (
        "scripts/tortured_phrase_screening.py",
        "Pass `checked_at` and `recorded_at` as explicit RFC 3339 inputs",
        "tortured-phrase-advisory/1.0",
        "evaluation_status: UNMEASURED",
        "schema-valid degraded advisory and then exit 1",
    ),
    FORMATTER_AGENT: (
        "v1.2 `tortured_phrase_match` row",
        "neutral **Phrase-list screening advisory**",
        "ABSTRACT_EMPTY",
        "single bounded page of at most 25 match-detail rows",
        "Do not re-run matching",
        "HEURISTIC-ADVISORY` / `UNMEASURED",
    ),
    HANDOFF_SCHEMAS: (
        "bibliographic-integrity-signal/1.2",
        "one current row for `cited_title` and one for",
        "`cited_abstract`; the surfaces never share a rolled-up status",
        "HEURISTIC-INDICATOR",
        "tortured-phrase-advisory/1.0",
    ),
}
REQUIRED_CONSUMER_TOKENS = {
    SIGNAL_RUNTIME: (
        "HEURISTIC-INDICATOR",
        "tortured_phrase_context",
        "Bibliographic Integrity Advisories",
    ),
    CORPUS_CHECKER: (
        "validate_cited_signal_binding",
        "tortured_phrase_match",
        "multiple current ",
        "tortured-phrase rows for surface",
    ),
}


class DuplicateKeyError(ValueError):
    """Strict JSON duplicate-key failure."""


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def _load_json_bytes(path: Path) -> tuple[dict[str, Any], bytes]:
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raise ValueError("UTF-8 BOM is forbidden")
    text = raw.decode("utf-8", errors="strict")
    value = json.loads(
        text,
        object_pairs_hook=_pairs,
        parse_constant=lambda token: (_ for _ in ()).throw(
            ValueError(f"non-finite JSON constant {token!r}")
        ),
    )
    if not isinstance(value, dict):
        raise ValueError("top level must be an object")
    return value, raw


def _load_json(path: Path) -> dict[str, Any]:
    return _load_json_bytes(path)[0]


def _closed_fields(
    schema: dict[str, Any], expected: set[str], label: str, errors: list[str]
) -> None:
    if schema.get("additionalProperties") is not False:
        errors.append(f"{label}: object must remain closed")
    if set(schema.get("required", ())) != expected:
        errors.append(f"{label}: required field set drifted")
    if set(schema.get("properties", {})) != expected:
        errors.append(f"{label}: property field set drifted")


def _consts(
    schema: dict[str, Any], expected: dict[str, Any], label: str, errors: list[str]
) -> None:
    properties = schema.get("properties", {})
    for name, value in expected.items():
        if properties.get(name, {}).get("const") != value:
            errors.append(f"{label}: {name} must equal {value!r}")


def _property_names(value: Any) -> set[str]:
    names: set[str] = set()
    if isinstance(value, dict):
        properties = value.get("properties")
        if isinstance(properties, dict):
            names.update(properties)
        for child in value.values():
            names.update(_property_names(child))
    elif isinstance(value, list):
        for child in value:
            names.update(_property_names(child))
    return names


def _schema_errors(root: Path) -> list[str]:
    errors: list[str] = []
    schemas: dict[Path, dict[str, Any]] = {}
    for relative in (SNAPSHOT_SCHEMA, MANIFEST_SCHEMA, ADVISORY_SCHEMA, SIGNAL_SCHEMA):
        try:
            schema = _load_json(root / relative)
            Draft202012Validator.check_schema(schema)
            schemas[relative] = schema
        except (OSError, UnicodeError, ValueError, DuplicateKeyError) as exc:
            errors.append(f"{relative}: cannot load/check schema: {exc}")
        except Exception as exc:  # jsonschema.SchemaError without API coupling.
            errors.append(f"{relative}: cannot load/check schema: {exc}")
    if len(schemas) != 4:
        return errors

    snapshot = schemas[SNAPSHOT_SCHEMA]
    _closed_fields(snapshot, SNAPSHOT_ROOT_KEYS, str(SNAPSHOT_SCHEMA), errors)
    _consts(
        snapshot,
        {
            "schema_version": SNAPSHOT_VERSION,
            "grammar_profile": GRAMMAR_PROFILE,
            "normalizer_profile": NORMALIZER_PROFILE,
        },
        str(SNAPSHOT_SCHEMA),
        errors,
    )
    definitions = snapshot.get("$defs", {})
    expression_refs = {
        branch.get("$ref")
        for branch in definitions.get("expression", {}).get("oneOf", ())
        if isinstance(branch, dict)
    }
    if expression_refs != {
        "#/$defs/literal_expression",
        "#/$defs/all_expression",
        "#/$defs/any_expression",
        "#/$defs/near_expression",
    }:
        errors.append(f"{SNAPSHOT_SCHEMA}: expression operator set drifted")
    expression_shapes = {
        "literal_expression": ({"op", "value"}, {"op", "value"}),
        "all_expression": (
            {"op", "terms", "max_span_tokens"},
            {"op", "terms", "max_span_tokens"},
        ),
        "any_expression": ({"op", "alternatives"}, {"op", "alternatives"}),
        "near_expression": (
            {"op", "left", "right", "max_gap_tokens", "ordered"},
            {"op", "left", "right", "max_gap_tokens", "ordered"},
        ),
        "exclusion": (
            {"expression", "within_tokens"},
            {"expression", "within_tokens"},
        ),
        "rule": ({"rule_id", "expression"}, {"rule_id", "expression", "exclude_if"}),
    }
    for name, (required, properties) in expression_shapes.items():
        definition = definitions.get(name, {})
        if definition.get("additionalProperties") is not False:
            errors.append(f"{SNAPSHOT_SCHEMA}: $defs.{name} must remain closed")
        if set(definition.get("required", ())) != required:
            errors.append(f"{SNAPSHOT_SCHEMA}: $defs.{name} required fields drifted")
        if set(definition.get("properties", {})) != properties:
            errors.append(f"{SNAPSHOT_SCHEMA}: $defs.{name} properties drifted")
    for name, key in (("all_expression", "terms"), ("any_expression", "alternatives")):
        array = definitions.get(name, {}).get("properties", {}).get(key, {})
        if (array.get("minItems"), array.get("maxItems")) != (2, 8):
            errors.append(f"{SNAPSHOT_SCHEMA}: {name}.{key} must contain 2..8 nodes")
    exclusion = definitions.get("rule", {}).get("properties", {}).get("exclude_if", {})
    if (exclusion.get("minItems"), exclusion.get("maxItems")) != (1, 8):
        errors.append(f"{SNAPSHOT_SCHEMA}: rule.exclude_if must contain 1..8 exclusions")
    forbidden_schema_fields = {
        "not",
        "regex",
        "wildcard",
        "severity",
        "score",
        "probability",
        "confidence",
        "origin",
        "contamination",
    }
    forbidden = _property_names(snapshot) & forbidden_schema_fields
    if forbidden:
        errors.append(f"{SNAPSHOT_SCHEMA}: forbidden fields {sorted(forbidden)}")

    manifest = schemas[MANIFEST_SCHEMA]
    _closed_fields(manifest, MANIFEST_ROOT_KEYS, str(MANIFEST_SCHEMA), errors)
    _consts(
        manifest,
        {
            "schema_version": MANIFEST_VERSION,
            "snapshot_schema_version": SNAPSHOT_VERSION,
            "grammar_profile": GRAMMAR_PROFILE,
            "normalizer_profile": NORMALIZER_PROFILE,
        },
        str(MANIFEST_SCHEMA),
        errors,
    )
    if set(manifest.get("properties", {}).get("supply_mode", {}).get("enum", ())) != {
        "user_supplied",
        "synthetic_fixture",
    }:
        errors.append(f"{MANIFEST_SCHEMA}: supply_mode vocabulary drifted")
    manifest_defs = manifest.get("$defs", {})
    for name, fields in (
        ("source", {"name", "version", "as_of", "locator"}),
        ("preprocessor", {"name", "version", "native_grammar", "reduction_notes"}),
        (
            "rights",
            {"basis", "redistribution_status", "reference", "user_declaration"},
        ),
    ):
        _closed_fields(
            manifest_defs.get(name, {}), fields, f"{MANIFEST_SCHEMA}: $defs.{name}", errors
        )

    advisory = schemas[ADVISORY_SCHEMA]
    _closed_fields(advisory, ADVISORY_ROOT_KEYS, str(ADVISORY_SCHEMA), errors)
    _consts(
        advisory,
        {
            "schema_version": ADVISORY_VERSION,
            "layer": "HEURISTIC-ADVISORY",
            "evaluation_status": "UNMEASURED",
            "surface": "own_draft",
        },
        str(ADVISORY_SCHEMA),
        errors,
    )
    advisory_defs = advisory.get("$defs", {})
    _closed_fields(
        advisory_defs.get("counts", {}), COUNTS_KEYS, f"{ADVISORY_SCHEMA}: $defs.counts", errors
    )
    _closed_fields(
        advisory_defs.get("match", {}), MATCH_KEYS, f"{ADVISORY_SCHEMA}: $defs.match", errors
    )
    boundary = advisory_defs.get("boundary", {})
    _closed_fields(
        boundary, set(BOUNDARY_VALUES), f"{ADVISORY_SCHEMA}: $defs.boundary", errors
    )
    _consts(boundary, BOUNDARY_VALUES, f"{ADVISORY_SCHEMA}: $defs.boundary", errors)
    contexts = set(
        advisory_defs.get("match", {})
        .get("properties", {})
        .get("context", {})
        .get("enum", ())
    )
    if contexts != CONTEXTS:
        errors.append(f"{ADVISORY_SCHEMA}: match context vocabulary drifted")
    if advisory.get("properties", {}).get("matches", {}).get("maxItems") != 4096:
        errors.append(f"{ADVISORY_SCHEMA}: full machine match bound drifted")
    advisory_reasons = set(advisory_defs.get("reason_code", {}).get("enum", ()))
    if "DOCUMENT_EMPTY" not in advisory_reasons:
        errors.append(f"{ADVISORY_SCHEMA}: reason_code must include DOCUMENT_EMPTY")

    signal = schemas[SIGNAL_SCHEMA]
    versions = set(signal.get("properties", {}).get("schema_version", {}).get("enum", ()))
    if SIGNAL_VERSION not in versions:
        errors.append(f"{SIGNAL_SCHEMA}: missing additive {SIGNAL_VERSION} carrier")
    phrase_context = signal.get("properties", {}).get("tortured_phrase_context", {})
    expected_phrase_fields = {
        "layer",
        "evaluation_status",
        "surface",
        "surface_binding",
        "snapshot",
        "reason_code",
        "counts",
        "matches",
        "boundary",
    }
    _closed_fields(
        phrase_context,
        expected_phrase_fields,
        f"{SIGNAL_SCHEMA}: properties.tortured_phrase_context",
        errors,
    )
    _consts(
        phrase_context,
        {"layer": "HEURISTIC-ADVISORY", "evaluation_status": "UNMEASURED"},
        f"{SIGNAL_SCHEMA}: properties.tortured_phrase_context",
        errors,
    )
    if set(
        phrase_context.get("properties", {}).get("surface", {}).get("enum", ())
    ) != {"cited_title", "cited_abstract"}:
        errors.append(f"{SIGNAL_SCHEMA}: citation surface vocabulary drifted")
    phrase_reasons = set(
        phrase_context.get("properties", {}).get("reason_code", {}).get("enum", ())
    )
    if "ABSTRACT_EMPTY" not in phrase_reasons:
        errors.append(f"{SIGNAL_SCHEMA}: reason_code must include ABSTRACT_EMPTY")

    version_branch: dict[str, Any] | None = None
    type_branch: dict[str, Any] | None = None
    for branch in signal.get("allOf", ()):
        if not isinstance(branch, dict):
            continue
        condition = branch.get("if", {}).get("properties", {})
        if condition.get("schema_version", {}).get("const") == SIGNAL_VERSION:
            version_branch = branch
        if condition.get("signal_type", {}).get("const") == "tortured_phrase_match":
            type_branch = branch
    then = version_branch.get("then", {}) if version_branch else {}
    then_properties = then.get("properties", {})
    if (
        "tortured_phrase_context" not in set(then.get("required", ()))
        or then_properties.get("signal_type", {}).get("const") != "tortured_phrase_match"
        or then_properties.get("epistemic_class", {}).get("const")
        != "heuristic_advisory"
        or then_properties.get("epistemic_label", {}).get("const")
        != "HEURISTIC-INDICATOR"
        or then_properties.get("display", {})
        .get("properties", {})
        .get("summary_label", {})
        .get("const")
        != ADVISORY_LABEL
    ):
        errors.append(f"{SIGNAL_SCHEMA}: v1.2 tortured-phrase profile drifted")
    not_checked_reasons: set[str] = set()
    for branch in signal.get("allOf", ()):
        if not isinstance(branch, dict):
            continue
        then_properties_for_branch = branch.get("then", {}).get("properties", {})
        if (
            then_properties_for_branch.get("check_status", {}).get("const")
            == "not_checked"
            and then_properties_for_branch.get("finding", {}).get("const")
            == "unresolved"
        ):
            not_checked_reasons.update(
                branch.get("if", {})
                .get("properties", {})
                .get("tortured_phrase_context", {})
                .get("properties", {})
                .get("reason_code", {})
                .get("enum", ())
            )
    if "ABSTRACT_EMPTY" not in not_checked_reasons:
        errors.append(
            f"{SIGNAL_SCHEMA}: ABSTRACT_EMPTY must map to not_checked/unresolved"
        )
    type_properties = type_branch.get("then", {}).get("properties", {}) if type_branch else {}
    terminal = type_properties.get("terminal_policy", {}).get("properties", {})
    display = type_properties.get("display", {}).get("properties", {})
    if (
        type_properties.get("epistemic_class", {}).get("const")
        != "heuristic_advisory"
        or type_properties.get("epistemic_label", {}).get("const")
        != "HEURISTIC-INDICATOR"
        or terminal.get("eligible", {}).get("const") is not False
        or terminal.get("owner", {}).get("const") != "none"
        or terminal.get("current_effect", {}).get("const") != "advisory_only"
        or display.get("marker_token", {}).get("type") != "null"
    ):
        errors.append(f"{SIGNAL_SCHEMA}: heuristic/advisory-only policy boundary drifted")
    return errors


def _fixture_errors(root: Path) -> list[str]:
    errors: list[str] = []
    try:
        snapshot, snapshot_raw = _load_json_bytes(root / SNAPSHOT_FIXTURE)
        manifest = _load_json(root / MANIFEST_FIXTURE)
        expectations = _load_json(root / EXPECTATIONS_FIXTURE)
        cited_detected = _load_json(root / CITED_DETECTED_FIXTURE)
        cited_missing = _load_json(root / CITED_MISSING_FIXTURE)
        snapshot_schema = _load_json(root / SNAPSHOT_SCHEMA)
        manifest_schema = _load_json(root / MANIFEST_SCHEMA)
        signal_schema = _load_json(root / SIGNAL_SCHEMA)
    except (OSError, UnicodeError, ValueError, DuplicateKeyError) as exc:
        return [f"#660 fixture load failed: {exc}"]

    for value, schema, label in (
        (snapshot, snapshot_schema, SNAPSHOT_FIXTURE),
        (manifest, manifest_schema, MANIFEST_FIXTURE),
        (cited_detected, signal_schema, CITED_DETECTED_FIXTURE),
        (cited_missing, signal_schema, CITED_MISSING_FIXTURE),
    ):
        validator = Draft202012Validator(
            schema, format_checker=Draft202012Validator.FORMAT_CHECKER
        )
        validation_errors = sorted(
            error.message for error in validator.iter_errors(value)
        )
        if validation_errors:
            errors.append(f"{label}: schema validation failed: {validation_errors[0]}")

    snapshot_sha = hashlib.sha256(snapshot_raw).hexdigest()
    manifest_sha = hashlib.sha256((root / MANIFEST_FIXTURE).read_bytes()).hexdigest()
    if manifest.get("snapshot_sha256") != snapshot_sha:
        errors.append(f"{MANIFEST_FIXTURE}: snapshot_sha256 does not bind exact bytes")
    if expectations.get("snapshot_sha256") != snapshot_sha:
        errors.append(f"{EXPECTATIONS_FIXTURE}: snapshot_sha256 does not bind exact bytes")
    if not (
        snapshot.get("snapshot_id")
        == manifest.get("snapshot_id")
        == expectations.get("snapshot_id")
    ):
        errors.append("#660 fixtures: snapshot_id join drifted")
    rules = snapshot.get("rules", [])
    if manifest.get("rule_count") != len(rules):
        errors.append(f"{MANIFEST_FIXTURE}: rule_count does not bind snapshot rules")
    if manifest.get("unsupported_rule_count") != 0:
        errors.append(f"{MANIFEST_FIXTURE}: partial/unsupported rule fixture is forbidden")
    if not rules or any(
        not isinstance(rule, dict)
        or not isinstance(rule.get("rule_id"), str)
        or not rule["rule_id"].startswith("syn_")
        for rule in rules
    ):
        errors.append(f"{SNAPSHOT_FIXTURE}: every fixture rule must be explicitly synthetic")
    source = manifest.get("source", {})
    preprocessor = manifest.get("preprocessor", {})
    rights = manifest.get("rights", {})
    if (
        manifest.get("supply_mode") != "synthetic_fixture"
        or rights
        != {
            "basis": "synthetic_fixture",
            "redistribution_status": "permitted",
            "reference": None,
            "user_declaration": None,
        }
        or not str(source.get("name", "")).lower().startswith("ars synthetic")
        or not str(source.get("locator", "")).startswith("fixture://")
        or not str(preprocessor.get("native_grammar", "")).startswith("synthetic-")
    ):
        errors.append(f"{MANIFEST_FIXTURE}: synthetic-only provenance/rights boundary drifted")
    if (
        expectations.get("label_scope") != "mechanical_matcher_conformance_only"
        or expectations.get("empirical_accuracy_claimed") is not False
        or expectations.get("contextual_false_positive_labels_provided") is not False
        or expectations.get("contextual_false_negative_labels_provided") is not False
    ):
        errors.append(f"{EXPECTATIONS_FIXTURE}: synthetic UNMEASURED claim ceiling drifted")
    input_paths = {
        item.get("path")
        for item in expectations.get("inputs", ())
        if isinstance(item, dict)
    }
    if input_paths != {"own_draft.md", "own_draft.tex", "corpus_input.yaml"}:
        errors.append(f"{EXPECTATIONS_FIXTURE}: conformance input inventory drifted")
    for fixture, expected in (
        (
            cited_detected,
            {
                "surface": "cited_title",
                "check_status": "checked",
                "finding": "detected",
                "reason_code": "CHECK_COMPLETED",
            },
        ),
        (
            cited_missing,
            {
                "surface": "cited_abstract",
                "check_status": "not_checked",
                "finding": "unresolved",
                "reason_code": "ABSTRACT_MISSING",
            },
        ),
    ):
        context = fixture.get("tortured_phrase_context", {})
        binding = context.get("snapshot", {}) if isinstance(context, dict) else {}
        if (
            fixture.get("schema_version") != SIGNAL_VERSION
            or fixture.get("signal_type") != "tortured_phrase_match"
            or fixture.get("epistemic_class") != "heuristic_advisory"
            or fixture.get("epistemic_label") != "HEURISTIC-INDICATOR"
            or fixture.get("check_status") != expected["check_status"]
            or fixture.get("finding") != expected["finding"]
            or context.get("layer") != "HEURISTIC-ADVISORY"
            or context.get("evaluation_status") != "UNMEASURED"
            or context.get("surface") != expected["surface"]
            or context.get("reason_code") != expected["reason_code"]
            or binding.get("snapshot_sha256") != snapshot_sha
            or binding.get("manifest_sha256") != manifest_sha
            or fixture.get("terminal_policy", {}).get("eligible") is not False
            or fixture.get("display", {}).get("marker_token") is not None
            or fixture.get("display", {}).get("summary_label") != ADVISORY_LABEL
        ):
            errors.append("#660 cited v1.2 fixtures: carrier/replay/claim binding drifted")
    for relative, tokens in (
        (FIXTURE_ROOT / "own_draft.md", ("luminous turnip", "crystal\u00adfern", "silver-\nleaf")),
        (FIXTURE_ROOT / "own_draft.tex", ("luminous turnip", "SILVER-LEAF")),
        (
            FIXTURE_ROOT / "corpus_input.yaml",
            ("fixture_complete_2026", "fixture_missing_2026", "fixture_negative_2026"),
        ),
    ):
        try:
            text = (root / relative).read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append(f"{relative}: cannot read synthetic input: {exc}")
            continue
        missing = [token for token in tokens if token not in text]
        if missing:
            errors.append(f"{relative}: missing conformance markers {missing}")
    return errors


def _function_map(tree: ast.Module) -> dict[str, ast.FunctionDef | ast.AsyncFunctionDef]:
    return {
        node.name: node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


def _assignment_value(tree: ast.Module, name: str) -> Any:
    for node in tree.body:
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        if not any(isinstance(target, ast.Name) and target.id == name for target in targets):
            continue
        try:
            return ast.literal_eval(node.value)
        except (TypeError, ValueError):
            return None
    return None


def _import_aliases(tree: ast.Module) -> dict[str, str]:
    aliases: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for item in node.names:
                aliases[item.asname or item.name.split(".", 1)[0]] = item.name
        elif isinstance(node, ast.ImportFrom) and node.module:
            for item in node.names:
                aliases[item.asname or item.name] = f"{node.module}.{item.name}"
    return aliases


def _qualified(node: ast.AST, aliases: dict[str, str]) -> str | None:
    if isinstance(node, ast.Name):
        return aliases.get(node.id, node.id)
    if isinstance(node, ast.Attribute):
        prefix = _qualified(node.value, aliases)
        return f"{prefix}.{node.attr}" if prefix else node.attr
    return None


def _arg_names(function: ast.FunctionDef | ast.AsyncFunctionDef) -> set[str]:
    return {
        argument.arg
        for argument in (
            function.args.posonlyargs + function.args.args + function.args.kwonlyargs
        )
    }


def _limit_comparison_count(
    function: ast.FunctionDef | ast.AsyncFunctionDef, constant_name: str
) -> int:
    return sum(
        1
        for node in ast.walk(function)
        if isinstance(node, ast.Compare)
        and any(
            isinstance(child, ast.Name)
            and isinstance(child.ctx, ast.Load)
            and child.id == constant_name
            for child in ast.walk(node)
        )
    )


def _strict_limit_guard(
    function: ast.FunctionDef | ast.AsyncFunctionDef,
    constant_name: str,
    *,
    length_of: str | None = None,
    value_name: str | None = None,
) -> ast.If | None:
    """Return an exact ``value > LIMIT: raise MatchLimitError`` guard."""
    if (length_of is None) == (value_name is None):
        raise ValueError("select exactly one limit-guard left-hand shape")
    for node in ast.walk(function):
        if not isinstance(node, ast.If) or not isinstance(node.test, ast.Compare):
            continue
        comparison = node.test
        if (
            len(comparison.ops) != 1
            or not isinstance(comparison.ops[0], ast.Gt)
            or len(comparison.comparators) != 1
            or not isinstance(comparison.comparators[0], ast.Name)
            or comparison.comparators[0].id != constant_name
        ):
            continue
        left = comparison.left
        if length_of is not None:
            left_matches = (
                isinstance(left, ast.Call)
                and isinstance(left.func, ast.Name)
                and left.func.id == "len"
                and len(left.args) == 1
                and isinstance(left.args[0], ast.Name)
                and left.args[0].id == length_of
                and not left.keywords
            )
        else:
            left_matches = isinstance(left, ast.Name) and left.id == value_name
        raises_limit = any(
            isinstance(child, ast.Raise)
            and isinstance(child.exc, ast.Call)
            and isinstance(child.exc.func, ast.Name)
            and child.exc.func.id == "MatchLimitError"
            for statement in node.body
            for child in ast.walk(statement)
        )
        if left_matches and raises_limit:
            return node
    return None


def _existing_signal_count_is_aggregate_sum(
    function: ast.FunctionDef | ast.AsyncFunctionDef,
) -> bool:
    for node in ast.walk(function):
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        if not any(
            isinstance(target, ast.Name) and target.id == "existing_signal_count"
            for target in targets
        ):
            continue
        value = node.value
        return bool(
            isinstance(value, ast.Call)
            and isinstance(value.func, ast.Name)
            and value.func.id == "sum"
            and any(
                isinstance(child, ast.Call)
                and isinstance(child.func, ast.Name)
                and child.func.id == "len"
                for child in ast.walk(value)
            )
            and any(
                isinstance(child, ast.Constant)
                and child.value == "bibliographic_integrity_signals"
                for child in ast.walk(value)
            )
        )
    return False


def _call_lines(
    function: ast.FunctionDef | ast.AsyncFunctionDef,
    aliases: dict[str, str],
    call_name: str,
) -> list[int]:
    return sorted(
        node.lineno
        for node in ast.walk(function)
        if isinstance(node, ast.Call)
        and _qualified(node.func, aliases) == call_name
    )


def _dict_binds_name(
    function: ast.FunctionDef | ast.AsyncFunctionDef, key: str, name: str
) -> bool:
    for node in ast.walk(function):
        if not isinstance(node, ast.Dict):
            continue
        for key_node, value_node in zip(node.keys, node.values):
            if (
                isinstance(key_node, ast.Constant)
                and key_node.value == key
                and isinstance(value_node, ast.Name)
                and isinstance(value_node.ctx, ast.Load)
                and value_node.id == name
            ):
                return True
    return False


def _string_literals(function: ast.FunctionDef | ast.AsyncFunctionDef) -> set[str]:
    return {
        node.value
        for node in ast.walk(function)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    }


def _transitive_hermetic_errors(root: Path, relative: Path) -> list[str]:
    """Apply the hermetic boundary to an imported executable helper module."""

    try:
        source = (root / relative).read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(relative))
    except (OSError, UnicodeError, SyntaxError) as exc:
        return [f"{relative}: cannot parse transitive runtime helper: {exc}"]
    errors: list[str] = []
    aliases = _import_aliases(tree)
    for node in ast.walk(tree):
        imported: list[str] = []
        if isinstance(node, ast.Import):
            imported = [item.name for item in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported = [node.module]
        for name in imported:
            if (
                name.split(".", 1)[0] in FORBIDDEN_IMPORT_ROOTS
                or any(
                    name == prefix or name.startswith(prefix + ".")
                    for prefix in FORBIDDEN_IMPORT_PREFIXES
                )
            ):
                errors.append(
                    f"{relative}: forbidden transitive model/network/process import {name}"
                )
        if isinstance(node, ast.Call):
            name = _qualified(node.func, aliases)
            if name in FORBIDDEN_CALLS:
                errors.append(
                    f"{relative}: forbidden transitive model/network/process call {name}"
                )
            if name in FORBIDDEN_CLOCK_CALLS:
                errors.append(f"{relative}: forbidden transitive ambient clock call {name}")
            tail = name.rsplit(".", 1)[-1] if name else None
            if tail in FORBIDDEN_PROCESS_CALL_TAILS:
                errors.append(f"{relative}: forbidden transitive process call {name}")
            if tail in FORBIDDEN_FILE_TIME_TAILS:
                errors.append(f"{relative}: forbidden transitive file-time call {name}")
            if tail in FORBIDDEN_SCAN_TAILS:
                errors.append(f"{relative}: forbidden transitive discovery call {name}")
        if isinstance(node, ast.Attribute) and _qualified(node, aliases) == "os.environ":
            errors.append(f"{relative}: transitive ambient environment access is forbidden")
    return errors


def _runtime_errors(root: Path) -> list[str]:
    errors: list[str] = []
    try:
        source = (root / RUNTIME).read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(RUNTIME))
    except (OSError, UnicodeError, SyntaxError) as exc:
        return [f"{RUNTIME}: cannot parse: {exc}"]

    errors.extend(_transitive_hermetic_errors(root, SIGNAL_RUNTIME))

    functions = _function_map(tree)
    required_functions = {
        "load_snapshot",
        "build_own_draft_report",
        "validate_own_draft_report",
        "render_own_draft_report",
        "build_cited_signal",
        "validate_cited_signal_binding",
        "enrich_passport",
        "main",
    }
    missing = required_functions - set(functions)
    if missing:
        errors.append(f"{RUNTIME}: missing public functions {sorted(missing)}")
    for name, expected in (
        ("SNAPSHOT_VERSION", SNAPSHOT_VERSION),
        ("MANIFEST_VERSION", MANIFEST_VERSION),
        ("ADVISORY_VERSION", ADVISORY_VERSION),
        ("SIGNAL_VERSION", SIGNAL_VERSION),
        ("GRAMMAR_PROFILE", GRAMMAR_PROFILE),
        ("NORMALIZER_PROFILE", NORMALIZER_PROFILE),
        ("LAYER", "HEURISTIC-ADVISORY"),
        ("EVALUATION_STATUS", "UNMEASURED"),
        ("SUMMARY_LABEL", "Phrase-list match requiring review"),
        ("ADVISORY_LABEL", ADVISORY_LABEL),
        ("MAX_NODE_WITNESSES", 512),
        ("MAX_NODE_COMBINATIONS", 100_000),
        ("MAX_PARSE_INTERVALS", 4096),
        ("MAX_SEGMENTS", 4096),
        ("MAX_PARSE_WORK_UNITS", 100_000),
        ("MAX_RAW_TOKEN_CODEPOINTS", 4096),
        ("MAX_CORPUS_ENTRIES", 512),
        ("MAX_CORPUS_EXISTING_SIGNALS", 8192),
        ("MAX_STRUCTURE_DEPTH", 64),
        ("MAX_STRUCTURE_NODES", 200_000),
        ("MAX_RENDER_PAGE_SIZE", 25),
    ):
        if _assignment_value(tree, name) != expected:
            errors.append(f"{RUNTIME}: {name} must equal {expected!r}")

    aliases = _import_aliases(tree)
    for node in ast.walk(tree):
        imported: list[str] = []
        if isinstance(node, ast.Import):
            imported = [item.name for item in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported = [node.module]
        for name in imported:
            if (
                name.split(".", 1)[0] in FORBIDDEN_IMPORT_ROOTS
                or any(
                    name == prefix or name.startswith(prefix + ".")
                    for prefix in FORBIDDEN_IMPORT_PREFIXES
                )
            ):
                errors.append(f"{RUNTIME}: forbidden model/network/process import {name}")
        if isinstance(node, ast.Call):
            name = _qualified(node.func, aliases)
            if name in FORBIDDEN_CALLS:
                errors.append(f"{RUNTIME}: forbidden model/network/process call {name}")
            if name in FORBIDDEN_CLOCK_CALLS:
                errors.append(f"{RUNTIME}: forbidden ambient clock call {name}")
            tail = name.rsplit(".", 1)[-1] if name else None
            if tail in FORBIDDEN_PROCESS_CALL_TAILS:
                errors.append(f"{RUNTIME}: forbidden process call {name}")
            if tail in FORBIDDEN_FILE_TIME_TAILS:
                errors.append(f"{RUNTIME}: forbidden ambient file-time call {name}")
            if tail in FORBIDDEN_SCAN_TAILS:
                errors.append(f"{RUNTIME}: forbidden ambient discovery call {name}")
        if isinstance(node, ast.Attribute):
            name = _qualified(node, aliases)
            if name == "os.environ":
                errors.append(f"{RUNTIME}: ambient environment access is forbidden")

    option_strings = {
        argument.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "add_argument"
        for argument in node.args
        if isinstance(argument, ast.Constant) and isinstance(argument.value, str)
    }
    forbidden_options = option_strings & FORBIDDEN_CLI_OPTIONS
    if forbidden_options:
        errors.append(f"{RUNTIME}: forbidden renderer options {sorted(forbidden_options)}")
    render = functions.get("render_own_draft_report")
    bounded_slice = False
    if render is not None:
        for node in ast.walk(render):
            if not isinstance(node, ast.Subscript) or not isinstance(node.slice, ast.Slice):
                continue
            if (
                isinstance(node.value, ast.Name)
                and node.value.id == "matches"
                and isinstance(node.slice.upper, ast.Name)
                and node.slice.upper.id == "MAX_RENDER_PAGE_SIZE"
                and node.slice.lower is None
                and node.slice.step is None
            ):
                bounded_slice = True
    if not bounded_slice:
        errors.append(f"{RUNTIME}: own-draft renderer must slice matches at the fixed cap")
    bounded_iteration = bool(
        render
        and any(
            isinstance(node, ast.For)
            and isinstance(node.iter, ast.Name)
            and node.iter.id == "selected"
            for node in ast.walk(render)
        )
    )
    unbounded_iteration = bool(
        render
        and any(
            isinstance(node, ast.For)
            and isinstance(node.iter, ast.Name)
            and node.iter.id == "matches"
            for node in ast.walk(render)
        )
    )
    if not bounded_iteration or unbounded_iteration:
        errors.append(f"{RUNTIME}: own-draft renderer must iterate only the fixed slice")
    limit_sites = (
        ("_minimal_witnesses", "MAX_NODE_WITNESSES", 1),
        ("_literal_witnesses", "MAX_NODE_WITNESSES", 1),
        ("evaluate_expression", "MAX_NODE_WITNESSES", 2),
        ("evaluate_expression", "MAX_NODE_COMBINATIONS", 2),
        ("_append_parse_interval", "MAX_PARSE_INTERVALS", 1),
        ("_append_opaque_opener", "MAX_PARSE_INTERVALS", 1),
        ("segment_document", "MAX_PARSE_INTERVALS", 1),
        ("tokenize", "MAX_RAW_TOKEN_CODEPOINTS", 1),
        ("build_own_draft_report", "MAX_SEGMENTS", 1),
        ("_preflight_json_structure", "MAX_STRUCTURE_DEPTH", 1),
        ("_preflight_json_structure", "MAX_STRUCTURE_NODES", 1),
        ("_preflight_yaml_structure", "MAX_STRUCTURE_DEPTH", 1),
        ("_preflight_yaml_structure", "MAX_STRUCTURE_NODES", 1),
        ("_reject_nonfinite_recursive", "MAX_STRUCTURE_DEPTH", 1),
        ("_reject_nonfinite_recursive", "MAX_STRUCTURE_NODES", 3),
    )
    for function_name, constant_name, minimum in limit_sites:
        function = functions.get(function_name)
        count = (
            _limit_comparison_count(function, constant_name)
            if function is not None
            else 0
        )
        if count < minimum:
            errors.append(
                f"{RUNTIME}: {function_name} must enforce {constant_name} "
                f"in at least {minimum} comparison(s)"
            )
    tokenize_function = functions.get("tokenize")
    raw_token_guard = (
        _strict_limit_guard(
            tokenize_function,
            "MAX_RAW_TOKEN_CODEPOINTS",
            length_of="buffer",
        )
        if tokenize_function is not None
        else None
    )
    if raw_token_guard is None:
        errors.append(
            f"{RUNTIME}: tokenize must enforce MAX_RAW_TOKEN_CODEPOINTS "
            "with the strict N/N+1 guard"
        )
    enricher = functions.get("enrich_passport")
    strict_json = functions.get("_strict_json_bytes")
    structure_guard = functions.get("_reject_nonfinite_recursive")
    if structure_guard is None:
        errors.append(f"{RUNTIME}: missing bounded iterative structure guard")
    if strict_json is None or not _call_lines(
        strict_json, aliases, "_reject_nonfinite_recursive"
    ):
        errors.append(f"{RUNTIME}: strict JSON loader must apply the structure guard")
    if enricher is None or not _call_lines(
        enricher, aliases, "_reject_nonfinite_recursive"
    ):
        errors.append(f"{RUNTIME}: direct passport enricher must apply the structure guard")
    entry_guard = (
        _strict_limit_guard(
            enricher,
            "MAX_CORPUS_ENTRIES",
            length_of="corpus",
        )
        if enricher is not None
        else None
    )
    signal_guard = (
        _strict_limit_guard(
            enricher,
            "MAX_CORPUS_EXISTING_SIGNALS",
            value_name="existing_signal_count",
        )
        if enricher is not None
        else None
    )
    if entry_guard is None:
        errors.append(
            f"{RUNTIME}: enrich_passport must enforce MAX_CORPUS_ENTRIES "
            "with the strict N/N+1 guard"
        )
    if signal_guard is None:
        errors.append(
            f"{RUNTIME}: enrich_passport must enforce "
            "MAX_CORPUS_EXISTING_SIGNALS with the strict N/N+1 guard"
        )
    if enricher is not None and not _existing_signal_count_is_aggregate_sum(enricher):
        errors.append(
            f"{RUNTIME}: existing_signal_count must aggregate every pre-existing "
            "bibliographic_integrity_signals row"
        )
    copy_lines = (
        _call_lines(enricher, aliases, "copy.deepcopy")
        if enricher is not None
        else []
    )
    if (
        len(copy_lines) != 1
        or entry_guard is None
        or signal_guard is None
        or (entry_guard.end_lineno or entry_guard.lineno) >= copy_lines[0]
        or (signal_guard.end_lineno or signal_guard.lineno) >= copy_lines[0]
    ):
        errors.append(
            f"{RUNTIME}: both corpus cardinality guards must run before "
            "copy.deepcopy and matching"
        )
    if enricher is not None and any(
        _call_lines(enricher, aliases, writer)
        for writer in ("_atomic_write_passport", "_atomic_write_json", "_atomic_write_bytes")
    ):
        errors.append(f"{RUNTIME}: enrich_passport must not mutate output paths")

    main_function = functions.get("main")
    enrich_lines = (
        _call_lines(main_function, aliases, "enrich_passport")
        if main_function is not None
        else []
    )
    passport_write_lines = (
        _call_lines(main_function, aliases, "_atomic_write_passport")
        if main_function is not None
        else []
    )
    if (
        len(enrich_lines) != 1
        or len(passport_write_lines) != 1
        or passport_write_lines[0] <= enrich_lines[0]
    ):
        errors.append(
            f"{RUNTIME}: main must write the passport only after enrich_passport "
            "returns successfully"
        )
    cited_builder = functions.get("build_cited_signal")
    if cited_builder is None or not _dict_binds_name(
        cited_builder, "summary_label", "ADVISORY_LABEL"
    ):
        errors.append(
            f"{RUNTIME}: build_cited_signal must bind summary_label to ADVISORY_LABEL"
        )
    own_builder = functions.get("build_own_draft_report")
    if own_builder is None or "DOCUMENT_EMPTY" not in _string_literals(own_builder):
        errors.append(f"{RUNTIME}: empty draft must emit DOCUMENT_EMPTY")
    cited_surface = functions.get("_cited_surface_result")
    if cited_surface is None or "ABSTRACT_EMPTY" not in _string_literals(cited_surface):
        errors.append(f"{RUNTIME}: empty abstract must emit ABSTRACT_EMPTY")
    for name in ("build_own_draft_report", "enrich_passport"):
        function = functions.get(name)
        if function is not None and not {"checked_at", "recorded_at"}.issubset(
            _arg_names(function)
        ):
            errors.append(f"{RUNTIME}: {name} requires explicit checked_at/recorded_at")
    for token in (
        "A match does not establish papermill, AI, or author origin",
        "not a clean-text certificate",
        "one fixed page capped at",
    ):
        if token not in source:
            errors.append(f"{RUNTIME}: missing claim/render boundary {token!r}")
    return errors


def _frozen_runtime_errors(root: Path) -> list[str]:
    """Bind every executable #660 projection surface to reviewed exact bytes."""

    errors: list[str] = []
    for relative, expected in FROZEN_RUNTIME_SHA256.items():
        try:
            actual = hashlib.sha256((root / relative).read_bytes()).hexdigest()
        except OSError as exc:
            errors.append(f"{relative}: cannot read frozen runtime bytes: {exc}")
            continue
        if actual != expected:
            errors.append(
                f"{relative}: frozen runtime sha256 drifted; "
                f"expected {expected}, got {actual}"
            )
    return errors


def _text_binding_errors(root: Path) -> list[str]:
    errors: list[str] = []
    for relative, tokens in {**REQUIRED_DOC_TOKENS, **REQUIRED_CONSUMER_TOKENS}.items():
        try:
            text = (root / relative).read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append(f"{relative}: cannot read: {exc}")
            continue
        missing = [token for token in tokens if token not in text]
        if missing:
            errors.append(f"{relative}: missing #660 integration tokens {missing}")
    return errors


def _consumer_ast_errors(root: Path) -> list[str]:
    errors: list[str] = []
    try:
        tree = ast.parse(
            (root / CORPUS_CHECKER).read_text(encoding="utf-8"),
            filename=str(CORPUS_CHECKER),
        )
    except (OSError, UnicodeError, SyntaxError) as exc:
        return [f"{CORPUS_CHECKER}: cannot parse consumer binding: {exc}"]
    calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "validate_cited_signal_binding"
    ]
    if len(calls) != 1:
        errors.append(
            f"{CORPUS_CHECKER}: must call validate_cited_signal_binding exactly once"
        )
    return errors


def _squash_whitespace(value: str) -> str:
    return " ".join(value.split())


def _measurement_plan_errors(root: Path) -> list[str]:
    errors: list[str] = []
    try:
        registry = _load_json(root / SUITE_REGISTRY)
    except (OSError, UnicodeError, ValueError, DuplicateKeyError) as exc:
        errors.append(f"{SUITE_REGISTRY}: cannot load strict registry JSON: {exc}")
    else:
        if registry.get("tortured_phrase_conformance") != "mechanical_match":
            errors.append(
                f"{SUITE_REGISTRY}: tortured_phrase_conformance must map exactly "
                "to mechanical_match"
            )

    texts: dict[Path, str] = {}
    for relative in (CONFORMANCE_README, MEASUREMENT_PLAN, MEASUREMENT_CONTRACT):
        try:
            texts[relative] = (root / relative).read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append(f"{relative}: cannot read frozen measurement plan binding: {exc}")

    contract = texts.get(MEASUREMENT_CONTRACT, "")
    mirror_prefix = "| `tortured_phrase_conformance` | `mechanical_match` |"
    if contract.count(mirror_prefix) != 1:
        errors.append(
            f"{MEASUREMENT_CONTRACT}: registry mirror must contain exactly one "
            "tortured_phrase_conformance/mechanical_match row"
        )

    plan = _squash_whitespace(texts.get(MEASUREMENT_PLAN, ""))
    plan_tokens = (
        "Status: PRE-REGISTERED / NOT RUN",
        "first commit reachable",
        "use that same 40-hex main-history commit for both "
        "`subject.config.suite_commit` and "
        "`preregistration.frozen_commit`",
        "No retry is permitted",
        "Primary metric: `synthetic_conformance_test_pass_rate`",
        "It uses zero judges, no agreement statistic, no adjudication, and no "
        "experimental arms",
        "A passing row may say only: “the pinned deterministic runtime passed the "
        "pinned repository-owned synthetic conformance suite.”",
        "It remains `UNMEASURED` for contextual validity and real-world "
        "false-positive/false-negative performance",
        "It cannot certify clean text or infer paper-mill, AI, misconduct, "
        "contamination, quality, acceptance, or origin",
    )
    missing_plan = [token for token in plan_tokens if token not in plan]
    if missing_plan:
        errors.append(f"{MEASUREMENT_PLAN}: frozen plan tokens drifted {missing_plan}")

    readme = _squash_whitespace(texts.get(CONFORMANCE_README, ""))
    readme_tokens = (
        f"The frozen post-main measurement was executed once on 2026-08-10 "
        f"against commit `{FROZEN_MAIN_SHA}`",
        "190 of 190 collected tests passed",
        "uses zero judges",
        "exact execution evidence",
        "The supported conclusion is only that the pinned deterministic runtime "
        "passed the pinned repository-owned synthetic conformance suite",
        "real-world false-positive/false-negative performance remain `UNMEASURED`",
        "contextual false-positive/false-negative labels",
        "not empirical false-positive or false-negative rates",
        "only a synthetic grammar/normalization/parser/replay conformance statement",
    )
    missing_readme = [token for token in readme_tokens if token not in readme]
    if missing_readme:
        errors.append(
            f"{CONFORMANCE_README}: UNMEASURED/contextual claim ceiling drifted "
            f"{missing_readme}"
        )
    return errors


def _json_values_equal(actual: Any, expected: Any) -> bool:
    """Compare JSON values without Python's bool/int or int/float coercions."""

    if type(actual) is not type(expected):
        return False
    if isinstance(actual, dict):
        return set(actual) == set(expected) and all(
            _json_values_equal(actual[key], expected[key]) for key in actual
        )
    if isinstance(actual, list):
        return len(actual) == len(expected) and all(
            _json_values_equal(left, right)
            for left, right in zip(actual, expected, strict=True)
        )
    return bool(actual == expected)


def _exact_frozen_object_errors(
    actual: dict[str, Any],
    expected: dict[str, Any],
    label: Path,
) -> list[str]:
    """Compare a closed evidence object while keeping diagnostics field-local."""

    errors: list[str] = []
    actual_keys = set(actual)
    expected_keys = set(expected)
    if actual_keys != expected_keys:
        errors.append(
            f"{label}: closed field set drifted; expected "
            f"{sorted(expected_keys)}, got {sorted(actual_keys)}"
        )
    for field in sorted(actual_keys & expected_keys):
        if not _json_values_equal(actual[field], expected[field]):
            errors.append(f"{label}: frozen field {field!r} drifted")
    return errors


def _canonical_json_bytes(value: dict[str, Any]) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
        + b"\n"
    )


def _walk_heldout_json_files(root: Path) -> tuple[list[Path], list[str]]:
    """Mirror held-out discovery for the closed one-row #660 cardinality rule."""

    heldout = root / HELDOUT_ROOT
    found: list[Path] = []
    walk_errors: list[str] = []
    visited: set[Path] = set()
    repo_real = root.resolve()
    heldout_real = heldout.resolve()

    def walk(directory: Path) -> None:
        try:
            real = directory.resolve()
        except OSError as exc:
            walk_errors.append(f"{directory}: cannot resolve directory: {exc}")
            return
        if real in visited:
            return
        if not (real.is_relative_to(heldout_real) or real.is_relative_to(repo_real)):
            walk_errors.append(
                f"{directory}: symlinked directory resolves outside the repository"
            )
            return
        visited.add(real)
        try:
            entries = sorted(os.scandir(directory), key=lambda entry: entry.name)
        except OSError as exc:
            walk_errors.append(f"{directory}: unreadable directory: {exc}")
            return
        for entry in entries:
            path = directory / entry.name
            try:
                is_dir = entry.is_dir(follow_symlinks=True)
            except OSError:
                is_dir = False
            if is_dir:
                walk(path)
                continue
            if path.suffix.lower() != ".json":
                continue
            try:
                file_real = path.resolve()
            except OSError as exc:
                walk_errors.append(f"{path}: cannot resolve JSON file: {exc}")
                continue
            if not (
                file_real.is_relative_to(heldout_real)
                or file_real.is_relative_to(repo_real)
            ):
                walk_errors.append(
                    f"{path}: file symlink resolves outside the repository"
                )
                continue
            found.append(path)

    if heldout.exists():
        walk(heldout)
    return found, walk_errors


def _expected_measurement_transcript() -> dict[str, Any]:
    return {
        "schema_version": "tortured-phrase-conformance-transcript/1.0",
        "command_utf8": MEASUREMENT_COMMAND,
        "started_at": MEASUREMENT_STARTED_AT,
        "completed_at": MEASUREMENT_COMPLETED_AT,
        "exit_code": 0,
        "environment": {
            "python_implementation": "CPython",
            "python_version": "3.11.15",
            "pytest_version": "9.0.3",
            "jsonschema_version": "4.26.0",
            "ruamel_yaml_version": "0.17.21",
        },
        "stdout_utf8": (
            "........................................................................ "
            "[ 37%]\n"
            "........................................................................ "
            "[ 75%]\n"
            "..............................................                           "
            "[100%]\n"
            "190 passed in 4.28s\n"
        ),
        "stderr_utf8": "",
    }


def _expected_execution_manifest() -> dict[str, Any]:
    return {
        "schema_version": "heldout-execution-manifest/1.0",
        "suite": "tortured_phrase_conformance",
        "created_at": MEASUREMENT_COMPLETED_AT,
        "write_once": True,
        "calls": [
            {
                "call_id": "tpc-2026-08-10-pytest",
                "sequence_index": 1,
                "started_at": MEASUREMENT_STARTED_AT,
                "completed_at": MEASUREMENT_COMPLETED_AT,
                "prompt_sha256": MEASUREMENT_COMMAND_SHA256,
                "output_sha256": MEASUREMENT_TRANSCRIPT_SHA256,
                "attempt": 1,
            }
        ],
    }


def _expected_measurement_report(manifest_sha256: str) -> dict[str, Any]:
    return {
        "measurement_contract": "heldout-measurement/1.1",
        "suite": "tortured_phrase_conformance",
        "suite_class": "mechanical_match",
        "measurement_date": "2026-08-10",
        "decision_relevant": True,
        "subject": {
            "model_id": "deterministic-runtime/tortured_phrase_screening.py",
            "config": {"suite_commit": FROZEN_MAIN_SHA},
        },
        "judge_plan": {"exception": "mechanical_suite"},
        "judges": [],
        "aggregate": {
            "headline": {
                "metric_name": "synthetic_conformance_test_pass_rate",
                "value": 1.0,
                "construction_rule": (
                    "passed_tests divided by collected_tests only when exit_status "
                    "is 0, all collected tests pass, and failed, error, skipped, "
                    "xfailed, and xpassed counts are zero."
                ),
                "estimand_status": "point_estimate",
            },
            "agreement": {
                "rate": None,
                "divergent_items": [],
                "note": (
                    "No judges are used for this mechanical suite, so agreement "
                    "is not applicable."
                ),
            },
        },
        "replicates": {
            "per_item": 1,
            "rule_ref": (
                "evals/heldout/tortured_phrase_conformance/measurement_plan.md"
                "#frozen-metric-and-verdict"
            ),
            "spread": None,
            "exception": (
                "The deterministic exact-byte replay is not rerun to manufacture "
                "variance."
            ),
        },
        "adjudication": {"applies": False},
        "preregistration": {
            "plan_ref": str(MEASUREMENT_PLAN),
            "plan_sha256": FROZEN_PLAN_SHA256,
            "frozen_commit": FROZEN_MAIN_SHA,
            "frozen_before_dispatch": True,
            "rubric_and_plan_frozen_together": True,
            "amendments_append_only": True,
            "amendments": [],
        },
        "execution_manifest": {
            "ref": str(MEASUREMENT_EXECUTION_MANIFEST),
            "sha256": manifest_sha256,
            "write_once": True,
            "claims": [],
        },
        "attempts": {
            "atomicity": (
                "The exact registered command was dispatched once, with no retry "
                "permitted."
            ),
            "partial_published": False,
            "blocked_runs": [],
        },
        "raw_outputs": {
            "retained": True,
            "paths": [str(MEASUREMENT_TRANSCRIPT)],
        },
        "results": {
            "design": "single-arm deterministic synthetic conformance",
            "arm_roles": {
                "treatment_or_cohort_arms": [],
                "variant_packet_arms": [],
            },
            "passed_tests": 190,
            "collected_tests": 190,
            "exit_status": 0,
            "synthetic_conformance_test_pass_rate": 1.0,
        },
        "verdict": (
            "The pinned deterministic runtime passed the pinned repository-owned "
            "synthetic conformance suite."
        ),
        "caveats": [
            "Contextual validity and real-world false-positive/false-negative "
            "performance remain UNMEASURED.",
            "This result cannot certify clean text or infer paper-mill, AI, "
            "misconduct, contamination, quality, acceptance, or origin.",
        ],
    }


def _measurement_errors(root: Path) -> list[str]:
    """Bind the one audited #660 measurement row and its exact evidence chain.

    ``FROZEN_MAIN_SHA`` is the commit whose main ancestry and pre-dispatch freeze
    were established by the human/git-history audit.  This integration checker
    deliberately remains process-free.  The shared held-out report checker owns
    the separate R3/R4 Git-object existence checks; here both commit fields are
    closed to that audited object so neither can drift independently.
    """

    errors: list[str] = []
    values: dict[Path, dict[str, Any]] = {}
    raw_bytes: dict[Path, bytes] = {}
    for relative in (
        MEASUREMENT_REPORT,
        MEASUREMENT_TRANSCRIPT,
        MEASUREMENT_EXECUTION_MANIFEST,
    ):
        try:
            value, raw = _load_json_bytes(root / relative)
        except (OSError, UnicodeError, ValueError, DuplicateKeyError) as exc:
            errors.append(
                f"{relative}: cannot load canonical #660 measurement artifact: {exc}"
            )
        else:
            values[relative] = value
            raw_bytes[relative] = raw

    heldout_files, walk_errors = _walk_heldout_json_files(root)
    errors.extend(f"{HELDOUT_ROOT}: #660 row discovery failed: {error}" for error in walk_errors)
    for path in heldout_files:
        relative = path.relative_to(root)
        if relative in {
            MEASUREMENT_REPORT,
            MEASUREMENT_TRANSCRIPT,
            MEASUREMENT_EXECUTION_MANIFEST,
        }:
            continue
        try:
            candidate, _ = _load_json_bytes(path)
        except (OSError, UnicodeError, ValueError, DuplicateKeyError) as exc:
            if "tortured_phrase_conformance" in path.parts:
                errors.append(
                    f"{relative}: cannot inspect the closed #660 row set: {exc}"
                )
            continue
        if "measurement_contract" in candidate and (
            candidate.get("suite") == "tortured_phrase_conformance"
            or "tortured_phrase_conformance" in path.parts
        ):
            errors.append(
                f"{relative}: second #660 measurement row is forbidden; "
                f"the only canonical row is {MEASUREMENT_REPORT}"
            )

    try:
        plan_sha256 = hashlib.sha256((root / MEASUREMENT_PLAN).read_bytes()).hexdigest()
    except OSError as exc:
        errors.append(f"{MEASUREMENT_PLAN}: cannot hash frozen plan bytes: {exc}")
    else:
        if plan_sha256 != FROZEN_PLAN_SHA256:
            errors.append(
                f"{MEASUREMENT_PLAN}: frozen plan sha256 drifted; expected "
                f"{FROZEN_PLAN_SHA256}, got {plan_sha256}"
            )

    command_sha256 = hashlib.sha256(MEASUREMENT_COMMAND.encode("utf-8")).hexdigest()
    if command_sha256 != MEASUREMENT_COMMAND_SHA256:
        errors.append(
            "#660 registered command bytes no longer match "
            f"MEASUREMENT_COMMAND_SHA256 {MEASUREMENT_COMMAND_SHA256}"
        )

    transcript = values.get(MEASUREMENT_TRANSCRIPT)
    transcript_raw = raw_bytes.get(MEASUREMENT_TRANSCRIPT)
    if transcript is not None and transcript_raw is not None:
        canonical_transcript = _canonical_json_bytes(transcript)
        if transcript_raw != canonical_transcript:
            errors.append(
                f"{MEASUREMENT_TRANSCRIPT}: bytes must be canonical sorted compact "
                "JSON with exactly one terminal LF"
            )
        transcript_sha256 = hashlib.sha256(transcript_raw).hexdigest()
        if transcript_sha256 != MEASUREMENT_TRANSCRIPT_SHA256:
            errors.append(
                f"{MEASUREMENT_TRANSCRIPT}: frozen transcript sha256 drifted; "
                f"expected {MEASUREMENT_TRANSCRIPT_SHA256}, got {transcript_sha256}"
            )
        errors.extend(
            _exact_frozen_object_errors(
                transcript,
                _expected_measurement_transcript(),
                MEASUREMENT_TRANSCRIPT,
            )
        )

    manifest = values.get(MEASUREMENT_EXECUTION_MANIFEST)
    manifest_raw = raw_bytes.get(MEASUREMENT_EXECUTION_MANIFEST)
    manifest_sha256 = ""
    if manifest is not None and manifest_raw is not None:
        if manifest_raw != _canonical_json_bytes(manifest):
            errors.append(
                f"{MEASUREMENT_EXECUTION_MANIFEST}: bytes must be canonical sorted "
                "compact JSON with exactly one terminal LF"
            )
        manifest_sha256 = hashlib.sha256(manifest_raw).hexdigest()
        if manifest_sha256 != MEASUREMENT_EXECUTION_MANIFEST_SHA256:
            errors.append(
                f"{MEASUREMENT_EXECUTION_MANIFEST}: frozen manifest sha256 drifted; "
                f"expected {MEASUREMENT_EXECUTION_MANIFEST_SHA256}, got "
                f"{manifest_sha256}"
            )
        errors.extend(
            _exact_frozen_object_errors(
                manifest,
                _expected_execution_manifest(),
                MEASUREMENT_EXECUTION_MANIFEST,
            )
        )

    report = values.get(MEASUREMENT_REPORT)
    report_raw = raw_bytes.get(MEASUREMENT_REPORT)
    if report is not None and report_raw is not None:
        if report_raw != _canonical_json_bytes(report):
            errors.append(
                f"{MEASUREMENT_REPORT}: bytes must be canonical sorted compact JSON "
                "with exactly one terminal LF"
            )
        report_sha256 = hashlib.sha256(report_raw).hexdigest()
        if report_sha256 != MEASUREMENT_REPORT_SHA256:
            errors.append(
                f"{MEASUREMENT_REPORT}: frozen report sha256 drifted; expected "
                f"{MEASUREMENT_REPORT_SHA256}, got {report_sha256}"
            )
    if report is not None and manifest_sha256:
        errors.extend(
            _exact_frozen_object_errors(
                report,
                _expected_measurement_report(manifest_sha256),
                MEASUREMENT_REPORT,
            )
        )
    return errors


def _ci_errors(root: Path) -> list[str]:
    errors: list[str] = []
    try:
        with (root / CI_MANIFEST).open("rb") as handle:
            manifest = tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        errors.append(f"{CI_MANIFEST}: cannot load: {exc}")
        manifest = {}
    entries = manifest.get("pytest", [])
    expected = {
        "660-tortured-phrase-screening": str(RUNTIME_TEST),
        "660-tortured-phrase-integration": "scripts/test_check_tortured_phrase_screening_integration.py",
    }
    for identifier, path in expected.items():
        matches = [
            item
            for item in entries
            if isinstance(item, dict) and item.get("id") == identifier
        ]
        if len(matches) != 1 or matches[0].get("path") != path:
            errors.append(f"{CI_MANIFEST}: missing exact {identifier!r} -> {path!r} binding")
        if not (root / path).is_file():
            errors.append(f"{CI_MANIFEST}: bound test path does not exist: {path}")
    try:
        workflow = (root / WORKFLOW).read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(f"{WORKFLOW}: cannot read: {exc}")
        workflow = ""
    command = "python3 scripts/check_tortured_phrase_screening_integration.py"
    if workflow.count(command) != 1:
        errors.append(f"{WORKFLOW}: direct #660 integration checker must run exactly once")
    if "python3 scripts/run_ci_pytest_manifest.py" not in workflow:
        errors.append(f"{WORKFLOW}: unified pytest-manifest runner binding is missing")
    return errors


def run_checks(root: Path = REPO_ROOT) -> list[str]:
    """Return stable, de-duplicated integration errors for ``root``."""

    errors = [
        *_schema_errors(root),
        *_fixture_errors(root),
        *_frozen_runtime_errors(root),
        *_runtime_errors(root),
        *_text_binding_errors(root),
        *_consumer_ast_errors(root),
        *_measurement_plan_errors(root),
        *_measurement_errors(root),
        *_ci_errors(root),
    ]
    return sorted(set(errors))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root", type=Path, default=REPO_ROOT, help="Repository root to inspect."
    )
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)
    errors = run_checks(args.root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("#660 tortured-phrase screening integration: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
