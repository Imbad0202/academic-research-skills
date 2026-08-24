#!/usr/bin/env python3
"""Shared markdown rendering semantics for the defrift lints (#771).

Single authority for one question: what does GitHub render from this
markdown? Inline code spans render literally (a link inside backticks is
not a link) and an image `![alt](target)` renders no anchor, so both are
excluded from the rendered link grammar. Grammar hardened under the #757 /
#758 review rounds; consumers are check_control_availability.py,
check_data_flows.py, check_risk_register.py, check_spec_consistency.py, and
run_indirect_prompt_injection_probe.py.

No helper writes to the filesystem or assumes a particular repository layout.
Consumers supply every path and own their invariant-specific error wording.

Modeling boundary: deeper CommonMark laminations — blocks terminated by the
enclosing quote or list, comments opened inside list items, … — are
deliberately not modeled. The surfaces the lints read do not use them, and a
full markdown parser is out of proportion for a maintainer-slip guard.
"""
from __future__ import annotations

import re
from enum import Enum
from pathlib import Path

# [text](target) and [text](target "title") — the target is captured before
# an optional quoted title; a titled link must not silently fall out of the
# link-resolution invariants. (?<!\!) — an image renders no anchor.
_LINK_RE = re.compile(r"(?<!\!)\[[^\]]*\]\(\s*([^)\s]+)(?:\s+\"[^\"]*\")?\s*\)")

# Inline code spans render literally. Stripped AFTER the block-level passes
# (a fence's contents are gone by then, so a lone backtick inside a fence
# cannot open a phantom span).
_CODE_SPAN_RE = re.compile(r"`([^`\n]+)`")

_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
_QUOTE_PREFIX_RE = re.compile(r"^(\s{0,3}>\s?)+")
_HEADING_RE = re.compile(r"^#{1,6}\s+(.*)$", re.MULTILINE)
_FENCE_OPEN_RE = re.compile(r"`{3,}|~{3,}")

# Link targets that are not repo-relative paths: absolute schemes plus
# intra-document anchors.
NON_RELATIVE_LINK_PREFIXES = ("http://", "https://", "mailto:", "#")


class RelativeLinkFailure(str, Enum):
    """Closed failure vocabulary for a rendered repo-relative link."""

    ESCAPES_REPOSITORY = "escapes_repository"
    DOES_NOT_EXIST = "does_not_exist"
    ANCHOR_ON_NON_MARKDOWN = "anchor_on_non_markdown"
    ANCHOR_NOT_FOUND = "anchor_not_found"


def _strip_fenced_code(md_text: str) -> str:
    """Fenced code blocks render literally: a link or heading inside a
    ``` / ~~~ fence counts for nothing. Runs BEFORE the comment pass, so a
    `<!--` inside a fence stays literal text and cannot open a comment
    block."""
    kept: list[str] = []
    fence: str | None = None  # the opening run, e.g. "```" or "~~~~"
    for line in md_text.split("\n"):
        content = _QUOTE_PREFIX_RE.sub("", line).lstrip(" ")
        if fence is None:
            opener = _FENCE_OPEN_RE.match(content)
            if opener:
                fence = opener.group(0)
                continue
        else:
            # CommonMark: the closer is a run of the SAME character at least
            # as long as the opener, with nothing but whitespace after it —
            # so a ```` fence is not closed by a literal ``` example line.
            if re.match(rf"{re.escape(fence[0])}{{{len(fence)},}}\s*$", content):
                fence = None
            continue
        kept.append(line)
    return "\n".join(kept)


def _strip_html_comments(md_text: str) -> str:
    """Non-rendering markdown counts for nothing (neither satisfying a
    coverage invariant nor firing a resolution one).

    Two GFM behaviors matter here:
    - A line beginning with `<!--` (up to 3 leading spaces) opens a type-2
      HTML block that runs through the line containing `-->` — or to EOF if
      unclosed — and NOTHING on those lines renders as markdown, including
      text after the terminator on the closing line.
    - Elsewhere, an inline `<!-- ... -->` span is raw HTML; the surrounding
      text still renders.

    The line-start test looks through leading block-quote markers (`> `),
    since the same type-2 rule applies to block-quote content.
    """
    kept: list[str] = []
    lines = md_text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        content = _QUOTE_PREFIX_RE.sub("", line)
        stripped = content.lstrip(" ")
        indent = len(content) - len(stripped)
        if indent <= 3 and stripped.startswith("<!--"):
            while i < len(lines) and "-->" not in lines[i]:
                i += 1
            i += 1  # skip the closing line entirely (or run off EOF)
            continue
        kept.append(line)
        i += 1
    return _HTML_COMMENT_RE.sub("", "\n".join(kept))


def strip_non_rendering(md_text: str) -> str:
    """Fenced code first (its contents are literal), then HTML comments.
    Inline code spans are NOT stripped here: heading-slug extraction needs a
    heading's backticked words (GitHub slugs keep them), so span stripping is
    applied only where links are extracted (`extract_link_targets`)."""
    return _strip_html_comments(_strip_fenced_code(md_text))


def github_slug(heading: str) -> str:
    """GitHub's markdown heading -> anchor slug, for ASCII headings:
    lowercase, drop punctuation, spaces become hyphens (consecutive spaces
    produce consecutive hyphens, e.g. "CLI / IDE" -> "cli--ide")."""
    text = heading.strip().lower()
    # Strip markdown emphasis/backticks before slugging.
    text = re.sub(r"[*_`]", "", text)
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def heading_slugs(md_text: str) -> set[str]:
    """GitHub anchor slugs of every rendered heading in `md_text`."""
    return {
        github_slug(match.group(1))
        for match in _HEADING_RE.finditer(strip_non_rendering(md_text))
    }


def anchor_resolves(md_text: str, fragment: str) -> bool:
    """Whether ``fragment`` exactly names a rendered heading id.

    The fragment is already an id reference, not heading prose to slugify.
    """
    return fragment in heading_slugs(md_text)


def link_targets(text: str) -> list[str]:
    """Link targets in `text` AS GIVEN — no stripping passes are applied;
    callers choose which passes have already run."""
    return _LINK_RE.findall(text)


def code_spans(text: str) -> list[str]:
    """Inline code-span contents in `text` AS GIVEN."""
    return _CODE_SPAN_RE.findall(text)


def extract_link_targets(md_text: str) -> list[str]:
    """Targets of the RENDERED markdown links in `md_text`: block-level
    non-rendering stripped, then inline code spans, then the image-excluding
    link grammar."""
    return link_targets(_CODE_SPAN_RE.sub("", strip_non_rendering(md_text)))


def links_to(md_text: str, surface_dir: Path, target_abs: Path) -> bool:
    """True when `md_text` carries a rendered link whose destination,
    resolved relative to `surface_dir`, is exactly `target_abs`. The check
    is on the link DESTINATION — a link whose visible label keeps the
    filename but whose target points elsewhere must not pass."""
    for target in extract_link_targets(md_text):
        if target.startswith(NON_RELATIVE_LINK_PREFIXES):
            continue
        path_part = target.partition("#")[0]
        if path_part and (surface_dir / path_part).resolve() == target_abs:
            return True
    return False


def relative_link_failure(
    repo_root: Path,
    source_path: Path,
    target: str,
) -> RelativeLinkFailure | None:
    """Return why a repo-relative rendered link fails, or ``None``.

    This is the shared file/anchor-resolution ladder for consumers that need
    more than :func:`links_to`: a target must stay inside ``repo_root``, exist,
    and, when it has a fragment, point to a Markdown heading with that exact
    generated id.

    The fragment is deliberately compared *as authored* with the generated
    heading ids.  It is not run through :func:`github_slug`: browsers resolve
    a fragment against an existing id, and slugifying the fragment itself
    would make broken variants such as ``#Mixed-Case`` falsely satisfy the
    real ``mixed-case`` id.

    Absolute/web targets are outside this helper's contract; callers retain
    their existing policy for skipping them.
    """
    root_abs = repo_root.resolve()
    path_part, separator, fragment = target.partition("#")
    resolved = (
        source_path.resolve()
        if not path_part
        else (source_path.parent / path_part).resolve()
    )

    if not resolved.is_relative_to(root_abs):
        return RelativeLinkFailure.ESCAPES_REPOSITORY
    if not resolved.exists():
        return RelativeLinkFailure.DOES_NOT_EXIST

    # Preserve the existing intra-document `#` behavior: it names an empty
    # fragment and therefore has no matching heading.  A trailing `file.md#`
    # has historically remained a plain file link in these lints.
    checks_anchor = bool(fragment) or (bool(separator) and not path_part)
    if not checks_anchor:
        return None
    if resolved.suffix.lower() != ".md":
        return RelativeLinkFailure.ANCHOR_ON_NON_MARKDOWN
    if not anchor_resolves(resolved.read_text(encoding="utf-8"), fragment):
        return RelativeLinkFailure.ANCHOR_NOT_FOUND
    return None
