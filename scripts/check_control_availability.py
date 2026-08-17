#!/usr/bin/env python3
"""Defrift lint for docs/CONTROL_AVAILABILITY.md (#757).

The control-availability matrix is a hand-maintained claim-adjudication
surface: users consult it to decide whether an integrity claim ("write-scope
guard", "tools allowlist", "mandatory checkpoints") holds in their install
channel. Its whole value is its pointers, so this lint pins exactly three
drift classes and deliberately nothing else — cell semantics (Active /
Conditional / Absent) stay owned by code review, mirroring
check_degradation_registry.py's index-not-author posture:

  CA-1  Every relative markdown link in the doc resolves: the linked file
        exists, and any anchor fragment (into docs/SETUP.md or intra-doc)
        matches a GitHub-slugified heading in the target file. This is the
        live drift class: several channel links point into version-tokened
        SETUP headings that a release retitle would silently 404.
  CA-2  The channel inventory cannot silently go stale: every `### Method`
        heading in docs/SETUP.md must be reachable from the doc via a link
        whose fragment is that heading's slug. Satisfiable form on purpose —
        the matrix may collapse methods into one channel or add non-SETUP
        channels (Pi), but a newly documented SETUP method must appear.
  CA-3  The doc stays discoverable: README.md and docs/SETUP.md each carry at
        least one link to docs/CONTROL_AVAILABILITY.md (the #757 acceptance
        criterion, pinned so a refactor cannot orphan the page).

Exit 0 when all invariants hold; exit 1 with one line per violation.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

DOC_RELPATH = Path("docs/CONTROL_AVAILABILITY.md")
SETUP_RELPATH = Path("docs/SETUP.md")
INBOUND_LINK_SURFACES = (Path("README.md"), SETUP_RELPATH)

# [text](target) and [text](target "title") — code fences in the doc carry no
# links, so no fence-stripping pass is needed. The target is captured before
# an optional quoted title; a titled link must not silently fall out of CA-1.
_LINK_RE = re.compile(r"\[[^\]]*\]\(\s*([^)\s]+)(?:\s+\"[^\"]*\")?\s*\)")
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$", re.MULTILINE)
_METHOD_HEADING_RE = re.compile(r"^###\s+Method\b.*$", re.MULTILINE)
_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
_QUOTE_PREFIX_RE = re.compile(r"^(\s{0,3}>\s?)+")


def _strip_fenced_code(md_text: str) -> str:
    """Fenced code blocks render literally: a link or heading inside a
    ``` / ~~~ fence counts for nothing. Runs BEFORE the comment pass, so a
    `<!--` inside a fence stays literal text and cannot open a comment
    block."""
    kept: list[str] = []
    in_fence = False
    fence_char = ""
    fence_len = 0
    for line in md_text.split("\n"):
        content = _QUOTE_PREFIX_RE.sub("", line).lstrip(" ")
        if not in_fence:
            opener = re.match(r"(`{3,}|~{3,})", content)
            if opener:
                in_fence = True
                fence_char = opener.group(1)[0]
                fence_len = len(opener.group(1))
                continue
        else:
            # CommonMark: the closer is a run of the SAME character at least
            # as long as the opener, with nothing but whitespace after it —
            # so a ```` fence is not closed by a literal ``` example line.
            closer = re.match(
                rf"({re.escape(fence_char)}{{{fence_len},}})\s*$", content
            )
            if closer:
                in_fence = False
            continue
        kept.append(line)
    return "\n".join(kept)


def _strip_html_comments(md_text: str) -> str:
    """Non-rendering markdown counts for nothing (neither satisfying
    CA-2/CA-3 nor firing CA-1).

    Two GFM behaviors matter here:
    - A line beginning with `<!--` (up to 3 leading spaces) opens a type-2
      HTML block that runs through the line containing `-->` — or to EOF if
      unclosed — and NOTHING on those lines renders as markdown, including
      text after the terminator on the closing line.
    - Elsewhere, an inline `<!-- ... -->` span is raw HTML; the surrounding
      text still renders.

    The line-start test looks through leading block-quote markers (`> `),
    since the same type-2 rule applies to block-quote content. Deeper
    CommonMark laminations (blocks terminated by the enclosing quote or
    list, comments opened inside list items, …) are deliberately not
    modeled — the surfaces this lint reads do not use them, and a full
    markdown parser is out of proportion for a maintainer-slip guard.
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


def github_slug(heading: str) -> str:
    """GitHub's markdown heading -> anchor slug, for the ASCII headings used
    in docs/SETUP.md: lowercase, drop punctuation, spaces become hyphens
    (consecutive spaces produce consecutive hyphens, e.g. "CLI / IDE" ->
    "cli--ide")."""
    text = heading.strip().lower()
    # Strip markdown emphasis/backticks before slugging.
    text = re.sub(r"[*_`]", "", text)
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def _strip_non_rendering(md_text: str) -> str:
    """Fenced code first (its contents are literal), then HTML comments."""
    return _strip_html_comments(_strip_fenced_code(md_text))


def _heading_slugs(md_text: str) -> set[str]:
    slugs: set[str] = set()
    for match in _HEADING_RE.finditer(_strip_non_rendering(md_text)):
        slugs.add(github_slug(match.group(2)))
    return slugs


def _doc_links(md_text: str) -> list[str]:
    return [
        m.group(1)
        for m in _LINK_RE.finditer(_strip_non_rendering(md_text))
    ]


def check_links_resolve(root: Path) -> list[str]:
    """CA-1: every relative link in the doc resolves (file + anchor)."""
    errors: list[str] = []
    doc_path = root / DOC_RELPATH
    text = doc_path.read_text(encoding="utf-8")
    self_slugs = _heading_slugs(text)
    for target in _doc_links(text):
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        if target.startswith("#"):
            if target[1:] not in self_slugs:
                errors.append(
                    f"CA-1: intra-doc anchor '{target}' has no matching "
                    f"heading in {DOC_RELPATH}"
                )
            continue
        path_part, _, fragment = target.partition("#")
        linked = (doc_path.parent / path_part).resolve()
        if not linked.is_relative_to(root.resolve()):
            # An existing HOST file outside the repo must not mask a broken
            # repo link (an over-deep `../../..` slip).
            errors.append(
                f"CA-1: link target '{path_part}' escapes the repository "
                f"(from {DOC_RELPATH})"
            )
            continue
        if not linked.exists():
            errors.append(
                f"CA-1: link target '{path_part}' does not exist "
                f"(from {DOC_RELPATH})"
            )
            continue
        if fragment:
            if linked.suffix.lower() != ".md":
                errors.append(
                    f"CA-1: anchor on non-markdown target '{target}'"
                )
                continue
            target_slugs = _heading_slugs(linked.read_text(encoding="utf-8"))
            if fragment not in target_slugs:
                errors.append(
                    f"CA-1: anchor '#{fragment}' not found in "
                    f"'{path_part}' (heading renamed or removed?)"
                )
    return errors


def check_method_coverage(root: Path) -> list[str]:
    """CA-2: every SETUP `### Method` heading is linked from the doc."""
    errors: list[str] = []
    setup_path = (root / SETUP_RELPATH).resolve()
    setup_text = setup_path.read_text(encoding="utf-8")
    doc_path = root / DOC_RELPATH
    doc_text = doc_path.read_text(encoding="utf-8")
    # Only fragments on links whose destination file IS docs/SETUP.md count:
    # a same-slug anchor into a copied/renamed file must not satisfy coverage.
    linked_fragments = set()
    for target in _doc_links(doc_text):
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        path_part, _, fragment = target.partition("#")
        if not fragment:
            continue
        if (doc_path.parent / path_part).resolve() == setup_path:
            linked_fragments.add(fragment)
    for match in _METHOD_HEADING_RE.finditer(_strip_non_rendering(setup_text)):
        heading = match.group(0).lstrip("#").strip()
        slug = github_slug(heading)
        if slug not in linked_fragments:
            errors.append(
                f"CA-2: SETUP heading '{heading}' has no link from "
                f"{DOC_RELPATH} — new or renamed install method missing "
                f"from the channel table"
            )
    return errors


def check_inbound_links(root: Path) -> list[str]:
    """CA-3: README.md and docs/SETUP.md link to the doc.

    The check is on the link DESTINATION, resolved relative to the surface —
    a link whose visible label keeps the filename but whose target points
    elsewhere must not pass.
    """
    errors: list[str] = []
    doc_abs = (root / DOC_RELPATH).resolve()
    for rel in INBOUND_LINK_SURFACES:
        surface = root / rel
        found = False
        for target in _doc_links(surface.read_text(encoding="utf-8")):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            path_part = target.partition("#")[0]
            if path_part and (surface.parent / path_part).resolve() == doc_abs:
                found = True
                break
        if not found:
            errors.append(
                f"CA-3: {rel} no longer links to {DOC_RELPATH.name} "
                f"(#757 acceptance criterion)"
            )
    return errors


def run_all_checks(root: Path) -> list[str]:
    doc_path = root / DOC_RELPATH
    if not doc_path.exists():
        return [f"CA-1: {DOC_RELPATH} is missing"]
    errors: list[str] = []
    errors.extend(check_links_resolve(root))
    errors.extend(check_method_coverage(root))
    errors.extend(check_inbound_links(root))
    return errors


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    errors = run_all_checks(root)
    if errors:
        for line in errors:
            print(f"ERROR: {line}", file=sys.stderr)
        print(
            f"check_control_availability: {len(errors)} violation(s)",
            file=sys.stderr,
        )
        return 1
    print("check_control_availability: OK (CA-1..CA-3)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
