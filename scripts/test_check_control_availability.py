"""Mutation tests for check_control_availability.py (#757).

Strategy: copy the real surfaces into a tmp repo root, verify the baseline
passes, then apply one mutation per test and assert the intended invariant
(and only that invariant class) fires.
"""
from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from check_control_availability import (
    DOC_RELPATH,
    SETUP_RELPATH,
    github_slug,
    run_all_checks,
)

REPO_ROOT = Path(__file__).resolve().parent.parent

# Every file the doc's relative links may touch, plus the inbound-link
# surfaces. Kept explicit so a test-fixture gap fails loudly here rather
# than passing vacuously.
_MIRRORED_FILES = (
    "docs/CONTROL_AVAILABILITY.md",
    "docs/SETUP.md",
    "docs/ARCHITECTURE.md",
    "README.md",
    "audits/iso42001-spirit-gap-assessment-2026-08-17.md",
    "pi/README.md",
    "shared/cross_model_verification.md",
    "shared/contracts/degradation_registry.json",
)


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    for rel in _MIRRORED_FILES:
        src = REPO_ROOT / rel
        dst = tmp_path / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
    return tmp_path


def _mutate(root: Path, rel: str, old: str, new: str) -> None:
    path = root / rel
    text = path.read_text(encoding="utf-8")
    assert old in text, f"mutation anchor not found in {rel}: {old!r}"
    path.write_text(text.replace(old, new), encoding="utf-8")


def test_baseline_passes(repo: Path) -> None:
    assert run_all_checks(repo) == []


def test_missing_doc_is_single_fatal_error(repo: Path) -> None:
    (repo / DOC_RELPATH).unlink()
    errors = run_all_checks(repo)
    assert len(errors) == 1
    assert "missing" in errors[0]


def test_ca1_dead_file_link_fires(repo: Path) -> None:
    _mutate(
        repo,
        "docs/CONTROL_AVAILABILITY.md",
        "../pi/README.md",
        "../pi/NO_SUCH_FILE.md",
    )
    errors = run_all_checks(repo)
    assert any("CA-1" in e and "does not exist" in e for e in errors)


def test_ca1_renamed_setup_heading_fires(repo: Path) -> None:
    # Retitling a SETUP method heading breaks the doc's deep anchor (CA-1)
    # and removes the slug the doc links (CA-2) — the exact silent-404 drift
    # class the lint exists for. Both invariants must fire.
    _mutate(
        repo,
        str(SETUP_RELPATH),
        "### Method 5: Claude Science import (v3.14.0+)",
        "### Method 5: Claude Science import (v9.99.0+)",
    )
    errors = run_all_checks(repo)
    assert any("CA-1" in e and "anchor" in e for e in errors)
    assert any("CA-2" in e for e in errors)


def test_ca1_broken_intra_doc_anchor_fires(repo: Path) -> None:
    _mutate(
        repo,
        "docs/CONTROL_AVAILABILITY.md",
        "(#environment-degradations-within-a-channel)",
        "(#environment-degradations-nope)",
    )
    errors = run_all_checks(repo)
    assert any("CA-1" in e and "intra-doc" in e for e in errors)


def test_ca1_case_wrong_fragment_is_not_re_slugified(repo: Path) -> None:
    target = repo / "docs/CASE_TARGET.md"
    target.write_text("# Mixed Case\n", encoding="utf-8")
    doc = repo / DOC_RELPATH
    doc.write_text(
        doc.read_text(encoding="utf-8")
        + "\n[case-wrong](CASE_TARGET.md#Mixed-Case)\n",
        encoding="utf-8",
    )

    errors = run_all_checks(repo)

    assert any("CA-1" in e and "Mixed-Case" in e for e in errors)


def test_ca2_new_setup_method_fires(repo: Path) -> None:
    setup = repo / SETUP_RELPATH
    setup.write_text(
        setup.read_text(encoding="utf-8")
        + "\n### Method 6: Hypothetical Future Channel\n\nBody.\n",
        encoding="utf-8",
    )
    errors = run_all_checks(repo)
    assert any("CA-2" in e and "Method 6" in e for e in errors)
    assert not any("CA-1" in e for e in errors)


def test_ca3_readme_link_removed_fires(repo: Path) -> None:
    _mutate(
        repo,
        "README.md",
        "CONTROL_AVAILABILITY.md",
        "CONTROL_AVAILABILITY_GONE.md",
    )
    # Replace ALL occurrences so no link survives.
    readme = repo / "README.md"
    assert "CONTROL_AVAILABILITY.md" not in readme.read_text(encoding="utf-8")
    errors = run_all_checks(repo)
    assert any("CA-3" in e and "README.md" in e for e in errors)


def test_ca3_setup_link_removed_fires(repo: Path) -> None:
    setup = repo / SETUP_RELPATH
    text = setup.read_text(encoding="utf-8")
    setup.write_text(
        text.replace("CONTROL_AVAILABILITY.md", "CONTROL_AVAILABILITY_X.md"),
        encoding="utf-8",
    )
    errors = run_all_checks(repo)
    assert any("CA-3" in e and "SETUP.md" in e for e in errors)


def test_ca1_titled_dead_link_fires(repo: Path) -> None:
    # A link with an optional quoted title must not fall out of the link
    # grammar and silently skip CA-1 (codex R2 finding).
    doc = repo / DOC_RELPATH
    doc.write_text(
        doc.read_text(encoding="utf-8")
        + '\nSee [dead](NO_SUCH_FILE.md "optional title").\n',
        encoding="utf-8",
    )
    errors = run_all_checks(repo)
    assert any("CA-1" in e and "NO_SUCH_FILE.md" in e for e in errors)


def test_ca2_same_slug_in_copied_file_does_not_satisfy(repo: Path) -> None:
    # Retargeting a method link at a copy of SETUP that carries the same
    # heading must fail CA-2: coverage counts only links whose destination
    # IS docs/SETUP.md (codex R2 finding).
    shutil.copyfile(repo / SETUP_RELPATH, repo / "docs/SETUP_COPY.md")
    _mutate(
        repo,
        "docs/CONTROL_AVAILABILITY.md",
        "SETUP.md#method-5-claude-science-import-v3140",
        "SETUP_COPY.md#method-5-claude-science-import-v3140",
    )
    errors = run_all_checks(repo)
    assert any("CA-2" in e and "Method 5" in e for e in errors)
    assert not any("CA-1" in e for e in errors)


def test_ca3_label_keeps_filename_but_target_moves_fires(repo: Path) -> None:
    # The visible label retaining the filename must not satisfy CA-3; only
    # the resolved link DESTINATION counts (codex R2 finding).
    readme = repo / "README.md"
    text = readme.read_text(encoding="utf-8")
    old = "[docs/CONTROL_AVAILABILITY.md](docs/CONTROL_AVAILABILITY.md)"
    assert old in text
    readme.write_text(
        text.replace(
            old,
            "[docs/CONTROL_AVAILABILITY.md](docs/CONTROL_AVAILABILITY_GONE.md)",
        ),
        encoding="utf-8",
    )
    errors = run_all_checks(repo)
    assert any("CA-3" in e and "README.md" in e for e in errors)


def test_ca3_commented_out_inbound_link_fires(repo: Path) -> None:
    # A link surviving only inside an HTML comment does not render and must
    # not satisfy CA-3 (codex R3 finding).
    readme = repo / "README.md"
    text = readme.read_text(encoding="utf-8")
    old = "[docs/CONTROL_AVAILABILITY.md](docs/CONTROL_AVAILABILITY.md)"
    assert old in text
    readme.write_text(
        text.replace(old, f"<!-- {old} -->"), encoding="utf-8"
    )
    errors = run_all_checks(repo)
    assert any("CA-3" in e and "README.md" in e for e in errors)


def test_ca1_commented_out_dead_link_does_not_fire(repo: Path) -> None:
    # Symmetry: commented-out markdown counts for nothing, so a dead link
    # inside a comment must not fire CA-1 either.
    doc = repo / DOC_RELPATH
    doc.write_text(
        doc.read_text(encoding="utf-8")
        + "\n<!-- [dead](NO_SUCH_FILE.md) -->\n",
        encoding="utf-8",
    )
    assert run_all_checks(repo) == []


def test_ca3_html_block_line_does_not_render_link(repo: Path) -> None:
    # GFM type-2 HTML block: a LINE BEGINNING with `<!--` stays raw HTML
    # through the `-->` line INCLUDING trailing text after the terminator,
    # so a link there does not render and must not satisfy CA-3 (codex R4
    # finding). The whole link-carrying line is replaced so the mutated
    # line starts with `<!--`.
    readme = repo / "README.md"
    link = "[docs/CONTROL_AVAILABILITY.md](docs/CONTROL_AVAILABILITY.md)"
    lines = readme.read_text(encoding="utf-8").split("\n")
    idx = next(i for i, line in enumerate(lines) if link in line)
    lines[idx] = f"<!-- note --> {link}"
    readme.write_text("\n".join(lines), encoding="utf-8")
    errors = run_all_checks(repo)
    assert any("CA-3" in e and "README.md" in e for e in errors)


def test_ca3_inline_comment_before_link_still_renders(repo: Path) -> None:
    # Symmetry: when the line does NOT begin with `<!--`, an inline comment
    # span before the link is just raw inline HTML — the link still renders,
    # so CA-3 must stay satisfied.
    readme = repo / "README.md"
    text = readme.read_text(encoding="utf-8")
    old = "[docs/CONTROL_AVAILABILITY.md](docs/CONTROL_AVAILABILITY.md)"
    assert old in text
    readme.write_text(
        text.replace(old, f"<!-- note --> {old}"), encoding="utf-8"
    )
    assert run_all_checks(repo) == []


def test_ca1_unclosed_comment_swallows_rest_of_document(repo: Path) -> None:
    # An unclosed `<!--` extends the HTML block to EOF: a dead link after it
    # never renders, so CA-1 must stay quiet.
    doc = repo / DOC_RELPATH
    doc.write_text(
        doc.read_text(encoding="utf-8")
        + "\n<!--\n[dead](NO_SUCH_FILE.md)\n",
        encoding="utf-8",
    )
    assert run_all_checks(repo) == []


def test_ca3_blockquoted_html_block_line_fires(repo: Path) -> None:
    # `> <!-- note --> [link]` — the type-2 HTML-block rule applies to
    # block-quote content too, so the link does not render (codex R5
    # finding). The stripper must look through leading `>` markers.
    readme = repo / "README.md"
    link = "[docs/CONTROL_AVAILABILITY.md](docs/CONTROL_AVAILABILITY.md)"
    lines = readme.read_text(encoding="utf-8").split("\n")
    idx = next(i for i, line in enumerate(lines) if link in line)
    lines[idx] = f"> <!-- note --> {link}"
    readme.write_text("\n".join(lines), encoding="utf-8")
    errors = run_all_checks(repo)
    assert any("CA-3" in e and "README.md" in e for e in errors)


def test_ca1_link_escaping_repo_fires_even_if_target_exists(repo: Path) -> None:
    # An over-deep `../..` slip resolving to an EXISTING host file must not
    # pass CA-1: containment under the repo root is part of the invariant
    # (codex R6 finding).
    outside = repo.parent / "outside_target.md"
    outside.write_text("# Outside\n", encoding="utf-8")
    doc = repo / DOC_RELPATH
    doc.write_text(
        doc.read_text(encoding="utf-8")
        + "\nSee [escapee](../../outside_target.md).\n",
        encoding="utf-8",
    )
    errors = run_all_checks(repo)
    assert any("CA-1" in e and "escapes the repository" in e for e in errors)


def test_ca3_link_inside_code_fence_fires(repo: Path) -> None:
    # A link surviving only inside a ``` fence renders literally, not as a
    # link, so CA-3 must fire (codex R7 finding).
    readme = repo / "README.md"
    link = "[docs/CONTROL_AVAILABILITY.md](docs/CONTROL_AVAILABILITY.md)"
    lines = readme.read_text(encoding="utf-8").split("\n")
    idx = next(i for i, line in enumerate(lines) if link in line)
    lines[idx] = f"```text\n{link}\n```"
    readme.write_text("\n".join(lines), encoding="utf-8")
    errors = run_all_checks(repo)
    assert any("CA-3" in e and "README.md" in e for e in errors)


def test_ca2_method_heading_inside_fence_not_counted(repo: Path) -> None:
    # A sample `### Method` heading inside a SETUP code fence does not
    # render as a heading and must not demand CA-2 coverage.
    setup = repo / SETUP_RELPATH
    setup.write_text(
        setup.read_text(encoding="utf-8")
        + "\n```markdown\n### Method 9: Sample In A Fence\n```\n",
        encoding="utf-8",
    )
    assert run_all_checks(repo) == []


def test_ca3_link_inside_four_backtick_fence_fires(repo: Path) -> None:
    # A four-backtick fence demonstrating a triple-backtick block is closed
    # only by a run of >= 4 backticks; the inner triple backticks must not
    # end it, so a link inside stays literal and CA-3 fires (codex R8
    # finding).
    readme = repo / "README.md"
    link = "[docs/CONTROL_AVAILABILITY.md](docs/CONTROL_AVAILABILITY.md)"
    lines = readme.read_text(encoding="utf-8").split("\n")
    idx = next(i for i, line in enumerate(lines) if link in line)
    lines[idx] = f"````markdown\n```\n{link}\n```\n````"
    readme.write_text("\n".join(lines), encoding="utf-8")
    errors = run_all_checks(repo)
    assert any("CA-3" in e and "README.md" in e for e in errors)


def test_slug_matches_github_for_punctuated_heading() -> None:
    heading = (
        "Method 0: Claude Code Plugin (v3.7.0+, recommended for "
        "Claude Code CLI / IDE users)"
    )
    assert github_slug(heading) == (
        "method-0-claude-code-plugin-v370-recommended-for-"
        "claude-code-cli--ide-users"
    )


def test_image_form_of_inbound_link_does_not_satisfy_ca3(repo: Path) -> None:
    # #771 shared-grammar alignment: an image pointing at the doc renders no
    # anchor, so it must not satisfy the README discoverability invariant.
    _mutate(
        repo,
        "README.md",
        "[docs/CONTROL_AVAILABILITY.md](docs/CONTROL_AVAILABILITY.md)",
        "![docs/CONTROL_AVAILABILITY.md](docs/CONTROL_AVAILABILITY.md)",
    )
    errors = run_all_checks(repo)
    assert any("CA-3" in e and "README.md" in e for e in errors)
