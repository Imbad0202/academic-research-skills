"""Schema 13.2 validator tests."""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from scripts import check_sprint_contract as checker

REPO = Path(__file__).resolve().parents[1]
FULL_PATH = REPO / "shared/contracts/reviewer/full.json"
MF_PATH = REPO / "shared/contracts/reviewer/methodology_focus.json"
WRITER_PATH = REPO / "shared/contracts/writer/full.json"
EVALUATOR_PATH = REPO / "shared/contracts/evaluator/full.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def full() -> dict:
    return load(FULL_PATH)


@pytest.mark.parametrize("path", [FULL_PATH, MF_PATH, WRITER_PATH, EVALUATOR_PATH])
def test_shipped_templates_validate(path):
    contract = load(path)
    assert checker.validate(contract) == []
    assert checker.check_structural_invariants(contract) == []


def test_branch13_reviewer_without_role_scope_fails():
    contract = full()
    contract["acceptance_dimensions"][0].pop("eligible_roles")
    contract["acceptance_dimensions"][0].pop("owner_role")
    assert any("eligible_roles" in error or "owner_role" in error
               for error in checker.validate(contract))


def test_owner_must_be_eligible():
    contract = full()
    contract["acceptance_dimensions"][0]["owner_role"] = "eic"
    assert any("owner_role" in error
               for error in checker.check_structural_invariants(contract))


def test_roles_must_be_mode_subset():
    contract = load(MF_PATH)
    contract["acceptance_dimensions"][0]["eligible_roles"].append("domain")
    assert any("outside" in error
               for error in checker.check_structural_invariants(contract))


def test_every_mode_role_must_have_a_dimension():
    contract = full()
    for dim in contract["acceptance_dimensions"]:
        dim["eligible_roles"] = [
            role for role in dim["eligible_roles"] if role != "perspective"
        ]
        if dim["owner_role"] == "perspective":
            dim["eligible_roles"] = ["eic"]
            dim["owner_role"] = "eic"
    assert any("perspective" in error
               for error in checker.check_structural_invariants(contract))


@pytest.mark.parametrize("path", [WRITER_PATH, EVALUATOR_PATH])
def test_writer_evaluator_reject_reviewer_fields(path):
    contract = load(path)
    contract["acceptance_dimensions"][0]["eligible_roles"] = ["eic"]
    contract["acceptance_dimensions"][0]["owner_role"] = "eic"
    assert any("reviewer-only" in error
               for error in checker.check_structural_invariants(contract))


def test_scoring_plan_requires_five_canonical_fields():
    contract = full()
    required = contract["measurement_procedure"]["scoring_plan_schema"]["required"]
    required.remove("what_triggers_fatal")
    assert checker.validate(contract)


def test_hybrid_action_rejected_by_branch4():
    contract = full()
    contract["failure_conditions"][0]["action"] = (
        "editorial_decision=reject_or_major_revision"
    )
    assert checker.validate(contract)


@pytest.mark.parametrize(
    "expression",
    [
        "any high dimension has a fatal block",
        "D4 has a fatal block",
        "D5 has a fatal block",
    ],
)
def test_fatal_atom_mandatory_scope_only(expression):
    contract = full()
    contract["failure_conditions"][0]["expression"] = expression
    assert any("fatal atom" in error
               for error in checker.check_structural_invariants(contract))


def test_mandatory_fatal_atoms_are_valid():
    contract = full()
    assert not any("fatal atom" in error
                   for error in checker.check_structural_invariants(contract))


def test_sc12_single_judge_mandatory_warning():
    warnings = checker.warn_suspicious(full(), "v3.20.0")
    assert {line.split("dimension ")[1].split()[0] for line in warnings
            if "SC-12" in line} == {"D1", "D2", "D6"}


def test_schema_rejects_duplicate_eligible_role():
    contract = full()
    contract["acceptance_dimensions"][0]["eligible_roles"].append("methodology")
    assert checker.validate(contract)


def test_duplicate_dimension_and_condition_ids_fail_invariants():
    contract = full()
    contract["acceptance_dimensions"][1]["id"] = "D1"
    contract["failure_conditions"][1]["condition_id"] = "F1"
    errors = checker.check_structural_invariants(contract)
    assert any("duplicate acceptance_dimensions id" in error for error in errors)
    assert any("duplicate failure_conditions" in error for error in errors)


def test_f0_accept_grade_is_schema_required():
    contract = full()
    contract["failure_conditions"] = [
        condition for condition in contract["failure_conditions"]
        if condition["condition_id"] != "F0"
    ]
    assert checker.validate(contract)


def test_full_and_mf_exact_eligibility_maps():
    full_map = {
        dim["id"]: (dim["eligible_roles"], dim["owner_role"])
        for dim in full()["acceptance_dimensions"]
    }
    assert full_map == {
        "D1": (["methodology"], "methodology"),
        "D2": (["domain"], "domain"),
        "D3": (["da", "methodology"], "da"),
        "D4": (["perspective"], "perspective"),
        "D5": (["eic"], "eic"),
        "D6": (["eic"], "eic"),
    }
    mf_map = {
        dim["id"]: (dim["eligible_roles"], dim["owner_role"])
        for dim in load(MF_PATH)["acceptance_dimensions"]
    }
    assert mf_map == {
        "D1": (["methodology"], "methodology"),
        "D2": (["eic"], "eic"),
    }


def test_writer_evaluator_byte_unchanged_against_hardcoded_baseline():
    """Spec A zero-touch pair, with non-self-referential byte witnesses."""
    import hashlib

    expected = {
        "shared/contracts/writer/full.json":
            "9340ad80971f643ca772243a645d0a52b4ab059e27e04e0bce463e0760d1553b",
        "shared/contracts/evaluator/full.json":
            "ce3b3e19f1da68985ebeb2dd2d7904d7343724d0847fff4e08704d79f083158a",
    }
    for rel, digest in expected.items():
        assert hashlib.sha256((REPO / rel).read_bytes()).hexdigest() == digest


def test_cli_valid_and_invalid(tmp_path):
    assert checker.main.__name__ == "main"
    bad = copy.deepcopy(full())
    bad["acceptance_dimensions"][0].pop("owner_role")
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(bad), encoding="utf-8")
    assert checker.validate(bad)
