"""Mutation tests for check_skill_inventory_parity.py (#809).

A synthetic root carries two skills on all four surfaces. Each test breaks
exactly one surface in one direction and asserts the lint names it. The
real repository tree is checked last.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from tests.test_helpers import run_skill_linter, write_skill

from check_skill_inventory_parity import run_all_checks

SCRIPT = Path(__file__).resolve().parent / "check_skill_inventory_parity.py"
REPO_ROOT = Path(__file__).resolve().parent.parent
NAMES = ("alpha-skill", "beta-skill")


def _write_table(root: Path, names: tuple[str, ...]) -> None:
    rows = "\n".join(f"| `{n}` v1.0.0 | purpose | full |" for n in names)
    (root / ".claude").mkdir(exist_ok=True)
    (root / ".claude" / "CLAUDE.md").write_text(
        "# Test\n\n## Skills Overview\n\n"
        "| Skill | Purpose | Key Modes |\n|-------|---------|-----------|\n"
        f"{rows}\n\n## Routing Rules\n\n"
        "| `not-a-skill` v9.9.9 | a row outside the section | x |\n",
        encoding="utf-8",
    )


def _write_manifests(
    root: Path,
    names: tuple[str, ...],
    *,
    market_entries: list[str] | None = None,
    market_desc: str | None = None,
    market_top_desc: str | None = None,
    plugin_desc: str | None = None,
) -> None:
    (root / ".claude-plugin").mkdir(exist_ok=True)
    entries = market_entries if market_entries is not None else [f"./{n}" for n in names]
    market = {
        "name": "test",
        "description": market_top_desc if market_top_desc is not None else "test marketplace",
        "plugins": [
            {
                "name": "test",
                "description": market_desc if market_desc is not None else f"{len(names)} skills + modes",
                "skills": entries,
            }
        ],
    }
    (root / ".claude-plugin" / "marketplace.json").write_text(
        json.dumps(market, indent=2), encoding="utf-8"
    )
    plugin = {
        "name": "test",
        "description": plugin_desc if plugin_desc is not None else f"pipeline: {len(names)} skills, 9 modes",
    }
    (root / ".claude-plugin" / "plugin.json").write_text(
        json.dumps(plugin, indent=2), encoding="utf-8"
    )


def _write_symlinks(root: Path, names: tuple[str, ...]) -> None:
    skills = root / "skills"
    skills.mkdir(exist_ok=True)
    for n in names:
        os.symlink(f"../{n}", skills / n)


def _write_registry(root: Path, text: str) -> None:
    (root / "MODE_REGISTRY.md").write_text(text, encoding="utf-8")


def _build_root(root: Path, names: tuple[str, ...] = NAMES) -> None:
    for n in names:
        write_skill(root, n, f"name: {n}\ndescription: t\nmetadata:\n  version: '1'\n")
    _write_symlinks(root, names)
    _write_table(root, names)
    _write_manifests(root, names)
    _write_registry(root, f"# Modes\n\n**9 modes** across {len(names)} skills.\n")


def _violations(root: Path) -> list[str]:
    return run_all_checks(root)


def _assert_single(violations: list[str], needle: str) -> None:
    assert len(violations) == 1, violations
    assert needle in violations[0], violations


# ---- baseline ---------------------------------------------------------------

def test_consistent_root_passes(tmp_path: Path) -> None:
    _build_root(tmp_path)
    assert _violations(tmp_path) == []


def test_cli_exit_codes(tmp_path: Path) -> None:
    _build_root(tmp_path)
    ok = run_skill_linter(SCRIPT, tmp_path)
    assert ok.returncode == 0, ok.stdout + ok.stderr
    assert "OK:" in ok.stdout
    (tmp_path / "skills" / NAMES[0]).unlink()
    bad = run_skill_linter(SCRIPT, tmp_path)
    assert bad.returncode == 1
    assert "ERROR:" in bad.stdout
    assert "1 violation(s) found." in bad.stderr


def test_empty_root_is_a_violation(tmp_path: Path) -> None:
    _assert_single(_violations(tmp_path), "no top-level <name>/SKILL.md found")


# ---- surface B: skills/ symlinks -------------------------------------------

def test_unpackaged_skill_dir_fails(tmp_path: Path) -> None:
    """A fifth directory on disk that nothing else knows about (the #807 shape)."""
    _build_root(tmp_path)
    write_skill(tmp_path, "gamma-skill", "name: gamma-skill\n")
    v = _violations(tmp_path)
    assert len(v) == 6, v
    missing = [line for line in v if "'gamma-skill' exists on disk" in line]
    assert len(missing) == 3, v
    assert any("skills/ symlinks" in line for line in missing)
    assert any("Skills Overview table" in line for line in missing)
    assert any("marketplace.json plugins[].skills" in line for line in missing)
    # the "2 skills" claims are now stale on every count surface
    counts = [line for line in v if "claims '2 skills' but 3" in line]
    assert len(counts) == 3, v  # marketplace, plugin.json, MODE_REGISTRY.md


def test_missing_symlink_fails(tmp_path: Path) -> None:
    _build_root(tmp_path)
    (tmp_path / "skills" / NAMES[1]).unlink()
    _assert_single(_violations(tmp_path), f"'{NAMES[1]}' exists on disk")


def test_extra_symlink_without_dir_fails(tmp_path: Path) -> None:
    _build_root(tmp_path)
    os.symlink("../ghost", tmp_path / "skills" / "ghost")
    v = _violations(tmp_path)
    assert len(v) == 2, v
    assert any("dangling symlink" in line for line in v)
    assert any("lists skill 'ghost' but no top-level" in line for line in v)


def test_symlink_to_wrong_target_fails(tmp_path: Path) -> None:
    _build_root(tmp_path)
    link = tmp_path / "skills" / NAMES[0]
    link.unlink()
    os.symlink(f"../{NAMES[1]}", link)
    _assert_single(_violations(tmp_path), "symlink resolves to")


def test_real_directory_instead_of_symlink_fails(tmp_path: Path) -> None:
    _build_root(tmp_path)
    link = tmp_path / "skills" / NAMES[0]
    link.unlink()
    link.mkdir()
    _assert_single(_violations(tmp_path), "must be a symlink")


def test_missing_skills_dir_fails(tmp_path: Path) -> None:
    _build_root(tmp_path)
    for n in NAMES:
        (tmp_path / "skills" / n).unlink()
    (tmp_path / "skills").rmdir()
    v = _violations(tmp_path)
    assert any("directory is missing" in line for line in v)
    assert sum("not listed in skills/ symlinks" in line for line in v) == len(NAMES)


# ---- surface C: CLAUDE.md table --------------------------------------------

def test_missing_table_row_fails(tmp_path: Path) -> None:
    _build_root(tmp_path)
    _write_table(tmp_path, NAMES[:1])
    _assert_single(_violations(tmp_path), f"'{NAMES[1]}' exists on disk")


def test_extra_table_row_fails(tmp_path: Path) -> None:
    _build_root(tmp_path)
    _write_table(tmp_path, NAMES + ("stale-skill",))
    _assert_single(_violations(tmp_path), "lists skill 'stale-skill' but no top-level")


def test_rows_outside_section_are_ignored(tmp_path: Path) -> None:
    """The fixture table carries a `not-a-skill` row under a later heading."""
    _build_root(tmp_path)
    assert _violations(tmp_path) == []


def _replace_alpha_row(root: Path, row: str) -> None:
    md = root / ".claude" / "CLAUDE.md"
    text = md.read_text(encoding="utf-8")
    md.write_text(text.replace("| `alpha-skill` v1.0.0 | purpose | full |", row), encoding="utf-8")


@pytest.mark.parametrize("row", [
    "| `alpha-skill` | no version at all | full |",
    "| `alpha-skill` 1.0.0 | version without v | full |",
])
def test_row_without_version_token_fails(tmp_path: Path, row: str) -> None:
    """A row the version lint would skip is still counted as listed AND reported."""
    _build_root(tmp_path)
    _replace_alpha_row(tmp_path, row)
    _assert_single(_violations(tmp_path), "row for 'alpha-skill' lacks a 'vX.Y.Z' token")


@pytest.mark.parametrize("name", ["Ghost-Skill", "ghost_skill", "ghost skill", "ghost.skill"])
def test_non_canonical_row_name_is_reported(tmp_path: Path, name: str) -> None:
    """A stale advertised row with a non-canonical name must not be invisible."""
    _build_root(tmp_path)
    md = tmp_path / ".claude" / "CLAUDE.md"
    text = md.read_text(encoding="utf-8").replace(
        "| `beta-skill` v1.0.0 | purpose | full |",
        f"| `beta-skill` v1.0.0 | purpose | full |\n| `{name}` v1.0.0 | stale | x |",
    )
    md.write_text(text, encoding="utf-8")
    _assert_single(_violations(tmp_path), f"row names {name!r}, which is not a canonical")


@pytest.mark.parametrize("row", [
    "| ghost-skill v1.0.0 | no backticks | x |",
    "| **ghost-skill** v1.0.0 | bold instead | x |",
    "| | empty first cell | x |",
])
def test_data_row_without_backticked_name_is_reported(tmp_path: Path, row: str) -> None:
    _build_root(tmp_path)
    md = tmp_path / ".claude" / "CLAUDE.md"
    text = md.read_text(encoding="utf-8").replace(
        "| `beta-skill` v1.0.0 | purpose | full |\n",
        f"| `beta-skill` v1.0.0 | purpose | full |\n{row}\n", 1)
    md.write_text(text, encoding="utf-8")
    _assert_single(_violations(tmp_path), "has no backticked skill name in its first cell")


@pytest.mark.parametrize("separator", ["|-------|---------|-----------|", "|:--|:-:|--:|", "| --- | --- | --- |"])
def test_header_and_separator_rows_are_not_data_rows(tmp_path: Path, separator: str) -> None:
    _build_root(tmp_path)
    md = tmp_path / ".claude" / "CLAUDE.md"
    md.write_text(md.read_text(encoding="utf-8").replace("|-------|---------|-----------|", separator), encoding="utf-8")
    assert _violations(tmp_path) == []


@pytest.mark.parametrize("mutation", ["drop_separator", "drop_header_and_separator"])
def test_table_without_separator_is_not_a_table(tmp_path: Path, mutation: str) -> None:
    _build_root(tmp_path)
    md = tmp_path / ".claude" / "CLAUDE.md"
    text = md.read_text(encoding="utf-8").replace("|-------|---------|-----------|\n", "", 1)
    if mutation == "drop_header_and_separator":
        text = text.replace("| Skill | Purpose | Key Modes |\n", "", 1)
    md.write_text(text, encoding="utf-8")
    v = _violations(tmp_path)
    assert any("is not followed by a GFM table" in line for line in v), v


@pytest.mark.parametrize("separator", ["|---|", "|---|---|", "|---|---|---|---|"])
def test_separator_width_must_match_header(tmp_path: Path, separator: str) -> None:
    _build_root(tmp_path)
    md = tmp_path / ".claude" / "CLAUDE.md"
    md.write_text(md.read_text(encoding="utf-8").replace("|-------|---------|-----------|", separator), encoding="utf-8")
    v = _violations(tmp_path)
    assert any("GFM requires them equal" in line for line in v), v


def test_escaped_pipe_in_header_is_one_cell(tmp_path: Path) -> None:
    _build_root(tmp_path)
    md = tmp_path / ".claude" / "CLAUDE.md"
    md.write_text(md.read_text(encoding="utf-8").replace("| Skill | Purpose | Key Modes |", "| Skill | Purpose \\| Role | Key Modes |"), encoding="utf-8")
    assert _violations(tmp_path) == []


def test_non_semver_version_token_is_left_to_the_version_lint(tmp_path: Path) -> None:
    """`vNOPE` satisfies the shared FULL grammar; check_version_consistency.py
    rejects it as non-semver, so parity stays silent by design."""
    _build_root(tmp_path)
    _replace_alpha_row(tmp_path, "| `alpha-skill` vNOPE | placeholder | full |")
    assert _violations(tmp_path) == []


def test_missing_section_fails(tmp_path: Path) -> None:
    _build_root(tmp_path)
    (tmp_path / ".claude" / "CLAUDE.md").write_text("# nothing\n", encoding="utf-8")
    v = _violations(tmp_path)
    assert any("H2 is missing" in line for line in v)


def test_demoted_heading_is_not_the_section(tmp_path: Path) -> None:
    _build_root(tmp_path)
    md = tmp_path / ".claude" / "CLAUDE.md"
    md.write_text(md.read_text(encoding="utf-8").replace("## Skills Overview", "### Skills Overview"), encoding="utf-8")
    v = _violations(tmp_path)
    assert any("H2 is missing" in line for line in v), v


def test_fenced_heading_copy_does_not_bind(tmp_path: Path) -> None:
    """A fenced example carrying the heading + a ghost row sits BEFORE the real
    section; parity must bind to the real H2 and ignore the ghost."""
    _build_root(tmp_path)
    md = tmp_path / ".claude" / "CLAUDE.md"
    fenced = "```markdown\n## Skills Overview\n\n| `ghost` v9.9.9 | x | y |\n```\n\n"
    md.write_text(md.read_text(encoding="utf-8").replace("## Skills Overview", fenced + "## Skills Overview", 1), encoding="utf-8")
    assert _violations(tmp_path) == []


@pytest.mark.parametrize("trailer", [
    "\n| Other | Table |\n|---|---|\n| `ghost` v1.0.0 | second table |\n",
    "\n```\n| `ghost` v1.0.0 | fenced sample |\n```\n",
    "\nProse mentioning `ghost` v1.0.0 | in a pipe-free line.\n",
])
def test_only_the_first_table_after_the_heading_counts(tmp_path: Path, trailer: str) -> None:
    _build_root(tmp_path)
    md = tmp_path / ".claude" / "CLAUDE.md"
    text = md.read_text(encoding="utf-8").replace("| `beta-skill` v1.0.0 | purpose | full |\n",
                                                   "| `beta-skill` v1.0.0 | purpose | full |\n" + trailer, 1)
    md.write_text(text, encoding="utf-8")
    assert _violations(tmp_path) == []


def test_skill_only_in_a_second_table_is_not_listed(tmp_path: Path) -> None:
    _build_root(tmp_path)
    md = tmp_path / ".claude" / "CLAUDE.md"
    text = md.read_text(encoding="utf-8").replace(
        "| `beta-skill` v1.0.0 | purpose | full |\n",
        "\n| Other | Table |\n|---|---|\n| `beta-skill` v1.0.0 | moved here |\n", 1)
    md.write_text(text, encoding="utf-8")
    _assert_single(_violations(tmp_path), "'beta-skill' exists on disk")


def test_missing_claude_md_fails(tmp_path: Path) -> None:
    _build_root(tmp_path)
    (tmp_path / ".claude" / "CLAUDE.md").unlink()
    v = _violations(tmp_path)
    assert any("CLAUDE.md: file is missing" in line for line in v)


# ---- surface D: marketplace.json -------------------------------------------

def test_missing_manifest_entry_fails(tmp_path: Path) -> None:
    _build_root(tmp_path)
    _write_manifests(tmp_path, NAMES, market_entries=[f"./{NAMES[0]}"])
    _assert_single(_violations(tmp_path), f"'{NAMES[1]}' exists on disk")


def test_extra_manifest_entry_fails(tmp_path: Path) -> None:
    _build_root(tmp_path)
    _write_manifests(tmp_path, NAMES, market_entries=[f"./{n}" for n in NAMES] + ["./stale"])
    _assert_single(_violations(tmp_path), "lists skill 'stale' but no top-level")


@pytest.mark.parametrize("bad", ["alpha-skill", "skills/alpha-skill", "./Alpha", "./a/b", 7, "./alpha-skill\n", "./alpha-skill "])
def test_malformed_manifest_entry_fails(tmp_path: Path, bad) -> None:
    _build_root(tmp_path)
    _write_manifests(tmp_path, NAMES, market_entries=[bad, f"./{NAMES[1]}"])
    v = _violations(tmp_path)
    assert any("must be './<name>'" in line for line in v), v
    # the malformed entry does not count as listing alpha-skill
    assert any(f"'{NAMES[0]}' exists on disk" in line for line in v), v


def test_invalid_manifest_json_fails(tmp_path: Path) -> None:
    _build_root(tmp_path)
    (tmp_path / ".claude-plugin" / "marketplace.json").write_text("{", encoding="utf-8")
    v = _violations(tmp_path)
    assert any("invalid JSON" in line for line in v)


def test_missing_marketplace_fails(tmp_path: Path) -> None:
    _build_root(tmp_path)
    (tmp_path / ".claude-plugin" / "marketplace.json").unlink()
    v = _violations(tmp_path)
    assert any("marketplace.json: file is missing" in line for line in v)


# ---- count claims -----------------------------------------------------------

def test_stale_marketplace_count_fails(tmp_path: Path) -> None:
    _build_root(tmp_path)
    _write_manifests(tmp_path, NAMES, market_desc="4 skills + 27 modes")
    _assert_single(_violations(tmp_path), "marketplace.json description: claims '4 skills'")


def test_stale_marketplace_top_level_count_fails(tmp_path: Path) -> None:
    _build_root(tmp_path)
    _write_manifests(tmp_path, NAMES, market_top_desc="A marketplace of 3 skills")
    _assert_single(_violations(tmp_path), "marketplace.json description: claims '3 skills'")


def test_stale_plugin_count_fails(tmp_path: Path) -> None:
    _build_root(tmp_path)
    _write_manifests(tmp_path, NAMES, plugin_desc="4 skills, 27 modes")
    _assert_single(_violations(tmp_path), "plugin.json description: claims '4 skills'")


@pytest.mark.parametrize("desc", ["4 Skills + 27 modes", "4 SKILLS"])
def test_count_claim_is_case_insensitive(tmp_path: Path, desc: str) -> None:
    _build_root(tmp_path)
    _write_manifests(tmp_path, NAMES, plugin_desc=desc)
    _assert_single(_violations(tmp_path), "plugin.json description: claims")


def test_description_without_count_makes_no_claim(tmp_path: Path) -> None:
    _build_root(tmp_path)
    _write_manifests(tmp_path, NAMES, market_desc="research skills for Claude Code", plugin_desc="40 skillsets")
    assert _violations(tmp_path) == []


def test_stale_mode_registry_count_fails(tmp_path: Path) -> None:
    _build_root(tmp_path)
    _write_registry(tmp_path, "**27 modes** across 4 skills.\n")
    _assert_single(_violations(tmp_path), "MODE_REGISTRY.md: claims '4 skills'")


def test_missing_mode_registry_fails(tmp_path: Path) -> None:
    _build_root(tmp_path)
    (tmp_path / "MODE_REGISTRY.md").unlink()
    _assert_single(_violations(tmp_path), "MODE_REGISTRY.md: file is missing")


def test_missing_plugin_json_fails(tmp_path: Path) -> None:
    _build_root(tmp_path)
    (tmp_path / ".claude-plugin" / "plugin.json").unlink()
    _assert_single(_violations(tmp_path), "plugin.json: file is missing")


# ---- real tree --------------------------------------------------------------

def test_real_tree_passes() -> None:
    assert run_all_checks(REPO_ROOT) == []
