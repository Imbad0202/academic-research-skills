#!/usr/bin/env python3
"""AST guard for the #675 offline-only Phase-2 envelope."""
from __future__ import annotations

import ast
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "scripts" / "run_indirect_prompt_injection_no_call.py"
ALLOWED_COMMANDS = {
    "init-run",
    "materialize",
    "validate",
    "ingest",
    "prepare-blind-packet",
}
FORBIDDEN_IMPORTS = {
    "aiohttp",
    "anthropic",
    "asyncio",
    "boto3",
    "ctypes",
    "ftplib",
    "grpc",
    "http",
    "httpx",
    "importlib",
    "multiprocessing",
    "openai",
    "paramiko",
    "requests",
    "smtplib",
    "socket",
    "subprocess",
    "telnetlib",
    "urllib",
    "urllib3",
    "webbrowser",
    "websocket",
    "websockets",
}
FORBIDDEN_OS_CALLS = {
    "execl",
    "execle",
    "execlp",
    "execlpe",
    "execv",
    "execve",
    "execvp",
    "execvpe",
    "popen",
    "spawnl",
    "spawnle",
    "spawnlp",
    "spawnlpe",
    "spawnv",
    "spawnve",
    "spawnvp",
    "spawnvpe",
    "system",
}
FORBIDDEN_FUNCTION_TOKENS = {
    "detect",
    "dispatch",
    "model",
    "provider",
    "probe",
    "retry",
    "transport",
}
FORBIDDEN_BUILTIN_CALLS = {"__import__", "compile", "eval", "exec"}

ALLOWED_DIRECT_IMPORTS = {
    "argparse", "base64", "copy", "hashlib", "json", "os", "re", "secrets",
    "stat", "sys", "unicodedata", "run_indirect_prompt_injection_probe",
}
ALLOWED_FROM_IMPORTS = {
    "__future__": {"annotations"},
    "datetime": {"datetime"},
    "pathlib": {"Path"},
    "typing": {"Any", "NoReturn"},
    "jsonschema": {"Draft202012Validator", "FormatChecker"},
    "scripts": {"run_indirect_prompt_injection_probe"},
}
ALLOWED_IMPORT_ALIASES = {
    ("run_indirect_prompt_injection_probe", "phase1"),
    ("scripts", "run_indirect_prompt_injection_probe", "phase1"),
}
ALLOWED_FUNCTIONS = {
    "__init__", "_fail", "_reject_pairs", "_strict_loads", "_canonical", "_json_bytes",
    "_sha", "_read_file", "_assert_contained", "_fsync_directory", "_write_new",
    "_replace_json", "_ensure_exact_new", "_journal_value", "_journal_ref",
    "_validate_journal_token", "_claim_journal_token", "_complete_journal_token",
    "_validate_run_tree",
    "_relative_files_and_directories", "_parent_directories", "_schema",
    "_validate_schema", "_timestamp", "_repo_path", "_repository_head_commit",
    "_asset_bindings", "_execution", "_observed_execution", "_scenario_index",
    "_factor_order", "_ordered_assignments", "_call_envelope", "_build_plan",
    "_config_from_plan", "_validate_plan", "_initial_manifest", "_validate_manifest",
    "_expected_run_inventory", "_unregistered_tree_snapshot",
    "_validate_run_inventory", "_decode_base64",
    "_validate_stop_intent", "_recover_stop_intent", "_validate_preload_quarantine",
    "_load_run", "_validate_ingestion_journal_lifecycle", "init_run",
    "_material_map", "_validate_materials", "materialize",
    "_response_diagnostics", "_has_visible_semantic_text", "_closed_embedded_object", "_normalize_raw_event",
    "_external_session_receipt", "_validate_transcript", "_validate_authorization_record",
    "_receipt_value", "_preserved_ingestion_artifacts", "_validate_ingested_artifacts",
    "validate_run", "_record_stop", "_record_preload_quarantine", "ingest",
    "_blind_identifiers", "_normalized_blind_text", "_compact_blind_text",
    "_fold_blind_alphanumeric", "_blind_screen_text", "_joined_blind_text",
    "_contains_complete_compact_identifier", "_contains_compact_phrase",
    "_assert_blindable_transcript",
    "_assert_blind_packet_structure", "visit", "_assignment_boundary",
    "_blind_packet_value", "_blind_inventory_value", "_private_map_value",
    "_blind_manifest_value", "_source_ingestion_manifest", "_validate_blind_bundle",
    "_finalize_blind_state", "prepare_blind_packet",
    "_run_args", "_parser", "main",
}
ALLOWED_CLASSES = {"EnvelopeError", "StopViolation"}
ALLOWED_NAME_CALLS = ALLOWED_FUNCTIONS | ALLOWED_CLASSES | {
    "Draft202012Validator", "FormatChecker", "Path", "SystemExit", "ValueError",
    "all", "any", "enumerate", "hasattr", "int", "isinstance", "len", "list",
    "max", "next", "ord", "print", "range", "reversed", "set", "sorted", "str",
    "sum", "super", "tuple", "type", "zip",
}
ALLOWED_ATTRIBUTE_NAMES = {
    "ArgumentParser", "IGNORECASE", "JSONDecodeError", "Namespace", "O_CREAT",
    "O_DIRECTORY", "O_EXCL", "O_NOFOLLOW", "O_RDONLY", "O_WRONLY", "RESPONSE_KEYS",
    "S_IMODE", "__init__", "absolute", "absolute_path", "add", "add_argument",
    "add_parser", "add_subparsers", "append", "as_posix", "auth_mode",
    "authorization_record", "b64decode", "b64encode", "casefold", "category",
    "check_schema", "chmod", "close", "code", "command", "compile", "count",
    "decode", "deepcopy", "detail", "dumps", "encode", "escape", "exists",
    "extend", "external_content", "fdopen", "fileno", "flush", "fromisoformat",
    "fsync", "fullmatch", "get", "glob", "hexdigest", "input_token_cap", "intersection",
    "is_absolute", "is_dir", "is_file", "is_symlink", "items", "iter_errors",
    "join", "load_assets", "loads", "message", "mkdir", "name", "normalize",
    "link", "open", "order_seed", "output_token_cap", "parent", "parents", "parse_args",
    "parts", "plan_sha256", "read_bytes", "read_text", "reasoning_effort",
    "relative_to", "removeprefix", "rename", "render_prompt", "replace", "resolve",
    "reverse", "rglob", "rmdir", "run_dir", "run_id", "search", "sha256", "sort",
    "split", "splitlines", "st_dev", "st_ino", "st_mode", "st_mtime_ns", "st_size",
    "startswith", "stat", "stderr", "strip", "subject_model", "subject_provider",
    "subject_runtime", "subject_runtime_version", "suite_commit", "throw", "token_hex",
    "transcript", "tzinfo", "unlink", "update", "values", "with_name", "write",
}
ALLOWED_ATTRIBUTE_CALLS = ALLOWED_ATTRIBUTE_NAMES - {
    "IGNORECASE", "JSONDecodeError", "Namespace", "O_CREAT", "O_DIRECTORY", "O_EXCL",
    "O_NOFOLLOW", "O_RDONLY", "O_WRONLY", "RESPONSE_KEYS", "absolute_path", "auth_mode",
    "authorization_record", "code", "command", "detail", "input_token_cap", "message",
    "name", "order_seed", "output_token_cap", "parent", "parents", "parts", "plan_sha256",
    "reasoning_effort", "run_dir", "run_id", "st_dev", "st_ino", "st_mode", "st_mtime_ns",
    "st_size", "stderr", "subject_model", "subject_provider", "subject_runtime",
    "subject_runtime_version", "suite_commit", "transcript", "tzinfo",
}
ALLOWED_MODULE_ATTRIBUTES = {
    "argparse": {"ArgumentParser", "Namespace"},
    "base64": {"b64decode", "b64encode"},
    "copy": {"deepcopy"},
    "hashlib": {"sha256"},
    "json": {"JSONDecodeError", "dumps", "loads"},
    "os": {"O_CREAT", "O_DIRECTORY", "O_EXCL", "O_NOFOLLOW", "O_RDONLY", "O_WRONLY", "chmod", "close", "fdopen", "fsync", "link", "open", "rename", "replace"},
    "re": {"IGNORECASE", "compile", "escape", "fullmatch", "search"},
    "secrets": {"token_hex"},
    "stat": {"S_IMODE"},
    "sys": {"stderr"},
    "unicodedata": {"category", "normalize"},
    "phase1": {"RESPONSE_KEYS", "external_content", "load_assets", "render_prompt"},
}
SENSITIVE_MODULE_NAMES = set(ALLOWED_MODULE_ATTRIBUTES)
EXPECTED_IMPORT_SPECS = {
    ("import", name, None, None)
    for name in ALLOWED_DIRECT_IMPORTS - {"run_indirect_prompt_injection_probe"}
} | {
    ("import", "run_indirect_prompt_injection_probe", None, "phase1"),
    ("from", "__future__", "annotations", None),
    ("from", "datetime", "datetime", None),
    ("from", "pathlib", "Path", None),
    ("from", "typing", "Any", None),
    ("from", "typing", "NoReturn", None),
    ("from", "jsonschema", "Draft202012Validator", None),
    ("from", "jsonschema", "FormatChecker", None),
    ("from", "scripts", "run_indirect_prompt_injection_probe", "phase1"),
}


def check_source(source: str) -> list[str]:
    errors: list[str] = []
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return [f"cannot parse runner: {exc}"]
    imported: set[str] = set()
    import_specs: list[tuple[str, str, str | None, str | None]] = []
    commands: list[str] = []
    functions: list[str] = []
    classes: list[str] = []
    parents = {child: parent for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                import_specs.append(("import", alias.name, None, alias.asname))
                imported.add(alias.name.split(".", 1)[0])
                allowed_alias = (alias.name, alias.asname) in ALLOWED_IMPORT_ALIASES
                if alias.name not in ALLOWED_DIRECT_IMPORTS or (
                    alias.asname is not None and not allowed_alias
                ):
                    errors.append(
                        f"import must match the exact module/alias allowlist: {alias.name} as {alias.asname}"
                    )
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            imported.add(module.split(".", 1)[0])
            allowed_symbols = ALLOWED_FROM_IMPORTS.get(module, set())
            if node.level != 0 or not allowed_symbols:
                errors.append(f"from-import module is not allowed: {module!r}")
            for alias in node.names:
                import_specs.append(("from", module, alias.name, alias.asname))
                allowed_alias = (
                    module, alias.name, alias.asname
                ) in ALLOWED_IMPORT_ALIASES
                if alias.name not in allowed_symbols or alias.name == "*" or (
                    alias.asname is not None and not allowed_alias
                ):
                    errors.append(
                        "from-import must match the exact symbol/alias allowlist: "
                        f"{module}.{alias.name} as {alias.asname}"
                    )
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append(node.name)
            if isinstance(node, ast.AsyncFunctionDef):
                errors.append(f"async function surface is forbidden: {node.name}")
        elif isinstance(node, ast.ClassDef):
            classes.append(node.name)
        elif (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "add_parser"
            and node.args
            and isinstance(node.args[0], ast.Constant)
            and isinstance(node.args[0].value, str)
        ):
            commands.append(node.args[0].value)
        if isinstance(node, ast.Attribute):
            if node.attr not in ALLOWED_ATTRIBUTE_NAMES:
                errors.append(f"attribute is outside the exact allowlist: {node.attr}")
            if isinstance(node.value, ast.Name) and node.value.id in SENSITIVE_MODULE_NAMES:
                allowed = ALLOWED_MODULE_ATTRIBUTES[node.value.id]
                if node.attr not in allowed:
                    errors.append(
                        f"module attribute is outside the exact allowlist: {node.value.id}.{node.attr}"
                    )
        if isinstance(node, ast.Name) and node.id in SENSITIVE_MODULE_NAMES:
            parent = parents.get(node)
            if not (
                isinstance(parent, ast.Attribute)
                and parent.value is node
            ):
                errors.append(f"module alias/escape is forbidden: {node.id}")
        if isinstance(node, ast.Name) and node.id in {
            "__builtins__", "globals", "locals", "vars", "getattr", "setattr", "delattr"
        }:
            errors.append(f"dynamic namespace capability is forbidden: {node.id}")
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id not in ALLOWED_NAME_CALLS:
                    errors.append(f"call target is outside the exact allowlist: {node.func.id}")
            elif isinstance(node.func, ast.Attribute):
                if node.func.attr not in ALLOWED_ATTRIBUTE_CALLS:
                    errors.append(
                        f"attribute call is outside the exact allowlist: {node.func.attr}"
                    )
            else:
                errors.append("indirect/subscript/lambda call target is forbidden")
            for keyword in node.keywords:
                if keyword.arg == "shell" and isinstance(keyword.value, ast.Constant):
                    if keyword.value.value is True:
                        errors.append("shell=True is forbidden")
    overlap = sorted(imported & FORBIDDEN_IMPORTS)
    if overlap:
        errors.append(f"forbidden transport/process imports: {overlap}")
    if set(import_specs) != EXPECTED_IMPORT_SPECS or len(import_specs) != len(
        EXPECTED_IMPORT_SPECS
    ):
        errors.append(
            "imports must match the exact statement/symbol/alias set; "
            f"unexpected={sorted(set(import_specs) - EXPECTED_IMPORT_SPECS, key=repr)!r}, "
            f"missing={sorted(EXPECTED_IMPORT_SPECS - set(import_specs), key=repr)!r}"
        )
    if set(commands) != ALLOWED_COMMANDS or len(commands) != len(ALLOWED_COMMANDS):
        errors.append(
            f"CLI commands must be exactly {sorted(ALLOWED_COMMANDS)}, found {sorted(commands)}"
        )
    if set(functions) != ALLOWED_FUNCTIONS or len(functions) != len(ALLOWED_FUNCTIONS):
        errors.append(
            "function definitions must match exact allowlist; "
            f"unexpected={sorted(set(functions) - ALLOWED_FUNCTIONS)}, "
            f"missing={sorted(ALLOWED_FUNCTIONS - set(functions))}"
        )
    if set(classes) != ALLOWED_CLASSES or len(classes) != len(ALLOWED_CLASSES):
        errors.append(
            "class definitions must match exact allowlist; "
            f"unexpected={sorted(set(classes) - ALLOWED_CLASSES)}, "
            f"missing={sorted(ALLOWED_CLASSES - set(classes))}"
        )
    return errors


def main() -> int:
    try:
        source = TARGET.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        print(f"ERROR: cannot read {TARGET}: {exc}", file=sys.stderr)
        return 1
    errors = check_source(source)
    if errors:
        print("#675 no-call AST guard failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("#675 no-call AST guard passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
