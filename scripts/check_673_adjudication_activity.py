#!/usr/bin/env python3
"""Deterministic static integration guard for #673 adjudication activity.

This checker deliberately does not execute the recorder.  It pins the closed
schemas, exact renderer language, hermetic CLI surface, terminal-first wiring,
terminal source authority, and the advisory-only/non-consumer boundary that
could otherwise drift independently of the focused runtime tests.
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


REPO_ROOT = Path(__file__).resolve().parent.parent

SPEC = Path("docs/design/2026-08-10-673-cross-run-adjudication-activity-spec.md")
INPUT_SCHEMA = Path(
    "shared/contracts/activity/adjudication_activity_input.schema.json"
)
STORE_SCHEMA = Path(
    "shared/contracts/activity/adjudication_activity_store.schema.json"
)
RUNTIME = Path("scripts/adjudication_activity.py")

STATE_TRACKER = Path("academic-pipeline/agents/state_tracker_agent.md")
ORCHESTRATOR = Path("academic-pipeline/agents/pipeline_orchestrator_agent.md")
PIPELINE_SKILL = Path("academic-pipeline/SKILL.md")
STATE_MACHINE = Path("academic-pipeline/references/pipeline_state_machine.md")
PROCESS_SUMMARY = Path("academic-pipeline/references/process_summary_protocol.md")
COMPLIANCE = Path("shared/compliance_checkpoint_protocol.md")
HANDOFFS = Path("shared/handoff_schemas.md")

FROZEN_FILES = (SPEC, INPUT_SCHEMA, STORE_SCHEMA)
WIRING_FILES = (
    STATE_TRACKER,
    ORCHESTRATOR,
    PIPELINE_SKILL,
    STATE_MACHINE,
    PROCESS_SUMMARY,
    COMPLIANCE,
    HANDOFFS,
)
NON_CONSUMER_GLOBS = (
    "academic-paper/**/*.md",
    "academic-paper-reviewer/**/*.md",
    "academic-pipeline/**/*.md",
    "shared/**/*.md",
    "shared/contracts/**/*.json",
)
EXECUTION_GLOBS = (
    "scripts/**/*.py",
    "scripts/**/*.sh",
    "hooks/**/*.sh",
    "tools/**/*.sh",
    ".github/**/*.sh",
    ".github/workflows/*.yml",
    ".github/workflows/*.yaml",
)
PYTHON_EXECUTION_WHITELIST = {
    RUNTIME,
    Path("scripts/check_673_adjudication_activity.py"),
    Path("scripts/test_adjudication_activity.py"),
    Path("scripts/test_check_673_adjudication_activity.py"),
    # Prompt-size regression test names the bounded #673 documentation block;
    # it neither imports nor executes the activity runtime.
    Path("scripts/test_v3_6_7_phase_6_6.py"),
}

LIMITATION_SENTENCE = (
    "This records explicit adjudication activity only. It cannot determine "
    "correctness, attentiveness, engagement, or whether human ownership is real; "
    "genuine agreement and non-review can produce the same history."
)
ADVISORY_SENTENCE = (
    "This series is advisory only; it never gates, blocks, scores, or changes any "
    "verdict."
)
COVERAGE_LINE = (
    "Coverage: only successfully retained records in this explicitly selected "
    "store are shown; runs without this store selection or whose append failed "
    "are not represented."
)

STAGES = [
    "pipeline_stage_1",
    "pipeline_stage_2",
    "pipeline_stage_2_5",
    "pipeline_stage_3",
    "pipeline_stage_3_prime",
    "pipeline_stage_4",
    "pipeline_stage_4_prime",
    "pipeline_stage_4_5",
    "pipeline_stage_5",
    "pipeline_stage_6",
]

CLI_COMMANDS = {
    "init-store",
    "build-input",
    "append-run",
    "render",
    "validate",
    "delete-runs",
    "delete-store",
}
BUILD_INPUT_OPTIONS = {"--state", "--artifact-root", "--store-id", "--output"}

FORBIDDEN_IMPORT_ROOTS = {
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
FORBIDDEN_SCAN_CALLS = {
    "glob",
    "iglob",
    "iterdir",
    "listdir",
    "rglob",
    "scandir",
    "walk",
}

FEATURE_RE = re.compile(
    r"adjudication[_ -]activity|ADJUDICATION-ACTIVITY|activity[_ -](?:store|count)|"
    r"overturn_count|adjudication_count|selected_retained_eligible_run_count",
    re.IGNORECASE,
)
CONSUMER_RE = re.compile(
    r"\b(?:input|consum(?:e|es|ed|ing)|consult|read|load|require|gate|block|score|rank|selector|select|"
    r"determine|change|affect|dispatch|prompt|passport|handoff|process record|"
    r"verdict)\b",
    re.IGNORECASE,
)
NEGATION_RE = re.compile(
    r"\b(?:never|not|no|cannot|must not|do not|does not|isn't|aren't|excluded|"
    r"prohibited|forbidden|unauthorized|advisory only|observability only)\b",
    re.IGNORECASE,
)
CLAUSE_SPLIT_RE = re.compile(
    r"\s*(?:;|；)\s*|\s*,?\s*\b(?:but|however|and)\b\s*|\s*(?:，?但|，?然而)\s*",
    re.IGNORECASE,
)
USER_RENDER_READ_RE = re.compile(
    r"\busers?\s+(?:may|can)\s+(?:read|view)\b.*\brender(?:er|ed)?\s+output\b",
    re.IGNORECASE,
)
RUNTIME_IMPORT_RE = re.compile(
    r"(?:from\s+scripts\.adjudication_activity\s+import\b|"
    r"from\s+scripts\s+import\s+adjudication_activity\b|"
    r"import\s+(?:scripts\.)?adjudication_activity\b)"
)


class DuplicateKeyError(ValueError):
    """Raised when strict JSON loading observes a duplicate object key."""


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise DuplicateKeyError(f"duplicate JSON key {key!r}")
        value[key] = item
    return value


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


def check_schema_contracts(input_schema: dict[str, Any], store_schema: dict[str, Any]) -> list[str]:
    """Return closed-schema errors for the cross-file frozen invariants."""
    errors: list[str] = []
    for label, schema in (("input", input_schema), ("store", store_schema)):
        try:
            Draft202012Validator.check_schema(schema)
        except Exception as exc:  # SchemaError varies across jsonschema releases.
            errors.append(f"{label} schema is not Draft 2020-12 valid: {exc}")
        if schema.get("additionalProperties") is not False:
            errors.append(f"{label} schema root is not closed")
        stage_enum = schema.get("$defs", {}).get("pipeline_stage", {}).get("enum")
        if stage_enum != STAGES:
            errors.append(f"{label} schema full Stage 1..6 enum drifted")

    input_text = json.dumps(input_schema, ensure_ascii=False, sort_keys=True)
    store_text = json.dumps(store_schema, ensure_ascii=False, sort_keys=True)
    if "source_stage" in input_text or "source_stage" in store_text:
        errors.append("retired source_stage reappeared in an activity schema")
    if "pipeline_stage_0" in input_text or "pipeline_stage_0" in store_text:
        errors.append("retired pipeline_stage_0 reappeared in an activity schema")

    forbidden_input_properties = {
        "events",
        "event_count",
        "adjudication_count",
        "overturn_count",
        "overturn",
        "rate",
        "score",
        "target",
        "threshold",
    }
    root_properties = set(input_schema.get("properties", {}))
    leaked = sorted(root_properties & forbidden_input_properties)
    if leaked:
        errors.append(f"input schema accepts caller-derived fields: {', '.join(leaked)}")

    artifact_hashes = store_schema.get("$defs", {}).get("source_receipt", {}).get(
        "properties", {}
    ).get("artifact_sha256s", {})
    if artifact_hashes.get("uniqueItems") is True:
        errors.append("store artifact_sha256s illegally reject legitimate repeated hashes")

    run_record = store_schema.get("$defs", {}).get("run_record", {})
    if run_record.get("properties", {}).get("sealed", {}).get("const") is not True:
        errors.append("store run records are no longer sealed")
    return errors


def _call_name(node: ast.Call) -> str | None:
    if isinstance(node.func, ast.Name):
        return node.func.id
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    return None


def _parser_surface(tree: ast.AST) -> tuple[set[str], dict[str, set[str]]]:
    """Extract argparse add_parser commands and long options by parser variable."""
    commands: set[str] = set()
    parser_vars: dict[str, str] = {}
    options: dict[str, set[str]] = {}
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        value = node.value
        if not isinstance(value, ast.Call) or _call_name(value) != "add_parser":
            continue
        if not value.args or not isinstance(value.args[0], ast.Constant):
            continue
        command = value.args[0].value
        if not isinstance(command, str):
            continue
        commands.add(command)
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        for target in targets:
            if isinstance(target, ast.Name):
                parser_vars[target.id] = command
                options.setdefault(command, set())
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or _call_name(node) != "add_argument":
            continue
        if not isinstance(node.func, ast.Attribute) or not isinstance(node.func.value, ast.Name):
            continue
        command = parser_vars.get(node.func.value.id)
        if command is None:
            continue
        for arg in node.args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                if arg.value.startswith("--"):
                    options[command].add(arg.value)
    return commands, options


def _subscript_key(node: ast.AST) -> str | None:
    if not isinstance(node, ast.Subscript):
        return None
    value = node.slice
    if isinstance(value, ast.Constant) and isinstance(value.value, str):
        return value.value
    return None


def _authority_ast_checks(
    functions: dict[str, ast.FunctionDef | ast.AsyncFunctionDef],
) -> list[str]:
    """Pin the state-inventory read and exact manifest-source comparison."""
    errors: list[str] = []
    validator = functions.get("_validate_manifest_authority")
    if validator is None:
        return ["runtime missing _validate_manifest_authority"]

    inventory_names: set[str] = set()
    for node in ast.walk(validator):
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        value = node.value
        if not (
            isinstance(value, ast.Call)
            and isinstance(value.func, ast.Attribute)
            and isinstance(value.func.value, ast.Name)
            and value.func.value.id == "state"
            and value.func.attr == "get"
            and value.args
            and isinstance(value.args[0], ast.Constant)
            and value.args[0].value == "adjudication_activity_sources"
        ):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        inventory_names.update(
            target.id for target in targets if isinstance(target, ast.Name)
        )
    if not inventory_names:
        errors.append(
            "_validate_manifest_authority does not read state adjudication_activity_sources"
        )

    exact_compare = False
    for node in ast.walk(validator):
        if not (
            isinstance(node, ast.If)
            and isinstance(node.test, ast.Compare)
            and len(node.test.ops) == 1
            and isinstance(node.test.ops[0], ast.NotEq)
            and len(node.test.comparators) == 1
            and any(isinstance(child, ast.Raise) for child in ast.walk(node))
        ):
            continue
        sides = (node.test.left, node.test.comparators[0])
        has_inventory = any(
            isinstance(side, ast.Name) and side.id in inventory_names for side in sides
        )
        has_manifest_sources = any(
            isinstance(side, ast.Subscript)
            and isinstance(side.value, ast.Name)
            and side.value.id == "manifest"
            and _subscript_key(side) == "sources"
            for side in sides
        )
        if has_inventory and has_manifest_sources:
            exact_compare = True
            break
    if not exact_compare:
        errors.append(
            "_validate_manifest_authority does not exact-compare sealed inventory "
            "with manifest sources"
        )

    build = functions.get("_cmd_build")
    if build is None:
        errors.append("runtime missing build-input handler _cmd_build")
    else:
        used_args = {
            node.attr
            for node in ast.walk(build)
            if isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id == "args"
        }
        allowed_args = {"state", "artifact_root", "store_id", "output"}
        indirect_args = any(
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in {"getattr", "vars"}
            and node.args
            and isinstance(node.args[0], ast.Name)
            and node.args[0].id == "args"
            for node in ast.walk(build)
        )
        unexpected = sorted(used_args - allowed_args)
        if unexpected or indirect_args or used_args != allowed_args:
            errors.append(
                "build-input handler reads caller source/hash arguments: "
                + (", ".join(unexpected) if unexpected else "indirect or incomplete args")
            )
    return errors


def check_runtime_text(text: str) -> list[str]:
    """Check the hermetic runtime and exact public surface without executing it."""
    errors: list[str] = []
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        return [f"runtime is not valid Python: {exc}"]

    commands, options = _parser_surface(tree)
    if commands != CLI_COMMANDS:
        errors.append(
            "CLI command surface drifted: expected "
            f"{sorted(CLI_COMMANDS)}, got {sorted(commands)}"
        )
    build_options = options.get("build-input", set())
    if build_options != BUILD_INPUT_OPTIONS:
        errors.append(
            "build-input must accept only explicit state/artifact-root/store-id/output; "
            f"got {sorted(build_options)}"
        )

    functions = {
        node.name: node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    errors.extend(_authority_ast_checks(functions))
    seal_function = functions.get("seal_terminal_inventory")
    if seal_function is None:
        errors.append("runtime missing deterministic seal_terminal_inventory entry point")
    else:
        positional = [
            *seal_function.args.posonlyargs,
            *seal_function.args.args,
        ]
        if [argument.arg for argument in positional] != [
            "state_path",
            "artifact_root",
            "pending_bindings",
        ] or seal_function.args.defaults:
            errors.append(
                "seal_terminal_inventory must require exactly "
                "(state_path, artifact_root, pending_bindings)"
            )

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names = [alias.name.split(".", 1)[0] for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            names = [(node.module or "").split(".", 1)[0]]
        else:
            names = []
        for name in names:
            if name in FORBIDDEN_IMPORT_ROOTS:
                errors.append(f"runtime imports forbidden model/network/clock/process module {name}")
        if isinstance(node, ast.Call):
            name = _call_name(node)
            if name in FORBIDDEN_SCAN_CALLS:
                errors.append(f"runtime performs forbidden ambient scan {name}()")
            if name == "getenv":
                errors.append("runtime reads environment state")
        if isinstance(node, ast.Attribute) and node.attr == "environ":
            errors.append("runtime reads environment state")

    for exact in (LIMITATION_SENTENCE, ADVISORY_SENTENCE, COVERAGE_LINE):
        if exact not in text:
            errors.append(f"runtime missing exact renderer text: {exact}")
    for authority in ("run_id", "adjudication_activity_sources", "sealed"):
        if authority not in text:
            errors.append(f"runtime missing terminal source authority token {authority}")
    return sorted(set(errors))


def _has_all(text: str, needles: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return all(needle.lower() in lowered for needle in needles)


def check_spec_text(text: str) -> list[str]:
    """Pin the three exact public renderer strings in the frozen contract."""
    return [
        f"frozen spec missing exact renderer text: {exact}"
        for exact in (LIMITATION_SENTENCE, ADVISORY_SENTENCE, COVERAGE_LINE)
        if exact not in text
    ]


def check_retired_tokens(path: Path, text: str) -> list[str]:
    """Reject the two retired stage spellings across the production surface."""
    return [
        f"{path}: retired token {token} reappeared"
        for token in ("source_stage", "pipeline_stage_0")
        if token in text
    ]


def check_wiring_texts(texts: dict[Path, str]) -> list[str]:
    """Pin producer, terminal-first, exact-authority, and advisory integration."""
    errors: list[str] = []
    state = texts.get(STATE_TRACKER, "")
    if not _has_all(
        state,
        (
            "run_id",
            "pending_adjudication_activity_bindings",
            "adjudication_activity_sources",
            "sealed",
            "five",
        ),
    ):
        errors.append("state tracker missing pending producer wiring or sealed five-row authority")

    orchestrator = texts.get(ORCHESTRATOR, "")
    terminal_bundle = "\n".join(
        texts.get(path, "")
        for path in (ORCHESTRATOR, PIPELINE_SKILL, STATE_MACHINE, PROCESS_SUMMARY)
    )
    for needle in (
        "seal_terminal_inventory",
        "build-input",
        "append-run",
        "render",
        "post-terminal",
        "best-effort",
    ):
        if needle.lower() not in terminal_bundle.lower():
            errors.append(f"post-terminal wiring missing {needle}")
    first = terminal_bundle.lower().find("terminal transition")
    seal = terminal_bundle.lower().find("seal_terminal_inventory")
    if first < 0 or seal < 0 or first > seal:
        errors.append("terminal-first order is not explicit before inventory sealing")
    if not _has_all(orchestrator, ("already", "terminal", "advisory")):
        errors.append("orchestrator does not preserve the already-durable terminal outcome")

    authority_bundle = state + "\n" + orchestrator
    if not _has_all(
        authority_bundle,
        ("run_id", "adjudication_activity_sources", "exact", "sealed", "build-input"),
    ):
        errors.append("run_id plus sealed adjudication_activity_sources authority drifted")

    compliance = texts.get(COMPLIANCE, "")
    if not _has_all(
        compliance,
        ("compliance_override_action_receipt", "best-effort", "after"),
    ):
        errors.append("compliance producer lacks paired post-action best-effort receipt wiring")

    handoffs = texts.get(HANDOFFS, "")
    if not _has_all(handoffs, ("adjudication activity", "never", "material passport", "handoff")):
        errors.append("handoff contract lacks explicit activity-store non-consumer boundary")
    process_summary = texts.get(PROCESS_SUMMARY, "")
    if not (
        FEATURE_RE.search(process_summary)
        and "process record" in process_summary.lower()
        and re.search(r"\b(?:never|must not|does not)\b", process_summary, re.I)
    ):
        errors.append("Process Record contract lacks explicit activity-store exclusion")
    return errors


def check_non_consumer_text(path: Path, text: str) -> list[str]:
    """Reject affirmative activity consumers while allowing explicit prohibitions."""
    errors: list[str] = []
    offset = 1
    for paragraph in re.split(r"\n\s*\n", text):
        number = offset
        offset += paragraph.count("\n") + 2
        flattened = " ".join(line.strip() for line in paragraph.splitlines())
        for sentence in re.split(r"(?<=[.!?])\s+", flattened):
            for clause in CLAUSE_SPLIT_RE.split(sentence):
                if not clause:
                    continue
            # `build-input` is the closed post-terminal producer command, not
            # an assertion that the activity artifact is a downstream input.
                consumer_view = re.sub(
                    r"\bbuild-input\b", "producer-command", clause, flags=re.I
                )
                if not FEATURE_RE.search(clause) or not CONSUMER_RE.search(consumer_view):
                    continue
                if USER_RENDER_READ_RE.search(clause):
                    continue
                if NEGATION_RE.search(clause):
                    continue
                errors.append(
                    f"{path}:{number}: affirmative activity consumer: {clause[:180]}"
                )
    return errors


def check_execution_surface(path: Path, text: str) -> list[str]:
    """Reject hidden Python/workflow/shell consumers outside exact owners."""
    feature = bool(FEATURE_RE.search(text))
    runtime_import = bool(RUNTIME_IMPORT_RE.search(text))
    if path.suffix == ".py":
        if path in PYTHON_EXECUTION_WHITELIST:
            return []
        if feature or runtime_import:
            return [f"{path}: non-whitelisted production Python activity consumer"]
        return []

    errors: list[str] = []
    if "scripts/adjudication_activity.py" in text or runtime_import:
        errors.append(f"{path}: execution surface invokes/imports activity runtime")
    for number, line in enumerate(text.splitlines(), start=1):
        if not FEATURE_RE.search(line):
            continue
        allowed_workflow_line = path == Path(".github/workflows/spec-consistency.yml") and (
            "Check adjudication-activity advisory integration (#673)" in line
            or "python3 scripts/check_673_adjudication_activity.py" in line
        )
        if not allowed_workflow_line:
            errors.append(f"{path}:{number}: non-whitelisted execution-surface activity token")
    errors.extend(check_non_consumer_text(path, text))
    return errors


def run_checks(root: Path = REPO_ROOT) -> list[str]:
    errors: list[str] = []
    for relative in (*FROZEN_FILES, RUNTIME, *WIRING_FILES):
        if not (root / relative).is_file():
            errors.append(f"missing required #673 file: {relative}")
    if errors:
        return errors

    try:
        spec = (root / SPEC).read_text(encoding="utf-8")
        input_schema = _load_json(root / INPUT_SCHEMA)
        store_schema = _load_json(root / STORE_SCHEMA)
        runtime = (root / RUNTIME).read_text(encoding="utf-8")
        wiring = {
            path: (root / path).read_text(encoding="utf-8") for path in WIRING_FILES
        }
    except (OSError, UnicodeError, ValueError, DuplicateKeyError) as exc:
        return [f"#673 file load failed: {exc}"]

    errors.extend(check_spec_text(spec))
    errors.extend(check_retired_tokens(SPEC, spec))
    errors.extend(check_schema_contracts(input_schema, store_schema))
    errors.extend(check_runtime_text(runtime))
    errors.extend(check_retired_tokens(RUNTIME, runtime))
    errors.extend(check_wiring_texts(wiring))
    for path, text in wiring.items():
        errors.extend(check_retired_tokens(path, text))
    scanned: set[Path] = set()
    for pattern in NON_CONSUMER_GLOBS:
        for absolute in sorted(root.glob(pattern)):
            if not absolute.is_file():
                continue
            relative = absolute.relative_to(root)
            if relative in (INPUT_SCHEMA, STORE_SCHEMA) or relative in scanned:
                continue
            scanned.add(relative)
            try:
                text = absolute.read_text(encoding="utf-8")
            except (OSError, UnicodeError) as exc:
                errors.append(f"{relative}: non-consumer scan failed: {exc}")
                continue
            errors.extend(check_non_consumer_text(relative, text))
    execution_scanned: set[Path] = set()
    for pattern in EXECUTION_GLOBS:
        for absolute in sorted(root.glob(pattern)):
            if not absolute.is_file():
                continue
            relative = absolute.relative_to(root)
            if relative in execution_scanned:
                continue
            execution_scanned.add(relative)
            try:
                text = absolute.read_text(encoding="utf-8")
            except (OSError, UnicodeError) as exc:
                errors.append(f"{relative}: execution-surface scan failed: {exc}")
                continue
            errors.extend(check_execution_surface(relative, text))
    return sorted(set(errors))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)
    errors = run_checks(args.root.resolve())
    if errors:
        print("check_673_adjudication_activity: FAIL", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("check_673_adjudication_activity: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
