#!/usr/bin/env python3
"""Mutation tests for the static #672 integration guard."""
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

import check_cross_document_consistency_advisory_integration as guard  # noqa: E402


COPIED_FILES = tuple(
    dict.fromkeys(
        (
            *guard.SCHEMA_VERSIONS,
            guard.RUNTIME,
            guard.RUNTIME_TEST,
            *guard.LEGACY_HASHES,
            *guard.REQUIRED_POINTERS,
            guard.CI_MANIFEST,
            guard.WORKFLOW,
        )
    )
)


def _tree(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    for relative in COPIED_FILES:
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO_ROOT / relative, target)
    return root


def _rewrite_json(
    root: Path,
    relative: Path,
    mutation: Callable[[dict[str, Any]], None],
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


def _replace_in_function(
    root: Path,
    function_name: str,
    old: str,
    new: str,
) -> None:
    path = root / guard.RUNTIME
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    function = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == function_name
    )
    segment = ast.get_source_segment(source, function)
    assert segment is not None and old in segment
    start = source.index(segment)
    replacement = segment.replace(old, new, 1)
    path.write_text(
        source[:start] + replacement + source[start + len(segment) :],
        encoding="utf-8",
    )


def _replace_where_present(root: Path, relatives: tuple[Path, ...], old: str, new: str) -> None:
    replacements = 0
    for relative in relatives:
        path = root / relative
        text = path.read_text(encoding="utf-8")
        if old not in text:
            continue
        replacements += text.count(old)
        path.write_text(text.replace(old, new), encoding="utf-8")
    assert replacements


def _assert_error(root: Path, marker: str) -> None:
    errors = guard.run_checks(root)
    assert any(marker in error for error in errors), errors


def test_current_repository_passes_cross_document_integration() -> None:
    assert guard.run_checks(REPO_ROOT) == []


@pytest.mark.parametrize("relative", tuple(guard.LEGACY_HASHES))
def test_frozen_legacy_and_template_identities_are_load_bearing(
    tmp_path: Path, relative: Path
) -> None:
    root = _tree(tmp_path)
    path = root / relative
    path.write_bytes(path.read_bytes() + b"\n# drift\n")
    _assert_error(root, "frozen legacy/template sha256 drifted")


@pytest.mark.parametrize("relative", tuple(guard.NEW_SCHEMA_HASHES))
def test_five_new_schema_exact_identities_are_load_bearing(
    tmp_path: Path, relative: Path
) -> None:
    root = _tree(tmp_path)
    path = root / relative
    path.write_bytes(path.read_bytes() + b" ")
    _assert_error(root, "frozen new schema sha256 drifted")


def test_schema_conditional_branch_loosening_and_substitution_fail(tmp_path: Path) -> None:
    mutations: tuple[tuple[Path, Callable[[dict[str, Any]], None]], ...] = (
        (guard.SIDECAR_SCHEMA, lambda value: value["allOf"][0].update({"then": {}})),
        (guard.EVIDENCE_SCHEMA, lambda value: value["$defs"]["methods_reported_analyses_slots"]["oneOf"].append({})),
        (guard.MANIFEST_SCHEMA, lambda value: value["$defs"]["artifact"]["allOf"].pop()),
        (guard.DRAFT_SCHEMA, lambda value: value["$defs"]["observation"]["allOf"].pop()),
        (guard.ADVISORY_SCHEMA, lambda value: value["$defs"]["final_observation"]["allOf"].pop()),
    )
    for index, (relative, mutation) in enumerate(mutations):
        root = _tree(tmp_path / f"loosen-{index}")
        _rewrite_json(root, relative, mutation)
        _assert_error(root, "frozen new schema sha256 drifted")

    root = _tree(tmp_path / "substitution")
    (root / guard.DRAFT_SCHEMA).write_bytes((root / guard.EVIDENCE_SCHEMA).read_bytes())
    _assert_error(root, "frozen new schema sha256 drifted")


def test_schema_external_ref_allowlist_rejects_claimintent_or_legacy_carrier(
    tmp_path: Path,
) -> None:
    for index, ref in enumerate(
        (
            "../passport/claim-intent-manifest.schema.json",
            "../passport/audit_artifact_entry.schema.json",
        )
    ):
        root = _tree(tmp_path / str(index))

        def mutate(schema: dict[str, Any], ref: str = ref) -> None:
            schema["properties"]["legacy_input"] = {"$ref": ref}

        _rewrite_json(root, guard.DRAFT_SCHEMA, mutate)
        _assert_error(root, "schema external $ref allowlist drifted")


@pytest.mark.parametrize(
    ("relative", "field", "replacement", "marker"),
    (
        (guard.SIDECAR_SCHEMA, "schema_version", "preregistration-artifact/2.0", "schema_version"),
        (guard.EVIDENCE_SCHEMA, "schema_version", "evidence-row/1.1", "schema_version"),
        (guard.EVIDENCE_SCHEMA, "surface", "phase_e_claim_verification", "surface drifted"),
        (guard.MANIFEST_SCHEMA, "schema_version", "cross-document-source-manifest/2.0", "schema_version"),
        (guard.DRAFT_SCHEMA, "layer", "DETERMINISTIC", "runtime constant"),
        (guard.ADVISORY_SCHEMA, "layer", "DETERMINISTIC", "layer must equal"),
        (guard.ADVISORY_SCHEMA, "evaluation_status", "MEASURED", "evaluation_status"),
    ),
)
def test_contract_identity_drift_fails(
    tmp_path: Path,
    relative: Path,
    field: str,
    replacement: str,
    marker: str,
) -> None:
    root = _tree(tmp_path)

    def mutate(schema: dict[str, Any]) -> None:
        schema["properties"][field]["const"] = replacement

    _rewrite_json(root, relative, mutate)
    # Draft layer is deliberately enforced by the runtime/static parity even
    # when the schema-specific message differs.
    errors = guard.run_checks(root)
    assert errors
    if relative != guard.DRAFT_SCHEMA:
        assert any(marker in error for error in errors), errors


@pytest.mark.parametrize(
    ("relative", "definition"),
    (
        (guard.SIDECAR_SCHEMA, None),
        (guard.EVIDENCE_SCHEMA, "checked_scope"),
        (guard.MANIFEST_SCHEMA, "artifact"),
        (guard.DRAFT_SCHEMA, "observation"),
        (guard.ADVISORY_SCHEMA, "input_binding"),
    ),
)
def test_recursive_closedness_is_load_bearing(
    tmp_path: Path, relative: Path, definition: str | None
) -> None:
    root = _tree(tmp_path)

    def mutate(schema: dict[str, Any]) -> None:
        target = schema if definition is None else schema["$defs"][definition]
        target.pop("additionalProperties")

    _rewrite_json(root, relative, mutate)
    _assert_error(root, "recursively closed")


def test_sidecar_status_projection_and_size_ceiling_drift_fail(tmp_path: Path) -> None:
    root = _tree(tmp_path)

    def mutate(schema: dict[str, Any]) -> None:
        schema["properties"]["status"]["enum"][0] = "available"
        schema["properties"]["source_artifact_size_bytes"]["maximum"] = 67108865

    _rewrite_json(root, guard.SIDECAR_SCHEMA, mutate)
    errors = guard.run_checks(root)
    assert any("status mapping" in error for error in errors), errors
    assert any("64 MiB" in error for error in errors), errors


def test_manifest_exact_two_artifact_authority_is_load_bearing(tmp_path: Path) -> None:
    root = _tree(tmp_path)

    def mutate(schema: dict[str, Any]) -> None:
        schema["properties"]["artifacts"]["maxItems"] = 3
        schema["properties"]["artifacts"]["allOf"].pop()
        schema["required"].remove("accepted_draft_sha256")

    _rewrite_json(root, guard.MANIFEST_SCHEMA, mutate)
    errors = guard.run_checks(root)
    assert any("exactly two" in error for error in errors), errors
    assert any("one-manuscript/one-preregistration" in error for error in errors), errors
    assert any("accepted-draft binding" in error for error in errors), errors


@pytest.mark.parametrize(
    "mutation",
    ("pair", "role", "cardinality", "state", "checked_scope", "cache"),
)
def test_evidence_row_bilateral_and_three_witness_matrix_is_load_bearing(
    tmp_path: Path, mutation: str
) -> None:
    root = _tree(tmp_path)

    def mutate(schema: dict[str, Any]) -> None:
        if mutation == "pair":
            schema["$defs"]["pair_kind"]["enum"][0] = "consent_protocol"
        elif mutation == "role":
            schema["$defs"]["manuscript_preregistration_slots"]["prefixItems"][2]["$ref"] = "#/$defs/slot_results"
        elif mutation == "cardinality":
            schema["$defs"]["manuscript_preregistration_slots"]["minItems"] = 2
        elif mutation == "state":
            schema["$defs"]["evidence_slot"]["properties"]["evidence_state"]["enum"].append("consistent")
        elif mutation == "checked_scope":
            schema["$defs"]["checked_scope"]["required"].remove("scope_sha256")
        else:
            schema["$defs"]["cache"]["properties"]["status"]["const"] = "hit"

    _rewrite_json(root, guard.EVIDENCE_SCHEMA, mutate)
    expected = {
        "pair": "pair roster",
        "role": "ordered roles",
        "cardinality": "slot cardinality",
        "state": "state vocabulary",
        "checked_scope": "checked_scope binding",
        "cache": "cache must remain",
    }[mutation]
    _assert_error(root, expected)


@pytest.mark.parametrize(
    "mutation",
    ("outcome", "finding", "negative", "roster", "ceiling", "conditional", "prereg_slots"),
)
def test_draft_semantic_input_matrix_is_load_bearing(
    tmp_path: Path, mutation: str
) -> None:
    root = _tree(tmp_path)

    def mutate(schema: dict[str, Any]) -> None:
        if mutation == "outcome":
            schema["$defs"]["outcome"]["enum"][0] = "PASS"
        elif mutation == "finding":
            schema["$defs"]["finding_type"]["enum"].append("consent_protocol")
        elif mutation == "negative":
            schema["$defs"]["negative_basis"]["enum"][0] = "consistent"
        elif mutation == "roster":
            schema["$defs"]["pair_kind"]["enum"].pop()
        elif mutation == "ceiling":
            schema["properties"]["observations"]["maxItems"] = 4097
        elif mutation == "conditional":
            schema["$defs"]["observation"]["allOf"] = schema["$defs"]["observation"]["allOf"][:3]
        else:
            schema["$defs"]["manuscript_preregistration_slots"]["maxItems"] = 2

    _rewrite_json(root, guard.DRAFT_SCHEMA, mutate)
    expected = {
        "outcome": "outcome vocabulary",
        "finding": "finding-type vocabulary",
        "negative": "negative-basis vocabulary",
        "roster": "pair roster",
        "ceiling": "observation ceiling",
        "conditional": "conditional matrix",
        "prereg_slots": "three-witness",
    }[mutation]
    _assert_error(root, expected)


@pytest.mark.parametrize(
    "mutation",
    ("pair_count", "pair_order", "binding", "boundary", "row_ref"),
)
def test_final_carrier_roster_binding_and_noninterference_are_load_bearing(
    tmp_path: Path, mutation: str
) -> None:
    root = _tree(tmp_path)

    def mutate(schema: dict[str, Any]) -> None:
        if mutation == "pair_count":
            schema["properties"]["pair_results"]["maxItems"] = 5
        elif mutation == "pair_order":
            items = schema["properties"]["pair_results"]["prefixItems"]
            items[0], items[1] = items[1], items[0]
        elif mutation == "binding":
            schema["$defs"]["input_binding"]["required"].remove("accepted_draft_sha256")
        elif mutation == "boundary":
            schema["$defs"]["boundary"]["properties"]["stage_5_routing_unchanged"] = {"type": "boolean"}
        else:
            schema["$defs"]["final_observation"]["properties"]["evidence_row"]["$ref"] = "../evidence/evidence_row_v1_1.schema.json"

    _rewrite_json(root, guard.ADVISORY_SCHEMA, mutate)
    expected = {
        "pair_count": "roster cardinality",
        "pair_order": "canonical pair ordering",
        "binding": "source/input binding",
        "boundary": "noninterference boundary",
        "row_ref": "embed evidence-row/1.2",
    }[mutation]
    _assert_error(root, expected)


def test_parallel_score_or_consent_contract_fields_fail(tmp_path: Path) -> None:
    for index, field in enumerate(("score", "consent_protocol")):
        root = _tree(tmp_path / str(index))

        def mutate(schema: dict[str, Any], field: str = field) -> None:
            schema["properties"][field] = {"type": "string"}

        _rewrite_json(root, guard.ADVISORY_SCHEMA, mutate)
        _assert_error(root, "forbidden determination fields")


@pytest.mark.parametrize(
    ("old", "new", "marker"),
    (
        ("MAX_PAGE_SIZE = 25", "MAX_PAGE_SIZE = 26", "MAX_PAGE_SIZE"),
        ('"abstract_results": ("abstract", "results"),', '"abstract_results": ("results", "abstract"),', "PAIR_ROLES"),
        ('"RESOURCE_LIMIT",', '"UNBOUNDED_ERROR",', "DIAGNOSTIC_CODES"),
        ('TEMPLATE_SHA256 = "40054e26', 'TEMPLATE_SHA256 = "50054e26', "template digest"),
        ('"manuscript_preregistration": (', '"consent_protocol": (', "PAIR_ROLES"),
    ),
)
def test_runtime_structural_constants_are_load_bearing(
    tmp_path: Path, old: str, new: str, marker: str
) -> None:
    root = _tree(tmp_path)
    _replace(root, guard.RUNTIME, old, new)
    _assert_error(root, marker)


@pytest.mark.parametrize(
    "statement",
    (
        "import requests\n",
        "import subprocess\n",
        "import socket\n",
        "from openai import OpenAI\n",
        "import urllib.request\n",
    ),
)
def test_runtime_model_network_or_process_import_fails(
    tmp_path: Path, statement: str
) -> None:
    root = _tree(tmp_path)
    path = root / guard.RUNTIME
    path.write_text(statement + path.read_text(encoding="utf-8"), encoding="utf-8")
    _assert_error(root, "forbidden model/network/process import")


@pytest.mark.parametrize(
    ("snippet", "marker"),
    (
        ("\ndef bad_clock():\n    return dt.datetime.now()\n", "clock call"),
        ("\ndef bad_scan(path):\n    return path.rglob('*')\n", "ambient directory scan"),
        ("\ndef bad_process():\n    return os.system('true')\n", "process/clock call"),
    ),
)
def test_runtime_clock_scan_or_process_call_fails(
    tmp_path: Path, snippet: str, marker: str
) -> None:
    root = _tree(tmp_path)
    path = root / guard.RUNTIME
    path.write_text(path.read_text(encoding="utf-8") + snippet, encoding="utf-8")
    _assert_error(root, marker)


def test_pure_renderer_reachable_io_fails(tmp_path: Path) -> None:
    root = _tree(tmp_path)
    _replace(
        root,
        guard.RUNTIME,
        "def render_advisory(\n"
        "    advisory: Mapping[str, Any], *, page: int = 1, page_size: int = 25\n"
        ") -> str:\n",
        "def render_advisory(\n"
        "    advisory: Mapping[str, Any], *, page: int = 1, page_size: int = 25\n"
        ") -> str:\n"
        "    Path('ambient').read_text()\n",
    )
    _assert_error(root, "pure renderer reaches forbidden I/O")


@pytest.mark.parametrize(
    ("old", "new"),
    (
        ('add_parser("build-preregistration-artifact"', 'add_parser("build-sidecar"'),
        ('for name in ("finalize", "validate", "render")', 'for name in ("finalize", "validate")'),
        ('add_argument("--page-size"', 'add_argument("--unbounded-page-size"'),
        ('print(f"ADVISORY_UNAVAILABLE:{exc.code}"', 'print(str(exc)'),
    ),
)
def test_cli_and_bounded_diagnostic_markers_are_load_bearing(
    tmp_path: Path, old: str, new: str
) -> None:
    root = _tree(tmp_path)
    _replace(root, guard.RUNTIME, old, new)
    _assert_error(root, "CLI/restricted diagnostic marker missing")


def test_renderer_all_switch_and_runtime_cross_consumer_fail(tmp_path: Path) -> None:
    payloads = (
        ("\n# --all\n", "must not expose --all"),
        ("\ndef consume(claim_intent):\n    return claim_intent\n", "structured nonconsumer"),
        ("\nlegacy_runner = 'scripts/run_codex_audit.sh'\n", "structured nonconsumer"),
        ("\nlegacy_carrier = 'audit_artifact_entry'\n", "structured nonconsumer"),
        ("\nlegacy_map = {'PASS': 'NO_LISTED_INCONSISTENCY_LOCATED'}\n", "structured nonconsumer"),
        ("\ntortured_phrase_input = None\n", "structured nonconsumer"),
    )
    for index, (payload, marker) in enumerate(payloads):
        root = _tree(tmp_path / str(index))
        path = root / guard.RUNTIME
        path.write_text(path.read_text(encoding="utf-8") + payload, encoding="utf-8")
        _assert_error(root, marker)


def test_runtime_import_and_parser_input_allowlists_reject_new_consumers(
    tmp_path: Path,
) -> None:
    root = _tree(tmp_path / "import")
    path = root / guard.RUNTIME
    path.write_text("import claim_intent\n" + path.read_text(encoding="utf-8"), encoding="utf-8")
    _assert_error(root, "runtime import allowlist drifted")

    root = _tree(tmp_path / "parser")
    _replace(
        root,
        guard.RUNTIME,
        'sidecar.add_argument("--status"',
        'sidecar.add_argument("--claim-intent")\n    sidecar.add_argument("--status"',
    )
    _assert_error(root, "runtime parser input allowlist drifted")


@pytest.mark.parametrize(
    ("old", "new"),
    (
        ("flags |= os.O_NONBLOCK", "flags |= 0"),
        ("if not stat.S_ISREG(metadata.st_mode):", "if False:"),
        ("object_pairs_hook=object_pairs", "object_pairs_hook=dict"),
        ("parse_float=reject_float", "parse_float=float"),
        (
            "parser = _ClosedArgumentParser(description=__doc__, allow_abbrev=False)",
            "parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)",
        ),
        (
            "def _strict_accepted_draft(raw: bytes) -> str:",
            "def _unchecked_accepted_draft(raw: bytes) -> str:",
        ),
        ("if not text.strip():", "if False:"),
        (
            'unreadable_code="SOURCE_BINDING_INVALID"',
            'unreadable_code="NAMED_INPUT_UNREADABLE"',
        ),
        (
            'locator = slot["document_locator"]',
            'locator = {"kind": "document", "value": "hidden"}',
        ),
    ),
)
def test_hardened_runtime_structure_tokens_are_load_bearing(
    tmp_path: Path, old: str, new: str
) -> None:
    root = _tree(tmp_path)
    _replace(root, guard.RUNTIME, old, new)
    _assert_error(root, "runtime hardened structure drifted")


@pytest.mark.parametrize(
    ("function_name", "old", "new"),
    (
        (
            "render_advisory",
            guard.RENDERER_CLAIM_CEILING_SENTENCE,
            "NO LISTED INCONSISTENCY LOCATED — clean document.",
        ),
        (
            "render_advisory",
            "result = f\"{observation['outcome']} — {observation['negative_basis']}\"",
            "result = observation['negative_basis']",
        ),
        (
            "build_preregistration_artifact",
            "if not text.strip():",
            "if False:",
        ),
        ("_precheck_depth", "if depth > MAX_JSON_DEPTH:", "if False:"),
        ("_count_nodes", "if count > MAX_JSON_NODES:", "if False:"),
        (
            "_strict_json_bytes",
            "_precheck_depth(text, code=code, path=path)",
            "_ = text",
        ),
        (
            "_strict_json_bytes",
            "_count_nodes(value, code=code, path=path)",
            "_ = value",
        ),
        ("_array", "len(value) > maximum", "False"),
        ("paginate", "page_size > MAX_PAGE_SIZE", "False"),
        (
            "_prepare_inputs",
            "if total > MAX_TOTAL_SOURCE_BYTES:",
            "if False:",
        ),
        (
            "finalize_advisory",
            "if len(_canonical_bytes(report)) > MAX_FINAL_BYTES:",
            "if False:",
        ),
    ),
)
def test_function_scoped_resource_and_renderer_markers_are_load_bearing(
    tmp_path: Path,
    function_name: str,
    old: str,
    new: str,
) -> None:
    root = _tree(tmp_path)
    _replace_in_function(root, function_name, old, new)
    _assert_error(root, "runtime function-scoped hardened structure drifted")


def test_legal_documented_nonconsumer_mentions_are_not_false_positives(
    tmp_path: Path,
) -> None:
    root = _tree(tmp_path)
    path = root / guard.PROTOCOL
    path.write_text(
        path.read_text(encoding="utf-8")
        + "\n\n#672 does not consume ClaimIntent, audit_artifact_entry, P1/P2/P3, or PASS.\n",
        encoding="utf-8",
    )
    assert guard.run_checks(root) == []


@pytest.mark.parametrize("relative", tuple(guard.REQUIRED_POINTERS))
def test_every_consumer_pointer_is_load_bearing(tmp_path: Path, relative: Path) -> None:
    root = _tree(tmp_path)
    marker = guard.REQUIRED_POINTERS[relative][0]
    path = root / relative
    text = path.read_text(encoding="utf-8")
    assert marker in text
    path.write_text(text.replace(marker, "REMOVED-672-POINTER"), encoding="utf-8")
    _assert_error(root, "required #672 pointers missing")


def test_research_architect_mirror_is_byte_exact(tmp_path: Path) -> None:
    root = _tree(tmp_path)
    path = root / guard.ARCHITECT_MIRROR
    path.write_text(path.read_text(encoding="utf-8") + "\nmirror drift\n", encoding="utf-8")
    _assert_error(root, "research architect mirror drifted")


def test_660_672_machine_join_and_order_are_load_bearing(tmp_path: Path) -> None:
    pipeline = (
        guard.PIPELINE_SKILL,
        guard.PIPELINE_ORCHESTRATOR,
        guard.INTEGRITY_PROTOCOL,
        guard.STATE_MACHINE,
    )
    root = _tree(tmp_path / "join")
    _replace_where_present(
        root,
        pipeline,
        "input_binding.artifact.artifact_id",
        "input_binding.artifact.unbound_id",
    )
    _assert_error(root, "exact accepted-draft ID/SHA machine join")

    root = _tree(tmp_path / "order")
    _replace_where_present(root, pipeline, "#660 first and #672 second", "#672 first and #660 second")
    _assert_error(root, "order, distinct failure, nonblocking, or stale")


def test_unmeasured_heldout_rejects_measurement_or_judge_artifact(tmp_path: Path) -> None:
    for index, name in enumerate(("measurement-2099.json", "scores.csv", "accuracy.md")):
        root = _tree(tmp_path / str(index))
        path = root / guard.HELDOUT_ROOT / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("fabricated", encoding="utf-8")
        _assert_error(root, "only canonical README.md is allowed")


def test_unmeasured_heldout_rejects_extra_directory_and_symlink(tmp_path: Path) -> None:
    root = _tree(tmp_path / "directory")
    (root / guard.HELDOUT_ROOT / "runs").mkdir()
    _assert_error(root, "only canonical README.md is allowed")

    root = _tree(tmp_path / "symlink")
    (root / guard.HELDOUT_ROOT / "README-link.md").symlink_to("README.md")
    _assert_error(root, "only canonical README.md is allowed")


@pytest.mark.parametrize(
    "claim",
    (
        "#672 improves semantic accuracy.",
        "#672 demonstrates efficacy.",
        "#672 increases inconsistency coverage improvement.",
        "#672 certifies a clean document.",
        "#672 proves cross-document agreement.",
    ),
)
def test_affirmative_semantic_claim_ceiling_is_load_bearing(
    tmp_path: Path, claim: str
) -> None:
    root = _tree(tmp_path)
    path = root / guard.PROTOCOL
    path.write_text(path.read_text(encoding="utf-8") + f"\n\n{claim}\n", encoding="utf-8")
    _assert_error(root, "affirmative #672 accuracy/efficacy/coverage/clean/agreement claim")


def test_ci_manifest_and_direct_workflow_guard_are_load_bearing(tmp_path: Path) -> None:
    root = _tree(tmp_path / "manifest")
    _replace(
        root,
        guard.CI_MANIFEST,
        "672-cross-document-consistency-integration",
        "672-integration-removed",
    )
    _assert_error(root, "CI manifest missing #672 marker")

    root = _tree(tmp_path / "workflow")
    _replace(
        root,
        guard.WORKFLOW,
        "check_cross_document_consistency_advisory_integration.py",
        "removed_cross_document_guard.py",
    )
    _assert_error(root, "workflow missing direct #672 integration guard")


@pytest.mark.parametrize(
    "payload",
    ('{"$schema":"a","$schema":"b"}', '{"value":NaN}'),
)
def test_duplicate_or_nonfinite_schema_json_fails_closed(
    tmp_path: Path, payload: str
) -> None:
    root = _tree(tmp_path)
    (root / guard.SIDECAR_SCHEMA).write_text(payload, encoding="utf-8")
    _assert_error(root, "schema load/check failed")
