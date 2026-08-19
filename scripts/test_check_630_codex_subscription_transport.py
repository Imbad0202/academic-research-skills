"""Mutation tests for the #630 integration guard."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


REPO = Path(__file__).resolve().parent.parent
GUARD_PATH = REPO / "scripts" / "check_630_codex_subscription_transport.py"


def _load_guard():
    spec = importlib.util.spec_from_file_location("guard_630", GUARD_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _mutated_file(tmp_path: Path, source: Path, old: str, new: str) -> Path:
    original = source.read_text(encoding="utf-8")
    mutated = original.replace(old, new, 1)
    assert mutated != original, f"mutation was a no-op: {old!r}"
    target = tmp_path / source.name
    target.write_text(mutated, encoding="utf-8")
    return target


def test_guard_passes_real_tree() -> None:
    assert _load_guard().check_all() == []


@pytest.mark.parametrize(
    "name,old,new,expected",
    [
        ("open-root", '"additionalProperties": false', '"additionalProperties": true', "not closed"),
        ("prompt-field", '"citation_context": {', '"prompt": {', "four-field"),
        ("wrong-version", "ars-codex-citation-request/1.0", "ars-codex-citation-request/2.0", "version"),
    ],
)
def test_schema_mutations_fail(tmp_path: Path, monkeypatch, name, old, new, expected) -> None:
    del name
    guard = _load_guard()
    mutated = _mutated_file(tmp_path, guard.REQUEST_SCHEMA, old, new)
    monkeypatch.setattr(guard, "REQUEST_SCHEMA", mutated)
    assert any(expected in error for error in guard.check_schemas())


def test_source_binding_mutation_fails(tmp_path: Path, monkeypatch) -> None:
    guard = _load_guard()
    data = json.loads(guard.RECEIPT_SCHEMA.read_text(encoding="utf-8"))
    data["$defs"]["source_binding"]["required"].remove("search_result_digest")
    target = tmp_path / "receipt.json"
    target.write_text(json.dumps(data), encoding="utf-8")
    monkeypatch.setattr(guard, "RECEIPT_SCHEMA", target)
    assert any("source binding" in error for error in guard.check_schemas())


def test_receipt_cross_field_condition_mutation_fails(tmp_path: Path, monkeypatch) -> None:
    guard = _load_guard()
    data = json.loads(guard.RECEIPT_SCHEMA.read_text(encoding="utf-8"))
    data["allOf"] = []
    target = tmp_path / "receipt.json"
    target.write_text(json.dumps(data), encoding="utf-8")
    monkeypatch.setattr(guard, "RECEIPT_SCHEMA", target)
    assert any("cross-field conditions" in error for error in guard.check_schemas())


@pytest.mark.parametrize(
    "old,new,expected",
    [
        ('"app-server"', '"exec"', "app-server"),
        ('"standalone_web_search"', '"something_else"', "standalone_web_search"),
        ('"sandbox": "read-only"', '"sandbox": "danger-full-access"', "read-only"),
        ('"approvalPolicy": "never"', '"approvalPolicy": "on-request"', "never"),
        ('"dynamicTools": []', '"dynamicTools": None', "dynamicTools"),
        ('"Logged in using ChatGPT"', '"Logged in"', "Logged in using ChatGPT"),
        ('selector != "codex"', 'selector not in {"codex", "anything"}', "selector"),
        ('"webSearch"', '"agentMessage"', "webSearch"),
        ('"search_result_digest"', '"result_digest"', "search_result_digest"),
    ],
)
def test_runtime_mutations_fail(tmp_path: Path, monkeypatch, old, new, expected) -> None:
    guard = _load_guard()
    mutated = _mutated_file(tmp_path, guard.RUNTIME, old, new)
    monkeypatch.setattr(guard, "RUNTIME", mutated)
    assert any(expected in error for error in guard.check_runtime())


def test_child_env_secret_mutation_fails(tmp_path: Path, monkeypatch) -> None:
    guard = _load_guard()
    mutated = _mutated_file(
        tmp_path,
        guard.RUNTIME,
        '"NO_COLOR": "1",',
        '"NO_COLOR": "1",\n        "OPENAI_API_KEY": environ.get("OPENAI_API_KEY", ""),',
    )
    monkeypatch.setattr(guard, "RUNTIME", mutated)
    assert any("child environment" in error for error in guard.check_runtime())


@pytest.mark.parametrize(
    "old,new,expected",
    [
        (
            "_close_app_server_stdin(proc)",
            "_stop_process(proc)",
            "post-terminal EOF boundary",
        ),
        (
            "drain_deadline = min(\n"
            "                deadline, terminal_observed_at + APP_SERVER_DRAIN_GRACE_SECONDS\n"
            "            )",
            "drain_deadline = terminal_observed_at + APP_SERVER_DRAIN_GRACE_SECONDS",
            "post-terminal EOF boundary",
        ),
        (
            "if remaining <= 0:\n"
            '        raise TransportError("APP_SERVER_DRAIN_TIMEOUT")\n'
            "    return remaining",
            "if remaining <= 0:\n        return 0.001\n    return remaining",
            "deadline no longer fails closed",
        ),
        (
            "            _drain_app_server_after_turn(\n"
            "                proc,\n"
            "                reader,\n"
            "                stderr_reader,\n"
            "                messages,\n"
            "                raw_lines,\n"
            "                drain_deadline,\n"
            "            )",
            "            try:\n"
            "                _drain_app_server_after_turn(\n"
            "                    proc,\n"
            "                    reader,\n"
            "                    stderr_reader,\n"
            "                    messages,\n"
            "                    raw_lines,\n"
            "                    drain_deadline,\n"
            "                )\n"
            "            except TransportError:\n"
            "                pass",
            "drain failure is caught",
        ),
    ],
    ids=[
        "stdin-close-removed",
        "fresh-drain-timeout",
        "drain-timeout-ignored",
        "drain-error-swallowed",
    ],
)
def test_terminal_drain_mutations_fail(
    tmp_path: Path, monkeypatch, old: str, new: str, expected: str
) -> None:
    guard = _load_guard()
    mutated = _mutated_file(tmp_path, guard.RUNTIME, old, new)
    monkeypatch.setattr(guard, "RUNTIME", mutated)
    assert any(expected in error for error in guard.check_runtime())


@pytest.mark.parametrize(
    "helper,constructor",
    [
        ("reader", "_LineReader(proc.stdout, limit=MAX_EVENT_BYTES)"),
        ("stderr_reader", "_DrainReader(proc.stderr, limit=MAX_STDERR_BYTES)"),
    ],
    ids=["stdout-helper-escaped", "stderr-helper-escaped"],
)
def test_reader_helper_construction_must_remain_process_owned(
    tmp_path: Path, monkeypatch, helper: str, constructor: str
) -> None:
    guard = _load_guard()
    original = guard.RUNTIME.read_text(encoding="utf-8")
    owner_anchor = (
        "        try:\n"
        "            if proc.stdout is None or proc.stderr is None:\n"
    )
    mutated = original.replace(
        owner_anchor,
        f"        {helper} = {constructor}\n" + owner_anchor,
        1,
    ).replace(
        f"            {helper} = {constructor}\n",
        f"            {helper} = {helper}\n",
        1,
    )
    assert mutated != original
    target = tmp_path / "runtime.py"
    target.write_text(mutated, encoding="utf-8")
    monkeypatch.setattr(guard, "RUNTIME", target)
    assert any("not process-owned" in error for error in guard.check_runtime())


@pytest.mark.parametrize(
    "attribute,old,new,expected",
    [
        ("SPEC", "Source implementation: PR #567 by `dcs-scd`", "Source implementation: internal", "PR #567"),
        ("PROTOCOL", "**Recommendation policy (2026-08-19):**", "**GPT-5.6 is recommended:**", "recommendation-policy"),
        ("PROTOCOL", "a lifecycle decision, not a measurement claim", "a measured upgrade over GPT-5.5", "recommendation-policy"),
        ("PROTOCOL", "`validated` is earned only there", "`validated` is granted on release", "recommendation-policy"),
        ("PRODUCER", "This adapter is not available to DA, reviewer, calibration", "This adapter is available to every path", "non-citation"),
        ("CHANGELOG", "@dcs-scd", "@someone-else", "@dcs-scd"),
    ],
)
def test_doc_mutations_fail(tmp_path: Path, monkeypatch, attribute, old, new, expected) -> None:
    guard = _load_guard()
    source = getattr(guard, attribute)
    mutated = _mutated_file(tmp_path, source, old, new)
    monkeypatch.setattr(guard, attribute, mutated)
    assert any(expected in error for error in guard.check_docs_and_wiring())


def test_smoke_wired_to_ci_fails(tmp_path: Path, monkeypatch) -> None:
    guard = _load_guard()
    mutated = tmp_path / "workflow.yml"
    mutated.write_text(
        guard.WORKFLOW.read_text(encoding="utf-8")
        + "\n      - run: scripts/cross_model_smoke_test_codex.sh\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(guard, "WORKFLOW", mutated)
    assert any("live Codex smoke" in error for error in guard.check_shell_and_ci())


def test_bash_4_mutation_fails(tmp_path: Path, monkeypatch) -> None:
    guard = _load_guard()
    mutated = _mutated_file(tmp_path, guard.VERIFY_SH, "set -u", "set -u\nmapfile rows")
    monkeypatch.setattr(guard, "VERIFY_SH", mutated)
    assert any("non-Bash-3.2" in error for error in guard.check_shell_and_ci())


def test_fixture_inventory_mutation_fails(tmp_path: Path, monkeypatch) -> None:
    guard = _load_guard()
    fixtures = tmp_path / "fixtures"
    fixtures.mkdir()
    for name in sorted(guard.EXPECTED_FIXTURES - {"missing_search.jsonl"}):
        (fixtures / name).write_text("{}\n", encoding="utf-8")
    monkeypatch.setattr(guard, "FIXTURES", fixtures)
    assert any("fixture inventory drift" in error for error in guard.check_shell_and_ci())
