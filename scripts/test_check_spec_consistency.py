"""Unit tests for check_spec_consistency.py.

Pre-#171, check_spec_consistency.py uses module-level ROOT + ERRORS state.
These tests monkey-patch ROOT into a TemporaryDirectory containing a minimal
fixture README, drive a specific checker directly, and read ERRORS. When
#171 lands the schema-driven manifest, these tests rewrite to call the
manifest runner instead.
"""
from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts import check_spec_consistency as csc


# Minimal ja-JP README capturing the version-bearing surfaces the lint needs
# to police: badge, release tag link, three release blocks (current + two
# prior so the symmetric structure with check_readme_zh_sections is visible),
# four localized mode headings, four skill-detail headings, and the DOCX line.
JA_README_TEMPLATE = """\
# Academic Research Skills

[![Version](https://img.shields.io/badge/version-v{ver}-blue)](https://github.com/Imbad0202/academic-research-skills/releases/tag/v{ver})

## クイックスタート

#### Deep Research（7 モード）
- outline-only モード
- abstract-only モード
- disclosure モード
- review モード

#### Academic Paper（10 モード）

#### Academic Paper Reviewer（6 モード）
- calibration モード

#### Academic Pipeline（オーケストレーター）

### Deep Research（v2.8）
### Academic Paper（v3.0）
### Academic Paper Reviewer（v1.8）
### Academic Pipeline（v3.7）

### サポートされる出力フォーマット

- DOCX（利用可能な場合 Pandoc 経由）

## Changelog

### v{ver} (2026-05-19) — latest entry
### v3.9.4.1 (2026-05-19) — previous hotfix
### v3.9.4 (2026-05-18) — temporal verification
### v3.9.1 (2026-05-18) — client hardening
### v3.9.0 (2026-05-17) — triangulation
### v3.8.0 (2026-05-16) — L3 audit
### v3.7.0 (2026-05-05) — plugin packaging
### v3.6.8 (2026-05-03) — generator-evaluator
### v3.6.7 (2026-04-30) — pattern protection
### v3.6.5 (2026-04-27) — corpus consumer
### v3.6.4 (2026-04-25) — corpus input port
### v3.6.3 (2026-04-23) — passport reset
### v3.6.2 (2026-04-23) — reviewer sprint
### v3.5.1 (2026-04-22) — reading-check probe
### v3.5.0 (2026-04-21) — collaboration depth
### v3.4.0 (2026-04-20) — compliance agent
### v3.3.6 (2026-04-15) — README streamlining
### v3.3.5 (2026-04-15)
### v3.3.4 (2026-04-15) — changelog sync
### v3.3.3 (2026-04-15) — release prep
### v3.3.2 (2026-04-15) — data access levels

## Version Info
- **Suite version**: {ver}
"""


def _write_ja_readme(root: Path, version: str) -> None:
    (root / "README.ja-JP.md").write_text(
        JA_README_TEMPLATE.format(ver=version), encoding="utf-8"
    )


class TestReadmeJaSections(unittest.TestCase):
    def setUp(self) -> None:
        # check_spec_consistency uses module-level ROOT and ERRORS. Reset and
        # restore around each test so state does not leak between cases.
        self._orig_root = csc.ROOT
        self._orig_errors = list(csc.ERRORS)
        csc.ERRORS.clear()

    def tearDown(self) -> None:
        csc.ROOT = self._orig_root
        csc.ERRORS.clear()
        csc.ERRORS.extend(self._orig_errors)

    def test_aligned_ja_readme_passes(self) -> None:
        """A README.ja-JP.md whose badge / tag link / release headings all
        agree with the suite version v3.9.4.2 must pass without errors."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            csc.ROOT = root
            _write_ja_readme(root, version="3.9.4.2")

            csc.check_readme_ja_sections()

            self.assertEqual(
                csc.ERRORS, [],
                msg=f"unexpected errors on aligned fixture: {csc.ERRORS!r}",
            )

    def test_stale_ja_badge_fails(self) -> None:
        """Regression for #170: if README.ja-JP.md keeps a stale v3.9.4.0
        badge while CHANGELOG has moved to v3.9.4.2, the lint must surface
        the drift instead of silently passing (pre-fix behavior: this file
        was outside the lint's needle list and the drift never surfaced)."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            csc.ROOT = root
            # Write the "current" v3.9.4.2 release block but downgrade only
            # the badge and tag link to v3.9.4.0. This is the realistic shape
            # of drift when one place gets forgotten during a release.
            stale = JA_README_TEMPLATE.format(ver="3.9.4.2").replace(
                "version-v3.9.4.2-blue", "version-v3.9.4.0-blue"
            ).replace(
                "releases/tag/v3.9.4.2", "releases/tag/v3.9.4.0"
            )
            (root / "README.ja-JP.md").write_text(stale, encoding="utf-8")

            csc.check_readme_ja_sections()

            self.assertTrue(
                any("README.ja-JP.md" in e and "v3.9.4.2" in e for e in csc.ERRORS),
                msg=f"expected ja-JP drift error in: {csc.ERRORS!r}",
            )


if __name__ == "__main__":
    unittest.main()
