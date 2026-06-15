#!/usr/bin/env python3
"""Lint: version labels stay aligned across .claude/CLAUDE.md, SKILL.md frontmatter, and CHANGELOG.md.

Invariants enforced:
  1. Every skill listed in .claude/CLAUDE.md Skills Overview table has a version
     equal to its own SKILL.md metadata.version.
  2. .claude/CLAUDE.md "**Suite version**: X.Y.Z" equals the most recent
     "## [X.Y.Z]" entry in CHANGELOG.md.
  3. academic-pipeline version in the table equals the suite version (pipeline
     = orchestrator, by convention tracks the suite release).
  4. The plugin manifests (.claude-plugin/plugin.json "version" and
     .claude-plugin/marketplace.json plugins[].version) equal the suite version.
     These are the repo's OUTWARD-FACING package metadata — a user updating the
     plugin sees them — and were the one surface a v3.10.0 release-doc pass missed
     because no lint covered them (marketplace had silently sat at 3.7.0).
  5. The README.md shields.io version badge (`badge/version-vX.Y.Z`) equals the
     suite version — the most outward-facing surface of all.
  6. No docs/*.md cites a `vX.Y.Z` ABOVE the suite version (a forward/unknown
     reference misleads readers). Equal-to-suite is allowed.
  7. Every version-bearing H2 heading in docs/<name>.md has a matching
     version-bearing H2 (same version) in docs/<name>.zh-TW.md and vice versa.
     Plain headings may differ — only version TAGS must stay in lockstep.
  8. The plugin.json description's "N-agent" claim (when present) equals the
     number of unique *_agent.md files in the tree (#414: the advertised
     number had silently drifted from the tree). The plugin-root agents/
     mirror dir is excluded from the count — real byte-identical copies of
     deep-research agents since #413 (symlinks before that), pinned as pure
     aliases by check_agents_mirror_sync.py, never a source of new agents.

Runs from repo root by default; `--path` lets tests point at a fake tree.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

from _skill_lint import parse_frontmatter, FrontmatterError


# Broad token captures: anything that looks like an identifier inside the
# expected position. The strict validator below then decides whether the raw
# token is a canonical semver. Using the regex as a filter (the pre-#169
# pattern) silently dropped invalid tokens and hid the very drift this lint
# is meant to surface; see dual-track review on PR for that class of bug.
TABLE_TOKEN_RE = re.compile(
    r"^\|\s*`([a-z0-9-]+)`\s+v([A-Za-z0-9.\-_+]+)\s*\|", re.MULTILINE
)
SUITE_TOKEN_RE = re.compile(
    r"^\s*-\s*\*\*Suite version\*\*:\s*([A-Za-z0-9.\-_+]+)", re.MULTILINE
)
CHANGELOG_TOKEN_RE = re.compile(r"^##\s*\[([A-Za-z0-9.\-_+]+)\]", re.MULTILINE)
SEMVER_STRICT_RE = re.compile(r"^\d+(?:\.\d+){2,3}$")  # exactly 3 or 4 segments (N.N.N or N.N.N.N)

# Invariant 5: shields.io version badge label, e.g. `badge/version-v3.11.1-blue`.
# `_VSEG` = 3-or-4 numeric segments. The trailing `(?!\.?\d)` stops a 5th
# segment (`3.11.1.2.3` would otherwise yield `3.11.1.2`); the label's own
# `-<color>` separator already bounds the token on the right, so no broader
# suffix lookahead is needed here. Keyed off the label, not the release URL.
_VSEG = r"(\d+(?:\.\d+){2,3})"
README_BADGE_RE = re.compile(r"badge/version-v" + _VSEG + r"(?!\.?\d)", re.IGNORECASE)
# Invariant 6 only: a CANONICAL `vX.Y.Z(.W)` token in docs prose. The leading
# `(?<![\w.])` blocks mid-identifier matches; the trailing `(?![\d.\-+A-Za-z])`
# drops prerelease/build/5-segment tokens ENTIRELY (`v3.12.0-alpha`,
# `v3.11.1.2.3`) rather than partial-matching them (review finding). `_VSEG` is
# 3-or-4 segments, so a 2-segment `v3.10` never matches and is silently
# ignored (inv 6 gates only on full release tokens; a partial like `v3.10`
# is not a version this lint adjudicates). Invariant 7 uses H2_VERSION_RE.
DOCS_VERSION_RE = re.compile(r"(?<![\w.])v" + _VSEG + r"(?![\d.\-+A-Za-z])")
# Invariant 7: version tag inside an H2 heading, e.g. `## Corpus (v3.6.4+)`.
# Same canonical-token shape, but a trailing `+` IS allowed (the repo's
# "vX.Y.Z and later" heading convention, e.g. `(v3.6.4+)`); only `-`/letters/
# extra `.N` segments disqualify.
H2_RE = re.compile(r"^##\s+(.*?)\s*$", re.MULTILINE)
H2_VERSION_RE = re.compile(r"(?<![\w.])v" + _VSEG + r"(?![\d.\-A-Za-z])")

NON_VERSION_CHANGELOG_TOKENS = frozenset({"Unreleased"})

# Invariant 8: the outward-facing agent-count claim, e.g. "38-agent ensemble".
AGENT_CLAIM_RE = re.compile(r"(\d+)-agent")

PIPELINE_SKILL_NAME = "academic-pipeline"


def _version_tuple(token: str) -> tuple[int, ...]:
    """Parse a canonical N.N.N(.N) into an int tuple for ordering."""
    return tuple(int(p) for p in token.split("."))


def _version_le(a: str, b: str) -> bool:
    """a <= b by segment-wise numeric compare (pads shorter with zeros)."""
    ta, tb = _version_tuple(a), _version_tuple(b)
    n = max(len(ta), len(tb))
    return ta + (0,) * (n - len(ta)) <= tb + (0,) * (n - len(tb))


def _is_strict_semver(token: str) -> bool:
    return bool(SEMVER_STRICT_RE.match(token))


def _parse_table_versions(
    claude_md_text: str,
) -> tuple[dict[str, str], list[tuple[str, str]]]:
    """Return (valid_versions, invalid_rows) from the Skills Overview table.

    `valid_versions` maps skill_name -> version for rows whose v-token is a
    canonical N.N.N(.N)+ string. `invalid_rows` collects (skill_name, raw_token)
    for rows where the v-token is present but not a canonical version; the
    caller surfaces these as errors so a malformed table row does not silently
    drop out of downstream invariants.
    """
    valid: dict[str, str] = {}
    invalid: list[tuple[str, str]] = []
    for skill, raw in TABLE_TOKEN_RE.findall(claude_md_text):
        if _is_strict_semver(raw):
            valid[skill] = raw
        else:
            invalid.append((skill, raw))
    return valid, invalid


def _parse_suite_version(claude_md_text: str) -> tuple[str | None, str | None]:
    """Return (valid_version, invalid_raw_token).

    Exactly one of the two is non-None when a Suite version line is present.
    Both are None when the line is missing entirely.
    """
    m = SUITE_TOKEN_RE.search(claude_md_text)
    if m is None:
        return None, None
    raw = m.group(1)
    if _is_strict_semver(raw):
        return raw, None
    return None, raw


def _parse_changelog_latest(
    changelog_text: str,
) -> tuple[str | None, str | None]:
    """Return (valid_latest, invalid_raw_token).

    Walks `## [TOKEN]` headings in document order, skipping pseudo-entries
    like `[Unreleased]`. The first remaining heading is the latest release.
    If that heading's token is not a canonical version, it is returned as
    `invalid_raw_token` so the caller flags it instead of silently falling
    through to a predecessor and hiding the malformed release entry.
    """
    for m in CHANGELOG_TOKEN_RE.finditer(changelog_text):
        raw = m.group(1)
        if raw in NON_VERSION_CHANGELOG_TOKENS:
            continue
        if _is_strict_semver(raw):
            return raw, None
        return None, raw
    return None, None


def check(root: Path) -> list[str]:
    errors: list[str] = []

    claude_md = root / ".claude" / "CLAUDE.md"
    if not claude_md.is_file():
        errors.append(f"{claude_md}: not found")
        return errors
    claude_text = claude_md.read_text(encoding="utf-8")

    table_versions, invalid_table_rows = _parse_table_versions(claude_text)
    if not table_versions and not invalid_table_rows:
        errors.append(
            f"{claude_md}: Skills Overview table has no parseable "
            "`<skill>` vX.Y.Z rows"
        )
    for skill, raw in invalid_table_rows:
        errors.append(
            f"{claude_md}: table row {skill!r} has invalid version "
            f"token v{raw!r} (expected canonical N.N.N or N.N.N.N)"
        )

    suite_version, invalid_suite_token = _parse_suite_version(claude_text)
    if suite_version is None and invalid_suite_token is None:
        errors.append(
            f"{claude_md}: missing '**Suite version**: X.Y.Z' line"
        )
    elif invalid_suite_token is not None:
        errors.append(
            f"{claude_md}: Suite version token {invalid_suite_token!r} is "
            "not a canonical N.N.N or N.N.N.N version"
        )

    changelog = root / "CHANGELOG.md"
    if not changelog.is_file():
        errors.append(f"{changelog}: not found")
    else:
        latest, invalid_latest = _parse_changelog_latest(
            changelog.read_text(encoding="utf-8")
        )
        if latest is None and invalid_latest is None:
            errors.append(f"{changelog}: no '## [X.Y.Z]' entry found")
        elif invalid_latest is not None:
            errors.append(
                f"{changelog}: latest entry token {invalid_latest!r} is "
                "not a canonical N.N.N or N.N.N.N version"
            )
        elif suite_version is not None and latest != suite_version:
            errors.append(
                f"{claude_md}: Suite version {suite_version!r} does not match "
                f"CHANGELOG latest entry {latest!r}"
            )

    for skill_name, table_version in sorted(table_versions.items()):
        skill_md = root / skill_name / "SKILL.md"
        if not skill_md.is_file():
            errors.append(
                f"{claude_md}: table lists {skill_name!r} v{table_version} "
                f"but {skill_md} does not exist"
            )
            continue
        try:
            fm = parse_frontmatter(skill_md)
        except FrontmatterError as exc:
            errors.append(str(exc))
            continue
        if fm is None:
            errors.append(f"{skill_md}: missing YAML frontmatter")
            continue
        metadata = fm.get("metadata") or {}
        declared = metadata.get("version")
        if declared is None:
            errors.append(f"{skill_md}: metadata.version is missing")
            continue
        declared_str = str(declared)
        if declared_str != table_version:
            errors.append(
                f"{claude_md}: {skill_name!r} listed as v{table_version} but "
                f"{skill_md} metadata.version is {declared_str!r}"
            )

    if suite_version is not None:
        pipeline_in_table = table_versions.get(PIPELINE_SKILL_NAME)
        if pipeline_in_table is not None and pipeline_in_table != suite_version:
            errors.append(
                f"{claude_md}: {PIPELINE_SKILL_NAME} listed as "
                f"v{pipeline_in_table} but suite version is {suite_version!r} "
                "(pipeline tracks the suite release)"
            )

    # Invariant 4: plugin manifests track the suite version (outward-facing
    # package metadata). Only checked when a suite version is known.
    if suite_version is not None:
        errors.extend(_check_plugin_manifests(root, suite_version))
        # Invariant 5: README version badge tracks the suite version.
        errors.extend(_check_readme_badge(root, suite_version))
        # Invariant 6: docs/ must not cite a version above the suite version.
        errors.extend(_check_docs_versions(root, suite_version))

    # Invariant 7: en<->zh-TW version-bearing-heading parity (independent of
    # suite version; pairs each docs/*.md with its docs/*.zh-TW.md sibling).
    errors.extend(_check_zhtw_heading_parity(root))

    # Invariant 8: plugin.json "N-agent" description claim equals the tree's
    # unique *_agent.md count (independent of suite version).
    errors.extend(_check_agent_count_claim(root))

    return errors


def _check_plugin_manifests(root: Path, suite_version: str) -> list[str]:
    """Invariant 4: .claude-plugin/plugin.json "version" and every
    .claude-plugin/marketplace.json plugins[].version equal the suite version.
    Missing files / malformed JSON / missing version keys are surfaced, never
    crash (a release lint must report drift, not blow up on it)."""
    errors: list[str] = []

    plugin_json = root / ".claude-plugin" / "plugin.json"
    if not plugin_json.is_file():
        errors.append(f"{plugin_json}: not found")
    else:
        try:
            data = json.loads(plugin_json.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, ValueError) as exc:
            errors.append(f"{plugin_json}: invalid JSON ({exc})")
        else:
            v = data.get("version")
            if v is None:
                errors.append(f"{plugin_json}: missing 'version' key")
            elif str(v) != suite_version:
                errors.append(
                    f"{plugin_json}: version {str(v)!r} does not match suite "
                    f"version {suite_version!r}"
                )

    marketplace = root / ".claude-plugin" / "marketplace.json"
    if not marketplace.is_file():
        errors.append(f"{marketplace}: not found")
    else:
        try:
            data = json.loads(marketplace.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, ValueError) as exc:
            errors.append(f"{marketplace}: invalid JSON ({exc})")
        else:
            plugins = data.get("plugins")
            if not isinstance(plugins, list) or not plugins:
                errors.append(f"{marketplace}: 'plugins' is missing or empty")
            else:
                for i, entry in enumerate(plugins):
                    v = (entry or {}).get("version") if isinstance(entry, dict) else None
                    if v is None:
                        errors.append(
                            f"{marketplace}: plugins[{i}] missing 'version' key"
                        )
                    elif str(v) != suite_version:
                        errors.append(
                            f"{marketplace}: plugins[{i}] version {str(v)!r} does "
                            f"not match suite version {suite_version!r}"
                        )

    return errors


def _check_readme_badge(root: Path, suite_version: str) -> list[str]:
    """Invariant 5: README.md shields.io version badge equals the suite version.

    The badge is outward-facing — the first thing a reader sees. A v3.10.0
    release-doc pass can miss it the same way it missed the marketplace
    manifest (invariant 4). Missing file / no badge surfaced, never crash."""
    errors: list[str] = []
    readme = root / "README.md"
    if not readme.is_file():
        errors.append(f"{readme}: not found")
        return errors
    text = readme.read_text(encoding="utf-8")
    matches = README_BADGE_RE.findall(text)
    if not matches:
        errors.append(f"{readme}: no `badge/version-vX.Y.Z` version badge found")
        return errors
    for raw in matches:
        if raw != suite_version:
            errors.append(
                f"{readme}: version badge v{raw} does not match suite "
                f"version {suite_version!r}"
            )
    return errors


def _check_docs_versions(root: Path, suite_version: str) -> list[str]:
    """Invariant 6: no docs/*.md cites a version ABOVE the suite version.

    A doc that references a not-yet-released (or deleted) version is a forward
    reference that misleads readers. Equal-to-suite is fine (<=). Non-canonical
    tokens are surfaced, not silently dropped."""
    errors: list[str] = []
    docs = root / "docs"
    if not docs.is_dir():
        return errors  # docs/ optional; absence is not drift
    for md in sorted(docs.rglob("*.md")):
        # docs/superpowers/ holds skill working files (specs/plans) that
        # deliberately plan the NEXT release — forward references are their
        # job, not a published-doc drift. Invariant 6 gates published docs.
        if "superpowers" in md.relative_to(docs).parts:
            continue
        text = md.read_text(encoding="utf-8")
        for raw in DOCS_VERSION_RE.findall(text):
            if not _is_strict_semver(raw):
                continue  # 2-segment etc. — not a release token we gate on
            if not _version_le(raw, suite_version):
                errors.append(
                    f"{md}: cites v{raw} which is ABOVE suite version "
                    f"{suite_version!r} (forward/unknown reference)"
                )
    return errors


def _version_bearing_headings(text: str) -> Counter:
    """Count version tokens across H2s that carry a vX.Y.Z tag.

    Returns a multiset {version: count}. Comparison is by version token, not
    heading text, so an en heading and its zh-TW translation match despite
    different wording. A MULTISET (not a set/dict) is load-bearing: two H2s in
    one doc tagged the same version count as two, so a translator dropping one
    of a duplicated pair surfaces as a count mismatch (review finding — a
    {version: heading} dict silently collapsed duplicates and passed)."""
    out: Counter = Counter()
    for h in H2_RE.findall(text):
        m = H2_VERSION_RE.search(h)
        if m:
            out[m.group(1)] += 1
    return out


def _check_zhtw_heading_parity(root: Path) -> list[str]:
    """Invariant 7: every version-bearing H2 in docs/<name>.md has a matching
    version-bearing H2 in docs/<name>.zh-TW.md (same version), and vice versa.

    Plain (no-version) headings may differ freely — translation asymmetry is
    allowed; only version TAGS must stay in lockstep. Compares by version-token
    MULTISET, so wording differences don't false-flag but a dropped/added/
    drifted version tag (including one of a same-version pair) does."""
    errors: list[str] = []
    docs = root / "docs"
    if not docs.is_dir():
        return errors
    for zh in sorted(docs.rglob("*.zh-TW.md")):
        en = zh.with_name(zh.name.replace(".zh-TW.md", ".md"))
        if not en.is_file():
            errors.append(f"{zh}: no English sibling {en.name}")
            continue
        en_vers = _version_bearing_headings(en.read_text(encoding="utf-8"))
        zh_vers = _version_bearing_headings(zh.read_text(encoding="utf-8"))
        # Counter subtraction keeps only positive surpluses; doing it both ways
        # surfaces under- and over-translation, and a 2-vs-1 same-version
        # mismatch shows as a residual count of 1.
        for v, n in sorted((en_vers - zh_vers).items()):
            errors.append(
                f"{zh.name}: missing {n} version-bearing heading(s) for v{v} "
                f"present in {en.name}"
            )
        for v, n in sorted((zh_vers - en_vers).items()):
            errors.append(
                f"{zh.name}: has {n} heading(s) citing v{v} not present in "
                f"{en.name} — version drift"
            )
    return errors


def _check_agent_count_claim(root: Path) -> list[str]:
    """Invariant 8 (#414): when plugin.json's description advertises an
    "N-agent" count, N must equal the number of unique *_agent.md files in
    the tree. The plugin-root agents/ mirror dir is excluded — its files are
    byte-identical aliases of deep-research agents (real copies since #413,
    symlinks before; check_agents_mirror_sync.py pins the byte-equality), so
    counting them would double-count. resolve() additionally dedups any
    remaining symlink alias. Missing/malformed manifest or a description
    without a count claim is NOT an invariant-8 error — the manifest problems
    are invariant 4's to report, and the claim is optional (only a stated
    number must be true)."""
    plugin_json = root / ".claude-plugin" / "plugin.json"
    if not plugin_json.is_file():
        return []
    try:
        data = json.loads(plugin_json.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, ValueError):
        return []
    description = data.get("description")
    if not isinstance(description, str):
        return []
    m = AGENT_CLAIM_RE.search(description)
    if m is None:
        return []
    claimed = int(m.group(1))
    actual = len({
        p.resolve()
        for p in root.rglob("*_agent.md")
        if ".git" not in p.parts
        and p.relative_to(root).parts[0] != "agents"  # plugin-root mirror = aliases (#413)
    })
    if claimed != actual:
        return [
            f"{plugin_json}: description claims {claimed}-agent but the tree "
            f"has {actual} unique *_agent.md files (agents/ mirror aliases "
            f"excluded, symlinks deduplicated)"
        ]
    return []


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--path",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
    )
    args = parser.parse_args()

    errors = check(args.path)
    if errors:
        print("Version consistency check failed:")
        for err in errors:
            print(f"- {err}")
        return 1
    print("Version consistency check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
