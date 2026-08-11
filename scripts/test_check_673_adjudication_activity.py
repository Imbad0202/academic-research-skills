#!/usr/bin/env python3
"""Hermetic mutation tests for the static #673 integration guard."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from scripts import check_673_adjudication_activity as guard


def _base_schema(version: str) -> dict[str, object]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "schema_version": {"const": version},
        },
        "$defs": {
            "pipeline_stage": {"enum": list(guard.STAGES)},
        },
    }


def _schemas() -> tuple[dict[str, object], dict[str, object]]:
    input_schema = _base_schema("adjudication-activity-input/1.0")
    store_schema = _base_schema("adjudication-activity-store/1.0")
    store_schema["$defs"].update(  # type: ignore[union-attr]
        {
            "source_receipt": {
                "type": "object",
                "properties": {
                    "artifact_sha256s": {
                        "type": "array",
                        "items": {"type": "string"},
                    }
                },
            },
            "run_record": {
                "type": "object",
                "properties": {"sealed": {"const": True}},
            },
        }
    )
    return input_schema, store_schema


def _runtime() -> str:
    return f'''
import argparse

LIMITATION = {guard.LIMITATION_SENTENCE!r}
ADVISORY = {guard.ADVISORY_SENTENCE!r}
COVERAGE = {guard.COVERAGE_LINE!r}
AUTHORITY = "run_id adjudication_activity_sources sealed"
PENDING_PROJECTION = "pending_adjudication_activity_bindings"

def seal_terminal_inventory(state_path, artifact_root, pending_bindings):
    return state_path, artifact_root, pending_bindings

def _validate_manifest_authority(manifest, root):
    state = load_state(root)
    inventory = state.get("adjudication_activity_sources")
    if inventory != manifest["sources"]:
        raise ValueError("authority mismatch")

def _cmd_build(args):
    return args.state, args.artifact_root, args.store_id, args.output

def parser():
    root = argparse.ArgumentParser()
    subs = root.add_subparsers()
    init = subs.add_parser("init-store")
    build = subs.add_parser("build-input")
    append = subs.add_parser("append-run")
    render = subs.add_parser("render")
    validate = subs.add_parser("validate")
    delete_runs = subs.add_parser("delete-runs")
    delete_store = subs.add_parser("delete-store")
    build.add_argument("--state")
    build.add_argument("--artifact-root")
    build.add_argument("--store-id")
    build.add_argument("--output")
    return root
'''


def _wiring() -> dict[Path, str]:
    return {
        guard.STATE_TRACKER: (
            "Stable run_id. pending_adjudication_activity_bindings are producer-only. "
            "The exact five adjudication_activity_sources rows are sealed."
        ),
        guard.ORCHESTRATOR: (
            "Make the terminal transition durable first; the already terminal "
            "outcome is preserved. In post-terminal advisory handling call "
            "seal_terminal_inventory, then build-input, append-run, and optionally "
            "render as best-effort work. The exact run_id plus sealed "
            "adjudication_activity_sources is build-input authority."
        ),
        guard.PIPELINE_SKILL: "post-terminal best-effort advisory append-run",
        guard.STATE_MACHINE: "terminal state transition is durable before post-terminal work",
        guard.PROCESS_SUMMARY: (
            "The adjudication activity store never enters the Process Record. "
            "post-terminal best-effort."
        ),
        guard.COMPLIANCE: (
            "After the qualifying action, best-effort write the "
            "compliance_override_action_receipt."
        ),
        guard.HANDOFFS: (
            "Adjudication activity never enters a Material Passport or handoff."
        ),
    }


def test_synthetic_contracts_pass() -> None:
    input_schema, store_schema = _schemas()
    assert guard.check_schema_contracts(input_schema, store_schema) == []
    assert guard.check_runtime_text(_runtime()) == []
    assert guard.check_wiring_texts(_wiring()) == []


@pytest.mark.parametrize(
    "exact",
    [guard.LIMITATION_SENTENCE, guard.ADVISORY_SENTENCE, guard.COVERAGE_LINE],
)
def test_frozen_exact_renderer_language_is_load_bearing(exact: str) -> None:
    spec = "\n".join(
        [guard.LIMITATION_SENTENCE, guard.ADVISORY_SENTENCE, guard.COVERAGE_LINE]
    )
    assert guard.check_spec_text(spec) == []
    assert any(
        "missing exact renderer text" in error
        for error in guard.check_spec_text(spec.replace(exact, "paraphrased", 1))
    )


@pytest.mark.parametrize("retired", ["source_stage", "pipeline_stage_0"])
def test_retired_stage_tokens_are_rejected_across_text_surfaces(retired: str) -> None:
    assert guard.check_retired_tokens(Path("surface.md"), "clean") == []
    assert any(
        retired in error
        for error in guard.check_retired_tokens(
            Path("surface.md"), f"reintroduced {retired}"
        )
    )


@pytest.mark.parametrize("schema_name", ["input", "store"])
def test_full_stage_enum_is_load_bearing(schema_name: str) -> None:
    input_schema, store_schema = _schemas()
    target = input_schema if schema_name == "input" else store_schema
    target["$defs"]["pipeline_stage"]["enum"].append("pipeline_stage_0")  # type: ignore[index,union-attr]
    errors = guard.check_schema_contracts(input_schema, store_schema)
    assert any("full Stage 1..6 enum drifted" in error for error in errors)
    assert any("pipeline_stage_0" in error for error in errors)


def test_retired_source_stage_is_rejected() -> None:
    input_schema, store_schema = _schemas()
    input_schema["properties"]["source_stage"] = {"type": "string"}  # type: ignore[index]
    assert any(
        "source_stage" in error
        for error in guard.check_schema_contracts(input_schema, store_schema)
    )


@pytest.mark.parametrize(
    "field",
    ["events", "adjudication_count", "overturn", "rate", "score", "threshold"],
)
def test_caller_derived_input_fields_are_rejected(field: str) -> None:
    input_schema, store_schema = _schemas()
    input_schema["properties"][field] = {"type": "integer"}  # type: ignore[index]
    assert any(
        "caller-derived fields" in error
        for error in guard.check_schema_contracts(input_schema, store_schema)
    )


def test_store_artifact_hashes_may_repeat() -> None:
    input_schema, store_schema = _schemas()
    store_schema["$defs"]["source_receipt"]["properties"]["artifact_sha256s"][  # type: ignore[index]
        "uniqueItems"
    ] = True
    assert any(
        "legitimate repeated hashes" in error
        for error in guard.check_schema_contracts(input_schema, store_schema)
    )


@pytest.mark.parametrize(
    ("old", "new", "expected"),
    [
        ("build.add_argument(\"--output\")", "build.add_argument(\"--source-sha256\")", "build-input"),
        ("subs.add_parser(\"render\")", "subs.add_parser(\"judge\")", "CLI command surface"),
        ("import argparse", "import argparse\nimport requests", "forbidden model/network"),
        ("return state_path, artifact_root, pending_bindings", "return artifact_root.rglob('*')", "ambient scan"),
        (guard.COVERAGE_LINE, "Coverage: available runs shown.", "exact renderer text"),
    ],
)
def test_runtime_mutations_fail(old: str, new: str, expected: str) -> None:
    source = _runtime()
    assert old in source
    errors = guard.check_runtime_text(source.replace(old, new, 1))
    assert any(expected in error for error in errors)


def test_seal_api_requires_three_explicit_inputs() -> None:
    source = _runtime().replace(
        "def seal_terminal_inventory(state_path, artifact_root, pending_bindings):",
        "def seal_terminal_inventory(state_path, artifact_root, pending_bindings=None):",
    )
    assert any("must require exactly" in error for error in guard.check_runtime_text(source))


@pytest.mark.parametrize(
    ("old", "new", "expected"),
    [
        (
            "def _validate_manifest_authority(manifest, root):",
            "def _validate_untrusted_manifest(manifest, root):",
            "missing _validate_manifest_authority",
        ),
        (
            'state.get("adjudication_activity_sources")',
            'state.get("pending_adjudication_activity_bindings")',
            "does not read state adjudication_activity_sources",
        ),
        (
            'inventory != manifest["sources"]',
            'inventory[:4] != manifest["sources"][:4]',
            "does not exact-compare sealed inventory",
        ),
        (
            "return args.state, args.artifact_root, args.store_id, args.output",
            "return args.state, args.source_sha256, args.store_id, args.output",
            "reads caller source/hash arguments",
        ),
        (
            "return args.state, args.artifact_root, args.store_id, args.output",
            'return args.state, getattr(args, "source_sha256"), args.store_id, args.output',
            "reads caller source/hash arguments",
        ),
    ],
)
def test_authority_ast_mutations_fail(old: str, new: str, expected: str) -> None:
    source = _runtime()
    assert old in source
    errors = guard.check_runtime_text(source.replace(old, new, 1))
    assert any(expected in error for error in errors)


@pytest.mark.parametrize(
    ("path", "old", "new", "expected"),
    [
        (
            guard.STATE_TRACKER,
            "The exact five adjudication_activity_sources rows are sealed.",
            "Sources may be inferred later.",
            "sealed five-row authority",
        ),
        (
            guard.ORCHESTRATOR,
            "Make the terminal transition durable first;",
            "Maybe make the transition later;",
            "terminal-first order",
        ),
        (
            guard.COMPLIANCE,
            "After the qualifying action, best-effort",
            "Before deciding the action, synchronously",
            "post-action best-effort",
        ),
    ],
)
def test_wiring_mutations_fail(
    path: Path, old: str, new: str, expected: str
) -> None:
    texts = deepcopy(_wiring())
    assert old in texts[path]
    texts[path] = texts[path].replace(old, new, 1)
    assert any(expected in error for error in guard.check_wiring_texts(texts))


@pytest.mark.parametrize(
    "consumer",
    [
        "Gate input: adjudication_activity_store",
        "Verdict reads adjudication_count",
        "Model prompt consumes adjudication activity",
        "Checkpoint selector loads overturn_count",
        "Process Record input includes activity store",
    ],
)
def test_affirmative_consumers_are_rejected(consumer: str) -> None:
    errors = guard.check_non_consumer_text(Path("synthetic.md"), consumer)
    assert errors and "affirmative activity consumer" in errors[0]


def test_explicit_non_consumer_statement_is_allowed() -> None:
    text = "The adjudication activity store never enters a gate, verdict, or model prompt."
    assert guard.check_non_consumer_text(Path("synthetic.md"), text) == []


def test_affirmative_consumer_cannot_hide_after_a_prohibition() -> None:
    text = (
        "The adjudication activity store never enters a gate. "
        "The model prompt consumes adjudication activity."
    )
    errors = guard.check_non_consumer_text(Path("synthetic.md"), text)
    assert len(errors) == 1
    assert "model prompt consumes" in errors[0].lower()


@pytest.mark.parametrize(
    "text",
    [
        "Adjudication activity is not optional; the activity store gates the verdict.",
        "The gate does not ignore the activity store and consumes adjudication_count.",
    ],
)
def test_clause_local_negation_cannot_hide_consumer(text: str) -> None:
    errors = guard.check_non_consumer_text(Path("synthetic.md"), text)
    assert errors and "affirmative activity consumer" in errors[0]


def test_user_may_read_renderer_output_is_allowed() -> None:
    text = "The user may read the adjudication activity renderer output."
    assert guard.check_non_consumer_text(Path("synthetic.md"), text) == []


@pytest.mark.parametrize(
    "payload",
    [
        "from scripts.adjudication_activity import render_store\n",
        "import scripts.adjudication_activity\n",
        "adjudication_count = 1\n",
    ],
)
def test_non_whitelisted_production_python_consumer_fails(payload: str) -> None:
    errors = guard.check_execution_surface(Path("scripts/hidden_consumer.py"), payload)
    assert errors and "non-whitelisted production Python" in errors[0]


def test_exact_python_owner_whitelist_is_allowed() -> None:
    for path in guard.PYTHON_EXECUTION_WHITELIST:
        assert guard.check_execution_surface(path, "adjudication_activity") == []


def test_shell_or_workflow_cannot_execute_activity_runtime() -> None:
    errors = guard.check_execution_surface(
        Path("scripts/hidden.sh"), "python3 scripts/adjudication_activity.py render"
    )
    assert any("invokes/imports activity runtime" in error for error in errors)


def test_workflow_allows_only_direct_guard_step() -> None:
    path = Path(".github/workflows/spec-consistency.yml")
    allowed = (
        "- name: Check adjudication-activity advisory integration (#673)\n"
        "  run: python3 scripts/check_673_adjudication_activity.py\n"
    )
    assert guard.check_execution_surface(path, allowed) == []
