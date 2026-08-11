from __future__ import annotations

import json
from pathlib import Path

from scripts import check_684_review_criteria_binding as guard
from scripts import check_phase_conformance as phase


def _texts() -> dict[Path, str]:
    return {
        path: (guard.REPO_ROOT / path).read_text(encoding="utf-8")
        for path in guard.REQUIRED_FILES + guard.NON_CONSUMERS
    }


def test_repository_integration_passes() -> None:
    assert guard.check() == []


def test_binding_consumer_enum_mutation_fails() -> None:
    texts = _texts()
    schema = json.loads(texts[guard.BINDING_SCHEMA])
    schema["$defs"]["receipt"]["properties"]["consumer_id"]["enum"].pop()
    texts[guard.BINDING_SCHEMA] = json.dumps(schema)
    assert "consumer enum/order drift" in "\n".join(guard.check_contracts(texts))


def test_binding_role_enum_mutation_fails() -> None:
    texts = _texts()
    schema = json.loads(texts[guard.BINDING_SCHEMA])
    schema["$defs"]["artifact_binding"]["properties"]["role"]["enum"].remove("DA")
    texts[guard.BINDING_SCHEMA] = json.dumps(schema)
    assert "closed role enum/order drift" in "\n".join(guard.check_contracts(texts))


def test_schema_opening_fails() -> None:
    texts = _texts()
    schema = json.loads(texts[guard.FINDINGS_SCHEMA])
    schema["additionalProperties"] = True
    texts[guard.FINDINGS_SCHEMA] = json.dumps(schema)
    assert "root must be closed" in "\n".join(guard.check_contracts(texts))


def test_proposed_result_values_must_remain_false() -> None:
    texts = _texts()
    schema = json.loads(texts[guard.FINDINGS_SCHEMA])
    schema["$defs"]["option"]["properties"]["proposed_result_values"] = {
        "type": "boolean"
    }
    texts[guard.FINDINGS_SCHEMA] = json.dumps(schema)
    assert "proposed_result_values" in "\n".join(guard.check_contracts(texts))


def test_suite_registry_class_mutation_fails() -> None:
    texts = _texts()
    registry = json.loads(texts[guard.SUITE_REGISTRY])
    registry["review_criteria_constructive_value"] = "mechanical_match"
    texts[guard.SUITE_REGISTRY] = json.dumps(registry)
    assert "paired_controls" in "\n".join(guard.check_contracts(texts))


def test_adjudication_must_retain_raw_expert_labels() -> None:
    texts = _texts()
    schema = json.loads(texts[guard.ADJUDICATION_SCHEMA])
    required = schema["$defs"]["finding"]["required"]
    required.remove("expert_labels")
    texts[guard.ADJUDICATION_SCHEMA] = json.dumps(schema)
    assert "finding rows need raw expert labels" in "\n".join(
        guard.check_contracts(texts)
    )


def test_adjudication_must_keep_exact_five_way_blinding() -> None:
    texts = _texts()
    schema = json.loads(texts[guard.ADJUDICATION_SCHEMA])
    blinded = schema["properties"]["experts"]["items"]["properties"]["blinded_to"]
    blinded["maxItems"] = 4
    texts[guard.ADJUDICATION_SCHEMA] = json.dumps(schema)
    assert "five-way blinding" in "\n".join(guard.check_contracts(texts))


def test_adjudication_cannot_relabel_model_as_human_expert() -> None:
    texts = _texts()
    schema = json.loads(texts[guard.ADJUDICATION_SCHEMA])
    expert = schema["properties"]["experts"]["items"]["properties"]
    expert["expert_type"] = {"type": "string"}
    texts[guard.ADJUDICATION_SCHEMA] = json.dumps(schema)
    assert "expert_type must be human" in "\n".join(guard.check_contracts(texts))


def test_measurement_call_plan_cannot_enable_api_or_drop_calls() -> None:
    texts = _texts()
    plan = json.loads(texts[guard.CALL_PLAN])
    plan["api_spend_ceiling_usd"] = 1
    plan["calls"].pop()
    texts[guard.CALL_PLAN] = json.dumps(plan)
    assert "24-call subscription/USD-0" in "\n".join(
        guard.check_measurement_assets(texts)
    )


def test_measurement_suite_lock_hash_mutation_fails() -> None:
    texts = _texts()
    lock = json.loads(texts[guard.SUITE_LOCK])
    first = next(iter(lock["assets"]))
    lock["assets"][first] = "0" * 64
    texts[guard.SUITE_LOCK] = json.dumps(lock)
    assert "hash mismatch" in "\n".join(guard.check_measurement_assets(texts))


def test_measurement_runner_rejects_network_import_and_consent_flag_removal() -> None:
    source = _texts()[guard.MEASUREMENT_RUNNER]
    source += "\nimport requests\n"
    source = source.replace('"--execute-24-subscription-calls"', '"--execute-calls"')
    joined = "\n".join(guard.check_measurement_runner(source))
    assert "forbidden API/network import requests" in joined
    assert "execute-24-subscription-calls" in joined


def test_runtime_consumer_order_mutation_fails() -> None:
    source = _texts()[guard.RUNTIME].replace(
        '("formative_planning", "internal_evaluator", "external_panel")',
        '("internal_evaluator", "formative_planning", "external_panel")',
    )
    assert "consumer tuple drift" in "\n".join(
        guard.check_python(guard.RUNTIME, source, runtime=True)
    )


def test_runtime_role_removal_fails() -> None:
    source = _texts()[guard.RUNTIME].replace(
        '("EIC", "R1", "R2", "R3", "DA")',
        '("EIC", "R1", "R2", "R3")',
    )
    assert "role map drift" in "\n".join(
        guard.check_python(guard.RUNTIME, source, runtime=True)
    )


def test_cli_command_removal_fails() -> None:
    source = _texts()[guard.RUNTIME].replace(
        'sub.add_parser("validate-findings", help="validate constructive finding sidecar")',
        'sub.add_parser("validate-sidecar", help="validate constructive finding sidecar")',
    )
    assert "CLI command set drift" in "\n".join(
        guard.check_python(guard.RUNTIME, source, runtime=True)
    )


def test_runtime_conflict_line_check_removal_fails() -> None:
    source = _texts()[guard.RUNTIME].replace(
        "or text.splitlines().count(expected_conflicts) != 1", "",
    )
    assert "exact conflict line" in "\n".join(
        guard.check_python(guard.RUNTIME, source, runtime=True)
    )


def test_live_import_and_ambient_scan_fail() -> None:
    source = _texts()[guard.SCORER] + "\nimport requests\nPath('.').rglob('*')\n"
    joined = "\n".join(guard.check_python(guard.SCORER, source, runtime=False))
    assert "forbidden live/clock import requests" in joined
    assert "forbidden ambient scan call rglob" in joined


def test_formative_marker_wiring_removal_fails() -> None:
    texts = _texts()
    texts[guard.FORMATIVE] = texts[guard.FORMATIVE].replace(
        "role `FORMATIVE` binding marker", "formative note"
    )
    assert "FORMATIVE" in "\n".join(guard.check_wiring(texts))


def test_synthesizer_five_role_check_removal_fails() -> None:
    texts = _texts()
    texts[guard.SYNTH] = texts[guard.SYNTH].replace(
        "EIC, R1, R2, R3, and DA", "available cards"
    )
    assert "EIC, R1, R2, R3, and DA" in "\n".join(guard.check_wiring(texts))


def test_integrity_agent_cannot_become_consumer() -> None:
    texts = _texts()
    target = guard.NON_CONSUMERS[0]
    texts[target] += "\nREVIEW-TARGET-BINDING becomes an integrity verdict input.\n"
    joined = "\n".join(guard.check_wiring(texts))
    assert "forbidden #684 consumer/gate surface" in joined


def test_measurement_cannot_drop_same_context_rule() -> None:
    texts = _texts()
    texts[guard.MEASUREMENT] = texts[guard.MEASUREMENT].replace(
        "identical target context bytes", "similar target context"
    )
    assert "identical target context bytes" in "\n".join(guard.check_wiring(texts))


def test_measurement_cannot_restore_api_as_default() -> None:
    texts = _texts()
    texts[guard.MEASUREMENT] = texts[guard.MEASUREMENT].replace(
        "incremental metered API spend ceiling of **USD 0**",
        "API spend is estimated before dispatch",
    )
    joined = "\n".join(guard.check_wiring(texts))
    assert "USD 0" in joined


def test_measurement_cannot_add_automatic_api_fallback() -> None:
    texts = _texts()
    texts[guard.MEASUREMENT] = texts[guard.MEASUREMENT].replace(
        "There is no API fallback within this run",
        "API fallback is permitted when subscription quota is exhausted",
    )
    joined = "\n".join(guard.check_wiring(texts))
    assert "no API fallback" in joined


def test_measurement_cannot_drop_human_expert_exception() -> None:
    texts = _texts()
    texts[guard.MEASUREMENT] = texts[guard.MEASUREMENT].replace(
        'judge_plan.exception: "human_expert_panel"',
        'judge_plan.exception: "none"',
    )
    joined = "\n".join(guard.check_wiring(texts))
    assert "human_expert_panel" in joined


def test_phase1_checker_accepts_pointer_commitment_without_extra_h2() -> None:
    contract = json.loads(
        (guard.REPO_ROOT / "shared/contracts/reviewer/full.json").read_text()
    )
    lines = ["## Contract Paraphrase", ""]
    for dimension in contract["acceptance_dimensions"]:
        lines.extend(
            [
                f"{dimension['id']} concerns {dimension['name']} as defined.",
                "",
            ]
        )
    lines.extend(["## Scoring Plan", ""])
    for dimension in contract["acceptance_dimensions"]:
        if "eic" not in dimension["eligible_roles"]:
            continue
        did = dimension["id"]
        lines.extend(
            [
                f"### {did}: {dimension['name']}",
                f"dimension_id: {did}",
                f"what_to_look_for: observable evidence for {did}",
                f"what_triggers_block: block evidence for {did}",
                f"what_triggers_warn: warn evidence for {did}",
            ]
        )
        if dimension["priority"] == "mandatory":
            lines.append(f"what_triggers_fatal: fatal evidence for {did}")
        lines.append("")
    lines.extend(
        [
            "criteria_parallel_conflicts: []",
            "[REVIEW-TARGET-BINDING v1]",
            "target_review_id=review-001",
            "consumer_id=external_panel",
            "role=EIC",
            "context_ref=phase0/context.json",
            f"context_sha256={'a' * 64}",
            f"resolved_digest={'b' * 64}",
            'selected_criterion_ids=["field.general.reporting"]',
            "[/REVIEW-TARGET-BINDING]",
            "[CONTRACT-ACKNOWLEDGED]",
        ]
    )
    parsed = phase.parse_phase1("bound-phase1.md", "\n".join(lines), contract, "eic")
    assert parsed is not None
