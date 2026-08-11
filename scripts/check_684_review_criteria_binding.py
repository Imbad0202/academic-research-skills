#!/usr/bin/env python3
"""Static integration guard for #684 review-criteria consumer binding."""
from __future__ import annotations

import ast
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
FORMATIVE = Path("academic-paper/agents/structure_architect_agent.md")
INTERNAL = Path("academic-paper/agents/peer_reviewer_agent.md")
CANONICAL = Path("academic-paper-reviewer/references/reviewer_sprint_prompt_source.md")
SYNTH = Path("academic-paper-reviewer/agents/editorial_synthesizer_agent.md")
ORCHESTRATOR = Path("academic-pipeline/agents/pipeline_orchestrator_agent.md")
STATE = Path("academic-pipeline/agents/state_tracker_agent.md")
HANDOFFS = Path("shared/handoff_schemas.md")
MEASUREMENT = Path("evals/heldout/review_criteria_constructive_value/measurement_plan.md")
ADJUDICATION_SCHEMA = Path("evals/heldout/review_criteria_constructive_value/paired_adjudication.schema.json")
SUITE_REGISTRY = Path("evals/heldout/suite_registry.json")

REQUIRED_FILES = (
    SPEC,
    BINDING_SCHEMA,
    FINDINGS_SCHEMA,
    PROTOCOL,
    RUNTIME,
    SCORER,
    FORMATIVE,
    INTERNAL,
    CANONICAL,
    SYNTH,
    ORCHESTRATOR,
    STATE,
    HANDOFFS,
    MEASUREMENT,
    ADJUDICATION_SCHEMA,
    SUITE_REGISTRY,
)

CLI_COMMANDS = {"init", "marker", "record", "validate", "validate-findings"}
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
        "at least two fresh isolated replicates",
        "No composite score",
        "PRE-REGISTERED / NOT RUN",
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
    for path in (BINDING_SCHEMA, FINDINGS_SCHEMA, ADJUDICATION_SCHEMA):
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
