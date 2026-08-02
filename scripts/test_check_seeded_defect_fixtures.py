"""Mutation tests for check_seeded_defect_fixtures.py (#574/#610 v0.2).

Runs the checker against a synthetic fixture tree (never the real one, so the
tests stay hermetic) and asserts each invariant actually fires.

Run standalone:
    python -m unittest scripts/test_check_seeded_defect_fixtures.py -v
"""
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import check_seeded_defect_fixtures as mod

ANCHOR = "the reported mean of 3.847 is not reachable from eighty-seven integer responses"


def make_tree(root: Path) -> None:
    (root / "manuscripts").mkdir(parents=True)
    (root / "manifests").mkdir()
    (root / "manuscripts" / "ms01_quant_defective.md").write_text(
        f"# Synthetic\n\nBody text where {ANCHOR} appears once.\n",
        encoding="utf-8",
    )
    (root / "manuscripts" / "ms00_clean_control.md").write_text(
        "# Clean control\n\nSound synthetic paper.\n", encoding="utf-8"
    )
    manifest = {
        "fixture_id": "ms01_quant",
        "fixture_version": "0.2",
        "manuscript": "manuscripts/ms01_quant_defective.md",
        "defect_count": 1,
        "defects": [
            {
                "defect_id": "SD-01",
                "class": "statistical",
                "statistical_kind": "grim",
                "expected_severity": "critical",
                "section": "Results",
                "anchor_quote": ANCHOR,
                "description": "GRIM-inconsistent mean.",
                "expected_detector": "statistics",
            }
        ],
    }
    (root / "manifests" / "ms01_quant.defects.json").write_text(
        json.dumps(manifest), encoding="utf-8"
    )


class SeededDefectCheckerTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.root = self.tmp / "reviewer_seeded_defects"
        make_tree(self.root)
        self.expected_kinds = {"ms01_quant": {"SD-01": "grim"}}
        patches = [
            mock.patch.object(mod, "ROOT", self.root),
            mock.patch.object(mod, "MANIFESTS", self.root / "manifests"),
            mock.patch.object(
                mod, "CLEAN_CONTROL", self.root / "manuscripts" / "ms00_clean_control.md"
            ),
            mock.patch.object(mod, "EXPECTED_FIXTURES", {"ms01_quant"}),
            mock.patch.object(
                mod, "EXPECTED_DEFECT_IDS", {"ms01_quant": {"SD-01"}}
            ),
            mock.patch.object(
                mod, "EXPECTED_STATISTICAL_KINDS", self.expected_kinds
            ),
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def mutate(self, fn) -> int:
        path = self.root / "manifests" / "ms01_quant.defects.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        fn(data)
        path.write_text(json.dumps(data), encoding="utf-8")
        return mod.main()

    def test_clean_tree_passes(self):
        self.assertEqual(mod.main(), 0)

    def test_missing_manuscript_fails(self):
        self.assertEqual(
            self.mutate(lambda d: d.update(manuscript="manuscripts/nope.md")), 1
        )

    def test_defect_count_mismatch_fails(self):
        self.assertEqual(self.mutate(lambda d: d.update(defect_count=2)), 1)

    def test_unknown_class_fails(self):
        self.assertEqual(
            self.mutate(lambda d: d["defects"][0].update({"class": "vibes"})), 1
        )

    def test_unknown_severity_fails(self):
        self.assertEqual(
            self.mutate(
                lambda d: d["defects"][0].update({"expected_severity": "fatal"})
            ),
            1,
        )

    def test_anchor_not_in_manuscript_fails(self):
        self.assertEqual(
            self.mutate(
                lambda d: d["defects"][0].update(
                    {"anchor_quote": "eight words that are surely not in the file"}
                )
            ),
            1,
        )

    def test_duplicate_anchor_fails(self):
        ms = self.root / "manuscripts" / "ms01_quant_defective.md"
        ms.write_text(
            ms.read_text(encoding="utf-8") + f"\nDuplicated: {ANCHOR}\n",
            encoding="utf-8",
        )
        self.assertEqual(mod.main(), 1)

    def test_anchor_too_short_fails(self):
        short = "seven words only in this anchor here"
        ms = self.root / "manuscripts" / "ms01_quant_defective.md"
        ms.write_text(
            ms.read_text(encoding="utf-8") + f"\n{short}\n", encoding="utf-8"
        )
        self.assertEqual(
            self.mutate(lambda d: d["defects"][0].update({"anchor_quote": short})), 1
        )

    def test_manifest_pointing_at_clean_control_fails(self):
        self.assertEqual(
            self.mutate(
                lambda d: d.update(manuscript="manuscripts/ms00_clean_control.md")
            ),
            1,
        )

    def test_missing_clean_control_fails(self):
        (self.root / "manuscripts" / "ms00_clean_control.md").unlink()
        self.assertEqual(mod.main(), 1)

    def test_invalid_json_fails(self):
        path = self.root / "manifests" / "ms01_quant.defects.json"
        path.write_text("{not json", encoding="utf-8")
        self.assertEqual(mod.main(), 1)

    def test_missing_top_level_key_fails(self):
        def drop(d):
            del d["fixture_id"]

        self.assertEqual(self.mutate(drop), 1)

    def test_fixture_version_drift_fails(self):
        self.assertEqual(
            self.mutate(lambda d: d.update(fixture_version="0.1")), 1
        )

    def test_missing_defect_field_fails(self):
        def drop(d):
            del d["defects"][0]["description"]

        self.assertEqual(self.mutate(drop), 1)

    def test_unknown_detector_fails(self):
        self.assertEqual(
            self.mutate(
                lambda d: d["defects"][0].update({"expected_detector": "psychic"})
            ),
            1,
        )

    def test_missing_statistical_kind_fails(self):
        def drop(d):
            del d["defects"][0]["statistical_kind"]

        self.assertEqual(self.mutate(drop), 1)

    def test_unknown_statistical_kind_fails(self):
        self.assertEqual(
            self.mutate(
                lambda d: d["defects"][0].update(
                    {"statistical_kind": "calculator_vibes"}
                )
            ),
            1,
        )

    def test_non_statistical_row_cannot_carry_kind(self):
        self.assertEqual(
            self.mutate(lambda d: d["defects"][0].update({"class": "methods"})),
            1,
        )

    def test_statistical_projection_change_fails(self):
        self.assertEqual(
            self.mutate(
                lambda d: d["defects"][0].update(
                    {"statistical_kind": "reporting_only"}
                )
            ),
            1,
        )

    @staticmethod
    def grimmer_oracle(
        *, reported_mean: str = "3.00", reported_sd: str = "0.10",
        convention: str = "sample",
        expected_consistent: bool = False,
    ) -> dict:
        return {
            "type": "integer_scale_mean_sd",
            "n": 10,
            "scale_min": 1,
            "scale_max": 5,
            "reported_mean": reported_mean,
            "reported_sd": reported_sd,
            "sd_convention": convention,
            "rounding": "half_up",
            "expected_consistent": expected_consistent,
        }

    def make_grimmer(
        self, data: dict, *, reported_mean: str = "3.00",
        reported_sd: str = "0.10",
        expected_consistent: bool = False,
    ) -> None:
        oracle = self.grimmer_oracle(
            reported_mean=reported_mean,
            reported_sd=reported_sd,
            expected_consistent=expected_consistent,
        )
        anchor = mod.canonical_recompute_oracle_anchor(oracle)
        manuscript = self.root / "manuscripts" / "ms01_quant_defective.md"
        manuscript.write_text(f"# Synthetic\n\n{anchor}\n", encoding="utf-8")
        data["defects"][0].update(
            {
                "statistical_kind": "grimmer",
                "anchor_quote": anchor,
                "recompute_oracle": oracle,
            }
        )
        self.expected_kinds["ms01_quant"]["SD-01"] = "grimmer"

    def test_grimmer_oracle_proves_planted_inconsistency(self):
        self.assertFalse(
            mod.integer_scale_mean_sd_consistent(self.grimmer_oracle())
        )

    def test_grimmer_oracle_accepts_reachable_zero_sd(self):
        oracle = self.grimmer_oracle(
            reported_sd="0.00", expected_consistent=True
        )
        self.assertTrue(mod.integer_scale_mean_sd_consistent(oracle))

    def test_grimmer_fixture_with_inconsistent_sd_passes(self):
        self.assertEqual(self.mutate(self.make_grimmer), 0)

    def test_grimmer_fixture_changed_to_reachable_sd_fails(self):
        self.assertEqual(
            self.mutate(lambda d: self.make_grimmer(d, reported_sd="0.00")),
            1,
        )

    def test_grimmer_cannot_self_certify_reachable_sd(self):
        self.assertEqual(
            self.mutate(
                lambda d: self.make_grimmer(
                    d, reported_sd="0.00", expected_consistent=True
                )
            ),
            1,
        )

    def test_grimmer_oracle_values_must_match_anchor(self):
        def drift(data: dict) -> None:
            self.make_grimmer(data)
            data["defects"][0]["recompute_oracle"]["n"] = 9

        self.assertEqual(self.mutate(drift), 1)

    def test_grimmer_anchor_prefixes_cannot_impersonate_oracle_values(self):
        def drift(data: dict) -> None:
            self.make_grimmer(data)
            anchor = (
                "the reported secondary-item values were N=1000; M=3.000; "
                "population SD=0.100; integer scale=1-5"
            )
            data["defects"][0]["anchor_quote"] = anchor
            manuscript = self.root / "manuscripts" / "ms01_quant_defective.md"
            manuscript.write_text(f"# Synthetic\n\n{anchor}\n", encoding="utf-8")

        self.assertEqual(self.mutate(drift), 1)

    def test_grimmer_prerequisite_mean_must_be_reachable(self):
        self.assertEqual(
            self.mutate(
                lambda d: self.make_grimmer(d, reported_mean="3.01")
            ),
            1,
        )

    def test_sample_and_population_sd_are_not_interchangeable(self):
        base = {
            "type": "integer_scale_mean_sd",
            "n": 2,
            "scale_min": 1,
            "scale_max": 5,
            "reported_mean": "3.00",
            "reported_sd": "1.00",
            "sd_convention": "population",
            "rounding": "half_up",
            "expected_consistent": True,
        }
        self.assertTrue(mod.integer_scale_mean_sd_consistent(base))
        sample = dict(base, sd_convention="sample", expected_consistent=False)
        self.assertFalse(mod.integer_scale_mean_sd_consistent(sample))

    def test_anchor_too_long_fails(self):
        long_anchor = " ".join(f"w{i}" for i in range(26))
        ms = self.root / "manuscripts" / "ms01_quant_defective.md"
        ms.write_text(
            ms.read_text(encoding="utf-8") + f"\n{long_anchor}\n", encoding="utf-8"
        )
        self.assertEqual(
            self.mutate(
                lambda d: d["defects"][0].update({"anchor_quote": long_anchor})
            ),
            1,
        )

    def test_deleted_manifest_fails_inventory_pin(self):
        (self.root / "manifests" / "ms01_quant.defects.json").unlink()
        self.assertEqual(mod.main(), 1)

    def test_coordinated_deletion_fails_defect_id_pin(self):
        def shrink(d):
            d["defects"] = []
            d["defect_count"] = 0

        self.assertEqual(self.mutate(shrink), 1)

    def test_renamed_defect_id_fails_pin(self):
        self.assertEqual(
            self.mutate(lambda d: d["defects"][0].update({"defect_id": "SD-99"})), 1
        )

    def test_duplicate_fixture_id_across_manifests_fails(self):
        src = self.root / "manifests" / "ms01_quant.defects.json"
        extra = self.root / "manifests" / "ms01_extra.defects.json"
        extra.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        self.assertEqual(mod.main(), 1)

    def test_unmanifested_defective_manuscript_fails(self):
        (self.root / "manuscripts" / "ms03_orphan_defective.md").write_text(
            "# Orphan defective manuscript with no manifest\n", encoding="utf-8"
        )
        self.assertEqual(mod.main(), 1)

    def test_duplicate_defect_id_fails(self):
        def dup(d):
            row = dict(d["defects"][0])
            d["defects"].append(row)
            d["defect_count"] = 2

        ms = self.root / "manuscripts" / "ms01_quant_defective.md"
        # keep anchor unique-count valid for the second row by making it a
        # distinct anchor that also appears once
        second = "a second distinct anchor phrase appearing exactly once in this file"
        ms.write_text(ms.read_text(encoding="utf-8") + f"\n{second}\n", encoding="utf-8")

        def mutate(d):
            row = dict(d["defects"][0])
            row["defect_id"] = "SD-01"  # duplicate id
            row["anchor_quote"] = second
            d["defects"].append(row)
            d["defect_count"] = 2

        self.assertEqual(self.mutate(mutate), 1)


if __name__ == "__main__":
    unittest.main()
