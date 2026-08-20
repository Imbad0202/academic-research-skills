"""Direct tests for the shared markdown grammar (#771).

The consumer lints' mutation suites pin their invariants end-to-end; this
suite pins the grammar itself once, so a grammar change is reasoned about
here rather than across three fixture repos.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from _markdown_lint_util import (
    extract_link_targets,
    github_slug,
    heading_slugs,
    links_to,
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
