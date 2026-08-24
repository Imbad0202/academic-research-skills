"""Direct tests for the shared markdown grammar (#771).

The consumer lints' mutation suites pin their invariants end-to-end; this
suite pins the grammar itself once, so a grammar change is reasoned about
here rather than across three fixture repos.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from _markdown_lint_util import (
    RelativeLinkFailure,
    anchor_resolves,
    extract_link_targets,
    github_slug,
    heading_slugs,
    links_to,
    relative_link_failure,
    strip_non_rendering,
)


@pytest.mark.parametrize(
    ("md_text", "expected"),
    [
        ("[label](docs/a.md)", ["docs/a.md"]),
        # Titled link: the target is captured, the title is not.
        ('[label](docs/a.md "the title")', ["docs/a.md"]),
        # An image renders no anchor.
        ("![alt](image.png)", []),
        # A link inside backticks renders literally.
        ("`[label](docs/a.md)`", []),
        # A link inside a fence renders literally.
        ("```\n[label](docs/a.md)\n```", []),
        # A four-backtick fence is not closed by a ``` example line.
        ("````\n```\n[label](docs/a.md)\n```\n````", []),
        # A type-2 HTML comment block swallows its lines.
        ("<!--\n[label](docs/a.md)\n-->", []),
        # An inline comment span is raw HTML; surrounding links render.
        ("<span><!-- x --></span> [label](docs/a.md)", ["docs/a.md"]),
    ],
)
def test_extract_link_targets(md_text: str, expected: list[str]) -> None:
    assert extract_link_targets(md_text) == expected


def test_heading_slugs_keeps_backticked_words() -> None:
    # GitHub slugs keep a heading's backticked words, so span stripping
    # must not apply to heading extraction.
    assert heading_slugs("## The `foo` flag") == {"the-foo-flag"}


def test_heading_inside_fence_is_not_a_heading() -> None:
    assert heading_slugs("```\n## fenced\n```") == set()


def test_anchor_resolves_exact_generated_id() -> None:
    text = "# Mixed Case\n"
    assert anchor_resolves(text, "mixed-case")
    assert not anchor_resolves(text, "Mixed-Case")


def test_github_slug_consecutive_hyphens() -> None:
    assert github_slug("CLI / IDE") == "cli--ide"


def test_strip_non_rendering_keeps_code_spans() -> None:
    assert strip_non_rendering("keep `this span`") == "keep `this span`"


def test_links_to_resolves_destination(tmp_path: Path) -> None:
    target = tmp_path / "docs" / "PAGE.md"
    target.parent.mkdir()
    target.write_text("# t", encoding="utf-8")
    assert links_to("[x](docs/PAGE.md)", tmp_path, target.resolve())
    # Label naming the file does not count when the target points elsewhere.
    assert not links_to("[docs/PAGE.md](docs/OTHER.md)", tmp_path, target.resolve())
    # Image form renders no anchor.
    assert not links_to("![x](docs/PAGE.md)", tmp_path, target.resolve())


@pytest.fixture()
def link_repo(tmp_path: Path) -> tuple[Path, Path]:
    source = tmp_path / "docs" / "SOURCE.md"
    source.parent.mkdir()
    source.write_text("# Source Heading\n", encoding="utf-8")
    (tmp_path / "docs" / "TARGET.md").write_text(
        "# Mixed Case\n", encoding="utf-8"
    )
    (tmp_path / "docs" / "data.json").write_text("{}\n", encoding="utf-8")
    return tmp_path, source


@pytest.mark.parametrize(
    ("target", "expected"),
    [
        ("TARGET.md#mixed-case", None),
        ("#source-heading", None),
        ("#", RelativeLinkFailure.ANCHOR_NOT_FOUND),
        ("TARGET.md#", None),
        ("MISSING.md", RelativeLinkFailure.DOES_NOT_EXIST),
        ("../../outside.md", RelativeLinkFailure.ESCAPES_REPOSITORY),
        (
            "data.json#mixed-case",
            RelativeLinkFailure.ANCHOR_ON_NON_MARKDOWN,
        ),
        ("TARGET.md#missing", RelativeLinkFailure.ANCHOR_NOT_FOUND),
    ],
)
def test_relative_link_failure_ladder(
    link_repo: tuple[Path, Path],
    target: str,
    expected: RelativeLinkFailure | None,
) -> None:
    root, source = link_repo
    assert relative_link_failure(root, source, target) is expected


def test_relative_link_fragment_is_an_exact_id_not_slug_input(
    link_repo: tuple[Path, Path],
) -> None:
    root, source = link_repo
    # Slugifying this fragment would turn it into the real `mixed-case` id
    # and silently accept a link whose authored fragment is case-wrong.
    assert relative_link_failure(
        root, source, "TARGET.md#Mixed-Case"
    ) is RelativeLinkFailure.ANCHOR_NOT_FOUND
