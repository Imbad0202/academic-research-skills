"""Mutation tests for the hermetic #660 integration guard."""
from __future__ import annotations

import ast
import json
import shutil
import sys
from pathlib import Path
from typing import Any, Callable

import pytest


SCRIPTS = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))

import check_tortured_phrase_screening_integration as integration  # noqa: E402


COPIED_FILES = (
    integration.SNAPSHOT_SCHEMA,
    integration.MANIFEST_SCHEMA,
    integration.ADVISORY_SCHEMA,
    integration.SIGNAL_SCHEMA,
    integration.RUNTIME,
    integration.RUNTIME_TEST,
    Path("scripts/check_tortured_phrase_screening_integration.py"),
    Path("scripts/test_check_tortured_phrase_screening_integration.py"),
    integration.SNAPSHOT_FIXTURE,
    integration.MANIFEST_FIXTURE,
    integration.EXPECTATIONS_FIXTURE,
    integration.CITED_DETECTED_FIXTURE,
    integration.CITED_MISSING_FIXTURE,
    integration.FIXTURE_ROOT / "own_draft.md",
    integration.FIXTURE_ROOT / "own_draft.tex",
    integration.FIXTURE_ROOT / "corpus_input.yaml",
    integration.DESIGN_SPEC,
    integration.SIGNAL_PROTOCOL,
    integration.CONTRACT_README,
    integration.INTEGRITY_PROTOCOL,
    integration.CORPUS_CONSUMER_PROTOCOL,
    integration.BIBLIOGRAPHY_AGENT,
    integration.PIPELINE_SKILL,
    integration.PIPELINE_ORCHESTRATOR,
    integration.FORMATTER_AGENT,
    integration.HANDOFF_SCHEMAS,
    integration.SIGNAL_RUNTIME,
    integration.CORPUS_CHECKER,
    integration.CI_MANIFEST,
    integration.WORKFLOW,
    integration.CONFORMANCE_README,
    integration.MEASUREMENT_PLAN,
    integration.SUITE_REGISTRY,
    integration.MEASUREMENT_CONTRACT,
)


def _copy_repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    for relative in COPIED_FILES:
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO_ROOT / relative, target)
    return root


def _rewrite_json(
    root: Path, relative: Path, mutation: Callable[[dict[str, Any]], None]
) -> None:
    path = root / relative
    value = json.loads(path.read_text(encoding="utf-8"))
    mutation(value)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _replace(root: Path, relative: Path, old: str, new: str) -> None:
    path = root / relative
    text = path.read_text(encoding="utf-8")
    assert old in text
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def _replace_nth(
    root: Path, relative: Path, old: str, new: str, occurrence: int
) -> None:
    path = root / relative
    text = path.read_text(encoding="utf-8")
    start = -len(old)
    for _ in range(occurrence):
        start = text.find(old, start + len(old))
        assert start >= 0
    path.write_text(text[:start] + new + text[start + len(old) :], encoding="utf-8")


def _assert_error(root: Path, expected: str) -> None:
    errors = integration.run_checks(root)
    assert any(expected in error for error in errors), errors


def test_repository_integration_is_currently_green() -> None:
    assert integration.run_checks(REPO_ROOT) == []


@pytest.mark.parametrize(
    "relative",
    (
        integration.RUNTIME,
        integration.SIGNAL_RUNTIME,
        integration.CORPUS_CHECKER,
    ),
)
def test_reviewed_runtime_byte_drift_fails(tmp_path: Path, relative: Path) -> None:
    root = _copy_repo(tmp_path)
    path = root / relative
    path.write_bytes(path.read_bytes() + b"\n# frozen-byte drift\n")
    _assert_error(root, "frozen runtime sha256 drifted")


def test_closed_snapshot_schema_operator_drift_fails(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)

    def mutate(schema: dict[str, Any]) -> None:
        all_expression = schema["$defs"]["all_expression"]
        all_expression["required"][1] = "operands"
        all_expression["properties"]["operands"] = all_expression["properties"].pop(
            "terms"
        )

    _rewrite_json(root, integration.SNAPSHOT_SCHEMA, mutate)
    _assert_error(root, "$defs.all_expression properties drifted")


def test_rule_exclusion_shape_drift_fails(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)

    def mutate(schema: dict[str, Any]) -> None:
        schema["$defs"]["rule"]["properties"]["exclude_if"]["maxItems"] = 9

    _rewrite_json(root, integration.SNAPSHOT_SCHEMA, mutate)
    _assert_error(root, "rule.exclude_if must contain 1..8")


def test_manifest_shape_drift_fails(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)

    def mutate(schema: dict[str, Any]) -> None:
        source = schema["$defs"]["source"]
        source["required"].remove("locator")
        source["properties"].pop("locator")

    _rewrite_json(root, integration.MANIFEST_SCHEMA, mutate)
    _assert_error(root, "$defs.source: required field set drifted")


@pytest.mark.parametrize(
    ("field", "value"),
    [("layer", "DETERMINISTIC"), ("evaluation_status", "MEASURED")],
)
def test_own_advisory_claim_const_drift_fails(
    tmp_path: Path, field: str, value: str
) -> None:
    root = _copy_repo(tmp_path)

    def mutate(schema: dict[str, Any]) -> None:
        schema["properties"][field]["const"] = value

    _rewrite_json(root, integration.ADVISORY_SCHEMA, mutate)
    _assert_error(root, f"{field} must equal")


def test_own_advisory_schema_requires_document_empty(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)

    def mutate(schema: dict[str, Any]) -> None:
        schema["$defs"]["reason_code"]["enum"].remove("DOCUMENT_EMPTY")

    _rewrite_json(root, integration.ADVISORY_SCHEMA, mutate)
    _assert_error(root, "reason_code must include DOCUMENT_EMPTY")


def test_cited_schema_requires_abstract_empty(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)

    def mutate(schema: dict[str, Any]) -> None:
        schema["properties"]["tortured_phrase_context"]["properties"]["reason_code"][
            "enum"
        ].remove("ABSTRACT_EMPTY")

    _rewrite_json(root, integration.SIGNAL_SCHEMA, mutate)
    _assert_error(root, "reason_code must include ABSTRACT_EMPTY")


def test_abstract_empty_must_remain_not_checked_unresolved(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)

    def mutate(schema: dict[str, Any]) -> None:
        branch = next(
            item
            for item in schema["allOf"]
            if "ABSTRACT_EMPTY"
            in item.get("if", {})
            .get("properties", {})
            .get("tortured_phrase_context", {})
            .get("properties", {})
            .get("reason_code", {})
            .get("enum", ())
        )
        branch["if"]["properties"]["tortured_phrase_context"]["properties"][
            "reason_code"
        ]["enum"].remove("ABSTRACT_EMPTY")

    _rewrite_json(root, integration.SIGNAL_SCHEMA, mutate)
    _assert_error(root, "ABSTRACT_EMPTY must map to not_checked/unresolved")


def test_v12_signal_epistemic_profile_drift_fails(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)

    def mutate(schema: dict[str, Any]) -> None:
        branch = next(
            item
            for item in schema["allOf"]
            if item.get("if", {})
            .get("properties", {})
            .get("schema_version", {})
            .get("const")
            == integration.SIGNAL_VERSION
        )
        branch["then"]["properties"]["epistemic_label"]["const"] = (
            "RESOLVER-OR-LIST-OBSERVATION"
        )

    _rewrite_json(root, integration.SIGNAL_SCHEMA, mutate)
    _assert_error(root, "v1.2 tortured-phrase profile drifted")


def test_v12_signal_neutral_label_drift_fails(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)

    def mutate(schema: dict[str, Any]) -> None:
        branch = next(
            item
            for item in schema["allOf"]
            if item.get("if", {})
            .get("properties", {})
            .get("schema_version", {})
            .get("const")
            == integration.SIGNAL_VERSION
        )
        branch["then"]["properties"]["display"]["properties"]["summary_label"][
            "const"
        ] = "Origin finding"

    _rewrite_json(root, integration.SIGNAL_SCHEMA, mutate)
    _assert_error(root, "v1.2 tortured-phrase profile drifted")


def test_signal_terminal_promotion_fails(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)

    def mutate(schema: dict[str, Any]) -> None:
        branch = next(
            item
            for item in schema["allOf"]
            if item.get("if", {})
            .get("properties", {})
            .get("signal_type", {})
            .get("const")
            == "tortured_phrase_match"
        )
        branch["then"]["properties"]["terminal_policy"]["properties"]["eligible"] = {
            "const": True
        }

    _rewrite_json(root, integration.SIGNAL_SCHEMA, mutate)
    _assert_error(root, "heuristic/advisory-only policy boundary drifted")


def test_strict_json_duplicate_schema_key_fails(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    path = root / integration.SNAPSHOT_SCHEMA
    text = path.read_text(encoding="utf-8")
    path.write_text(
        text.replace(
            '"title": "Tortured-phrase canonical snapshot",',
            '"title": "Tortured-phrase canonical snapshot",\n  "title": "duplicate",',
            1,
        ),
        encoding="utf-8",
    )
    _assert_error(root, "duplicate JSON key")


def test_fixture_snapshot_exact_byte_hash_drift_fails(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    path = root / integration.SNAPSHOT_FIXTURE
    path.write_bytes(path.read_bytes() + b" ")
    _assert_error(root, "snapshot_sha256 does not bind exact bytes")


def test_fixture_must_remain_synthetic_only(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)

    def mutate(manifest: dict[str, Any]) -> None:
        manifest["supply_mode"] = "user_supplied"

    _rewrite_json(root, integration.MANIFEST_FIXTURE, mutate)
    _assert_error(root, "synthetic-only provenance/rights boundary drifted")


def test_cited_fixture_must_bind_the_detached_manifest_bytes(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)

    def mutate(fixture: dict[str, Any]) -> None:
        fixture["tortured_phrase_context"]["snapshot"]["manifest_sha256"] = "0" * 64

    _rewrite_json(root, integration.CITED_DETECTED_FIXTURE, mutate)
    _assert_error(root, "cited v1.2 fixtures: carrier/replay/claim binding drifted")


@pytest.mark.parametrize(
    "field",
    (
        "empirical_accuracy_claimed",
        "contextual_false_positive_labels_provided",
        "contextual_false_negative_labels_provided",
    ),
)
def test_seed_cannot_claim_contextual_measurement(tmp_path: Path, field: str) -> None:
    root = _copy_repo(tmp_path)

    def mutate(expectations: dict[str, Any]) -> None:
        expectations[field] = True

    _rewrite_json(root, integration.EXPECTATIONS_FIXTURE, mutate)
    _assert_error(root, "synthetic UNMEASURED claim ceiling drifted")


@pytest.mark.parametrize(
    "module", ("requests", "openai", "subprocess", "urllib.request")
)
def test_runtime_forbids_network_model_and_process_imports(
    tmp_path: Path, module: str
) -> None:
    root = _copy_repo(tmp_path)
    path = root / integration.RUNTIME
    path.write_text(
        path.read_text(encoding="utf-8") + f"\nimport {module}\n",
        encoding="utf-8",
    )
    _assert_error(root, f"forbidden model/network/process import {module}")


def test_runtime_forbids_process_calls_without_subprocess_import(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    path = root / integration.RUNTIME
    path.write_text(
        path.read_text(encoding="utf-8")
        + "\n\ndef _process_mutation():\n    return os.system('forbidden')\n",
        encoding="utf-8",
    )
    _assert_error(root, "forbidden model/network/process call os.system")


@pytest.mark.parametrize(
    "body",
    (
        "return dt.datetime.now()",
        "return dt.datetime.utcnow()",
        "import time\n    return time.time()",
    ),
)
def test_runtime_forbids_ambient_clock(tmp_path: Path, body: str) -> None:
    root = _copy_repo(tmp_path)
    path = root / integration.RUNTIME
    path.write_text(
        path.read_text(encoding="utf-8") + f"\n\ndef _ambient_clock_mutation():\n    {body}\n",
        encoding="utf-8",
    )
    _assert_error(root, "forbidden ambient clock call")


def test_runtime_forbids_source_file_time(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    path = root / integration.RUNTIME
    path.write_text(
        path.read_text(encoding="utf-8")
        + "\n\ndef _file_time_mutation(path):\n    return path.stat().st_mtime\n",
        encoding="utf-8",
    )
    _assert_error(root, "forbidden ambient file-time call")


def test_runtime_forbids_ambient_environment(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    path = root / integration.RUNTIME
    path.write_text(
        path.read_text(encoding="utf-8")
        + "\n\ndef _ambient_environment_mutation():\n    return os.environ.get('API_KEY')\n",
        encoding="utf-8",
    )
    _assert_error(root, "ambient environment access is forbidden")


def test_runtime_forbids_ambient_file_discovery(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    path = root / integration.RUNTIME
    path.write_text(
        path.read_text(encoding="utf-8")
        + "\n\ndef _ambient_scan_mutation(path):\n    return path.rglob('*.json')\n",
        encoding="utf-8",
    )
    _assert_error(root, "forbidden ambient discovery call")


@pytest.mark.parametrize(
    ("body", "expected"),
    (
        ("import requests\n", "forbidden transitive model/network/process import"),
        (
            "\n\ndef _clock_mutation():\n    return dt.datetime.now()\n",
            "forbidden transitive ambient clock call",
        ),
        (
            "\nimport os\n\ndef _environment_mutation():\n"
            "    return os.environ.get('TOKEN')\n",
            "transitive ambient environment access is forbidden",
        ),
        (
            "\nimport subprocess\n\ndef _process_mutation():\n"
            "    return subprocess.run([])\n",
            "forbidden transitive model/network/process import",
        ),
    ),
)
def test_imported_signal_helper_shares_the_hermetic_boundary(
    tmp_path: Path, body: str, expected: str
) -> None:
    root = _copy_repo(tmp_path)
    path = root / integration.SIGNAL_RUNTIME
    path.write_text(path.read_text(encoding="utf-8") + body, encoding="utf-8")
    _assert_error(root, expected)


@pytest.mark.parametrize("option", ("--all", "--page", "--page-size"))
def test_renderer_traversal_flags_are_forbidden(tmp_path: Path, option: str) -> None:
    root = _copy_repo(tmp_path)
    path = root / integration.RUNTIME
    path.write_text(
        path.read_text(encoding="utf-8")
        + f"\n\ndef _renderer_option_mutation(parser):\n    parser.add_argument({option!r})\n",
        encoding="utf-8",
    )
    _assert_error(root, "forbidden renderer options")


@pytest.mark.parametrize(
    ("old", "new", "constant"),
    (
        (
            'ADVISORY_LABEL = "Phrase-list screening advisory"',
            'ADVISORY_LABEL = "Origin classifier"',
            "ADVISORY_LABEL",
        ),
        ("MAX_NODE_WITNESSES = 512", "MAX_NODE_WITNESSES = 513", "MAX_NODE_WITNESSES"),
        (
            "MAX_NODE_COMBINATIONS = 100_000",
            "MAX_NODE_COMBINATIONS = 100_001",
            "MAX_NODE_COMBINATIONS",
        ),
        ("MAX_PARSE_INTERVALS = 4096", "MAX_PARSE_INTERVALS = 4097", "MAX_PARSE_INTERVALS"),
        ("MAX_SEGMENTS = 4096", "MAX_SEGMENTS = 4097", "MAX_SEGMENTS"),
        (
            "MAX_PARSE_WORK_UNITS = 100_000",
            "MAX_PARSE_WORK_UNITS = 100_001",
            "MAX_PARSE_WORK_UNITS",
        ),
        (
            "MAX_RAW_TOKEN_CODEPOINTS = 4096",
            "MAX_RAW_TOKEN_CODEPOINTS = 4097",
            "MAX_RAW_TOKEN_CODEPOINTS",
        ),
        ("MAX_CORPUS_ENTRIES = 512", "MAX_CORPUS_ENTRIES = 513", "MAX_CORPUS_ENTRIES"),
        (
            "MAX_CORPUS_EXISTING_SIGNALS = 8192",
            "MAX_CORPUS_EXISTING_SIGNALS = 8193",
            "MAX_CORPUS_EXISTING_SIGNALS",
        ),
        (
            "MAX_STRUCTURE_DEPTH = 64",
            "MAX_STRUCTURE_DEPTH = 65",
            "MAX_STRUCTURE_DEPTH",
        ),
        (
            "MAX_STRUCTURE_NODES = 200_000",
            "MAX_STRUCTURE_NODES = 200_001",
            "MAX_STRUCTURE_NODES",
        ),
    ),
)
def test_runtime_frozen_constant_drift_fails(
    tmp_path: Path, old: str, new: str, constant: str
) -> None:
    root = _copy_repo(tmp_path)
    _replace(root, integration.RUNTIME, old, new)
    _assert_error(root, f"{constant} must equal")


@pytest.mark.parametrize(
    ("old", "new", "expected"),
    (
        (
            "if len(corpus) > MAX_CORPUS_ENTRIES:",
            "if len(corpus) >= MAX_CORPUS_ENTRIES:",
            "MAX_CORPUS_ENTRIES with the strict N/N+1 guard",
        ),
        (
            "if existing_signal_count > MAX_CORPUS_EXISTING_SIGNALS:",
            "if existing_signal_count >= MAX_CORPUS_EXISTING_SIGNALS:",
            "MAX_CORPUS_EXISTING_SIGNALS with the strict N/N+1 guard",
        ),
    ),
)
def test_corpus_cardinality_boundary_drift_fails(
    tmp_path: Path,
    old: str,
    new: str,
    expected: str,
) -> None:
    root = _copy_repo(tmp_path)
    _replace(root, integration.RUNTIME, old, new)
    _assert_error(root, expected)


def test_raw_token_boundary_must_remain_strict_n_plus_one(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    _replace(
        root,
        integration.RUNTIME,
        "if len(buffer) > MAX_RAW_TOKEN_CODEPOINTS:",
        "if len(buffer) >= MAX_RAW_TOKEN_CODEPOINTS:",
    )
    _assert_error(root, "MAX_RAW_TOKEN_CODEPOINTS with the strict N/N+1 guard")


def test_existing_signal_limit_must_count_the_aggregate(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    _replace(
        root,
        integration.RUNTIME,
        "existing_signal_count = sum(",
        "existing_signal_count = max(",
    )
    _assert_error(root, "existing_signal_count must aggregate every pre-existing")


def test_passport_write_cannot_precede_successful_enrichment(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    _replace(
        root,
        integration.RUNTIME,
        "            document, kind = _load_passport(args.input)\n"
        "            output = enrich_passport(",
        "            document, kind = _load_passport(args.input)\n"
        "            _atomic_write_passport(args.output, document, kind)\n"
        "            output = enrich_passport(",
    )
    _assert_error(root, "write the passport only after enrich_passport returns")


@pytest.mark.parametrize(
    ("old", "new", "expected"),
    (
        (
            "if len(unique) > MAX_NODE_WITNESSES:",
            "if False:  # removed witness guard",
            "_minimal_witnesses must enforce MAX_NODE_WITNESSES",
        ),
        (
            "if len(result) > MAX_NODE_WITNESSES:",
            "if False:  # removed literal witness guard",
            "_literal_witnesses must enforce MAX_NODE_WITNESSES",
        ),
        (
            "if attempts > MAX_NODE_COMBINATIONS:",
            "if False:  # removed combination guard",
            "evaluate_expression must enforce MAX_NODE_COMBINATIONS",
        ),
        (
            "if len(intervals) > MAX_PARSE_INTERVALS:",
            "if False:  # removed interval guard",
            "_append_parse_interval must enforce MAX_PARSE_INTERVALS",
        ),
        (
            "if len(openers) > MAX_PARSE_INTERVALS:",
            "if False:  # removed opaque candidate guard",
            "_append_opaque_opener must enforce MAX_PARSE_INTERVALS",
        ),
        (
            "if len(buffer) > MAX_RAW_TOKEN_CODEPOINTS:",
            "if False:  # removed raw-token guard",
            "tokenize must enforce MAX_RAW_TOKEN_CODEPOINTS",
        ),
        (
            "if len(segments) > MAX_SEGMENTS:",
            "if False:  # removed segment guard",
            "build_own_draft_report must enforce MAX_SEGMENTS",
        ),
        (
            "if nodes_seen > MAX_STRUCTURE_NODES:",
            "if False:  # removed structure-node guard",
            "_reject_nonfinite_recursive must enforce MAX_STRUCTURE_NODES",
        ),
        (
            '"summary_label": ADVISORY_LABEL,',
            '"summary_label": "Phrase-list screening advisory",',
            "build_cited_signal must bind summary_label to ADVISORY_LABEL",
        ),
    ),
)
def test_runtime_limit_and_label_structure_drift_fails(
    tmp_path: Path, old: str, new: str, expected: str
) -> None:
    root = _copy_repo(tmp_path)
    _replace(root, integration.RUNTIME, old, new)
    _assert_error(root, expected)


def test_iterative_structure_depth_guard_cannot_be_removed(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    _replace_nth(
        root,
        integration.RUNTIME,
        "if depth > MAX_STRUCTURE_DEPTH:",
        "if False:  # removed iterative structure-depth guard",
        3,
    )
    _assert_error(
        root,
        "_reject_nonfinite_recursive must enforce MAX_STRUCTURE_DEPTH",
    )


def test_segment_document_retains_its_aggregate_interval_cap(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    _replace_nth(
        root,
        integration.RUNTIME,
        "if len(intervals) > MAX_PARSE_INTERVALS:",
        "if False:  # removed aggregate interval guard",
        2,
    )
    _assert_error(root, "segment_document must enforce MAX_PARSE_INTERVALS")


@pytest.mark.parametrize(
    ("old", "expected"),
    (
        (
            "    _reject_nonfinite_recursive(value, path=label)\n",
            "strict JSON loader must apply the structure guard",
        ),
        (
            '    _reject_nonfinite_recursive(document, path="passport")\n',
            "direct passport enricher must apply the structure guard",
        ),
    ),
)
def test_structure_guard_call_cannot_be_removed(
    tmp_path: Path, old: str, expected: str
) -> None:
    root = _copy_repo(tmp_path)
    _replace(root, integration.RUNTIME, old, "")
    _assert_error(root, expected)


def test_renderer_cap_drift_fails(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    _replace(root, integration.RUNTIME, "MAX_RENDER_PAGE_SIZE = 25", "MAX_RENDER_PAGE_SIZE = 26")
    _assert_error(root, "MAX_RENDER_PAGE_SIZE must equal 25")


def test_renderer_unbounded_slice_fails(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    _replace(
        root,
        integration.RUNTIME,
        "selected = matches[:MAX_RENDER_PAGE_SIZE]",
        "selected = matches[:]",
    )
    _assert_error(root, "renderer must slice matches at the fixed cap")


def test_renderer_must_iterate_the_bounded_selection(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    _replace(
        root,
        integration.RUNTIME,
        "for match in selected:",
        "for match in matches:",
    )
    _assert_error(root, "renderer must iterate only the fixed slice")


@pytest.mark.parametrize(
    ("old", "new", "expected"),
    (
        (
            'reason_code = "DOCUMENT_EMPTY"',
            'reason_code = "DOCUMENT_BLANK"',
            "empty draft must emit DOCUMENT_EMPTY",
        ),
        (
            '            "ABSTRACT_EMPTY",',
            '            "ABSTRACT_BLANK",',
            "empty abstract must emit ABSTRACT_EMPTY",
        ),
    ),
)
def test_runtime_empty_reason_drift_fails(
    tmp_path: Path, old: str, new: str, expected: str
) -> None:
    root = _copy_repo(tmp_path)
    _replace(root, integration.RUNTIME, old, new)
    _assert_error(root, expected)


def test_explicit_timestamp_parameters_are_required(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    _replace(root, integration.RUNTIME, "    checked_at: str,", "    captured_at: str,")
    _assert_error(root, "requires explicit checked_at/recorded_at")


def test_design_claim_ceiling_binding_fails_closed(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    _replace(
        root,
        integration.DESIGN_SPEC,
        "No #654 measurement row may be manufactured",
        "A #654 measurement row may be manufactured",
    )
    _assert_error(root, "missing #660 integration tokens")


@pytest.mark.parametrize(
    "token",
    (
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
    ),
)
def test_design_corpus_cardinality_boundary_is_bound(
    tmp_path: Path,
    token: str,
) -> None:
    root = _copy_repo(tmp_path)
    _replace(root, integration.DESIGN_SPEC, token, "REMOVED_CORPUS_BOUNDARY")
    _assert_error(root, "missing #660 integration tokens")


@pytest.mark.parametrize("token", ("ABSTRACT_EMPTY", "DOCUMENT_EMPTY"))
def test_design_empty_reason_vocabulary_is_bound(tmp_path: Path, token: str) -> None:
    root = _copy_repo(tmp_path)
    _replace(root, integration.DESIGN_SPEC, token, "REMOVED_EMPTY_REASON")
    _assert_error(root, "missing #660 integration tokens")


def test_formatter_neutral_advisory_label_is_bound(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    _replace(
        root,
        integration.FORMATTER_AGENT,
        "neutral **Phrase-list screening advisory**",
        "categorical **Origin classifier**",
    )
    _assert_error(root, "missing #660 integration tokens")


def test_orchestrator_preserves_degraded_artifact_after_exit_one(
    tmp_path: Path,
) -> None:
    root = _copy_repo(tmp_path)
    _replace(
        root,
        integration.PIPELINE_ORCHESTRATOR,
        "schema-valid degraded advisory and then exit 1",
        "degraded output and then exits",
    )
    _assert_error(root, "missing #660 integration tokens")


def test_design_neutral_advisory_label_is_bound(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    _replace(
        root,
        integration.DESIGN_SPEC,
        "category label is the neutral **“Phrase-list screening",
        "category label is the categorical **“Origin classifier",
    )
    _assert_error(root, "missing #660 integration tokens")


def test_consumer_binding_drift_fails(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    _replace(
        root,
        integration.CORPUS_CHECKER,
        "                                    validate_cited_signal_binding(signal, entry)",
        "                                    validate_removed_signal_binding(signal, entry)",
    )
    _assert_error(root, "must call validate_cited_signal_binding exactly once")


def test_runtime_manifest_entry_is_required(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    block = (
        '[[pytest]]\n'
        'id = "660-tortured-phrase-screening"\n'
        'path = "scripts/test_tortured_phrase_screening.py"\n\n'
    )
    _replace(root, integration.CI_MANIFEST, block, "")
    _assert_error(root, "660-tortured-phrase-screening")


def test_integration_manifest_entry_is_required(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    block = (
        '[[pytest]]\n'
        'id = "660-tortured-phrase-integration"\n'
        'path = "scripts/test_check_tortured_phrase_screening_integration.py"\n\n'
    )
    _replace(root, integration.CI_MANIFEST, block, "")
    _assert_error(root, "660-tortured-phrase-integration")


def test_direct_workflow_checker_is_required(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    _replace(
        root,
        integration.WORKFLOW,
        "python3 scripts/check_tortured_phrase_screening_integration.py",
        "python3 scripts/check_bibliographic_integrity_signals.py",
    )
    _assert_error(root, "direct #660 integration checker must run exactly once")


def test_conformance_suite_registry_entry_is_required(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)

    def mutate(registry: dict[str, Any]) -> None:
        registry.pop("tortured_phrase_conformance")

    _rewrite_json(root, integration.SUITE_REGISTRY, mutate)
    _assert_error(root, "tortured_phrase_conformance must map exactly to mechanical_match")


def test_measurement_contract_registry_mirror_is_required(tmp_path: Path) -> None:
    root = _copy_repo(tmp_path)
    _replace(
        root,
        integration.MEASUREMENT_CONTRACT,
        "| `tortured_phrase_conformance` | `mechanical_match` |",
        "| `tortured_phrase_conformance` | `llm_judged` |",
    )
    _assert_error(root, "registry mirror must contain exactly one")


@pytest.mark.parametrize(
    ("old", "new"),
    (
        ("Status: PRE-REGISTERED / NOT RUN", "Status: DRAFT / MAY RUN"),
        (
            "first commit reachable",
            "working-tree state not reachable on the default branch",
        ),
        (
            "use that same 40-hex main-history commit for both",
            "different commits may be used for",
        ),
        ("No retry is permitted", "One retry is permitted"),
        ("synthetic_conformance_test_pass_rate", "contextual_accuracy"),
        ("It uses zero", "It uses two"),
        ("A passing row may say only", "A passing row may broadly claim"),
    ),
)
def test_frozen_measurement_plan_token_drift_fails(
    tmp_path: Path, old: str, new: str
) -> None:
    root = _copy_repo(tmp_path)
    _replace(root, integration.MEASUREMENT_PLAN, old, new)
    _assert_error(root, "frozen plan tokens drifted")


@pytest.mark.parametrize(
    ("old", "new"),
    (
        ("remains `UNMEASURED`", "becomes `MEASURED`"),
        (
            "contextual false-positive/false-negative labels",
            "contextual accuracy labels",
        ),
    ),
)
def test_conformance_readme_claim_ceiling_drift_fails(
    tmp_path: Path, old: str, new: str
) -> None:
    root = _copy_repo(tmp_path)
    _replace(root, integration.CONFORMANCE_README, old, new)
    _assert_error(root, "UNMEASURED/contextual claim ceiling drifted")


def test_scored_heldout_row_is_forbidden_on_implementation_branch(
    tmp_path: Path,
) -> None:
    root = _copy_repo(tmp_path)
    path = root / integration.HELDOUT_ROOT / "tortured_phrase" / "measurement.json"
    path.parent.mkdir(parents=True)
    path.write_text(
        json.dumps(
            {
                "measurement_contract": "heldout-measurement/1.0",
                "surface": "tortured_phrase",
            }
        ),
        encoding="utf-8",
    )
    _assert_error(root, "must remain UNMEASURED")


def test_checker_imports_no_network_model_or_process_modules() -> None:
    source = Path(integration.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = {
        alias.name.split(".", 1)[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    } | {
        node.module.split(".", 1)[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    }
    assert not imports & integration.FORBIDDEN_IMPORT_ROOTS


def test_cli_main_reports_success_and_invocation_error(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _copy_repo(tmp_path)
    assert integration.main(["--root", str(root)]) == 0
    assert "integration: ok" in capsys.readouterr().out
    assert integration.main(["--unknown"]) == 2
