#!/usr/bin/env python3
"""Check the static #681 advisory boundary and cross-file wiring.

The executable runtimes own row/report replay.  This guard pins the pieces that
can otherwise drift independently: the two closed schemas, exact vocabulary,
mandatory #667 replay, hermetic renderer/finalizer call graphs, documentation
pointers, and the honest UNMEASURED-with-no-measurement-row boundary.

Exit 0 on success, 1 on one or more integration errors, and 2 on invocation
errors.
"""
from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path, PurePath
from typing import Any

from jsonschema import Draft202012Validator


REPO_ROOT = Path(__file__).resolve().parent.parent

EVIDENCE_SCHEMA = Path("shared/contracts/evidence/evidence_row_v1_1.schema.json")
ADVISORY_SCHEMA = Path(
    "shared/contracts/human_subjects/content_coverage_advisory.schema.json"
)
EVIDENCE_RUNTIME = Path("scripts/evidence_rows.py")
ADVISORY_RUNTIME = Path("scripts/build_content_coverage_advisory.py")
CONTRACT_README = Path("shared/contracts/README.md")
EVIDENCE_PROTOCOL = Path("shared/references/evidence_row_protocol.md")
PACKET_PROTOCOL = Path("shared/references/submission_packet_manifest_protocol.md")
ADVISORY_PROTOCOL = Path(
    "shared/references/authority_content_coverage_advisory_protocol.md"
)
DESIGN_SPEC = Path(
    "docs/design/2026-08-09-681-authority-content-coverage-advisory-spec.md"
)
HELDOUT_ROOT = Path("evals/heldout")
HELDOUT_STATUS = HELDOUT_ROOT / "authority_content_coverage" / "README.md"
DEEP_SKILL = Path("deep-research/SKILL.md")
ETHICS_AGENT = Path("deep-research/agents/ethics_review_agent.md")
ARCHITECT = Path("deep-research/agents/research_architect_agent.md")
ARCHITECT_MIRROR = Path("agents/research_architect_agent.md")

ADVISORY_STATES = {
    "agent_extracted",
    "checked_no_match",
    "not_checked",
    "source_missing",
    "access_failed",
    "retrieval_failed",
}
REASON_CODES = {
    "ALL_EXPECTATIONS_APPEAR_COVERED",
    "EXPECTATION_NOT_LOCATED",
    "CONFLICTING_COVERAGE_OBSERVATIONS",
    "COVERAGE_CHECK_NOT_PERFORMED",
    "SESSION_CONTENT_NOT_PROVIDED",
    "SOURCE_ACCESS_FAILED",
    "SOURCE_RETRIEVAL_FAILED",
    "DETERMINISTIC_PACKET_GAP",
    "DETERMINISTIC_PACKET_CONFLICT",
    "WAIVER_OR_EXCEPTION_BOUNDARY",
    "EXTERNAL_DEPENDENCY",
    "APPLICABILITY_UNRESOLVED",
    "NO_PROFILED_STRUCTURED_EXPECTATIONS",
    "INSTITUTIONAL_ACCEPTANCE_REQUIRED",
}
BOUNDARY_KEYS = {
    "deterministic_status_unchanged",
    "submission_readiness_unchanged",
    "authorization_status_unchanged",
    "institutional_acceptance_unchanged",
    "adequacy_not_assessed",
}
FINAL_ROOT_KEYS = {
    "schema_version",
    "layer",
    "evaluation_status",
    "input_binding",
    "deterministic_status",
    "requirement_results",
    "excluded_requirements",
    "boundary",
    "report_digest",
}
ROW_ROOT_KEYS = {
    "schema_version",
    "surface",
    "row_id",
    "coverage_subject",
    "source",
    "anchor",
    "excerpt",
    "cache",
    "content_handling",
    "row_sha256",
}
DRAFT_ROOT_KEYS = {"schema_version", "layer", "judgments"}
DRAFT_JUDGMENT_KEYS = {
    "requirement_id",
    "expectation_pointer",
    "artifact_id",
    "coverage_check_state",
    "advisory_coverage_status",
    "document_locator",
    "quoted_anchor_encoded",
    "captured_at",
    "failure_state",
}
PERFORMED_STATUSES = {"DOCUMENTED", "NOT_LOCATED", "CONFLICTING"}
FAILURE_STATES = {"not_checked", "source_missing", "access_failed", "retrieval_failed"}
LOCATOR_KINDS = {"document", "page", "section", "paragraph", "other"}
FORBIDDEN_SCHEMA_FIELDS = {
    "verdict",
    "adequacy",
    "approval",
    "approval_status",
    "authorization_decision",
    "compliance",
    "confidence",
    "efficacy",
    "measurement_rows",
    "probability",
    "review_level",
    "score",
}
FORBIDDEN_IMPORT_ROOTS = {
    "anthropic",
    "http",
    "openai",
    "requests",
    "socket",
    "subprocess",
}
FORBIDDEN_IMPORT_PREFIXES = {"urllib.request", "urllib3"}
FORBIDDEN_SCAN_CALLS = {
    "fwalk",
    "glob",
    "iglob",
    "iterdir",
    "listdir",
    "rglob",
    "scandir",
    "walk",
}
FORBIDDEN_PURE_CALLS = FORBIDDEN_SCAN_CALLS | {
    "Popen",
    "check_call",
    "check_output",
    "connect",
    "create_connection",
    "open",
    "read_bytes",
    "read_text",
    "run",
    "system",
    "urlopen",
    "write_bytes",
    "write_text",
}


def _required_pointers(
    evidence_schema: PurePath = EVIDENCE_SCHEMA,
    advisory_schema: PurePath = ADVISORY_SCHEMA,
    advisory_runtime: PurePath = ADVISORY_RUNTIME,
    advisory_protocol: PurePath = ADVISORY_PROTOCOL,
) -> dict[Path, tuple[str, ...]]:
    """Build Markdown tokens from repository paths using portable separators."""
    return {
        CONTRACT_README: (
            evidence_schema.as_posix(),
            advisory_schema.as_posix(),
            advisory_runtime.as_posix(),
        ),
        EVIDENCE_PROTOCOL: (
            "evidence-row/1.1",
            "authority_profile_content_coverage",
            evidence_schema.as_posix(),
        ),
        PACKET_PROTOCOL: (
            "#681",
            "LLM-ADVISORY",
            "advisory_coverage_status",
        ),
        ADVISORY_PROTOCOL: (
            evidence_schema.as_posix(),
            advisory_schema.as_posix(),
            advisory_runtime.as_posix(),
            "validate_submission_packet_manifest",
            "evaluation_status=UNMEASURED",
            "never synthesize an \"unmeasured\" measurement JSON file",
        ),
        DESIGN_SPEC: (
            "evidence-row/1.1",
            "content-coverage-advisory/1.0",
            "LLM-ADVISORY",
            "evaluation_status = UNMEASURED",
            "There is no scored held-out row for #681",
        ),
        HELDOUT_STATUS: (
            "UNMEASURED — no scored held-out measurement row exists",
            "no `measurement-*.json`",
            "Passing them cannot create a score",
        ),
        DEEP_SKILL: (
            advisory_protocol.as_posix(),
            advisory_schema.as_posix(),
            evidence_schema.as_posix(),
            "LLM-ADVISORY",
            "UNMEASURED",
        ),
        ETHICS_AGENT: (
            advisory_protocol.as_posix(),
            advisory_schema.as_posix(),
            advisory_runtime.as_posix(),
            "validate_advisory(...)" ,
            "LLM-ADVISORY",
            "evaluation_status=UNMEASURED",
        ),
        ARCHITECT: (
            advisory_protocol.as_posix(),
            advisory_schema.as_posix(),
            advisory_runtime.as_posix(),
            "validate_advisory(...)" ,
            "LLM-ADVISORY",
            "evaluation_status=UNMEASURED",
        ),
        ARCHITECT_MIRROR: (
            advisory_protocol.as_posix(),
            advisory_schema.as_posix(),
            advisory_runtime.as_posix(),
            "validate_advisory(...)" ,
            "LLM-ADVISORY",
            "evaluation_status=UNMEASURED",
        ),
    }


REQUIRED_POINTERS = _required_pointers()


class DuplicateKeyError(ValueError):
    pass


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=_pairs,
        parse_constant=lambda token: (_ for _ in ()).throw(
            ValueError(f"non-finite JSON constant {token!r}")
        ),
    )
    if not isinstance(value, dict):
        raise ValueError("top level must be an object")
    return value


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
    try:
        row_schema = _load_json(root / EVIDENCE_SCHEMA)
        advisory_schema = _load_json(root / ADVISORY_SCHEMA)
        Draft202012Validator.check_schema(row_schema)
        Draft202012Validator.check_schema(advisory_schema)
    except (OSError, UnicodeError, ValueError, DuplicateKeyError) as exc:
        return [f"#681 schema load/check failed: {exc}"]
    except Exception as exc:  # jsonschema.SchemaError without coupling the guard API.
        return [f"#681 schema load/check failed: {exc}"]

    if row_schema.get("additionalProperties") is not False:
        errors.append(f"{EVIDENCE_SCHEMA}: root must be closed")
    if set(row_schema.get("required", ())) != ROW_ROOT_KEYS:
        errors.append(f"{EVIDENCE_SCHEMA}: root field set drifted")
    row_properties = row_schema.get("properties", {})
    if row_properties.get("schema_version", {}).get("const") != "evidence-row/1.1":
        errors.append(f"{EVIDENCE_SCHEMA}: schema version drifted")
    if row_properties.get("surface", {}).get("const") != (
        "authority_profile_content_coverage"
    ):
        errors.append(f"{EVIDENCE_SCHEMA}: advisory surface drifted")
    try:
        states = set(
            row_schema["$defs"]["excerpt"]["properties"]["state"]["enum"]
        )
    except (KeyError, TypeError):
        states = set()
    if states != ADVISORY_STATES:
        errors.append(f"{EVIDENCE_SCHEMA}: excerpt-state vocabulary drifted")
    if row_properties.get("cache", {}).get("properties") != {
        "status": {"const": "not_used"},
        "key_sha256": {"type": "null"},
    }:
        errors.append(f"{EVIDENCE_SCHEMA}: advisory cache must stay not_used/null")
    forbidden = _property_names(row_schema) & FORBIDDEN_SCHEMA_FIELDS
    if forbidden:
        errors.append(
            f"{EVIDENCE_SCHEMA}: forbidden determination fields: {sorted(forbidden)}"
        )

    if advisory_schema.get("additionalProperties") is not False:
        errors.append(f"{ADVISORY_SCHEMA}: root must be closed")
    if set(advisory_schema.get("required", ())) != FINAL_ROOT_KEYS:
        errors.append(f"{ADVISORY_SCHEMA}: root field set drifted")
    properties = advisory_schema.get("properties", {})
    expected_consts = {
        "schema_version": "content-coverage-advisory/1.0",
        "layer": "LLM-ADVISORY",
        "evaluation_status": "UNMEASURED",
    }
    for key, expected in expected_consts.items():
        if properties.get(key, {}).get("const") != expected:
            errors.append(f"{ADVISORY_SCHEMA}: {key} must equal {expected!r}")
    try:
        reasons = set(advisory_schema["$defs"]["reason_code"]["enum"])
    except (KeyError, TypeError):
        reasons = set()
    if reasons != REASON_CODES:
        errors.append(f"{ADVISORY_SCHEMA}: reason vocabulary drifted")
    boundary = properties.get("boundary", {})
    if set(boundary.get("required", ())) != BOUNDARY_KEYS:
        errors.append(f"{ADVISORY_SCHEMA}: boundary field set drifted")
    for key in BOUNDARY_KEYS:
        if boundary.get("properties", {}).get(key, {}).get("const") is not True:
            errors.append(f"{ADVISORY_SCHEMA}: boundary.{key} must remain true")
    forbidden = _property_names(advisory_schema) & FORBIDDEN_SCHEMA_FIELDS
    if forbidden:
        errors.append(
            f"{ADVISORY_SCHEMA}: forbidden determination fields: {sorted(forbidden)}"
        )

    try:
        draft = advisory_schema["$defs"]["advisory_draft"]
        judgment = advisory_schema["$defs"]["advisory_draft_judgment"]
    except (KeyError, TypeError):
        errors.append(f"{ADVISORY_SCHEMA}: missing closed advisory draft definitions")
        return errors
    if draft.get("additionalProperties") is not False:
        errors.append(f"{ADVISORY_SCHEMA}: advisory draft root must be closed")
    if set(draft.get("required", ())) != DRAFT_ROOT_KEYS or set(
        draft.get("properties", {})
    ) != DRAFT_ROOT_KEYS:
        errors.append(f"{ADVISORY_SCHEMA}: advisory draft root fields drifted")
    if draft.get("properties", {}).get("schema_version", {}).get("const") != (
        "content-coverage-advisory-draft/1.0"
    ):
        errors.append(f"{ADVISORY_SCHEMA}: advisory draft version drifted")
    if draft.get("properties", {}).get("layer", {}).get("const") != "LLM-ADVISORY":
        errors.append(f"{ADVISORY_SCHEMA}: advisory draft layer drifted")
    if judgment.get("additionalProperties") is not False:
        errors.append(f"{ADVISORY_SCHEMA}: draft judgment must be closed")
    if set(judgment.get("required", ())) != DRAFT_JUDGMENT_KEYS or set(
        judgment.get("properties", {})
    ) != DRAFT_JUDGMENT_KEYS:
        errors.append(f"{ADVISORY_SCHEMA}: draft judgment fields drifted")
    if set(
        judgment.get("properties", {})
        .get("coverage_check_state", {})
        .get("enum", ())
    ) != {"performed", "not_checked"}:
        errors.append(f"{ADVISORY_SCHEMA}: draft check-state vocabulary drifted")
    status_choices = {
        token
        for branch in judgment.get("properties", {})
        .get("advisory_coverage_status", {})
        .get("oneOf", ())
        for token in branch.get("enum", ())
    }
    if status_choices != PERFORMED_STATUSES:
        errors.append(f"{ADVISORY_SCHEMA}: draft status vocabulary drifted")
    failure_choices = {
        token
        for branch in judgment.get("properties", {})
        .get("failure_state", {})
        .get("oneOf", ())
        for token in branch.get("enum", ())
    }
    if failure_choices != FAILURE_STATES:
        errors.append(f"{ADVISORY_SCHEMA}: draft failure vocabulary drifted")
    if set(
        judgment.get("properties", {})
        .get("document_locator", {})
        .get("properties", {})
        .get("kind", {})
        .get("enum", ())
    ) != LOCATOR_KINDS:
        errors.append(f"{ADVISORY_SCHEMA}: document-locator vocabulary drifted")

    validator = Draft202012Validator(
        advisory_schema, format_checker=Draft202012Validator.FORMAT_CHECKER
    ).evolve(schema=draft)
    sample = {
        "schema_version": "content-coverage-advisory-draft/1.0",
        "layer": "LLM-ADVISORY",
        "judgments": [
            {
                "requirement_id": "fixture.requirement",
                "expectation_pointer": "/profiles/0/requirements/0/structured_expectations/0",
                "artifact_id": "fixture.artifact",
                "coverage_check_state": "performed",
                "advisory_coverage_status": "DOCUMENTED",
                "document_locator": {"kind": "section", "value": "Consent"},
                "quoted_anchor_encoded": "bounded%20quote",
                "captured_at": "2026-08-09T12:00:00Z",
                "failure_state": None,
            }
        ],
    }
    if list(validator.iter_errors(sample)):
        errors.append(f"{ADVISORY_SCHEMA}: canonical draft sample no longer validates")
    invalid_samples: list[dict[str, Any]] = []
    for mutation in (
        "extra",
        "missing_captured_at",
        "performed_null_status",
        "performed_failure",
        "documented_null_time",
        "not_located_quote",
        "not_located_time",
        "not_checked_status",
        "not_checked_quote",
        "not_checked_time",
        "not_checked_null_failure",
    ):
        candidate = json.loads(json.dumps(sample))
        row = candidate["judgments"][0]
        if mutation == "extra":
            row["extra"] = True
        elif mutation == "missing_captured_at":
            row.pop("captured_at")
        elif mutation == "performed_null_status":
            row["advisory_coverage_status"] = None
        elif mutation == "performed_failure":
            row["failure_state"] = "not_checked"
        elif mutation == "documented_null_time":
            row["captured_at"] = None
        elif mutation.startswith("not_located"):
            row.update(
                {
                    "advisory_coverage_status": "NOT_LOCATED",
                    "quoted_anchor_encoded": "",
                    "captured_at": None,
                }
            )
            if mutation == "not_located_quote":
                row["quoted_anchor_encoded"] = "unexpected"
            else:
                row["captured_at"] = "2026-08-09T12:00:00Z"
        else:
            row.update(
                {
                    "coverage_check_state": "not_checked",
                    "advisory_coverage_status": None,
                    "quoted_anchor_encoded": "",
                    "captured_at": None,
                    "failure_state": "not_checked",
                }
            )
            if mutation == "not_checked_status":
                row["advisory_coverage_status"] = "DOCUMENTED"
            elif mutation == "not_checked_quote":
                row["quoted_anchor_encoded"] = "unexpected"
            elif mutation == "not_checked_time":
                row["captured_at"] = "2026-08-09T12:00:00Z"
            else:
                row["failure_state"] = None
        invalid_samples.append(candidate)
    if any(not list(validator.iter_errors(candidate)) for candidate in invalid_samples):
        errors.append(f"{ADVISORY_SCHEMA}: draft conditional matrix was weakened")
    return errors


def _call_name(node: ast.Call) -> str | None:
    if isinstance(node.func, ast.Name):
        return node.func.id
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    return None


def _function_map(tree: ast.Module) -> dict[str, ast.FunctionDef | ast.AsyncFunctionDef]:
    return {
        node.name: node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


def _assignment_node(tree: ast.Module, name: str) -> ast.AST | None:
    for node in tree.body:
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        if any(isinstance(target, ast.Name) and target.id == name for target in targets):
            return node.value
    return None


def _literal_set(node: ast.AST | None) -> set[Any] | None:
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id in {"set", "frozenset"}
        and len(node.args) == 1
        and not node.keywords
    ):
        node = node.args[0]
    try:
        value = ast.literal_eval(node) if node is not None else None
    except (ValueError, TypeError):
        return None
    if not isinstance(value, (set, frozenset, list, tuple)):
        return None
    return set(value)


def _reachable_nodes(
    functions: dict[str, ast.FunctionDef | ast.AsyncFunctionDef], starts: set[str]
) -> list[ast.AST]:
    pending = list(starts)
    seen: set[str] = set()
    nodes: list[ast.AST] = []
    while pending:
        name = pending.pop()
        if name in seen or name not in functions:
            continue
        seen.add(name)
        function = functions[name]
        nodes.append(function)
        for child in ast.walk(function):
            if isinstance(child, ast.Call):
                called = _call_name(child)
                if called in functions and called not in seen:
                    pending.append(called)
    return nodes


def _import_errors(path: Path, tree: ast.Module) -> list[str]:
    errors: list[str] = []
    for node in ast.walk(tree):
        names: list[str] = []
        if isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module:
            names = [node.module]
        for name in names:
            if (
                name.split(".", 1)[0] in FORBIDDEN_IMPORT_ROOTS
                or any(name == prefix or name.startswith(prefix + ".") for prefix in FORBIDDEN_IMPORT_PREFIXES)
            ):
                errors.append(f"{path}: forbidden model/network/process import {name}")
    return errors


def _runtime_ast_errors(root: Path) -> list[str]:
    errors: list[str] = []
    trees: dict[Path, ast.Module] = {}
    for relative in (EVIDENCE_RUNTIME, ADVISORY_RUNTIME):
        try:
            trees[relative] = ast.parse(
                (root / relative).read_text(encoding="utf-8"), filename=str(relative)
            )
        except (OSError, UnicodeError, SyntaxError) as exc:
            errors.append(f"{relative}: cannot parse: {exc}")
    if errors:
        return errors

    evidence_tree = trees[EVIDENCE_RUNTIME]
    evidence_functions = _function_map(evidence_tree)
    if "build_advisory" not in evidence_functions:
        errors.append(f"{EVIDENCE_RUNTIME}: missing public build_advisory")
    for name, literal in (
        ("ADVISORY_SCHEMA_VERSION", "evidence-row/1.1"),
        ("ADVISORY_SURFACE", "authority_profile_content_coverage"),
    ):
        if not any(
            isinstance(node, ast.Assign)
            and any(isinstance(target, ast.Name) and target.id == name for target in node.targets)
            and isinstance(node.value, ast.Constant)
            and node.value.value == literal
            for node in evidence_tree.body
        ):
            errors.append(f"{EVIDENCE_RUNTIME}: {name} must equal {literal!r}")

    runtime_tree = trees[ADVISORY_RUNTIME]
    errors.extend(_import_errors(ADVISORY_RUNTIME, runtime_tree))
    functions = _function_map(runtime_tree)
    required = {"finalize_advisory", "validate_advisory", "render_advisory", "main"}
    missing = required - set(functions)
    if missing:
        errors.append(f"{ADVISORY_RUNTIME}: missing public functions {sorted(missing)}")
        return errors

    for name, expected in (
        ("DRAFT_SCHEMA_VERSION", "content-coverage-advisory-draft/1.0"),
        ("REPORT_SCHEMA_VERSION", "content-coverage-advisory/1.0"),
        ("LAYER", "LLM-ADVISORY"),
        ("EVALUATION_STATUS", "UNMEASURED"),
    ):
        node = _assignment_node(runtime_tree, name)
        if not isinstance(node, ast.Constant) or node.value != expected:
            errors.append(f"{ADVISORY_RUNTIME}: {name} must equal {expected!r}")
    for name, expected in (
        ("PERFORMED_STATUSES", PERFORMED_STATUSES),
        ("FAILURE_STATES", FAILURE_STATES),
        ("LOCATOR_KINDS", LOCATOR_KINDS),
        ("REASON_CODES", REASON_CODES),
    ):
        if _literal_set(_assignment_node(runtime_tree, name)) != expected:
            errors.append(f"{ADVISORY_RUNTIME}: {name} vocabulary drifted")

    draft_validator = functions.get("_validate_draft")
    if draft_validator is None:
        errors.append(f"{ADVISORY_RUNTIME}: missing manual _validate_draft parity gate")
    else:
        fields: set[Any] | None = None
        for node in ast.walk(draft_validator):
            if isinstance(node, ast.Assign) and any(
                isinstance(target, ast.Name) and target.id == "fields"
                for target in node.targets
            ):
                fields = _literal_set(node.value)
                break
        if fields != DRAFT_JUDGMENT_KEYS:
            errors.append(f"{ADVISORY_RUNTIME}: manual draft judgment fields drifted")
        manual = ast.unparse(draft_validator)
        conditional_markers = (
            "if check_state == 'performed':",
            "if failure is not None:",
            "if status in {'DOCUMENTED', 'CONFLICTING'} and (not decoded):",
            "if status == 'NOT_LOCATED' and decoded:",
            "captured_at = _timestamp(captured_at,",
            "'NOT_LOCATED requires null'",
            "if status is not None:",
            "failure = _enum(failure,",
            "'not_checked requires an empty anchor'",
            "'not_checked requires null'",
        )
        if any(marker not in manual for marker in conditional_markers):
            errors.append(
                f"{ADVISORY_RUNTIME}: manual draft conditional matrix drifted"
            )

    for name in ("finalize_advisory", "validate_advisory"):
        parameters = {
            argument.arg
            for argument in (
                functions[name].args.posonlyargs
                + functions[name].args.args
                + functions[name].args.kwonlyargs
            )
        }
        for required_parameter in {
            "inventory",
            "packet_root",
            "context",
            "registry",
            "resolved",
            "manifest",
            "session_sources",
        }:
            if required_parameter not in parameters:
                errors.append(
                    f"{ADVISORY_RUNTIME}.{name}: missing {required_parameter} replay input"
                )

    replay_nodes = _reachable_nodes(
        functions, {"finalize_advisory", "validate_advisory"}
    )
    replay_calls = {
        called
        for node in replay_nodes
        for child in ast.walk(node)
        if isinstance(child, ast.Call)
        if (called := _call_name(child)) is not None
    }
    if "validate_submission_packet_manifest" not in replay_calls:
        errors.append(
            f"{ADVISORY_RUNTIME}: finalize/validate do not reach exact #667 replay"
        )

    pure_nodes = _reachable_nodes(
        functions, {"finalize_advisory", "validate_advisory", "render_advisory"}
    )
    for node in pure_nodes:
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                called = _call_name(child)
                if called in FORBIDDEN_PURE_CALLS:
                    errors.append(
                        f"{ADVISORY_RUNTIME}: pure advisory path reaches forbidden {called}()"
                    )
    for child in ast.walk(runtime_tree):
        if isinstance(child, ast.Call) and _call_name(child) in FORBIDDEN_SCAN_CALLS:
            errors.append(
                f"{ADVISORY_RUNTIME}: forbidden ambient scan {_call_name(child)}()"
            )
    return errors


def _documentation_errors(root: Path) -> list[str]:
    errors: list[str] = []
    for relative, tokens in REQUIRED_POINTERS.items():
        try:
            text = (root / relative).read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append(f"{relative}: cannot read: {exc}")
            continue
        compact = " ".join(text.split())
        for token in tokens:
            if " ".join(token.split()) not in compact:
                errors.append(f"{relative}: missing #681 token {token!r}")
    try:
        if (root / ARCHITECT).read_bytes() != (root / ARCHITECT_MIRROR).read_bytes():
            errors.append(f"{ARCHITECT_MIRROR}: architect mirror drift")
    except OSError as exc:
        errors.append(f"architect mirror cannot be compared: {exc}")
    return errors


def _measurement_errors(root: Path) -> list[str]:
    errors: list[str] = []
    heldout = root / HELDOUT_ROOT
    if not heldout.is_dir():
        return [f"{HELDOUT_ROOT}: missing held-out registry root"]
    needles = (
        '"authority_profile_content_coverage"',
        '"content-coverage-advisory/1.0"',
    )
    for path in sorted(heldout.rglob("*.json")):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append(f"{path.relative_to(root)}: cannot inspect measurement boundary: {exc}")
            continue
        if any(needle in text for needle in needles):
            errors.append(
                f"{path.relative_to(root)}: fictitious #681 held-out measurement row exists while UNMEASURED"
            )
    return errors


def run_checks(root: Path = REPO_ROOT) -> list[str]:
    """Return deterministic integration errors for a repository tree."""

    errors = [
        *_schema_errors(root),
        *_runtime_ast_errors(root),
        *_documentation_errors(root),
        *_measurement_errors(root),
    ]
    return sorted(set(errors))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check #681 authority content-coverage advisory integration",
        allow_abbrev=False,
    )
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    return parser


def main(argv: list[str] | None = None) -> int:
    try:
        args = _parser().parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)
    errors = run_checks(args.root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Content-coverage advisory integration check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
