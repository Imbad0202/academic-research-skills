from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent.parent
MODULE_PATH = ROOT / "scripts" / "validate_ideation_diversity_assets.py"
SPEC = importlib.util.spec_from_file_location("ideation_assets", MODULE_PATH)
assert SPEC and SPEC.loader
assets = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(assets)


def _loaded():
    return assets.load_json_strict(assets.SET_PATH), assets.load_json_strict(
        assets.VARIANT_PATH
    )


def test_real_assets_validate_and_freeze_six_bilingual_role_cards():
    heldout, variant = assets.load_assets()
    assert heldout["suite"] == "within_session_ideation_diversity"
    assert len(heldout["scenarios"]) == 6
    assert len({row["pair_id"] for row in heldout["scenarios"]}) == 3
    assert variant["nonproduction_only"] is True
    assert variant["runtime_install_forbidden"] is True


def test_two_mechanisms_are_separate_paired_controls():
    heldout, _ = _loaded()
    experiments = heldout["design"]["experiments"]
    assert [row["mechanism_id"] for row in experiments] == [
        "adjacent_probe",
        "exploratory_guardrails",
    ]
    assert experiments[0]["held_constant"] == "production exploratory guardrails on"
    assert experiments[1]["held_constant"] == "adjacent probe off"
    assert set(experiments[0]["arms"]).isdisjoint(experiments[1]["arms"])


def test_subject_and_judge_blinding_hide_role_ground_truth_and_arms():
    heldout, _ = _loaded()
    assert "owned_framings" in heldout["subject_blind_fields"]
    assert "response_policy" in heldout["subject_blind_fields"]
    assert "arm_id" in heldout["judge_blind_fields"]
    assert "aggregate" in heldout["judge_blind_fields"]
    assert "paired_transcript" in heldout["actor_blind_fields"]


def test_each_role_has_one_initial_and_two_unexpressed_owned_framings():
    heldout, _ = _loaded()
    for scenario in heldout["scenarios"]:
        initial = [
            row["framing_key"]
            for row in scenario["owned_framings"]
            if row["initially_expressed"]
        ]
        assert initial == ["F1"]
        assert [row["framing_key"] for row in scenario["owned_framings"]] == [
            "F1",
            "F2",
            "F3",
        ]


def test_codebook_keeps_count_dispersion_and_followthrough_separate():
    text = assets.CODEBOOK_PATH.read_text(encoding="utf-8")
    assert "owned_framing_count" in text
    assert "owned_facet_family_count" in text
    assert "facet_followthrough_rate" in text
    assert "Do not average metrics 1-6 into a score" in text
    assert "never contributes to A1" in text


def test_materialized_variant_changes_only_derived_output(tmp_path):
    production = ROOT / "deep-research" / "agents" / "socratic_mentor_agent.md"
    production_before = production.read_bytes()
    output = tmp_path / "ablation.md"
    assets.materialize_variant(output)
    rendered = output.read_text(encoding="utf-8")
    assert production.read_bytes() == production_before
    assert "Standard taxonomy balance (non-production ablation)" in rendered
    assert "This variant must never be installed as a production agent." in rendered
    assert "Higher `[Q:CHALLENGE]` ratio (40%+ across all layers)" not in rendered


def test_materializer_refuses_overwrite(tmp_path):
    output = tmp_path / "exists.md"
    output.write_text("owned", encoding="utf-8")
    with pytest.raises(assets.AssetError, match="refusing to overwrite"):
        assets.materialize_variant(output)
    assert output.read_text(encoding="utf-8") == "owned"


def test_duplicate_scenario_id_fails_closed():
    heldout, variant = _loaded()
    mutated = copy.deepcopy(heldout)
    mutated["scenarios"][1]["scenario_id"] = mutated["scenarios"][0]["scenario_id"]
    with pytest.raises(assets.AssetError, match="scenario_id values must be unique"):
        assets.validate_assets(mutated, variant)


def test_missing_language_pair_fails_closed():
    heldout, variant = _loaded()
    mutated = copy.deepcopy(heldout)
    mutated["scenarios"][1]["pair_id"] = "idi-quality-policy"
    with pytest.raises(assets.AssetError, match="one en and one zh-TW"):
        assets.validate_assets(mutated, variant)


def test_equivalence_key_drift_fails_closed():
    heldout, variant = _loaded()
    mutated = copy.deepcopy(heldout)
    mutated["scenarios"][1]["equivalence_key"] = "eq-drift-v1"
    with pytest.raises(assets.AssetError, match="equivalence_key must match"):
        assets.validate_assets(mutated, variant)


def test_facet_family_drift_between_languages_fails_closed():
    heldout, variant = _loaded()
    mutated = copy.deepcopy(heldout)
    mutated["scenarios"][1]["owned_framings"][1]["facet_kind"] = "time_dimension"
    with pytest.raises(assets.AssetError, match="structure differs by language"):
        assets.validate_assets(mutated, variant)


def test_only_f1_may_be_initially_expressed():
    heldout, variant = _loaded()
    mutated = copy.deepcopy(heldout)
    mutated["scenarios"][0]["owned_framings"][1]["initially_expressed"] = True
    with pytest.raises(assets.AssetError, match="exactly F1"):
        assets.validate_assets(mutated, variant)


@pytest.mark.parametrize(
    "phrase",
    [
        "the causal mechanism",
        "the intervention impact angle",
        "教師中介效果的角度",
        "如何改善成果？",
    ],
)
def test_directional_or_formed_facet_phrase_fails_closed(phrase):
    heldout, variant = _loaded()
    mutated = copy.deepcopy(heldout)
    mutated["scenarios"][0]["owned_framings"][1]["matching_facet_phrases"][0] = phrase
    with pytest.raises(assets.AssetError, match="directional or formed"):
        assets.validate_assets(mutated, variant)


def test_variant_source_hash_drift_fails_closed():
    _, variant = _loaded()
    mutated = copy.deepcopy(variant)
    mutated["source_sha256"] = "0" * 64
    with pytest.raises(assets.AssetError, match="source_sha256"):
        assets.render_variant(mutated)


def test_variant_path_traversal_fails_closed():
    _, variant = _loaded()
    mutated = copy.deepcopy(variant)
    mutated["source_path"] = "../socratic_mentor_agent.md"
    with pytest.raises(assets.AssetError, match="repository-relative and safe"):
        assets.render_variant(mutated)


def test_variant_replacement_must_match_exactly_once():
    _, variant = _loaded()
    mutated = copy.deepcopy(variant)
    mutated["replacements"][0]["before"] = "missing production bytes"
    with pytest.raises(assets.AssetError, match="expected 1 occurrence, found 0"):
        assets.render_variant(mutated)


def test_variant_replacement_ids_must_be_unique():
    _, variant = _loaded()
    mutated = copy.deepcopy(variant)
    mutated["replacements"][1]["replacement_id"] = mutated["replacements"][0][
        "replacement_id"
    ]
    with pytest.raises(assets.AssetError, match="duplicate replacement_id"):
        assets.render_variant(mutated)


def test_variant_requires_nonproduction_and_install_forbidden_attestations():
    _, variant = _loaded()
    for key, message in (
        ("nonproduction_only", "nonproduction_only"),
        ("runtime_install_forbidden", "runtime installation"),
    ):
        mutated = copy.deepcopy(variant)
        mutated[key] = False
        with pytest.raises(assets.AssetError, match=message):
            assets.render_variant(mutated)


def test_strict_json_rejects_duplicate_keys(tmp_path):
    path = tmp_path / "duplicate.json"
    path.write_text('{"suite": "a", "suite": "b"}', encoding="utf-8")
    with pytest.raises(assets.AssetError, match="duplicate JSON key"):
        assets.load_json_strict(path)


def test_cli_contains_no_model_network_or_subprocess_transport():
    source = MODULE_PATH.read_text(encoding="utf-8").casefold()
    for forbidden in (
        "import requests",
        "import urllib",
        "import subprocess",
        "codex exec",
        "claude -p",
        "openai",
        "anthropic",
    ):
        assert forbidden not in source


def test_suite_registry_declares_paired_controls():
    registry = json.loads(
        (ROOT / "evals" / "heldout" / "suite_registry.json").read_text(
            encoding="utf-8"
        )
    )
    assert registry["within_session_ideation_diversity"] == "paired_controls"
