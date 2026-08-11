from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from scripts import check_669_review_pathway_rule_trace as check


ROOT = Path(__file__).resolve().parents[1]
CHECKED = (
    check.REQUEST_SCHEMA,
    check.TRACE_SCHEMA,
    check.REGISTRY,
    check.RUNTIME,
    check.OUTPUT_LINT,
    check.RUNTIME_TEST,
    check.LINT_FIXTURE,
    check.DESIGN,
    check.PROTOCOL,
    check.AUTHORITY_PROTOCOL,
    check.CONTRACT_README,
    check.NAVIGATION_AID,
    check.DEEP_SKILL,
    check.ETHICS_AGENT,
    check.ARCHITECT,
    check.ARCHITECT_MIRROR,
    check.CI_MANIFEST,
    check.WORKFLOW,
)


@pytest.fixture
def tree(tmp_path: Path) -> Path:
    for rel in CHECKED:
        target = tmp_path / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / rel, target)
    return tmp_path


def _errors(tree: Path) -> list[str]:
    return check.run_checks(tree)


def _replace(tree: Path, rel: Path, old: str, new: str) -> None:
    path = tree / rel
    text = path.read_text(encoding="utf-8")
    assert old in text
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def test_current_tree_passes() -> None:
    assert check.run_checks(ROOT) == []


@pytest.mark.parametrize(
    ("rel", "snippet"),
    [
        (rel, snippet)
        for rel, snippets in check.REQUIRED_SNIPPETS.items()
        for snippet in snippets
    ],
)
def test_required_wiring_removal_fails(tree: Path, rel: Path, snippet: str) -> None:
    _replace(tree, rel, snippet, "removed-669-contract")
    assert _errors(tree)


@pytest.mark.parametrize(
    ("rel", "snippet"),
    [
        (rel, snippet)
        for rel, scopes in check.SCOPED_SNIPPETS.items()
        for _start, _end, snippets in scopes
        for snippet in snippets
    ],
)
def test_shadow_token_cannot_mask_primary_contract_removal(
    tree: Path, rel: Path, snippet: str
) -> None:
    path = tree / rel
    text = path.read_text(encoding="utf-8")
    assert snippet in text
    path.write_text(
        text.replace(snippet, "removed-primary-contract", 1)
        + f"\n<!-- shadow only: {snippet} -->\n",
        encoding="utf-8",
    )
    assert any("primary #669 section" in error for error in _errors(tree))


def test_schema_result_footer_and_state_drift_fail(tree: Path) -> None:
    path = tree / check.TRACE_SCHEMA
    value = json.loads(path.read_text(encoding="utf-8"))
    value["properties"]["result"]["const"] = "candidate selected"
    path.write_text(json.dumps(value), encoding="utf-8")
    assert any("institutional result" in error for error in _errors(tree))

    value = json.loads((ROOT / check.TRACE_SCHEMA).read_text(encoding="utf-8"))
    value["properties"]["boundary_footer"]["const"] = "Authorization granted."
    path.write_text(json.dumps(value), encoding="utf-8")
    assert any("footer" in error for error in _errors(tree))

    value = json.loads((ROOT / check.TRACE_SCHEMA).read_text(encoding="utf-8"))
    value["properties"]["trace_state"]["enum"].append("approved")
    path.write_text(json.dumps(value), encoding="utf-8")
    assert any("trace-state" in error for error in _errors(tree))


@pytest.mark.parametrize(
    "field",
    [
        "verdict",
        "gate",
        "checkpoint",
        "approval_status",
        "probability",
        "selected_pathway",
        "submission_readiness",
        "authorization_status",
    ],
)
def test_trace_schema_cannot_represent_determination_or_workflow_field(
    tree: Path, field: str
) -> None:
    path = tree / check.TRACE_SCHEMA
    value = json.loads(path.read_text(encoding="utf-8"))
    value["properties"][field] = {"type": "string"}
    path.write_text(json.dumps(value), encoding="utf-8")
    assert any("determination/workflow keys" in error for error in _errors(tree))


def test_request_two_axis_grammar_drift_fails(tree: Path) -> None:
    path = tree / check.REQUEST_SCHEMA
    value = json.loads(path.read_text(encoding="utf-8"))
    value["$defs"]["profile_ref"]["properties"]["axis"]["enum"] = [
        "review_ethics"
    ]
    path.write_text(json.dumps(value), encoding="utf-8")
    assert any("two-axis" in error for error in _errors(tree))


@pytest.mark.parametrize("rel", [check.REQUEST_SCHEMA, check.TRACE_SCHEMA])
def test_display_only_ordering_constant_drift_fails(tree: Path, rel: Path) -> None:
    path = tree / rel
    value = json.loads(path.read_text(encoding="utf-8"))
    value["properties"]["ordering_semantics"]["const"] = "preferred_order"
    path.write_text(json.dumps(value), encoding="utf-8")
    assert any("ordering constant" in error for error in _errors(tree))


def test_any_object_schema_opening_fails(tree: Path) -> None:
    path = tree / check.REQUEST_SCHEMA
    value = json.loads(path.read_text(encoding="utf-8"))
    value["$defs"]["candidate_pathway"]["additionalProperties"] = True
    path.write_text(json.dumps(value), encoding="utf-8")
    assert any("not closed" in error for error in _errors(tree))


def test_alternative_row_schema_cap_drift_fails(tree: Path) -> None:
    path = tree / check.TRACE_SCHEMA
    value = json.loads(path.read_text(encoding="utf-8"))
    value["$defs"]["candidate_trace"]["properties"][
        "alternative_pathway_triggers"
    ]["maxItems"] = 65536
    path.write_text(json.dumps(value), encoding="utf-8")
    assert any("alternative-row schema cap" in error for error in _errors(tree))


def test_registry_requirement_scope_removal_fails(tree: Path) -> None:
    path = tree / check.REGISTRY
    value = json.loads(path.read_text(encoding="utf-8"))
    scopes = value["profiles"][0]["requirements"][0]["consumer_scopes"]
    scopes.remove("pathway_trace")
    path.write_text(json.dumps(value), encoding="utf-8")
    assert any("lost pathway_trace" in error for error in _errors(tree))


def test_lint_fixture_class_coverage_drift_fails(tree: Path) -> None:
    path = tree / check.LINT_FIXTURE
    value = json.loads(path.read_text(encoding="utf-8"))
    value["failing_surfaces"] = [
        row
        for row in value["failing_surfaces"]
        if row["class"] != "hedged_determination"
    ]
    path.write_text(json.dumps(value), encoding="utf-8")
    assert any("near-miss class coverage" in error for error in _errors(tree))


@pytest.mark.parametrize(
    "payload",
    [
        "\nimport socket\n",
        "\nimport openai\n",
        "\nimport subprocess\n",
        "\ndef scan(path):\n    return path.rglob('*')\n",
        "\ndef scan(path):\n    return os.listdir(path)\n",
        "\ndef clock():\n    return date.today()\n",
        "\ndef dynamic(text):\n    return eval(text)\n",
        "\ndef reflected(path):\n    return getattr(path, 'rglob')('*')\n",
        "\ndef judge(value):\n    return value\n\ndef use(value):\n    return judge(value)\n",
    ],
)
@pytest.mark.parametrize("rel", [check.RUNTIME, check.OUTPUT_LINT])
def test_runtime_or_lint_transport_scan_clock_model_drift_fails(
    tree: Path, rel: Path, payload: str
) -> None:
    path = tree / rel
    path.write_text(path.read_text(encoding="utf-8") + payload, encoding="utf-8")
    assert _errors(tree)


@pytest.mark.parametrize(
    ("rel", "name"),
    [
        (check.RUNTIME, "build_review_pathway_rule_trace"),
        (check.RUNTIME, "validate_review_pathway_rule_trace"),
        (check.RUNTIME, "render_review_pathway_rule_trace"),
        (check.OUTPUT_LINT, "normalize_surface"),
        (check.OUTPUT_LINT, "lint_trace_surface"),
    ],
)
def test_required_public_function_rename_fails(
    tree: Path, rel: Path, name: str
) -> None:
    _replace(tree, rel, f"def {name}(", f"def removed_{name}(")
    assert any("missing required function" in error for error in _errors(tree))


def test_pathway_or_banned_vocabulary_drift_fails(tree: Path) -> None:
    _replace(tree, check.OUTPUT_LINT, '("exempt",),', '("removed",),')
    assert any("pathway-name vocabulary" in error for error in _errors(tree))
    shutil.copyfile(ROOT / check.OUTPUT_LINT, tree / check.OUTPUT_LINT)
    _replace(tree, check.OUTPUT_LINT, '("approved",),', '("removed",),')
    assert any("banned-output vocabulary" in error for error in _errors(tree))


@pytest.mark.parametrize(
    ("rel", "old", "new", "message"),
    [
        (check.RUNTIME, "MAX_ALTERNATIVE_ROWS = 4096", "MAX_ALTERNATIVE_ROWS = 9999", "safety limit"),
        (check.RUNTIME, "MAX_TRACE_BYTES = 8 * 1024 * 1024", "MAX_TRACE_BYTES = 16 * 1024 * 1024", "safety limit"),
        (check.RUNTIME, "MAX_RENDERED_BYTES = 8 * 1024 * 1024", "MAX_RENDERED_BYTES = 16 * 1024 * 1024", "safety limit"),
        (check.OUTPUT_LINT, "MAX_RENDERED_BYTES = 8 * 1024 * 1024", "MAX_RENDERED_BYTES = 16 * 1024 * 1024", "byte limit"),
        (check.OUTPUT_LINT, "MAX_SURFACE_NODES = 200_000", "MAX_SURFACE_NODES = 300_000", "node limit"),
    ],
)
def test_resource_limit_drift_fails(
    tree: Path, rel: Path, old: str, new: str, message: str
) -> None:
    _replace(tree, rel, old, new)
    assert any(message in error for error in _errors(tree))


def test_candidate_json_or_markdown_grammar_drift_fails(tree: Path) -> None:
    _replace(
        tree,
        check.OUTPUT_LINT,
        'path[2] == "candidate_pathway_name"',
        'path[2] == "any_text"',
    )
    assert _errors(tree)
    shutil.copyfile(ROOT / check.OUTPUT_LINT, tree / check.OUTPUT_LINT)
    _replace(
        tree,
        check.OUTPUT_LINT,
        'line.startswith("Candidate pathway examined:")',
        'line.startswith("Candidate:")',
    )
    assert _errors(tree)


def test_linter_cannot_grow_an_ambient_path_argument(tree: Path) -> None:
    path = tree / check.OUTPUT_LINT
    path.write_text(
        path.read_text(encoding="utf-8")
        + '\n\ndef forbidden(parser):\n    parser.add_argument("--root")\n',
        encoding="utf-8",
    )
    # The forbidden function alone is not a scan; make the execution surface
    # materially ambient so the AST guard proves the policy boundary.
    with path.open("a", encoding="utf-8") as handle:
        handle.write("\ndef forbidden_scan(path):\n    return path.rglob('*.md')\n")
    assert any("ambient scan" in error for error in _errors(tree))


def test_architect_mirror_drift_fails(tree: Path) -> None:
    path = tree / check.ARCHITECT_MIRROR
    path.write_text(path.read_text(encoding="utf-8") + "\nmirror drift\n", encoding="utf-8")
    assert any("mirror drift" in error for error in _errors(tree))


def test_duplicate_schema_key_fails_strict_json(tree: Path) -> None:
    path = tree / check.TRACE_SCHEMA
    text = path.read_text(encoding="utf-8")
    path.write_text(
        text.replace('"title":', '"title":"duplicate",\n"title":', 1),
        encoding="utf-8",
    )
    assert any("duplicate key" in error for error in _errors(tree))
