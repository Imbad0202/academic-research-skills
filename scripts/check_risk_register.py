#!/usr/bin/env python3
"""Defrift lint for docs/RISK_REGISTER.md (#759).

The risk register is a hand-maintained index linking each standing risk to
its existing controls, its evidence status, and its residual gap. Its whole
value is its pointers, so this lint pins exactly three drift classes and
deliberately nothing else — risk wording, control selection, and residual-gap
semantics stay owned by code review, mirroring check_degradation_registry.py's
index-not-author posture:

  RR-1  Pointer integrity: every relative markdown link in the doc resolves
        inside the repo to an existing file (anchor fragments must match a
        GitHub-slugified heading in the target), and every backtick-quoted
        repo path (a code span containing "/" that does not start with "/")
        names an existing file or directory. A control a row cites must
        exist on disk.
  RR-2  Status mirroring: every "- **Evidence status**:" bullet carries at
        least one recognized citation. A citation of the form
        `STATUS` (capability matrix row `row_id`) must name an existing row
        in shared/contracts/capability/stage_capability_matrix.json and
        STATUS must equal that row's behavioral_evidence.status verbatim —
        the register mirrors the matrix, it can never upgrade it. A citation
        of the form `STATUS` (asserted here; no capability-matrix row) is a
        declared maintainer assertion and may only carry a no-measurement
        status (DESIGNED / NOT_RUN / OUT_OF_SCOPE): the matrix stays the
        sole authority for MEASURED/MIXED claims. Every occurrence of a
        citation phrase must belong to a well-formed citation (reported per
        segment, so the offending text is locatable), and the shipped
        matrix-row citations are inventory-locked to Evidence-status bullets
        (house pattern: the degradation registry's D5, the matrix lint's
        M13) so a lint-pinned citation can be neither demoted to an asserted
        one nor relocated out of the bullet the lock is about.
  RR-3  Discoverability: README.md carries at least one rendered link that
        resolves to docs/RISK_REGISTER.md (the #759 acceptance criterion,
        pinned so a refactor cannot orphan the page). Links inside code
        spans render literally and do not count.

Exit 0 when all invariants hold; exit 1 with one line per violation.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

# Shared markdown machinery (#771); the matrix vocabulary comes from the
# matrix lint, a genuinely data-owning dependency.
from _markdown_lint_util import (  # noqa: E402
    NON_RELATIVE_LINK_PREFIXES,
    RelativeLinkFailure,
    code_spans,
    link_targets,
    links_to,
    relative_link_failure,
    strip_non_rendering,
)
from check_stage_capability_matrix import (  # noqa: E402
    _BEHAVIORAL_STATUSES,
    _load,
    _status,
)

DOC_RELPATH = Path("docs/RISK_REGISTER.md")
MATRIX_RELPATH = Path("shared/contracts/capability/stage_capability_matrix.json")
README_RELPATH = Path("README.md")

_CITE_RE = re.compile(
    r"`([A-Za-z_]+)`\s*\((?:capability matrix row\s+`([A-Za-z0-9_.]+)`"
    r"|asserted here; no capability-matrix row)\)"
)
# Substrings whose every occurrence must be consumed by a well-formed
# citation, so a typo cannot demote a pinned status to unchecked prose.
_CITE_PHRASES = ("capability matrix row", "asserted here")
_EVIDENCE_BULLET_PREFIX = "- **Evidence status**:"
# Segment boundaries for locatable per-segment reporting: top-level bullets
# and headings.
_SEGMENT_RE = re.compile(r"\n(?=- \*\*|#)")

# An asserted-here citation may only describe absence of evidence; any
# measurement claim (MEASURED / MIXED) must come from the matrix.
_ASSERTED_ALLOWED = frozenset({"DESIGNED", "NOT_RUN", "OUT_OF_SCOPE"})

# Shipped-inventory lock: every row_id here must stay cited as a matrix-tied
# citation in the register. Dropping one (or demoting it to asserted-here)
# fails CI until this constant is updated in the same commit.
_EXPECTED_MATRIX_ROW_CITATIONS = frozenset(
    {
        "retrieval.citation_existence_gate",
        "integrity_check.claim_verification",
        "revision.claim_drift_guard",
        "review.calibration",
    }
)


def _doc_text(root: Path) -> str:
    return strip_non_rendering(
        (root / DOC_RELPATH).read_text(encoding="utf-8")
    )


def _looks_like_repo_path(token: str) -> bool:
    """A code span is treated as a repo path when it contains a "/" but is
    not an absolute path or slash command (leading "/") or a URL. Spaces do
    NOT opt a span out — a typo'd `scripts/no such file.py` must fail RR-1,
    not silently skip it. Everything else (env vars, row_ids, JSON keys) is
    opted out by construction."""
    if "/" not in token or token.startswith("/"):
        return False
    if "://" in token:
        return False
    return True


def referenced_paths(doc_text: str) -> tuple[list[str], list[str]]:
    """(relative link targets, backtick repo paths) named by the doc.
    Link targets keep their #fragment; callers split as needed."""
    links = []
    for target in link_targets(doc_text):
        if target.startswith(NON_RELATIVE_LINK_PREFIXES):
            continue
        links.append(target)
    spans = [
        token
        for token in code_spans(doc_text)
        if _looks_like_repo_path(token)
    ]
    return links, spans


def check_pointer_integrity(root: Path) -> list[str]:
    errors: list[str] = []
    root_abs = root.resolve()
    doc_dir = (root / DOC_RELPATH).parent
    links, spans = referenced_paths(_doc_text(root))
    for target in links:
        path_part, _, fragment = target.partition("#")
        failure = relative_link_failure(root, root / DOC_RELPATH, target)
        if failure is RelativeLinkFailure.ESCAPES_REPOSITORY:
            errors.append(
                f"RR-1: {DOC_RELPATH} links to {target!r}, which escapes "
                "the repository root"
            )
        elif failure is RelativeLinkFailure.DOES_NOT_EXIST:
            errors.append(
                f"RR-1: {DOC_RELPATH} links to {target!r}, which does not "
                f"exist relative to {doc_dir.name}/"
            )
        elif failure is RelativeLinkFailure.ANCHOR_ON_NON_MARKDOWN:
            errors.append(
                f"RR-1: {DOC_RELPATH} links to {target!r}, an anchor "
                "on a non-markdown target"
            )
        elif failure is RelativeLinkFailure.ANCHOR_NOT_FOUND:
            errors.append(
                f"RR-1: {DOC_RELPATH} links to {target!r}, but no "
                f"heading in {path_part!r} has id {fragment!r}"
            )
    for token in spans:
        resolved = (root / token).resolve()
        if not resolved.is_relative_to(root_abs) or not resolved.exists():
            errors.append(
                f"RR-1: {DOC_RELPATH} cites repo path `{token}`, which does "
                "not exist"
            )
    return errors


def check_status_mirroring(root: Path) -> list[str]:
    errors: list[str] = []
    doc_text = _doc_text(root)
    try:
        matrix = _load(root / MATRIX_RELPATH)
    except ValueError as exc:
        return [f"RR-2: cannot load {MATRIX_RELPATH}: {exc}"]
    rows = {row.get("row_id"): _status(row) for row in matrix.get("rows", [])}

    cited_matrix_rows: set[str] = set()
    for segment in _SEGMENT_RE.split(doc_text):
        first_line = segment.strip().split("\n", 1)[0]
        is_evidence_bullet = segment.strip().startswith(_EVIDENCE_BULLET_PREFIX)
        cites = _CITE_RE.findall(segment)

        # Malformed-citation guard, reported against the segment so the
        # offending text is locatable.
        consumed = _CITE_RE.sub("", segment)
        for phrase in _CITE_PHRASES:
            if phrase in consumed:
                errors.append(
                    f"RR-2: {phrase!r} appears outside a well-formed "
                    f"citation in segment starting {first_line!r}"
                )

        if is_evidence_bullet and not cites:
            errors.append(
                f"RR-2: evidence-status bullet carries no recognized "
                f"citation: {first_line!r}"
            )

        for status, row_id in cites:
            if status not in _BEHAVIORAL_STATUSES:
                errors.append(
                    f"RR-2: status {status!r} not in matrix vocabulary "
                    f"{_BEHAVIORAL_STATUSES}"
                )
            if row_id:
                # The inventory lock counts only citations sitting in an
                # Evidence-status bullet: relocating a matrix citation into
                # another bullet must not satisfy the lock.
                if is_evidence_bullet:
                    cited_matrix_rows.add(row_id)
                if row_id not in rows:
                    errors.append(
                        f"RR-2: capability matrix row {row_id!r} does not "
                        f"exist in {MATRIX_RELPATH}"
                    )
                elif rows[row_id] != status:
                    errors.append(
                        f"RR-2: register states {status!r} for matrix row "
                        f"{row_id!r} but the matrix records {rows[row_id]!r}"
                    )
            elif status in _BEHAVIORAL_STATUSES and status not in _ASSERTED_ALLOWED:
                errors.append(
                    f"RR-2: asserted-here citation may not claim {status!r}; "
                    "the matrix is the sole authority for measurement "
                    "statuses"
                )

    for row_id in sorted(_EXPECTED_MATRIX_ROW_CITATIONS - cited_matrix_rows):
        errors.append(
            f"RR-2: expected matrix-row citation {row_id!r} is no longer "
            "present in an Evidence-status bullet; update "
            "_EXPECTED_MATRIX_ROW_CITATIONS in the same commit if intentional"
        )
    return errors


def check_inbound_link(root: Path) -> list[str]:
    """RR-3, same grammar as DF-3/CA-3: resolved-path compare, code spans
    stripped so a backticked pseudo-link cannot satisfy the invariant."""
    doc_abs = (root / DOC_RELPATH).resolve()
    surface = root / README_RELPATH
    if links_to(surface.read_text(encoding="utf-8"), surface.parent, doc_abs):
        return []
    return [
        f"RR-3: {README_RELPATH} carries no rendered link to {DOC_RELPATH}"
    ]


def run_all_checks(root: Path) -> list[str]:
    if not (root / DOC_RELPATH).exists():
        return [f"RR-1: {DOC_RELPATH} is missing"]
    errors: list[str] = []
    errors.extend(check_pointer_integrity(root))
    errors.extend(check_status_mirroring(root))
    errors.extend(check_inbound_link(root))
    return errors


def main() -> int:
    root = _SCRIPTS_DIR.parent
    errors = run_all_checks(root)
    if errors:
        for line in errors:
            print(f"ERROR: {line}", file=sys.stderr)
        print(
            f"check_risk_register: {len(errors)} violation(s)",
            file=sys.stderr,
        )
        return 1
    print("check_risk_register: OK (RR-1..RR-3)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
