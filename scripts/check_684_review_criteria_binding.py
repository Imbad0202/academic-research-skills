#!/usr/bin/env python3
"""Static integration guard for #684 review-criteria consumer binding."""
from __future__ import annotations

import ast
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC = Path("docs/design/2026-08-11-684-review-criteria-consumer-binding-spec.md")
BINDING_SCHEMA = Path("shared/contracts/review_target/review_criteria_binding_manifest.schema.json")
FINDINGS_SCHEMA = Path("shared/contracts/review_target/constructive_review_findings.schema.json")
PROTOCOL = Path("shared/references/review_criteria_consumer_protocol.md")
RUNTIME = Path("scripts/review_criteria_binding.py")
SCORER = Path("scripts/score_review_criteria_constructive_value.py")
MEASUREMENT_RUNNER = Path("scripts/run_review_criteria_constructive_value.py")
FORMATIVE = Path("academic-paper/agents/structure_architect_agent.md")
INTERNAL = Path("academic-paper/agents/peer_reviewer_agent.md")
CANONICAL = Path("academic-paper-reviewer/references/reviewer_sprint_prompt_source.md")
SYNTH = Path("academic-paper-reviewer/agents/editorial_synthesizer_agent.md")
ORCHESTRATOR = Path("academic-pipeline/agents/pipeline_orchestrator_agent.md")
STATE = Path("academic-pipeline/agents/state_tracker_agent.md")
HANDOFFS = Path("shared/handoff_schemas.md")
MEASUREMENT = Path("evals/heldout/review_criteria_constructive_value/measurement_plan.md")
ADJUDICATION_SCHEMA = Path("evals/heldout/review_criteria_constructive_value/paired_adjudication.schema.json")
SCENARIOS_SCHEMA = Path("evals/heldout/review_criteria_constructive_value/scenarios.schema.json")
SCENARIOS = Path("evals/heldout/review_criteria_constructive_value/scenarios.json")
SUBJECT_OUTPUT_SCHEMA = Path("evals/heldout/review_criteria_constructive_value/subject_output.schema.json")
EXPERT_PACKET_SCHEMA = Path("evals/heldout/review_criteria_constructive_value/expert_packet.schema.json")
EXPERT_LABELS_SCHEMA = Path("evals/heldout/review_criteria_constructive_value/expert_labels.schema.json")
DECISIONS_SCHEMA = Path("evals/heldout/review_criteria_constructive_value/adjudication_decisions.schema.json")
CALL_PLAN = Path("evals/heldout/review_criteria_constructive_value/call_plan.json")
SUITE_LOCK = Path("evals/heldout/review_criteria_constructive_value/suite_lock.json")
HELDOUT_SET = Path("evals/heldout/review_criteria_constructive_value/heldout_set.json")
BASELINE_PROMPT = Path("evals/heldout/review_criteria_constructive_value/baseline_prompt.md")
TREATMENT_PROMPT = Path("evals/heldout/review_criteria_constructive_value/treatment_prompt.md")
EXPERT_GUIDE = Path("evals/heldout/review_criteria_constructive_value/expert_label_guide.md")
SCENARIO_REGISTRY = Path("scripts/fixtures/review_target_context/synthetic-registry.json")
SUITE_REGISTRY = Path("evals/heldout/suite_registry.json")

REQUIRED_FILES = (
    SPEC,
    BINDING_SCHEMA,
    FINDINGS_SCHEMA,
    PROTOCOL,
    RUNTIME,
    SCORER,
    MEASUREMENT_RUNNER,
    FORMATIVE,
    INTERNAL,
    CANONICAL,
    SYNTH,
    ORCHESTRATOR,
    STATE,
    HANDOFFS,
    MEASUREMENT,
    ADJUDICATION_SCHEMA,
    SCENARIOS_SCHEMA,
    SCENARIOS,
    SUBJECT_OUTPUT_SCHEMA,
    EXPERT_PACKET_SCHEMA,
    EXPERT_LABELS_SCHEMA,
    DECISIONS_SCHEMA,
    CALL_PLAN,
    SUITE_LOCK,
    HELDOUT_SET,
    BASELINE_PROMPT,
    TREATMENT_PROMPT,
    EXPERT_GUIDE,
    SCENARIO_REGISTRY,
    SUITE_REGISTRY,
)

CLI_COMMANDS = {"init", "marker", "record", "validate", "validate-findings"}
MEASUREMENT_COMMANDS = {
    "validate-assets",
    "detect",
    "init-run",
    "dispatch",
    "prepare-expert-packet",
    "validate-labels",
    "finalize",
    "build-report",
}
LOCKED_MEASUREMENT_ASSETS = (
    DECISIONS_SCHEMA,
    BASELINE_PROMPT,
    CALL_PLAN,
    EXPERT_GUIDE,
    EXPERT_LABELS_SCHEMA,
    EXPERT_PACKET_SCHEMA,
    HELDOUT_SET,
    MEASUREMENT,
    ADJUDICATION_SCHEMA,
    SCENARIOS,
    SCENARIOS_SCHEMA,
    SUBJECT_OUTPUT_SCHEMA,
    TREATMENT_PROMPT,
    SCENARIO_REGISTRY,
    MEASUREMENT_RUNNER,
    SCORER,
)
CONSUMERS = ("formative_planning", "internal_evaluator", "external_panel")
ROLES = ("FORMATIVE", "INTERNAL", "EIC", "R1", "R2", "R3", "DA")
FORBIDDEN_IMPORTS = {
    "anthropic",
    "datetime",
    "http",
    "openai",
    "requests",
    "socket",
    "subprocess",
    "time",
    "urllib",
}
FORBIDDEN_SCANS = {"glob", "iglob", "iterdir", "listdir", "rglob", "scandir", "walk"}
NON_CONSUMERS = (
    Path("academic-pipeline/agents/integrity_verification_agent.md"),
    Path("academic-paper/agents/formatter_agent.md"),
    Path("academic-pipeline/references/process_summary_protocol.md"),
    Path("shared/contracts/evaluator/full.json"),
    Path("shared/contracts/writer/full.json"),
)
FEATURE_TOKENS = (
    "review_criteria_binding",
    "criteria_binding_v1",
    "REVIEW-TARGET-BINDING",
    "constructive-review-findings/1.0",
)

REQUIRED_TEXT: dict[Path, tuple[str, ...]] = {
    SPEC: (
        "Exactly three consumer",
        "Phase 1 receives the sprint contract",
        "proposed_result_values",
        "value effect is unmeasured",
    ),
    PROTOCOL: (
        "formative_planning",
        "## 4. Internal evaluator",
        "external_panel",
        "EIC", "R1", "R2", "R3", "DA",
        "criteria_binding_unavailable",
    ),
    FORMATIVE: (
        "role `FORMATIVE` binding marker",
        "single formative receipt",
        "criteria_parallel_conflicts: <canonical compact JSON array>",
    ),
    INTERNAL: ("role `INTERNAL` marker", "do not decide manuscript"),
    CANONICAL: (
        "criteria_parallel_conflicts:",
        "[REVIEW-TARGET-BINDING v1]",
        "do not decide applicability in Phase 1",
        "Criteria-aware constructive findings (#684)",
    ),
    SYNTH: (
        "EIC, R1, R2, R3, and DA",
        "Missing or mismatched binding aborts",
        "conformance is not a score",
    ),
    ORCHESTRATOR: (
        "scripts/review_criteria_binding.py init",
        "--require-complete",
        "validate-findings",
        "mid-entry run validates only consumers actually dispatched",
        "pre-commitment artifact is recorded as `INTERNAL` before Phase 6b",
        "not a manuscript gate",
    ),
    STATE: ("manifest itself is the sole", "no missing consumer is"),
    HANDOFFS: ("Separately named review-target authority (#683/#684)",),
    MEASUREMENT: (
        "identical target context bytes",
        "exactly two fresh isolated replicates",
        "No composite score",
        "PRE-REGISTERED / NOT RUN",
        "dispatches exactly 24 subject calls",
        "judge_plan.exception: \"human_expert_panel\"",
        "`judges` is empty",
        "No model judge is",
        "independent blinded human experts",
        "incremental metered API spend ceiling of **USD 0**",
        "There is no API fallback within this run",
        "provider_managed_not_exposed",
        "citation adapter is not this launcher",
        "call_plan.json",
        "suite_lock.json",
        "scripts/run_review_criteria_constructive_value.py",
        "validate these artifacts and the scorer but never dispatch",
    ),
}


def _read_json(text: str, label: str, errors: list[str]) -> dict[str, Any] | None:
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        errors.append(f"{label}: invalid JSON: {exc}")
        return None
    if not isinstance(value, dict):
        errors.append(f"{label}: top-level value must be an object")
        return None
    return value


def check_contracts(texts: dict[Path, str]) -> list[str]:
    errors: list[str] = []
    schemas: dict[Path, dict[str, Any]] = {}
    for path in (
        BINDING_SCHEMA,
        FINDINGS_SCHEMA,
        ADJUDICATION_SCHEMA,
        SCENARIOS_SCHEMA,
        SUBJECT_OUTPUT_SCHEMA,
        EXPERT_PACKET_SCHEMA,
        EXPERT_LABELS_SCHEMA,
        DECISIONS_SCHEMA,
    ):
        value = _read_json(texts[path], str(path), errors)
        if value is None:
            continue
        try:
            Draft202012Validator.check_schema(value)
        except Exception as exc:  # jsonschema exposes several schema exceptions
            errors.append(f"{path}: Draft 2020-12 metaschema failure: {exc}")
        if value.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            errors.append(f"{path}: must declare Draft 2020-12")
        if value.get("additionalProperties") is not False:
            errors.append(f"{path}: root must be closed")
        schemas[path] = value

    binding = schemas.get(BINDING_SCHEMA)
    if binding is not None:
        receipt = binding.get("$defs", {}).get("receipt", {})
        consumer_enum = receipt.get("properties", {}).get("consumer_id", {}).get("enum")
        if consumer_enum != list(CONSUMERS):
            errors.append("binding schema: consumer enum/order drift")
        roles = (
            binding.get("$defs", {})
            .get("artifact_binding", {})
            .get("properties", {})
            .get("role", {})
            .get("enum")
        )
        if roles != list(ROLES):
            errors.append("binding schema: closed role enum/order drift")
        receipts = binding.get("properties", {}).get("receipts", {})
        if receipts.get("maxItems") != 3:
            errors.append("binding schema: receipts.maxItems must be 3")

    findings = schemas.get(FINDINGS_SCHEMA)
    if findings is not None:
        option = findings.get("$defs", {}).get("option", {})
        proposed = option.get("properties", {}).get("proposed_result_values", {})
        if proposed.get("const") is not False:
            errors.append("findings schema: proposed_result_values must be const false")
        severity = (
            findings.get("$defs", {})
            .get("finding", {})
            .get("properties", {})
            .get("severity", {})
            .get("enum")
        )
        if severity != ["critical", "major"]:
            errors.append("findings schema: sidecar must be Critical/Major only")

    adjudication = schemas.get(ADJUDICATION_SCHEMA)
    if adjudication is not None:
        defs = adjudication.get("$defs", {})
        applicability_required = (
            defs.get("replicate", {})
            .get("properties", {})
            .get("applicability", {})
            .get("items", {})
            .get("required", [])
        )
        finding_required = defs.get("finding", {}).get("required", [])
        if "expert_labels" not in applicability_required:
            errors.append("adjudication schema: applicability rows need raw expert labels")
        if "expert_labels" not in finding_required:
            errors.append("adjudication schema: finding rows need raw expert labels")
        blinded = (
            adjudication.get("properties", {})
            .get("experts", {})
            .get("items", {})
            .get("properties", {})
            .get("blinded_to", {})
        )
        if blinded.get("minItems") != 5 or blinded.get("maxItems") != 5:
            errors.append("adjudication schema: experts need exact five-way blinding")
        expert_properties = (
            adjudication.get("properties", {})
            .get("experts", {})
            .get("items", {})
            .get("properties", {})
        )
        adjudication_properties = (
            adjudication.get("properties", {}).get("adjudication", {}).get("properties", {})
        )
        if expert_properties.get("expert_type", {}).get("const") != "human":
            errors.append("adjudication schema: expert_type must be human")
        if adjudication_properties.get("adjudicator_type", {}).get("const") != "human":
            errors.append("adjudication schema: adjudicator_type must be human")

    registry = _read_json(texts[SUITE_REGISTRY], str(SUITE_REGISTRY), errors)
    if registry is not None and registry.get("review_criteria_constructive_value") != "paired_controls":
        errors.append("suite registry: #684 suite must be paired_controls")
    return errors


def _assignment(tree: ast.AST, name: str) -> Any:
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    try:
                        return ast.literal_eval(node.value)
                    except (ValueError, TypeError):
                        return None
    return None


def check_python(path: Path, source: str, *, runtime: bool) -> list[str]:
    errors: list[str] = []
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        return [f"{path}: cannot parse Python: {exc}"]
    for node in ast.walk(tree):
        roots: list[str] = []
        if isinstance(node, ast.Import):
            roots = [alias.name.split(".")[0] for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots = [node.module.split(".")[0]]
        for root in roots:
            if root in FORBIDDEN_IMPORTS:
                errors.append(f"{path}:{node.lineno}: forbidden live/clock import {root}")
        if isinstance(node, ast.Call):
            name = ""
            if isinstance(node.func, ast.Name):
                name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                name = node.func.attr
            if name in FORBIDDEN_SCANS:
                errors.append(f"{path}:{node.lineno}: forbidden ambient scan call {name}")
    if runtime:
        consumers = _assignment(tree, "CONSUMERS")
        roles = _assignment(tree, "ROLES")
        if consumers != CONSUMERS:
            errors.append(f"{path}: runtime consumer tuple drift")
        expected_roles = {
            "formative_planning": ("FORMATIVE",),
            "internal_evaluator": ("INTERNAL",),
            "external_panel": ("EIC", "R1", "R2", "R3", "DA"),
        }
        if roles != expected_roles:
            errors.append(f"{path}: runtime role map drift")
        commands = {
            node.args[0].value
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "add_parser"
            and node.args
            and isinstance(node.args[0], ast.Constant)
            and isinstance(node.args[0].value, str)
        }
        if commands != CLI_COMMANDS:
            errors.append(f"{path}: CLI command set drift: {sorted(commands)}")
        if "text.splitlines().count(expected_conflicts) != 1" not in source:
            errors.append(f"{path}: receipt no longer verifies the exact conflict line")
    return errors


def check_measurement_runner(source: str) -> list[str]:
    errors: list[str] = []
    try:
        tree = ast.parse(source, filename=str(MEASUREMENT_RUNNER))
    except SyntaxError as exc:
        return [f"{MEASUREMENT_RUNNER}: cannot parse Python: {exc}"]
    forbidden_imports = {"anthropic", "http", "openai", "requests", "socket", "urllib"}
    for node in ast.walk(tree):
        roots: list[str] = []
        if isinstance(node, ast.Import):
            roots = [alias.name.split(".")[0] for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots = [node.module.split(".")[0]]
        for root in roots:
            if root in forbidden_imports:
                errors.append(
                    f"{MEASUREMENT_RUNNER}:{node.lineno}: forbidden API/network import {root}"
                )
        if isinstance(node, ast.Call):
            name = ""
            if isinstance(node.func, ast.Name):
                name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                name = node.func.attr
            if name in FORBIDDEN_SCANS:
                errors.append(
                    f"{MEASUREMENT_RUNNER}:{node.lineno}: forbidden ambient scan call {name}"
                )
            for keyword in node.keywords:
                if (
                    keyword.arg == "shell"
                    and isinstance(keyword.value, ast.Constant)
                    and keyword.value.value is True
                ):
                    errors.append(
                        f"{MEASUREMENT_RUNNER}:{node.lineno}: shell=True is forbidden"
                    )
    commands = {
        node.args[0].value
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "add_parser"
        and node.args
        and isinstance(node.args[0], ast.Constant)
        and isinstance(node.args[0].value, str)
    }
    if commands != MEASUREMENT_COMMANDS:
        errors.append(
            f"{MEASUREMENT_RUNNER}: measurement CLI command drift: {sorted(commands)}"
        )
    disabled = _assignment(tree, "DISABLED_FEATURES")
    required_disabled = {
        "shell_tool", "unified_exec", "apps", "plugins", "multi_agent",
        "computer_use", "browser_use", "in_app_browser", "image_generation",
    }
    if not isinstance(disabled, tuple) or not required_disabled.issubset(set(disabled)):
        errors.append(f"{MEASUREMENT_RUNNER}: contained disabled-feature set drift")
    for needle in (
        '"Logged in using ChatGPT"',
        '"AUTH_NOT_CHATGPT_SUBSCRIPTION"',
        '"codex_chatgpt_subscription"',
        '"api_spend_ceiling_usd": 0',
        '"api_spend_usd": 0',
        '"--execute-24-subscription-calls"',
        '"--plan-sha256"',
        '"--ignore-user-config"',
        '"--ephemeral"',
        '"read-only"',
    ):
        if needle not in source:
            errors.append(
                f"{MEASUREMENT_RUNNER}: missing containment text {needle!r}"
            )
    return errors


def check_measurement_assets(texts: dict[Path, str]) -> list[str]:
    errors: list[str] = []
    lock = _read_json(texts[SUITE_LOCK], str(SUITE_LOCK), errors)
    if lock is not None:
        if set(lock) != {"schema_version", "suite", "assets"}:
            errors.append("suite lock: root must be the closed three-field object")
        assets = lock.get("assets")
        expected_refs = {str(path) for path in LOCKED_MEASUREMENT_ASSETS}
        if not isinstance(assets, dict) or set(assets) != expected_refs:
            errors.append("suite lock: exact locked asset set drift")
        else:
            for path in LOCKED_MEASUREMENT_ASSETS:
                actual = hashlib.sha256(texts[path].encode("utf-8")).hexdigest()
                if assets[str(path)] != actual:
                    errors.append(f"suite lock: hash mismatch for {path}")

    call_plan = _read_json(texts[CALL_PLAN], str(CALL_PLAN), errors)
    if call_plan is not None:
        calls = call_plan.get("calls")
        if (
            call_plan.get("transport") != "codex_chatgpt_subscription"
            or call_plan.get("api_spend_ceiling_usd") != 0
            or not isinstance(calls, list)
            or len(calls) != 24
        ):
            errors.append("call plan: must remain exact 24-call subscription/USD-0")
        elif [row.get("sequence_index") for row in calls] != list(range(1, 25)):
            errors.append("call plan: sequence must remain contiguous 1..24")
        else:
            for offset in range(6):
                arms = [row.get("arm") for row in calls[offset * 4:(offset + 1) * 4]]
                expected = ["baseline", "treatment", "treatment", "baseline"]
                if offset % 2:
                    expected = ["treatment", "baseline", "baseline", "treatment"]
                if arms != expected:
                    errors.append(f"call plan: item block {offset + 1} lost ABBA/BAAB balance")

    scenarios = _read_json(texts[SCENARIOS], str(SCENARIOS), errors)
    heldout = _read_json(texts[HELDOUT_SET], str(HELDOUT_SET), errors)
    if scenarios is not None and heldout is not None:
        scenario_ids = [row.get("item_id") for row in scenarios.get("items", [])]
        heldout_ids = [row.get("item_id") for row in heldout.get("items", [])]
        if scenario_ids != [f"RCV-0{index}" for index in range(1, 7)]:
            errors.append("scenarios: exact six-item identity/order drift")
        if heldout_ids != scenario_ids:
            errors.append("heldout set: scenario identity/order drift")
    if "[REVIEW-TARGET-BINDING v1]" in texts[BASELINE_PROMPT]:
        errors.append("baseline prompt: treatment binding leaked into control")
    if "[REVIEW-TARGET-BINDING v1]" not in texts[TREATMENT_PROMPT]:
        errors.append("treatment prompt: binding marker requirement missing")
    return errors


def check_wiring(texts: dict[Path, str]) -> list[str]:
    errors: list[str] = []
    for path, needles in REQUIRED_TEXT.items():
        for needle in needles:
            if needle not in texts[path]:
                errors.append(f"{path}: missing load-bearing text {needle!r}")
    for path in NON_CONSUMERS:
        folded = texts[path].casefold()
        for token in FEATURE_TOKENS:
            if token.casefold() in folded:
                errors.append(f"{path}: forbidden #684 consumer/gate surface {token!r}")
    return errors


def check(root: Path = REPO_ROOT) -> list[str]:
    errors: list[str] = []
    texts: dict[Path, str] = {}
    for path in REQUIRED_FILES + NON_CONSUMERS:
        absolute = root / path
        if not absolute.is_file():
            errors.append(f"missing required file: {path}")
            texts[path] = ""
            continue
        texts[path] = absolute.read_text(encoding="utf-8")
    if errors:
        return errors
    errors.extend(check_contracts(texts))
    errors.extend(check_python(RUNTIME, texts[RUNTIME], runtime=True))
    errors.extend(check_python(SCORER, texts[SCORER], runtime=False))
    errors.extend(check_measurement_runner(texts[MEASUREMENT_RUNNER]))
    errors.extend(check_measurement_assets(texts))
    errors.extend(check_wiring(texts))
    return errors


def main() -> int:
    errors = check()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("#684 criteria binding: contracts, three consumers, blind wiring, held-out boundary ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
