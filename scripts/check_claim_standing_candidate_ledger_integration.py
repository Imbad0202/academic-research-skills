#!/usr/bin/env python3
"""Static, hermetic integration guard for #655 Track A."""
from __future__ import annotations

import ast
import copy
import hashlib
import json
import sys
from pathlib import Path


SCHEMA_DIR = Path("shared/contracts/claim_standing")
SCHEMAS = {
    "query_plan.schema.json": "claim-standing-query-plan/1.0",
    "retrieval_input.schema.json": "claim-standing-retrieval-input/1.0",
    "candidate_ledger.schema.json": "claim-standing-candidate-ledger/1.0",
}
RUNTIME = Path("scripts/build_claim_standing_candidate_ledger.py")
PROTOCOL = Path("shared/references/claim_standing_candidate_ledger_protocol.md")
PHASE_E_PROTOCOL = Path(
    "academic-pipeline/references/claim_verification_protocol.md"
)
DESIGN = Path("docs/design/2026-08-13-655-search-bounded-claim-standing-probe-design.md")
CONTRACT_README = Path("shared/contracts/README.md")
MANIFEST = Path("scripts/_ci_pytest_manifest.toml")
WORKFLOW = Path(".github/workflows/spec-consistency.yml")
CHANGELOG = Path("CHANGELOG.md")
FIXTURES = (
    Path("scripts/fixtures/claim_standing_candidate_ledger/query_plan.json"),
    Path("scripts/fixtures/claim_standing_candidate_ledger/retrieval_input.json"),
)
RESOLVER_HASHES = {
    Path("scripts/semantic_scholar_client.py"): "86e2c3d713804d0e9f4d095e245db0521afb0d198686434515a0c1b225d0f787",
    Path("scripts/openalex_client.py"): "e90207a2b591a385dab61a55a86a92a6623cb60c428edce360a4199947209cda",
    Path("scripts/crossref_client.py"): "06da046164f882e20383cd63ec9e9b6da2507d7a5e1f23066adebb88f2256e25",
    Path("scripts/arxiv_client.py"): "76ace0911bf98b1a288e64ee41f4c2caf993b9df48ef3abb0c57b8446acf02a7",
}
ALLOWED_RUNTIME_DIRECT_IMPORTS = {
    "argparse",
    "copy",
    "hashlib",
    "json",
    "os",
    "re",
    "sys",
    "unicodedata",
}
ALLOWED_RUNTIME_FROM_IMPORTS = {
    "__future__": {"annotations"},
    "collections": {"Counter"},
    "datetime": {"datetime"},
    "itertools": {"combinations"},
    "json": {"JSONDecodeError"},
    "jsonschema": {"Draft202012Validator"},
    "jsonschema.exceptions": {"SchemaError", "ValidationError"},
    "pathlib": {"Path"},
    "typing": {"Any"},
}
ALLOWED_RUNTIME_MODULE_CALLS = {
    "argparse": {"ArgumentParser"},
    "copy": {"deepcopy"},
    "hashlib": {"sha256"},
    "json": {"dumps", "loads"},
    "os": {"close", "fdopen", "fsync", "open"},
    "re": {"compile"},
    "unicodedata": {"category", "normalize"},
}
ALLOWED_RUNTIME_MODULE_VALUES = {
    # The only non-call module value is the explicit print(..., file=...) sink.
    "sys": {"stderr"},
}
ALLOWED_RUNTIME_MODULE_CONSTANTS = {
    "os": {"O_CREAT", "O_EXCL", "O_NOFOLLOW", "O_RDONLY", "O_WRONLY", "name"},
}
FORBIDDEN_RUNTIME_NAMES = {
    "__builtins__",
    "__import__",
    "breakpoint",
    "compile",
    "delattr",
    "eval",
    "exec",
    "getattr",
    "globals",
    "locals",
    "setattr",
    "vars",
}
FORBIDDEN_RUNTIME_ATTRIBUTES = {
    "Popen",
    "__bases__",
    "__builtins__",
    "__class__",
    "__closure__",
    "__code__",
    "__dict__",
    "__getattribute__",
    "__globals__",
    "__import__",
    "__loader__",
    "__subclasses__",
    "_getframe",
    "call",
    "check_call",
    "check_output",
    "connect",
    "create_connection",
    "execv",
    "execve",
    "f_builtins",
    "f_globals",
    "f_locals",
    "fork",
    "import_module",
    "modules",
    "popen",
    "request",
    "run",
    "spawn",
    "system",
    "urlopen",
}


def _read(root: Path, relative: Path, errors: list[str]) -> str | None:
    try:
        return (root / relative).read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(f"{relative}: cannot read strict UTF-8: {exc}")
        return None


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_checks(root: Path) -> list[str]:
    errors: list[str] = []
    loaded_schemas: dict[str, dict] = {}
    for name, version in SCHEMAS.items():
        relative = SCHEMA_DIR / name
        text = _read(root, relative, errors)
        if text is None:
            continue
        try:
            schema = json.loads(text)
        except json.JSONDecodeError as exc:
            errors.append(f"{relative}: invalid JSON: {exc}")
            continue
        loaded_schemas[name] = schema
        if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            errors.append(f"{relative}: Draft 2020-12 identity drifted")
        if schema.get("additionalProperties") is not False:
            errors.append(f"{relative}: root must remain closed")
        if schema.get("properties", {}).get("schema_version", {}).get("const") != version:
            errors.append(f"{relative}: schema_version drifted")
        property_names = {
            key
            for node in _objects(schema)
            for key in node.get("properties", {})
        }
        forbidden_fields = property_names & {
            "evidence_rows",
            "full_text",
            "gate_effect",
            "model",
            "stance",
            "verdict",
        }
        if forbidden_fields:
            errors.append(f"{relative}: Track B/live fields entered Track A: {sorted(forbidden_fields)}")

    retrieval = loaded_schemas.get("retrieval_input.schema.json")
    candidate = loaded_schemas.get("candidate_ledger.schema.json")
    if retrieval is not None and candidate is not None:
        for input_name, output_name in (
            ("attempt", "attempt"),
            ("retry_authorization", "retry_authorization"),
            ("confirmed_relation", "confirmed_relation"),
        ):
            if retrieval["$defs"].get(input_name) != candidate["$defs"].get(output_name):
                errors.append(
                    f"{SCHEMA_DIR}: shared {input_name}/{output_name} definitions drifted"
                )
        input_raw = copy.deepcopy(retrieval["$defs"]["raw_hit"])
        output_raw = copy.deepcopy(candidate["$defs"]["base_raw_hit"])
        input_raw.pop("additionalProperties", None)
        output_raw.pop("additionalProperties", None)
        if input_raw["properties"]["abstract_text"] == {"$ref": "#/$defs/nullable_string"}:
            input_raw["properties"]["abstract_text"] = retrieval["$defs"]["nullable_string"]
        if input_raw != output_raw:
            errors.append(f"{SCHEMA_DIR}: shared raw_hit/base_raw_hit definitions drifted")
        terminal = candidate["$defs"]["final_raw_hit"]["allOf"][1]["properties"][
            "terminal_state"
        ]["enum"]
        expected_terminal = [
            "selected",
            "missing_title_and_stable_id",
            "outside_date_range",
            "outside_language_set",
            "outside_document_type",
            "duplicate_version",
            "not_relevant",
            "not_checked",
            "candidate_cap_exceeded",
        ]
        if terminal != expected_terminal:
            errors.append(f"{SCHEMA_DIR}: raw terminal-state vocabulary drifted")
        input_relevance = retrieval["$defs"]["relevance"]["properties"]["state"]["enum"]
        output_relevance = candidate["$defs"]["relevance"]["properties"]["state"]["enum"]
        if input_relevance != ["relevant", "not_relevant", "ambiguous", "not_checked"]:
            errors.append(f"{SCHEMA_DIR}: retained relevance vocabulary drifted")
        if output_relevance != ["relevant", "not_relevant", "ambiguous", "not_checked"]:
            errors.append(f"{SCHEMA_DIR}: finalized relevance vocabulary drifted")
        if retrieval["$defs"]["relevance"] != candidate["$defs"]["relevance"]:
            errors.append(f"{SCHEMA_DIR}: shared relevance fields drifted")

    runtime_text = _read(root, RUNTIME, errors)
    if runtime_text is not None:
        try:
            tree = ast.parse(runtime_text, filename=str(RUNTIME))
        except SyntaxError as exc:
            errors.append(f"{RUNTIME}: invalid Python: {exc}")
        else:
            forbidden_imports: set[str] = set()
            direct_module_bindings: dict[str, str] = {}
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name not in ALLOWED_RUNTIME_DIRECT_IMPORTS:
                            forbidden_imports.add(alias.name)
                            continue
                        binding = alias.asname or alias.name
                        existing = direct_module_bindings.get(binding)
                        if existing is not None and existing != alias.name:
                            forbidden_imports.add(
                                f"ambiguous-binding:{binding}"
                            )
                        direct_module_bindings[binding] = alias.name
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or "<relative>"
                    allowed_symbols = (
                        ALLOWED_RUNTIME_FROM_IMPORTS.get(module, set())
                        if node.level == 0
                        else set()
                    )
                    forbidden_imports.update(
                        f"{module}.{alias.name}"
                        for alias in node.names
                        if alias.name not in allowed_symbols
                    )
            if forbidden_imports:
                errors.append(
                    f"{RUNTIME}: non-allowlisted transport/model/process-capable imports: "
                    f"{sorted(forbidden_imports)}"
                )
            shadowed_module_bindings: set[str] = set()
            for node in ast.walk(tree):
                if (
                    isinstance(node, ast.Name)
                    and isinstance(node.ctx, (ast.Store, ast.Del))
                    and node.id in direct_module_bindings
                ):
                    shadowed_module_bindings.add(node.id)
                elif (
                    isinstance(node, ast.arg)
                    and node.arg in direct_module_bindings
                ):
                    shadowed_module_bindings.add(node.arg)
                elif isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        if (alias.asname or alias.name) in direct_module_bindings:
                            shadowed_module_bindings.add(alias.asname or alias.name)
            if shadowed_module_bindings:
                errors.append(
                    f"{RUNTIME}: direct module bindings cannot be shadowed: "
                    f"{sorted(shadowed_module_bindings)}"
                )
            parents = {
                child: parent
                for parent in ast.walk(tree)
                for child in ast.iter_child_nodes(parent)
            }
            module_reference_errors: set[str] = set()
            for node in ast.walk(tree):
                if not (
                    isinstance(node, ast.Name)
                    and isinstance(node.ctx, ast.Load)
                    and node.id in direct_module_bindings
                ):
                    continue
                module = direct_module_bindings[node.id]
                parent = parents.get(node)
                if not (isinstance(parent, ast.Attribute) and parent.value is node):
                    module_reference_errors.add(
                        f"{module} via {node.id}: bare module reference"
                    )
                    continue
                attributes = [parent.attr]
                outer = parent
                while True:
                    ancestor = parents.get(outer)
                    if not (
                        isinstance(ancestor, ast.Attribute)
                        and ancestor.value is outer
                    ):
                        break
                    attributes.append(ancestor.attr)
                    outer = ancestor
                attribute_path = ".".join(attributes)
                use_parent = parents.get(outer)
                is_allowed_call = (
                    attribute_path
                    in ALLOWED_RUNTIME_MODULE_CALLS.get(module, set())
                    and isinstance(use_parent, ast.Call)
                    and use_parent.func is outer
                )
                is_allowed_value = (
                    attribute_path
                    in ALLOWED_RUNTIME_MODULE_VALUES.get(module, set())
                    and isinstance(use_parent, ast.keyword)
                    and use_parent.arg == "file"
                    and isinstance(parents.get(use_parent), ast.Call)
                    and isinstance(parents[use_parent].func, ast.Name)
                    and parents[use_parent].func.id == "print"
                )
                is_allowed_constant = attribute_path in (
                    ALLOWED_RUNTIME_MODULE_CONSTANTS.get(module, set())
                ) and isinstance(outer.ctx, ast.Load)
                if not (
                    is_allowed_call or is_allowed_value or is_allowed_constant
                ):
                    module_reference_errors.add(
                        f"{module} via {node.id}.{attribute_path}"
                    )
            if module_reference_errors:
                errors.append(
                    f"{RUNTIME}: direct module references must match exact "
                    "current-use call/value allowlists: "
                    f"{sorted(module_reference_errors)}"
                )
            dynamic_references: set[str] = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Name) and node.id in FORBIDDEN_RUNTIME_NAMES:
                    dynamic_references.add(node.id)
                elif (
                    isinstance(node, ast.Attribute)
                    and node.attr in FORBIDDEN_RUNTIME_ATTRIBUTES
                ):
                    dynamic_references.add(node.attr)
            if dynamic_references:
                errors.append(
                    f"{RUNTIME}: dynamic import, introspection, process, or network "
                    f"references are forbidden: {sorted(dynamic_references)}"
                )
        for forbidden in ("add_parser(\"dispatch\"", "add_parser('dispatch'", "urlopen(", ".request("):
            if forbidden in runtime_text:
                errors.append(f"{RUNTIME}: forbidden capability marker {forbidden!r}")
        for marker in (
            "MAX_QUERIES = 3",
            "MAX_INDEXES = 4",
            "MAX_HITS_PER_QUERY_INDEX = 20",
            "MAX_RAW_HITS = 240",
            "MAX_SELECTED = 40",
            "consentable_plan_projection",
            "expected_root_pairs",
            "retry_authorizations",
            "failed_completed < authorized < retry_started",
            "distinct_dois",
            "started <= returned <= completed",
            "relevance_assessment_input_projection",
            "render_relevance_prompt",
            "assessment_input_sha256",
            "has_visible_semantic_text",
            "_DOI_BODY_RE",
            '== "explicit_local_export"',
            "EXPLICIT_LOCAL_EXPORT_BOUNDARY",
            "os.O_NOFOLLOW",
            "os.O_EXCL",
            "0o600",
            '"not_checked"',
        ):
            if marker not in runtime_text:
                errors.append(f"{RUNTIME}: frozen cap marker missing: {marker}")

    for relative, expected in RESOLVER_HASHES.items():
        path = root / relative
        if not path.is_file():
            errors.append(f"{relative}: resolver baseline missing")
        elif _sha(path) != expected:
            errors.append(f"{relative}: existing resolver changed; Track A requires separate future adapters")

    for fixture in FIXTURES:
        text = _read(root, fixture, errors)
        if text is not None:
            try:
                json.loads(text)
            except json.JSONDecodeError as exc:
                errors.append(f"{fixture}: invalid JSON: {exc}")

    required_text = {
        PROTOCOL: (
            "STANCE CLASSIFICATION UNMEASURED",
            "does not retrieve records",
            "candidate_cap_exceeded",
            "claim-standing-transmission-ledger/1.0",
            "build_claim_standing_query_plan.py",
            "check_claim_standing_freshness.py",
            "check_claim_standing_transmissions.py",
        ),
        DESIGN: (
            "TRACK A SUBSTRATE IMPLEMENTED",
            "claim-standing-candidate-ledger/1.0",
            "It does not close #655",
        ),
        CONTRACT_README: (
            "Claim-standing candidate ledger (#655 Track A)",
            "claim-standing-query-plan/1.0",
            "claim-standing-candidate-ledger/1.0",
            "claim-standing-transmission-ledger/1.0",
            "transmission_ledger.schema.json",
        ),
        PHASE_E_PROTOCOL: (
            "## Claim-Standing Probe Offer (#655",
            "opt-in, advisory-only",
            "`HIGH-IMPACT`",
            "`RANDOM`, `TOP-UP`, and `NOT-SELECTED` rows are never eligible",
            "`ALL` is not permission to probe every claim",
            "ineligible until the researcher confirms",
            "never written back to the registry",
            "Eligibility never dispatches anything",
            "`not_checked` declination record",
            "scripts/build_claim_standing_query_plan.py",
            "shared/references/claim_standing_candidate_ledger_protocol.md",
            "STANCE CLASSIFICATION UNMEASURED",
            "gate_effect = none",
        ),
        CHANGELOG: (
            "candidate-ledger substrate (#655 Track A)",
            "Pipeline wiring for the #655 claim-standing probe",
        ),
        MANIFEST: (
            'id = "655-claim-standing-candidate-ledger"',
            'id = "655-claim-standing-candidate-ledger-integration"',
            'id = "655-claim-standing-query-plan-builder"',
            'id = "655-claim-standing-freshness"',
            'id = "655-claim-standing-transmissions"',
            'id = "655-claim-standing-pipeline-wiring"',
        ),
        WORKFLOW: (
            "Check claim-standing candidate-ledger integration (#655)",
            "python3 scripts/check_claim_standing_candidate_ledger_integration.py",
        ),
    }
    for relative, markers in required_text.items():
        text = _read(root, relative, errors)
        if text is None:
            continue
        for marker in markers:
            if marker not in text:
                errors.append(f"{relative}: required #655 marker missing: {marker}")
    forbidden_text = {
        PROTOCOL: ("deferred to the pipeline-wiring slice",),
    }
    for relative, markers in forbidden_text.items():
        text = _read(root, relative, errors)
        if text is None:
            continue
        for marker in markers:
            if marker in text:
                errors.append(
                    f"{relative}: stale #655 marker must not appear: {marker}"
                )
    return errors


def _objects(value: object):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _objects(child)
    elif isinstance(value, list):
        for child in value:
            yield from _objects(child)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    errors = run_checks(root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("PASS: #655 Track A candidate-ledger integration is closed and offline")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
