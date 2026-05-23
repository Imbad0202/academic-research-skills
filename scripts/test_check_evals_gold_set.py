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
    obj = json.loads(f.read_text(encoding="utf-8"))
    obj["tuple_id"] = "wrong-id"
    f.write_text(json.dumps(obj))
    # I1 stays clean: filename and expected_outcomes key both still
    # equal "001-valid-doi-test". Only I2 fires here -- I2 is
    # independent of filename-vs-key set equality.
    errors = check_evals_gold_set.validate(target)
    assert any("I2" in e for e in errors), f"I2 not caught; errors: {errors}"


def test_i3_wrong_kind_distribution_caught(tmp_path):
    """I3: tuple kind count disagrees with manifest tuple_distribution."""
    target = _copy_clean(tmp_path)
    # mutate one tuple's kind to break the count
    f = target / "tuples" / "001-valid-doi-test.json"
    obj = json.loads(f.read_text(encoding="utf-8"))
    obj["kind"] = "fabricated"
    obj["fabrication_intent"] = True  # keep I7 consistent
    f.write_text(json.dumps(obj))
    errors = check_evals_gold_set.validate(target)
    assert any("I3" in e for e in errors), f"I3 not caught; errors: {errors}"


def test_i4_duplicate_expected_outcomes_keys_caught(tmp_path):
    """I4: duplicate keys in expected_outcomes.json caught."""
    target = _copy_clean(tmp_path)
    # write raw JSON with duplicate key (json.dumps cannot produce this, so write text)
    exp_path = target / "expected_outcomes.json"
    raw = exp_path.read_text(encoding="utf-8").rstrip().rstrip("}")
    # find the first key in the dict and inject a duplicate at the end
    raw += ', "001-valid-doi-test": {"lookup_verified": "false", "resolver_outcomes": {}}}'
    exp_path.write_text(raw)
    errors = check_evals_gold_set.validate(target)
    assert any("I4" in e for e in errors), f"I4 not caught; errors: {errors}"


def test_i5_label_disagrees_with_kind_caught(tmp_path):
    """I5: expected_outcomes lookup_verified mismatches manifest's declared label for the kind."""
    target = _copy_clean(tmp_path)
    exp = json.loads((target / "expected_outcomes.json").read_text(encoding="utf-8"))
    exp["001-valid-doi-test"]["lookup_verified"] = "false"  # should be "true" for valid_doi
    (target / "expected_outcomes.json").write_text(json.dumps(exp))
    errors = check_evals_gold_set.validate(target)
    assert any("I5" in e for e in errors), f"I5 not caught; errors: {errors}"


def test_i5_invalid_label_enum_caught(tmp_path):
    """I5: expected_outcomes lookup_verified not in label enum caught."""
    target = _copy_clean(tmp_path)
    exp = json.loads((target / "expected_outcomes.json").read_text(encoding="utf-8"))
    exp["001-valid-doi-test"]["lookup_verified"] = "BOGUS"
    (target / "expected_outcomes.json").write_text(json.dumps(exp))
    errors = check_evals_gold_set.validate(target)
    assert any("I5" in e for e in errors), f"I5 not caught; errors: {errors}"


def test_i6_valid_arxiv_missing_arxiv_id_caught(tmp_path):
    """I6: valid_arxiv tuple with null arxiv_id caught."""
    target = _copy_clean(tmp_path)
    f = target / "tuples" / "002-valid-arxiv-test.json"
    obj = json.loads(f.read_text(encoding="utf-8"))
    obj["arxiv_id"] = None
    f.write_text(json.dumps(obj))
    errors = check_evals_gold_set.validate(target)
    assert any("I6" in e for e in errors), f"I6 not caught; errors: {errors}"


def test_i6_valid_doi_with_arxiv_id_caught(tmp_path):
    """I6: valid_doi tuple with non-null arxiv_id caught."""
    target = _copy_clean(tmp_path)
    f = target / "tuples" / "001-valid-doi-test.json"
    obj = json.loads(f.read_text(encoding="utf-8"))
    obj["arxiv_id"] = "2401.12345"
    f.write_text(json.dumps(obj))
    errors = check_evals_gold_set.validate(target)
    assert any("I6" in e for e in errors), f"I6 not caught; errors: {errors}"


def test_i6_valid_doi_missing_doi_caught(tmp_path):
    """I6: valid_doi tuple with null corpus_entry.doi caught."""
    target = _copy_clean(tmp_path)
    f = target / "tuples" / "001-valid-doi-test.json"
    obj = json.loads(f.read_text(encoding="utf-8"))
    obj["corpus_entry"].pop("doi", None)
    f.write_text(json.dumps(obj))
    errors = check_evals_gold_set.validate(target)
    assert any("I6" in e for e in errors), f"I6 not caught; errors: {errors}"


def test_i7_fabricated_without_intent_marker_caught(tmp_path):
    """I7: fabricated tuple with fabrication_intent=False caught."""
    target = _copy_clean(tmp_path)
    f = target / "tuples" / "003-fabricated-test.json"
    obj = json.loads(f.read_text(encoding="utf-8"))
    obj["fabrication_intent"] = False
    f.write_text(json.dumps(obj))
    errors = check_evals_gold_set.validate(target)
    assert any("I7" in e for e in errors), f"I7 not caught; errors: {errors}"


def test_i7_non_fabricated_with_intent_marker_caught(tmp_path):
    """I7: non-fabricated tuple with fabrication_intent=True caught."""
    target = _copy_clean(tmp_path)
    f = target / "tuples" / "001-valid-doi-test.json"
    obj = json.loads(f.read_text(encoding="utf-8"))
    obj["fabrication_intent"] = True
    f.write_text(json.dumps(obj))
    errors = check_evals_gold_set.validate(target)
    assert any("I7" in e for e in errors), f"I7 not caught; errors: {errors}"


def test_i8_unresolvable_missing_provenance_note_caught(tmp_path):
    """I8: valid_unresolvable tuple without provenance_note caught."""
    target = _copy_clean(tmp_path)
    f = target / "tuples" / "004-unresolvable-test.json"
    obj = json.loads(f.read_text(encoding="utf-8"))
    obj["provenance_note"] = None
    f.write_text(json.dumps(obj))
    errors = check_evals_gold_set.validate(target)
    assert any("I8" in e for e in errors), f"I8 not caught; errors: {errors}"


def test_i8_unresolvable_malformed_provenance_note_caught(tmp_path):
    """I8: valid_unresolvable provenance_note missing date pattern caught."""
    target = _copy_clean(tmp_path)
    f = target / "tuples" / "004-unresolvable-test.json"
    obj = json.loads(f.read_text(encoding="utf-8"))
    obj["provenance_note"] = "checked recently"  # no date pattern
    f.write_text(json.dumps(obj))
    errors = check_evals_gold_set.validate(target)
    assert any("I8" in e for e in errors), f"I8 not caught; errors: {errors}"


def test_i9_missing_resolver_caught(tmp_path):
    """I9: expected_outcomes missing one of the four resolvers caught."""
    target = _copy_clean(tmp_path)
    exp = json.loads((target / "expected_outcomes.json").read_text(encoding="utf-8"))
    exp["001-valid-doi-test"]["resolver_outcomes"].pop("arxiv")
    (target / "expected_outcomes.json").write_text(json.dumps(exp))
    errors = check_evals_gold_set.validate(target)
    assert any("I9" in e for e in errors), f"I9 not caught; errors: {errors}"


def test_i9_invalid_status_enum_caught(tmp_path):
    """I9: expected_outcomes resolver status not in enum caught."""
    target = _copy_clean(tmp_path)
    exp = json.loads((target / "expected_outcomes.json").read_text(encoding="utf-8"))
    exp["001-valid-doi-test"]["resolver_outcomes"]["crossref"]["status"] = "BOGUS"
    (target / "expected_outcomes.json").write_text(json.dumps(exp))
    errors = check_evals_gold_set.validate(target)
    assert any("I9" in e for e in errors), f"I9 not caught; errors: {errors}"
