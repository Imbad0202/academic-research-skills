#!/usr/bin/env python3

from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

if __package__:  # Package import in tests.
    from ._markdown_lint_util import (
        NON_RELATIVE_LINK_PREFIXES,
        extract_link_targets,
    )
    from ._skill_lint import iter_skill_files
else:  # pragma: no cover - exercised by the CLI smoke path
    from _markdown_lint_util import (
        NON_RELATIVE_LINK_PREFIXES,
        extract_link_targets,
    )
    from _skill_lint import iter_skill_files


ROOT = Path(__file__).resolve().parents[1]
ERRORS: list[str] = []


def read(rel_path: str) -> str:
    return (ROOT / rel_path).read_text(encoding="utf-8")


def fail(message: str) -> None:
    ERRORS.append(message)


def expect_contains(rel_path: str, needle: str) -> None:
    text = read(rel_path)
    if needle not in text:
        fail(f"{rel_path}: missing expected text: {needle!r}")


def expect_absent(rel_path: str, needle: str) -> None:
    text = read(rel_path)
    if needle in text:
        fail(f"{rel_path}: forbidden text still present: {needle!r}")


def extract_section(text: str, start: str, end: str) -> str:
    start_idx = text.find(start)
    if start_idx == -1:
        fail(f"missing section start: {start!r}")
        return ""
    end_idx = text.find(end, start_idx + len(start))
    if end_idx == -1:
        fail(f"missing section end after {start!r}: {end!r}")
        return text[start_idx:]
    return text[start_idx:end_idx]


def check_relative_markdown_links(rel_path: str) -> None:
    text = read(rel_path)
    doc_path = ROOT / rel_path
    for raw_target in extract_link_targets(text):
        if raw_target.startswith(NON_RELATIVE_LINK_PREFIXES):
            continue
        target = raw_target.partition("#")[0]
        if not target:
            continue
        resolved = (doc_path.parent / target).resolve()
        if not resolved.exists():
            fail(f"{rel_path}: broken relative markdown link {raw_target!r}")


def check_mode_registry() -> None:
    rel_path = "MODE_REGISTRY.md"
    text = read(rel_path)
    expect_contains(rel_path, "Last updated: v3.21.1 (2026-08-24)")
    for heading in (
        "## deep-research (8 modes)",
        "## academic-paper (11 modes)",
        "## academic-paper-reviewer (6 modes)",
    ):
        if heading not in text:
            fail(f"{rel_path}: missing mode heading {heading!r}")


def check_claude_md() -> None:
    rel_path = ".claude/CLAUDE.md"
    expect_contains(rel_path, "integrity check (Stage 2.5)")
    expect_contains(rel_path, "final integrity check (Stage 4.5)")
    expect_contains(rel_path, "**Suite version**: 3.21.1")
    for forbidden in (
        "6th independent reviewer",
        "Peer review gains 6th independent reviewer",
    ):
        expect_absent(rel_path, forbidden)


# Every top-level skill carries the same frontmatter (`version` / `last_updated`) +
# Version-Info-table (`| Skill Version |` / `| Last Updated |`) pair. Pre-#377 only the
# reviewer was policed. Derived from disk (#809) rather than hand-listed, so a new skill
# directory is policed the moment it exists; check_skill_inventory_parity.py pins that
# the on-disk set matches every surface that advertises it.
def _skill_version_paths() -> tuple[str, ...]:
    """Read ROOT at call time (tests swap `csc.ROOT` for fixture trees; an
    import-time tuple would carry the real checkout's skills into them)."""
    return tuple(
        f"{skill_md.parent.name}/SKILL.md" for skill_md in iter_skill_files(ROOT)
    )

# The single skill whose `version` tracks the suite version. The other three move independently,
# so only this one's date is sanity-checked against the release (CHANGELOG) in #377(b).
_SUITE_SKILL_PATH = "academic-pipeline/SKILL.md"


def _parse_skill_version_block(rel_path: str) -> tuple[str, str, str, str] | None:
    """Return (frontmatter_version, frontmatter_last_updated, table_version, table_last_updated)
    for a SKILL.md, or None (after recording an error) if any surface is unparseable."""
    text = read(rel_path)
    frontmatter_match = re.search(
        r'metadata:\s*[\s\S]*?\n\s+version:\s"([^"]+)"\n\s+last_updated:\s"([^"]+)"',
        text,
    )
    if not frontmatter_match:
        fail(f"{rel_path}: could not parse frontmatter version/last_updated")
        return None

    version_block_match = re.search(r"\| Skill Version \| ([^|]+) \|", text)
    updated_block_match = re.search(r"\| Last Updated \| ([^|]+) \|", text)
    if not version_block_match or not updated_block_match:
        fail(f"{rel_path}: missing Version Info table rows")
        return None

    version, last_updated = frontmatter_match.groups()
    return (
        version,
        last_updated,
        version_block_match.group(1).strip(),
        updated_block_match.group(1).strip(),
    )


def check_skill_version_blocks() -> None:
    """#377(a): for ALL FOUR SKILL.md, the frontmatter version/last_updated must match the
    Version-Info-table rows (an internal per-file consistency check)."""
    for rel_path in _skill_version_paths():
        parsed = _parse_skill_version_block(rel_path)
        if parsed is None:
            continue
        version, last_updated, version_block, updated_block = parsed
        if version != version_block:
            fail(
                f"{rel_path}: frontmatter version {version!r} does not match Version Info block {version_block!r}"
            )
        if last_updated != updated_block:
            fail(
                f"{rel_path}: frontmatter last_updated {last_updated!r} does not match Version Info block {updated_block!r}"
            )


def _latest_changelog_date() -> str | None:
    """Parse the date of the latest release entry in CHANGELOG.md. The file follows
    Keep-a-Changelog convention — entries are reverse-chronological under a leading
    dateless `## [Unreleased]` header — so the FIRST date-bearing
    `## [X.Y.Z] - YYYY-MM-DD` header is the latest release. `## [Unreleased]` carries no
    `- YYYY-MM-DD` suffix and so never matches this date-bearing pattern."""
    match = re.search(rf"^## \[{_VERSION}\] - (\d{{4}}-\d{{2}}-\d{{2}})", read("CHANGELOG.md"), re.M)
    return match.group(1) if match else None


def check_suite_skill_date_sanity() -> None:
    """#377(b): the suite-tracking skill's `last_updated` must NOT predate the latest CHANGELOG
    entry date — a release that bumps the suite version but forgets the date fails here.

    Scope is deliberately narrow: only `academic-pipeline/SKILL.md` (the suite-tracking skill) is
    date-checked. `academic-paper` / `academic-paper-reviewer` / `deep-research` version
    independently and legitimately keep their own earlier last-change dates, so forcing
    release-date alignment on them would be wrong (#377 out-of-scope)."""
    # check_skill_version_blocks() runs first and already parses the suite SKILL. If it recorded
    # an error for that file (unparseable frontmatter/table), skip rather than re-report the same
    # root cause from a second re-parse here.
    if any(e.startswith(f"{_SUITE_SKILL_PATH}:") for e in ERRORS):
        return

    changelog_date = _latest_changelog_date()
    if changelog_date is None:
        fail("CHANGELOG.md: could not parse latest release entry date")
        return

    parsed = _parse_skill_version_block(_SUITE_SKILL_PATH)
    if parsed is None:
        return
    last_updated = parsed[1]

    # ISO-8601 dates compare correctly as strings (zero-padded, fixed-width).
    if last_updated < changelog_date:
        fail(
            f"{_SUITE_SKILL_PATH}: last_updated {last_updated!r} predates latest CHANGELOG entry "
            f"date {changelog_date!r} — the suite version bumped but the skill date is stale"
        )


def check_pipeline_docs() -> None:
    for rel_path in (
        "academic-pipeline/SKILL.md",
        "academic-pipeline/agents/pipeline_orchestrator_agent.md",
    ):
        expect_absent(rel_path, "auto-continue in 5 seconds")
        expect_contains(rel_path, "One-line status + explicit continue/pause prompt")

    expect_contains(
        "academic-pipeline/agents/pipeline_orchestrator_agent.md",
        "Stage 2.5 can NEVER be skipped",
    )
    expect_contains(
        "academic-pipeline/agents/pipeline_orchestrator_agent.md",
        "Stage 4.5 can NEVER be skipped",
    )


# A version token is a dot-separated run of ≥3 numeric components. The repo's own grammar
# already ships 4-component versions (v3.9.4.2), so a fixed `\d+\.\d+\.\d+` would capture only
# the first three components of `3.9.4.2` and silently compare a truncated `3.9.4` — making a
# genuinely-stale 4-component marker pass. `(?:\.\d+)*` is greedy, so it captures the FULL token;
# the trailing `(?!\.?\d)` is a hard right boundary so a longer numeric run can never tail-match a
# shorter capture (e.g. `3.9.4` must not partial-match inside `3.9.4.2`).
_VERSION = r"\d+\.\d+\.\d+(?:\.\d+)*(?!\.?\d)"


def _suite_version() -> str | None:
    """Parse the canonical suite version from `.claude/CLAUDE.md` (`**Suite version**: X.Y.Z[.W]`)."""
    match = re.search(rf"\*\*Suite version\*\*:\s*({_VERSION})", read(".claude/CLAUDE.md"))
    return match.group(1) if match else None


def check_architecture_component_version() -> None:
    """Invariant-4 (#345): the *current-component* `academic-pipeline` version markers in
    docs/ARCHITECTURE.md must equal the suite version.

    docs/ARCHITECTURE.md carries two kinds of version string and only the first must track the
    suite version:
      - current-component markers — the mermaid orchestrator node + the component table row + the
        four stage-table `(gate)` / stage-6 rows — describe what the *current* pipeline is.
      - feature-history markers — the `timeline` block (`vX.Y.Z : <feature>`) and inline
        "introduced in vX.Y.Z" provenance — record which version first shipped a gate/feature and
        must NOT be bumped on a release that adds no new gate.

    This check anchors on the `academic-pipeline <ver>` component pattern specifically (mermaid
    `<br/>vX.Y.Z` node + ` academic-pipeline vX.Y.Z` table/stage rows) and never inspects the
    timeline block, so a stale current-component marker fails while a feature-history marker is
    left alone. (Surfaced during the v3.11.1 release: six component markers were missed by the
    bump and only caught by a manual sweep — #343/#344.)
    """
    rel_path = "docs/ARCHITECTURE.md"
    version = _suite_version()
    if version is None:
        fail(".claude/CLAUDE.md: could not parse '**Suite version**: X.Y.Z' for ARCHITECTURE check")
        return
    text = read(rel_path)

    # 1. Mermaid orchestrator node: `academic-pipeline<br/>orchestrator<br/>vX.Y.Z`.
    node_versions = re.findall(
        rf"academic-pipeline<br/>orchestrator<br/>v({_VERSION})", text
    )
    if not node_versions:
        fail(f"{rel_path}: no mermaid `academic-pipeline<br/>orchestrator<br/>vX.Y.Z` node found")
    for found in node_versions:
        if found != version:
            fail(
                f"{rel_path}: mermaid orchestrator node version v{found} != suite v{version} "
                f"(invariant-4: current-component marker must equal the suite version)"
            )

    # 2. Component table + stage rows: ` academic-pipeline vX.Y.Z` (table cell / `(gate)` rows).
    #    Anchored to markdown table rows (`^\s*\|` … on the same line) so the scan only ever sees
    #    component/stage cells — never prose like `` `academic-pipeline` v3.9.4 introduced … ``,
    #    which is feature-history provenance and must NOT be policed against the suite version.
    #    The timeline `vX.Y.Z :` form never carries the `academic-pipeline` token, so it is already
    #    out of scope; the table-row anchor additionally excludes any narrative mention.
    row_versions = re.findall(
        rf"(?m)^\s*\|.*?`?academic-pipeline`?\s+v({_VERSION})", text
    )
    if not row_versions:
        fail(f"{rel_path}: no `academic-pipeline vX.Y.Z` component/stage row found")
    for found in row_versions:
        if found != version:
            fail(
                f"{rel_path}: `academic-pipeline v{found}` component/stage row != suite v{version} "
                f"(invariant-4: current-component marker must equal the suite version)"
            )


def check_readme_sections() -> None:
    rel_path = "README.md"
    text = read(rel_path)

    expect_contains(rel_path, "version-v3.21.1-blue")
    expect_contains(rel_path, "releases/tag/v3.21.1")
    expect_contains(rel_path, "### v3.12.0 (2026-06-08)")
    expect_contains(rel_path, "### v3.11.1 (2026-06-06)")
    expect_contains(rel_path, "### v3.11.0 (2026-06-04)")
    expect_contains(rel_path, "### v3.10.0 (2026-06-01)")
    expect_contains(rel_path, "### v3.9.4.2 (2026-05-19)")
    expect_contains(rel_path, "### v3.9.4.1 (2026-05-19)")
    expect_contains(rel_path, "### v3.9.4 (2026-05-18)")
    expect_contains(rel_path, "### v3.9.1 (2026-05-18)")
    expect_contains(rel_path, "### v3.9.0 (2026-05-17)")
    expect_contains(rel_path, "### v3.8.0 (2026-05-16)")
    expect_contains(rel_path, "### v3.7.0 (2026-05-05)")
    expect_contains(rel_path, "### v3.6.8 (2026-05-03)")
    expect_contains(rel_path, "### v3.6.7 (2026-04-30)")
    expect_contains(rel_path, "### v3.6.5 (2026-04-27)")
    expect_contains(rel_path, "### v3.6.4 (2026-04-25)")
    expect_contains(rel_path, "### v3.6.3 (2026-04-23)")
    expect_contains(rel_path, "### v3.6.2 (2026-04-23)")
    expect_contains(rel_path, "### v3.5.1 (2026-04-22)")
    expect_contains(rel_path, "### v3.5.0 (2026-04-21)")
    expect_contains(rel_path, "### v3.4.0 (2026-04-20)")
    expect_contains(rel_path, "### v3.3.6 (2026-04-15)")
    expect_contains(rel_path, "### v3.3.5 (2026-04-15)")
    expect_contains(rel_path, "### v3.3.4 (2026-04-15)")
    expect_contains(rel_path, "### v3.3.3 (2026-04-15)")
    expect_contains(rel_path, "### v3.3.2 (2026-04-15)")
    for heading in (
        "#### Deep Research (8 modes)",
        "#### Academic Paper (11 modes)",
        "#### Academic Paper Reviewer (6 modes)",
        "### Deep Research (v2.12.1)",
        "### Academic Paper (v3.3.1)",
        "### Academic Paper Reviewer (v1.11.1)",
        "### Academic Pipeline (v3.21.1)",
    ):
        if heading not in text:
            fail(f"{rel_path}: missing heading {heading!r}")

    paper_usage = extract_section(
        text, "#### Academic Paper (11 modes)", "#### Academic Paper Reviewer (6 modes)"
    )
    for expected in ("outline-only mode", "abstract-only mode", "disclosure mode"):
        if expected not in paper_usage:
            fail(f"{rel_path}: Academic Paper usage section missing {expected!r}")
    for forbidden in ("bilingual-abstract mode", "writing-polish mode", "full-auto mode"):
        if forbidden in paper_usage:
            fail(f"{rel_path}: Academic Paper usage section still contains {forbidden!r}")

    deep_usage = extract_section(
        text, "#### Deep Research (8 modes)", "#### Academic Paper (11 modes)"
    )
    if "review mode" not in deep_usage:
        fail(f"{rel_path}: Deep Research usage section missing 'review mode'")
    if "paper-review" in deep_usage:
        fail(f"{rel_path}: Deep Research usage section still contains 'paper-review'")

    reviewer_usage = extract_section(
        text, "#### Academic Paper Reviewer (6 modes)", "#### Academic Pipeline (Orchestrator)"
    )
    if "calibration mode" not in reviewer_usage:
        fail(f"{rel_path}: reviewer usage section missing 'calibration mode'")

    for forbidden in (
        "6th independent reviewer",
        "Peer review gains 6th independent reviewer",
    ):
        expect_absent(rel_path, forbidden)
    # DOCX contract lines moved to docs/SETUP.md in v3.3.6; checked there instead.
    expect_contains(rel_path, "DOCX (via Pandoc when available)")
    check_relative_markdown_links(rel_path)


def check_readme_ja_sections() -> None:
    """Symmetric coverage of README.ja-JP.md added in PR #161 (closes #170).

    Pre-#170 the lint silently skipped this file. ja-JP uses ASCII parentheses
    for release blocks (matching the English README), full-width parentheses
    for mode and skill-detail headings, and "モード" instead of "mode".
    """
    rel_path = "README.ja-JP.md"
    text = read(rel_path)

    expect_contains(rel_path, "version-v3.21.1-blue")
    expect_contains(rel_path, "releases/tag/v3.21.1")
    expect_contains(rel_path, "### v3.12.0 (2026-06-08)")
    expect_contains(rel_path, "### v3.11.1 (2026-06-06)")
    expect_contains(rel_path, "### v3.11.0 (2026-06-04)")
    expect_contains(rel_path, "### v3.10.0 (2026-06-01)")
    expect_contains(rel_path, "### v3.9.4.2 (2026-05-19)")
    expect_contains(rel_path, "### v3.9.4.1 (2026-05-19)")
    expect_contains(rel_path, "### v3.9.4 (2026-05-18)")
    expect_contains(rel_path, "### v3.9.1 (2026-05-18)")
    expect_contains(rel_path, "### v3.9.0 (2026-05-17)")
    expect_contains(rel_path, "### v3.8.0 (2026-05-16)")
    expect_contains(rel_path, "### v3.7.0 (2026-05-05)")
    expect_contains(rel_path, "### v3.6.8 (2026-05-03)")
    expect_contains(rel_path, "### v3.6.7 (2026-04-30)")
    expect_contains(rel_path, "### v3.6.5 (2026-04-27)")
    expect_contains(rel_path, "### v3.6.4 (2026-04-25)")
    expect_contains(rel_path, "### v3.6.3 (2026-04-23)")
    expect_contains(rel_path, "### v3.6.2 (2026-04-23)")
    expect_contains(rel_path, "### v3.5.1 (2026-04-22)")
    expect_contains(rel_path, "### v3.5.0 (2026-04-21)")
    expect_contains(rel_path, "### v3.4.0 (2026-04-20)")
    expect_contains(rel_path, "### v3.3.6 (2026-04-15)")
    expect_contains(rel_path, "### v3.3.5 (2026-04-15)")
    expect_contains(rel_path, "### v3.3.4 (2026-04-15)")
    expect_contains(rel_path, "### v3.3.3 (2026-04-15)")
    expect_contains(rel_path, "### v3.3.2 (2026-04-15)")
    for heading in (
        "#### Deep Research（8 モード）",
        "#### Academic Paper（11 モード）",
        "#### Academic Paper Reviewer（6 モード）",
        "#### Academic Pipeline（オーケストレーター）",
        "### Deep Research（v2.12.1）",
        "### Academic Paper（v3.3.1）",
        "### Academic Paper Reviewer（v1.11.1）",
        "### Academic Pipeline（v3.21.1）",
    ):
        if heading not in text:
            fail(f"{rel_path}: missing heading {heading!r}")

    for forbidden in (
        "6th independent reviewer",
        "Peer review gains 6th independent reviewer",
    ):
        expect_absent(rel_path, forbidden)

    # Mode-section content guards (e.g. `outline-only モード` inside the
    # Academic Paper usage block) are deliberately not enforced here; the
    # zh-TW checker uses `extract_section` for that and #171's schema-driven
    # refactor will fold the three locales together. Adding the extract_section
    # mirror now would be discarded by that refactor.
    expect_contains(rel_path, "DOCX（利用可能な場合 Pandoc 経由）")
    check_relative_markdown_links(rel_path)


def check_readme_ko_sections() -> None:
    """Symmetric coverage of README.ko-KR.md added with Korean localization.

    Korean typography uses ASCII parentheses, so the release-block headings match
    the English / ja-JP convention verbatim (NOT the full-width zh-CN/zh-TW form).
    Localized mode headings use ASCII parens + "N개 모드"; skill-detail headings
    reuse the English ASCII-paren form. Mode-section inner-content guards are
    deliberately omitted here, mirroring check_readme_ja_sections — the #171
    schema-driven refactor will fold the locales together, so an extract_section
    mirror added now would be discarded by it.
    """
    rel_path = "README.ko-KR.md"
    text = read(rel_path)

    expect_contains(rel_path, "version-v3.21.1-blue")
    expect_contains(rel_path, "releases/tag/v3.21.1")
    expect_contains(rel_path, "### v3.18.0 (2026-07-18)")
    expect_contains(rel_path, "### v3.12.0 (2026-06-08)")
    expect_contains(rel_path, "### v3.11.1 (2026-06-06)")
    expect_contains(rel_path, "### v3.11.0 (2026-06-04)")
    expect_contains(rel_path, "### v3.10.0 (2026-06-01)")
    expect_contains(rel_path, "### v3.9.4.2 (2026-05-19)")
    expect_contains(rel_path, "### v3.9.4.1 (2026-05-19)")
    expect_contains(rel_path, "### v3.9.4 (2026-05-18)")
    expect_contains(rel_path, "### v3.9.1 (2026-05-18)")
    expect_contains(rel_path, "### v3.9.0 (2026-05-17)")
    expect_contains(rel_path, "### v3.8.0 (2026-05-16)")
    expect_contains(rel_path, "### v3.7.0 (2026-05-05)")
    expect_contains(rel_path, "### v3.6.8 (2026-05-03)")
    expect_contains(rel_path, "### v3.6.7 (2026-04-30)")
    expect_contains(rel_path, "### v3.6.5 (2026-04-27)")
    expect_contains(rel_path, "### v3.6.4 (2026-04-25)")
    expect_contains(rel_path, "### v3.6.3 (2026-04-23)")
    expect_contains(rel_path, "### v3.6.2 (2026-04-23)")
    expect_contains(rel_path, "### v3.5.1 (2026-04-22)")
    expect_contains(rel_path, "### v3.5.0 (2026-04-21)")
    expect_contains(rel_path, "### v3.4.0 (2026-04-20)")
    expect_contains(rel_path, "### v3.3.6 (2026-04-15)")
    expect_contains(rel_path, "### v3.3.5 (2026-04-15)")
    expect_contains(rel_path, "### v3.3.4 (2026-04-15)")
    expect_contains(rel_path, "### v3.3.3 (2026-04-15)")
    expect_contains(rel_path, "### v3.3.2 (2026-04-15)")
    for heading in (
        "#### Deep Research (8개 모드)",
        "#### Academic Paper (11개 모드)",
        "#### Academic Paper Reviewer (6개 모드)",
        "#### Academic Pipeline (오케스트레이터)",
        "### Deep Research (v2.12.1)",
        "### Academic Paper (v3.3.1)",
        "### Academic Paper Reviewer (v1.11.1)",
        "### Academic Pipeline (v3.21.1)",
    ):
        if heading not in text:
            fail(f"{rel_path}: missing heading {heading!r}")

    for forbidden in (
        "6th independent reviewer",
        "Peer review gains 6th independent reviewer",
    ):
        expect_absent(rel_path, forbidden)

    expect_contains(rel_path, "DOCX (가능한 경우 Pandoc 경유)")
    check_relative_markdown_links(rel_path)


ZH_README_CONFIGS = (
    {
        "rel_path": "README.zh-TW.md",
        "headings": (
            "#### Deep Research（深度研究，8 種模式）",
            "#### Academic Paper（學術論文撰寫，11 種模式）",
            "#### Academic Paper Reviewer（論文審查，6 種模式）",
            "### Deep Research (v2.12.1)",
            "### Academic Paper (v3.3.1)",
            "### Academic Paper Reviewer (v1.11.1)",
            "### Academic Pipeline (v3.21.1)",
        ),
        "paper_start": "#### Academic Paper（學術論文撰寫，11 種模式）",
        "reviewer_start": "#### Academic Paper Reviewer（論文審查，6 種模式）",
        "pipeline_start": "#### Academic Pipeline（全流程調度器）",
        "deep_start": "#### Deep Research（深度研究，8 種模式）",
        "docx_line": "DOCX（Pandoc 可用時）",
    },
    {
        "rel_path": "README.zh-CN.md",
        "headings": (
            "#### Deep Research（深度研究，8 种模式）",
            "#### Academic Paper（学术论文撰写，11 种模式）",
            "#### Academic Paper Reviewer（论文审查，6 种模式）",
            "### Deep Research (v2.12.1)",
            "### Academic Paper (v3.3.1)",
            "### Academic Paper Reviewer (v1.11.1)",
            "### Academic Pipeline (v3.21.1)",
        ),
        "paper_start": "#### Academic Paper（学术论文撰写，11 种模式）",
        "reviewer_start": "#### Academic Paper Reviewer（论文审查，6 种模式）",
        "pipeline_start": "#### Academic Pipeline（全流程调度器）",
        "deep_start": "#### Deep Research（深度研究，8 种模式）",
        "docx_line": "DOCX（Pandoc 可用时）",
    },
)


def check_readme_zh_sections() -> None:
    for config in ZH_README_CONFIGS:
        rel_path = config["rel_path"]
        text = read(rel_path)

        expect_contains(rel_path, "version-v3.21.1-blue")
        expect_contains(rel_path, "releases/tag/v3.21.1")
        expect_contains(rel_path, "### v3.12.0（2026-06-08）")
        expect_contains(rel_path, "### v3.11.1（2026-06-06）")
        expect_contains(rel_path, "### v3.11.0（2026-06-04）")
        expect_contains(rel_path, "### v3.10.0（2026-06-01）")
        expect_contains(rel_path, "### v3.9.4.2（2026-05-19）")
        expect_contains(rel_path, "### v3.9.4.1（2026-05-19）")
        expect_contains(rel_path, "### v3.9.4（2026-05-18）")
        expect_contains(rel_path, "### v3.9.1（2026-05-18）")
        expect_contains(rel_path, "### v3.9.0（2026-05-17）")
        expect_contains(rel_path, "### v3.8.0（2026-05-16）")
        expect_contains(rel_path, "### v3.7.0（2026-05-05）")
        expect_contains(rel_path, "### v3.6.8（2026-05-03）")
        expect_contains(rel_path, "### v3.6.7（2026-04-30）")
        expect_contains(rel_path, "### v3.6.5（2026-04-27）")
        expect_contains(rel_path, "### v3.6.4（2026-04-25）")
        expect_contains(rel_path, "### v3.6.3（2026-04-23）")
        expect_contains(rel_path, "### v3.6.2（2026-04-23）")
        expect_contains(rel_path, "### v3.5.1（2026-04-22）")
        expect_contains(rel_path, "### v3.5.0（2026-04-21）")
        expect_contains(rel_path, "### v3.4.0（2026-04-20）")
        expect_contains(rel_path, "### v3.3.6 (2026-04-15)")
        expect_contains(rel_path, "### v3.3.5 (2026-04-15)")
        expect_contains(rel_path, "### v3.3.4 (2026-04-15)")
        expect_contains(rel_path, "### v3.3.3 (2026-04-15)")
        expect_contains(rel_path, "### v3.3.2 (2026-04-15)")
        for heading in config["headings"]:
            if heading not in text:
                fail(f"{rel_path}: missing heading {heading!r}")

        paper_usage = extract_section(
            text,
            config["paper_start"],
            config["reviewer_start"],
        )
        for expected in ("outline-only mode", "abstract-only mode", "disclosure mode"):
            if expected not in paper_usage:
                fail(f"{rel_path}: Academic Paper usage section missing {expected!r}")
        for forbidden in ("bilingual-abstract mode", "writing-polish mode", "full-auto mode"):
            if forbidden in paper_usage:
                fail(f"{rel_path}: Academic Paper usage section still contains {forbidden!r}")

        deep_usage = extract_section(
            text,
            config["deep_start"],
            config["paper_start"],
        )
        if "review mode" not in deep_usage:
            fail(f"{rel_path}: Deep Research usage section missing 'review mode'")
        if "paper-review" in deep_usage:
            fail(f"{rel_path}: Deep Research usage section still contains 'paper-review'")

        reviewer_usage = extract_section(
            text,
            config["reviewer_start"],
            config["pipeline_start"],
        )
        if "calibration mode" not in reviewer_usage:
            fail(f"{rel_path}: reviewer usage section missing 'calibration mode'")

        for forbidden in (
            "6th independent reviewer",
            "Peer review gains 6th independent reviewer",
        ):
            expect_absent(rel_path, forbidden)
        # DOCX contract lines moved to setup docs in v3.3.6; checked there instead.
        expect_contains(rel_path, config["docx_line"])
        check_relative_markdown_links(rel_path)


def check_setup_docs() -> None:
    expect_contains("docs/SETUP.md", "Direct `.docx` generation uses [Pandoc]")
    expect_contains(
        "docs/SETUP.md",
        "Direct `.docx` generation requires Pandoc, and PDF generation requires `tectonic`",
    )
    expect_contains("docs/SETUP.zh-TW.md", "若要直接產出 `.docx`，需要安裝 [Pandoc]")
    expect_contains(
        "docs/SETUP.zh-TW.md",
        "直接產出 `.docx` 需要 Pandoc，PDF 需要 `tectonic`",
    )
    check_relative_markdown_links("docs/SETUP.md")
    check_relative_markdown_links("docs/SETUP.zh-TW.md")
    # #758 data-flow map: its outbound relative links (audit doc, SECURITY,
    # THIRD_PARTY, cross_model_verification) must keep resolving.
    check_relative_markdown_links("docs/DATA_FLOWS.md")


def check_docx_contract() -> None:
    expect_contains(
        "academic-paper/SKILL.md",
        "LaTeX/DOCX-via-Pandoc/PDF output",
    )
    expect_contains(
        "academic-paper/agents/formatter_agent.md",
        "If Pandoc is available, generate the `.docx` file directly",
    )
    expect_contains(
        "academic-paper/agents/formatter_agent.md",
        "If Pandoc is unavailable, provide complete markdown + DOCX conversion instructions",
    )
    expect_contains(
        "academic-pipeline/SKILL.md",
        "DOCX via Pandoc when available, otherwise conversion instructions",
    )
    expect_contains(
        "academic-pipeline/agents/pipeline_orchestrator_agent.md",
        "DOCX via Pandoc when available (otherwise instructions)",
    )
    for rel_path in (
        "academic-pipeline/SKILL.md",
        "academic-pipeline/agents/pipeline_orchestrator_agent.md",
    ):
        expect_absent(rel_path, "Auto-produce MD + DOCX")


def check_reference_docs() -> None:
    expect_contains(
        "academic-pipeline/references/passport_as_reset_boundary.md",
        "# Passport as Reset Boundary (v3.6.3)",
    )
    expect_contains(
        "academic-pipeline/references/passport_as_reset_boundary.md",
        "## `resume_from_passport` mode contract",
    )
    expect_contains(
        "academic-pipeline/references/passport_as_reset_boundary.md",
        "## Iron rules",
    )
    # Unified PASSPORT-RESET tag format across protocol doc + orchestrator emission + checkpoint template.
    # Divergence here breaks cross-session machine-stable handoff.
    tag_format = "[PASSPORT-RESET: hash=<hash>, stage=<completed>, next=<next>]"
    expect_contains(
        "academic-pipeline/references/passport_as_reset_boundary.md",
        tag_format,
    )
    expect_contains(
        "academic-pipeline/agents/pipeline_orchestrator_agent.md",
        tag_format,
    )


def check_rebuttal_audit_guard() -> None:
    """The rebuttal-audit mode section must declare its integrity boundary.

    A standalone rebuttal-audit invocation runs outside the pipeline, so it must
    NOT emit Schema 11 / Material Passport / ready_to_submit. This guard is the
    load-bearing reason rebuttal-audit is safe to ship as a mode rather than a
    pipeline stage; if the suppression language is ever dropped, the mode would
    silently re-introduce the false-certification risk it was designed to avoid.
    """
    text = read("academic-paper/SKILL.md")
    m = re.search(r"##\s*Rebuttal-Audit Mode.*?(?=\n##\s|\Z)", text, re.DOTALL)
    section = m.group(0) if m else ""
    if not section:
        fail("academic-paper/SKILL.md: missing '## Rebuttal-Audit Mode' section")
        return
    for kw in ["Schema 11", "Material Passport", "ready_to_submit"]:
        if kw not in section:
            fail(
                f"academic-paper/SKILL.md Rebuttal-Audit Mode section must declare "
                f"{kw!r} suppression (integrity boundary)"
            )
    if "MUST NOT" not in section:
        fail(
            "academic-paper/SKILL.md Rebuttal-Audit Mode section lacks an explicit "
            "'MUST NOT' suppression statement"
        )


def check_ideation_diversity_no_call_contract() -> None:
    """Keep #659's schemas, runner, docs, and CI registration aligned."""
    suite = "evals/heldout/within_session_ideation_diversity"
    schema_paths = {
        "run_plan": f"{suite}/run_plan.schema.json",
        "authorization": f"{suite}/authorization_record.schema.json",
        "transcript": f"{suite}/transcript.schema.json",
        "ingestion": f"{suite}/ingestion_manifest.schema.json",
        "stop_intent": f"{suite}/stop_intent.schema.json",
        "blind_packet": f"{suite}/blind_packet.schema.json",
        "blind_inventory": f"{suite}/blind_inventory.schema.json",
        "blind_manifest": f"{suite}/blind_manifest.schema.json",
        "private_arm_map": f"{suite}/private_arm_map.schema.json",
        "blind_intent": f"{suite}/blind_intent.schema.json",
    }
    schemas: dict[str, dict] = {}
    for name, rel_path in schema_paths.items():
        try:
            value = json.loads(read(rel_path))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            fail(f"{rel_path}: cannot load #659 contract: {exc}")
            continue
        if not isinstance(value, dict) or value.get("additionalProperties") is not False:
            fail(f"{rel_path}: root contract must be a closed object")
            continue
        schemas[name] = value

    plan = schemas.get("run_plan", {})
    plan_properties = plan.get("properties", {})
    design = plan_properties.get("design", {}).get("properties", {})
    expected_design = {
        "experiments": 2,
        "scenarios": 6,
        "arms_per_experiment": 2,
        "replicates_per_scenario_arm": 2,
        "subject_session_cells": 48,
    }
    for field, expected in expected_design.items():
        if design.get(field, {}).get("const") != expected:
            fail(f"{schema_paths['run_plan']}: {field} must remain const {expected}")
    execution = plan.get("$defs", {}).get("execution", {}).get("properties", {})
    no_call_constants = {
        "tools": [],
        "web_enabled": False,
        "runner_transport": "none",
        "dispatch_available": False,
        "api_spend_ceiling_usd": 0,
        "api_fallback": False,
        "envelope_grants_consent": False,
        "fresh_external_authorization_required": True,
    }
    for field, expected in no_call_constants.items():
        if execution.get(field, {}).get("const") != expected:
            fail(f"{schema_paths['run_plan']}: no-call constant {field!r} drifted")
    provenance = plan_properties.get("suite_commit_provenance", {}).get(
        "properties", {}
    )
    if provenance.get("status", {}).get("const") != "operator_declared_unverified":
        fail(f"{schema_paths['run_plan']}: suite commit must remain unverified")
    cap_boundary = execution.get("token_cap_verification", {}).get("properties", {})
    for field, expected in {
        "status": "operator_declared_unverified",
        "enforced_by_no_call_runner": False,
        "observed_usage_recorded": False,
        "provider_tokenizer_verified": False,
    }.items():
        if cap_boundary.get(field, {}).get("const") != expected:
            fail(
                f"{schema_paths['run_plan']}: token-cap boundary {field!r} drifted"
            )
    judge = plan_properties.get("judge_requirements", {}).get("properties", {})
    for field, expected in {
        "first_round_assignment_ledger_required_before_delivery": True,
        "same_role_card_cross_arm_or_replicate_exposure_forbidden": True,
        "bundle_alone_proves_judge_exposure_blindness": False,
    }.items():
        if judge.get(field, {}).get("const") != expected:
            fail(f"{schema_paths['run_plan']}: judge exposure boundary {field!r} drifted")
    if plan_properties.get("cells", {}).get("minItems") != 48 or plan_properties.get(
        "cells", {}
    ).get("maxItems") != 48:
        fail(f"{schema_paths['run_plan']}: cells must remain exactly 48")
    assets = plan_properties.get("asset_bindings", {})
    if assets.get("minItems") != 18 or assets.get("maxItems") != 18:
        fail(f"{schema_paths['run_plan']}: asset bindings must remain exactly 18")

    stop_receipt = (
        schemas.get("ingestion", {})
        .get("$defs", {})
        .get("stop_receipt", {})
        .get("properties", {})
    )
    if "pre_stop_inventory" not in stop_receipt:
        fail(f"{schema_paths['ingestion']}: compact pre-stop inventory binding missing")
    blind_intent = schemas.get("blind_intent", {}).get("properties", {})
    for field, expected in {
        "staging_ref": "blind-staging",
        "final_ref": "blind",
        "recovery_policy": "exact_recovery_only_no_second_bundle",
    }.items():
        if blind_intent.get(field, {}).get("const") != expected:
            fail(f"{schema_paths['blind_intent']}: {field!r} recovery boundary drifted")
    intent_protection = blind_intent.get("protection", {}).get("properties", {})
    for field, expected in {
        "procedural_nondisclosure_only": True,
        "file_mode": "0600",
        "deliver_to_judges": False,
    }.items():
        if intent_protection.get(field, {}).get("const") != expected:
            fail(
                f"{schema_paths['blind_intent']}: "
                f"protection boundary {field!r} drifted"
            )

    runner_path = "scripts/run_ideation_diversity_no_call.py"
    runner_source = read(runner_path)
    try:
        tree = ast.parse(runner_source)
    except SyntaxError as exc:
        fail(f"{runner_path}: cannot parse runner AST: {exc}")
        tree = ast.Module(body=[], type_ignores=[])
    allowed_direct_imports = {
        "argparse",
        "base64",
        "copy",
        "hashlib",
        "json",
        "os",
        "re",
        "secrets",
        "stat",
        "sys",
        "unicodedata",
        "validate_ideation_diversity_assets",
    }
    allowed_from_imports = {
        "__future__": {"annotations"},
        "datetime": {"datetime"},
        "jsonschema": {"Draft202012Validator", "FormatChecker"},
        "pathlib": {"Path"},
        "typing": {"Any", "NoReturn"},
    }
    allowed_module_calls = {
        "argparse": {"ArgumentParser"},
        "base64": {"b64decode", "b64encode"},
        "copy": {"deepcopy"},
        "hashlib": {"sha256"},
        "json": {"dumps", "loads"},
        "os": {
            "chmod",
            "close",
            "fsync",
            "link",
            "open",
            "rename",
            "replace",
            "write",
        },
        "re": {"compile", "escape", "search"},
        "secrets": {"token_hex"},
        "stat": {"S_IFMT", "S_IMODE", "S_ISREG"},
        "unicodedata": {"category", "normalize"},
        "validate_ideation_diversity_assets": {"load_assets", "render_variant"},
    }
    allowed_module_constants = {
        "argparse": {"ArgumentParser", "Namespace"},
        "json": {"JSONDecodeError"},
        "os": {
            "O_CREAT",
            "O_DIRECTORY",
            "O_EXCL",
            "O_NOFOLLOW",
            "O_RDONLY",
            "O_WRONLY",
        },
        "re": {"IGNORECASE"},
    }
    forbidden_dynamic_names = {
        "__builtins__",
        "__import__",
        "breakpoint",
        "compile",
        "delattr",
        "eval",
        "exec",
        "getattr",
        "globals",
        "locals",
        "setattr",
        "vars",
    }
    forbidden_dynamic_attributes = {
        "Popen",
        "__bases__",
        "__builtins__",
        "__class__",
        "__closure__",
        "__code__",
        "__dict__",
        "__getattribute__",
        "__globals__",
        "__import__",
        "__loader__",
        "__subclasses__",
        "_getframe",
        "call",
        "check_call",
        "check_output",
        "connect",
        "create_connection",
        "execv",
        "execve",
        "f_builtins",
        "f_globals",
        "f_locals",
        "fork",
        "import_module",
        "modules",
        "popen",
        "request",
        "run",
        "spawn",
        "system",
        "urlopen",
    }
    commands: set[str] = set()
    forbidden_imports: set[str] = set()
    direct_module_bindings: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name not in allowed_direct_imports:
                    forbidden_imports.add(alias.name)
                    continue
                binding = alias.asname or alias.name
                existing = direct_module_bindings.get(binding)
                if existing is not None and existing != alias.name:
                    forbidden_imports.add(f"ambiguous-binding:{binding}")
                direct_module_bindings[binding] = alias.name
        elif isinstance(node, ast.ImportFrom):
            module = node.module or "<relative>"
            allowed_symbols = (
                allowed_from_imports.get(module, set())
                if node.level == 0
                else set()
            )
            forbidden_imports.update(
                f"{module}.{alias.name}"
                for alias in node.names
                if alias.name not in allowed_symbols
            )
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "add_parser"
            and node.args
            and isinstance(node.args[0], ast.Constant)
            and isinstance(node.args[0].value, str)
        ):
            commands.add(node.args[0].value)
    if forbidden_imports:
        fail(
            f"{runner_path}: imports must match the exact import allowlist: "
            f"{sorted(forbidden_imports)!r}"
        )

    shadowed_module_bindings: set[str] = set()
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Name)
            and isinstance(node.ctx, (ast.Store, ast.Del))
            and node.id in direct_module_bindings
        ):
            shadowed_module_bindings.add(node.id)
        elif isinstance(node, ast.arg) and node.arg in direct_module_bindings:
            shadowed_module_bindings.add(node.arg)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if node.name in direct_module_bindings:
                shadowed_module_bindings.add(node.name)
        elif isinstance(node, ast.ExceptHandler):
            if isinstance(node.name, str) and node.name in direct_module_bindings:
                shadowed_module_bindings.add(node.name)
        elif isinstance(node, (ast.MatchAs, ast.MatchStar)):
            if isinstance(node.name, str) and node.name in direct_module_bindings:
                shadowed_module_bindings.add(node.name)
        elif isinstance(node, ast.MatchMapping):
            if isinstance(node.rest, str) and node.rest in direct_module_bindings:
                shadowed_module_bindings.add(node.rest)
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                binding = alias.asname or alias.name
                if binding in direct_module_bindings:
                    shadowed_module_bindings.add(binding)
    if shadowed_module_bindings:
        fail(
            f"{runner_path}: direct module bindings cannot be shadowed: "
            f"{sorted(shadowed_module_bindings)!r}"
        )

    parents = {
        child: parent
        for parent in ast.walk(tree)
        for child in ast.iter_child_nodes(parent)
    }
    module_reference_errors: set[str] = set()
    for node in ast.walk(tree):
        if not (
            isinstance(node, ast.Name)
            and isinstance(node.ctx, ast.Load)
            and node.id in direct_module_bindings
        ):
            continue
        module = direct_module_bindings[node.id]
        parent = parents.get(node)
        allowed_hasattr = (
            isinstance(parent, ast.Call)
            and isinstance(parent.func, ast.Name)
            and parent.func.id == "hasattr"
            and len(parent.args) == 2
            and parent.args[0] is node
            and isinstance(parent.args[1], ast.Constant)
            and parent.args[1].value in {"O_DIRECTORY", "O_NOFOLLOW"}
            and module == "os"
        )
        if allowed_hasattr:
            continue
        if not (isinstance(parent, ast.Attribute) and parent.value is node):
            module_reference_errors.add(
                f"{module} via {node.id}: bare module reference"
            )
            continue
        attributes = [parent.attr]
        outer = parent
        while True:
            ancestor = parents.get(outer)
            if not (
                isinstance(ancestor, ast.Attribute) and ancestor.value is outer
            ):
                break
            attributes.append(ancestor.attr)
            outer = ancestor
        attribute_path = ".".join(attributes)
        use_parent = parents.get(outer)
        allowed_call = (
            attribute_path in allowed_module_calls.get(module, set())
            and isinstance(use_parent, ast.Call)
            and use_parent.func is outer
        )
        allowed_print_value = (
            module == "sys"
            and attribute_path == "stderr"
            and isinstance(use_parent, ast.keyword)
            and use_parent.arg == "file"
            and isinstance(parents.get(use_parent), ast.Call)
            and isinstance(parents[use_parent].func, ast.Name)
            and parents[use_parent].func.id == "print"
        )
        allowed_constant = (
            attribute_path in allowed_module_constants.get(module, set())
            and isinstance(outer.ctx, ast.Load)
        )
        if not (allowed_call or allowed_print_value or allowed_constant):
            module_reference_errors.add(
                f"{module} via {node.id}.{attribute_path}"
            )
    if module_reference_errors:
        fail(
            f"{runner_path}: direct module references must match exact "
            "current-use call/value allowlists: "
            f"{sorted(module_reference_errors)!r}"
        )

    dynamic_references: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id in forbidden_dynamic_names:
            dynamic_references.add(node.id)
        elif (
            isinstance(node, ast.Attribute)
            and node.attr in forbidden_dynamic_attributes
        ):
            dynamic_references.add(node.attr)
    if dynamic_references:
        fail(
            f"{runner_path}: dynamic import, introspection, process, or network "
            f"references are forbidden: {sorted(dynamic_references)!r}"
        )
    expected_commands = {
        "init-run",
        "materialize",
        "validate",
        "ingest",
        "prepare-blind-packet",
    }
    if commands != expected_commands:
        fail(f"{runner_path}: command set must be exactly {sorted(expected_commands)!r}")

    readme = f"{suite}/README.md"
    design_doc = "docs/design/2026-08-13-659-within-session-ideation-diversity-design.md"
    for rel_path, phrases in (
        (
            readme,
            (
                "48-cell plan",
                "no transport, dispatch, probe",
                "The first binding",
                "compact canonical digest",
                "blind-intent.json",
                "exactly one isolated packet",
                "cannot authenticate the operator",
                "two independent human judges",
            ),
        ),
        (
            design_doc,
            (
                "Phase-2 no-call execution envelope",
                "= 48 subject-session",
                "API spend ceiling USD 0",
                "48 write-once isolated single-session packets",
                "durable deterministic blind intent",
                "does not authenticate operator identity",
                "No subject, actor, judge, or adjudicator session is authorized",
            ),
        ),
    ):
        for phrase in phrases:
            expect_contains(rel_path, phrase)
    expect_contains(
        "scripts/_ci_pytest_manifest.toml",
        'id = "659-within-session-ideation-diversity-no-call-envelope"',
    )
    expect_contains(
        "scripts/_ci_pytest_manifest.toml",
        'path = "scripts/test_run_ideation_diversity_no_call.py"',
    )
    expect_contains(
        "CHANGELOG.md",
        "Within-session ideation-diversity Phase-2 no-call envelope (#659)",
    )
def check_indirect_prompt_injection_no_call_envelope() -> None:
    """Pin #675 Phase-2's no-call surface and human-evidence boundary."""
    readme = "evals/heldout/indirect_prompt_injection_behavior/README.md"
    design = "docs/design/2026-08-13-675-indirect-prompt-injection-behavior-eval-spec.md"
    workflow = ".github/workflows/spec-consistency.yml"
    manifest = "scripts/_ci_pytest_manifest.toml"
    for rel_path in (
        "evals/heldout/indirect_prompt_injection_behavior/run_plan.schema.json",
        "evals/heldout/indirect_prompt_injection_behavior/authorization_record.schema.json",
        "evals/heldout/indirect_prompt_injection_behavior/transcript.schema.json",
        "evals/heldout/indirect_prompt_injection_behavior/ingestion_manifest.schema.json",
        "evals/heldout/indirect_prompt_injection_behavior/blind_session_packet.schema.json",
        "evals/heldout/indirect_prompt_injection_behavior/blind_inventory.schema.json",
        "evals/heldout/indirect_prompt_injection_behavior/blind_private_map.schema.json",
        "evals/heldout/indirect_prompt_injection_behavior/blind_manifest.schema.json",
        "evals/heldout/indirect_prompt_injection_behavior/stop_intent.schema.json",
        "evals/heldout/indirect_prompt_injection_behavior/judge_assignment_ledger.schema.json",
        "evals/heldout/indirect_prompt_injection_behavior/journal_token.schema.json",
        "scripts/run_indirect_prompt_injection_no_call.py",
        "scripts/check_indirect_prompt_injection_no_call.py",
        "scripts/test_run_indirect_prompt_injection_no_call.py",
    ):
        if not (ROOT / rel_path).is_file():
            fail(f"#675 Phase-2 required surface is missing: {rel_path}")
    for needle in (
        "8 scenarios x 2 content conditions x 2 guidance",
        "runner_transport=none",
        "64 complete records",
        "two independent arm-blind human judges",
        "separate arm-blind human",
        "does not verify",
        "operator identity",
        "pinned canonical-event decoder",
        "unique receipt id",
        "write-once stop intent",
        "pre-armed journal claim",
        "pre-load-terminal token",
        "same-inode completed",
        "ambiguous state before reading another transcript",
        "deterministic sibling staging path",
        "pre-load quarantine",
        "future closed assignment ledger",
        "does not prove arm blindness",
        "finalized blind manifest",
        "map is unencrypted",
    ):
        expect_contains(readme, needle)
    for needle in (
        "exactly 64 subject",
        "provider transport, detect, dispatch, probe, model, network, process",
        "does not authenticate the operator",
        "two independent arm-blind human judges",
        "closed write-once stop",
        "pre-arms 64 immutable ingestion journal tokens",
        "one pre-load-terminal",
        "same-inode completed",
        "claimed-only state is permanently ambiguous",
        "deterministic sibling staging path",
        "pre-load quarantine",
        "future closed assignment ledger",
        "does not prove that property",
        "unique receipt id",
        "final manifest binds the exact",
        "private map is not encrypted",
    ):
        expect_contains(design, needle)
    expect_contains(workflow, "python3 scripts/check_indirect_prompt_injection_no_call.py")
    expect_contains(manifest, 'path = "scripts/test_run_indirect_prompt_injection_no_call.py"')
    check_relative_markdown_links(readme)


def main() -> int:
    check_mode_registry()
    check_claude_md()
    check_skill_version_blocks()
    check_suite_skill_date_sanity()
    check_pipeline_docs()
    check_architecture_component_version()
    check_readme_sections()
    check_readme_zh_sections()
    check_readme_ja_sections()
    check_readme_ko_sections()
    check_setup_docs()
    check_docx_contract()
    check_reference_docs()
    check_rebuttal_audit_guard()
    check_ideation_diversity_no_call_contract()
    check_indirect_prompt_injection_no_call_envelope()

    if ERRORS:
        print("Spec consistency check failed:")
        for error in ERRORS:
            print(f"- {error}")
        return 1

    print("Spec consistency check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
