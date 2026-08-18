#!/usr/bin/env python3
"""Defrift lint for docs/RISK_REGISTER.md (#759).

The risk register is a hand-maintained index linking each standing risk to
its existing controls, its evidence status, and its residual gap. Its whole
value is its pointers, so this lint pins exactly three drift classes and
deliberately nothing else — risk wording, control selection, and residual-gap
semantics stay owned by code review, mirroring check_degradation_registry.py's
index-not-author posture:

  RR-1  Pointer integrity: every relative markdown link in the doc resolves
        to an existing file, and every backtick-quoted repo path (a code
        span containing "/" that does not start with "/") names an existing
        file or directory. A control a row cites must exist on disk.
  RR-2  Status mirroring: every "- **Evidence status**:" bullet carries at
        least one recognized citation. A citation of the form
        `STATUS` (capability matrix row `row_id`) must name an existing row
        in shared/contracts/capability/stage_capability_matrix.json and
        STATUS must equal that row's behavioral_evidence.status verbatim —
        the register mirrors the matrix, it can never upgrade it. A citation
        of the form `STATUS` (asserted here; no capability-matrix row) is a
        declared maintainer assertion. Both forms must use the matrix's
        behavioral-status vocabulary, and every occurrence of the phrases
        "capability matrix row" / "asserted here" must belong to a
        well-formed citation so a malformed one cannot silently drop out.
  RR-3  Discoverability: README.md carries at least one rendered link to
        docs/RISK_REGISTER.md (the #759 acceptance criterion, pinned so a
        refactor cannot orphan the page).

Exit 0 when all invariants hold; exit 1 with one line per violation.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

# Reuse the superset markdown-stripping helpers (#771 tracks consolidating
# them into a shared module; importing beats a third copy) and the matrix's
# frozen behavioral-status vocabulary so the two lints cannot drift apart.
from check_data_flows import _strip_non_rendering  # noqa: E402
from check_stage_capability_matrix import _BEHAVIORAL_STATUSES  # noqa: E402

DOC_RELPATH = Path("docs/RISK_REGISTER.md")
MATRIX_RELPATH = Path("shared/contracts/capability/stage_capability_matrix.json")
README_RELPATH = Path("README.md")

_LINK_RE = re.compile(r"(?<!\!)\[[^\]]*\]\(\s*([^)\s]+)(?:\s+\"[^\"]*\")?\s*\)")
_CODE_SPAN_RE = re.compile(r"`([^`\n]+)`")
_MATRIX_CITE_RE = re.compile(
    r"`([A-Za-z_]+)`\s*\(capability matrix row\s+`([A-Za-z0-9_.]+)`\)"
)
_ASSERTED_CITE_RE = re.compile(
    r"`([A-Za-z_]+)`\s*\(asserted here; no capability-matrix row\)"
)
_EVIDENCE_BULLET_PREFIX = "- **Evidence status**:"


def _doc_text(root: Path) -> str:
    return _strip_non_rendering(
        (root / DOC_RELPATH).read_text(encoding="utf-8")
    )


def _looks_like_repo_path(token: str) -> bool:
    """A code span is treated as a repo path when it contains a "/" but is
    not an absolute path or slash command (leading "/"), a URL, or prose
    with spaces. Everything else (env vars, row_ids, JSON keys) is opted
    out by construction."""
    if "/" not in token or token.startswith("/"):
        return False
    if " " in token or "://" in token:
        return False
    return True


def referenced_paths(doc_text: str) -> tuple[list[str], list[str]]:
    """(relative link targets, backtick repo paths) named by the doc."""
    links = []
    for target in _LINK_RE.findall(doc_text):
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        links.append(target.split("#", 1)[0])
    spans = [
        token
        for token in _CODE_SPAN_RE.findall(doc_text)
        if _looks_like_repo_path(token)
    ]
    return links, spans


def check_pointer_integrity(root: Path) -> list[str]:
    errors: list[str] = []
    doc_dir = (root / DOC_RELPATH).parent
    links, spans = referenced_paths(_doc_text(root))
    for target in links:
        if not (doc_dir / target).exists():
            errors.append(
                f"RR-1: {DOC_RELPATH} links to {target!r}, which does not "
                f"exist relative to {doc_dir.name}/"
            )
    for token in spans:
        if not (root / token).exists():
            errors.append(
                f"RR-1: {DOC_RELPATH} cites repo path `{token}`, which does "
                "not exist"
            )
    return errors


def check_status_mirroring(root: Path) -> list[str]:
    errors: list[str] = []
    doc_text = _doc_text(root)
    matrix = json.loads((root / MATRIX_RELPATH).read_text(encoding="utf-8"))
    rows = {
        row.get("row_id"): row.get("behavioral_evidence", {}).get("status")
        for row in matrix.get("rows", [])
    }

    matrix_cites = _MATRIX_CITE_RE.findall(doc_text)
    asserted_cites = _ASSERTED_CITE_RE.findall(doc_text)

    # Malformed-citation guard: every occurrence of the citation phrases must
    # be consumed by a well-formed citation, or a typo would silently turn a
    # lint-pinned status into unchecked prose.
    if doc_text.count("capability matrix row") != len(matrix_cites):
        errors.append(
            "RR-2: a 'capability matrix row' phrase does not parse as a "
            "well-formed `STATUS` (capability matrix row `row_id`) citation"
        )
    if doc_text.count("asserted here") != len(asserted_cites):
        errors.append(
            "RR-2: an 'asserted here' phrase does not parse as a well-formed "
            "`STATUS` (asserted here; no capability-matrix row) citation"
        )

    for status, row_id in matrix_cites:
        if status not in _BEHAVIORAL_STATUSES:
            errors.append(
                f"RR-2: status {status!r} (row {row_id!r}) not in matrix "
                f"vocabulary {_BEHAVIORAL_STATUSES}"
            )
        if row_id not in rows:
            errors.append(
                f"RR-2: capability matrix row {row_id!r} does not exist in "
                f"{MATRIX_RELPATH}"
            )
        elif rows[row_id] != status:
            errors.append(
                f"RR-2: register states {status!r} for matrix row {row_id!r} "
                f"but the matrix records {rows[row_id]!r}"
            )
    for status in asserted_cites:
        if status not in _BEHAVIORAL_STATUSES:
            errors.append(
                f"RR-2: asserted status {status!r} not in matrix vocabulary "
                f"{_BEHAVIORAL_STATUSES}"
            )

    # A bullet's citations may wrap onto continuation lines; scan each
    # bullet's full logical extent (up to the next "- **" bullet).
    bullets = re.split(r"\n(?=- \*\*)", doc_text)
    for bullet in bullets:
        if not bullet.strip().startswith(_EVIDENCE_BULLET_PREFIX):
            continue
        if not (_MATRIX_CITE_RE.search(bullet) or _ASSERTED_CITE_RE.search(bullet)):
            first_line = bullet.strip().split("\n", 1)[0]
            errors.append(
                f"RR-2: evidence-status bullet carries no recognized "
                f"citation: {first_line!r}"
            )
    return errors


def check_inbound_link(root: Path) -> list[str]:
    readme = _strip_non_rendering(
        (root / README_RELPATH).read_text(encoding="utf-8")
    )
    for target in _LINK_RE.findall(readme):
        if target.split("#", 1)[0] in ("docs/RISK_REGISTER.md",):
            return []
    return [
        f"RR-3: {README_RELPATH} carries no rendered link to {DOC_RELPATH}"
    ]


def run_all_checks(root: Path) -> list[str]:
    errors: list[str] = []
    errors.extend(check_pointer_integrity(root))
    errors.extend(check_status_mirroring(root))
    errors.extend(check_inbound_link(root))
    return errors


def main() -> int:
    root = _SCRIPTS_DIR.parent
    errors = run_all_checks(root)
    for error in errors:
        print(error, file=sys.stderr)
    if errors:
        print(f"check_risk_register: {len(errors)} violation(s)", file=sys.stderr)
        return 1
    print("check_risk_register: OK (RR-1, RR-2, RR-3)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
