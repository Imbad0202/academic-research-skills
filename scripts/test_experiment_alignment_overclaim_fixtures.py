"""Fixture guard for evals/heldout/experiment_alignment_overclaim (#915).

The two passports are subject-visible inputs for the #260 C4 check. These
tests keep them valid against the passport contracts, keep the answers out of
them, and keep heldout_set.json pointing at claims the passports declare.
They do not run the subject or score a verdict.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import check_claim_audit_consistency as _lint  # noqa: E402
from tests.test_helpers import run_script  # noqa: E402

SUITE = REPO / "evals/heldout/experiment_alignment_overclaim"
SHAPE_VALIDATOR = REPO / "scripts/check_experiment_provenance.py"
VERDICTS = {"ALIGNED", "OVERSTATED", "NOT_SUPPORTED_BY_PROVENANCE", "PROVENANCE_INSUFFICIENT"}

HELDOUT = json.loads((SUITE / "heldout_set.json").read_text(encoding="utf-8"))
ITEMS = HELDOUT["items"]


def _passport(item: dict) -> dict:
    return yaml.safe_load((SUITE / item["passport"]).read_text(encoding="utf-8"))


def _claim_ids(body: dict) -> set[str]:
    return {c["claim_id"] for m in body["claim_intent_manifests"] for c in m["claims"]}


def test_case_and_claim_inventory() -> None:
    """Parametrized tests pass vacuously on an empty set; pin the inventory."""
    inventory = {i["id"]: sorted(i["ground_truth"]["claims"]) for i in ITEMS}
    assert inventory == {"st2-01": ["C-001", "C-002", "C-003"], "st2-02": ["C-001", "C-002"]}


def test_suite_is_registered_as_mechanical_match() -> None:
    registry = json.loads((REPO / "evals/heldout/suite_registry.json").read_text(encoding="utf-8"))
    assert registry["experiment_alignment_overclaim"] == "mechanical_match"
    assert HELDOUT["scoring"]["suite_class"] == "mechanical_match"


@pytest.mark.parametrize("item", ITEMS, ids=[i["id"] for i in ITEMS])
def test_passport_shape_validates(item: dict) -> None:
    proc = run_script(SHAPE_VALIDATOR, str(SUITE / item["passport"]),
                      extra_env={"PYTHONPATH": str(REPO)})
    assert proc.returncode == 0, f"{proc.stdout}\n{proc.stderr}"


@pytest.mark.parametrize("item", ITEMS, ids=[i["id"] for i in ITEMS])
def test_passport_cross_array_clean(item: dict) -> None:
    assert [f.render() for f in _lint.validate_passport(_passport(item))] == []


@pytest.mark.parametrize("item", ITEMS, ids=[i["id"] for i in ITEMS])
def test_passport_carries_no_answer(item: dict) -> None:
    body = _passport(item)
    assert "experiment_alignment_results" not in body
    text = (SUITE / item["passport"]).read_text(encoding="utf-8")
    assert "heldout_set" not in text, f"{item['passport']} points the subject at the answers"
    for verdict in VERDICTS:
        assert verdict not in text, f"{item['passport']} names the verdict {verdict}"


@pytest.mark.parametrize("item", ITEMS, ids=[i["id"] for i in ITEMS])
def test_ground_truth_matches_declared_claims(item: dict) -> None:
    declared = _claim_ids(_passport(item))
    graded = item["ground_truth"]["claims"]
    assert set(graded) == declared
    assert set(item["manuscript_locators"]) == declared
    for claim in graded.values():
        assert claim["expected_verdicts"] and set(claim["expected_verdicts"]) <= VERDICTS


def test_each_item_has_an_aligned_control() -> None:
    for item in ITEMS:
        expected = [c["expected_verdicts"] for c in item["ground_truth"]["claims"].values()]
        assert ["ALIGNED"] in expected, f"{item['id']} has no ALIGNED control claim"
        assert any("ALIGNED" not in e for e in expected), f"{item['id']} has no overclaim"
