#!/usr/bin/env python3
"""Shared markdown non-rendering semantics for the defrift lints (#771).

Single authority for the stripping/link grammar that was hardened across the
#757 (check_control_availability.py) and #758 (check_data_flows.py) review
rounds and then shipped as two diverging copies. Consolidation rule from
issue #771: the #770 versions are the superset and win — inline code spans
render literally (a link inside backticks is not a link) and an image
`![alt](target)` renders no anchor, so both are excluded from the rendered
link grammar. check_risk_register.py (#760) imports the same machinery.

Pure text helpers: no filesystem access, no repo assumptions. Consumers own
their invariant semantics; this module only answers "what does GitHub render
from this markdown?" for the surfaces those lints read.

Modeling boundary (unchanged from the source copies): deeper CommonMark
laminations — blocks terminated by the enclosing quote or list, comments
opened inside list items, … — are deliberately not modeled. The surfaces the
lints read do not use them, and a full markdown parser is out of proportion
for a maintainer-slip guard.
"""
from __future__ import annotations

import re

# [text](target) and [text](target "title") — the target is captured before
# an optional quoted title; a titled link must not silently fall out of the
# link-resolution invariants. (?<!\!) — an image `![alt](target)` renders no
# anchor and must not satisfy an inbound-link invariant.
LINK_RE = re.compile(r"(?<!\!)\[[^\]]*\]\(\s*([^)\s]+)(?:\s+\"[^\"]*\")?\s*\)")

# Inline code spans render literally — a link inside backticks is not a
# link. Stripped AFTER the block-level passes (a fence's contents are gone
# by then, so a lone backtick inside a fence cannot open a phantom span).
CODE_SPAN_RE = re.compile(r"`([^`\n]+)`")

_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
_QUOTE_PREFIX_RE = re.compile(r"^(\s{0,3}>\s?)+")


def strip_fenced_code(md_text: str) -> str:
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


def strip_html_comments(md_text: str) -> str:
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
    return strip_html_comments(strip_fenced_code(md_text))


def extract_link_targets(md_text: str) -> list[str]:
    """Targets of the RENDERED markdown links in `md_text`: block-level
    non-rendering stripped, then inline code spans, then the image-excluding
    link grammar."""
    return [
        m.group(1)
        for m in LINK_RE.finditer(CODE_SPAN_RE.sub("", strip_non_rendering(md_text)))
    ]
