"""Mutation tests for check_seeded_defect_fixtures.py (#574 E4 v0.1).

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
        "manuscript": "manuscripts/ms01_quant_defective.md",
        "defect_count": 1,
        "defects": [
            {
                "defect_id": "SD-01",
                "class": "statistical",
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
