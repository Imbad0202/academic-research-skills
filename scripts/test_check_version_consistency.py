"""Unit tests for check_version_consistency.py."""
from __future__ import annotations

import subprocess
import textwrap
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from tests.test_helpers import run_script

SCRIPT = Path(__file__).resolve().parent / "check_version_consistency.py"


def _run(root: Path) -> subprocess.CompletedProcess:
    return run_script(SCRIPT, "--path", str(root))


def _write_skill(root: Path, name: str, version: str) -> None:
    skill_dir = root / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(
        textwrap.dedent(
            f"""\
            ---
            name: {name}
            description: "fixture"
            metadata:
              version: "{version}"
              last_updated: "2026-04-22"
              status: active
              data_access_level: raw
              task_type: open-ended
            ---

            # {name}
            """
        ),
        encoding="utf-8",
    )


def _write_claude_md(
    root: Path,
    suite_version: str,
    table_rows: list[tuple[str, str]],
) -> None:
    claude_dir = root / ".claude"
    claude_dir.mkdir(parents=True, exist_ok=True)
    rows = "\n".join(
        f"| `{name}` v{ver} | purpose | modes |" for name, ver in table_rows
    )
    text = (
        "# Academic Research Skills\n"
        "\n"
        "## Skills Overview\n"
        "\n"
        "| Skill | Purpose | Key Modes |\n"
        "|-------|---------|-----------|\n"
        f"{rows}\n"
        "\n"
        "## Version Info\n"
        f"- **Suite version**: {suite_version} (per CHANGELOG.md)\n"
    )
    (claude_dir / "CLAUDE.md").write_text(text, encoding="utf-8")


def _write_changelog(
    root: Path,
    latest_version: str,
    prior_versions: list[str] | None = None,
) -> None:
    """Write fixture CHANGELOG with `latest_version` first, then any `prior_versions`."""
    entries = [f"## [{latest_version}] - 2026-04-22\n\n### Added\n- fixture entry\n"]
    for prev in prior_versions or []:
        entries.append(f"## [{prev}] - 2026-04-15\n\n### Added\n- prior fixture entry\n")
    (root / "CHANGELOG.md").write_text(
        "# Changelog\n\n" + "\n".join(entries),
        encoding="utf-8",
    )


def _write_plugin_manifests(root: Path, version: str) -> None:
    """Fixture .claude-plugin/{plugin,marketplace}.json at `version` (invariant 4)."""
    import json
    plugin_dir = root / ".claude-plugin"
    plugin_dir.mkdir(parents=True, exist_ok=True)
    (plugin_dir / "plugin.json").write_text(
        json.dumps({"name": "fixture", "version": version}), encoding="utf-8"
    )
    (plugin_dir / "marketplace.json").write_text(
        json.dumps({"name": "fixture", "plugins": [{"name": "fixture", "version": version}]}),
        encoding="utf-8",
    )


def _write_aligned_fixture(root: Path) -> None:
    """Everything lines up — baseline for PASS cases and drift mutations."""
    skills = [
        ("deep-research", "2.9.0"),
        ("academic-paper", "3.1.0"),
        ("academic-paper-reviewer", "1.8.1"),
        ("academic-pipeline", "3.5.0"),
    ]
    for name, ver in skills:
        _write_skill(root, name, ver)
    _write_claude_md(root, suite_version="3.5.0", table_rows=skills)
    _write_changelog(root, latest_version="3.5.0")
    _write_plugin_manifests(root, "3.5.0")


def _write_aligned_fixture_v351(root: Path) -> None:
    """v3.5.1 suite: deep-research 2.9.1, academic-pipeline 3.5.1."""
    skills = [
        ("deep-research", "2.9.1"),
        ("academic-paper", "3.1.0"),
        ("academic-paper-reviewer", "1.8.1"),
        ("academic-pipeline", "3.5.1"),
    ]
    for name, ver in skills:
        _write_skill(root, name, ver)
    _write_claude_md(root, suite_version="3.5.1", table_rows=skills)
    _write_changelog(root, latest_version="3.5.1")
    _write_plugin_manifests(root, "3.5.1")


class TestVersionConsistency(unittest.TestCase):
    def test_all_aligned_passes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_aligned_fixture(root)
            result = _run(root)
            self.assertEqual(
                result.returncode, 0,
                msg=f"stdout={result.stdout!r} stderr={result.stderr!r}",
            )

    def test_all_aligned_v351_passes(self) -> None:
        """v3.5.1 suite (deep-research 2.9.1, academic-pipeline 3.5.1) must pass."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_aligned_fixture_v351(root)
            result = _run(root)
            self.assertEqual(
                result.returncode, 0,
                msg=f"stdout={result.stdout!r} stderr={result.stderr!r}",
            )

    def test_table_version_drift_fails(self) -> None:
        """Table lists deep-research v2.9.0 but SKILL.md says 2.8.0 — must fail."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_aligned_fixture(root)
            _write_skill(root, "deep-research", "2.8.0")
            result = _run(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("deep-research", result.stdout)
            self.assertIn("2.9.0", result.stdout)
            self.assertIn("2.8.0", result.stdout)

    def test_suite_version_vs_changelog_drift_fails(self) -> None:
        """CLAUDE.md suite version != CHANGELOG latest entry — must fail."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_aligned_fixture(root)
            _write_changelog(root, latest_version="3.4.0")
            result = _run(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("3.5.0", result.stdout)
            self.assertIn("3.4.0", result.stdout)
            self.assertIn("CHANGELOG", result.stdout)

    def test_plugin_json_version_drift_fails(self) -> None:
        """Invariant 4: .claude-plugin/plugin.json version != suite — must fail.
        (Regression for the v3.10.0 release miss: plugin.json sat at the prior
        version because no lint covered it.)"""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_aligned_fixture(root)  # suite 3.5.0
            _write_plugin_manifests(root, "3.4.0")  # drift both manifests down
            result = _run(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("plugin.json", result.stdout)
            self.assertIn("3.4.0", result.stdout)
            self.assertIn("3.5.0", result.stdout)

    def test_marketplace_version_drift_fails(self) -> None:
        """Invariant 4: marketplace.json plugins[].version != suite — must fail.
        (Regression for marketplace.json silently sitting at 3.7.0 for releases.)"""
        import json
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_aligned_fixture(root)  # suite 3.5.0; plugin.json aligned at 3.5.0
            # Drift ONLY marketplace, leaving plugin.json correct, to isolate it.
            (root / ".claude-plugin" / "marketplace.json").write_text(
                json.dumps({"name": "fixture",
                            "plugins": [{"name": "fixture", "version": "3.7.0"}]}),
                encoding="utf-8",
            )
            result = _run(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("marketplace.json", result.stdout)
            self.assertIn("3.7.0", result.stdout)

    def test_pipeline_version_vs_suite_drift_fails(self) -> None:
        """academic-pipeline version in table must equal suite version."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_aligned_fixture(root)
            # Drop pipeline to 3.4.0 in both table and SKILL.md, keep suite at 3.5.0.
            # This isolates invariant 3 (pipeline tracks suite) from invariant 1
            # (SKILL.md == table).
            _write_skill(root, "academic-pipeline", "3.4.0")
            _write_claude_md(
                root,
                suite_version="3.5.0",
                table_rows=[
                    ("deep-research", "2.9.0"),
                    ("academic-paper", "3.1.0"),
                    ("academic-paper-reviewer", "1.8.1"),
                    ("academic-pipeline", "3.4.0"),
                ],
            )
            result = _run(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("academic-pipeline", result.stdout)

    def test_skill_missing_frontmatter_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_aligned_fixture(root)
            (root / "deep-research" / "SKILL.md").write_text(
                "# deep-research\n\nNo frontmatter here.\n",
                encoding="utf-8",
            )
            result = _run(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("deep-research", result.stdout)

    def test_skill_listed_in_table_but_missing_on_disk_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_aligned_fixture(root)
            import shutil
            shutil.rmtree(root / "academic-paper-reviewer")
            result = _run(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("academic-paper-reviewer", result.stdout)

    def test_missing_suite_version_in_claude_md_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_aligned_fixture(root)
            (root / ".claude" / "CLAUDE.md").write_text(
                textwrap.dedent(
                    """\
                    # Academic Research Skills

                    ## Skills Overview

                    | Skill | Purpose | Key Modes |
                    |-------|---------|-----------|
                    | `deep-research` v2.9.0 | x | y |
                    | `academic-paper` v3.1.0 | x | y |
                    | `academic-paper-reviewer` v1.8.1 | x | y |
                    | `academic-pipeline` v3.5.0 | x | y |

                    ## Version Info
                    - No suite version line here.
                    """
                ),
                encoding="utf-8",
            )
            result = _run(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("Suite version", result.stdout)

    def test_four_segment_suite_vs_changelog_drift_fails(self) -> None:
        """Regression for #169: 4-segment hotfix versions (e.g. 3.9.4.1 vs 3.9.4.2)
        must not be silently parsed as a shared 3-segment prefix.

        Scenario: suite claims v3.9.4.2 but CHANGELOG's latest entry is v3.9.4.1.
        Pre-fix behavior: both got truncated to "3.9.4" and the lint passed silently.
        """
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            skills = [
                ("deep-research", "2.9.4"),
                ("academic-paper", "3.1.2"),
                ("academic-paper-reviewer", "1.9.1"),
                ("academic-pipeline", "3.9.4.2"),
            ]
            for name, ver in skills:
                _write_skill(root, name, ver)
            _write_claude_md(root, suite_version="3.9.4.2", table_rows=skills)
            # Include the 3-segment ancestor so the pre-fix regex would still find
            # *something* and silently report a passing 3.9.4 == 3.9.4 comparison.
            _write_changelog(
                root, latest_version="3.9.4.1", prior_versions=["3.9.4"],
            )
            result = _run(root)
            self.assertEqual(
                result.returncode, 1,
                msg=f"stdout={result.stdout!r} stderr={result.stderr!r}",
            )
            self.assertIn("3.9.4.2", result.stdout)
            self.assertIn("3.9.4.1", result.stdout)
            self.assertIn("CHANGELOG", result.stdout)

    def test_five_segment_changelog_does_not_silently_fall_through(self) -> None:
        """Regression for dual-track review of #169: an N+1 segment latest
        entry (e.g. 3.9.4.2.1) must not silently skip to the next valid
        3-or-4 segment predecessor. Pre-fix CHANGELOG_ENTRY_RE failed on
        the 5-segment heading and `re.search` fell through to a predecessor;
        if that predecessor happened to equal the suite version, the lint
        reported PASS even though the actual latest release was a different
        version."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            skills = [
                ("deep-research", "2.9.4"),
                ("academic-paper", "3.1.2"),
                ("academic-paper-reviewer", "1.9.1"),
                ("academic-pipeline", "3.9.4.2"),
            ]
            for name, ver in skills:
                _write_skill(root, name, ver)
            _write_claude_md(root, suite_version="3.9.4.2", table_rows=skills)
            _write_changelog(
                root, latest_version="3.9.4.2.1", prior_versions=["3.9.4.2"],
            )
            result = _run(root)
            self.assertEqual(
                result.returncode, 1,
                msg=f"stdout={result.stdout!r} stderr={result.stderr!r}",
            )
            self.assertIn("3.9.4.2.1", result.stdout)
            # Either path is acceptable surfacing: either the suite-vs-CHANGELOG
            # mismatch (if the new 5-seg token is itself accepted as canonical
            # under the broadened validator) or an invalid-token report.
            self.assertTrue(
                "does not match CHANGELOG latest entry" in result.stdout
                or "canonical" in result.stdout,
                msg=f"expected either drift or invalid-token surface: {result.stdout!r}",
            )

    def test_invalid_table_row_token_is_reported(self) -> None:
        """Regression for dual-track review of #169: a table row carrying a
        non-canonical version token (e.g. v3.9.4.2-alpha or v3.9.4.2.1) must
        surface as an error. Pre-fix: TABLE_ROW_RE failed and the row silently
        vanished from table_versions, so invariant 3 (pipeline tracks suite)
        was skipped because `pipeline_in_table` ended up None."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            skills_on_disk = [
                ("deep-research", "2.9.4"),
                ("academic-paper", "3.1.2"),
                ("academic-paper-reviewer", "1.9.1"),
                ("academic-pipeline", "3.9.4.2"),
            ]
            for name, ver in skills_on_disk:
                _write_skill(root, name, ver)
            table_rows_with_junk = [
                ("deep-research", "2.9.4"),
                ("academic-paper", "3.1.2"),
                ("academic-paper-reviewer", "1.9.1"),
                ("academic-pipeline", "3.9.4.2-alpha"),  # invalid token
            ]
            _write_claude_md(
                root, suite_version="3.9.4.2", table_rows=table_rows_with_junk
            )
            _write_changelog(
                root, latest_version="3.9.4.2", prior_versions=["3.9.4"],
            )
            result = _run(root)
            self.assertEqual(
                result.returncode, 1,
                msg=f"stdout={result.stdout!r} stderr={result.stderr!r}",
            )
            self.assertIn("academic-pipeline", result.stdout)
            self.assertIn("3.9.4.2-alpha", result.stdout)
            self.assertIn("canonical", result.stdout)

    def test_invalid_suite_token_is_reported(self) -> None:
        """Regression for dual-track review of #169: a non-canonical suite
        version token (e.g. 3.9.4.2-alpha) must surface as an error rather
        than being partially captured as 3.9.4.2 via prefix match."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            skills = [
                ("deep-research", "2.9.4"),
                ("academic-paper", "3.1.2"),
                ("academic-paper-reviewer", "1.9.1"),
                ("academic-pipeline", "3.9.4.2"),
            ]
            for name, ver in skills:
                _write_skill(root, name, ver)
            _write_claude_md(
                root, suite_version="3.9.4.2-alpha", table_rows=skills
            )
            _write_changelog(
                root, latest_version="3.9.4.2", prior_versions=["3.9.4"],
            )
            result = _run(root)
            self.assertEqual(
                result.returncode, 1,
                msg=f"stdout={result.stdout!r} stderr={result.stderr!r}",
            )
            self.assertIn("3.9.4.2-alpha", result.stdout)
            self.assertIn("canonical", result.stdout)

    def test_four_segment_table_row_drift_fails(self) -> None:
        """Regression for #169: the Skills table row regex must also see the 4th
        segment, so a pipeline row v3.9.4.1 vs suite version 3.9.4.2 is caught."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            # Pipeline SKILL.md and CHANGELOG both at 3.9.4.2, but the table row
            # in CLAUDE.md still says v3.9.4.1 (forgot to bump one place).
            skills_on_disk = [
                ("deep-research", "2.9.4"),
                ("academic-paper", "3.1.2"),
                ("academic-paper-reviewer", "1.9.1"),
                ("academic-pipeline", "3.9.4.2"),
            ]
            for name, ver in skills_on_disk:
                _write_skill(root, name, ver)
            table_rows_drifted = [
                ("deep-research", "2.9.4"),
                ("academic-paper", "3.1.2"),
                ("academic-paper-reviewer", "1.9.1"),
                ("academic-pipeline", "3.9.4.1"),  # drift inside the 4th segment
            ]
            _write_claude_md(
                root, suite_version="3.9.4.2", table_rows=table_rows_drifted
            )
            _write_changelog(
                root, latest_version="3.9.4.2", prior_versions=["3.9.4"],
            )
            result = _run(root)
            self.assertEqual(
                result.returncode, 1,
                msg=f"stdout={result.stdout!r} stderr={result.stderr!r}",
            )
            self.assertIn("academic-pipeline", result.stdout)
            self.assertIn("3.9.4.1", result.stdout)
            self.assertIn("3.9.4.2", result.stdout)

    def test_five_segment_token_rejected_as_non_canonical(self) -> None:
        """Regression for #178: post-ship codex review of PR #173 flagged that
        SEMVER_STRICT_RE used `{2,}` (3 or more dot segments) with no upper
        bound, so a 5-segment token like 3.9.4.2.1 passed the canonical check
        even though the file-level docstrings and #173 design defined canonical
        as N.N.N or N.N.N.N. If a 5-segment typo were copied consistently to
        CLAUDE.md, CHANGELOG.md, and the pipeline table, the lint would have
        passed despite the malformed shape. Cap to {2,3}: 4 segments max."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            # All four sources self-consistent on a 5-segment typo. Pre-fix:
            # all three regexes captured "3.9.4.2.1" verbatim, _is_strict_semver
            # returned True (matched {2,} = 3 or more segments), and every
            # invariant compared two identical strings — lint reported PASS
            # even though the shape was malformed. Post-fix: SEMVER_STRICT_RE
            # rejects 5+ segments, so the suite, table row, and CHANGELOG
            # entry all surface as "canonical" violations.
            skills_5seg = [
                ("deep-research", "2.9.4"),
                ("academic-paper", "3.1.2"),
                ("academic-paper-reviewer", "1.9.1"),
                ("academic-pipeline", "3.9.4.2.1"),
            ]
            for name, ver in skills_5seg:
                _write_skill(root, name, ver)
            _write_claude_md(
                root, suite_version="3.9.4.2.1", table_rows=skills_5seg
            )
            _write_changelog(
                root, latest_version="3.9.4.2.1", prior_versions=["3.9.4.2"],
            )
            result = _run(root)
            self.assertEqual(
                result.returncode, 1,
                msg=f"stdout={result.stdout!r} stderr={result.stderr!r}",
            )
            self.assertIn("3.9.4.2.1", result.stdout)
            self.assertIn("canonical", result.stdout)


if __name__ == "__main__":
    unittest.main()
