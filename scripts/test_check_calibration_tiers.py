"""Mutation tests for the bounded reviewer calibration contract."""
from __future__ import annotations

import shutil
import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from tests.test_helpers import run_script


SCRIPT = Path(__file__).resolve().parent / "check_calibration_tiers.py"
REPO_ROOT = SCRIPT.parent.parent
PROTOCOL = Path("academic-paper-reviewer/references/calibration_mode_protocol.md")
SKILL = Path("academic-paper-reviewer/SKILL.md")
HANDOFF = Path("shared/handoff_schemas.md")
SYNTHESIZER = Path("academic-paper-reviewer/agents/editorial_synthesizer_agent.md")
PEER_REVIEWER = Path("academic-paper/agents/peer_reviewer_agent.md")
WORKFLOW = Path("academic-paper/references/workflow_phase_details.md")
CROSS_MODEL = Path("shared/cross_model_verification.md")


def _run(root: Path) -> subprocess.CompletedProcess:
    return run_script(SCRIPT, "--root", str(root))


def _tree(root: Path) -> None:
    for rel in (
        PROTOCOL,
        SKILL,
        HANDOFF,
        SYNTHESIZER,
        PEER_REVIEWER,
        WORKFLOW,
        CROSS_MODEL,
    ):
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO_ROOT / rel, target)


def _replace(root: Path, rel: Path, old: str, new: str) -> None:
    path = root / rel
    text = path.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise AssertionError(
            f"mutation anchor must occur exactly once in {rel}: {old!r}"
        )
    path.write_text(text.replace(old, new), encoding="utf-8")


class TestCalibrationTiers(unittest.TestCase):
    def test_real_repo_passes(self) -> None:
        result = _run(REPO_ROOT)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_missing_protocol_fails_loud(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _tree(root)
            (root / PROTOCOL).unlink()
            result = _run(root)
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)

    def test_directional_not_calibrated_is_required(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _tree(root)
            path = root / PROTOCOL
            path.write_text(
                path.read_text(encoding="utf-8").replace(
                    "The directional tier always reports `calibration_status: NOT_CALIBRATED`",
                    "The directional tier reports a compact readout",
                ),
                encoding="utf-8",
            )
            result = _run(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("missing witness", result.stderr)

    def test_legacy_gold_scores_are_rejected(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _tree(root)
            path = root / PROTOCOL
            path.write_text(
                path.read_text(encoding="utf-8") + "\nper_dimension_gold_scores\n",
                encoding="utf-8",
            )
            result = _run(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("retired numeric calibration token", result.stderr)

    def test_weighted_average_is_rejected(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _tree(root)
            path = root / PROTOCOL
            path.write_text(
                path.read_text(encoding="utf-8") + "\nWeighted Average\n",
                encoding="utf-8",
            )
            result = _run(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    def test_fixed_decision_mapping_is_rejected(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _tree(root)
            path = root / PROTOCOL
            path.write_text(
                path.read_text(encoding="utf-8")
                + "\n≥80 Accept, 65-79 Minor, 50-64 Major, <50 Reject\n",
                encoding="utf-8",
            )
            result = _run(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("fixed score-to-decision mapping", result.stderr)

    def test_live_package_profile_upgrade_witness_is_required(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _tree(root)
            path = root / SYNTHESIZER
            path.write_text(
                path.read_text(encoding="utf-8").replace(
                    "Set the package-level `calibration_status` to `NOT_CALIBRATED`",
                    "Set the package calibration from any attached profile name",
                ),
                encoding="utf-8",
            )
            result = _run(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("missing witness", result.stderr)

    def test_protocol_gold_isolation_is_required(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _tree(root)
            _replace(
                root,
                PROTOCOL,
                "This isolation applies to transport as well as prompt construction",
                "Gold may be included during transport construction",
            )
            result = _run(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("missing witness", result.stderr)

    def test_cross_replicate_freshness_claim_ceiling_is_required(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _tree(root)
            _replace(
                root,
                PROTOCOL,
                "does not establish cross-replicate freshness or independent error processes",
                "establishes fresh and independent replicate panels",
            )
            result = _run(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("missing witness", result.stderr)

    def test_legacy_cross_replicate_freshness_claim_is_rejected(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _tree(root)
            path = root / PROTOCOL
            path.write_text(
                path.read_text(encoding="utf-8")
                + "\nFull-tier repeats use fresh contexts.\n",
                encoding="utf-8",
            )
            result = _run(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("overstated cross-replicate freshness claim", result.stderr)

    def test_joined_gold_cannot_feed_back_into_a_panel(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _tree(root)
            _replace(
                root,
                PROTOCOL,
                "joined material cannot be fed back into another panel",
                "joined material may guide the next panel",
            )
            result = _run(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("missing witness", result.stderr)

    def test_transport_excludes_gold_inputs(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _tree(root)
            _replace(
                root,
                CROSS_MODEL,
                "any gold label, human score, per-dimension gold, or gold rationale",
                "gold labels and rationales may accompany the manuscript",
            )
            result = _run(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("gold isolation", result.stderr)

    def test_both_closed_delimiter_predicates_are_required(self) -> None:
        predicates = (
            r"`</\s*reviewer_configuration\b[^>]*>`",
            r"`</\s*paper_content\b[^>]*>`",
        )
        for predicate in predicates:
            with self.subTest(predicate=predicate), TemporaryDirectory() as tmp:
                root = Path(tmp)
                _tree(root)
                _replace(root, CROSS_MODEL, predicate, "exact closing tag only")
                result = _run(root)
                self.assertEqual(
                    result.returncode, 1, result.stdout + result.stderr
                )
                self.assertIn("delimiter-collision preflight", result.stderr)

    def test_collision_refuses_transport_without_rewriting(self) -> None:
        anchors = (
            (
                "refuse the entire calibration attempt before transport and send no provider call containing either payload",
                "send the provider call after a warning",
            ),
            (
                "MUST NOT escape, strip, rewrite, truncate, switch delimiters, or fall back to primary routing",
                "escape the delimiter and continue",
            ),
        )
        for old, new in anchors:
            with self.subTest(anchor=old), TemporaryDirectory() as tmp:
                root = Path(tmp)
                _tree(root)
                _replace(root, CROSS_MODEL, old, new)
                result = _run(root)
                self.assertEqual(
                    result.returncode, 1, result.stdout + result.stderr
                )
                self.assertIn("delimiter-collision preflight", result.stderr)

    def test_calibration_transport_is_homogeneous(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _tree(root)
            _replace(
                root,
                CROSS_MODEL,
                "every paper and replicate uses the single-call branch above",
                "some papers may use a different transport after fallback",
            )
            result = _run(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("homogeneous calibration transport", result.stderr)

    def test_active_protocol_requires_one_transport_and_substrate(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _tree(root)
            _replace(
                root,
                PROTOCOL,
                "use the same transport and substrate for every paper",
                "allow a different transport for each paper",
            )
            result = _run(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("missing witness", result.stderr)

    def test_mid_attempt_failure_invalidates_all_aggregates(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _tree(root)
            _replace(
                root,
                CROSS_MODEL,
                "diagnostic-only and MUST NOT enter any aggregate",
                "may remain in the result aggregate",
            )
            result = _run(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("attempt-atomic restart", result.stderr)

    def test_retry_uses_new_attempt_and_restarts_from_first_panel(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _tree(root)
            _replace(
                root,
                CROSS_MODEL,
                "new `attempt_id`, an empty aggregate, and a restart at paper 1 / replicate 1",
                "reuse the attempt and resume at the failed panel",
            )
            result = _run(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("attempt-atomic restart", result.stderr)

    def test_active_protocol_retry_cannot_resume_a_failed_attempt(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _tree(root)
            _replace(
                root,
                PROTOCOL,
                "Never resume the failed attempt, mix",
                "Resume the failed attempt and mix",
            )
            result = _run(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("missing witness", result.stderr)

    def test_live_peer_reviewer_status_is_unconditional(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _tree(root)
            _replace(
                root,
                PEER_REVIEWER,
                "unconditionally in the current release",
                "unless a matching profile is attached",
            )
            result = _run(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("must be unconditional", result.stderr)

    def test_live_workflow_status_is_unconditional(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _tree(root)
            _replace(
                root,
                WORKFLOW,
                "unconditionally in the current release",
                "unless a matching profile is attached",
            )
            result = _run(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("must be unconditional", result.stderr)

    def test_live_disclosure_cannot_claim_only_that_no_profile_matched(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _tree(root)
            _replace(
                root,
                PROTOCOL,
                "Live profile application is not implemented in the current release",
                "No empirical target profile matches this review",
            )
            result = _run(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("not merely that no profile matched", result.stderr)

    def test_candidate_application_status_is_pinned_on_live_surfaces(self) -> None:
        for rel in (PEER_REVIEWER, WORKFLOW):
            with self.subTest(rel=str(rel)), TemporaryDirectory() as tmp:
                root = Path(tmp)
                _tree(root)
                _replace(
                    root,
                    rel,
                    "`application_status: NOT_WIRED_TO_LIVE_REVIEW`",
                    "candidate profile application is available",
                )
                result = _run(root)
                self.assertEqual(
                    result.returncode, 1, result.stdout + result.stderr
                )
                self.assertIn("missing witness", result.stderr)


if __name__ == "__main__":
    unittest.main()
