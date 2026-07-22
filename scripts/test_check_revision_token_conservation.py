"""Mutation tests for check_revision_token_conservation.py (#570).

Covers: numeric-token multiset conservation (decimals, percentages,
thousands separators, signs, en-dash ranges), Unicode fold-before-split
ordering (fullwidth digits, U+2212 minus — the #524 lesson: normalize the
whole value BEFORE any split/extract), citation-token conservation
(<!--ref:-->/<!--anchor:--> markers, bracketed groups, author-year),
comment exclusion from prose numbers, protected-term word boundaries,
patch-mode per-op attribution to roadmap_item_ids, ADV-REV advisory-row
rendering, and CLI exit semantics (advisory exit 0 / --strict exit 1).

Run standalone:
    python -m unittest scripts/test_check_revision_token_conservation.py -v
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.check_revision_token_conservation import (
    audit_pair,
    audit_patch,
    extract_citation_tokens,
    extract_numbers,
    main,
    protected_term_counts,
)


class NumberExtractionTests(unittest.TestCase):
    def test_decimal_percentage_is_one_token(self):
        numbers = extract_numbers("Accuracy was 87.08% in 612 participants.")
        self.assertEqual(dict(numbers), {"87.08%": 1, "612": 1})

    def test_thousands_separator_number_is_one_token(self):
        numbers = extract_numbers("We analyzed 612,418 moderation decisions.")
        self.assertEqual(dict(numbers), {"612,418": 1})

    def test_fullwidth_digits_normalized_before_split(self):
        # Fold-before-split: NFKC runs on the whole text BEFORE tokenization,
        # so a fullwidth respelling cannot smuggle a changed value past the
        # multiset comparison (nor false-flag an unchanged one).
        self.assertEqual(
            extract_numbers("准确率为８７.０８％。"),
            extract_numbers("准确率为87.08%。"),
        )

    def test_unicode_minus_normalized_to_ascii(self):
        self.assertEqual(
            extract_numbers("β = −0.45 in the adjusted model."),
            extract_numbers("β = -0.45 in the adjusted model."),
        )

    def test_sign_attaches_after_equals_but_not_inside_range(self):
        numbers = extract_numbers("β = -0.45; 95% CI: 0.58–0.92.")
        self.assertEqual(
            dict(numbers), {"-0.45": 1, "95%": 1, "0.58": 1, "0.92": 1}
        )

    def test_endash_range_conserved_against_hyphen_respelling(self):
        self.assertEqual(
            extract_numbers("(HR = 0.73, 95% CI: 0.58–0.92)"),
            extract_numbers("(HR = 0.73, 95% CI: 0.58-0.92)"),
        )

    def test_sign_inside_brackets_and_after_comma_is_kept(self):
        # A CI lower bound or a comma-separated negative must keep its sign:
        # [-0.45, 0.12] flipping to [0.45, 0.12] is a real change, not conserved.
        numbers = extract_numbers("CI [-0.45, 0.12] and slope of -1.3, 0.7")
        self.assertEqual(
            dict(numbers), {"-0.45": 1, "0.12": 1, "-1.3": 1, "0.7": 1}
        )

    def test_scientific_exponent_is_part_of_the_token(self):
        # 6.02e23 must not truncate to 6.02 (which would let 6.02e23 -> 6.02e24
        # pass as conserved).
        self.assertEqual(dict(extract_numbers("Avogadro 6.02e23 units")), {"6.02e23": 1})
        self.assertEqual(dict(extract_numbers("p = 1.2E-5 overall")), {"1.2E-5": 1})
        self.assertFalse(audit_pair("6.02e23 units", "6.02e24 units")["conserved"])

    def test_letter_adjacent_identifier_digits_are_not_prose_numbers(self):
        numbers = extract_numbers("Contrary to H2, Model-A7 held at T0.")
        self.assertEqual(dict(numbers), {})

    def test_cjk_adjacent_numbers_still_count(self):
        numbers = extract_numbers("本研究共612名受試者，準確率87.08%。")
        self.assertEqual(dict(numbers), {"612": 1, "87.08%": 1})

    def test_marker_comments_excluded_from_prose_numbers(self):
        numbers = extract_numbers(
            "The effect held.<!--ref:li2023--><!--anchor:page:12-->"
        )
        self.assertEqual(dict(numbers), {})


class CitationExtractionTests(unittest.TestCase):
    def test_ref_and_anchor_markers_counted(self):
        tokens = extract_citation_tokens(
            "Claim.<!--ref:smith2024--><!--anchor:quote:stable%20terms-->"
        )
        self.assertEqual(
            dict(tokens),
            {"ref:smith2024": 1, "anchor:quote:stable%20terms": 1},
        )

    def test_author_year_reorder_conserved(self):
        source = "In 612 adults, Model-A7 improved accuracy (Li & Chen, 2023)."
        revision = "Model-A7 improved accuracy in 612 adults (Li & Chen, 2023)."
        self.assertEqual(
            extract_citation_tokens(source), extract_citation_tokens(revision)
        )

    def test_narrative_author_swap_with_same_slug_is_a_delta(self):
        # A narrative citation carries the author OUTSIDE the parenthesized year;
        # swapping "Smith (2020)" -> "Jones (2020)" while keeping the same
        # <!--ref:smith2020--> slug must not read as conserved (the visible
        # attribution changed even though the marker and year did not).
        result = audit_pair(
            "Smith (2020)<!--ref:smith2020--> found X.",
            "Jones (2020)<!--ref:smith2020--> found X.",
        )
        self.assertFalse(result["conserved"])

    def test_narrative_author_year_token_includes_author(self):
        tokens = extract_citation_tokens("As Okonkwo and Vidal (2021) showed,")
        self.assertIn("Okonkwo and Vidal (2021)", dict(tokens))

    def test_resolved_ref_marker_keys_on_slug(self):
        # The finalizer resolves <!--ref:slug--> into 0/1/2-status-token forms
        # (<!--ref:slug ok-->, <!--ref:slug LOW-WARN CONTAMINATED-PREPRINT-->,
        # ... policy_hash=...). Revision reruns run on already-resolved drafts,
        # so the checker must key the citation multiset on the SLUG alone —
        # status/suffix tokens are derived metadata, idempotently recomputed,
        # never writer content. Bare vs resolved must NOT read as a delta.
        bare = extract_citation_tokens("Claim.<!--ref:smith2024-->")
        resolved = extract_citation_tokens(
            "Claim.<!--ref:smith2024 LOW-WARN CONTAMINATED-PREPRINT-->"
        )
        self.assertEqual(bare, resolved)
        self.assertEqual(dict(bare), {"ref:smith2024": 1})

    def test_dropped_resolved_ref_marker_is_a_delta(self):
        # The regression the checker exists to catch: a resolved marker deleted
        # during revision must surface, not vanish under COMMENT_RE stripping.
        result = audit_pair(
            "The effect held.<!--ref:li2023 ok policy_hash=abc123-->",
            "The effect held.",
        )
        self.assertFalse(result["conserved"])
        self.assertEqual(result["citations_delta"]["removed"], {"ref:li2023": 1})

    def test_bracketed_group_change_flagged(self):
        self.assertNotEqual(
            extract_citation_tokens("The score rose [17]."),
            extract_citation_tokens("The score rose [18]."),
        )

    def test_markdown_link_is_not_a_citation(self):
        tokens = extract_citation_tokens("See [the appendix](https://x.test).")
        self.assertEqual(dict(tokens), {})


class ProtectedTermTests(unittest.TestCase):
    def test_short_term_uses_word_boundaries(self):
        counts = protected_term_counts("AI evidence, as they SAID, is limited.", ["AI"])
        self.assertEqual(counts["AI"], 1)

    def test_case_change_counts_as_loss(self):
        source = protected_term_counts("Normalized to GAPDH.", ["GAPDH"])
        revision = protected_term_counts("Normalized to Gapdh.", ["GAPDH"])
        self.assertNotEqual(source, revision)


class AuditPairTests(unittest.TestCase):
    def test_reordering_with_identical_tokens_is_conserved(self):
        result = audit_pair(
            "In 612 participants, Model-A7 reached 87.08% (Li, 2023).",
            "Model-A7 reached 87.08% among 612 participants (Li, 2023).",
            protected_terms=["Model-A7"],
        )
        self.assertTrue(result["conserved"])
        self.assertEqual(result["numbers_delta"], {"removed": {}, "added": {}})

    def test_changed_decimal_reports_removed_and_added(self):
        result = audit_pair(
            "The hazard ratio was 0.73.", "The hazard ratio was 0.75."
        )
        self.assertFalse(result["conserved"])
        self.assertEqual(result["numbers_delta"]["removed"], {"0.73": 1})
        self.assertEqual(result["numbers_delta"]["added"], {"0.75": 1})

    def test_dropped_ref_marker_reports_citation_delta(self):
        result = audit_pair(
            "The effect held.<!--ref:li2023-->", "The effect held."
        )
        self.assertFalse(result["conserved"])
        self.assertEqual(result["citations_delta"]["removed"], {"ref:li2023": 1})


PATCH_BASE = """# Results

<!--block:B0001-->
Model-A7 reached 87.08% accuracy in 612 participants (Li, 2023).

<!--block:B0002-->
The null result for H2 held (β = 0.04, p = 0.41).<!--ref:ahmed2022-->

<!--block:B0003-->
Recruitment used one online panel, which may limit generalizability.
"""


def _patch(ops):
    return {
        "patch_format_version": "1.0",
        "revision_round": 1,
        "base_draft_hash": "0" * 12,
        "ops": ops,
        "emitted_by": "draft_writer_agent",
    }


class AuditPatchTests(unittest.TestCase):
    def test_replace_op_delta_attributed_to_roadmap_items(self):
        report = audit_patch(
            _patch(
                [
                    {
                        "op": "replace_block",
                        "block_id": "B0001",
                        "old_hash": "x",
                        "new_text": "Model-A7 reached 89.00% accuracy in 612 participants (Li, 2023).",
                        "roadmap_item_ids": ["R-2"],
                    }
                ]
            ),
            PATCH_BASE,
        )
        self.assertFalse(report["conserved"])
        (row,) = report["op_reports"]
        self.assertEqual(row["block_id"], "B0001")
        self.assertEqual(row["roadmap_item_ids"], ["R-2"])
        self.assertEqual(row["delta"]["numbers_delta"]["removed"], {"87.08%": 1})
        self.assertEqual(row["delta"]["numbers_delta"]["added"], {"89.00%": 1})

    def test_insert_and_delete_ops_report_added_and_removed_tokens(self):
        report = audit_patch(
            _patch(
                [
                    {
                        "op": "insert_after",
                        "block_id": "B0003",
                        "old_hash": "x",
                        "new_text": "A replication in 2,048 users is planned.",
                        "roadmap_item_ids": ["R-5"],
                    },
                    {
                        "op": "delete_block",
                        "block_id": "B0002",
                        "old_hash": "x",
                        "roadmap_item_ids": ["R-6"],
                    },
                ]
            ),
            PATCH_BASE,
        )
        by_block = {r["block_id"]: r for r in report["op_reports"]}
        self.assertEqual(
            by_block["B0003"]["delta"]["numbers_delta"]["added"], {"2,048": 1}
        )
        removed = by_block["B0002"]["delta"]["numbers_delta"]["removed"]
        self.assertEqual(removed, {"0.04": 1, "0.41": 1})
        self.assertEqual(
            by_block["B0002"]["delta"]["citations_delta"]["removed"],
            {"ref:ahmed2022": 1},
        )

    def test_conserved_patch_yields_no_advisory_rows(self):
        report = audit_patch(
            _patch(
                [
                    {
                        "op": "replace_block",
                        "block_id": "B0003",
                        "old_hash": "x",
                        "new_text": "Because recruitment used one online panel, generalizability may be limited.",
                        "roadmap_item_ids": ["R-1"],
                    }
                ]
            ),
            PATCH_BASE,
        )
        self.assertTrue(report["conserved"])
        self.assertEqual(report["advisory_rows"], [])

    def test_advisory_rows_numbered_and_carry_roadmap_ids(self):
        report = audit_patch(
            _patch(
                [
                    {
                        "op": "replace_block",
                        "block_id": "B0001",
                        "old_hash": "x",
                        "new_text": "Model-A7 reached 89% accuracy in 612 participants (Li, 2023).",
                        "roadmap_item_ids": ["R-2", "R-3"],
                    },
                    {
                        "op": "delete_block",
                        "block_id": "B0002",
                        "old_hash": "x",
                        "roadmap_item_ids": ["R-6"],
                    },
                ]
            ),
            PATCH_BASE,
        )
        self.assertEqual(len(report["advisory_rows"]), 2)
        self.assertTrue(report["advisory_rows"][0].startswith("ADV-REV-1:"))
        self.assertTrue(report["advisory_rows"][1].startswith("ADV-REV-2:"))
        self.assertIn("R-2", report["advisory_rows"][0])
        self.assertIn("R-6", report["advisory_rows"][1])


class CliTests(unittest.TestCase):
    def _run(self, *argv):
        return subprocess.run(
            [sys.executable, "scripts/check_revision_token_conservation.py", *argv],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )

    def test_pair_mode_advisory_exit_zero_despite_delta(self):
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "src.md"
            rev = Path(td) / "rev.md"
            src.write_text("Accuracy was 87.08%.", encoding="utf-8")
            rev.write_text("Accuracy was 88.00%.", encoding="utf-8")
            proc = self._run("pair", "--source", str(src), "--revision", str(rev))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertFalse(payload["conserved"])

    def test_pair_mode_strict_exit_one_on_delta_zero_when_conserved(self):
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "src.md"
            rev = Path(td) / "rev.md"
            src.write_text("Accuracy was 87.08%.", encoding="utf-8")
            rev.write_text("Accuracy was 88.00%.", encoding="utf-8")
            same = Path(td) / "same.md"
            same.write_text("Accuracy was 87.08%, unchanged.", encoding="utf-8")
            drifted = self._run(
                "pair", "--source", str(src), "--revision", str(rev), "--strict"
            )
            conserved = self._run(
                "pair", "--source", str(src), "--revision", str(same), "--strict"
            )
        self.assertEqual(drifted.returncode, 1)
        self.assertEqual(conserved.returncode, 0, conserved.stderr)

    def test_patch_mode_cli_reports_op_rows(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td) / "base.md"
            patch = Path(td) / "patch.json"
            base.write_text(PATCH_BASE, encoding="utf-8")
            patch.write_text(
                json.dumps(
                    _patch(
                        [
                            {
                                "op": "replace_block",
                                "block_id": "B0001",
                                "old_hash": "x",
                                "new_text": "Model-A7 reached 90% accuracy in 612 participants (Li, 2023).",
                                "roadmap_item_ids": ["R-2"],
                            }
                        ]
                    )
                ),
                encoding="utf-8",
            )
            proc = self._run("patch", "--patch", str(patch), "--base", str(base))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["op_reports"][0]["roadmap_item_ids"], ["R-2"])
        self.assertEqual(len(payload["advisory_rows"]), 1)


if __name__ == "__main__":
    unittest.main()
