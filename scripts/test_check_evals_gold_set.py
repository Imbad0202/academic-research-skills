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
