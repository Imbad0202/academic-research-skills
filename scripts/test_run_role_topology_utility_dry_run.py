from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "run_role_topology_utility_dry_run.py"
SPEC = importlib.util.spec_from_file_location("role_topology_dry_run", MODULE_PATH)
assert SPEC and SPEC.loader
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


def _assets():
    return runner.load_json_strict(runner.PLAN_PATH), runner.load_json_strict(
        runner.SET_PATH
    )


def test_real_assets_validate_and_materialize_exact_frozen_call_count():
    plan, heldout = runner.load_assets()
    manifest, prompts = runner.build_manifest(plan, heldout)
    assert len(manifest["calls"]) == len(prompts) == 186
    assert manifest["dispatch_authorized"] is False
    assert manifest["measurement_generated"] is False


def test_task_classes_have_independent_exact_arms_and_evaluators():
    plan, _heldout = _assets()
    classes = {row["task_class_id"]: row for row in plan["task_classes"]}
    assert [arm["role_count"] for arm in classes["decomposable_reviewer_evidence_review"]["arms"]] == [1, 2, 5, 7]
    writing = classes["sequential_writing_revision"]
    assert [arm["role_count"] for arm in writing["arms"]] == [1, 2, 5, 8]
    assert writing["evaluator_id"] == "writing-revision-rubric-v1"
    assert classes["decomposable_reviewer_evidence_review"]["evaluator_id"] == "reviewer-evidence-rubric-v1"


def test_writing_never_reuses_accept_reject_outcomes():
    plan, heldout = _assets()
    writing = next(row for row in plan["task_classes"] if row["task_class_id"] == "sequential_writing_revision")
    assert set(writing["forbidden_outcomes"]) == runner.WRITING_FORBIDDEN
    assert not runner.WRITING_FORBIDDEN.intersection(writing["outcome_vocabulary"])
    for row in heldout["scenarios"]:
        if row["task_class"] == "sequential_writing_revision":
            constraints = " ".join(row["constraints"]).casefold()
            assert all(label in constraints for label in ("accept", "reject", "minor revision", "major revision"))


def test_budget_tools_replicates_stopping_and_uncertainty_are_frozen():
    plan, _heldout = _assets()
    assert plan["budgets"] == {
        "per_call_input_token_cap": 24000,
        "per_call_output_token_cap": 1500,
        "no_rollover_between_seats": True,
        "planned_subject_calls": 186,
        "judge_calls_included": False,
        "api_spend_authorized_usd": 0,
    }
    assert plan["tools"] == {"allowed": [], "web": False, "network": False, "external_corpus": False, "workspace_reads": False}
    assert plan["replicates"]["per_scenario_arm"] == 3
    assert plan["stopping"]["retry_attempts"] == 0
    assert plan["stopping"]["stop_entire_study_on_first_blocked_partial_or_protocol_deviation"] is True
    assert plan["uncertainty"]["pool_task_classes"] is False
    assert plan["uncertainty"]["pool_metrics_to_scalar"] is False


def test_unique_verified_value_requires_blinded_human_verification():
    plan, _heldout = _assets()
    uvv = plan["unique_verified_value"]
    assert uvv["human_verification_required"] is True
    assert uvv["minimum_independent_experts"] == 2
    assert uvv["blind_adjudicator_required"] is True
    assert uvv["cross_task_label_reuse"] is False
    assert uvv["unavailable_panel_status"] == "NOT_COMPUTABLE"


def test_subject_prompts_hide_gold_and_exact_arm_identifiers():
    plan, heldout = runner.load_assets()
    manifest, prompts = runner.build_manifest(plan, heldout)
    scenarios = {row["scenario_id"]: row for row in heldout["scenarios"]}
    for call in manifest["calls"]:
        prompt = prompts[call["prompt_template_path"]]
        assert call["arm_id"].encode() not in prompt
        assert b"role_count" not in prompt
        scenario = scenarios[call["scenario_id"]]
        units = scenario["gold"].get("value_units", scenario["gold"].get("revision_requirements", []))
        assert all(unit["unit_id"].encode() not in prompt for unit in units)


def test_subject_blinding_is_exact_and_does_not_claim_hidden_dependency_count():
    plan, heldout = _assets()
    expected = runner.EXPECTED_SUBJECT_BLIND_FIELDS
    assert plan["blinding"]["subject_blind_fields"] == expected
    assert heldout["subject_blind_fields"] == expected
    assert "role_count" not in expected


def test_complete_hash_bound_role_contract_is_embedded_and_within_budget():
    plan, heldout = runner.load_assets()
    manifest, prompts = runner.build_manifest(plan, heldout)
    for call in manifest["calls"]:
        prompt = prompts[call["prompt_template_path"]]
        role_raw = (ROOT / call["role_ref"]).read_bytes()
        marker = f'<source_role_contract sha256="{call["role_ref_sha256"]}">\n'.encode()
        assert marker + role_raw + b"</source_role_contract>" in prompt
        assert call["role_contract_embedded"] is True
        adapter_raw = (ROOT / call["invocation_adapter_ref"]).read_bytes()
        adapter_marker = (
            f'<suite_invocation_adapter sha256="{call["invocation_adapter_sha256"]}">\n'
        ).encode()
        assert adapter_marker + adapter_raw + b"</suite_invocation_adapter>" in prompt
        assert call["invocation_adapter_embedded"] is True
        output_contract_raw = call["study_output_contract"].encode("utf-8")
        output_marker = (
            f'<study_output_contract sha256="{call["study_output_contract_sha256"]}">\n'
        ).encode()
        assert output_marker + output_contract_raw + b"</study_output_contract>" in prompt
        assert call["study_output_contract_embedded"] is True
        assert b"highest-precedence runtime authority" in prompt
        assert call["estimated_template_tokens"] == runner._estimated_template_tokens(prompt)
        assert call["reserved_dependency_tokens"] == len(call["depends_on"]) * 1500
        assert call["estimated_worst_case_input_tokens"] <= 24000


def test_manifest_order_ids_paths_hashes_and_dependencies_are_deterministic():
    plan, heldout = runner.load_assets()
    first, first_prompts = runner.build_manifest(plan, heldout)
    second, second_prompts = runner.build_manifest(plan, heldout)
    assert runner._canonical_json(first) == runner._canonical_json(second)
    assert first_prompts == second_prompts
    calls = first["calls"]
    assert [row["call_id"] for row in calls] == [f"call-{i:03d}" for i in range(1, 187)]
    assert [row["sequence_index"] for row in calls] == list(range(1, 187))
    assert len({row["prompt_template_path"] for row in calls}) == 186
    runner.validate_manifest_integrity(first, first_prompts, plan, heldout)


def test_manifest_integrity_rejects_duplicate_or_cross_cell_dependency():
    plan, heldout = runner.load_assets()
    manifest, prompts = runner.build_manifest(plan, heldout)
    duplicate = copy.deepcopy(manifest)
    duplicate["calls"][1]["call_id"] = duplicate["calls"][0]["call_id"]
    with pytest.raises(runner.TopologyError, match="call ids must be unique"):
        runner.validate_manifest_integrity(duplicate, prompts, plan, heldout)

    crossed = copy.deepcopy(manifest)
    target = next(row for row in crossed["calls"] if row["depends_on"])
    target["depends_on"] = [crossed["calls"][0]["call_id"]]
    target["reserved_dependency_tokens"] = target["output_token_cap"]
    target["estimated_worst_case_input_tokens"] = (
        target["estimated_template_tokens"] + target["output_token_cap"]
    )
    with pytest.raises(runner.TopologyError, match="dependency crosses"):
        runner.validate_manifest_integrity(crossed, prompts, plan, heldout)


def test_manifest_source_digests_bind_the_exact_in_memory_snapshots():
    plan, heldout = runner.load_assets()
    original, _ = runner.build_manifest(plan, heldout)
    mutated = copy.deepcopy(heldout)
    mutated["scenarios"][0]["assignment"] += " Preserve this disclosed mutation."
    changed, _ = runner.build_manifest(plan, mutated)
    assert changed["plan_sha256"] == original["plan_sha256"]
    assert changed["heldout_sha256"] != original["heldout_sha256"]
    assert changed["heldout_sha256"] == runner._sha256(
        runner._canonical_json(mutated)
    )


def test_exact_rebuild_rejects_metadata_or_placeholder_dependency_drift():
    plan, heldout = runner.load_assets()
    manifest, prompts = runner.build_manifest(plan, heldout)
    metadata = copy.deepcopy(manifest)
    metadata["calls"][0]["role_id"] = "draft_writer"
    with pytest.raises(runner.TopologyError, match="exact rebuild"):
        runner.validate_manifest_integrity(metadata, prompts, plan, heldout)

    dependency = copy.deepcopy(manifest)
    target_index, alternatives = next(
        (index, candidates)
        for index, target_row in enumerate(dependency["calls"])
        if len(target_row["depends_on"]) >= 2
        for candidates in [[
            row["call_id"]
            for row in dependency["calls"][:index]
            if all(
                row[key] == target_row[key]
                for key in ("task_class", "scenario_id", "arm_id", "replicate_id")
            )
            and row["call_id"] not in target_row["depends_on"]
        ]]
        if candidates
    )
    target = dependency["calls"][target_index]
    target["depends_on"][0] = alternatives[0]
    with pytest.raises(runner.TopologyError, match="exact rebuild"):
        runner.validate_manifest_integrity(dependency, prompts, plan, heldout)


def test_materialize_writes_closed_hash_bound_no_dispatch_manifest(tmp_path: Path):
    result = runner.materialize(tmp_path / "packet")
    manifest = json.loads((tmp_path / "packet" / "prompt-manifest.json").read_text(encoding="utf-8"))
    assert result["status"] == "MATERIALIZED_NO_DISPATCH"
    assert result["call_count"] == 186
    assert manifest["dispatch_authorized"] is False
    assert manifest["measurement_generated"] is False
    assert len(list((tmp_path / "packet" / "prompts").glob("*.txt"))) == 186


def test_dry_run_cli_writes_nothing(tmp_path: Path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    before = list(tmp_path.iterdir())
    assert runner.main(["dry-run"]) == 0
    after = list(tmp_path.iterdir())
    result = json.loads(capsys.readouterr().out)
    assert before == after == []
    assert result["status"] == "DRY_RUN_PASS"
    assert result["dispatch_authorized"] is False


def test_materializer_refuses_nonempty_destination(tmp_path: Path):
    target = tmp_path / "existing"
    target.mkdir()
    (target / "owned.txt").write_text("preserve", encoding="utf-8")
    with pytest.raises(runner.TopologyError, match="refusing non-empty"):
        runner.materialize(target)
    assert (target / "owned.txt").read_text(encoding="utf-8") == "preserve"


def test_role_count_or_arm_drift_fails_closed():
    plan, heldout = _assets()
    mutated = copy.deepcopy(plan)
    mutated["task_classes"][0]["arms"][1]["role_count"] = 5
    with pytest.raises(runner.TopologyError, match="arm ids or role counts drifted"):
        runner.validate_assets(mutated, heldout)


@pytest.mark.parametrize("mutation", ["evaluator", "role_ref", "dependency_graph"])
def test_exact_evaluator_and_role_graph_drift_fails_closed(mutation):
    plan, heldout = _assets()
    mutated = copy.deepcopy(plan)
    if mutation == "evaluator":
        mutated["task_classes"][0]["evaluator_id"] = "writing-revision-rubric-v1"
    elif mutation == "role_ref":
        roles = mutated["task_classes"][0]["arms"][2]["roles"]
        roles[0]["role_ref"], roles[1]["role_ref"] = (
            roles[1]["role_ref"],
            roles[0]["role_ref"],
        )
    else:
        mutated["task_classes"][0]["arms"][2]["roles"][-1]["depends_on"] = [
            "review-journal-fit"
        ]
    with pytest.raises(runner.TopologyError, match="exact role graph drifted"):
        runner.validate_assets(mutated, heldout)


@pytest.mark.parametrize("audience", ["expert_blind_fields", "adjudicator_blind_fields"])
def test_human_blinding_fields_are_exactly_frozen(audience):
    plan, heldout = _assets()
    mutated = copy.deepcopy(plan)
    mutated["blinding"][audience][-1] = "placeholder"
    with pytest.raises(runner.TopologyError, match="blind fields drifted"):
        runner.validate_assets(mutated, heldout)
    with pytest.raises(runner.TopologyError):
        runner._validate_schema(mutated, runner.PLAN_SCHEMA_PATH, "study plan")


def test_task_class_cannot_accept_other_task_gold_shape():
    plan, heldout = _assets()
    mutated = copy.deepcopy(heldout)
    review = next(
        row
        for row in mutated["scenarios"]
        if row["task_class"] == "decomposable_reviewer_evidence_review"
    )
    writing = next(
        row
        for row in mutated["scenarios"]
        if row["task_class"] == "sequential_writing_revision"
    )
    review["gold"] = copy.deepcopy(writing["gold"])
    with pytest.raises(runner.TopologyError, match="reviewer gold"):
        runner.validate_assets(plan, mutated)
    with pytest.raises(runner.TopologyError):
        runner._validate_schema(mutated, runner.SET_SCHEMA_PATH, "held-out set")


def test_dependency_on_later_or_missing_seat_fails_closed():
    plan, heldout = _assets()
    mutated = copy.deepcopy(plan)
    mutated["task_classes"][0]["arms"][1]["roles"][0]["depends_on"] = ["review-synthesis"]
    with pytest.raises(runner.TopologyError, match="dependency is not earlier"):
        runner.validate_assets(mutated, heldout)


def test_gold_anchor_or_evidence_drift_fails_closed():
    plan, heldout = _assets()
    mutated = copy.deepcopy(heldout)
    mutated["scenarios"][0]["gold"]["value_units"][0]["anchor"] = "not present"
    with pytest.raises(runner.TopologyError, match="anchor not in draft"):
        runner.validate_assets(plan, mutated)


def test_closed_schema_rejects_extra_plan_property():
    plan, _heldout = _assets()
    mutated = copy.deepcopy(plan)
    mutated["dispatch"] = True
    with pytest.raises(runner.TopologyError, match="Additional properties"):
        runner._validate_schema(mutated, runner.PLAN_SCHEMA_PATH, "study plan")


@pytest.mark.parametrize(
    ("mutation", "value"),
    [
        ("extra_dispatch", True),
        ("api_spend", 100),
        ("provider", "live-provider/model"),
    ],
)
def test_programmatic_builder_and_integrity_entrypoints_enforce_closed_source_schemas(
    mutation, value
):
    plan, heldout = _assets()
    baseline, prompts = runner.build_manifest(plan, heldout)
    mutated = copy.deepcopy(plan)
    if mutation == "extra_dispatch":
        mutated["dispatch"] = value
    elif mutation == "api_spend":
        mutated["budgets"]["api_spend_authorized_usd"] = value
    else:
        mutated["model_contract"]["subject_provider_model"] = value
    with pytest.raises(runner.TopologyError, match="study plan schema error"):
        runner.build_manifest(mutated, heldout)
    with pytest.raises(runner.TopologyError, match="study plan schema error"):
        runner.validate_manifest_integrity(baseline, prompts, mutated, heldout)


def test_each_arm_has_one_hash_bound_final_output_contract_and_role_scoped_intermediates():
    plan, heldout = runner.load_assets()
    manifest, prompts = runner.build_manifest(plan, heldout)
    for task in plan["task_classes"]:
        for arm in task["arms"]:
            finals = [
                role for role in arm["roles"] if role["output_kind"] == "final_outcome"
            ]
            assert [role["seat_id"] for role in finals] == [arm["final_output_seat"]]
            for role in arm["roles"]:
                contract = role["study_output_contract"].casefold()
                if role["output_kind"] == "intermediate_artifact":
                    assert "only" in contract
                    assert "do not" in contract
    field_calls = [row for row in manifest["calls"] if row["role_id"] == "field_analyst"]
    assert field_calls
    for call in field_calls:
        contract = call["study_output_contract"].casefold()
        assert "configuration" in contract
        assert "do not make findings" in contract
        assert contract.encode() in prompts[call["prompt_template_path"]].lower()
    peer_calls = [row for row in manifest["calls"] if row["role_id"] == "peer_reviewer"]
    assert peer_calls
    for call in peer_calls:
        contract = call["study_output_contract"].casefold()
        assert "do not produce a revised draft" in contract
        assert call["output_kind"] == "intermediate_artifact"


def test_output_contract_or_final_seat_drift_fails_closed():
    plan, heldout = _assets()
    mutated = copy.deepcopy(plan)
    arm = mutated["task_classes"][1]["arms"][2]
    arm["roles"][0]["output_kind"] = "final_outcome"
    with pytest.raises(runner.TopologyError, match="only final_output_seat"):
        runner.validate_assets(mutated, heldout)

    mutated = copy.deepcopy(plan)
    mutated["task_classes"][1]["arms"][2]["roles"][0][
        "study_output_contract"
    ] += " Mutated."
    with pytest.raises(runner.TopologyError, match="exact role graph drifted"):
        runner.validate_assets(mutated, heldout)


def test_strict_json_rejects_duplicate_keys(tmp_path: Path):
    path = tmp_path / "duplicate.json"
    path.write_text('{"suite":"a","suite":"b"}', encoding="utf-8")
    with pytest.raises(runner.TopologyError, match="duplicate JSON key"):
        runner.load_json_strict(path)


def test_repository_relative_role_path_cannot_escape_through_symlink(
    tmp_path: Path, monkeypatch
):
    repository = tmp_path / "repository"
    repository.mkdir()
    outside = tmp_path / "outside.md"
    outside.write_text("OUTSIDE SENTINEL", encoding="utf-8")
    (repository / "role.md").symlink_to(outside)
    monkeypatch.setattr(runner, "ROOT", repository)
    with pytest.raises(runner.TopologyError, match="escapes the repository"):
        runner._safe_repo_file("role.md")


def test_runner_has_no_transport_dispatch_or_measurement_command():
    source = MODULE_PATH.read_text(encoding="utf-8").casefold()
    for forbidden in ("import requests", "import urllib", "import subprocess", "openai", "anthropic", "codex exec", "claude -p"):
        assert forbidden not in source
    parser = runner._parser()
    subparser_action = next(
        action for action in parser._actions if hasattr(action, "choices") and action.choices
    )
    assert set(subparser_action.choices) == {"validate-assets", "dry-run", "materialize"}


def test_ci_registry_contract_and_spec_wiring():
    registry = json.loads((ROOT / "evals" / "heldout" / "suite_registry.json").read_text(encoding="utf-8"))
    assert registry[runner.SUITE] == "paired_controls"
    contract = (ROOT / "evals" / "heldout" / "MEASUREMENT_CONTRACT.md").read_text(encoding="utf-8")
    workflow = (ROOT / ".github" / "workflows" / "spec-consistency.yml").read_text(encoding="utf-8")
    manifest = (ROOT / "scripts" / "_ci_pytest_manifest.toml").read_text(encoding="utf-8")
    assert "| `role_topology_utility` | `paired_controls` |" in contract
    assert "run_role_topology_utility_dry_run.py validate-assets" in workflow
    assert 'id = "582-role-topology-utility-dry-run"' in manifest
