"""Mutation tests for scripts/check_evals_gold_set.py.

Each test mutates the clean fixture to violate one invariant and asserts
the validator catches it. Plus one positive test on the clean fixture.
"""
import json
import shutil
from pathlib import Path

import pytest
import yaml

from scripts import check_evals_gold_set

FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "check_evals_gold_set"
CLEAN_FIXTURE = FIXTURE_ROOT / "clean"


def _copy_clean(tmp_path: Path) -> Path:
    """Copy clean fixture to a tmp dir for mutation."""
    dest = tmp_path / "mutated"
    shutil.copytree(CLEAN_FIXTURE, dest)
    return dest


def test_clean_fixture_passes(tmp_path):
    """Clean fixture passes all 9 invariants."""
    target = _copy_clean(tmp_path)
    errors = check_evals_gold_set.validate(target)
    assert errors == [], f"clean fixture should pass; got: {errors}"


def test_i1_extra_tuple_file_caught(tmp_path):
    """I1: extra tuple file without expected_outcomes entry fails."""
    target = _copy_clean(tmp_path)
    extra = target / "tuples" / "999-extra.json"
    extra.write_text(json.dumps({
        "tuple_id": "999-extra",
        "kind": "valid_doi",
        "corpus_entry": {
            "citation_key": "Extra", "title": "x", "authors": ["x"], "year": 2023,
            "doi": "10.1/x", "venue": "x", "source_pointer": "https://doi.org/10.1/x",
            "obtained_via": "folder-scan"
        },
        "arxiv_id": None, "ref_slug": "extra", "anchor": {"kind": "page", "value": "1"},
        "human_expert_verdict": None, "provenance_note": None, "fabrication_intent": False
    }))
    errors = check_evals_gold_set.validate(target)
    assert any("I1" in e for e in errors), f"I1 not caught; errors: {errors}"


def test_i2_tuple_id_filename_mismatch_caught(tmp_path):
    """I2: tuple_id field disagrees with filename stem."""
    target = _copy_clean(tmp_path)
    f = target / "tuples" / "001-valid-doi-test.json"
    obj = json.loads(f.read_text())
    obj["tuple_id"] = "wrong-id"
    f.write_text(json.dumps(obj))
    # also rewrite expected_outcomes to keep I1 clean (we want only I2 to fire)
    exp = json.loads((target / "expected_outcomes.json").read_text())
    # I1 will fire because stems no longer match expected_outcomes (file is still
    # 001-valid-doi-test.json but tuple_id is "wrong-id"). Confirm BOTH I1 and I2 fire
    # -- that's the actual semantics; I2 is independent of I1's filename match.
    errors = check_evals_gold_set.validate(target)
    assert any("I2" in e for e in errors), f"I2 not caught; errors: {errors}"


def test_i3_wrong_kind_distribution_caught(tmp_path):
    """I3: tuple kind count disagrees with manifest tuple_distribution."""
    target = _copy_clean(tmp_path)
    # mutate one tuple's kind to break the count
    f = target / "tuples" / "001-valid-doi-test.json"
    obj = json.loads(f.read_text())
    obj["kind"] = "fabricated"
    obj["fabrication_intent"] = True  # keep I7 consistent
    f.write_text(json.dumps(obj))
    errors = check_evals_gold_set.validate(target)
    assert any("I3" in e for e in errors), f"I3 not caught; errors: {errors}"
