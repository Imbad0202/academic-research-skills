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


class TestRelativeMarkdownLinkGrammar(unittest.TestCase):
    """#794: rendered-link grammar, with the old lint scope retained."""

    def setUp(self) -> None:
        self._old_root = csc.ROOT
        csc.ERRORS.clear()
        self._tmp = TemporaryDirectory()
        csc.ROOT = Path(self._tmp.name)
        (csc.ROOT / "docs").mkdir()

    def tearDown(self) -> None:
        csc.ROOT = self._old_root
        csc.ERRORS.clear()
        self._tmp.cleanup()

    def _check(self, text: str) -> list[str]:
        (csc.ROOT / "docs/PAGE.md").write_text(text, encoding="utf-8")
        csc.check_relative_markdown_links("docs/PAGE.md")
        return list(csc.ERRORS)

    def test_rendered_dead_link_still_fires(self) -> None:
        errors = self._check("[dead](MISSING.md)\n")
        self.assertTrue(any("MISSING.md" in error for error in errors))

    def test_non_rendering_and_image_targets_do_not_fire(self) -> None:
        errors = self._check(
            "![image](missing-image.png)\n"
            "`[example](missing-inline.md)`\n"
            "<!-- [commented](missing-comment.md) -->\n"
            "```markdown\n[fenced](missing-fenced.md)\n```\n"
        )
        self.assertEqual(errors, [])

    def test_titled_link_checks_only_its_destination(self) -> None:
        errors = self._check('[dead](MISSING.md "optional title")\n')
        self.assertEqual(
            errors,
            ["docs/PAGE.md: broken relative markdown link 'MISSING.md'"],
        )

    def test_existing_file_with_unknown_fragment_remains_out_of_scope(self) -> None:
        (csc.ROOT / "docs/TARGET.md").write_text("# Real Heading\n", encoding="utf-8")
        errors = self._check("[pointer](TARGET.md#not-a-real-heading)\n")
        self.assertEqual(errors, [])


# The README fixtures follow the lint's own version pins, so a version bump
# edits only check_spec_consistency.py. The suite version and the three kept
# changelog headings come from README_CHANGELOG_KEEP, whose first entry is the
# current release. The sub-skill versions come from the zh-TW heading list;
# the ja and ko checkers pin the same versions inline. The fixtures spell the
# heading formats themselves, so the tests share the lint's data but not its
# formatting. The text after each changelog heading's dash is free: the lint
# matches the `### vX.Y.Z (YYYY-MM-DD)` prefix.
CUR_VER, CUR_DATE = csc.README_CHANGELOG_KEEP[0]
CUR_HEADING = f"### v{CUR_VER} ({CUR_DATE})"
CUR_HEADING_FULLWIDTH = f"### v{CUR_VER}（{CUR_DATE}）"
ASCII_KEPT = "".join(
    f"### v{ver} ({date}) — kept release\n" for ver, date in csc.README_CHANGELOG_KEEP
)
FULLWIDTH_KEPT = "".join(
    f"### v{ver}（{date}） — kept release\n" for ver, date in csc.README_CHANGELOG_KEEP
)


def _pinned_skill_version(name: str) -> str:
    prefix = f"### {name} (v"
    (heading,) = (h for h in csc.ZH_README_CONFIGS[0]["headings"] if h.startswith(prefix))
    return heading[len(prefix):-1]


DR_VER = _pinned_skill_version("Deep Research")
AP_VER = _pinned_skill_version("Academic Paper")
APR_VER = _pinned_skill_version("Academic Paper Reviewer")


# Minimal ja-JP README capturing the version-bearing surfaces the lint needs
# to police: badge, release tag link, the CHANGELOG/archive links plus the three
# kept release blocks (README_CHANGELOG_KEEP),
# four localized mode headings, four skill-detail headings, and the DOCX line.
JA_README = f"""\
# Academic Research Skills

[![Version](https://img.shields.io/badge/version-v{CUR_VER}-blue)](https://github.com/Imbad0202/academic-research-skills/releases/tag/v{CUR_VER})

## クイックスタート

#### Deep Research（8 モード）
- outline-only モード
- abstract-only モード
- disclosure モード
- review モード

#### Academic Paper（11 モード）

#### Academic Paper Reviewer（6 モード）
- calibration モード

#### Academic Pipeline（オーケストレーター）

### Deep Research（v{DR_VER}）
### Academic Paper（v{AP_VER}）
### Academic Paper Reviewer（v{APR_VER}）
### Academic Pipeline（v{CUR_VER}）

### サポートされる出力フォーマット

- DOCX（利用可能な場合 Pandoc 経由）

## Changelog

[CHANGELOG.md](CHANGELOG.md) · [docs/changelog-archive/ja-JP.md](docs/changelog-archive/ja-JP.md)

{ASCII_KEPT}
## Version Info
- **Suite version**: {CUR_VER}
"""


def _write_changelog_targets(root: Path, locale: str) -> None:
    """The README changelog section links to CHANGELOG.md and the frozen
    locale archive; check_relative_markdown_links needs both to exist."""
    (root / "CHANGELOG.md").write_text("# Changelog\n", encoding="utf-8")
    archive = root / "docs" / "changelog-archive" / f"{locale}.md"
    archive.parent.mkdir(parents=True, exist_ok=True)
    archive.write_text("# frozen\n", encoding="utf-8")


def _write_ja_readme(root: Path) -> None:
    _write_changelog_targets(root, "ja-JP")
    (root / "README.ja-JP.md").write_text(JA_README, encoding="utf-8")


# Minimal ko-KR README capturing the version-bearing surfaces check_readme_ko_sections
# polices: badge, release tag link, the same release-block list as the other locales,
# four localized mode headings ("N개 모드" with ASCII parens — Korean typographic norm
# matching English/ja, NOT the full-width zh form), four skill-detail headings (English
# ASCII-paren form reused verbatim), and the Korean DOCX line.
KO_README = f"""\
# Academic Research Skills

[![Version](https://img.shields.io/badge/version-v{CUR_VER}-blue)](https://github.com/Imbad0202/academic-research-skills/releases/tag/v{CUR_VER})

## 빠른 시작

#### Deep Research (8개 모드)
- outline-only 모드
- abstract-only 모드
- disclosure 모드
- review 모드

#### Academic Paper (11개 모드)

#### Academic Paper Reviewer (6개 모드)
- calibration 모드

#### Academic Pipeline (오케스트레이터)

### Deep Research (v{DR_VER})
### Academic Paper (v{AP_VER})
### Academic Paper Reviewer (v{APR_VER})
### Academic Pipeline (v{CUR_VER})

### 지원되는 출력 형식

- DOCX (가능한 경우 Pandoc 경유)

## 변경 이력

[CHANGELOG.md](CHANGELOG.md) · [docs/changelog-archive/ko-KR.md](docs/changelog-archive/ko-KR.md)

{ASCII_KEPT}"""


def _write_ko_readme(root: Path) -> None:
    _write_changelog_targets(root, "ko-KR")
    (root / "README.ko-KR.md").write_text(KO_README, encoding="utf-8")


# Minimal zh-CN README capturing the version-bearing surfaces the lint needs
# to police via ZH_README_CONFIGS[1]: badge, release tag link, the same
# release-block list as zh-TW, four Simplified-Chinese localized mode
# headings, four skill-detail headings, and the Simplified-Chinese DOCX line.
ZH_CN_README = f"""\
# Academic Research Skills

[![Version](https://img.shields.io/badge/version-v{CUR_VER}-blue)](https://github.com/Imbad0202/academic-research-skills/releases/tag/v{CUR_VER})

#### Deep Research（深度研究，8 种模式）
- review mode

#### Academic Paper（学术论文撰写，11 种模式）
- outline-only mode
- abstract-only mode
- disclosure mode

#### Academic Paper Reviewer（论文审查，6 种模式）
- calibration mode

#### Academic Pipeline（全流程调度器）

### Deep Research (v{DR_VER})
### Academic Paper (v{AP_VER})
### Academic Paper Reviewer (v{APR_VER})
### Academic Pipeline (v{CUR_VER})

### 支持的输出格式

- DOCX（Pandoc 可用时）

## 更新纪录

[CHANGELOG.md](CHANGELOG.md) · [docs/changelog-archive/zh-CN.md](docs/changelog-archive/zh-CN.md)

{FULLWIDTH_KEPT}"""


def _write_zh_cn_readme(root: Path) -> None:
    _write_changelog_targets(root, "zh-CN")
    (root / "README.zh-CN.md").write_text(ZH_CN_README, encoding="utf-8")


# zh-TW fixture matching ZH_README_CONFIGS[0]. check_readme_zh_sections
# iterates BOTH configs, so to test the zh-CN branch in isolation we still
# need a passing zh-TW companion (or vice versa). The minimal zh-TW fixture
# below uses the same shape with Traditional-Chinese localized strings.
ZH_TW_README = f"""\
# Academic Research Skills

[![Version](https://img.shields.io/badge/version-v{CUR_VER}-blue)](https://github.com/Imbad0202/academic-research-skills/releases/tag/v{CUR_VER})

#### Deep Research（深度研究，8 種模式）
- review mode

#### Academic Paper（學術論文撰寫，11 種模式）
- outline-only mode
- abstract-only mode
- disclosure mode

#### Academic Paper Reviewer（論文審查，6 種模式）
- calibration mode

#### Academic Pipeline（全流程調度器）

### Deep Research (v{DR_VER})
### Academic Paper (v{AP_VER})
### Academic Paper Reviewer (v{APR_VER})
### Academic Pipeline (v{CUR_VER})

### 支援的輸出格式

- DOCX（Pandoc 可用時）

## 更新紀錄

[CHANGELOG.md](CHANGELOG.md) · [docs/changelog-archive/zh-TW.md](docs/changelog-archive/zh-TW.md)

{FULLWIDTH_KEPT}"""


def _write_zh_tw_readme(root: Path) -> None:
    _write_changelog_targets(root, "zh-TW")
    (root / "README.zh-TW.md").write_text(ZH_TW_README, encoding="utf-8")


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
        agree with the current suite version must pass without errors."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            csc.ROOT = root
            _write_ja_readme(root)

            csc.check_readme_ja_sections()

            self.assertEqual(
                csc.ERRORS, [],
                msg=f"unexpected errors on aligned fixture: {csc.ERRORS!r}",
            )

    def test_stale_ja_badge_fails(self) -> None:
        """Regression for #170: if README.ja-JP.md keeps a stale v3.9.4.0
        badge while CHANGELOG has moved to the current release, the lint must surface
        the drift instead of silently passing (pre-fix behavior: this file
        was outside the lint's needle list and the drift never surfaced)."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            csc.ROOT = root
            # Write the current release block but downgrade only
            # the badge and tag link to v3.9.4.0. This is the realistic shape
            # of drift when one place gets forgotten during a release.
            stale = JA_README.replace(
                f"version-v{CUR_VER}-blue", "version-v3.9.4.0-blue"
            ).replace(
                f"releases/tag/v{CUR_VER}", "releases/tag/v3.9.4.0"
            )
            (root / "README.ja-JP.md").write_text(stale, encoding="utf-8")

            csc.check_readme_ja_sections()

            self.assertTrue(
                any("README.ja-JP.md" in e and f"v{CUR_VER}" in e for e in csc.ERRORS),
                msg=f"expected ja-JP drift error in: {csc.ERRORS!r}",
            )


class TestReadmeKoSections(unittest.TestCase):
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

    def test_aligned_ko_readme_passes(self) -> None:
        """A README.ko-KR.md whose badge / tag link / release headings / Korean
        mode + skill headings all agree with the suite version must pass."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            csc.ROOT = root
            _write_ko_readme(root)

            csc.check_readme_ko_sections()

            self.assertEqual(
                csc.ERRORS, [],
                msg=f"unexpected errors on aligned ko fixture: {csc.ERRORS!r}",
            )

    def test_stale_ko_badge_fails(self) -> None:
        """Symmetric to the ja drift regression: a stale badge / tag link on
        README.ko-KR.md must surface the drift rather than silently passing."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            csc.ROOT = root
            stale = KO_README.replace(
                f"version-v{CUR_VER}-blue", "version-v3.9.4.0-blue"
            ).replace(
                f"releases/tag/v{CUR_VER}", "releases/tag/v3.9.4.0"
            )
            (root / "README.ko-KR.md").write_text(stale, encoding="utf-8")

            csc.check_readme_ko_sections()

            self.assertTrue(
                any("README.ko-KR.md" in e and f"v{CUR_VER}" in e for e in csc.ERRORS),
                msg=f"expected ko-KR drift error in: {csc.ERRORS!r}",
            )

    def test_missing_korean_mode_heading_fails(self) -> None:
        """If a localized mode heading is dropped (e.g. the "N개 모드" form is
        accidentally written in the English "(8 modes)" shape), the lint must
        catch it — proving the heading checks are load-bearing, not vacuous."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            csc.ROOT = root
            broken = KO_README.replace(
                "#### Deep Research (8개 모드)", "#### Deep Research (8 modes)"
            )
            (root / "README.ko-KR.md").write_text(broken, encoding="utf-8")

            csc.check_readme_ko_sections()

            self.assertTrue(
                any("README.ko-KR.md" in e and "8개 모드" in e for e in csc.ERRORS),
                msg=f"expected missing-heading error in: {csc.ERRORS!r}",
            )

    def test_full_width_korean_changelog_parentheses_fail(self) -> None:
        """Korean changelog headings use ASCII parentheses, not full-width forms."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            csc.ROOT = root
            broken = KO_README.replace(
                CUR_HEADING,
                CUR_HEADING_FULLWIDTH,
            )
            (root / "README.ko-KR.md").write_text(broken, encoding="utf-8")

            csc.check_readme_ko_sections()

            self.assertTrue(
                any(
                    "README.ko-KR.md" in e
                    and CUR_HEADING in e
                    for e in csc.ERRORS
                ),
                msg=f"expected Korean parenthesis-style error in: {csc.ERRORS!r}",
            )


    def test_fourth_release_heading_fails(self) -> None:
        """The README keeps only README_CHANGELOG_KEEP; a fourth `### v`
        heading (the pre-2026-09-15 regrowth pattern) must fail."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            csc.ROOT = root
            _write_changelog_targets(root, "ko-KR")
            regrown = KO_README + (
                "### v3.20.1 (2026-08-15) — stale fourth entry\n"
            )
            (root / "README.ko-KR.md").write_text(regrown, encoding="utf-8")

            csc.check_readme_ko_sections()

            self.assertTrue(
                any(
                    "README.ko-KR.md" in e
                    and "only the 3 most recent" in e
                    and "v3.20.1" in e
                    for e in csc.ERRORS
                ),
                msg=f"expected extra-heading error in: {csc.ERRORS!r}",
            )

    def test_missing_archive_link_fails(self) -> None:
        """The translated README must point at its frozen archive."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            csc.ROOT = root
            _write_changelog_targets(root, "ko-KR")
            unlinked = KO_README.replace(
                " · [docs/changelog-archive/ko-KR.md](docs/changelog-archive/ko-KR.md)", ""
            )
            (root / "README.ko-KR.md").write_text(unlinked, encoding="utf-8")

            csc.check_readme_ko_sections()

            self.assertTrue(
                any(
                    "README.ko-KR.md" in e
                    and "must link to docs/changelog-archive/ko-KR.md" in e
                    for e in csc.ERRORS
                ),
                msg=f"expected missing-archive-link error in: {csc.ERRORS!r}",
            )


    def test_duplicate_kept_release_heading_fails(self) -> None:
        """Membership is not enough: a kept release repeated twice is still
        four headings (codex P2 on #870)."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            csc.ROOT = root
            _write_changelog_targets(root, "ko-KR")
            doubled = KO_README + (
                f"{CUR_HEADING} — pasted twice\n"
            )
            (root / "README.ko-KR.md").write_text(doubled, encoding="utf-8")

            csc.check_readme_ko_sections()

            self.assertTrue(
                any("README.ko-KR.md" in e and "repeats" in e for e in csc.ERRORS),
                msg=f"expected duplicate-heading error in: {csc.ERRORS!r}",
            )

    def test_fenced_changelog_section_does_not_count(self) -> None:
        """A changelog section inside a code fence does not render, so it must
        not satisfy the heading / link checks (codex P2 on #870)."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            csc.ROOT = root
            _write_changelog_targets(root, "ko-KR")
            base = KO_README
            head, _, section = base.partition("## 변경 이력\n")
            fenced = head + "```markdown\n## 변경 이력\n" + section + "```\n\n## 변경 이력\n\n"
            (root / "README.ko-KR.md").write_text(fenced, encoding="utf-8")

            csc.check_readme_ko_sections()

            self.assertTrue(
                any("README.ko-KR.md" in e and CUR_HEADING in e for e in csc.ERRORS),
                msg=f"expected missing-heading error for the fenced copy in: {csc.ERRORS!r}",
            )


class TestReadmeZhSections(unittest.TestCase):
    """Coverage for the ZH_README_CONFIGS tuple branch added when zh-CN
    joined zh-TW under check_readme_zh_sections. check_readme_zh_sections
    iterates both configs, so both fixtures must exist on every test path."""

    def setUp(self) -> None:
        self._orig_root = csc.ROOT
        self._orig_errors = list(csc.ERRORS)
        csc.ERRORS.clear()

    def tearDown(self) -> None:
        csc.ROOT = self._orig_root
        csc.ERRORS.clear()
        csc.ERRORS.extend(self._orig_errors)

    def test_aligned_zh_cn_readme_passes(self) -> None:
        """Both zh-TW and zh-CN fixtures aligned to the current release produce no
        lint errors. Locks the new ZH_README_CONFIGS[1] branch."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            csc.ROOT = root
            _write_zh_tw_readme(root)
            _write_zh_cn_readme(root)

            csc.check_readme_zh_sections()

            self.assertEqual(
                csc.ERRORS, [],
                msg=f"unexpected errors on aligned zh fixtures: {csc.ERRORS!r}",
            )

    def test_stale_zh_cn_badge_fails(self) -> None:
        """Regression symmetric with #170 ja-JP: if README.zh-CN.md keeps
        a stale v3.9.4.0 badge while the rest of the file moved to the current release,
        the lint must surface the drift on the zh-CN branch specifically."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            csc.ROOT = root
            _write_zh_tw_readme(root)
            stale = ZH_CN_README.replace(
                f"version-v{CUR_VER}-blue", "version-v3.9.4.0-blue"
            ).replace(
                f"releases/tag/v{CUR_VER}", "releases/tag/v3.9.4.0"
            )
            (root / "README.zh-CN.md").write_text(stale, encoding="utf-8")

            csc.check_readme_zh_sections()

            self.assertTrue(
                any("README.zh-CN.md" in e and f"v{CUR_VER}" in e for e in csc.ERRORS),
                msg=f"expected zh-CN drift error in: {csc.ERRORS!r}",
            )


# Minimal docs/ARCHITECTURE.md fixture carrying the THREE marker kinds the invariant-4 check (#345)
# must distinguish: current-component markers (mermaid node + component/stage rows, which MUST equal
# the suite version), a feature-history timeline marker (`vX.Y.Z : <feature>`, which must NOT be
# policed), and a prose mention of `academic-pipeline vX.Y.Z` (provenance narrative, which must also
# NOT be policed — it is excluded by the table-row anchor). `{comp}` = current-component version;
# `{hist}` = timeline version; `{prose}` = the version named in the narrative provenance line.
ARCHITECTURE_TEMPLATE = """\
# Architecture

```mermaid
flowchart TD
    Pipeline[academic-pipeline<br/>orchestrator<br/>v{comp}<br/>Agent Team: 5]
```

| Stage | Gate | ... |
|-------|------|-----|
| **2.5 INTEGRITY** | `academic-pipeline` v{comp} (gate) | VERIFIED_ONLY |
| **6. PROCESS SUMMARY** | `academic-pipeline` v{comp} | VERIFIED_ONLY |

| Component | Role |
|-----------|------|
| `academic-pipeline` v{comp} | orchestrator (delegates to sub-skill modes) |

The `academic-pipeline` v{prose} release first introduced the integrity gate (narrative provenance).

```mermaid
timeline
    title ARS evolution timeline
    v{hist} : deterministic citation verification gate (#182)
```
"""


def _write_architecture_fixture(
    root: Path, *, suite: str, comp: str, hist: str, prose: str | None = None
) -> None:
    """Write `.claude/CLAUDE.md` (suite version source) + a docs/ARCHITECTURE.md fixture.

    `prose` defaults to the suite version so the narrative line is innocuous unless a test
    deliberately sets it to a stale version to assert the prose mention is not policed.
    """
    (root / ".claude").mkdir(parents=True, exist_ok=True)
    (root / ".claude" / "CLAUDE.md").write_text(
        f"# ARS\n\n- **Suite version**: {suite} (per CHANGELOG.md)\n", encoding="utf-8"
    )
    (root / "docs").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "ARCHITECTURE.md").write_text(
        ARCHITECTURE_TEMPLATE.format(comp=comp, hist=hist, prose=prose or suite),
        encoding="utf-8",
    )


class TestArchitectureComponentVersion(unittest.TestCase):
    """#345: invariant-4 lint for docs/ARCHITECTURE.md current-component version markers."""

    def setUp(self) -> None:
        self._orig_root = csc.ROOT
        self._orig_errors = list(csc.ERRORS)
        csc.ERRORS.clear()

    def tearDown(self) -> None:
        csc.ROOT = self._orig_root
        csc.ERRORS.clear()
        csc.ERRORS.extend(self._orig_errors)

    def test_aligned_passes(self) -> None:
        """All component markers at the suite version → no errors (timeline at an older version
        is fine — it records history)."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            csc.ROOT = root
            _write_architecture_fixture(root, suite="3.11.1", comp="3.11.1", hist="3.11.0")

            csc.check_architecture_component_version()

            self.assertEqual(
                csc.ERRORS, [], msg=f"unexpected errors on aligned fixture: {csc.ERRORS!r}"
            )

    def test_stale_component_marker_fails(self) -> None:
        """A current-component marker left at the prior version (the exact #343/#344 drift) must
        fail — both the mermaid node and the rows carry the stale version here."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            csc.ROOT = root
            _write_architecture_fixture(root, suite="3.11.1", comp="3.11.0", hist="3.11.0")

            csc.check_architecture_component_version()

            self.assertTrue(
                any("ARCHITECTURE.md" in e and "3.11.0" in e and "3.11.1" in e for e in csc.ERRORS),
                msg=f"expected stale-component drift error in: {csc.ERRORS!r}",
            )

    def test_stale_timeline_marker_does_not_fail(self) -> None:
        """The critical distinction: a timeline `vX.Y.Z : <feature>` node at a DIFFERENT version
        from the suite must NOT fail — it records which version shipped a feature, and a
        naive `v3.x` scan would wrongly flag it. Component markers are aligned here."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            csc.ROOT = root
            # Component markers all at the suite version; only the timeline records an old version.
            _write_architecture_fixture(root, suite="3.11.1", comp="3.11.1", hist="3.9.4")

            csc.check_architecture_component_version()

            self.assertEqual(
                csc.ERRORS, [],
                msg=f"timeline marker must not be policed, but got: {csc.ERRORS!r}",
            )

    def test_missing_component_marker_fails(self) -> None:
        """If the component markers vanish entirely (e.g. a refactor removes them), the check must
        surface that rather than silently passing on an empty match."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            csc.ROOT = root
            (root / ".claude").mkdir(parents=True, exist_ok=True)
            (root / ".claude" / "CLAUDE.md").write_text(
                "- **Suite version**: 3.11.1 (per CHANGELOG.md)\n", encoding="utf-8"
            )
            (root / "docs").mkdir(parents=True, exist_ok=True)
            (root / "docs" / "ARCHITECTURE.md").write_text(
                "# Architecture\n\nNo component markers here.\n", encoding="utf-8"
            )

            csc.check_architecture_component_version()

            self.assertTrue(
                any("no mermaid" in e or "no `academic-pipeline" in e for e in csc.ERRORS),
                msg=f"expected missing-marker error in: {csc.ERRORS!r}",
            )

    def test_four_component_aligned_passes(self) -> None:
        """#352 P2: the repo's own grammar ships 4-component versions (v3.9.4.2). A suite and
        component markers both at a 4-component version must pass — the version regex must capture
        the FULL token, not truncate to three components."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            csc.ROOT = root
            _write_architecture_fixture(root, suite="3.9.4.2", comp="3.9.4.2", hist="3.9.4")

            csc.check_architecture_component_version()

            self.assertEqual(
                csc.ERRORS, [],
                msg=f"unexpected errors on aligned 4-component fixture: {csc.ERRORS!r}",
            )

    def test_four_component_marker_against_three_component_suite_fails(self) -> None:
        """#352 P2 (the silent-pass this fix closes): suite is the 3-component `3.9.4` but a
        component marker carries the 4-component `3.9.4.2`. A truncating `\\d+\\.\\d+\\.\\d+`
        would capture `3.9.4` from the marker and falsely pass (3.9.4 == 3.9.4). The full-token
        capture must instead see `3.9.4.2` and fail it against the suite."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            csc.ROOT = root
            _write_architecture_fixture(root, suite="3.9.4", comp="3.9.4.2", hist="3.9.4")

            csc.check_architecture_component_version()

            # The error must name the FULL 4-component marker as != the 3-component suite. Asserting
            # on `!= suite v3.9.4` (not just substring `3.9.4`, which is contained in `3.9.4.2`)
            # proves the captured marker was the full `3.9.4.2`, i.e. the truncation was closed.
            self.assertTrue(
                any("v3.9.4.2" in e and "!= suite v3.9.4 " in e for e in csc.ERRORS),
                msg=f"expected 4-vs-3-component drift error in: {csc.ERRORS!r}",
            )

    def test_prose_provenance_mention_does_not_fail(self) -> None:
        """#352 P3: a narrative line naming `academic-pipeline v<old>` (feature provenance) must
        NOT be policed against the suite version — only markdown table-row component cells are.
        Component markers + timeline are aligned/innocuous; only the prose line is stale."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            csc.ROOT = root
            _write_architecture_fixture(
                root, suite="3.11.1", comp="3.11.1", hist="3.9.4", prose="3.9.4"
            )

            csc.check_architecture_component_version()

            self.assertEqual(
                csc.ERRORS, [],
                msg=f"prose provenance mention must not be policed, but got: {csc.ERRORS!r}",
            )


# --- #377: SKILL.md frontmatter↔table consistency (all 4) + suite-skill date sanity ---

# Minimal SKILL.md carrying the version-bearing surfaces the #377 check polices: a
# `metadata:` frontmatter block with `version` / `last_updated`, and a Version-Info table
# with `| Skill Version |` / `| Last Updated |` rows. Mirrors the real four SKILL.md shape.
SKILL_TEMPLATE = """\
---
name: {name}
metadata:
  version: "{fm_ver}"
  last_updated: "{fm_date}"
---

# {name}

Body.

## Version Info

| Field | Value |
|-------|-------|
| Skill Version | {tbl_ver} |
| Last Updated | {tbl_date} |
"""

# The four SKILL.md paths the generalized check must cover, with their real independent
# versions/dates. `academic-pipeline` tracks the suite; the other three move independently.
_SKILL_FIXTURES = {
    "academic-pipeline": ("3.12.0", "2026-06-08"),
    "academic-paper": ("3.2.0", "2026-06-01"),
    "academic-paper-reviewer": ("1.10.0", "2026-06-01"),
    "deep-research": ("2.9.4", "2026-05-18"),
}


def _write_skill_fixtures(root: Path, overrides: dict | None = None) -> None:
    """Write all four SKILL.md with frontmatter == table by default. `overrides` maps a
    skill dir to a partial dict of {fm_ver, fm_date, tbl_ver, tbl_date} to introduce drift."""
    overrides = overrides or {}
    for skill, (ver, date) in _SKILL_FIXTURES.items():
        fields = {"fm_ver": ver, "fm_date": date, "tbl_ver": ver, "tbl_date": date}
        fields.update(overrides.get(skill, {}))
        (root / skill).mkdir(parents=True, exist_ok=True)
        (root / skill / "SKILL.md").write_text(
            SKILL_TEMPLATE.format(name=skill, **fields), encoding="utf-8"
        )


class TestSkillVersionTableConsistency(unittest.TestCase):
    """#377(a): frontmatter version/last_updated ↔ Version-Info table for ALL FOUR SKILL.md
    (pre-#377 only academic-paper-reviewer was checked)."""

    def setUp(self) -> None:
        self._orig_root = csc.ROOT
        self._orig_errors = list(csc.ERRORS)
        csc.ERRORS.clear()

    def tearDown(self) -> None:
        csc.ROOT = self._orig_root
        csc.ERRORS.clear()
        csc.ERRORS.extend(self._orig_errors)

    def test_skill_paths_follow_the_active_root(self) -> None:
        """#809: paths derive from ROOT at call time, so a fixture tree with a
        different skill set is policed on ITS skills, never the checkout's."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            csc.ROOT = root
            (root / "only-skill").mkdir()
            (root / "only-skill" / "SKILL.md").write_text("---\nname: only-skill\n---\n", encoding="utf-8")
            self.assertEqual(csc._skill_version_paths(), ("only-skill/SKILL.md",))
            csc.check_skill_version_blocks()
            self.assertTrue(all(e.startswith("only-skill/SKILL.md:") for e in csc.ERRORS), csc.ERRORS)

    def test_all_four_aligned_passes(self) -> None:
        """All four SKILL.md with frontmatter matching their table → no errors."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            csc.ROOT = root
            _write_skill_fixtures(root)

            csc.check_skill_version_blocks()

            self.assertEqual(
                csc.ERRORS, [], msg=f"unexpected errors on aligned fixtures: {csc.ERRORS!r}"
            )

    def test_table_date_drift_in_non_reviewer_skill_fails(self) -> None:
        """The exact #377 root cause: a SKILL whose frontmatter date is bumped but whose table
        date is left stale must fail — and crucially for a skill OTHER than reviewer (which is
        the only one the pre-#377 check covered)."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            csc.ROOT = root
            _write_skill_fixtures(
                root, overrides={"academic-pipeline": {"tbl_date": "2026-06-01"}}
            )

            csc.check_skill_version_blocks()

            self.assertTrue(
                any(
                    "academic-pipeline/SKILL.md" in e and "2026-06-08" in e and "2026-06-01" in e
                    for e in csc.ERRORS
                ),
                msg=f"expected frontmatter↔table date drift error in: {csc.ERRORS!r}",
            )

    def test_table_version_drift_fails(self) -> None:
        """A version (not date) drift between frontmatter and table also fails — for a third
        skill (deep-research) to prove the check is not reviewer-specific."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            csc.ROOT = root
            _write_skill_fixtures(
                root, overrides={"deep-research": {"tbl_ver": "2.9.3"}}
            )

            csc.check_skill_version_blocks()

            self.assertTrue(
                any(
                    "deep-research/SKILL.md" in e and "2.9.4" in e and "2.9.3" in e
                    for e in csc.ERRORS
                ),
                msg=f"expected frontmatter↔table version drift error in: {csc.ERRORS!r}",
            )

    def test_missing_table_rows_fails(self) -> None:
        """A SKILL.md that loses its Version-Info table rows must surface rather than silently
        pass on an empty match."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            csc.ROOT = root
            _write_skill_fixtures(root)
            (root / "academic-paper" / "SKILL.md").write_text(
                '---\nname: academic-paper\nmetadata:\n  version: "3.2.0"\n'
                '  last_updated: "2026-06-01"\n---\n\nNo version table here.\n',
                encoding="utf-8",
            )

            csc.check_skill_version_blocks()

            self.assertTrue(
                any("academic-paper/SKILL.md" in e and "Version Info" in e for e in csc.ERRORS),
                msg=f"expected missing-table-rows error in: {csc.ERRORS!r}",
            )


# Minimal CHANGELOG whose latest entry date is the parameter; the suite-date-sanity check
# compares academic-pipeline/SKILL.md last_updated against this. Two prior entries so the
# "latest" selection (first `## [X.Y.Z]` after [Unreleased]) is exercised, not just sole-entry.
CHANGELOG_TEMPLATE = """\
# Changelog

## [Unreleased]

## [{latest_ver}] - {latest_date} — latest real entry

## [3.11.1] - 2026-06-06 — prior patch

## [3.11.0] - 2026-06-04 — prior minor
"""


def _write_date_sanity_fixtures(
    root: Path, *, changelog_date: str, pipeline_date: str, changelog_ver: str = "3.12.0"
) -> None:
    """Write a CHANGELOG with a known latest-entry date + four SKILL.md where only
    academic-pipeline's last_updated is the variable under test."""
    (root / "CHANGELOG.md").write_text(
        CHANGELOG_TEMPLATE.format(latest_ver=changelog_ver, latest_date=changelog_date),
        encoding="utf-8",
    )
    _write_skill_fixtures(
        root,
        overrides={
            "academic-pipeline": {"fm_date": pipeline_date, "tbl_date": pipeline_date}
        },
    )


class TestSuiteSkillDateSanity(unittest.TestCase):
    """#377(b): academic-pipeline/SKILL.md last_updated must be >= the latest CHANGELOG entry
    date. The other three SKILL.md version independently and are NOT date-policed here."""

    def setUp(self) -> None:
        self._orig_root = csc.ROOT
        self._orig_errors = list(csc.ERRORS)
        csc.ERRORS.clear()

    def tearDown(self) -> None:
        csc.ROOT = self._orig_root
        csc.ERRORS.clear()
        csc.ERRORS.extend(self._orig_errors)

    def test_pipeline_date_equal_to_changelog_passes(self) -> None:
        """last_updated == latest CHANGELOG date → fine (the normal aligned-release case)."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            csc.ROOT = root
            _write_date_sanity_fixtures(
                root, changelog_date="2026-06-08", pipeline_date="2026-06-08"
            )

            csc.check_suite_skill_date_sanity()

            self.assertEqual(
                csc.ERRORS, [], msg=f"unexpected errors on aligned date: {csc.ERRORS!r}"
            )

    def test_pipeline_date_after_changelog_passes(self) -> None:
        """last_updated strictly AFTER the latest CHANGELOG date is allowed — a post-release
        doc touch legitimately advances the date past the release entry."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            csc.ROOT = root
            _write_date_sanity_fixtures(
                root, changelog_date="2026-06-08", pipeline_date="2026-06-10"
            )

            csc.check_suite_skill_date_sanity()

            self.assertEqual(
                csc.ERRORS, [], msg=f"a later last_updated must pass, got: {csc.ERRORS!r}"
            )

    def test_pipeline_date_before_changelog_fails(self) -> None:
        """The exact v3.12.0 drift: suite version bumped, last_updated left at the prior release
        date (earlier than the latest CHANGELOG entry) → must fail."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            csc.ROOT = root
            _write_date_sanity_fixtures(
                root, changelog_date="2026-06-08", pipeline_date="2026-06-01"
            )

            csc.check_suite_skill_date_sanity()

            self.assertTrue(
                any(
                    "academic-pipeline/SKILL.md" in e
                    and "2026-06-01" in e
                    and "2026-06-08" in e
                    for e in csc.ERRORS
                ),
                msg=f"expected stale-suite-date error in: {csc.ERRORS!r}",
            )

    def test_date_check_is_bound_to_suite_path_only(self) -> None:
        """Out-of-scope guard (#377): the date check polices ONLY `_SUITE_SKILL_PATH`. To prove
        this is genuine scoping and not a vacuous pass, the test demonstrates that the SAME early
        date is ignored when carried by an independent skill but flagged when carried by whatever
        path `_SUITE_SKILL_PATH` names — i.e. repointing the constant repoints the policing.

        Fixture: pipeline date is current (2026-06-08, == CHANGELOG); academic-paper carries an
        early date (2026-06-01 < CHANGELOG). With the real constant the early academic-paper date
        is NOT flagged; after repointing the constant AT academic-paper, that exact same early
        date IS flagged. If the check ever fanned out across all four skills, the first assertion
        would already fail."""
        orig_suite_path = csc._SUITE_SKILL_PATH
        try:
            with TemporaryDirectory() as tmp:
                root = Path(tmp)
                csc.ROOT = root
                _write_date_sanity_fixtures(
                    root, changelog_date="2026-06-08", pipeline_date="2026-06-08"
                )
                # academic-paper keeps its default early date (2026-06-01) from _write_skill_fixtures.

                # Real constant → only pipeline policed; academic-paper's early date is ignored.
                csc.check_suite_skill_date_sanity()
                self.assertEqual(
                    csc.ERRORS, [],
                    msg=f"independent-skill early date must not be policed, got: {csc.ERRORS!r}",
                )

                # Repoint the constant at academic-paper → its early date is now the policed one.
                csc.ERRORS.clear()
                csc._SUITE_SKILL_PATH = "academic-paper/SKILL.md"
                csc.check_suite_skill_date_sanity()
                self.assertTrue(
                    any(
                        "academic-paper/SKILL.md" in e and "2026-06-01" in e and "2026-06-08" in e
                        for e in csc.ERRORS
                    ),
                    msg=f"repointed suite path must police academic-paper's early date: {csc.ERRORS!r}",
                )
        finally:
            csc._SUITE_SKILL_PATH = orig_suite_path

    def test_malformed_suite_skill_does_not_double_report(self) -> None:
        """When the suite SKILL.md is unparseable, check_skill_version_blocks() already records the
        error; check_suite_skill_date_sanity() must NOT re-report the same root cause from its own
        re-parse. Drives both checks in order (as main() does) and asserts a single pipeline error."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            csc.ROOT = root
            _write_date_sanity_fixtures(
                root, changelog_date="2026-06-08", pipeline_date="2026-06-08"
            )
            # Strip the suite SKILL's Version-Info table rows so it fails to parse.
            pipeline_skill = root / "academic-pipeline" / "SKILL.md"
            text = pipeline_skill.read_text(encoding="utf-8")
            pipeline_skill.write_text(
                text.replace("| Skill Version | 3.12.0 |", "").replace(
                    "| Last Updated | 2026-06-08 |", ""
                ),
                encoding="utf-8",
            )

            csc.check_skill_version_blocks()
            csc.check_suite_skill_date_sanity()

            pipeline_errors = [e for e in csc.ERRORS if "academic-pipeline/SKILL.md" in e]
            self.assertEqual(
                len(pipeline_errors), 1,
                msg=f"expected exactly one pipeline error, got {len(pipeline_errors)}: {pipeline_errors!r}",
            )


class RebuttalAuditGuardTest(unittest.TestCase):
    """check_rebuttal_audit_guard() must enforce the integrity-boundary language
    in the academic-paper Rebuttal-Audit Mode section. Mutation tests prove the
    guard actually fails when the suppression language is dropped — otherwise the
    check would be a vacuous pass that lets the false-certification risk back in."""

    _GOOD = (
        "## Rebuttal-Audit Mode\n\n"
        "Advisory QA of an existing rebuttal draft.\n\n"
        "**IRON RULE:** standalone, so it MUST NOT emit a Schema 11 ledger, "
        "MUST NOT write the Material Passport, and MUST NOT mark ready_to_submit.\n\n"
        "## Next Section\n"
    )

    def _run_guard_with(self, skill_text: str) -> list:
        orig_read = csc.read
        csc.ERRORS.clear()
        try:
            csc.read = lambda rel: skill_text if rel == "academic-paper/SKILL.md" else orig_read(rel)
            csc.check_rebuttal_audit_guard()
            return list(csc.ERRORS)
        finally:
            csc.read = orig_read
            csc.ERRORS.clear()

    def test_guard_passes_with_full_suppression_language(self) -> None:
        self.assertEqual(self._run_guard_with(self._GOOD), [])

    def test_guard_fails_when_section_missing(self) -> None:
        errs = self._run_guard_with("## Some Other Mode\n\nno rebuttal section here\n")
        self.assertTrue(any("missing" in e and "Rebuttal-Audit" in e for e in errs), errs)

    def test_guard_fails_when_schema11_suppression_dropped(self) -> None:
        mutated = self._GOOD.replace("Schema 11", "the tracker")
        errs = self._run_guard_with(mutated)
        self.assertTrue(any("Schema 11" in e for e in errs), errs)

    def test_guard_fails_when_must_not_dropped(self) -> None:
        mutated = self._GOOD.replace("MUST NOT", "should avoid")
        errs = self._run_guard_with(mutated)
        self.assertTrue(any("MUST NOT" in e for e in errs), errs)


class OutputLanguagePairContractTest(unittest.TestCase):
    """#862 Phase 1: check_output_language_pair_contract() must fail visibly.

    The four deterministic cases (covered / omitted / unsupported / malformed) are
    exercised against a minimal contract + Schema-4 + template triple, so a mutation
    proves the parity check fires instead of passing vacuously.
    """

    _CONTRACT = """\
# Output Language Pair

## Registry

<!-- output-language-pair-registry:start -->
| Token | L1 language | L1 script | L2 language | L2 script | Status |
|-------|-------------|-----------|-------------|-----------|--------|
| `zh-tw-en` | Traditional Chinese (`zh-TW`) | CJK | English (`en`) | Latin | default |
<!-- output-language-pair-registry:end -->

## Field semantics

### Conflicting declarations fail visibly

A handoff whose sites disagree stops and names both values; no site wins silently.

## Abstract length and keyword regime

The regime table lives in
[`abstract_writing_guide.md`](../academic-paper/references/abstract_writing_guide.md);
this contract points at it and does not restate its figures.
"""

    _SCHEMA = """\
# Handoff Schemas

## Schema 4: Paper Draft

| Field | Type | Description |
|-------|------|-------------|
| `abstract` | object | `{english: string, chinese: string}` (chinese is required only if bilingual) |
| `keywords` | object | `{en: list[string], zh_tw: list[string]}` bilingual keywords; counts per [`abstract_writing_guide.md`](abstract_writing_guide.md); token per [`shared/output_language_pair.md`](output_language_pair.md) |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `output_language_pair` | string | Opaque registry token, initially `zh-tw-en`; absent = legacy. Registry: [`shared/output_language_pair.md`](output_language_pair.md). |

## Schema 5: Something Else

An unrelated marker, with an up-to-date checklist line.
"""

    _TEMPLATE = (
        "# Bilingual Abstract Template\n\n"
        "## English Abstract\n\n"
        "## Chinese Abstract (zh-TW)\n\n"
        "The default entry is `zh-tw-en`.\n"
    )

    # The guide is the regime table's single home: the fixture carries the marked block and
    # a pointer back to the registry contract, so a mutation under test fires on the shape
    # being mutated rather than on a fixture that was never valid.
    _GUIDE = (
        "Regime rows for `zh-tw-en`; registry: "
        "[`shared/output_language_pair.md`](../shared/output_language_pair.md).\n\n"
        "<!-- abstract-regime-table:start -->\n"
        "| Paper type | L1 abstract (`zh-TW`, CJK) | L2 abstract (`en`) | Keywords per language |\n"
        "|------------|---------------------------|--------------------|-----------------------|\n"
        "| Standard | 300-500 characters | 150-250 words | 5-7 |\n"
        "| Conference | 300-800 characters | 200-500 words | 5-7 |\n"
        "| Extended abstract | not declared | 500-1,000 words | not declared |\n"
        "| Dissertation | 500-1,000 characters | up to 350 words | 5-7 |\n"
        "<!-- abstract-regime-table:end -->\n"
    )

    # R9: the scan covers eleven consumer surfaces. The synthetic tree carries all of
    # them so the fixture harness fails on the mutation under test, never on a missing
    # surface; `_SCHEMA` and `_TEMPLATE` above are two of the eleven.
    _OTHER_SURFACES = {
        "academic-paper/SKILL.md": "The bilingual abstract follows the `zh-tw-en` pair.\n",
        "academic-paper/agents/intake_agent.md": "Step 6 records the `zh-tw-en` pair.\n",
        "academic-paper/agents/abstract_bilingual_agent.md": "Labels are derived from `zh-tw-en`.\n",
        "academic-paper/agents/structure_architect_agent.md": "Allocations follow `zh-tw-en`.\n",
        "academic-paper/agents/draft_writer_agent.md": (
            "Serializes `output_language_pair` into Schema 4.\n"
        ),
        "academic-paper/references/abstract_writing_guide.md": _GUIDE,
        "academic-paper/references/workflow_phase_details.md": "Phase 5b uses `zh-tw-en`.\n",
        "academic-paper/references/mode_selection_guide.md": (
            "Bilingual = zh-TW + EN prose; no pair token here.\n"
        ),
        "commands/ars-abstract.md": "The command honours `zh-tw-en`.\n",
    }

    def setUp(self) -> None:
        self._old_root = csc.ROOT
        csc.ERRORS.clear()
        self._tmp = TemporaryDirectory()
        csc.ROOT = Path(self._tmp.name)
        (csc.ROOT / "shared").mkdir()
        (csc.ROOT / "academic-paper/templates").mkdir(parents=True)

    def tearDown(self) -> None:
        csc.ROOT = self._old_root
        csc.ERRORS.clear()
        self._tmp.cleanup()

    def _write(
        self,
        contract: str | None = None,
        schema: str | None = None,
        template: str | None = None,
        guide: str | None = None,
    ) -> None:
        (csc.ROOT / "shared/output_language_pair.md").write_text(
            self._CONTRACT if contract is None else contract, encoding="utf-8"
        )
        (csc.ROOT / "shared/handoff_schemas.md").write_text(
            self._SCHEMA if schema is None else schema, encoding="utf-8"
        )
        (csc.ROOT / "academic-paper/templates/bilingual_abstract_template.md").write_text(
            self._TEMPLATE if template is None else template, encoding="utf-8"
        )
        for rel_path, text in self._OTHER_SURFACES.items():
            if guide is not None and rel_path == csc.OUTPUT_LANGUAGE_PAIR_GUIDE:
                text = guide
            target = csc.ROOT / rel_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")

    def _errors(self, **overrides: str | None) -> list[str]:
        self._write(**overrides)
        csc.ERRORS.clear()
        csc.check_output_language_pair_contract()
        return list(csc.ERRORS)

    def test_default_state_passes(self) -> None:
        self.assertEqual(self._errors(), [])

    def test_pack_entry_absent_from_consumers_is_not_an_error(self) -> None:
        # A pack contributes registry entries as configuration; Schema-4 prose is not
        # expected to enumerate them, so only the default entry is a required carrier.
        contract = self._CONTRACT.replace(
            "| `zh-tw-en` | Traditional Chinese (`zh-TW`) | CJK | English (`en`) | Latin | default |",
            "| `zh-tw-en` | Traditional Chinese (`zh-TW`) | CJK | English (`en`) | Latin | default |\n"
            "| `es-en` | Spanish (`es`) | Latin | English (`en`) | Latin | pack |",
        )
        self.assertEqual(self._errors(contract=contract), [])

    def test_schema4_omitting_the_default_token_fails(self) -> None:
        schema = self._SCHEMA.replace("`zh-tw-en`", "the declared pair")
        errors = self._errors(schema=schema)
        self.assertTrue(
            any("does not reference the default registry entry" in e for e in errors), errors
        )

    def test_default_entry_must_match_the_legacy_pair(self) -> None:
        contract = self._CONTRACT.replace("`zh-tw-en`", "`en-zh-tw`")
        schema = self._SCHEMA.replace("`zh-tw-en`", "`en-zh-tw`")
        errors = self._errors(contract=contract, schema=schema)
        self.assertTrue(any("default registry entry must be exactly 'zh-tw-en'" in e for e in errors), errors)

    def test_consumer_advertising_an_unsupported_pair_fails(self) -> None:
        template = self._TEMPLATE + "\nThe run declares the `ja-en` pair.\n"
        errors = self._errors(template=template)
        self.assertTrue(any("absent from the registry" in e and "ja-en" in e for e in errors), errors)

    def test_bare_token_in_pair_context_is_not_collected(self) -> None:
        # P2-c: the backtick is the contract's own spelling rule, so it is the only spelling
        # the scan accepts. The bare-token branch could not tell an advertised pair from
        # ordinary hyphenated prose on any line that mentioned the field.
        template = self._TEMPLATE + "\nThe output_language_pair control accepts zh-tw-ja here.\n"
        self.assertEqual(self._errors(template=template), [])
        self.assertEqual(
            csc.advertised_output_language_pair_tokens(
                "The output_language_pair control accepts zh-tw-ja here."
            ),
            set(),
        )
        self.assertEqual(
            csc.advertised_output_language_pair_tokens("The pair is `zh-tw-en`."),
            {"zh-tw-en"},
        )

    def test_ordinary_hyphenated_prose_does_not_fire(self) -> None:
        self.assertEqual(self._errors(), [])
        self.assertEqual(csc.advertised_output_language_pair_tokens("an up-to-date marker"), set())

    def test_schema4_missing_contract_reference_fails(self) -> None:
        schema = self._SCHEMA.replace("[`shared/output_language_pair.md`](output_language_pair.md)", "the contract")
        errors = self._errors(schema=schema)
        self.assertTrue(any("must reference the output-language-pair contract" in e for e in errors), errors)

    def test_schema4_section_missing_fails(self) -> None:
        errors = self._errors(schema="# Handoff Schemas\n\n## Schema 5: Elsewhere\n")
        self.assertTrue(any("Schema 4 section" in e and "is missing" in e for e in errors), errors)

    def test_missing_contract_file_fails(self) -> None:
        self._write()
        (csc.ROOT / "shared/output_language_pair.md").unlink()
        csc.ERRORS.clear()
        csc.check_output_language_pair_contract()
        self.assertTrue(any("contract file is missing" in e for e in csc.ERRORS), list(csc.ERRORS))

    def test_missing_consumer_surface_fails(self) -> None:
        self._write()
        (csc.ROOT / "academic-paper/templates/bilingual_abstract_template.md").unlink()
        csc.ERRORS.clear()
        csc.check_output_language_pair_contract()
        self.assertTrue(any("consumer surface is missing" in e for e in csc.ERRORS), list(csc.ERRORS))

    def test_unparseable_registry_fails(self) -> None:
        errors = self._errors(contract="# Output Language Pair\n\nno registry block here\n")
        self.assertTrue(any("registry block markers are missing" in e for e in errors), errors)

    def test_unary_registry_entry_fails(self) -> None:
        contract = (
            "# Output Language Pair\n\n"
            "<!-- output-language-pair-registry:start -->\n"
            "| Token | L1 language | L1 script | Status |\n"
            "|-------|-------------|-----------|--------|\n"
            "| `zh-tw` | Traditional Chinese (`zh-TW`) | CJK | default |\n"
            "<!-- output-language-pair-registry:end -->\n"
        )
        errors = self._errors(contract=contract)
        self.assertTrue(any("single-language pairs are not supported" in e for e in errors), errors)

    def test_malformed_value_validation_is_not_vacuous(self) -> None:
        # (d): if the validator ever accepts a malformed value, the lint itself fails.
        original = csc.validate_output_language_pair
        csc.validate_output_language_pair = lambda value, registry: []
        try:
            errors = self._errors()
        finally:
            csc.validate_output_language_pair = original
        self.assertTrue(any("must be rejected" in e for e in errors), errors)

    def test_conflict_rule_pin_fires_when_its_literals_are_dropped(self) -> None:
        # R10: the conflict rule is prose-only, so it is pinned by literal presence.
        for literal in (
            "### Conflicting declarations fail visibly",
            "names both values",
        ):
            with self.subTest(literal=literal):
                errors = self._errors(contract=self._CONTRACT.replace(literal, "dropped"))
                self.assertTrue(
                    any("conflict-rule text" in e and literal in e for e in errors), errors
                )
    def test_regime_table_copied_into_the_contract_fails(self) -> None:
        # P1-1: one reconciled table, one home. A second copy in the contract is exactly
        # how the two figures drifted apart in the first place.
        table = (
            "<!-- abstract-regime-table:start -->\n"
            "| Paper type | L1 abstract | L2 abstract | Keywords per language |\n"
            "|------------|-------------|-------------|-----------------------|\n"
            "| Standard | 300-500 characters | 150-250 words | 5-7 |\n"
            "<!-- abstract-regime-table:end -->\n"
        )
        errors = self._errors(contract=self._CONTRACT + "\n" + table)
        self.assertTrue(any("must carry no competing copy" in e for e in errors), errors)

    def test_regime_table_unmarked_header_in_contract_fails(self) -> None:
        # An unmarked copy with the same four regime columns must fail, not only the marked block.
        table = (
            "\n| Paper type | L1 abstract | L2 abstract | Keywords per language |\n"
            "|------------|-------------|-------------|-----------------------|\n"
            "| Standard | 300-500 characters | 150-250 words | 5-7 |\n"
        )
        errors = self._errors(contract=self._CONTRACT + table)
        self.assertTrue(any("must carry no competing copy" in e for e in errors), errors)

    def test_contract_without_guide_pointer_fails(self) -> None:
        contract = self._CONTRACT.replace(
            "[`abstract_writing_guide.md`](../academic-paper/references/abstract_writing_guide.md)",
            "the guide",
        )
        errors = self._errors(contract=contract)
        self.assertTrue(any("must point at the regime table's home" in e for e in errors), errors)

    def test_guide_without_the_marked_table_fails(self) -> None:
        errors = self._errors(guide="Regime rows for `zh-tw-en`.\n")
        self.assertTrue(any("regime table markers are missing" in e for e in errors), errors)

    def test_guide_without_registry_reference_fails(self) -> None:
        guide = self._GUIDE.replace(
            "[`shared/output_language_pair.md`](../shared/output_language_pair.md)", "the registry"
        )
        errors = self._errors(guide=guide)
        self.assertTrue(any("must reference the registry contract" in e for e in errors), errors)

    def test_regime_table_missing_paper_type_row_fails(self) -> None:
        guide = self._GUIDE.replace(
            "| Dissertation | 500-1,000 characters | up to 350 words | 5-7 |\n", ""
        )
        errors = self._errors(guide=guide)
        self.assertTrue(any("missing the 'dissertation' row" in e for e in errors), errors)

    def test_regime_table_missing_required_column_fails(self) -> None:
        errors = self._errors(guide=self._GUIDE.replace("| Keywords per language |", "| Notes |"))
        self.assertTrue(any("keyword count" in e for e in errors), errors)

    def test_regime_row_without_an_l2_abstract_length_fails(self) -> None:
        errors = self._errors(guide=self._GUIDE.replace("| 150-250 words |", "|  |"))
        self.assertTrue(any("declares no L2 abstract length" in e for e in errors), errors)

    def test_duplicate_regime_row_fails(self) -> None:
        guide = self._GUIDE.replace(
            "| Conference | 300-800 characters | 200-500 words | 5-7 |",
            "| Standard | 300-500 characters | 150-250 words | 5-7 |",
        )
        errors = self._errors(guide=guide)
        self.assertTrue(any("duplicate regime row" in e for e in errors), errors)

class OutputLanguagePairLiteralPinTest(unittest.TestCase):
    """#862 Phase 1 (R8): the legacy literals are pinned where they are operative.

    `OutputLanguagePairContractTest` rewrites `csc.ROOT`, so its synthetic tree cannot
    prove that the shipped surfaces still carry the literals Phase 1 holds fixed. These
    tests copy the real files into a temp tree, mutate one operative location, and require
    the pin to fire — the mutation is the only difference from the shipped bytes.

    The pins target heading lines and typed Schema-4 rows rather than "the literal appears
    somewhere in the file": a rename of the operative line has to fail even when a prose
    sentence still quotes the old string, and the Schema-4 `output_language_pair` row does
    quote `abstract: {english, chinese}`.
    """

    def setUp(self) -> None:
        csc.ERRORS.clear()
        self._tmp = TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self) -> None:
        csc.ERRORS.clear()
        self._tmp.cleanup()

    def _copy_real(self, rel_path: str) -> str:
        text = (csc.OUTPUT_LANGUAGE_PAIR_LITERAL_ROOT / rel_path).read_text(encoding="utf-8")
        target = self.root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
        return text

    def _copied_pin_tree(self) -> None:
        for rel_path, _ in csc.LEGACY_PAIR_HEADING_BLOCKS:
            self._copy_real(rel_path)
        for rel_path, _ in csc.LEGACY_PAIR_QUOTED_LITERALS:
            self._copy_real(rel_path)
        for rel_path, *_rest in csc.PAIR_CARRIER_STEPS:
            self._copy_real(rel_path)
        self._copy_real(csc.OUTPUT_LANGUAGE_PAIR_SCHEMA_SURFACE)
        self._copy_real(csc.OUTPUT_LANGUAGE_PAIR_GUIDE)

    def _mutated_errors(self, rel_path: str, old: str, new: str = "") -> list[str]:
        self._copied_pin_tree()
        return self._mutate_and_run(rel_path, old, new, csc.check_output_language_pair_literal_pins)

    def _mutated_heading_errors(self, rel_path: str, heading: str, new_heading: str = "") -> list[str]:
        self._copied_pin_tree()
        path = self.root / rel_path
        lines = path.read_text(encoding="utf-8").splitlines()
        found = False
        new_lines: list[str] = []
        for line in lines:
            if line.rstrip() == heading.rstrip():
                found = True
                new_lines.append(new_heading)
            else:
                new_lines.append(line)
        self.assertTrue(found, f"the shipped file must still carry the heading {heading!r}")
        path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        csc.ERRORS.clear()
        csc.check_output_language_pair_literal_pins(self.root)
        return list(csc.ERRORS)

    def _mutate_and_run(self, rel_path: str, old: str, new: str, checker) -> list[str]:
        path = self.root / rel_path
        text = path.read_text(encoding="utf-8")
        self.assertIn(old, text, "the shipped file must still carry the pinned literal")
        path.write_text(text.replace(old, new), encoding="utf-8")
        csc.ERRORS.clear()
        checker(self.root)
        return list(csc.ERRORS)

    def test_real_tree_pins_hold(self) -> None:
        csc.ERRORS.clear()
        csc.check_output_language_pair_literal_pins()
        csc.check_output_language_pair_carrier_steps()
        csc.check_abstract_regime_table(csc.OUTPUT_LANGUAGE_PAIR_LITERAL_ROOT)
        self.assertEqual(list(csc.ERRORS), [])

    def test_abstract_agent_l2_heading_pin_fires(self) -> None:
        errors = self._mutated_heading_errors(
            "academic-paper/agents/abstract_bilingual_agent.md", "### English Abstract"
        )
        self.assertTrue(any("### English Abstract" in e for e in errors), errors)

    def test_abstract_agent_l1_heading_pin_fires(self) -> None:
        errors = self._mutated_heading_errors(
            "academic-paper/agents/abstract_bilingual_agent.md", "### Chinese Abstract"
        )
        self.assertTrue(any("### Chinese Abstract" in e for e in errors), errors)

    def test_template_l2_heading_pin_fires(self) -> None:
        errors = self._mutated_heading_errors(
            "academic-paper/templates/bilingual_abstract_template.md", "## English Abstract"
        )
        self.assertTrue(any("## English Abstract" in e for e in errors), errors)

    def test_template_l1_heading_pin_fires(self) -> None:
        errors = self._mutated_heading_errors(
            "academic-paper/templates/bilingual_abstract_template.md",
            "## Chinese Abstract (zh-TW)",
        )
        self.assertTrue(any("## Chinese Abstract (zh-TW)" in e for e in errors), errors)

    def test_renamed_heading_with_a_prose_quote_still_fires(self) -> None:
        # A whole-file literal pin passed when the operative heading was renamed but some
        # sentence still quoted the old string; the pin now targets the heading line.
        rel_path = "academic-paper/agents/abstract_bilingual_agent.md"
        self._copied_pin_tree()
        path = self.root / rel_path
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                "### English Abstract", "### English Abstract Text"
            )
            + "\nThe historical heading literal was `### English Abstract`.\n",
            encoding="utf-8",
        )
        csc.ERRORS.clear()
        csc.check_output_language_pair_literal_pins(self.root)
        errors = list(csc.ERRORS)
        self.assertTrue(any("### English Abstract" in e and "heading" in e for e in errors), errors)

    def test_workflow_l2_heading_pin_fires(self) -> None:
        errors = self._mutated_errors(
            "academic-paper/references/workflow_phase_details.md", "### English Abstract"
        )
        self.assertTrue(any("### English Abstract" in e for e in errors), errors)

    def test_workflow_l1_heading_pin_fires(self) -> None:
        errors = self._mutated_errors(
            "academic-paper/references/workflow_phase_details.md", "### Chinese Abstract"
        )
        self.assertTrue(any("### Chinese Abstract" in e for e in errors), errors)

    def test_schema4_abstract_typed_row_rename_fires(self) -> None:
        errors = self._mutated_errors(
            csc.OUTPUT_LANGUAGE_PAIR_SCHEMA_SURFACE,
            "| `abstract` | object | `{english: string, chinese: string}`",
            "| `abstract` | object | `{en: string, zh_tw: string}`",
        )
        self.assertTrue(any("must keep its legacy typed shape" in e for e in errors), errors)

    def test_schema4_abstract_prose_quote_does_not_keep_a_renamed_row(self) -> None:
        # The Schema-4 `output_language_pair` row still quotes `abstract: {english,
        # chinese}` in prose, so a whole-file pin would pass after the typed row was
        # renamed. The pin must key off the typed row itself.
        rel_path = csc.OUTPUT_LANGUAGE_PAIR_SCHEMA_SURFACE
        self._copied_pin_tree()
        text = (self.root / rel_path).read_text(encoding="utf-8")
        self.assertIn("abstract: {english, chinese}", text)
        errors = self._mutate_and_run(
            rel_path,
            "| `abstract` | object | `{english: string, chinese: string}`",
            "| `abstract` | object | `{en: string, zh_tw: string}`",
            csc.check_output_language_pair_literal_pins,
        )
        self.assertIn("abstract: {english, chinese}", (self.root / rel_path).read_text(encoding="utf-8"))
        self.assertTrue(any("must keep its legacy typed shape" in e for e in errors), errors)

    def test_schema4_keywords_typed_row_rename_fires(self) -> None:
        errors = self._mutated_errors(
            csc.OUTPUT_LANGUAGE_PAIR_SCHEMA_SURFACE,
            "| `keywords` | object | `{en: list[string], zh_tw: list[string]}`",
            "| `keywords` | object | `{en: list[string]}`",
        )
        self.assertTrue(any("must keep its legacy typed shape" in e for e in errors), errors)

    def test_schema4_duplicate_abstract_row_unbackticked_fires(self) -> None:
        rel_path = csc.OUTPUT_LANGUAGE_PAIR_SCHEMA_SURFACE
        self._copied_pin_tree()
        path = self.root / rel_path
        lines = path.read_text(encoding="utf-8").splitlines()
        new_lines: list[str] = []
        for line in lines:
            new_lines.append(line)
            if "| `abstract` | object |" in line:
                new_lines.append(
                    "| abstract | object | a duplicate row that would shadow the pinned one |"
                )
        path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        csc.ERRORS.clear()
        csc.check_output_language_pair_literal_pins(self.root)
        errors = list(csc.ERRORS)
        self.assertTrue(any("the Schema-4 `abstract` row appears more than once" in e for e in errors), errors)

    def test_schema4_pair_row_removed_fires(self) -> None:
        errors = self._mutated_errors(
            csc.OUTPUT_LANGUAGE_PAIR_SCHEMA_SURFACE,
            "| `output_language_pair` | string |",
            "| `pair_token` | string |",
        )
        self.assertTrue(any("row is missing" in e for e in errors), errors)

    def test_intake_pcr_row_renamed_fires(self) -> None:
        self._copied_pin_tree()
        errors = self._mutate_and_run(
            "academic-paper/agents/intake_agent.md",
            "| **Output Language Pair** |",
            "| Output Language Pair |",
            csc.check_output_language_pair_carrier_steps,
        )
        self.assertTrue(errors)

    def test_intake_pair_row_omission_clause_removed_fires_while_format_profile_row_intact(
        self,
    ) -> None:
        rel_path = "academic-paper/agents/intake_agent.md"
        row_marker = "| **Output Language Pair** |"
        self._copied_pin_tree()
        path = self.root / rel_path
        lines = path.read_text(encoding="utf-8").splitlines()
        new_lines: list[str] = []
        for line in lines:
            if row_marker in line:
                new_lines.append(
                    line.replace(
                        "ROW OMITTED ENTIRELY when the run declares no pair, so a pre-#862 PCR keeps the same rows; ",
                        "",
                    )
                )
            else:
                new_lines.append(line)
        path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        csc.ERRORS.clear()
        csc.check_output_language_pair_carrier_steps(self.root)
        errors = list(csc.ERRORS)
        self.assertTrue(
            any("Output Language Pair" in e and "omitted when the field is absent on that row" in e for e in errors),
            errors,
        )
        format_profile_line = next(
            line for line in path.read_text(encoding="utf-8").splitlines() if "| **Format Profile** |" in line
        )
        self.assertIn("ROW OMITTED ENTIRELY", format_profile_line)

    def test_draft_writer_present_value_bullet_removed_fires(self) -> None:
        self._copied_pin_tree()
        errors = self._mutate_and_run(
            "academic-paper/agents/draft_writer_agent.md",
            "serialize it into the Schema 4 handoff under that exact key",
            "",
            csc.check_output_language_pair_carrier_steps,
        )
        self.assertTrue(
            any("present-value branch" in e for e in errors),
            errors,
        )

    def test_draft_writer_serialization_section_removed_fires(self) -> None:
        self._copied_pin_tree()
        errors = self._mutate_and_run(
            "academic-paper/agents/draft_writer_agent.md",
            "### Schema 4 Serialization (#862 Phase 1)",
            "",
            csc.check_output_language_pair_carrier_steps,
        )
        self.assertTrue(errors)

    def test_missing_pinned_surface_fires(self) -> None:
        self._copied_pin_tree()
        (self.root / csc.LEGACY_PAIR_HEADING_BLOCKS[0][0]).unlink()
        csc.ERRORS.clear()
        csc.check_output_language_pair_literal_pins(self.root)
        errors = list(csc.ERRORS)
        self.assertTrue(any("consumer surface is missing" in e for e in errors), errors)

    def test_real_tree_regime_table_parses(self) -> None:
        csc.ERRORS.clear()
        csc.check_abstract_regime_table(csc.OUTPUT_LANGUAGE_PAIR_LITERAL_ROOT)
        self.assertEqual(list(csc.ERRORS), [])

    def test_regime_table_marker_removed_fires_on_the_real_guide(self) -> None:
        self._copy_real(csc.OUTPUT_LANGUAGE_PAIR_GUIDE)
        errors = self._mutate_and_run(
            csc.OUTPUT_LANGUAGE_PAIR_GUIDE,
            csc._REGIME_TABLE_START,
            "",
            csc.check_abstract_regime_table,
        )
        self.assertTrue(any("markers are missing" in e for e in errors), errors)

    def test_regime_table_required_column_is_pinned_on_the_real_guide(self) -> None:
        # The guide's own table is what the lint reads: renaming a required column has to
        # fail on the shipped file, not only on the fixture.
        self._copy_real(csc.OUTPUT_LANGUAGE_PAIR_GUIDE)
        errors = self._mutate_and_run(
            csc.OUTPUT_LANGUAGE_PAIR_GUIDE,
            "Keywords per language",
            "Notes",
            csc.check_abstract_regime_table,
        )
        self.assertTrue(any("keywords_per_language" in e for e in errors), errors)


if __name__ == "__main__":
    unittest.main()
