#!/usr/bin/env python3
"""Check the static #669 schemas, runtime, lint surface, and consumer wiring."""
from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path
from typing import Any


REQUEST_SCHEMA = Path(
    "shared/contracts/human_subjects/review_pathway_trace_request.schema.json"
)
TRACE_SCHEMA = Path(
    "shared/contracts/human_subjects/review_pathway_rule_trace.schema.json"
)
REGISTRY = Path("shared/human_subjects_authority_registry.json")
RUNTIME = Path("scripts/build_review_pathway_rule_trace.py")
OUTPUT_LINT = Path("scripts/check_review_pathway_output.py")
RUNTIME_TEST = Path("scripts/test_review_pathway_rule_trace.py")
LINT_FIXTURE = Path(
    "scripts/fixtures/review_pathway_rule_trace/lint-near-misses.json"
)
DESIGN = Path("docs/design/2026-08-11-669-review-pathway-rule-trace-spec.md")
PROTOCOL = Path("shared/references/review_pathway_rule_trace_protocol.md")
AUTHORITY_PROTOCOL = Path("shared/references/human_subjects_authority_protocol.md")
CONTRACT_README = Path("shared/contracts/README.md")
NAVIGATION_AID = Path("deep-research/references/irb_decision_tree.md")
DEEP_SKILL = Path("deep-research/SKILL.md")
ETHICS_AGENT = Path("deep-research/agents/ethics_review_agent.md")
ARCHITECT = Path("deep-research/agents/research_architect_agent.md")
ARCHITECT_MIRROR = Path("agents/research_architect_agent.md")
CI_MANIFEST = Path("scripts/_ci_pytest_manifest.toml")
WORKFLOW = Path(".github/workflows/spec-consistency.yml")

RESULT = "institutional determination required"
ORDERING = "display_only_sequence_no_decision_meaning"
FOOTER = (
    "Human-subjects boundary: This output does not authorize recruitment, "
    "consent, access to identifiable data, intervention, or data collection."
)
TRACE_STATES = {
    "completed",
    "jurisdiction_unresolved",
    "authority_context_unresolved",
}
FORBIDDEN_OUTPUT_KEYS = {
    "verdict",
    "gate",
    "checkpoint",
    "decision",
    "determination",
    "approval",
    "approval_status",
    "clearance",
    "exemption",
    "probability",
    "confidence",
    "likelihood",
    "ranking",
    "timeline",
    "recommended_pathway",
    "selected_pathway",
    "review_pathway",
    "submission_readiness",
    "authorization_status",
    "institutional_acceptance",
}
FORBIDDEN_IMPORT_ROOTS = {
    "anthropic",
    "glob",
    "http",
    "importlib",
    "openai",
    "requests",
    "random",
    "secrets",
    "socket",
    "subprocess",
    "time",
    "urllib",
    "uuid",
}
FORBIDDEN_SCAN_CALLS = {
    "glob",
    "iglob",
    "rglob",
    "iterdir",
    "listdir",
    "scandir",
    "walk",
    "fwalk",
}
FORBIDDEN_CLOCK_CALLS = {"today", "now", "utcnow", "time", "monotonic"}
FORBIDDEN_PROCESS_CALLS = {
    "system",
    "popen",
    "fork",
    "forkpty",
    "spawnl",
    "spawnle",
    "spawnlp",
    "spawnlpe",
    "spawnv",
    "spawnve",
    "spawnvp",
    "spawnvpe",
}
FORBIDDEN_DECISION_CALLS = {
    "judge",
    "evaluate",
    "score",
    "classify",
    "predict",
    "rank",
}
RUNTIME_FUNCTIONS = {
    "_validate_alternative_volume",
    "validate_review_pathway_trace_request",
    "build_review_pathway_rule_trace",
    "validate_review_pathway_rule_trace",
    "render_review_pathway_rule_trace",
    "main",
}
LINT_FUNCTIONS = {
    "_read_text_limited",
    "normalize_surface",
    "lint_trace_surface",
    "lint_rendered_surface",
    "lint_artifacts",
    "main",
}
EXPECTED_PATHWAY_TERMS = {
    ("exempt",),
    ("expedited",),
    ("full", "board"),
    ("convened", "board"),
    ("not", "human", "subjects", "research"),
    ("nhsr",),
}
REQUIRED_ALWAYS_BANNED = {
    ("no", "irb", "needed"),
    ("no", "irb", "required"),
    ("irb", "not", "required"),
    ("no", "ethics", "review", "needed"),
    ("no", "ethics", "review", "required"),
    ("approved",),
    ("approval",),
    ("approve",),
    ("approves",),
    ("approving",),
    ("cleared",),
    ("clearance",),
    ("clear",),
    ("clears",),
    ("low", "risk"),
    ("probability",),
    ("confidence",),
    ("likely",),
    ("unlikely",),
    ("probably",),
    ("chance",),
    ("odds",),
    ("likelihood",),
    ("percent",),
    ("percentage",),
    ("rank",),
    ("ranked",),
    ("ranking",),
    ("preferred",),
    ("recommended",),
    ("most", "studies", "like", "yours"),
    ("timeline",),
}
REQUIRED_SNIPPETS: dict[Path, tuple[str, ...]] = {
    DESIGN: (
        "every string leaf in one named",
        "candidate_pathways[*].candidate_pathway_name",
        "No determination, probability, confidence, likelihood ranking, timeline",
        "never a gate, verdict, checkpoint input",
    ),
    PROTOCOL: (
        "validate_review_pathway_rule_trace(",
        "check_review_pathway_output.py",
        "It never scans a directory, repository",
        "does not open or change #666's",
        "cannot change submission readiness",
    ),
    AUTHORITY_PROTOCOL: (
        "#669 consumes every selected-profile requirement scoped to `pathway_trace`",
        "review_pathway_rule_trace_protocol.md",
    ),
    CONTRACT_README: (
        "## Review-pathway rule trace (#669)",
        "review_pathway_trace_request.schema.json",
        "review_pathway_rule_trace.schema.json",
    ),
    NAVIGATION_AID: (
        "### 1.3 Derived #669 candidate rule trace",
        "validate_review_pathway_rule_trace(...)",
        "cannot update readiness, authorization, an action",
    ),
    DEEP_SKILL: (
        "surface-linted #669 artifact",
        "shared/references/review_pathway_rule_trace_protocol.md",
    ),
    ETHICS_AGENT: (
        "For a separately dispatched #669",
        "check_review_pathway_output.py",
        "workflow input",
    ),
    ARCHITECT: (
        "Replay-bound #669 rule trace is display-only",
        "check_review_pathway_output.py",
        "workflow input",
    ),
    CI_MANIFEST: (
        'id = "669-review-pathway-rule-trace"',
        'path = "scripts/test_review_pathway_rule_trace.py"',
        'id = "669-review-pathway-integration"',
        'path = "scripts/test_check_669_review_pathway_rule_trace.py"',
    ),
    WORKFLOW: (
        "Check review-pathway rule-trace integration (#669)",
        "python3 scripts/check_669_review_pathway_rule_trace.py",
    ),
}
SCOPED_SNIPPETS: dict[
    Path, tuple[tuple[str, str | None, tuple[str, ...]], ...]
] = {
    DESIGN: (
        (
            "## 9. Surface-scoped banned-output lint",
            "## 10. Producers and consumers",
            ("candidate_pathways[*].candidate_pathway_name",),
        ),
    ),
    PROTOCOL: (
        (
            "## Surface-scoped output lint",
            "## Consumer contract",
            ("It never scans a directory, repository",),
        ),
        (
            "## Consumer contract",
            "## Non-goals",
            ("The trace never supplies an action assignment",),
        ),
    ),
    NAVIGATION_AID: (
        (
            "### 1.3 Derived #669 candidate rule trace",
            "---\n\n## 2. Exact Bounded Requirement Pointers",
            ("validate_review_pathway_rule_trace(...)",),
        ),
    ),
    ETHICS_AGENT: (
        (
            "### 7. Human Subjects Ethics",
            "## References",
            ("check_review_pathway_output.py", "workflow input"),
        ),
    ),
    ARCHITECT: (
        (
            "### 6. Ethics & Human-Subjects Administrative Planning",
            "### 7. Reporting Standards",
            ("check_review_pathway_output.py", "workflow input"),
        ),
    ),
}


class DuplicateKeyError(ValueError):
    pass


def _no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, child in pairs:
        if key in value:
            raise DuplicateKeyError(f"duplicate key: {key}")
        value[key] = child
    return value


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=_no_duplicates,
        parse_constant=lambda token: (_ for _ in ()).throw(
            ValueError(f"non-finite value: {token}")
        ),
    )
    if not isinstance(value, dict):
        raise ValueError("top-level value must be an object")
    return value


def _schema_property_names(value: Any) -> set[str]:
    names: set[str] = set()
    if isinstance(value, dict):
        properties = value.get("properties")
        if isinstance(properties, dict):
            names.update(properties)
        for child in value.values():
            names.update(_schema_property_names(child))
    elif isinstance(value, list):
        for child in value:
            names.update(_schema_property_names(child))
    return names


def _closed_schema_errors(value: Any, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        if value.get("type") == "object" and value.get("additionalProperties") is not False:
            errors.append(f"{path}: object schema is not closed")
        for key, child in value.items():
            errors.extend(_closed_schema_errors(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(_closed_schema_errors(child, f"{path}[{index}]"))
    return errors


def _literal_assignment(tree: ast.Module, name: str) -> Any:
    def literal(node: ast.AST) -> Any:
        try:
            return ast.literal_eval(node)
        except (ValueError, TypeError):
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mult):
                left = literal(node.left)
                right = literal(node.right)
                if (
                    isinstance(left, int)
                    and not isinstance(left, bool)
                    and isinstance(right, int)
                    and not isinstance(right, bool)
                ):
                    return left * right
            return None

    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if any(isinstance(target, ast.Name) and target.id == name for target in targets):
                return literal(node.value)
    return None


def _runtime_ast_errors(path: Path, source: str, required: set[str]) -> list[str]:
    errors: list[str] = []
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return [f"{path}: cannot parse: {exc}"]
    functions = {
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    for name in sorted(required - functions):
        errors.append(f"{path}: missing required function {name}")
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports = [node.module]
            if node.module == "os":
                for alias in node.names:
                    if alias.name in FORBIDDEN_SCAN_CALLS | FORBIDDEN_PROCESS_CALLS:
                        errors.append(
                            f"{path}: forbidden imported scan/process call {alias.name}"
                        )
        else:
            imports = []
        for imported in imports:
            if imported.split(".", 1)[0] in FORBIDDEN_IMPORT_ROOTS:
                errors.append(f"{path}: forbidden transport/model/process import {imported}")
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                if node.func.attr in FORBIDDEN_SCAN_CALLS:
                    errors.append(f"{path}: forbidden ambient scan call {node.func.attr}()")
                if node.func.attr in FORBIDDEN_CLOCK_CALLS:
                    errors.append(f"{path}: forbidden ambient clock call {node.func.attr}()")
                if node.func.attr in FORBIDDEN_PROCESS_CALLS:
                    errors.append(f"{path}: forbidden process call {node.func.attr}()")
                if node.func.attr.casefold() in FORBIDDEN_DECISION_CALLS:
                    errors.append(f"{path}: forbidden decision/evaluator call {node.func.attr}()")
            elif isinstance(node.func, ast.Name):
                if node.func.id in FORBIDDEN_SCAN_CALLS:
                    errors.append(f"{path}: forbidden ambient scan call {node.func.id}()")
                if node.func.id in {"eval", "exec", "__import__"}:
                    errors.append(f"{path}: forbidden dynamic execution call {node.func.id}()")
                if node.func.id.casefold() in FORBIDDEN_DECISION_CALLS:
                    errors.append(f"{path}: forbidden decision/evaluator call {node.func.id}()")
            if (
                isinstance(node.func, ast.Name)
                and node.func.id == "getattr"
                and len(node.args) >= 2
                and isinstance(node.args[1], ast.Constant)
                and isinstance(node.args[1].value, str)
                and node.args[1].value
                in FORBIDDEN_SCAN_CALLS
                | FORBIDDEN_CLOCK_CALLS
                | FORBIDDEN_PROCESS_CALLS
                | FORBIDDEN_DECISION_CALLS
            ):
                errors.append(
                    f"{path}: forbidden reflected call {node.args[1].value}"
                )
    return errors


def run_checks(root: Path) -> list[str]:
    errors: list[str] = []
    json_values: dict[Path, dict[str, Any]] = {}
    texts: dict[Path, str] = {}
    for rel in (REQUEST_SCHEMA, TRACE_SCHEMA, REGISTRY, LINT_FIXTURE):
        try:
            json_values[rel] = _load_json(root / rel)
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
            errors.append(f"{rel}: cannot read strict JSON: {exc}")
    text_paths = {
        RUNTIME,
        OUTPUT_LINT,
        RUNTIME_TEST,
        DESIGN,
        PROTOCOL,
        AUTHORITY_PROTOCOL,
        CONTRACT_README,
        NAVIGATION_AID,
        DEEP_SKILL,
        ETHICS_AGENT,
        ARCHITECT,
        ARCHITECT_MIRROR,
        CI_MANIFEST,
        WORKFLOW,
    }
    for rel in text_paths:
        try:
            texts[rel] = (root / rel).read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append(f"{rel}: cannot read: {exc}")

    request_schema = json_values.get(REQUEST_SCHEMA)
    if request_schema is not None:
        const = request_schema.get("properties", {}).get("schema_version", {}).get("const")
        if const != "review-pathway-trace-request/1.0":
            errors.append(f"{REQUEST_SCHEMA}: schema version drifted")
        if (
            request_schema.get("properties", {})
            .get("ordering_semantics", {})
            .get("const")
            != ORDERING
        ):
            errors.append(f"{REQUEST_SCHEMA}: display-only ordering constant drifted")
        axis = (
            request_schema.get("$defs", {})
            .get("profile_ref", {})
            .get("properties", {})
            .get("axis", {})
            .get("enum")
        )
        if set(axis or []) != {"review_ethics", "data_protection"}:
            errors.append(f"{REQUEST_SCHEMA}: exact two-axis candidate profile grammar drifted")
        errors.extend(f"{REQUEST_SCHEMA}: {item}" for item in _closed_schema_errors(request_schema))

    trace_schema = json_values.get(TRACE_SCHEMA)
    if trace_schema is not None:
        properties = trace_schema.get("properties", {})
        if properties.get("schema_version", {}).get("const") != "review-pathway-rule-trace/1.0":
            errors.append(f"{TRACE_SCHEMA}: schema version drifted")
        if properties.get("result", {}).get("const") != RESULT:
            errors.append(f"{TRACE_SCHEMA}: fixed institutional result drifted")
        if properties.get("ordering_semantics", {}).get("const") != ORDERING:
            errors.append(f"{TRACE_SCHEMA}: display-only ordering constant drifted")
        if properties.get("boundary_footer", {}).get("const") != FOOTER:
            errors.append(f"{TRACE_SCHEMA}: fixed #665 footer drifted")
        if set(properties.get("trace_state", {}).get("enum") or []) != TRACE_STATES:
            errors.append(f"{TRACE_SCHEMA}: trace-state vocabulary drifted")
        alternative_max = (
            trace_schema.get("$defs", {})
            .get("candidate_trace", {})
            .get("properties", {})
            .get("alternative_pathway_triggers", {})
            .get("maxItems")
        )
        if alternative_max != 4096:
            errors.append(f"{TRACE_SCHEMA}: alternative-row schema cap drifted")
        forbidden = _schema_property_names(trace_schema) & FORBIDDEN_OUTPUT_KEYS
        if forbidden:
            errors.append(
                f"{TRACE_SCHEMA}: determination/workflow keys are representable: "
                f"{', '.join(sorted(forbidden))}"
            )
        errors.extend(f"{TRACE_SCHEMA}: {item}" for item in _closed_schema_errors(trace_schema))

    registry = json_values.get(REGISTRY)
    if registry is not None:
        for profile_index, profile in enumerate(registry.get("profiles", [])):
            for requirement_index, requirement in enumerate(profile.get("requirements", [])):
                if "pathway_trace" not in requirement.get("consumer_scopes", []):
                    errors.append(
                        f"{REGISTRY}: profiles[{profile_index}].requirements[{requirement_index}] "
                        "lost pathway_trace scope"
                    )

    lint_fixture = json_values.get(LINT_FIXTURE)
    if lint_fixture is not None:
        if lint_fixture.get("schema_version") != "review-pathway-lint-fixtures/1.0":
            errors.append(f"{LINT_FIXTURE}: fixture schema version drifted")
        rows = lint_fixture.get("failing_surfaces")
        if not isinstance(rows, list):
            errors.append(f"{LINT_FIXTURE}: failing_surfaces must be an array")
        else:
            classes = {
                row.get("class")
                for row in rows
                if isinstance(row, dict) and isinstance(row.get("class"), str)
            }
            required_classes = {
                "approved",
                "bare_pathway",
                "candidate_context_prefix",
                "candidate_prose",
                "cleared",
                "hedged_determination",
                "low_risk",
                "probability",
                "timeline",
                "unicode_format",
                "whitespace",
            }
            if not required_classes <= classes:
                errors.append(f"{LINT_FIXTURE}: near-miss class coverage drifted")

    runtime_source = texts.get(RUNTIME)
    if runtime_source is not None:
        errors.extend(_runtime_ast_errors(RUNTIME, runtime_source, RUNTIME_FUNCTIONS))
        try:
            runtime_tree = ast.parse(runtime_source)
        except SyntaxError:
            runtime_tree = None
        if runtime_tree is not None:
            expected_limits = {
                "MAX_ALTERNATIVE_ROWS": 4096,
                "MAX_TRACE_BYTES": 8 * 1024 * 1024,
                "MAX_RENDERED_BYTES": 8 * 1024 * 1024,
            }
            for name, expected in expected_limits.items():
                if _literal_assignment(runtime_tree, name) != expected:
                    errors.append(f"{RUNTIME}: {name} safety limit drifted")
        for token in ('add_parser("build"', 'add_parser("validate"', 'add_parser("render"'):
            if token not in runtime_source:
                errors.append(f"{RUNTIME}: missing CLI surface {token}")
        if "lint_trace_surface(output)" not in runtime_source:
            errors.append(f"{RUNTIME}: generated JSON is not linted before publication")

    lint_source = texts.get(OUTPUT_LINT)
    if lint_source is not None:
        errors.extend(_runtime_ast_errors(OUTPUT_LINT, lint_source, LINT_FUNCTIONS))
        try:
            lint_tree = ast.parse(lint_source)
        except SyntaxError:
            lint_tree = None
        if lint_tree is not None:
            pathway_terms = _literal_assignment(lint_tree, "PATHWAY_TERMS")
            banned = _literal_assignment(lint_tree, "ALWAYS_BANNED_TERMS")
            if set(pathway_terms or []) != EXPECTED_PATHWAY_TERMS:
                errors.append(f"{OUTPUT_LINT}: closed pathway-name vocabulary drifted")
            if not REQUIRED_ALWAYS_BANNED <= set(banned or []):
                errors.append(f"{OUTPUT_LINT}: required banned-output vocabulary drifted")
            if _literal_assignment(lint_tree, "MAX_RENDERED_BYTES") != 8 * 1024 * 1024:
                errors.append(f"{OUTPUT_LINT}: rendered byte limit drifted")
            if _literal_assignment(lint_tree, "MAX_SURFACE_NODES") != 200_000:
                errors.append(f"{OUTPUT_LINT}: surface-node limit drifted")
        option_names: set[str] = set()
        for node in ast.walk(lint_tree) if lint_tree is not None else ():
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "add_argument"
                and node.args
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)
                and node.args[0].value.startswith("--")
            ):
                option_names.add(node.args[0].value)
        if option_names != {"--trace-json", "--rendered"}:
            errors.append(
                f"{OUTPUT_LINT}: explicit CLI surface drifted: {', '.join(sorted(option_names))}"
            )
        for token in (
            'parser.add_argument("--trace-json"',
            'parser.add_argument("--rendered"',
            'unicodedata.normalize("NFKC", text).casefold()',
            'path[2] == "candidate_pathway_name"',
            "_candidate_name_violations(value)",
            'line.startswith("Candidate pathway examined:")',
            "rendered != expected",
        ):
            if token not in lint_source:
                errors.append(f"{OUTPUT_LINT}: missing surface-scope/normalization grammar {token}")

    for rel, snippets in REQUIRED_SNIPPETS.items():
        text = texts.get(rel)
        if text is None:
            continue
        for snippet in snippets:
            count = text.count(snippet)
            if count != 1:
                errors.append(
                    f"{rel}: #669 contract snippet must occur exactly once "
                    f"({snippet!r}, observed {count})"
                )

    for rel, scopes in SCOPED_SNIPPETS.items():
        text = texts.get(rel)
        if text is None:
            continue
        for start, end, snippets in scopes:
            start_index = text.find(start)
            if start_index < 0:
                errors.append(f"{rel}: missing scoped #669 section start {start!r}")
                continue
            content_start = start_index + len(start)
            end_index = text.find(end, content_start) if end is not None else len(text)
            if end_index < 0:
                errors.append(f"{rel}: missing scoped #669 section end {end!r}")
                continue
            section = text[content_start:end_index]
            for snippet in snippets:
                if snippet not in section:
                    errors.append(
                        f"{rel}: primary #669 section {start!r} missing {snippet!r}"
                    )

    if ARCHITECT in texts and ARCHITECT_MIRROR in texts:
        if texts[ARCHITECT] != texts[ARCHITECT_MIRROR]:
            errors.append(f"{ARCHITECT_MIRROR}: research-architect mirror drift")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)
    errors = run_checks(args.root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Review-pathway rule-trace integration check passed (#669).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
