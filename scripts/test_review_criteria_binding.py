from __future__ import annotations

import copy
import json
import os
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

import review_criteria_binding as binding
from resolve_review_target_context import load_json, resolve


REPO = Path(__file__).resolve().parents[1]
FIXTURES = REPO / "scripts" / "fixtures" / "review_target_context"
CONTRACTS = REPO / "shared" / "contracts" / "review_target"
LIVE_REGISTRY = REPO / "shared" / "review_criteria_registry.json"
LIVE_MSR_DECLARATION = FIXTURES / "msr-2027-technical-full-declaration.json"
PROVING_SET_IDS = {
    "official.msr2027.technical.full.scope",
    "official.msr2027.technical.full.validity",
    "official.msr2027.technical.full.open-science",
    "field.sigsoft.empirical.general-essential",
    "overlay.sigsoft.repository-mining.essential",
}


def _write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


@pytest.fixture
def resolved_inputs(tmp_path: Path) -> tuple[Path, Path, dict, dict]:
    declaration = load_json(FIXTURES / "exact-declaration.json")
    registry = load_json(FIXTURES / "synthetic-registry.json")
    context = resolve(declaration, registry)
    context_path = tmp_path / "context.json"
    registry_path = tmp_path / "registry.json"
    _write_json(context_path, context)
    _write_json(registry_path, registry)
    return context_path, registry_path, context, registry


def _init(tmp_path: Path, resolved_inputs, *, target: str = "review-001",
          prior: Path | None = None) -> Path:
    context_path, registry_path, _, _ = resolved_inputs
    manifest = tmp_path / f"{target}.binding.json"
    args = [
        "init",
        "--context", str(context_path),
        "--context-ref", "phase0/context.json",
        "--registry", str(registry_path),
        "--registry-ref", "phase0/registry.json",
        "--target-review-id", target,
        "--output", str(manifest),
    ]
    if prior is not None:
        args.extend(["--prior-manifest", str(prior)])
    assert binding.main(args) == 0
    return manifest


def _manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _record(tmp_path: Path, manifest_path: Path, consumer: str) -> list[Path]:
    manifest = _manifest(manifest_path)
    artifacts: list[Path] = []
    args = ["record", "--manifest", str(manifest_path), "--consumer", consumer]
    for role in binding.ROLES[consumer]:
        path = tmp_path / f"{consumer}-{role}.md"
        path.write_text(
            f"# Output\n\n{binding._render_conflict_line(manifest)}\n"
            f"{binding._render_marker(manifest, consumer, role)}\n",
            encoding="utf-8",
        )
        artifacts.append(path)
        args.extend(["--artifact", f"{role}={path.name}"])
    old = Path.cwd()
    try:
        os.chdir(tmp_path)
        assert binding.main(args) == 0
    finally:
        os.chdir(old)
    return artifacts


def _complete(tmp_path: Path, resolved_inputs) -> Path:
    manifest = _init(tmp_path, resolved_inputs)
    for consumer in binding.CONSUMERS:
        _record(tmp_path, manifest, consumer)
    return manifest


def _option(*, new_data: bool = False, intent: str = "no") -> dict:
    return {
        "action": "Narrow the claim to the evidence currently available.",
        "resource_effort": {
            "scope": "new_data" if new_data else "sentence",
            "description": "Collect an additional sample." if new_data else "Revise one claim sentence.",
        },
        "trade_offs": "The narrower statement reduces breadth but preserves support.",
        "changes_research_intent": intent,
        "requires_new_data": new_data,
        "proposed_result_values": False,
    }


def _findings(manifest: dict, *, no_remedy: bool = False) -> dict:
    authority = manifest["context_authority"]
    pointer = next(item for item in authority["selected_criteria"] if item["blocking_eligible"])
    ref = {key: pointer[key] for key in ("criterion_id", "criterion_version", "criterion_digest")}
    row = {
        "finding_id": "finding-1",
        "consumer_id": "external_panel",
        "reviewer_id": "DA",
        "severity": "major",
        "criterion_refs": [ref],
        "evidence_anchor": {
            "anchor_type": "absence",
            "locator": "Methods",
            "absence_scope": "sampling justification",
            "check_performed": "Methods and appendix checked",
        },
        "scholarly_relevance": "The inference depends on the population represented by the sample.",
        "confirmed_target_relevance": {
            "status": "confirmed",
            "rationale": "The author-confirmed contribution type requires supported inference.",
        },
        "remedy_status": "none" if no_remedy else "available",
        "minimum_viable_remedy": None if no_remedy else _option(),
        "stronger_option": None if no_remedy else _option(new_data=True, intent="yes_author_choice_required"),
        "stronger_option_reason": "No stronger option is honest without changing the study." if no_remedy else None,
        "no_honest_remedy_reason": "The missing observations cannot be reconstructed." if no_remedy else None,
    }
    return {
        "schema_version": binding.FINDINGS_VERSION,
        "target_review_id": manifest["target_review_id"],
        "resolved_digest": authority["resolved_digest"],
        "selected_criterion_ids": authority["selected_criterion_ids"],
        "findings": [row],
    }


def _validate_findings(tmp_path: Path, resolved_inputs, manifest_path: Path,
                       findings: dict) -> int:
    context_path, registry_path, _, _ = resolved_inputs
    path = tmp_path / "findings.json"
    _write_json(path, findings)
    return binding.main(
        [
            "validate-findings",
            "--manifest", str(manifest_path),
            "--context", str(context_path),
            "--registry", str(registry_path),
            "--findings", str(path),
        ]
    )


def test_draft_2020_12_schemas_are_valid() -> None:
    for name in (
        "review_criteria_binding_manifest.schema.json",
        "constructive_review_findings.schema.json",
    ):
        Draft202012Validator.check_schema(load_json(CONTRACTS / name))


def test_schema_accepts_positive_manifest_and_findings(tmp_path, resolved_inputs) -> None:
    manifest_path = _complete(tmp_path, resolved_inputs)
    manifest = _manifest(manifest_path)
    Draft202012Validator(load_json(CONTRACTS / "review_criteria_binding_manifest.schema.json")).validate(manifest)
    Draft202012Validator(load_json(CONTRACTS / "constructive_review_findings.schema.json")).validate(_findings(manifest))


def test_schema_rejects_undeclared_fields(tmp_path, resolved_inputs) -> None:
    manifest = _manifest(_init(tmp_path, resolved_inputs))
    manifest["copied_criterion_prose"] = "forbidden"
    errors = list(
        Draft202012Validator(
            load_json(CONTRACTS / "review_criteria_binding_manifest.schema.json")
        ).iter_errors(manifest)
    )
    assert errors


def test_schema_rejects_duplicate_consumer_and_wrong_role(
    tmp_path, resolved_inputs
) -> None:
    manifest_path = _init(tmp_path, resolved_inputs)
    _record(tmp_path, manifest_path, "formative_planning")
    manifest = _manifest(manifest_path)
    schema = load_json(CONTRACTS / "review_criteria_binding_manifest.schema.json")
    validator = Draft202012Validator(schema)

    duplicate = copy.deepcopy(manifest)
    duplicate["receipts"].append(copy.deepcopy(duplicate["receipts"][0]))
    assert list(validator.iter_errors(duplicate))

    wrong_role = copy.deepcopy(manifest)
    wrong_role["receipts"][0]["artifacts"][0]["role"] = "INTERNAL"
    assert list(validator.iter_errors(wrong_role))


def test_findings_schema_rejects_new_data_flag_mismatch(
    tmp_path, resolved_inputs
) -> None:
    manifest = _manifest(_init(tmp_path, resolved_inputs))
    findings = _findings(manifest)
    findings["findings"][0]["minimum_viable_remedy"]["requires_new_data"] = True
    schema = load_json(CONTRACTS / "constructive_review_findings.schema.json")
    assert list(Draft202012Validator(schema).iter_errors(findings))


def test_init_and_validate_round_trip(tmp_path, resolved_inputs) -> None:
    context_path, registry_path, context, _ = resolved_inputs
    manifest_path = _init(tmp_path, resolved_inputs)
    manifest = _manifest(manifest_path)
    assert manifest["context_authority"]["resolved_digest"] == context["resolved_digest"]
    assert [p["criterion_id"] for p in manifest["context_authority"]["selected_criteria"]] == context["selected_criterion_ids"]
    assert binding.main([
        "validate", "--manifest", str(manifest_path), "--context", str(context_path),
        "--registry", str(registry_path),
    ]) == 0


def test_marker_is_exact_pointer_only(tmp_path, resolved_inputs, capsys) -> None:
    manifest_path = _init(tmp_path, resolved_inputs)
    assert binding.main([
        "marker", "--manifest", str(manifest_path),
        "--consumer", "external_panel", "--role", "DA",
    ]) == 0
    output = capsys.readouterr().out
    assert "[REVIEW-TARGET-BINDING v1]" in output
    assert "consumer_id=external_panel" in output
    assert "role=DA" in output
    assert "statement" not in output


@pytest.mark.parametrize("consumer", binding.CONSUMERS)
def test_each_consumer_receipt_records_exact_roles(tmp_path, resolved_inputs, consumer) -> None:
    manifest_path = _init(tmp_path, resolved_inputs)
    _record(tmp_path, manifest_path, consumer)
    receipt = _manifest(manifest_path)["receipts"][0]
    assert receipt["consumer_id"] == consumer
    assert tuple(item["role"] for item in receipt["artifacts"]) == binding.ROLES[consumer]


def test_complete_requires_three_consumers_and_five_external_seats(tmp_path, resolved_inputs) -> None:
    context_path, registry_path, _, _ = resolved_inputs
    manifest_path = _complete(tmp_path, resolved_inputs)
    assert binding.main([
        "validate", "--manifest", str(manifest_path), "--context", str(context_path),
        "--registry", str(registry_path), "--require-complete",
    ]) == 0


def test_live_msr_proving_set_binds_all_three_consumers(tmp_path: Path) -> None:
    declaration = load_json(LIVE_MSR_DECLARATION)
    registry = load_json(LIVE_REGISTRY)
    context = resolve(declaration, registry)
    context_path = tmp_path / "msr-context.json"
    registry_path = tmp_path / "live-registry.json"
    _write_json(context_path, context)
    _write_json(registry_path, registry)
    inputs = (context_path, registry_path, context, registry)

    manifest_path = _complete(tmp_path, inputs)
    manifest = _manifest(manifest_path)

    assert tuple(item["consumer_id"] for item in manifest["receipts"]) == binding.CONSUMERS
    assert manifest["context_authority"]["resolved_digest"] == context["resolved_digest"]
    assert binding.main(
        [
            "validate",
            "--manifest",
            str(manifest_path),
            "--context",
            str(context_path),
            "--registry",
            str(registry_path),
            "--require-complete",
        ]
    ) == 0


def test_predecessor_context_cannot_silently_bind_to_live_registry(
    tmp_path: Path,
) -> None:
    live = load_json(LIVE_REGISTRY)
    predecessor = copy.deepcopy(live)
    predecessor["registry_version"] = "2026.08"
    predecessor["as_of"] = "2026-08-08"
    predecessor["criteria"] = [
        item
        for item in predecessor["criteria"]
        if item["criterion_id"] not in PROVING_SET_IDS
    ]
    for authority_class in (
        "official_venue_type",
        "field_society_standard",
        "reporting_design_overlay",
    ):
        predecessor["authority_classes"][authority_class] = []

    declaration = load_json(FIXTURES / "field-general-declaration.json")
    old_context = resolve(declaration, predecessor)
    context_path = tmp_path / "old-context.json"
    registry_path = tmp_path / "live-registry.json"
    output_path = tmp_path / "must-not-exist.binding.json"
    _write_json(context_path, old_context)
    _write_json(registry_path, live)

    assert binding.main(
        [
            "init",
            "--context",
            str(context_path),
            "--context-ref",
            "phase0/old-context.json",
            "--registry",
            str(registry_path),
            "--registry-ref",
            "phase0/live-registry.json",
            "--target-review-id",
            "migration-must-rebind",
            "--output",
            str(output_path),
        ]
    ) == 2
    assert not output_path.exists()


def test_incomplete_manifest_fails_complete_gate(tmp_path, resolved_inputs) -> None:
    context_path, registry_path, _, _ = resolved_inputs
    manifest_path = _init(tmp_path, resolved_inputs)
    assert binding.main([
        "validate", "--manifest", str(manifest_path), "--context", str(context_path),
        "--registry", str(registry_path), "--require-complete",
    ]) == 2


def test_exact_receipt_retry_is_no_write(tmp_path, resolved_inputs) -> None:
    manifest_path = _init(tmp_path, resolved_inputs)
    _record(tmp_path, manifest_path, "formative_planning")
    before = manifest_path.stat().st_mtime_ns
    _record(tmp_path, manifest_path, "formative_planning")
    assert manifest_path.stat().st_mtime_ns == before


def test_different_receipt_for_same_consumer_conflicts(tmp_path, resolved_inputs) -> None:
    manifest_path = _init(tmp_path, resolved_inputs)
    artifacts = _record(tmp_path, manifest_path, "formative_planning")
    artifacts[0].write_text(
        artifacts[0].read_text(encoding="utf-8") + "changed\n", encoding="utf-8"
    )
    old = Path.cwd()
    try:
        os.chdir(tmp_path)
        assert binding.main([
            "record", "--manifest", str(manifest_path),
            "--consumer", "formative_planning",
            "--artifact", f"FORMATIVE={artifacts[0].name}",
        ]) == 3
    finally:
        os.chdir(old)


def test_tampered_marker_is_rejected(tmp_path, resolved_inputs) -> None:
    manifest_path = _init(tmp_path, resolved_inputs)
    manifest = _manifest(manifest_path)
    artifact = tmp_path / "bad.md"
    artifact.write_text(
        binding._render_conflict_line(manifest)
        + "\n"
        + binding._render_marker(manifest, "formative_planning", "FORMATIVE").replace(
            "resolved_digest=", "resolved_digest=0"
        ),
        encoding="utf-8",
    )
    old = Path.cwd()
    try:
        os.chdir(tmp_path)
        assert binding.main([
            "record", "--manifest", str(manifest_path),
            "--consumer", "formative_planning", "--artifact", "FORMATIVE=bad.md",
        ]) == 2
    finally:
        os.chdir(old)


def test_external_panel_rejects_missing_da(tmp_path, resolved_inputs) -> None:
    manifest_path = _init(tmp_path, resolved_inputs)
    manifest = _manifest(manifest_path)
    args = ["record", "--manifest", str(manifest_path), "--consumer", "external_panel"]
    for role in binding.ROLES["external_panel"][:-1]:
        path = tmp_path / f"{role}.md"
        path.write_text(
            binding._render_conflict_line(manifest)
            + "\n"
            + binding._render_marker(manifest, "external_panel", role),
            encoding="utf-8",
        )
        args.extend(["--artifact", f"{role}={path.name}"])
    old = Path.cwd()
    try:
        os.chdir(tmp_path)
        assert binding.main(args) == 2
    finally:
        os.chdir(old)


def test_same_target_id_changed_context_conflicts(tmp_path, resolved_inputs) -> None:
    prior = _init(tmp_path, resolved_inputs)
    context_path, registry_path, context, _ = resolved_inputs
    changed = copy.deepcopy(context)
    changed["resolved_digest"] = "0" * 64
    _write_json(context_path, changed)
    output = tmp_path / "changed.binding.json"
    assert binding.main([
        "init", "--context", str(context_path), "--context-ref", "phase0/context.json",
        "--registry", str(registry_path), "--registry-ref", "phase0/registry.json",
        "--target-review-id", "review-001", "--prior-manifest", str(prior),
        "--output", str(output),
    ]) == 2
    assert not output.exists()


def test_new_target_id_records_noncomparability(tmp_path, resolved_inputs) -> None:
    prior = _init(tmp_path, resolved_inputs)
    successor = _init(tmp_path, resolved_inputs, target="review-002", prior=prior)
    assert _manifest(successor)["predecessor"] == {
        "target_review_id": "review-001",
        "resolved_digest": _manifest(prior)["context_authority"]["resolved_digest"],
        "comparability": "new_target_review_not_comparable",
    }


def test_context_semantic_tamper_fails_before_write(tmp_path, resolved_inputs) -> None:
    context_path, registry_path, context, _ = resolved_inputs
    context["selected_criterion_ids"] = list(reversed(context["selected_criterion_ids"]))
    _write_json(context_path, context)
    output = tmp_path / "tampered.binding.json"
    assert binding.main([
        "init", "--context", str(context_path), "--context-ref", "phase0/context.json",
        "--registry", str(registry_path), "--registry-ref", "phase0/registry.json",
        "--target-review-id", "review-001", "--output", str(output),
    ]) == 2
    assert not output.exists()


def test_duplicate_json_keys_are_rejected(tmp_path, resolved_inputs) -> None:
    _, registry_path, _, _ = resolved_inputs
    context = tmp_path / "duplicate.json"
    context.write_text('{"declaration":{},"declaration":{}}', encoding="utf-8")
    assert binding.main([
        "init", "--context", str(context), "--context-ref", "phase0/context.json",
        "--registry", str(registry_path), "--registry-ref", "phase0/registry.json",
        "--target-review-id", "review-001", "--output", str(tmp_path / "out.json"),
    ]) == 2


def test_symlinked_input_is_rejected(tmp_path, resolved_inputs) -> None:
    context_path, registry_path, _, _ = resolved_inputs
    link = tmp_path / "context-link.json"
    link.symlink_to(context_path)
    assert binding.main([
        "init", "--context", str(link), "--context-ref", "phase0/context.json",
        "--registry", str(registry_path), "--registry-ref", "phase0/registry.json",
        "--target-review-id", "review-001", "--output", str(tmp_path / "out.json"),
    ]) == 2


def test_input_beneath_symlinked_parent_is_rejected(tmp_path, resolved_inputs) -> None:
    context_path, registry_path, _, _ = resolved_inputs
    real_parent = tmp_path / "real-parent"
    real_parent.mkdir()
    nested_context = real_parent / "context.json"
    nested_context.write_bytes(context_path.read_bytes())
    linked_parent = tmp_path / "linked-parent"
    linked_parent.symlink_to(real_parent, target_is_directory=True)
    assert binding.main([
        "init", "--context", str(linked_parent / "context.json"),
        "--context-ref", "phase0/context.json",
        "--registry", str(registry_path), "--registry-ref", "phase0/registry.json",
        "--target-review-id", "review-001", "--output", str(tmp_path / "out.json"),
    ]) == 2


def test_artifact_with_second_binding_marker_is_rejected(
    tmp_path, resolved_inputs
) -> None:
    manifest_path = _init(tmp_path, resolved_inputs)
    manifest = _manifest(manifest_path)
    artifact = tmp_path / "ambiguous.md"
    artifact.write_text(
        binding._render_conflict_line(manifest)
        + "\n"
        + binding._render_marker(manifest, "formative_planning", "FORMATIVE")
        + "\n"
        + binding._render_marker(manifest, "internal_evaluator", "INTERNAL"),
        encoding="utf-8",
    )
    old = Path.cwd()
    try:
        os.chdir(tmp_path)
        assert binding.main([
            "record", "--manifest", str(manifest_path),
            "--consumer", "formative_planning", "--artifact", "FORMATIVE=ambiguous.md",
        ]) == 2
    finally:
        os.chdir(old)


def test_missing_or_changed_parallel_conflict_line_is_rejected(
    tmp_path, resolved_inputs
) -> None:
    manifest_path = _init(tmp_path, resolved_inputs)
    manifest = _manifest(manifest_path)
    artifact = tmp_path / "conflict-drift.md"
    artifact.write_text(
        "criteria_parallel_conflicts: []\n"
        + binding._render_marker(manifest, "formative_planning", "FORMATIVE"),
        encoding="utf-8",
    )
    old = Path.cwd()
    try:
        os.chdir(tmp_path)
        assert binding.main([
            "record", "--manifest", str(manifest_path),
            "--consumer", "formative_planning", "--artifact", "FORMATIVE=conflict-drift.md",
        ]) == 2
    finally:
        os.chdir(old)


@pytest.mark.parametrize("no_remedy", [False, True])
def test_valid_constructive_findings(tmp_path, resolved_inputs, no_remedy) -> None:
    manifest_path = _init(tmp_path, resolved_inputs)
    assert _validate_findings(
        tmp_path, resolved_inputs, manifest_path,
        _findings(_manifest(manifest_path), no_remedy=no_remedy),
    ) == 0


def test_unselected_criterion_pointer_fails(tmp_path, resolved_inputs) -> None:
    manifest_path = _init(tmp_path, resolved_inputs)
    findings = _findings(_manifest(manifest_path))
    findings["findings"][0]["criterion_refs"][0]["criterion_id"] = "unknown.criterion"
    assert _validate_findings(tmp_path, resolved_inputs, manifest_path, findings) == 2


def test_nonblocking_only_finding_fails(tmp_path, resolved_inputs) -> None:
    manifest_path = _init(tmp_path, resolved_inputs)
    manifest = _manifest(manifest_path)
    pointer = next(
        item for item in manifest["context_authority"]["selected_criteria"]
        if not item["blocking_eligible"]
    )
    findings = _findings(manifest)
    findings["findings"][0]["criterion_refs"] = [
        {key: pointer[key] for key in ("criterion_id", "criterion_version", "criterion_digest")}
    ]
    assert _validate_findings(tmp_path, resolved_inputs, manifest_path, findings) == 2


def test_invented_result_values_fail(tmp_path, resolved_inputs) -> None:
    manifest_path = _init(tmp_path, resolved_inputs)
    findings = _findings(_manifest(manifest_path))
    findings["findings"][0]["minimum_viable_remedy"]["proposed_result_values"] = True
    assert _validate_findings(tmp_path, resolved_inputs, manifest_path, findings) == 2


def test_new_data_scope_must_match_flag(tmp_path, resolved_inputs) -> None:
    manifest_path = _init(tmp_path, resolved_inputs)
    findings = _findings(_manifest(manifest_path))
    findings["findings"][0]["minimum_viable_remedy"]["requires_new_data"] = True
    assert _validate_findings(tmp_path, resolved_inputs, manifest_path, findings) == 2


@pytest.mark.parametrize("field", ["title", "statement"])
def test_copied_registry_prose_fails(tmp_path, resolved_inputs, field) -> None:
    manifest_path = _init(tmp_path, resolved_inputs)
    findings = _findings(_manifest(manifest_path))
    _, _, _, registry = resolved_inputs
    findings["findings"][0]["scholarly_relevance"] = registry["criteria"][0][field]
    assert _validate_findings(tmp_path, resolved_inputs, manifest_path, findings) == 2


def test_wrong_consumer_role_pair_fails(tmp_path, resolved_inputs) -> None:
    manifest_path = _init(tmp_path, resolved_inputs)
    findings = _findings(_manifest(manifest_path))
    findings["findings"][0]["consumer_id"] = "internal_evaluator"
    assert _validate_findings(tmp_path, resolved_inputs, manifest_path, findings) == 2


def test_long_text_quote_fails(tmp_path, resolved_inputs) -> None:
    manifest_path = _init(tmp_path, resolved_inputs)
    findings = _findings(_manifest(manifest_path))
    findings["findings"][0]["evidence_anchor"] = {
        "anchor_type": "text",
        "locator": "Results",
        "quote": " ".join(["word"] * 26),
    }
    assert _validate_findings(tmp_path, resolved_inputs, manifest_path, findings) == 2


def test_manifest_digest_tamper_fails(tmp_path, resolved_inputs) -> None:
    context_path, registry_path, _, _ = resolved_inputs
    manifest_path = _init(tmp_path, resolved_inputs)
    manifest = _manifest(manifest_path)
    manifest["manifest_digest"] = "0" * 64
    _write_json(manifest_path, manifest)
    assert binding.main([
        "validate", "--manifest", str(manifest_path), "--context", str(context_path),
        "--registry", str(registry_path),
    ]) == 2


def test_no_ambient_manuscript_scan(tmp_path, resolved_inputs) -> None:
    sentinel = "UNIQUE-MANUSCRIPT-SENTINEL-684"
    (tmp_path / "manuscript.md").write_text(sentinel, encoding="utf-8")
    manifest_path = _init(tmp_path, resolved_inputs)
    assert sentinel not in manifest_path.read_text(encoding="utf-8")
