"""Schema 13.2 validator tests."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import check_sprint_contract as checker
from tests.test_helpers import run_script

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts/check_sprint_contract.py"
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


def test_reviewer_re_review_mode_rejected():
    """#576 Spec B §5.4: `reviewer_re_review` left the Schema 13 enum.

    Re-review is governed by the dedicated contract family under
    shared/contracts/re_review/ (+ scripts/check_re_review_synthesis.py),
    not by a Schema 13 sprint contract — a contract claiming the mode
    must fail validation.
    """
    contract = full()
    contract["mode"] = "reviewer_re_review"
    errors = checker.validate(contract)
    assert any("reviewer_re_review" in e or "mode" in e for e in errors)


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


SCHEMA_MUTATIONS = (
    "missing_contract_id",
    "missing_mode",
    "missing_stage",
    "missing_baseline_version",
    "missing_dimensions",
    "missing_conditions",
    "bad_contract_id",
    "bad_mode",
    "empty_stage",
    "zero_panel",
    "empty_dimensions",
    "bad_dimension_id",
    "bad_dimension_name",
    "empty_description",
    "bad_priority",
    "empty_eligible_roles",
    "bad_eligible_role",
    "bad_owner_role",
    "extra_dimension_field",
    "short_scoring_schema",
    "duplicate_scoring_field",
    "typo_scoring_field",
    "zero_paraphrase_minimum",
    "empty_conditions",
    "bad_condition_id",
    "negative_severity",
    "excessive_severity",
    "bad_quantifier",
    "empty_expression",
    "bad_action",
    "missing_quantifier",
    "missing_panel",
    "short_override_ladder",
    "misordered_override_ladder",
)


def apply_schema_mutation(contract: dict, case: str) -> None:
    dim = contract["acceptance_dimensions"][0]
    condition = contract["failure_conditions"][0]
    if case.startswith("missing_") and case.removeprefix("missing_") in {
        "contract_id", "mode", "stage", "baseline_version",
    }:
        contract.pop(case.removeprefix("missing_"))
    elif case == "missing_dimensions":
        contract.pop("acceptance_dimensions")
    elif case == "missing_conditions":
        contract.pop("failure_conditions")
    elif case == "bad_contract_id":
        contract["contract_id"] = "BAD"
    elif case == "bad_mode":
        contract["mode"] = "reviewer_quick"
    elif case == "empty_stage":
        contract["stage"] = ""
    elif case == "zero_panel":
        contract["panel_size"] = 0
    elif case == "empty_dimensions":
        contract["acceptance_dimensions"] = []
    elif case == "bad_dimension_id":
        dim["id"] = "D01"
    elif case == "bad_dimension_name":
        dim["name"] = "Bad Name"
    elif case == "empty_description":
        dim["description"] = ""
    elif case == "bad_priority":
        dim["priority"] = "urgent"
    elif case == "empty_eligible_roles":
        dim["eligible_roles"] = []
    elif case == "bad_eligible_role":
        dim["eligible_roles"] = ["copyeditor"]
    elif case == "bad_owner_role":
        dim["owner_role"] = "copyeditor"
    elif case == "extra_dimension_field":
        dim["scoring_scale"] = ["pass"]
    elif case == "short_scoring_schema":
        contract["measurement_procedure"]["scoring_plan_schema"]["required"].pop()
    elif case == "duplicate_scoring_field":
        required = contract["measurement_procedure"]["scoring_plan_schema"]["required"]
        required[-1] = required[0]
    elif case == "typo_scoring_field":
        contract["measurement_procedure"]["scoring_plan_schema"]["required"][-1] = (
            "fatal_trigger"
        )
    elif case == "zero_paraphrase_minimum":
        contract["measurement_procedure"]["paraphrase_minimum_dimensions"] = 0
    elif case == "empty_conditions":
        contract["failure_conditions"] = []
    elif case == "bad_condition_id":
        condition["condition_id"] = "F01"
    elif case == "negative_severity":
        condition["severity"] = -1
    elif case == "excessive_severity":
        condition["severity"] = 101
    elif case == "bad_quantifier":
        condition["cross_reviewer_quantifier"] = "plurality"
    elif case == "empty_expression":
        condition["expression"] = ""
    elif case == "bad_action":
        condition["action"] = "editorial_decision=revise"
    elif case == "missing_quantifier":
        condition.pop("cross_reviewer_quantifier")
    elif case == "missing_panel":
        contract.pop("panel_size")
    elif case in {"short_override_ladder", "misordered_override_ladder"}:
        contract["override_ladder"] = [
            {"round": 1, "trigger": "first", "required": ["a"]},
            {"round": 2, "trigger": "second", "required": ["b"]},
            {"round": 3, "trigger": "third", "required": ["c"]},
        ]
        if case == "short_override_ladder":
            contract["override_ladder"].pop()
        else:
            contract["override_ladder"][0]["round"] = 2
    else:  # pragma: no cover - guards the test table itself
        raise AssertionError(case)


@pytest.mark.parametrize("case", SCHEMA_MUTATIONS)
def test_legacy_schema_mutations_still_fail(case):
    contract = full()
    apply_schema_mutation(contract, case)
    assert checker.validate(contract), case


WARNING_CASES = (
    ("sc1_lag", "SC-1", True),
    ("sc1_exact_two", "SC-1", False),
    ("sc1_no_current", "SC-1", False),
    ("sc2_single", "SC-2", True),
    ("sc3_no_mandatory", "SC-3", True),
    ("sc4_orphan", "SC-4", True),
    ("sc5_missing_output", "SC-5", True),
    ("sc7_conflict", "SC-7", True),
    ("sc9_impossible", "SC-9", True),
    ("sc10_unreferenced", "SC-10", True),
    ("sc11_single", "SC-11", True),
    ("sc11_mode_mismatch", "SC-11", True),
    ("writer_no_sc5", "SC-5", False),
    ("writer_no_sc11", "SC-11", False),
)


@pytest.mark.parametrize("case,fragment,present", WARNING_CASES)
def test_legacy_warning_boundaries(case, fragment, present):
    contract = full()
    current = None
    if case == "sc1_lag":
        contract["baseline_version"], current = "v3.3.0", "v3.6.2"
    elif case == "sc1_exact_two":
        contract["baseline_version"], current = "v3.4.0", "v3.6.2"
    elif case == "sc1_no_current":
        contract["baseline_version"] = "v3.3.0"
    elif case == "sc2_single":
        contract["acceptance_dimensions"] = contract["acceptance_dimensions"][:1]
    elif case == "sc3_no_mandatory":
        for dim in contract["acceptance_dimensions"]:
            dim["priority"] = "normal"
    elif case == "sc4_orphan":
        contract["failure_conditions"][0]["expression"] = "D99 scores 'block'"
    elif case == "sc5_missing_output":
        contract["measurement_procedure"]["reviewer_must_output_before_paper"] = [
            "contract_paraphrase"
        ]
    elif case == "sc7_conflict":
        contract["failure_conditions"][1]["severity"] = (
            contract["failure_conditions"][0]["severity"]
        )
    elif case == "sc9_impossible":
        contract["measurement_procedure"]["paraphrase_minimum_dimensions"] = 99
    elif case == "sc10_unreferenced":
        contract["failure_conditions"] = [
            {
                "condition_id": "F0",
                "severity": 0,
                "cross_reviewer_quantifier": "all",
                "expression": "every dimension scores 'pass'",
                "action": "editorial_decision=accept",
            }
        ]
    elif case == "sc11_single":
        contract["panel_size"] = 1
    elif case == "sc11_mode_mismatch":
        contract["panel_size"] = 4
    elif case.startswith("writer_"):
        contract = load(WRITER_PATH)
    else:  # pragma: no cover - guards the test table itself
        raise AssertionError(case)
    warnings = checker.warn_suspicious(contract, current)
    assert any(
        warning.startswith(f"{fragment} WARNING") for warning in warnings
    ) is present


@pytest.mark.parametrize("case,expected", (("valid", 0), ("missing", 1), ("bad_json", 1)))
def test_cli_executes_real_process(tmp_path, case, expected):
    if case == "missing":
        path = tmp_path / "missing.json"
    elif case == "bad_json":
        path = tmp_path / "bad.json"
        path.write_text("{", encoding="utf-8")
    else:
        path = tmp_path / "valid.json"
        path.write_text(json.dumps(full()), encoding="utf-8")
    result = run_script(SCRIPT, str(path))
    assert result.returncode == expected, result.stderr


@pytest.mark.parametrize(
    "path,required_field",
    (
        (WRITER_PATH, "pre_commitment_artifacts"),
        (EVALUATOR_PATH, "disagreement_handling"),
    ),
)
def test_generator_mode_specific_artifact_is_required(path, required_field):
    contract = load(path)
    contract.pop(required_field)
    assert checker.validate(contract)


@pytest.mark.parametrize(
    "path,bad_action",
    (
        (WRITER_PATH, "editorial_decision=accept"),
        (EVALUATOR_PATH, "writer_decision=accept"),
    ),
)
def test_generator_mode_action_enum_is_pinned(path, bad_action):
    contract = load(path)
    contract["failure_conditions"][0]["action"] = bad_action
    assert checker.validate(contract)


@pytest.mark.parametrize(
    "path,source",
    (
        (
            WRITER_PATH,
            ("pre_commitment_artifacts", "acceptance_criteria_paraphrase"),
        ),
        (EVALUATOR_PATH, ("disagreement_handling",)),
    ),
)
def test_generator_sc9_reads_mode_specific_source(path, source):
    contract = load(path)
    target = contract
    for key in source:
        target = target[key]
    target["minimum_dimensions" if len(source) == 2 else "paraphrase_minimum_dimensions"] = 99
    assert any(
        warning.startswith("SC-9 WARNING")
        for warning in checker.warn_suspicious(contract, None)
    )


@pytest.mark.parametrize("path", (WRITER_PATH, EVALUATOR_PATH))
@pytest.mark.parametrize("warning", ("SC-5", "SC-11"))
def test_generator_modes_do_not_receive_reviewer_only_warnings(path, warning):
    assert not any(
        item.startswith(f"{warning} WARNING")
        for item in checker.warn_suspicious(load(path), None)
    )
