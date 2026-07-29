"""Mutation tests for check_persuasion_invariance_fixtures.py (#576 Spec B §14 v0.1).

Runs the checker against a synthetic fixture tree (never the real one, so the tests stay
hermetic) and asserts each invariant actually fires. The synthetic tree mirrors the real
scenario/arm inventory pinned in the checker's EXPECTED_ARMS with trivial content; the
pair-id and cell-count pins are patched to the synthetic tree's shape so that invariant 2's
pair/cell half is exercised against a known baseline rather than against the real set.

Run standalone:
    python -m unittest scripts/test_check_persuasion_invariance_fixtures.py -v
"""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import check_persuasion_invariance_fixtures as mod

APPLY_REPORT = (
    "```json\n"
    "{\n"
    '  "report_format_version": "1.2",\n'
    '  "base_draft_hash": "<<BASE_DRAFT_HASH>>",\n'
    '  "output_draft_hash": "<<OUTPUT_DRAFT_HASH>>",\n'
    '  "patch_digest": "<<PATCH_DIGEST>>"\n'
    "}\n"
    "```\n"
)
ANSWER_A = {"en": "Approved. Apply the escalation floor.", "zh-TW": "核准。套用 escalation 樓地板。"}
ANSWER_C = {"en": "Not approved. Record it only.", "zh-TW": "不予核准。僅作記錄。"}

PACKET = "# Packet\n\n## A. Roadmap\n\ncontent\n\n## B. Letter\n\ncontent\n"
ARM = "## H. Response to Reviewers\n\ncontent\n\n" + APPLY_REPORT
POINTER = "ARM-MATERIAL-POINTER: arm-a.{lang}.md\n\nUse arm-a's material.\n"

GT_TEMPLATE = """# {sid} ground truth

**HELD OUT.**

## Pair structure

| Pair | Observable | Relation | Target | Expected |
|------|-----------|----------|--------|----------|
| a↔b | `decision_state` | differs | — | `Accept` vs `Major Revision` |
| a↔b | `phase2a_verdict` | identical | REV-001 | `NOT_ADDRESSED` both |

## Rule anchors

- spec §6
"""

# Pins matched to the synthetic tree (one pair, two cells per scenario).
SYNTH_PAIRS = {sid: {f"{sid}/a-b"} for sid in mod.EXPECTED_ARMS}
SYNTH_CELL_COUNTS = {sid: 2 for sid in mod.EXPECTED_ARMS}
# synthetic tree: two non-pointer arms x two languages for P-1/P-2/P-4, three for
# P-3/P-5, and two non-pointer arms for P-6 -> (2+2+3+2+3+2) * 2 = 28 report-bearing files
SYNTH_APPLY_REPORT_FILES = 28


def _scenario(sid: str, sdir: str, arm_ids: list[str], *, claim_equality: bool = False,
              pointer_arm: str | None = None,
              answers: dict[str, dict] | None = None) -> dict:
    answers = answers or {}
    arms = []
    for aid in arm_ids:
        arm = {
            "arm_id": aid,
            "condition": f"{aid}-condition",
            "material": {
                "en": f"arms/{aid}.en.md",
                "zh-TW": f"arms/{aid}.zh-TW.md",
            },
            "claim_set": ["C1", "C2"] if claim_equality else None,
            "scripted_checkpoint_answer": answers.get(aid),
        }
        if pointer_arm == aid:
            arm["material_pointer"] = "arm-a"
        arms.append(arm)
    pair = {
        "pair_id": f"{sid}/a-b",
        "arms": [arm_ids[0], arm_ids[1]],
        "cells": [
            {
                "observable": "decision_state",
                "target": None,
                "relation": "differs",
                "expected": {arm_ids[0]: "Accept", arm_ids[1]: "Major Revision"},
                "rule_anchor": "spec §6 Step 2",
            },
            {
                "observable": "phase2a_verdict",
                "target": "REV-001",
                "relation": "identical",
                "expected": {arm_ids[0]: "NOT_ADDRESSED", arm_ids[1]: "NOT_ADDRESSED"},
                "rule_anchor": "spec §3.1",
                "on_mismatch": "dispatch_violation",
            },
        ],
    }
    return {
        "id": sid,
        "dir": sdir,
        "title": f"{sid} title",
        "controlled_factor": "factor",
        "arm_supplied_sections": ["H"],
        "packet": {"en": "packet.en.md", "zh-TW": "packet.zh-TW.md"},
        "claim_set_equality_required": claim_equality,
        "arms": arms,
        "pairs": [pair],
    }


def make_index() -> dict:
    return {
        "set_version": "0.1.0",
        "issue": 576,
        "spec_authority": mod.SPEC_AUTHORITY,
        "spec_section": "14",
        "harness": {"joins": "evals/heldout/reviewer_seeded_defects"},
        "languages": ["en", "zh-TW"],
        "hash_placeholders": list(mod.PLACEHOLDERS),
        "relation_enum": {"identical": "same", "differs": "different"},
        "observable_enum": {
            "decision_state": "the emission's decision_state",
            "phase2a_verdict": "committed Phase 2A verdict",
        },
        "scenarios": [
            _scenario("P-1", "scenarios/s1", ["arm-a", "arm-b"], claim_equality=True),
            _scenario("P-2", "scenarios/s2", ["arm-a", "arm-b"]),
            _scenario("P-3", "scenarios/s3", ["arm-a", "arm-b", "arm-c"]),
            _scenario("P-4", "scenarios/s4", ["arm-a", "arm-b"]),
            _scenario("P-5", "scenarios/s5", ["arm-a", "arm-b", "arm-c"]),
            _scenario(
                "P-6",
                "scenarios/s6",
                ["arm-a", "arm-b", "arm-c"],
                pointer_arm="arm-c",
                answers={"arm-a": ANSWER_A, "arm-c": ANSWER_C},
            ),
        ],
    }


def make_tree(root: Path, index: dict) -> None:
    (root / "heldout_set.json").write_text(json.dumps(index, indent=2, ensure_ascii=False),
                                           encoding="utf-8")
    for scenario in index["scenarios"]:
        sdir = root / scenario["dir"]
        (sdir / "arms").mkdir(parents=True, exist_ok=True)
        (sdir / "ground_truth.md").write_text(
            GT_TEMPLATE.format(sid=scenario["id"]), encoding="utf-8")
        for lang in ("en", "zh-TW"):
            (sdir / f"packet.{lang}.md").write_text(PACKET, encoding="utf-8")
        for arm in scenario["arms"]:
            is_pointer = arm.get("material_pointer") is not None
            for lang in ("en", "zh-TW"):
                body = POINTER.format(lang=lang) if is_pointer else ARM
                (sdir / arm["material"][lang]).write_text(body, encoding="utf-8")


class _Buffer:
    """Minimal writable sink that keeps what was written."""

    def __init__(self) -> None:
        self.value = ""

    def write(self, text: str) -> int:
        self.value += text
        return len(text)

    def flush(self) -> None:
        return None


class PersuasionInvarianceFixtureTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "set"
        self.root.mkdir()
        self.index = make_index()
        self.tree_mutation = None

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def run_checker(self) -> tuple[int, str]:
        make_tree(self.root, self.index)
        if self.tree_mutation is not None:
            self.tree_mutation(self.root)
        with mock.patch.object(mod, "ROOT", self.root), \
             mock.patch.object(mod, "INDEX", self.root / "heldout_set.json"), \
             mock.patch.object(mod, "EXPECTED_PAIRS", SYNTH_PAIRS), \
             mock.patch.object(mod, "EXPECTED_CELL_COUNTS", SYNTH_CELL_COUNTS), \
             mock.patch.object(mod, "EXPECTED_APPLY_REPORT_FILES", SYNTH_APPLY_REPORT_FILES), \
             mock.patch("sys.stderr", new_callable=_Buffer) as err, \
             mock.patch("sys.stdout", new_callable=_Buffer) as out:
            code = mod.main()
        return code, err.value + out.value

    def assert_fails(self, needle: str) -> None:
        code, output = self.run_checker()
        self.assertEqual(code, 1, f"expected failure, got pass. output:\n{output}")
        self.assertIn(needle, output)

    # --- baseline -------------------------------------------------------
    def test_clean_tree_passes(self) -> None:
        code, output = self.run_checker()
        self.assertEqual(code, 0, output)
        self.assertIn("6 scenarios, 15 arms", output)

    # --- invariant 1: index shape ---------------------------------------
    def test_missing_top_level_key_fails(self) -> None:
        del self.index["spec_authority"]
        self.assert_fails("1. index missing top-level keys")

    def test_wrong_spec_authority_fails(self) -> None:
        self.index["spec_authority"] = "docs/design/some-other-spec.md"
        self.assert_fails("1. index spec_authority is")

    def test_wrong_issue_fails(self) -> None:
        self.index["issue"] = 574
        self.assert_fails("1. index issue is 574")

    def test_missing_language_fails(self) -> None:
        self.index["languages"] = ["en"]
        self.assert_fails("1. index languages are")

    def test_placeholder_list_drift_fails(self) -> None:
        self.index["hash_placeholders"] = ["<<BASE_DRAFT_HASH>>"]
        self.assert_fails("1. index hash_placeholders are")

    def test_empty_observable_enum_fails(self) -> None:
        self.index["observable_enum"] = {}
        self.assert_fails("1. index observable_enum must be a non-empty object")

    # --- invariant 2: inventory -----------------------------------------
    def test_deleted_scenario_fails(self) -> None:
        self.index["scenarios"] = self.index["scenarios"][:-1]
        self.assert_fails("2. scenario inventory is")

    def test_deleted_arm_fails(self) -> None:
        scenario = self.index["scenarios"][2]
        removed = scenario["arms"].pop()
        scenario["pairs"] = [p for p in scenario["pairs"]
                             if removed["arm_id"] not in p["arms"]]
        self.assert_fails("2. P-3 arm-id set is")

    def test_deleted_pair_fails(self) -> None:
        self.index["scenarios"][1]["pairs"] = []
        self.assert_fails("2. P-2 pair-id set is")

    def test_renamed_pair_fails(self) -> None:
        self.index["scenarios"][1]["pairs"][0]["pair_id"] = "P-2/x-y"
        self.assert_fails("2. P-2 pair-id set is")

    def test_deleted_cell_fails(self) -> None:
        self.index["scenarios"][3]["pairs"][0]["cells"].pop()
        self.assert_fails("2. P-4 declares 1 cells, expected 2")

    # --- invariant 3: paths ---------------------------------------------
    def test_missing_packet_file_fails(self) -> None:
        self.tree_mutation = lambda root: (root / "scenarios/s2/packet.en.md").unlink()
        self.assert_fails("3. P-2 packet file does not exist")

    def test_missing_ground_truth_fails(self) -> None:
        self.tree_mutation = lambda root: (root / "scenarios/s4/ground_truth.md").unlink()
        self.assert_fails("3. P-4 missing ground_truth.md")

    # --- invariant 4: referential integrity -----------------------------
    def test_pair_naming_undeclared_arm_fails(self) -> None:
        pair = self.index["scenarios"][0]["pairs"][0]
        pair["arms"] = ["arm-a", "arm-z"]
        pair["cells"][0]["expected"] = {"arm-a": "Accept", "arm-z": "Major Revision"}
        pair["cells"][1]["expected"] = {"arm-a": "NOT_ADDRESSED", "arm-z": "NOT_ADDRESSED"}
        self.assert_fails("names undeclared arm ids")

    def test_pair_with_one_arm_fails(self) -> None:
        self.index["scenarios"][1]["pairs"][0]["arms"] = ["arm-a"]
        self.assert_fails("names 1 arms, expected exactly 2")

    def test_self_paired_arm_fails(self) -> None:
        self.index["scenarios"][1]["pairs"][0]["arms"] = ["arm-a", "arm-a"]
        self.assert_fails("pairs an arm with itself")

    # --- invariant 5: cell shape ----------------------------------------
    def test_unknown_observable_fails(self) -> None:
        self.index["scenarios"][0]["pairs"][0]["cells"][0]["observable"] = "vibes"
        self.assert_fails("observable 'vibes' is not in observable_enum")

    def test_unknown_relation_fails(self) -> None:
        self.index["scenarios"][0]["pairs"][0]["cells"][0]["relation"] = "maybe"
        self.assert_fails("relation 'maybe' is not in relation_enum")

    def test_empty_rule_anchor_fails(self) -> None:
        self.index["scenarios"][0]["pairs"][0]["cells"][0]["rule_anchor"] = "   "
        self.assert_fails("rule_anchor is empty")

    def test_missing_target_key_fails(self) -> None:
        del self.index["scenarios"][0]["pairs"][0]["cells"][0]["target"]
        self.assert_fails("missing cell keys: ['target']")

    def test_empty_conditional_on_fails(self) -> None:
        self.index["scenarios"][0]["pairs"][0]["cells"][0]["conditional_on"] = "  "
        self.assert_fails("conditional_on must be a non-empty string")

    def test_non_string_conditional_on_fails(self) -> None:
        self.index["scenarios"][0]["pairs"][0]["cells"][0]["conditional_on"] = {"when": "x"}
        self.assert_fails("conditional_on must be a non-empty string, got dict")

    def test_unknown_on_mismatch_fails(self) -> None:
        self.index["scenarios"][0]["pairs"][0]["cells"][1]["on_mismatch"] = "shrug"
        self.assert_fails("on_mismatch 'shrug' is not in")

    def test_expected_keys_not_matching_arms_fails(self) -> None:
        self.index["scenarios"][0]["pairs"][0]["cells"][0]["expected"] = {"arm-a": "Accept"}
        self.assert_fails("expected keys are ['arm-a']")

    # --- invariant 6: relation/value agreement --------------------------
    def test_identical_cell_with_differing_values_fails(self) -> None:
        self.index["scenarios"][0]["pairs"][0]["cells"][1]["expected"]["arm-b"] = "FULLY_ADDRESSED"
        self.assert_fails("relation is 'identical' but expected values differ")

    def test_differs_cell_with_equal_values_fails(self) -> None:
        self.index["scenarios"][0]["pairs"][0]["cells"][0]["expected"]["arm-b"] = "Accept"
        self.assert_fails("relation is 'differs' but expected values are equal")

    # --- invariant 7: claim-set equality --------------------------------
    def test_unequal_claim_sets_fail(self) -> None:
        self.index["scenarios"][0]["arms"][1]["claim_set"] = ["C1", "C2", "C6"]
        self.assert_fails("7. P-1/arm-b claim_set")

    def test_missing_claim_set_fails(self) -> None:
        self.index["scenarios"][0]["arms"][1]["claim_set"] = None
        self.assert_fails("but carries no claim_set")

    # --- invariant 8: hash placeholders ---------------------------------
    def test_literal_hash_in_apply_report_fails(self) -> None:
        def mutate(root: Path) -> None:
            p = root / "scenarios/s2/arms/arm-a.en.md"
            p.write_text(p.read_text(encoding="utf-8").replace(
                "<<BASE_DRAFT_HASH>>", "a17c4e0b9d33"), encoding="utf-8")
        self.tree_mutation = mutate
        self.assert_fails("base_draft_hash is 'a17c4e0b9d33'")

    def test_missing_hash_key_fails(self) -> None:
        def mutate(root: Path) -> None:
            p = root / "scenarios/s2/arms/arm-a.en.md"
            p.write_text(
                p.read_text(encoding="utf-8").replace(
                    '  "patch_digest": "<<PATCH_DIGEST>>"\n', ""),
                encoding="utf-8")
        self.tree_mutation = mutate
        self.assert_fails('carries an apply report with 0 "patch_digest" key(s)')

    def test_duplicate_hash_key_fails(self) -> None:
        def mutate(root: Path) -> None:
            p = root / "scenarios/s2/arms/arm-a.en.md"
            p.write_text(
                p.read_text(encoding="utf-8").replace(
                    '  "patch_digest": "<<PATCH_DIGEST>>"\n',
                    '  "patch_digest": "<<PATCH_DIGEST>>",\n'
                    '  "patch_digest": "<<PATCH_DIGEST>>"\n'),
                encoding="utf-8")
        self.tree_mutation = mutate
        self.assert_fails('carries an apply report with 2 "patch_digest" key(s)')

    def test_whole_apply_report_deleted_fails(self) -> None:
        """Removing every hash key must not make the file look report-free."""
        def mutate(root: Path) -> None:
            p = root / "scenarios/s2/arms/arm-a.en.md"
            t = p.read_text(encoding="utf-8")
            for token in mod.PLACEHOLDERS:
                t = "\n".join(l for l in t.splitlines() if token not in l)
            p.write_text(t + "\n", encoding="utf-8")
        self.tree_mutation = mutate
        self.assert_fails('carries an apply report with 0 "base_draft_hash" key(s)')

    def test_apply_report_block_removed_entirely_fails(self) -> None:
        """Deleting the whole report block trips the pinned report-bearing file count."""
        def mutate(root: Path) -> None:
            p = root / "scenarios/s2/arms/arm-a.en.md"
            p.write_text("## H. Response to Reviewers\n\ncontent\n", encoding="utf-8")
        self.tree_mutation = mutate
        self.assert_fails("file(s) carry an apply report, expected 28")

    def test_duplicate_report_format_version_fails(self) -> None:
        def mutate(root: Path) -> None:
            p = root / "scenarios/s2/arms/arm-a.en.md"
            p.write_text(
                p.read_text(encoding="utf-8").replace(
                    '  "report_format_version": "1.2",\n',
                    '  "report_format_version": "1.2",\n  "report_format_version": "1.2",\n'),
                encoding="utf-8")
        self.tree_mutation = mutate
        self.assert_fails('with 2 "report_format_version" key(s)')

    def test_swapped_placeholder_tokens_fail(self) -> None:
        def mutate(root: Path) -> None:
            p = root / "scenarios/s2/arms/arm-a.en.md"
            t = (p.read_text(encoding="utf-8")
                 .replace("<<BASE_DRAFT_HASH>>", "<<TMP>>")
                 .replace("<<OUTPUT_DRAFT_HASH>>", "<<BASE_DRAFT_HASH>>")
                 .replace("<<TMP>>", "<<OUTPUT_DRAFT_HASH>>"))
            p.write_text(t, encoding="utf-8")
        self.tree_mutation = mutate
        self.assert_fails("the token is key-bound")

    # --- invariant 9: pointer arms --------------------------------------
    def test_pointer_arm_without_pointer_file_fails(self) -> None:
        self.tree_mutation = lambda root: (
            root / "scenarios/s6/arms/arm-c.en.md").write_text(ARM, encoding="utf-8")
        self.assert_fails("is not a pointer file")

    def test_undeclared_pointer_file_fails(self) -> None:
        self.tree_mutation = lambda root: (
            root / "scenarios/s3/arms/arm-c.en.md").write_text(
                POINTER.format(lang="en"), encoding="utf-8")
        self.assert_fails("is a pointer file but the index declares no material_pointer")

    def test_pointer_to_missing_file_fails(self) -> None:
        self.tree_mutation = lambda root: (
            root / "scenarios/s6/arms/arm-c.en.md").write_text(
                "ARM-MATERIAL-POINTER: arm-q.en.md\n", encoding="utf-8")
        self.assert_fails("points at a missing file")

    def test_self_referential_pointer_fails(self) -> None:
        self.index["scenarios"][5]["arms"][2]["material_pointer"] = "arm-c"

        def mutate(root: Path) -> None:
            for lang in ("en", "zh-TW"):
                (root / f"scenarios/s6/arms/arm-c.{lang}.md").write_text(
                    f"ARM-MATERIAL-POINTER: arm-c.{lang}.md\n", encoding="utf-8")
        self.tree_mutation = mutate
        self.assert_fails("material_pointer points at itself")

    def test_pointer_chain_fails(self) -> None:
        def mutate(root: Path) -> None:
            for lang in ("en", "zh-TW"):
                (root / f"scenarios/s6/arms/arm-a.{lang}.md").write_text(
                    f"ARM-MATERIAL-POINTER: arm-b.{lang}.md\n", encoding="utf-8")
        self.tree_mutation = mutate
        self.assert_fails("which is itself a pointer")

    # --- invariant 10: held-out boundary --------------------------------
    def test_material_referencing_ground_truth_fails(self) -> None:
        def mutate(root: Path) -> None:
            p = root / "scenarios/s5/packet.en.md"
            p.write_text(p.read_text(encoding="utf-8") + "\nSee ground_truth.md.\n",
                         encoding="utf-8")
        self.tree_mutation = mutate
        self.assert_fails("references ground_truth.md")

    def test_scripted_answer_leaking_into_material_fails(self) -> None:
        def mutate(root: Path) -> None:
            p = root / "scenarios/s6/arms/arm-a.en.md"
            p.write_text(p.read_text(encoding="utf-8") + f"\n{ANSWER_A['en']}\n",
                         encoding="utf-8")
        self.tree_mutation = mutate
        self.assert_fails("scripted checkpoint answer (en)")

    def test_zh_scripted_answer_leaking_into_zh_material_fails(self) -> None:
        def mutate(root: Path) -> None:
            p = root / "scenarios/s6/arms/arm-a.zh-TW.md"
            p.write_text(p.read_text(encoding="utf-8") + f"\n{ANSWER_A['zh-TW']}\n",
                         encoding="utf-8")
        self.tree_mutation = mutate
        self.assert_fails("scripted checkpoint answer (zh-TW)")

    def test_cross_language_scripted_answer_leak_fails(self) -> None:
        """An English answer pasted into a zh-TW file is still contamination."""
        def mutate(root: Path) -> None:
            p = root / "scenarios/s6/arms/arm-a.zh-TW.md"
            p.write_text(p.read_text(encoding="utf-8") + f"\n{ANSWER_A['en']}\n",
                         encoding="utf-8")
        self.tree_mutation = mutate
        self.assert_fails("scripted checkpoint answer (en)")

    def test_scripted_answer_as_bare_string_fails(self) -> None:
        self.index["scenarios"][5]["arms"][0]["scripted_checkpoint_answer"] = "Approved."
        self.assert_fails("scripted_checkpoint_answer must be an object")

    def test_scripted_answer_missing_language_fails(self) -> None:
        self.index["scenarios"][5]["arms"][0]["scripted_checkpoint_answer"] = {"en": "Approved."}
        self.assert_fails("scripted_checkpoint_answer must be an object")

    # --- invariant 11: section split ------------------------------------
    def test_arm_supplied_section_leaking_into_packet_fails(self) -> None:
        def mutate(root: Path) -> None:
            p = root / "scenarios/s1/packet.en.md"
            p.write_text(p.read_text(encoding="utf-8")
                         + "\n## H. Response to Reviewers\n\nx\n", encoding="utf-8")
        self.tree_mutation = mutate
        self.assert_fails("contains arm-supplied section(s) ['H']")

    def test_arm_missing_its_supplied_section_fails(self) -> None:
        self.tree_mutation = lambda root: (
            root / "scenarios/s1/arms/arm-b.zh-TW.md").write_text(
                "## Z. Something else\n\nx\n", encoding="utf-8")
        self.assert_fails("section set is ['Z'], expected exactly ['H']")

    def test_arm_with_extra_undeclared_section_fails(self) -> None:
        def mutate(root: Path) -> None:
            p = root / "scenarios/s1/arms/arm-a.en.md"
            p.write_text(p.read_text(encoding="utf-8")
                         + "\n## F. Revised manuscript\n\nsmuggled\n", encoding="utf-8")
        self.tree_mutation = mutate
        self.assert_fails("section set is ['F', 'H'], expected exactly ['H']")

    def test_arm_with_duplicate_section_fails(self) -> None:
        def mutate(root: Path) -> None:
            p = root / "scenarios/s1/arms/arm-a.en.md"
            p.write_text(p.read_text(encoding="utf-8")
                         + "\n## H. Response to Reviewers\n\nagain\n", encoding="utf-8")
        self.tree_mutation = mutate
        self.assert_fails("<duplicate>")

    def test_empty_arm_supplied_sections_fails(self) -> None:
        self.index["scenarios"][3]["arm_supplied_sections"] = []
        self.assert_fails("11. P-4 declares no arm_supplied_sections")

    # --- invariant 12: ground-truth agreement ---------------------------
    def test_ground_truth_without_pair_structure_fails(self) -> None:
        self.tree_mutation = lambda root: (
            root / "scenarios/s3/ground_truth.md").write_text(
                "# P-3\n\nno table here\n", encoding="utf-8")
        self.assert_fails("has no '## Pair structure' section")

    def test_ground_truth_missing_a_cell_fails(self) -> None:
        def mutate(root: Path) -> None:
            p = root / "scenarios/s5/ground_truth.md"
            p.write_text(
                p.read_text(encoding="utf-8").replace(
                    "| a↔b | `phase2a_verdict` | identical | REV-001 | `NOT_ADDRESSED` both |\n",
                    ""),
                encoding="utf-8")
        self.tree_mutation = mutate
        self.assert_fails("index declares cells ground_truth.md Pair structure does not")

    def test_ground_truth_extra_cell_fails(self) -> None:
        def mutate(root: Path) -> None:
            p = root / "scenarios/s5/ground_truth.md"
            p.write_text(
                p.read_text(encoding="utf-8").replace(
                    "## Rule anchors",
                    "| a↔b | `attribution` | differs | — | x vs y |\n\n## Rule anchors"),
                encoding="utf-8")
        self.tree_mutation = mutate
        self.assert_fails("Pair structure declares cells the index does not")

    def test_pair_rows_after_the_next_h2_are_ignored(self) -> None:
        """A later section's table must not be folded into the Pair-structure comparison."""
        def mutate(root: Path) -> None:
            p = root / "scenarios/s5/ground_truth.md"
            p.write_text(
                p.read_text(encoding="utf-8")
                + "\n## Appendix\n\n| a↔b | `attribution` | differs | — | x vs y |\n",
                encoding="utf-8")
        self.tree_mutation = mutate
        code, output = self.run_checker()
        self.assertEqual(code, 0, output)

    def test_ground_truth_wrong_target_fails(self) -> None:
        def mutate(root: Path) -> None:
            p = root / "scenarios/s5/ground_truth.md"
            p.write_text(
                p.read_text(encoding="utf-8").replace(
                    "| a↔b | `phase2a_verdict` | identical | REV-001 |",
                    "| a↔b | `phase2a_verdict` | identical | REV-009 |"),
                encoding="utf-8")
        self.tree_mutation = mutate
        self.assert_fails("Pair structure declares cells the index does not")

    def test_ground_truth_collapsing_two_targets_into_one_row_fails(self) -> None:
        """Two index cells sharing an observable but not a target need two GT rows."""
        cells = self.index["scenarios"][4]["pairs"][0]["cells"]
        cells.append({
            "observable": "phase2a_verdict",
            "target": "REV-002",
            "relation": "identical",
            "expected": {"arm-a": "NOT_ADDRESSED", "arm-b": "NOT_ADDRESSED"},
            "rule_anchor": "spec §3.1",
        })
        with mock.patch.dict(SYNTH_CELL_COUNTS, {"P-5": 3}):
            self.assert_fails("index declares cells ground_truth.md Pair structure does not")


if __name__ == "__main__":
    unittest.main()
