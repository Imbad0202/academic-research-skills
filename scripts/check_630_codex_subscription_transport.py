#!/usr/bin/env python3
"""Static integration guard for the contained #630 citation transport."""

from __future__ import annotations

import ast
import json
from pathlib import Path
import re
import sys
from typing import Any


REPO = Path(__file__).resolve().parent.parent
RUNTIME = REPO / "scripts" / "cross_model_codex_transport.py"
RUNTIME_TEST = REPO / "scripts" / "test_cross_model_codex_transport.py"
VERIFY_SH = REPO / "scripts" / "cross_model_codex_verify.sh"
SMOKE_SH = REPO / "scripts" / "cross_model_smoke_test_codex.sh"
SPEC = REPO / "docs" / "design" / "2026-08-11-630-codex-subscription-citation-transport-spec.md"
PROTOCOL = REPO / "shared" / "cross_model_verification.md"
PRODUCER = REPO / "academic-pipeline" / "agents" / "integrity_verification_agent.md"
SETUP_EN = REPO / "docs" / "SETUP.md"
SETUP_ZH = REPO / "docs" / "SETUP.zh-TW.md"
CHANGELOG = REPO / "CHANGELOG.md"
REQUEST_SCHEMA = (
    REPO / "shared" / "contracts" / "cross_model" / "codex_citation_request.schema.json"
)
RECEIPT_SCHEMA = (
    REPO / "shared" / "contracts" / "cross_model" / "codex_citation_receipt.schema.json"
)
FIXTURES = REPO / "scripts" / "fixtures" / "cross_model_codex_transport"
MANIFEST = REPO / "scripts" / "_ci_pytest_manifest.toml"
WORKFLOW = REPO / ".github" / "workflows" / "spec-consistency.yml"

EXPECTED_FIXTURES = {
    "forbidden_event.jsonl",
    "grounded_verified.jsonl",
    "malformed.jsonl",
    "missing_search.jsonl",
    "multiple_finals.jsonl",
    "not_found.jsonl",
    "unbound_source.jsonl",
    "wrong_search_shape.jsonl",
}
EXPECTED_CHILD_ENV = {"PATH", "CODEX_HOME", "HOME", "TMPDIR", "LANG", "LC_ALL", "NO_COLOR"}
EXPECTED_STATUS_ENV = {"PATH", "CODEX_HOME", "HOME", "LANG", "LC_ALL", "NO_COLOR"}
REQUIRED_DISABLED_FEATURES = {
    "apps",
    "artifact",
    "browser_use",
    "code_mode",
    "computer_use",
    "goals",
    "hooks",
    "image_generation",
    "multi_agent",
    "plugins",
    "shell_tool",
    "skill_search",
    "unified_exec",
    "view_image",
    "workspace_dependencies",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_json(path: Path) -> dict[str, Any]:
    def closed(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, item in pairs:
            if key in value:
                raise ValueError(f"duplicate key {key!r}")
            value[key] = item
        return value

    return json.loads(_read(path), object_pairs_hook=closed)


def _function(tree: ast.Module, name: str) -> ast.FunctionDef:
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise ValueError(f"missing function {name}")


def _assignment_literal(tree: ast.Module, name: str) -> Any:
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            target = node.targets[0] if isinstance(node, ast.Assign) else node.target
            if isinstance(target, ast.Name) and target.id == name:
                return ast.literal_eval(node.value)
    raise ValueError(f"missing assignment {name}")


def _returned_dict_keys(function: ast.FunctionDef) -> set[str]:
    returns = [node for node in ast.walk(function) if isinstance(node, ast.Return)]
    if len(returns) != 1 or returns[0].value is None:
        raise ValueError("expected exactly one return value")
    value = returns[0].value
    if isinstance(value, ast.Name):
        assignments = [
            node
            for node in ast.walk(function)
            if isinstance(node, ast.Assign)
            and any(isinstance(target, ast.Name) and target.id == value.id for target in node.targets)
        ]
        if len(assignments) != 1:
            raise ValueError("returned dictionary name has no single assignment")
        value = assignments[0].value
    if not isinstance(value, ast.Dict):
        raise ValueError("return value is not a literal dictionary")
    return {ast.literal_eval(key) for key in value.keys}


def check_schemas() -> list[str]:
    errors: list[str] = []
    try:
        request = _load_json(REQUEST_SCHEMA)
        receipt = _load_json(RECEIPT_SCHEMA)
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        return [f"schema load failed: {exc}"]
    for label, schema, version in (
        ("request", request, "ars-codex-citation-request/1.0"),
        ("receipt", receipt, "ars-codex-citation-receipt/1.0"),
    ):
        if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            errors.append(f"{label} schema is not Draft 2020-12")
        if schema.get("type") != "object" or schema.get("additionalProperties") is not False:
            errors.append(f"{label} schema root is not closed")
        if schema.get("properties", {}).get("schema_version", {}).get("const") != version:
            errors.append(f"{label} schema version is not pinned")
    request_properties = set(request.get("properties", {}))
    if request_properties != {"schema_version", "request_id", "reference_text", "citation_context"}:
        errors.append("request schema is not the exact four-field data-only carrier")
    forbidden_request_fields = {"path", "prompt", "file", "url", "instructions", "verdict"}
    if request_properties & forbidden_request_fields:
        errors.append("request schema exposes a prompt/path/verdict field")
    for name, definition in receipt.get("$defs", {}).items():
        if isinstance(definition, dict) and definition.get("type") == "object":
            if definition.get("additionalProperties") is not False:
                errors.append(f"receipt definition {name} is open")
    binding_required = {"url", "search_item_id", "result_index", "search_result_digest"}
    if set(receipt.get("$defs", {}).get("source_binding", {}).get("required", [])) != binding_required:
        errors.append("receipt source binding is not exact item/index/digest authority")
    receipt_conditions = json.dumps(receipt.get("allOf", []), sort_keys=True)
    for token in ("NOT_SEARCHED", "VERIFIED", "MISMATCH", "NOT_FOUND", "minItems", "maxItems"):
        if token not in receipt_conditions:
            errors.append(f"receipt cross-field conditions dropped {token}")
    return errors


def check_runtime() -> list[str]:
    errors: list[str] = []
    try:
        source = _read(RUNTIME)
        tree = ast.parse(source)
    except (OSError, UnicodeError, SyntaxError) as exc:
        return [f"runtime parse failed: {exc}"]
    try:
        if _assignment_literal(tree, "MIN_CODEX_VERSION") < (0, 147, 0):
            errors.append("minimum Codex version is below 0.147.0")
        app_timeout = _assignment_literal(tree, "APP_SERVER_TIMEOUT_SECONDS")
        drain_grace = _assignment_literal(tree, "APP_SERVER_DRAIN_GRACE_SECONDS")
        if (
            not isinstance(drain_grace, (int, float))
            or isinstance(drain_grace, bool)
            or drain_grace <= 0
            or drain_grace >= app_timeout
        ):
            errors.append("post-terminal drain grace is not positive and smaller than runtime")
        disabled = set(_assignment_literal(tree, "DISABLED_FEATURES"))
        missing = REQUIRED_DISABLED_FEATURES - disabled
        if missing:
            errors.append(f"disabled feature set dropped: {sorted(missing)}")
        for function_name, expected_keys in (
            ("_minimal_status_env", EXPECTED_STATUS_ENV),
            ("_child_env", EXPECTED_CHILD_ENV),
        ):
            function = _function(tree, function_name)
            keys = _returned_dict_keys(function)
            if keys != expected_keys:
                errors.append(f"child environment is not closed in {function_name}: {sorted(keys)}")
        allowed_items = set(_assignment_literal(tree, "ALLOWED_ITEM_TYPES"))
        if "webSearch" not in allowed_items:
            errors.append("allowed item types dropped webSearch")
    except (ValueError, TypeError, SyntaxError) as exc:
        errors.append(f"runtime structural contract failed: {exc}")

    command_source = ast.get_source_segment(source, _function(tree, "build_app_server_command")) or ""
    for token in (
        "app-server",
        "--stdio",
        "--strict-config",
        "standalone_web_search",
        "mcp_servers={}",
    ):
        if token not in command_source:
            errors.append(f"app-server command dropped {token}")
    if re.search(r"['\"]exec['\"]", command_source):
        errors.append("runtime regressed to codex exec instead of app-server")
    detection_source = ast.get_source_segment(source, _function(tree, "detect_transport")) or ""
    for token in (
        'selector in {"", "api"}',
        'selector != "codex"',
        "Logged in using ChatGPT",
        "CODEX_VERSION_TOO_OLD",
        "AUTH_NOT_CHATGPT_SUBSCRIPTION",
    ):
        if token not in detection_source:
            errors.append(f"detection contract dropped {token!r}")
    run_source = ast.get_source_segment(source, _function(tree, "run_app_server")) or ""
    run_function = _function(tree, "run_app_server")
    for token in (
        '"sandbox": "read-only"',
        '"ephemeral": True',
        '"dynamicTools": []',
        '"selectedCapabilityRoots": []',
        '"runtimeWorkspaceRoots": []',
        "TemporaryDirectory",
    ):
        if token not in run_source:
            errors.append(f"minimum-privilege runtime dropped {token!r}")
    if run_source.count('"approvalPolicy": "never"') != 2:
        errors.append("minimum-privilege runtime must pin approvalPolicy never at thread and turn")
    helper_calls = {
        helper: [
            node
            for node in ast.walk(run_function)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == helper
        ]
        for helper in ("_LineReader", "_DrainReader")
    }
    if any(len(calls) != 1 for calls in helper_calls.values()):
        errors.append("reader helpers must each be constructed exactly once")
    else:
        helper_nodes = [calls[0] for calls in helper_calls.values()]
        helpers_process_owned = False
        for try_node in (node for node in ast.walk(run_function) if isinstance(node, ast.Try)):
            body_nodes = [nested for statement in try_node.body for nested in ast.walk(statement)]
            final_nodes = [nested for statement in try_node.finalbody for nested in ast.walk(statement)]
            has_process_stop = any(
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "_stop_process"
                for node in final_nodes
            )
            if has_process_stop and all(node in body_nodes for node in helper_nodes):
                final_source = "\n".join(
                    ast.get_source_segment(source, statement) or ""
                    for statement in try_node.finalbody
                )
                if (
                    "reader.thread.join" in final_source
                    and "stderr_reader.thread.join" in final_source
                ):
                    helpers_process_owned = True
                    break
        if not helpers_process_owned:
            errors.append("reader helper construction is not process-owned through cleanup")
    for token in (
        "_close_app_server_stdin(proc)",
        "terminal_observed_at = time.monotonic()",
        "drain_deadline = min(",
        "deadline, terminal_observed_at + APP_SERVER_DRAIN_GRACE_SECONDS",
        "_drain_app_server_after_turn(",
        "drain_deadline",
    ):
        if token not in run_source:
            errors.append(f"post-terminal EOF boundary dropped {token!r}")
    drain_calls = [
        node
        for node in ast.walk(run_function)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "_drain_app_server_after_turn"
    ]
    if len(drain_calls) != 1:
        errors.append("post-terminal drain must be called exactly once")
    for try_node in (node for node in ast.walk(run_function) if isinstance(node, ast.Try)):
        body_nodes = [nested for statement in try_node.body for nested in ast.walk(statement)]
        if try_node.handlers and any(node in body_nodes for node in drain_calls):
            errors.append("post-terminal drain failure is caught inside run_app_server")
    drain_source = ast.get_source_segment(
        source, _function(tree, "_drain_app_server_after_turn")
    ) or ""
    for token in (
        'timeout_code="APP_SERVER_DRAIN_TIMEOUT"',
        "_parse_rpc_line(raw)",
        'raise TransportError("APP_SERVER_UNEXPECTED_REQUEST")',
        'raise TransportError("EVENT_MESSAGE_LIMIT_EXCEEDED")',
        "proc.wait(timeout=_remaining_drain_seconds(deadline))",
        'raise TransportError("APP_SERVER_EXIT_NONZERO")',
        "reader.thread.join(timeout=_remaining_drain_seconds(deadline))",
        "stderr_reader.thread.join(timeout=_remaining_drain_seconds(deadline))",
        'raise TransportError("APP_SERVER_STDERR_TOO_LARGE")',
    ):
        if token not in drain_source:
            errors.append(f"post-terminal closed drain dropped {token!r}")
    remaining_source = ast.get_source_segment(
        source, _function(tree, "_remaining_drain_seconds")
    ) or ""
    if 'raise TransportError("APP_SERVER_DRAIN_TIMEOUT")' not in remaining_source:
        errors.append("post-terminal drain deadline no longer fails closed")
    parser_source = ast.get_source_segment(source, _function(tree, "parse_app_server_messages")) or ""
    for token in (
        "webSearch",
        "results",
        "_query_is_reference_bound",
        "_extract_result_urls",
        "search_result_digest",
        "SOURCE_NOT_IN_SEARCH_RESULTS",
        "FORBIDDEN_TOOL_EVENT",
    ):
        if token not in parser_source:
            errors.append(f"result-binding parser dropped {token}")
    if "shutil.copy" in source or "copytree" in source:
        errors.append("runtime copies ambient Codex state instead of auth-only bytes")
    if any(token in source for token in ("requests.", "urllib.request", "http.client", "socket.")):
        errors.append("runtime performs its own network access outside contained Codex search")
    return errors


def check_docs_and_wiring() -> list[str]:
    errors: list[str] = []
    try:
        spec = _read(SPEC)
        protocol = _read(PROTOCOL)
        producer = _read(PRODUCER)
        setup_en = _read(SETUP_EN)
        setup_zh = _read(SETUP_ZH)
        changelog = _read(CHANGELOG)
    except (OSError, UnicodeError) as exc:
        return [f"documentation load failed: {exc}"]
    required_spec = (
        "Source implementation: PR #567 by `dcs-scd`",
        "It is legal only for the one-reference-at-a-time citation-integrity call",
        "It is not a transport for Devil's",
        "No model promotion, recommended-default change",
        "CI must never run it",
        "close app-server stdin",
        "clean parent exit and stdout/stderr EOF",
        "min(global deadline, terminal observation time + drain grace)",
    )
    for text in required_spec:
        if text not in spec:
            errors.append(f"frozen spec dropped {text!r}")
    for label, text in (("protocol", protocol), ("producer", producer)):
        for token in (
            "ARS_CROSS_MODEL_TRANSPORT=codex",
            "codex_citation_request",
            "codex_citation_receipt",
            "citation",
        ):
            if token not in text:
                errors.append(f"{label} wiring dropped {token}")
    if "This adapter is not available to DA, reviewer, calibration" not in producer:
        errors.append("producer no longer excludes non-citation consumers")
    for token in (
        'case "${ARS_CROSS_MODEL_TRANSPORT:-api}" in',
        "python3 scripts/cross_model_codex_transport.py detect",
        "invalid ARS_CROSS_MODEL_TRANSPORT selector",
    ):
        if token not in protocol:
            errors.append(f"protocol availability routing dropped {token!r}")
    # The policy BODY clauses are pinned alongside the heading: a rewrite that
    # keeps the marker but asserts measured parity (or drops the bakeoff-only
    # route to `validated`) must fail, not just a deleted heading (#783).
    for token in (
        "**Recommendation policy (2026-08-19):**",
        "a lifecycle decision, not a measurement claim",
        "`validated` is earned only there",
    ):
        if token not in protocol:
            errors.append(
                f"#630 recommendation-policy witness dropped {token!r} — the "
                "default-model recommendation must stay an explicit, dated, "
                "no-measurement-claim policy note with the bakeoff as the only "
                "route to validated (#783), never a silent promotion"
            )
    if "**provisional pending ARS validation**" not in protocol:
        errors.append("#630 must not promote GPT-5.6 from provisional")
    bash_marker = 'export ARS_CROSS_MODEL_TRANSPORT="codex"'
    if bash_marker not in setup_en or bash_marker not in setup_zh:
        errors.append("SETUP en/zh-TW dropped the closed selector example")
    for token in ("@dcs-scd", "PR #567", "no model promotion", "#725", "stdin EOF"):
        if token not in changelog:
            errors.append(f"contributor changelog dropped {token}")
    return errors


def check_shell_and_ci() -> list[str]:
    errors: list[str] = []
    try:
        verify = _read(VERIFY_SH)
        smoke = _read(SMOKE_SH)
        workflow = _read(WORKFLOW)
        manifest = _read(MANIFEST)
    except (OSError, UnicodeError) as exc:
        return [f"shell/CI load failed: {exc}"]
    for label, text in (("verify", verify), ("smoke", smoke)):
        if not text.startswith("#!/bin/bash\n"):
            errors.append(f"{label} wrapper does not declare /bin/bash")
        for pattern in (r"\bmapfile\b", r"\breadarray\b", r"declare\s+-A", r"\$\{!", r"<\("):
            if re.search(pattern, text):
                errors.append(f"{label} wrapper uses non-Bash-3.2 syntax: {pattern}")
    if "Manual LIVE smoke test. CI must never invoke this file." not in smoke:
        errors.append("live smoke lost its manual/no-CI warning")
    if "cross_model_smoke_test_codex.sh" in workflow or "cross_model_smoke_test_codex.sh" in manifest:
        errors.append("live Codex smoke is wired into CI")
    for entry in (
        'id = "630-codex-subscription-transport"',
        'path = "scripts/test_cross_model_codex_transport.py"',
        'id = "630-codex-subscription-integration"',
        'path = "scripts/test_check_630_codex_subscription_transport.py"',
    ):
        if entry not in manifest:
            errors.append(f"pytest manifest dropped {entry}")
    if "python3 scripts/check_630_codex_subscription_transport.py" not in workflow:
        errors.append("spec-consistency workflow does not invoke the #630 guard directly")
    try:
        names = {path.name for path in FIXTURES.iterdir() if path.is_file()}
    except OSError as exc:
        errors.append(f"fixture inventory unavailable: {exc}")
    else:
        if names != EXPECTED_FIXTURES:
            errors.append(
                f"fixture inventory drift: missing={sorted(EXPECTED_FIXTURES - names)} "
                f"extra={sorted(names - EXPECTED_FIXTURES)}"
            )
    if "subprocess.run" not in _read(RUNTIME_TEST) or "fake-bin" not in _read(RUNTIME_TEST):
        errors.append("runtime tests no longer exercise a fake Codex executable end-to-end")
    return errors


def check_all() -> list[str]:
    return check_schemas() + check_runtime() + check_docs_and_wiring() + check_shell_and_ci()


def main() -> int:
    errors = check_all()
    if errors:
        print("#630 Codex subscription transport integration guard FAILED:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print("#630 Codex subscription transport integration guard PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
