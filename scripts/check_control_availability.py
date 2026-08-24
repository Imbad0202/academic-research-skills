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

Rendered-link / non-rendering / slug grammar: scripts/_markdown_lint_util.py
(#771 consolidation; since then CA-1..CA-3 also apply its code-span and
image-exclusion rules).

Exit 0 when all invariants hold; exit 1 with one line per violation.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from _markdown_lint_util import (
    NON_RELATIVE_LINK_PREFIXES,
    RelativeLinkFailure,
    extract_link_targets,
    github_slug,
    links_to,
    relative_link_failure,
    strip_non_rendering,
)

DOC_RELPATH = Path("docs/CONTROL_AVAILABILITY.md")
SETUP_RELPATH = Path("docs/SETUP.md")
INBOUND_LINK_SURFACES = (Path("README.md"), SETUP_RELPATH)

_METHOD_HEADING_RE = re.compile(r"^###\s+Method\b.*$", re.MULTILINE)


def check_links_resolve(root: Path) -> list[str]:
    """CA-1: every relative link in the doc resolves (file + anchor)."""
    errors: list[str] = []
    doc_path = root / DOC_RELPATH
    text = doc_path.read_text(encoding="utf-8")
    for target in extract_link_targets(text):
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        path_part, _, fragment = target.partition("#")
        failure = relative_link_failure(root, doc_path, target)
        if failure is RelativeLinkFailure.ESCAPES_REPOSITORY:
            # An existing HOST file outside the repo must not mask a broken
            # repo link (an over-deep `../../..` slip).
            errors.append(
                f"CA-1: link target '{path_part}' escapes the repository "
                f"(from {DOC_RELPATH})"
            )
        elif failure is RelativeLinkFailure.DOES_NOT_EXIST:
            errors.append(
                f"CA-1: link target '{path_part}' does not exist "
                f"(from {DOC_RELPATH})"
            )
        elif failure is RelativeLinkFailure.ANCHOR_ON_NON_MARKDOWN:
            errors.append(
                f"CA-1: anchor on non-markdown target '{target}'"
            )
        elif failure is RelativeLinkFailure.ANCHOR_NOT_FOUND:
            if not path_part:
                errors.append(
                    f"CA-1: intra-doc anchor '{target}' has no matching "
                    f"heading in {DOC_RELPATH}"
                )
            else:
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
    for target in extract_link_targets(doc_text):
        if target.startswith(NON_RELATIVE_LINK_PREFIXES):
            continue
        path_part, _, fragment = target.partition("#")
        if not fragment:
            continue
        if (doc_path.parent / path_part).resolve() == setup_path:
            linked_fragments.add(fragment)
    for match in _METHOD_HEADING_RE.finditer(strip_non_rendering(setup_text)):
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
        text = surface.read_text(encoding="utf-8")
        if not links_to(text, surface.parent, doc_abs):
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
