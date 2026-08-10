#!/usr/bin/env python3
"""Bounded mutation tests for the hermetic revision-claim-drift v2 guard (#679)."""

from __future__ import annotations

import copy
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

import pytest

from scripts import check_revision_claim_drift_suite_v2 as guard
from scripts.check_heldout_measurement_report import validate_report


REPO_ROOT = Path(__file__).resolve().parents[1]
SUITE = Path(guard.SUITE_REL)
FIXTURES = Path("scripts/fixtures/revision_claim_drift_v2")
DESIGN = Path("docs/design/2026-08-10-679-revision-claim-drift-suite-v2-spec.md")
MEASUREMENT_SCHEMA = Path("evals/heldout/measurement_report.schema.json")
EXECUTION_SCHEMA = Path("evals/heldout/execution_manifest.schema.json")
LADDER = Path("shared/references/claim_strength_ladder.md")
LAUNCHER_SCHEMA = SUITE / "subject_launcher_config.schema.json"
CALL_PLAN_SCHEMA = SUITE / "subject_call_plan.schema.json"


def _copy_file(root: Path, relative: Path | str) -> None:
    relative_path = Path(relative)
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(REPO_ROOT / relative_path, destination)


def _mirror(tmp_path: Path) -> Path:
    """Copy only the repository surfaces inspected by ``run_checks``."""
    root = tmp_path / "repo"
    shutil.copytree(REPO_ROOT / SUITE, root / SUITE)
    shutil.copytree(REPO_ROOT / FIXTURES, root / FIXTURES)
    _copy_file(root, DESIGN)
    _copy_file(root, LADDER)
    return root


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_object_digest(value: dict[str, Any]) -> str:
    raw = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _replace(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    assert old in text
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def _sync_v2_rubric(root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Re-pin a deliberate rubric mutation so semantic guards are exercised."""
    rubric = root / SUITE / "adjudication_rubric_v2.md"
    digest = _digest(rubric)
    monkeypatch.setattr(guard, "V2_RUBRIC_SHA256", digest)
    ledger_path = root / SUITE / "rubric_amendments.json"
    ledger = _read_json(ledger_path)
    ledger["rubrics"][1]["sha256"] = digest
    ledger["amendments"][0]["to_sha256"] = digest
    _write_json(ledger_path, ledger)


def _sync_subject_schema(root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    schema_path = root / SUITE / "subject_context_record.schema.json"
    monkeypatch.setattr(guard, "SUBJECT_SCHEMA_SHA256", _digest(schema_path))


def _schema() -> dict[str, Any]:
    return _read_json(REPO_ROOT / SUITE / "subject_context_record.schema.json")


def _fixture(name: str) -> dict[str, Any]:
    return _read_json(REPO_ROOT / FIXTURES / name)


def test_current_repository_passes_all_679_guards() -> None:
    assert guard.run_checks(REPO_ROOT) == [
        "historical bytes/tree and no-new-measurement boundary",
        "v2 rubric and closed amendment ledger",
        "subject-context/launcher/call-plan schemas and four synthetic fixtures",
        "README/design prospective protocol",
        "prospective heldout-measurement/1.1 context replay",
    ]


def test_unmutated_minimal_mirror_passes(tmp_path: Path) -> None:
    assert len(guard.run_checks(_mirror(tmp_path))) == 5


def test_protected_historical_file_byte_drift_fails(tmp_path: Path) -> None:
    root = _mirror(tmp_path)
    path = root / SUITE / "heldout_set.json"
    path.write_bytes(path.read_bytes() + b"\n")
    with pytest.raises(guard.ContractError, match="protected historical byte drift"):
        guard.run_checks(root)


@pytest.mark.parametrize("mutation", ["add", "delete", "byte_drift"])
def test_historical_run_tree_inventory_is_write_once(
    tmp_path: Path, mutation: str
) -> None:
    root = _mirror(tmp_path)
    tree = root / guard.HISTORICAL_TREE_REL
    files = sorted(path for path in tree.rglob("*") if path.is_file())
    assert files
    if mutation == "add":
        (tree / "unauthorized-addition.txt").write_text("drift\n", encoding="utf-8")
    elif mutation == "delete":
        files[0].unlink()
    else:
        files[0].write_bytes(files[0].read_bytes() + b"\n")
    with pytest.raises(guard.ContractError, match="protected historical run-tree drift"):
        guard.run_checks(root)


def test_679_cannot_create_a_measurement_row(tmp_path: Path) -> None:
    root = _mirror(tmp_path)
    _write_json(root / SUITE / "measurement-2099-01-01.json", {})
    with pytest.raises(guard.ContractError, match="creates no measurement row"):
        guard.run_checks(root)


def test_v2_rubric_hash_is_load_bearing(tmp_path: Path) -> None:
    root = _mirror(tmp_path)
    rubric = root / SUITE / "adjudication_rubric_v2.md"
    rubric.write_text(rubric.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    with pytest.raises(guard.ContractError, match="rubric byte identity"):
        guard._check_rubric(root)


@pytest.mark.parametrize("mutation", ["c9_authority", "canonical_anchor", "ladder_copy"])
def test_v2_rubric_semantics_survive_rehashing_attacks(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mutation: str
) -> None:
    root = _mirror(tmp_path)
    rubric = root / SUITE / "adjudication_rubric_v2.md"
    if mutation == "c9_authority":
        _replace(
            rubric,
            "### C9 — Non-control citation-attachment violation",
            "### C9 — Citation-token conservation",
        )
        expected = "C9 title/authority drift"
    elif mutation == "canonical_anchor":
        _replace(
            rubric,
            "#what-counts-as-a-move-and-what-does-not",
            "#unfrozen-local-summary",
        )
        expected = "missing or duplicates frozen marker"
    else:
        rubric.write_text(
            rubric.read_text(encoding="utf-8") + "\nhedged → asserted\n",
            encoding="utf-8",
        )
        expected = "must point to, not copy"
    _sync_v2_rubric(root, monkeypatch)
    with pytest.raises(guard.ContractError, match=expected):
        guard._check_rubric(root)


def test_closed_amendment_ledger_rejects_mutation(tmp_path: Path) -> None:
    root = _mirror(tmp_path)
    path = root / SUITE / "rubric_amendments.json"
    ledger = _read_json(path)
    ledger["amendments"][0]["historical_effect"] = "rescore"
    _write_json(path, ledger)
    with pytest.raises(guard.ContractError, match="closed amendment"):
        guard._check_rubric(root)


@pytest.mark.parametrize(
    "payload",
    [
        '{"schema_version":"x","schema_version":"y"}',
        '{"schema_version":"x","score":NaN}',
        '\ufeff{"schema_version":"x"}',
    ],
    ids=["duplicate-key", "nonfinite", "utf8-bom"],
)
def test_new_contract_json_is_parsed_strictly(
    tmp_path: Path, payload: str
) -> None:
    root = _mirror(tmp_path)
    (root / SUITE / "historical_artifacts.lock.json").write_text(
        payload, encoding="utf-8"
    )
    with pytest.raises(guard.ContractError, match="duplicate JSON key|non-finite|strict JSON"):
        guard.run_checks(root)


def test_subject_context_schema_hash_is_load_bearing(tmp_path: Path) -> None:
    root = _mirror(tmp_path)
    path = root / SUITE / "subject_context_record.schema.json"
    path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    with pytest.raises(guard.ContractError, match="schema byte identity"):
        guard._check_subject_assets(root)


@pytest.mark.parametrize(
    ("fixture_name", "container"),
    [
        ("subject_context_machine_supported.json", "execution_manifest"),
        ("subject_context_machine_supported.json", "neutral_cwd"),
        ("subject_context_machine_supported.json", "cli"),
        ("subject_context_machine_supported.json", "instruction_visibility"),
        ("subject_context_machine_supported.json", "context_probe"),
        ("subject_context_machine_supported.json", "data_minimization"),
        ("subject_context_attested_only.json", "attestation"),
    ],
)
def test_subject_context_nested_branches_are_closed(
    fixture_name: str, container: str
) -> None:
    record = _fixture(fixture_name)
    assert isinstance(record[container], dict)
    record[container]["raw_secret"] = "must-not-be-stored"
    with pytest.raises(guard.ContractError):
        guard.validate_subject_context(record, _schema())


@pytest.mark.parametrize("mutation", ["add", "delete", "byte_drift"])
def test_fixture_inventory_and_bytes_are_frozen(
    tmp_path: Path, mutation: str
) -> None:
    root = _mirror(tmp_path)
    fixture_dir = root / FIXTURES
    if mutation == "add":
        _write_json(fixture_dir / "extra.json", {})
        expected = "fixture inventory drift"
    elif mutation == "delete":
        (fixture_dir / "subject_context_unknown.json").unlink()
        expected = "fixture inventory drift"
    else:
        path = fixture_dir / "subject_context_unknown.json"
        path.write_bytes(path.read_bytes() + b"\n")
        expected = "fixture byte drift"
    with pytest.raises(guard.ContractError, match=expected):
        guard._check_subject_assets(root)


@pytest.mark.parametrize("relation", ["inside_repository", "repository_visible"])
def test_derived_not_isolated_relations_are_load_bearing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    relation: str,
) -> None:
    root = _mirror(tmp_path)
    path = root / SUITE / "subject_context_record.schema.json"
    schema = _read_json(path)
    branches = schema["$defs"]["notIsolatedRecord"]["anyOf"]
    if relation == "inside_repository":
        branches[2]["properties"]["neutral_cwd"]["properties"][
            "repo_membership_probe"
        ]["const"] = "outside_suite_repository"
        expected = "derived inside-repository record"
    else:
        branches[1]["properties"]["instruction_visibility"]["properties"][
            "repository_instructions"
        ]["const"] = "not_detected"
        expected = "derived repository-visible record"
    _write_json(path, schema)
    _sync_subject_schema(root, monkeypatch)
    with pytest.raises(guard.ContractError, match=expected):
        guard._check_subject_assets(root)


@pytest.mark.parametrize("surface", ["README", "design"])
def test_protocol_document_markers_are_load_bearing(
    tmp_path: Path, surface: str
) -> None:
    root = _mirror(tmp_path)
    if surface == "README":
        path = root / SUITE / "README.md"
        _replace(path, "negative probe is evidence, not proof", "negative probe proves isolation")
        expected = "README missing"
    else:
        path = root / DESIGN
        _replace(path, "DESIGN-FROZEN / PROSPECTIVE-ONLY", "DRAFT")
        expected = "design missing"
    with pytest.raises(guard.ContractError, match=expected):
        guard._check_docs(root)


@pytest.mark.parametrize(
    "relative",
    [
        "runs/future-window/hidden-row.json",
        "future-contract-record.JSON",
        "archive/nonstandard-name.json",
    ],
)
def test_contract_row_discovery_is_recursive_and_filename_independent(
    tmp_path: Path, relative: str
) -> None:
    root = _mirror(tmp_path)
    _write_json(
        root / SUITE / relative,
        {
            "measurement_contract": "heldout-measurement/1.1",
            "suite": "revision_claim_drift",
        },
    )
    with pytest.raises(guard.ContractError, match="contract-marked measurement row"):
        guard._check_history(root)


def test_escaped_contract_marker_is_discovered(tmp_path: Path) -> None:
    root = _mirror(tmp_path)
    path = root / SUITE / "runs/future-window/escaped.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        '{"measurement\\u005fcontract":"heldout-measurement/1.1",'
        '"suite":"revision_claim_drift"}\n',
        encoding="utf-8",
    )
    with pytest.raises(guard.ContractError, match="contract-marked measurement row"):
        guard._check_history(root)


@pytest.mark.parametrize("mutation", ["delete", "hash"])
def test_canonical_claim_ladder_target_is_required(
    tmp_path: Path, mutation: str
) -> None:
    root = _mirror(tmp_path)
    ladder = root / LADDER
    if mutation == "delete":
        ladder.unlink()
        expected = "canonical claim-strength ladder: missing"
    else:
        ladder.write_bytes(ladder.read_bytes() + b"\n")
        expected = "ladder target hash drifted"
    with pytest.raises(guard.ContractError, match=expected):
        guard._check_rubric(root)


def test_canonical_claim_ladder_headings_are_load_bearing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _mirror(tmp_path)
    ladder = root / LADDER
    _replace(ladder, "## The ladder", "## Local ladder summary")
    old_hash = guard.CLAIM_LADDER_SHA256
    new_hash = _digest(ladder)
    monkeypatch.setattr(guard, "CLAIM_LADDER_SHA256", new_hash)
    rubric = root / SUITE / "adjudication_rubric_v2.md"
    _replace(rubric, old_hash, new_hash)
    _sync_v2_rubric(root, monkeypatch)
    with pytest.raises(guard.ContractError, match="ladder target headings drifted"):
        guard._check_rubric(root)




def _future_bundle(
    tmp_path: Path, status: str = "machine_supported"
) -> tuple[Path, dict[str, Any], Path, Path]:
    """Create a fully joined synthetic future row without executing an eval."""
    root = tmp_path / f"future-{status}"
    for relative in (
        MEASUREMENT_SCHEMA,
        EXECUTION_SCHEMA,
        SUITE / "subject_context_record.schema.json",
        LAUNCHER_SCHEMA,
        CALL_PLAN_SCHEMA,
        SUITE / "heldout_set.json",
    ):
        _copy_file(root, relative)

    run_id = "future-ni" if status == "not_isolated" else f"future-{status.replace('_', '-')}"
    commit = "a" * 40
    subject_model_id = "synthetic-subject/not-executed"
    run_rel = SUITE / "runs" / run_id
    context_ref = (run_rel / "subject-context.json").as_posix()
    launcher_ref = (run_rel / "launcher-config.json").as_posix()
    plan_ref = (run_rel / "subject-call-plan.json").as_posix()
    manifest_ref = (run_rel / "execution-manifest.json").as_posix()
    context_path = root / context_ref
    launcher_path = root / launcher_ref
    plan_path = root / plan_ref
    manifest_path = root / manifest_ref

    fixture_by_status = {
        "machine_supported": "subject_context_machine_supported.json",
        "attested_only": "subject_context_attested_only.json",
        "not_isolated": "subject_context_not_isolated.json",
        "unknown": "subject_context_unknown.json",
    }
    context = _fixture(fixture_by_status[status])
    context["run_id"] = run_id
    context["suite_commit"] = commit
    context["execution_manifest"]["ref"] = manifest_ref
    context["recorded_at"] = "2026-08-10T01:00:04Z"
    if context["context_probe"]["status"] != "not_run":
        context["context_probe"]["started_at"] = "2026-08-10T01:00:00Z"
        context["context_probe"]["completed_at"] = "2026-08-10T01:00:02Z"
    if context["attestation"] is not None:
        context["attestation"]["attested_at"] = "2026-08-10T01:00:03Z"

    policy_by_membership = {
        "outside_suite_repository": "fresh_outside_suite_repository",
        "inside_suite_repository": "inside_suite_repository",
        "unresolved": "unresolved",
    }
    launcher = {
        "schema_version": "revision-claim-drift-launcher-config/1.0",
        "suite": "revision_claim_drift",
        "run_id": run_id,
        "sealed_at": "2026-08-10T00:59:40Z",
        "applies_to": ["context_probe", "subject_fleet"],
        "launcher": {
            "client_id": "synthetic-cli",
            "client_version": "0.0-test",
            "mode": context["cli"]["mode"],
            "bare_requested": context["cli"]["bare_requested"],
            "bare_used": context["cli"]["bare_used"],
            "authentication_result": context["cli"]["authentication_result"],
        },
        "working_directory": {
            "policy": policy_by_membership[
                context["neutral_cwd"]["repo_membership_probe"]
            ],
            "pwd_p_sha256": context["neutral_cwd"]["pwd_p_sha256"],
        },
        "instruction_loading": {
            "repository_instructions": "disabled",
            "global_instructions": "enabled",
        },
        "invocation_sha256": "0" * 64,
        "data_minimization": {
            "raw_command_stored": False,
            "raw_environment_stored": False,
            "raw_physical_cwd_stored": False,
            "raw_instruction_content_stored": False,
        },
    }
    launcher["invocation_sha256"] = _canonical_object_digest(
        {
            key: launcher[key]
            for key in ("launcher", "working_directory", "instruction_loading")
        }
    )
    _write_json(launcher_path, launcher)
    launcher_binding = {"ref": launcher_ref, "sha256": _digest(launcher_path)}
    context["cli"]["launcher_config"] = copy.deepcopy(launcher_binding)

    item_ids = [f"rp-{index:02d}" for index in range(1, 9)]
    control_ids = {"rp-07", "rp-08"}
    subject_specs = [
        {
            "item_id": item_id,
            "item_replicate_id": f"{item_id}.single.r{replicate_index}",
            "replicate_index": replicate_index,
            "arm_id": "single",
            "control_item": item_id in control_ids,
        }
        for item_id in item_ids
        for replicate_index in (1, 2)
    ]
    judge_specs = [
        {
            "judge_id": judge_id,
            "model_id": f"{judge_id}/not-executed",
            "model_family": judge_id,
            "blinded_to": ["arm_identity", "control_status", "mechanism_state"],
        }
        for judge_id in ("judge-a", "judge-b")
    ]
    call_specs = [
        {
            **subject,
            "call_id": f"subject.{subject['item_replicate_id']}",
            "role": "subject",
            "judge_id": None,
        }
        for subject in subject_specs
    ] + [
        {
            **subject,
            "call_id": f"judge.{judge_id}.{subject['item_replicate_id']}",
            "role": "judge",
            "judge_id": judge_id,
        }
        for judge_id in ("judge-a", "judge-b")
        for subject in subject_specs
    ]
    planned_calls: list[dict[str, Any]] = []
    raw_paths = [context_ref, launcher_ref, plan_ref, manifest_ref]
    plan_judges: list[dict[str, Any]] = []
    for judge in judge_specs:
        template_ref = (
            run_rel / "raw" / f"judge.{judge['judge_id']}.template.txt"
        ).as_posix()
        template_path = root / template_ref
        template_path.parent.mkdir(parents=True, exist_ok=True)
        template_path.write_text(
            f"synthetic frozen template for {judge['judge_id']}\n",
            encoding="utf-8",
        )
        raw_paths.append(template_ref)
        plan_judges.append(
            {
                **judge,
                "prompt_template": {
                    "ref": template_ref,
                    "sha256": _digest(template_path),
                },
            }
        )
    output_hashes: list[str] = []
    prompt_hashes: list[str] = []
    judge_plan_by_id = {judge["judge_id"]: judge for judge in plan_judges}
    for index, spec in enumerate(call_specs, start=1):
        call_id = spec["call_id"]
        role = spec["role"]
        prompt_ref = (run_rel / "raw" / f"{call_id}.prompt.txt").as_posix()
        output_ref = (run_rel / "raw" / f"{call_id}.output.txt").as_posix()
        prompt_path = root / prompt_ref
        output_path = root / output_ref
        prompt_path.parent.mkdir(parents=True, exist_ok=True)
        if role == "subject":
            prompt_path.write_text(
                f"synthetic {role} prompt {index}\n", encoding="utf-8"
            )
            prompt_binding: dict[str, Any] = {
                "ref": prompt_ref,
                "sha256": _digest(prompt_path),
            }
        else:
            plan_judge = judge_plan_by_id[spec["judge_id"]]
            template_ref = plan_judge["prompt_template"]["ref"]
            subject_output_ref = (
                run_rel
                / "raw"
                / f"subject.{spec['item_replicate_id']}.output.txt"
            ).as_posix()
            subject_prompt_ref = (
                run_rel
                / "raw"
                / f"subject.{spec['item_replicate_id']}.prompt.txt"
            ).as_posix()
            prompt_path.write_bytes(
                (root / template_ref).read_bytes()
                + guard.JUDGE_SUBJECT_INPUT_SEPARATOR
                + (root / subject_prompt_ref).read_bytes()
                + guard.JUDGE_SUBJECT_OUTPUT_SEPARATOR
                + (root / subject_output_ref).read_bytes()
            )
            prompt_binding = {
                "ref": prompt_ref,
                "sha256": None,
                "composition": "template_then_subject_input_then_subject_output/1.0",
                "template_ref": template_ref,
                "subject_prompt_ref": subject_prompt_ref,
                "subject_output_ref": subject_output_ref,
            }
        output_path.write_text(f"synthetic {role} output {index}\n", encoding="utf-8")
        raw_paths.extend((prompt_ref, output_ref))
        prompt_hashes.append(_digest(prompt_path))
        output_hashes.append(_digest(output_path))
        planned_calls.append(
            {
                "call_id": call_id,
                "sequence_index": index,
                "role": role,
                "judge_id": spec["judge_id"],
                "item_id": spec["item_id"],
                "item_replicate_id": spec["item_replicate_id"],
                "replicate_index": spec["replicate_index"],
                "arm_id": spec["arm_id"],
                "control_item": spec["control_item"],
                "prompt": prompt_binding,
                "output_ref": output_ref,
            }
        )

    plan = {
        "schema_version": "revision-claim-drift-subject-call-plan/1.0",
        "suite": "revision_claim_drift",
        "run_id": run_id,
        "suite_commit": commit,
        "subject_model_id": subject_model_id,
        "created_at": "2026-08-10T00:59:50Z",
        "launcher_config": copy.deepcopy(launcher_binding),
        "heldout_set": {
            "ref": f"{guard.SUITE_REL}/heldout_set.json",
            "sha256": guard.HISTORICAL_FILES[
                f"{guard.SUITE_REL}/heldout_set.json"
            ],
        },
        "arm_ids": ["single"],
        "judges": plan_judges,
        "calls": planned_calls,
        "data_minimization": {
            "prompt_content_embedded": False,
            "output_content_embedded": False,
        },
    }
    _write_json(plan_path, plan)
    plan_binding = {"ref": plan_ref, "sha256": _digest(plan_path)}
    context["subject_call_plan"] = copy.deepcopy(plan_binding)
    _write_json(context_path, context)

    timings = [
        (
            f"2026-08-10T01:01:{index:02d}.000Z",
            f"2026-08-10T01:01:{index:02d}.100Z",
        )
        for index in range(1, len(planned_calls) + 1)
    ]
    manifest_calls = []
    for planned, prompt_hash, output_hash, (started, completed) in zip(
        planned_calls, prompt_hashes, output_hashes, timings, strict=True
    ):
        manifest_calls.append(
            {
                "call_id": planned["call_id"],
                "sequence_index": planned["sequence_index"],
                "started_at": started,
                "completed_at": completed,
                "prompt_sha256": prompt_hash,
                "output_sha256": output_hash,
                "attempt": 1,
                "concurrency_group": None,
            }
        )
    manifest = {
        "schema_version": "heldout-execution-manifest/1.0",
        "suite": "revision_claim_drift",
        "created_at": "2026-08-10T01:02:01Z",
        "write_once": True,
        "execution_window": {
            "window_id": run_id,
            "started_at": "2026-08-10T01:01:00Z",
            "completed_at": "2026-08-10T01:01:59Z",
        },
        "calls": manifest_calls,
    }
    _write_json(manifest_path, manifest)

    row: dict[str, Any] = {
        "measurement_contract": "heldout-measurement/1.1",
        "suite": "revision_claim_drift",
        "suite_class": "llm_judged",
        "measurement_date": "2026-08-10",
        "decision_relevant": True,
        "subject": {
            "model_id": subject_model_id,
            "config": {
                "suite_commit": commit,
                "subject_context": {
                    "ref": context_ref,
                    "sha256": _digest(context_path),
                    "status": status,
                },
                "launcher_config": copy.deepcopy(launcher_binding),
                "subject_call_plan": copy.deepcopy(plan_binding),
            },
        },
        "judge_plan": {"exception": "none"},
        "judges": [],
        "aggregate": {
            "headline": {
                "metric_name": "claim_strength_hedge_drift_rate",
                "value": 0,
                "construction_rule": (
                    "Confirmed C1/C2 item-replicate flags divided by evaluated "
                    "item-replicates; flags-only adjudication makes this a lower bound."
                ),
                "estimand_status": "lower_bound",
            },
            "agreement": {
                "rate": 1.0,
                "divergent_items": [],
                "note": "Two synthetic fixture judges agree; no calls were made.",
            },
        },
        "replicates": {
            "per_item": 2,
            "rule_ref": "prospective-only",
            "spread": None,
        },
        "adjudication": {
            "applies": True,
            "rubric_ref": f"{guard.SUITE_REL}/adjudication_rubric_v2.md",
            "rubric_sha256": guard.V2_RUBRIC_SHA256,
            "rubric_precommitted": True,
            "blinded_to": [],
            "overrides": [],
            "raw_published": True,
            "resolution_direction": "flags_only",
            "resolution_rule_ref": "adjudication_rubric_v2.md#resolution",
        },
        "attempts": {
            "atomicity": "Synthetic fixture only; no dispatch occurred.",
            "partial_published": False,
            "blocked_runs": [],
        },
        "raw_outputs": {"retained": True, "paths": raw_paths},
        "preregistration": {
            "plan_ref": plan_binding["ref"],
            "plan_sha256": plan_binding["sha256"],
            "rubric_ref": f"{guard.SUITE_REL}/adjudication_rubric_v2.md",
            "rubric_sha256": guard.V2_RUBRIC_SHA256,
            "frozen_commit": commit,
            "frozen_before_dispatch": True,
            "rubric_and_plan_frozen_together": True,
            "judge_template_version": "synthetic-v1",
            "amendments_append_only": True,
            "amendments": [],
        },
        "execution_manifest": {
            "ref": manifest_ref,
            "sha256": _digest(manifest_path),
            "write_once": True,
            "claims": ["same_window", "ordering"],
        },
        "results": {
            "design": "prospective synthetic contract replay",
            "arm_roles": {
                "treatment_or_cohort_arms": ["single"],
                "variant_packet_arms": [],
            },
            "revision_claim_drift_v2": {
                "rubric_version": "2.0",
                "claim_strength_headline_criteria": ["C1", "C2"],
                "deterministic_token_criterion": "C6",
                "arm_ids": ["single"],
                "citation_attachment": {
                    "criterion": "C9",
                    "scope": "all_items_including_non_controls",
                    "reported_separately": True,
                    "evaluated_item_replicates": sorted(
                        subject["item_replicate_id"] for subject in subject_specs
                    ),
                    "control_item_replicates": sorted(
                        subject["item_replicate_id"]
                        for subject in subject_specs
                        if subject["control_item"]
                    ),
                    "finding_count": 0,
                    "decisions": [],
                    "findings": [],
                },
            },
            "subject_context_claim": guard.STATUS_CLAIMS[status],
        },
        "verdict": "Synthetic prospective row; no result was measured.",
        "caveats": [
            "Flags-only adjudication means any headline is a lower bound; this "
            "prospective synthetic replay measured no result."
        ],
    }
    for plan_judge in plan_judges:
        row["judges"].append(
            {
                "judge_id": plan_judge["judge_id"],
                "model_id": plan_judge["model_id"],
                "model_family": plan_judge["model_family"],
                "prompt_ref": plan_judge["prompt_template"]["ref"],
                "evidence_provided": "synthetic contract fixture only",
                "judging_budget": "zero live calls; fixture replay only",
                "blinded_to": plan_judge["blinded_to"],
                "per_item": [
                    {
                        "item_id": subject["item_replicate_id"],
                        "flag": False,
                        "citation_attachment": {"criterion": "C9", "flag": False},
                    }
                    for subject in subject_specs
                ],
            }
        )
    return root, row, context_path, manifest_path


def _sync_context(row: dict[str, Any], context_path: Path) -> None:
    row["subject"]["config"]["subject_context"]["sha256"] = _digest(context_path)


def _sync_manifest(row: dict[str, Any], manifest_path: Path) -> None:
    row["execution_manifest"]["sha256"] = _digest(manifest_path)


def _bound_path(root: Path, row: dict[str, Any], key: str) -> Path:
    return root / row["subject"]["config"][key]["ref"]


def _rewrite_plan(root: Path, row: dict[str, Any], plan: dict[str, Any]) -> Path:
    plan_path = _bound_path(root, row, "subject_call_plan")
    _write_json(plan_path, plan)
    digest = _digest(plan_path)
    row["subject"]["config"]["subject_call_plan"]["sha256"] = digest
    row["preregistration"]["plan_ref"] = row["subject"]["config"][
        "subject_call_plan"
    ]["ref"]
    row["preregistration"]["plan_sha256"] = digest
    context_path = root / row["subject"]["config"]["subject_context"]["ref"]
    context = _read_json(context_path)
    context["subject_call_plan"]["sha256"] = digest
    _write_json(context_path, context)
    _sync_context(row, context_path)
    return plan_path


def _rewrite_launcher(
    root: Path, row: dict[str, Any], launcher: dict[str, Any]
) -> Path:
    launcher_path = _bound_path(root, row, "launcher_config")
    _write_json(launcher_path, launcher)
    binding = {
        "ref": row["subject"]["config"]["launcher_config"]["ref"],
        "sha256": _digest(launcher_path),
    }
    row["subject"]["config"]["launcher_config"] = copy.deepcopy(binding)

    plan_path = _bound_path(root, row, "subject_call_plan")
    plan = _read_json(plan_path)
    plan["launcher_config"] = copy.deepcopy(binding)
    _write_json(plan_path, plan)
    plan_digest = _digest(plan_path)
    row["subject"]["config"]["subject_call_plan"]["sha256"] = plan_digest
    row["preregistration"]["plan_ref"] = row["subject"]["config"][
        "subject_call_plan"
    ]["ref"]
    row["preregistration"]["plan_sha256"] = plan_digest

    context_path = root / row["subject"]["config"]["subject_context"]["ref"]
    context = _read_json(context_path)
    context["cli"]["launcher_config"] = copy.deepcopy(binding)
    context["subject_call_plan"]["sha256"] = plan_digest
    _write_json(context_path, context)
    _sync_context(row, context_path)
    return launcher_path


def _add_c9_finding(root: Path, row: dict[str, Any]) -> Path:
    run_prefix = Path(row["subject"]["config"]["subject_context"]["ref"]).parent
    finding_id = "C9-F-001"
    item_replicate_id = "rp-01.single.r1"
    evidence_ref = (run_prefix / "c9" / f"{finding_id}.json").as_posix()
    evidence_path = root / evidence_ref
    attachment_contents = {
        "citation_tokens": "[Smith, 2024]\n",
        "original_attachment": "Original proposition <- [Smith, 2024]\n",
        "revised_attachment": "Different proposition <- [Smith, 2024]\n",
    }
    attachment_suffixes = {
        "citation_tokens": "citation-tokens.txt",
        "original_attachment": "original-attachment.txt",
        "revised_attachment": "revised-attachment.txt",
    }
    bindings: dict[str, dict[str, str]] = {}
    for field, content in attachment_contents.items():
        ref = (run_prefix / "c9" / f"{finding_id}.{attachment_suffixes[field]}").as_posix()
        path = root / ref
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        bindings[field] = {"ref": ref, "sha256": _digest(path)}
    _write_json(
        evidence_path,
        {
            "schema_version": "revision-claim-drift-c9-evidence/1.0",
            "suite": "revision_claim_drift",
            "run_id": run_prefix.name,
            "finding_id": finding_id,
            "item_replicate_id": item_replicate_id,
            "criterion": "C9",
            "raw_flags": [{"judge_id": "judge-a", "criterion": "C9", "flag": True}],
            "adjudication": {
                "disposition": "confirmed",
                "authorization": "unauthorized_under_C3",
            },
            "citation_tokens": bindings["citation_tokens"],
            "original_attachment": bindings["original_attachment"],
            "revised_attachment": bindings["revised_attachment"],
            "data_minimization": {"raw_rationale_stored": False},
        },
    )
    layer = row["results"]["revision_claim_drift_v2"]["citation_attachment"]
    layer["finding_count"] = 1
    layer["decisions"] = [
        {
            "decision_id": f"c9d.judge-a.{item_replicate_id}",
            "judge_id": "judge-a",
            "item_replicate_id": item_replicate_id,
            "raw_flag": True,
            "disposition": "confirmed",
            "criterion_ref": "C9",
            "reason_code": "violation_confirmed",
            "finding_id": finding_id,
        }
    ]
    layer["findings"] = [
        {
            "finding_id": finding_id,
            "item_replicate_id": item_replicate_id,
            "criterion": "C9",
            "authorization": "unauthorized_under_C3",
            "citation_tokens_ref": bindings["citation_tokens"]["ref"],
            "citation_tokens_sha256": bindings["citation_tokens"]["sha256"],
            "original_attachment_ref": bindings["original_attachment"]["ref"],
            "original_attachment_sha256": bindings["original_attachment"]["sha256"],
            "revised_attachment_ref": bindings["revised_attachment"]["ref"],
            "revised_attachment_sha256": bindings["revised_attachment"]["sha256"],
            "evidence_ref": evidence_ref,
            "evidence_sha256": _digest(evidence_path),
            "raw_flag_judge_ids": ["judge-a"],
            "adjudication_disposition": "confirmed",
        }
    ]
    row["judges"][0]["per_item"][0]["citation_attachment"]["flag"] = True
    row["raw_outputs"]["paths"].extend(
        [binding["ref"] for binding in bindings.values()] + [evidence_ref]
    )
    return evidence_path


@pytest.mark.parametrize(
    "status", ["machine_supported", "attested_only", "not_isolated", "unknown"]
)
def test_future_1_1_context_replay_accepts_supported_statuses(
    tmp_path: Path, status: str
) -> None:
    root, row, _, _ = _future_bundle(tmp_path, status)
    errors, warnings = validate_report(row)
    assert errors == []
    assert warnings == []
    guard.validate_prospective_measurement(row, root)


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        ("missing", "missing subject.config.subject_context"),
        ("ref", "must end in subject-context.json"),
        ("hash", "row hash mismatch"),
        ("status", "binding status differs"),
        ("raw_path", "appear verbatim in raw_outputs.paths"),
    ],
)
def test_future_context_binding_fails_closed(
    tmp_path: Path, mutation: str, expected: str
) -> None:
    root, row, context_path, _ = _future_bundle(tmp_path)
    binding = row["subject"]["config"]["subject_context"]
    if mutation == "missing":
        del row["subject"]["config"]["subject_context"]
    elif mutation == "ref":
        bad_ref = context_path.with_name("context.json").relative_to(root).as_posix()
        shutil.copyfile(context_path, root / bad_ref)
        binding["ref"] = bad_ref
        binding["sha256"] = _digest(root / bad_ref)
        row["raw_outputs"]["paths"] = [bad_ref]
    elif mutation == "hash":
        binding["sha256"] = "0" * 64
    elif mutation == "status":
        binding["status"] = "unknown"
    else:
        row["raw_outputs"]["paths"] = []
    with pytest.raises(guard.ContractError, match=expected):
        guard.validate_prospective_measurement(row, root)


def test_future_context_run_id_must_match_parent_path(tmp_path: Path) -> None:
    root, row, context_path, _ = _future_bundle(tmp_path)
    context = _read_json(context_path)
    context["run_id"] = "different-window"
    _write_json(context_path, context)
    _sync_context(row, context_path)
    with pytest.raises(guard.ContractError, match="not the canonical run sibling"):
        guard.validate_prospective_measurement(row, root)


@pytest.mark.parametrize("mutation", ["ref", "hash"])
def test_future_manifest_ref_and_hash_are_bound(
    tmp_path: Path, mutation: str
) -> None:
    root, row, _, _ = _future_bundle(tmp_path)
    if mutation == "ref":
        row["execution_manifest"]["ref"] = (
            f"{guard.RUNS_PREFIX}other-run/execution-manifest.json"
        )
        expected = "row/context execution_manifest ref mismatch"
    else:
        row["execution_manifest"]["sha256"] = "0" * 64
        expected = "execution-manifest hash mismatch"
    with pytest.raises(guard.ContractError, match=expected):
        guard.validate_prospective_measurement(row, root)


def test_context_record_must_precede_first_scored_call(tmp_path: Path) -> None:
    root, row, context_path, _ = _future_bundle(tmp_path)
    context = _read_json(context_path)
    context["recorded_at"] = "2026-08-10T01:01:02Z"
    _write_json(context_path, context)
    _sync_context(row, context_path)
    with pytest.raises(guard.ContractError, match="gate was not sealed before"):
        guard.validate_prospective_measurement(row, root)


def test_probe_completion_cannot_follow_context_record(tmp_path: Path) -> None:
    root, row, context_path, _ = _future_bundle(tmp_path)
    context = _read_json(context_path)
    context["context_probe"]["completed_at"] = "2026-08-10T01:00:05Z"
    _write_json(context_path, context)
    _sync_context(row, context_path)
    with pytest.raises(guard.ContractError, match="probe timestamps"):
        guard.validate_prospective_measurement(row, root)


def test_attestation_cannot_precede_completed_probe(tmp_path: Path) -> None:
    root, row, context_path, _ = _future_bundle(tmp_path, "attested_only")
    context = _read_json(context_path)
    context["attestation"]["attested_at"] = "2026-08-10T00:59:59Z"
    _write_json(context_path, context)
    _sync_context(row, context_path)
    with pytest.raises(guard.ContractError, match="attestation precedes"):
        guard.validate_prospective_measurement(row, root)


@pytest.mark.parametrize("mutation", ["row_suite", "config_commit", "frozen_commit"])
def test_future_suite_and_frozen_commit_bindings(
    tmp_path: Path, mutation: str
) -> None:
    root, row, _, _ = _future_bundle(tmp_path)
    if mutation == "row_suite":
        row["suite"] = "other_suite"
        expected = "row suite mismatch"
    elif mutation == "config_commit":
        row["subject"]["config"]["suite_commit"] = "b" * 40
        expected = "suite_commit differs"
    else:
        row["preregistration"]["frozen_commit"] = "b" * 40
        expected = "frozen_commit differs"
    with pytest.raises(guard.ContractError, match=expected):
        guard.validate_prospective_measurement(row, root)


def test_launcher_config_row_hash_replays_exactly(tmp_path: Path) -> None:
    root, row, _, _ = _future_bundle(tmp_path)
    row["subject"]["config"]["launcher_config"]["sha256"] = "9" * 64
    with pytest.raises(guard.ContractError, match="launcher_config binding mismatch"):
        guard.validate_prospective_measurement(row, root)


def test_future_adjudication_is_flags_only(tmp_path: Path) -> None:
    root, row, _, _ = _future_bundle(tmp_path)
    row["adjudication"]["resolution_direction"] = "bidirectional"
    with pytest.raises(guard.ContractError, match="must be flags_only"):
        guard.validate_prospective_measurement(row, root)


@pytest.mark.parametrize("mutation", ["criterion", "scope", "separation", "extra"])
def test_future_c9_result_layer_is_closed_and_separate(
    tmp_path: Path, mutation: str
) -> None:
    root, row, _, _ = _future_bundle(tmp_path)
    layer = row["results"]["revision_claim_drift_v2"]["citation_attachment"]
    if mutation == "criterion":
        layer["criterion"] = "C8"
    elif mutation == "scope":
        layer["scope"] = "non_controls_only"
    elif mutation == "separation":
        layer["reported_separately"] = False
    else:
        layer["affects_headline"] = True
    with pytest.raises(guard.ContractError, match="closed separate C9"):
        guard.validate_prospective_measurement(row, root)


def test_c9_cannot_be_smuggled_into_the_generic_aggregate_headline(
    tmp_path: Path,
) -> None:
    root, row, _, _ = _future_bundle(tmp_path)
    row["aggregate"]["headline"]["metric_name"] = "C9_citation_attachment_rate"
    row["aggregate"]["headline"]["construction_rule"] = (
        "C9 citation-attachment flags-only adjudication defines this lower bound."
    )
    with pytest.raises(guard.ContractError):
        guard.validate_prospective_measurement(row, root)


@pytest.mark.parametrize(
    "wording",
    [
        "The subject ran in a clean context.",
        "The subject was fully isolated.",
        "Prompt isolation was verified.",
        "Repository-instruction isolation was achieved.",
    ],
)
def test_unqualified_isolation_language_is_rejected(
    tmp_path: Path, wording: str
) -> None:
    root, row, _, _ = _future_bundle(tmp_path)
    row["verdict"] = wording
    with pytest.raises(
        guard.ContractError,
        match="isolation wording is allowed only",
    ):
        guard.validate_prospective_measurement(row, root)


def test_status_claim_ceiling_is_exact_for_unknown_status(tmp_path: Path) -> None:
    root, row, _, _ = _future_bundle(tmp_path, "unknown")
    row["results"]["subject_context_claim"] = (
        "repository-instruction isolated (machine-supported)"
    )
    with pytest.raises(guard.ContractError, match="exact status-derived ceiling"):
        guard.validate_prospective_measurement(row, root)


@pytest.mark.parametrize(
    "claim_key",
    ["repository_instruction_isolation_confirmed", "clean_context"],
)
def test_typed_boolean_keys_cannot_publish_an_unsupported_isolation_claim(
    tmp_path: Path, claim_key: str
) -> None:
    root, row, _, _ = _future_bundle(tmp_path, "unknown")
    row["results"][claim_key] = True
    with pytest.raises(guard.ContractError, match="claim-shaped isolation keys are forbidden"):
        guard.validate_prospective_measurement(row, root)


def test_manifest_window_id_must_equal_context_run_id(tmp_path: Path) -> None:
    root, row, _, manifest_path = _future_bundle(tmp_path)
    manifest = _read_json(manifest_path)
    manifest["execution_window"]["window_id"] = "different-window"
    _write_json(manifest_path, manifest)
    _sync_manifest(row, manifest_path)
    with pytest.raises(guard.ContractError, match="window ID.*run_id mismatch"):
        guard.validate_prospective_measurement(row, root)


@pytest.mark.parametrize(
    ("schema_name", "expected"),
    [
        ("subject_launcher_config.schema.json", "launcher-config schema byte identity"),
        ("subject_call_plan.schema.json", "call-plan schema byte identity"),
    ],
)
def test_prospective_companion_schema_hashes_are_load_bearing(
    tmp_path: Path, schema_name: str, expected: str
) -> None:
    root = _mirror(tmp_path)
    path = root / SUITE / schema_name
    path.write_bytes(path.read_bytes() + b"\n")
    with pytest.raises(guard.ContractError, match=expected):
        guard._check_subject_assets(root)


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        ("missing", "subject.config: keys mismatch"),
        ("ref", "launcher_config binding mismatch"),
        ("hash", "launcher-config artifact hash mismatch"),
        ("raw", "launcher-config ref must appear"),
        ("schema", "launcher-config artifact fails schema"),
        ("provenance", "working-directory policy mismatch"),
        ("invocation_hash", "launcher-config invocation hash mismatch"),
    ],
)
def test_launcher_config_binding_is_canonical_and_replayed(
    tmp_path: Path, mutation: str, expected: str
) -> None:
    root, row, _, _ = _future_bundle(tmp_path)
    config = row["subject"]["config"]
    launcher_path = _bound_path(root, row, "launcher_config")
    if mutation == "missing":
        del config["launcher_config"]
    elif mutation == "ref":
        config["launcher_config"]["ref"] = (
            f"{guard.RUNS_PREFIX}other/launcher-config.json"
        )
    elif mutation == "hash":
        launcher_path.write_bytes(launcher_path.read_bytes() + b"\n")
    elif mutation == "raw":
        row["raw_outputs"]["paths"].remove(config["launcher_config"]["ref"])
    else:
        launcher = _read_json(launcher_path)
        if mutation == "schema":
            launcher["raw_command"] = "forbidden"
        elif mutation == "invocation_hash":
            launcher["invocation_sha256"] = "0" * 64
        else:
            launcher["working_directory"]["policy"] = "inside_suite_repository"
            launcher["invocation_sha256"] = _canonical_object_digest(
                {
                    key: launcher[key]
                    for key in (
                        "launcher",
                        "working_directory",
                        "instruction_loading",
                    )
                }
            )
        _rewrite_launcher(root, row, launcher)
    with pytest.raises(guard.ContractError, match=expected):
        guard.validate_prospective_measurement(row, root)


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        ("missing", "subject.config: keys mismatch"),
        ("ref", "subject_call_plan binding mismatch"),
        ("hash", "subject-call-plan artifact hash mismatch"),
        ("raw", "subject-call-plan ref must appear"),
        ("schema", "subject-call-plan artifact fails schema"),
        ("provenance", "provenance differs"),
        ("subject_model", "provenance differs"),
        ("late", "not frozen before probe/preflight"),
    ],
)
def test_subject_call_plan_binding_is_canonical_and_precommitted(
    tmp_path: Path, mutation: str, expected: str
) -> None:
    root, row, _, _ = _future_bundle(tmp_path)
    config = row["subject"]["config"]
    plan_path = _bound_path(root, row, "subject_call_plan")
    if mutation == "missing":
        del config["subject_call_plan"]
    elif mutation == "ref":
        config["subject_call_plan"]["ref"] = (
            f"{guard.RUNS_PREFIX}other/subject-call-plan.json"
        )
    elif mutation == "hash":
        plan_path.write_bytes(plan_path.read_bytes() + b"\n")
    elif mutation == "raw":
        row["raw_outputs"]["paths"].remove(config["subject_call_plan"]["ref"])
    else:
        plan = _read_json(plan_path)
        if mutation == "schema":
            plan["uncommitted_calls"] = []
        elif mutation == "provenance":
            plan["suite_commit"] = "b" * 40
        elif mutation == "subject_model":
            plan["subject_model_id"] = "different/subject"
        else:
            plan["created_at"] = "2026-08-10T01:00:05Z"
        _rewrite_plan(root, row, plan)
    with pytest.raises(guard.ContractError, match=expected):
        guard.validate_prospective_measurement(row, root)


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        ("missing_sealed", "launcher-config artifact fails schema"),
        ("sealed_after_probe", "not sealed before probe/preflight"),
        ("sealed_after_plan", "not sealed before the subject-call plan"),
    ],
)
def test_launcher_and_call_plan_are_sealed_in_preflight_order(
    tmp_path: Path, mutation: str, expected: str
) -> None:
    root, row, _, _ = _future_bundle(tmp_path)
    launcher = _read_json(_bound_path(root, row, "launcher_config"))
    if mutation == "missing_sealed":
        del launcher["sealed_at"]
    elif mutation == "sealed_after_probe":
        launcher["sealed_at"] = "2026-08-10T01:00:01Z"
    else:
        launcher["sealed_at"] = "2026-08-10T00:59:55Z"
    _rewrite_launcher(root, row, launcher)
    with pytest.raises(guard.ContractError, match=expected):
        guard.validate_prospective_measurement(row, root)


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        ("plan_order", "same 2..8 sorted judges"),
        ("row_identity", "published judge identity/template differs"),
        ("template_ref", "prompt-template ref is not canonical"),
        ("template_hash", "prompt-template hash mismatch"),
        ("template_raw", "prompt-template ref must appear"),
        ("closed_schema", "subject-call-plan artifact fails schema"),
        ("one_family", "at least two judge model families"),
        ("decision_relevant", "decision-relevant with no judge exception"),
        ("judge_exception", "decision-relevant with no judge exception"),
    ],
)
def test_judge_roster_identity_templates_and_decision_authority_are_frozen(
    tmp_path: Path, mutation: str, expected: str
) -> None:
    root, row, _, _ = _future_bundle(tmp_path)
    plan = _read_json(_bound_path(root, row, "subject_call_plan"))
    template_ref = plan["judges"][0]["prompt_template"]["ref"]
    if mutation == "plan_order":
        plan["judges"].reverse()
        _rewrite_plan(root, row, plan)
    elif mutation == "row_identity":
        row["judges"][0]["model_id"] = "different/model"
    elif mutation == "template_ref":
        alternate_ref = template_ref.replace(".template.txt", ".alternate.txt")
        alternate_path = root / alternate_ref
        alternate_path.write_text("alternate frozen template\n", encoding="utf-8")
        row["raw_outputs"]["paths"].append(alternate_ref)
        plan["judges"][0]["prompt_template"] = {
            "ref": alternate_ref,
            "sha256": _digest(alternate_path),
        }
        row["judges"][0]["prompt_ref"] = alternate_ref
        _rewrite_plan(root, row, plan)
    elif mutation == "template_hash":
        (root / template_ref).write_bytes((root / template_ref).read_bytes() + b"drift")
    elif mutation == "template_raw":
        row["raw_outputs"]["paths"].remove(template_ref)
    elif mutation == "closed_schema":
        plan["judges"][0]["unfrozen_prompt"] = True
        _rewrite_plan(root, row, plan)
    elif mutation == "one_family":
        row["judges"][1]["model_family"] = row["judges"][0]["model_family"]
        plan["judges"][1]["model_family"] = plan["judges"][0]["model_family"]
        _rewrite_plan(root, row, plan)
    elif mutation == "decision_relevant":
        row["decision_relevant"] = False
    else:
        row["judge_plan"] = {
            "exception": "legacy_comparability",
            "legacy_baseline_ref": "measurement-historical.json",
        }
    with pytest.raises(guard.ContractError, match=expected):
        guard.validate_prospective_measurement(row, root)


@pytest.mark.parametrize("field", ["plan_ref", "plan_sha256"])
def test_preregistration_exactly_binds_the_subject_call_plan(
    tmp_path: Path, field: str
) -> None:
    root, row, _, _ = _future_bundle(tmp_path)
    row["preregistration"][field] = "0" * 64 if field.endswith("sha256") else "other"
    with pytest.raises(guard.ContractError, match="preregistration plan binding differs"):
        guard.validate_prospective_measurement(row, root)


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        ("delete_judge", "exactly cover judge x item-replicate"),
        ("reindex", "sequence indexes must be ordered"),
        ("role", "exactly cover item x arm x replicate"),
        ("judge_item", "judge-call roster differs from the frozen run design"),
    ],
)
def test_call_plan_call_roster_role_and_index_are_load_bearing(
    tmp_path: Path, mutation: str, expected: str
) -> None:
    root, row, _, _ = _future_bundle(tmp_path)
    plan_path = _bound_path(root, row, "subject_call_plan")
    plan = _read_json(plan_path)
    if mutation == "delete_judge":
        plan["calls"].pop()
    elif mutation == "reindex":
        plan["calls"][1]["sequence_index"] = 3
        plan["calls"][2]["sequence_index"] = 2
    elif mutation == "role":
        call = plan["calls"][0]
        subject_prompt_ref = call["prompt"]["ref"]
        call["role"] = "judge"
        call["judge_id"] = "judge-a"
        call["prompt"] = {
            "ref": subject_prompt_ref,
            "sha256": None,
            "composition": "template_then_subject_input_then_subject_output/1.0",
            "template_ref": plan["judges"][0]["prompt_template"]["ref"],
            "subject_prompt_ref": subject_prompt_ref,
            "subject_output_ref": call["output_ref"],
        }
    else:
        plan["calls"][16]["item_id"] = "other-item"
    _rewrite_plan(root, row, plan)
    with pytest.raises(guard.ContractError, match=expected):
        guard.validate_prospective_measurement(row, root)


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        ("prompt_drift", "subject prompt hash mismatch"),
        ("prompt_missing", "missing/unreadable path"),
        ("output_drift", "output hash differs"),
        ("output_missing", "missing/unreadable path"),
        ("prompt_raw", "planned prompt/output ref must be retained raw"),
        ("output_raw", "planned prompt/output ref must be retained raw"),
    ],
)
def test_every_call_prompt_and_output_is_hashed_and_retained(
    tmp_path: Path, mutation: str, expected: str
) -> None:
    root, row, _, _ = _future_bundle(tmp_path)
    plan = _read_json(_bound_path(root, row, "subject_call_plan"))
    prompt_ref = plan["calls"][0]["prompt"]["ref"]
    output_ref = plan["calls"][-1 if mutation == "output_drift" else 0]["output_ref"]
    if mutation == "prompt_drift":
        (root / prompt_ref).write_bytes((root / prompt_ref).read_bytes() + b"drift")
    elif mutation == "prompt_missing":
        (root / prompt_ref).unlink()
    elif mutation == "output_drift":
        (root / output_ref).write_bytes((root / output_ref).read_bytes() + b"drift")
    elif mutation == "output_missing":
        (root / output_ref).unlink()
    elif mutation == "prompt_raw":
        row["raw_outputs"]["paths"].remove(prompt_ref)
    else:
        row["raw_outputs"]["paths"].remove(output_ref)
    with pytest.raises(guard.ContractError, match=expected):
        guard.validate_prospective_measurement(row, root)


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        ("composition", "subject-call-plan artifact fails schema"),
        ("template_ref", "judge prompt dependency differs"),
        ("subject_prompt_ref", "judge prompt dependency differs"),
        ("subject_output_ref", "judge prompt dependency differs"),
        ("materialized_hash", "subject-call-plan artifact fails schema"),
        ("bytes", "judge prompt bytes do not replay"),
    ],
)
def test_judge_prompts_are_deferred_and_replay_frozen_dependencies(
    tmp_path: Path, mutation: str, expected: str
) -> None:
    root, row, _, _ = _future_bundle(tmp_path)
    plan = _read_json(_bound_path(root, row, "subject_call_plan"))
    judge_call = plan["calls"][16]
    if mutation == "composition":
        judge_call["prompt"]["composition"] = "free_form/1.0"
        _rewrite_plan(root, row, plan)
    elif mutation == "template_ref":
        judge_call["prompt"]["template_ref"] = plan["judges"][1][
            "prompt_template"
        ]["ref"]
        _rewrite_plan(root, row, plan)
    elif mutation == "subject_prompt_ref":
        judge_call["prompt"]["subject_prompt_ref"] = plan["calls"][1]["prompt"][
            "ref"
        ]
        _rewrite_plan(root, row, plan)
    elif mutation == "subject_output_ref":
        judge_call["prompt"]["subject_output_ref"] = plan["calls"][1]["output_ref"]
        _rewrite_plan(root, row, plan)
    elif mutation == "materialized_hash":
        judge_call["prompt"]["sha256"] = "0" * 64
        _rewrite_plan(root, row, plan)
    else:
        prompt_path = root / judge_call["prompt"]["ref"]
        prompt_path.write_bytes(prompt_path.read_bytes() + b"drift")
    with pytest.raises(guard.ContractError, match=expected):
        guard.validate_prospective_measurement(row, root)


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        ("delete", "does not exactly cover the call plan"),
        ("reindex", "sequence indexes must be ordered"),
        ("call_id", "differs from precommitted call plan"),
        ("prompt_hash", "differs from precommitted call plan"),
    ],
)
def test_execution_manifest_exactly_joins_the_call_plan(
    tmp_path: Path, mutation: str, expected: str
) -> None:
    root, row, _, manifest_path = _future_bundle(tmp_path)
    manifest = _read_json(manifest_path)
    if mutation == "delete":
        manifest["calls"].pop()
    elif mutation == "reindex":
        manifest["calls"][1]["sequence_index"] = 3
        manifest["calls"][2]["sequence_index"] = 2
    elif mutation == "call_id":
        manifest["calls"][0]["call_id"] = "judge-disguised-as-subject"
    else:
        manifest["calls"][0]["prompt_sha256"] = "9" * 64
    _write_json(manifest_path, manifest)
    _sync_manifest(row, manifest_path)
    with pytest.raises(guard.ContractError, match=expected):
        guard.validate_prospective_measurement(row, root)


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        ("created_before_call", "recorded before its final call completed"),
        ("created_before_window_end", "recorded before its window ended"),
        ("window_excludes_call", "execution window does not contain all calls"),
    ],
)
def test_manifest_created_and_window_ordering_is_load_bearing(
    tmp_path: Path, mutation: str, expected: str
) -> None:
    root, row, _, manifest_path = _future_bundle(tmp_path)
    manifest = _read_json(manifest_path)
    if mutation == "created_before_call":
        manifest["created_at"] = "2026-08-10T01:01:40Z"
    elif mutation == "created_before_window_end":
        manifest["execution_window"]["completed_at"] = "2026-08-10T01:04:00Z"
    else:
        manifest["execution_window"]["started_at"] = "2026-08-10T01:01:05Z"
    _write_json(manifest_path, manifest)
    _sync_manifest(row, manifest_path)
    with pytest.raises(guard.ContractError, match=expected):
        guard.validate_prospective_measurement(row, root)


def test_context_gate_precedes_every_scored_call_even_without_ordering_claim(
    tmp_path: Path,
) -> None:
    root, row, _, manifest_path = _future_bundle(tmp_path)
    manifest = _read_json(manifest_path)
    manifest["execution_window"]["started_at"] = "2026-08-10T00:59:00Z"
    manifest["calls"][16]["started_at"] = "2026-08-10T00:59:10Z"
    manifest["calls"][16]["completed_at"] = "2026-08-10T00:59:20Z"
    row["execution_manifest"]["claims"].remove("ordering")
    _write_json(manifest_path, manifest)
    _sync_manifest(row, manifest_path)
    with pytest.raises(guard.ContractError):
        guard.validate_prospective_measurement(row, root)


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        ("plan_chronology", "not chronological by plan order"),
        ("judge_overlap", "judge calls began before the subject fleet completed"),
    ],
)
def test_manifest_call_times_follow_plan_order_and_separate_judge_dispatch(
    tmp_path: Path, mutation: str, expected: str
) -> None:
    root, row, _, manifest_path = _future_bundle(tmp_path)
    manifest = _read_json(manifest_path)
    if mutation == "plan_chronology":
        manifest["calls"][1]["started_at"] = "2026-08-10T01:01:00.500Z"
        manifest["calls"][1]["completed_at"] = "2026-08-10T01:01:00.600Z"
    else:
        manifest["calls"][16]["started_at"] = "2026-08-10T01:01:16.050Z"
        manifest["calls"][16]["completed_at"] = "2026-08-10T01:01:16.150Z"
    _write_json(manifest_path, manifest)
    _sync_manifest(row, manifest_path)
    with pytest.raises(guard.ContractError, match=expected):
        guard.validate_prospective_measurement(row, root)


def test_c9_zero_finding_layer_still_covers_the_subject_roster(tmp_path: Path) -> None:
    root, row, _, _ = _future_bundle(tmp_path)
    layer = row["results"]["revision_claim_drift_v2"]["citation_attachment"]
    assert len(layer["evaluated_item_replicates"]) == 16
    assert layer["control_item_replicates"] == [
        "rp-07.single.r1",
        "rp-07.single.r2",
        "rp-08.single.r1",
        "rp-08.single.r2",
    ]
    assert layer["finding_count"] == 0
    assert layer["decisions"] == []
    assert layer["findings"] == []
    guard.validate_prospective_measurement(row, root)


@pytest.mark.parametrize("mutation", ["missing", "extra", "control"])
def test_c9_roster_is_derived_from_precommitted_subject_calls(
    tmp_path: Path, mutation: str
) -> None:
    root, row, _, _ = _future_bundle(tmp_path)
    layer = row["results"]["revision_claim_drift_v2"]["citation_attachment"]
    if mutation == "missing":
        layer["evaluated_item_replicates"] = []
    elif mutation == "extra":
        layer["evaluated_item_replicates"].append("unplanned-r9")
    else:
        layer["control_item_replicates"] = ["rp-07.single.r1"]
    with pytest.raises(guard.ContractError):
        guard.validate_prospective_measurement(row, root)


def test_c9_well_formed_finding_with_bound_evidence_passes(tmp_path: Path) -> None:
    root, row, _, _ = _future_bundle(tmp_path)
    _add_c9_finding(root, row)
    guard.validate_prospective_measurement(row, root)


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        ("item", "unevaluated item-replicate"),
        ("criterion", "finding authority"),
        ("authorization", "finding authority"),
        ("evidence_hash", "evidence artifact hash mismatch"),
        ("evidence_ref", "evidence_ref is not the canonical run-local path"),
        ("raw", "evidence_ref must appear"),
        ("count", "finding_count must equal"),
    ],
)
def test_c9_finding_authority_evidence_and_count_fail_closed(
    tmp_path: Path, mutation: str, expected: str
) -> None:
    root, row, _, _ = _future_bundle(tmp_path)
    evidence_path = _add_c9_finding(root, row)
    layer = row["results"]["revision_claim_drift_v2"]["citation_attachment"]
    finding = layer["findings"][0]
    if mutation == "item":
        finding["item_replicate_id"] = "unplanned-r9"
    elif mutation == "criterion":
        finding["criterion"] = "C8"
    elif mutation == "authorization":
        finding["authorization"] = "authorized_under_C3"
    elif mutation == "evidence_hash":
        finding["evidence_sha256"] = "0" * 64
    elif mutation == "evidence_ref":
        finding["evidence_ref"] = "evals/heldout/other/evidence.json"
    elif mutation == "raw":
        row["raw_outputs"]["paths"].remove(evidence_path.relative_to(root).as_posix())
    else:
        layer["finding_count"] = 0
    with pytest.raises(guard.ContractError, match=expected):
        guard.validate_prospective_measurement(row, root)


def test_generic_non_c9_judge_flags_do_not_create_a_c9_finding(
    tmp_path: Path,
) -> None:
    root, row, _, _ = _future_bundle(tmp_path)
    for judge in row["judges"]:
        judge["per_item"][0]["flag"] = True
    guard.validate_prospective_measurement(row, root)


def test_published_c9_finding_requires_typed_raw_flag_authority(
    tmp_path: Path,
) -> None:
    root, row, _, _ = _future_bundle(tmp_path)
    _add_c9_finding(root, row)
    finding = row["results"]["revision_claim_drift_v2"]["citation_attachment"][
        "findings"
    ][0]
    del finding["raw_flag_judge_ids"]
    with pytest.raises(guard.ContractError):
        guard.validate_prospective_measurement(row, root)


def test_generic_true_flag_cannot_override_typed_false_c9_verdict(
    tmp_path: Path,
) -> None:
    root, row, _, _ = _future_bundle(tmp_path)
    _add_c9_finding(root, row)
    raw_row = row["judges"][0]["per_item"][0]
    raw_row["flag"] = True
    raw_row["citation_attachment"]["flag"] = False
    with pytest.raises(guard.ContractError, match="exactly resolve every typed raw true flag"):
        guard.validate_prospective_measurement(row, root)


def test_typed_raw_true_c9_flag_cannot_be_omitted_from_decisions(
    tmp_path: Path,
) -> None:
    root, row, _, _ = _future_bundle(tmp_path)
    row["judges"][0]["per_item"][0]["citation_attachment"]["flag"] = True
    with pytest.raises(guard.ContractError, match="exactly resolve every typed raw true"):
        guard.validate_prospective_measurement(row, root)


def test_c5_cannot_reject_a_noncontrol_c9_raw_flag(tmp_path: Path) -> None:
    root, row, _, _ = _future_bundle(tmp_path)
    item_replicate_id = "rp-01.single.r1"
    row["judges"][0]["per_item"][0]["citation_attachment"]["flag"] = True
    layer = row["results"]["revision_claim_drift_v2"]["citation_attachment"]
    layer["decisions"] = [
        {
            "decision_id": f"c9d.judge-a.{item_replicate_id}",
            "judge_id": "judge-a",
            "item_replicate_id": item_replicate_id,
            "raw_flag": True,
            "disposition": "rejected",
            "criterion_ref": "C5",
            "reason_code": "authorized_under_C3",
            "finding_id": None,
        }
    ]
    with pytest.raises(guard.ContractError, match="invalid closed reason"):
        guard.validate_prospective_measurement(row, root)


def test_generic_override_cannot_route_c9_or_citation_attachment(
    tmp_path: Path,
) -> None:
    root, row, _, _ = _future_bundle(tmp_path)
    row["adjudication"]["overrides"] = [
        {
            "item_id": "rp-01.single.r1",
            "judge_id": "judge-a",
            "raw": "citation_attachment C9=true",
            "adjudicated": "citation_attachment=false",
            "criterion_ref": "C5",
        }
    ]
    with pytest.raises(guard.ContractError, match="cannot be routed through generic overrides"):
        guard.validate_prospective_measurement(row, root)


@pytest.mark.parametrize("mutation", ["missing_finding", "wrong_reason", "wrong_id"])
def test_confirmed_c9_decision_mapping_is_closed(
    tmp_path: Path, mutation: str
) -> None:
    root, row, _, _ = _future_bundle(tmp_path)
    _add_c9_finding(root, row)
    layer = row["results"]["revision_claim_drift_v2"]["citation_attachment"]
    decision = layer["decisions"][0]
    if mutation == "missing_finding":
        decision["finding_id"] = "C9-F-missing"
    elif mutation == "wrong_reason":
        decision["reason_code"] = "authorized_under_C3"
    else:
        decision["decision_id"] = "noncanonical"
    with pytest.raises(guard.ContractError):
        guard.validate_prospective_measurement(row, root)


def test_confirmed_c9_decision_cannot_be_relabelled_to_another_item(
    tmp_path: Path,
) -> None:
    root, row, _, _ = _future_bundle(tmp_path)
    evidence_path = _add_c9_finding(root, row)
    item_b = "rp-01.single.r2"
    row["judges"][0]["per_item"][1]["citation_attachment"]["flag"] = True
    layer = row["results"]["revision_claim_drift_v2"]["citation_attachment"]
    layer["decisions"].append(
        {
            "decision_id": f"c9d.judge-a.{item_b}",
            "judge_id": "judge-a",
            "item_replicate_id": item_b,
            "raw_flag": True,
            "disposition": "rejected",
            "criterion_ref": "C9",
            "reason_code": "no_citation_attachment_violation",
            "finding_id": None,
        }
    )
    finding = layer["findings"][0]
    finding["item_replicate_id"] = item_b
    evidence = _read_json(evidence_path)
    evidence["item_replicate_id"] = item_b
    _write_json(evidence_path, evidence)
    finding["evidence_sha256"] = _digest(evidence_path)
    with pytest.raises(guard.ContractError, match="confirmed decisions"):
        guard.validate_prospective_measurement(row, root)


def test_report_replicate_count_must_match_precommitted_subject_roster(
    tmp_path: Path,
) -> None:
    root, row, _, _ = _future_bundle(tmp_path)
    row["replicates"]["per_item"] = 3
    with pytest.raises(guard.ContractError):
        guard.validate_prospective_measurement(row, root)


def test_extra_unjudged_subject_call_is_rejected(tmp_path: Path) -> None:
    root, row, _, _ = _future_bundle(tmp_path)
    plan = _read_json(_bound_path(root, row, "subject_call_plan"))
    extra = copy.deepcopy(plan["calls"][0])
    extra["call_id"] = "subject-unjudged-002"
    extra["sequence_index"] = 4
    extra["item_id"] = "item-002"
    extra["item_replicate_id"] = "item-002-r1"
    extra["prompt"] = copy.deepcopy(plan["calls"][1]["prompt"])
    extra["output_ref"] = plan["calls"][1]["output_ref"]
    plan["calls"].append(extra)
    _rewrite_plan(root, row, plan)
    with pytest.raises(guard.ContractError):
        guard.validate_prospective_measurement(row, root)


def test_c9_evidence_cannot_alias_an_arbitrary_retained_artifact(tmp_path: Path) -> None:
    root, row, _, _ = _future_bundle(tmp_path)
    _add_c9_finding(root, row)
    finding = row["results"]["revision_claim_drift_v2"]["citation_attachment"][
        "findings"
    ][0]
    context_ref = row["subject"]["config"]["subject_context"]["ref"]
    finding["evidence_ref"] = context_ref
    finding["evidence_sha256"] = _digest(root / context_ref)
    with pytest.raises(guard.ContractError):
        guard.validate_prospective_measurement(row, root)


def test_c9_evidence_cannot_use_unreplayed_placeholder_hashes(tmp_path: Path) -> None:
    root, row, _, _ = _future_bundle(tmp_path)
    _add_c9_finding(root, row)
    finding = row["results"]["revision_claim_drift_v2"]["citation_attachment"][
        "findings"
    ][0]
    finding["citation_tokens_sha256"] = "0" * 64
    finding["original_attachment_sha256"] = "0" * 64
    finding["revised_attachment_sha256"] = "0" * 64
    with pytest.raises(guard.ContractError):
        guard.validate_prospective_measurement(row, root)


def test_boolean_finding_count_is_not_an_integer_count(tmp_path: Path) -> None:
    root, row, _, _ = _future_bundle(tmp_path)
    _add_c9_finding(root, row)
    row["results"]["revision_claim_drift_v2"]["citation_attachment"][
        "finding_count"
    ] = True
    with pytest.raises(guard.ContractError):
        guard.validate_prospective_measurement(row, root)


@pytest.mark.parametrize(
    ("field", "mutation"),
    [
        (field, mutation)
        for field in (
            "citation_tokens",
            "original_attachment",
            "revised_attachment",
        )
        for mutation in ("ref", "hash", "raw", "empty")
    ],
)
def test_c9_attachment_artifacts_are_canonical_hashed_nonempty_and_retained(
    tmp_path: Path, field: str, mutation: str
) -> None:
    root, row, _, _ = _future_bundle(tmp_path)
    _add_c9_finding(root, row)
    finding = row["results"]["revision_claim_drift_v2"]["citation_attachment"][
        "findings"
    ][0]
    ref_key = f"{field}_ref"
    hash_key = f"{field}_sha256"
    ref = finding[ref_key]
    if mutation == "ref":
        finding[ref_key] = ref.replace(".txt", ".other.txt")
    elif mutation == "hash":
        finding[hash_key] = "0" * 64
    elif mutation == "raw":
        row["raw_outputs"]["paths"].remove(ref)
    else:
        (root / ref).write_bytes(b"")
        finding[hash_key] = _digest(root / ref)
    with pytest.raises(guard.ContractError):
        guard.validate_prospective_measurement(row, root)


@pytest.mark.parametrize("mutation", ["missing", "overlap", "unsorted"])
def test_published_arm_roles_exactly_partition_call_plan_arms(
    tmp_path: Path, mutation: str
) -> None:
    root, row, _, _ = _future_bundle(tmp_path)
    roles = row["results"]["arm_roles"]
    if mutation == "missing":
        roles["treatment_or_cohort_arms"] = []
    elif mutation == "overlap":
        roles["variant_packet_arms"] = ["single"]
    else:
        roles["treatment_or_cohort_arms"] = ["single", "alpha"]
        roles["variant_packet_arms"] = []
    with pytest.raises(guard.ContractError, match="arm roles do not exactly partition"):
        guard.validate_prospective_measurement(row, root)


def test_call_plan_binds_exact_frozen_heldout_set(tmp_path: Path) -> None:
    root, row, _, _ = _future_bundle(tmp_path)
    plan = _read_json(_bound_path(root, row, "subject_call_plan"))
    plan["heldout_set"]["sha256"] = "0" * 64
    _rewrite_plan(root, row, plan)
    with pytest.raises(guard.ContractError, match="bind the frozen held-out set"):
        guard.validate_prospective_measurement(row, root)


@pytest.mark.parametrize("replicates", [1, 11, True])
def test_future_resource_grammar_bounds_replicates(
    tmp_path: Path, replicates: int | bool
) -> None:
    root, row, _, _ = _future_bundle(tmp_path)
    row["replicates"]["per_item"] = replicates
    with pytest.raises(
        guard.ContractError,
        match="2..10 replicates|not of type 'integer'",
    ):
        guard.validate_prospective_measurement(row, root)


def test_future_resource_grammar_requires_at_least_two_judges(tmp_path: Path) -> None:
    root, row, _, _ = _future_bundle(tmp_path)
    row["judges"].pop()
    with pytest.raises(guard.ContractError, match="same 2..8 sorted judges"):
        guard.validate_prospective_measurement(row, root)
