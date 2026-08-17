#!/usr/bin/env python3
"""Stage capability/evidence matrix lint + renderer (#745).

Pins shared/contracts/capability/stage_capability_matrix.json — the single
machine-readable source for what each pipeline stage's mechanisms are, what
evidence exists for them, and the maximum claim that evidence licenses — so
capability language can never silently outrun the recorded evidence:

  M1.  Matrix parses, carries the exact schema_version, no unknown top-level
       fields, no duplicate JSON object keys (fail-closed: a missing or
       unparseable matrix is an error, never a silent pass).
  M2.  task_families equals the frozen TASK_FAMILIES vocabulary exactly,
       including order (the same closed list the #742 profile contract
       consumes — additions require touching this lint in the same commit).
  M3.  Rows are closed shapes: required fields present and non-empty, no
       unknown fields, unique row_id, task_family from the vocabulary,
       mechanism_status and deterministic_conformance from closed enums.
  M4.  behavioral_evidence.status is one of DESIGNED / NOT_RUN / MEASURED /
       MIXED / OUT_OF_SCOPE and the statuses cannot collapse: MEASURED/MIXED
       require full provenance (eval_ref existing in-repo, model, population,
       measured_at ISO date, result_summary); DESIGNED/NOT_RUN must not carry
       measured_at or result_summary (an unrun eval can never carry numbers);
       OUT_OF_SCOPE requires a reason.
  M5.  Every task family has at least one row (no silently uncovered stage).
  M6.  max_licensed_claim is non-empty, and on a row whose behavioral status
       is not MEASURED/MIXED it must not contain effectiveness stems
       (improve/outperform/guarantee/proven/state-of-the-art) — conservative
       language discipline, not semantic parsing.
  M7.  Every claim_anchors entry names an existing repo file and its anchor
       (>= 16 chars) appears VERBATIM in that file, so top-level capability
       claims resolve to a matrix row and fail the build when reworded
       without touching the matrix.
  M8.  A MEASURED/MIXED row older than stale_after_days must carry a
       staleness_note (stale evidence stays visible, never silently current).
  M9.  next_required_evaluation is non-empty except on OUT_OF_SCOPE rows.
  M10. docs/STAGE_CAPABILITY_MATRIX.md is byte-identical to render(matrix)
       (the human view is generated, never hand-drifted).

The matrix indexes evidence, it does not create it: this lint verifies
citation resolution and status discipline, not that the recorded results are
scientifically meaningful. Registering a row licenses at most the row's
max_licensed_claim, never more.

Usage:
  python3 scripts/check_stage_capability_matrix.py            # full check
  python3 scripts/check_stage_capability_matrix.py --render   # rewrite view
Exit 0 = all invariants hold; exit 1 = violations (listed on stderr).
"""
from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MATRIX = (
    REPO_ROOT / "shared" / "contracts" / "capability" / "stage_capability_matrix.json"
)
DEFAULT_VIEW = REPO_ROOT / "docs" / "STAGE_CAPABILITY_MATRIX.md"

# Frozen stage/task-family vocabulary — the same closed list the #742 profile
# contract's stage_map consumes (docs/design/2026-08-17-742-research-family-
# profile-contract-design.md §2). Changing it is a contract version bump in
# BOTH consumers, in the same commit as this constant.
TASK_FAMILIES = (
    "rq_formation",
    "retrieval",
    "methodology",
    "synthesis",
    "drafting",
    "integrity_check",
    "review",
    "revision",
    "finalization",
)

_TOP_FIELDS = {
    "schema_version",
    "generated_view",
    "stale_after_days",
    "task_families",
    "rows",
}
_SCHEMA_VERSION = "stage-capability-matrix/1.0"
_ROW_REQUIRED = (
    "row_id",
    "task_family",
    "mechanism",
    "mechanism_status",
    "deterministic_conformance",
    "behavioral_evidence",
    "external_outcome_evidence",
    "known_exclusions",
    "transport_limits",
    "max_licensed_claim",
    "next_required_evaluation",
)
_ROW_OPTIONAL = ("claim_anchors",)
_MECHANISM_STATUSES = ("IMPLEMENTED", "PARTIAL", "DESIGNED")
_CONFORMANCE_STATUSES = ("CI_GATED", "TESTED", "NONE")
_BEHAVIORAL_STATUSES = ("DESIGNED", "NOT_RUN", "MEASURED", "MIXED", "OUT_OF_SCOPE")
_EVIDENCE_PROVENANCE = ("eval_ref", "model", "population", "measured_at", "result_summary")
_EVIDENCE_FIELDS = set(
    ("status", "reason", "staleness_note") + _EVIDENCE_PROVENANCE
)
# Conservative effectiveness stems: forbidden in max_licensed_claim unless the
# row's behavioral evidence is MEASURED/MIXED (which records what was measured).
_OVERCLAIM_STEMS = (
    "improv",
    "outperform",
    "guarantee",
    "proven",
    "state-of-the-art",
    "state of the art",
    "sota",
)
_MIN_ANCHOR_LEN = 16


def _reject_duplicate_keys(pairs):
    seen = set()
    for key, _ in pairs:
        if key in seen:
            raise ValueError(f"duplicate JSON object key: {key!r}")
        seen.add(key)
    return dict(pairs)


def _nonempty_str(value) -> bool:
    return isinstance(value, str) and value.strip() != ""


def _str_list(value) -> bool:
    return isinstance(value, list) and all(_nonempty_str(v) for v in value)


def _check_behavioral(row_id: str, ev, today: datetime.date, stale_after_days: int,
                      repo_root: Path, errors: list[str]) -> None:
    prefix = f"M4 row {row_id}:"
    if not isinstance(ev, dict):
        errors.append(f"{prefix} behavioral_evidence must be an object")
        return
    unknown = set(ev) - _EVIDENCE_FIELDS
    if unknown:
        errors.append(f"{prefix} unknown behavioral_evidence fields {sorted(unknown)}")
    status = ev.get("status")
    if status not in _BEHAVIORAL_STATUSES:
        errors.append(
            f"{prefix} status {status!r} not in {_BEHAVIORAL_STATUSES}"
        )
        return
    if status in ("MEASURED", "MIXED"):
        for field in _EVIDENCE_PROVENANCE:
            if not _nonempty_str(ev.get(field)):
                errors.append(
                    f"{prefix} {status} requires non-empty {field!r} provenance"
                )
        measured_at = ev.get("measured_at")
        measured_date = None
        if _nonempty_str(measured_at):
            try:
                measured_date = datetime.date.fromisoformat(measured_at)
            except ValueError:
                errors.append(
                    f"{prefix} measured_at {measured_at!r} is not an ISO date"
                )
        eval_ref = ev.get("eval_ref")
        if _nonempty_str(eval_ref) and not (repo_root / eval_ref).exists():
            errors.append(
                f"{prefix} eval_ref {eval_ref!r} does not exist in the repo"
            )
        if measured_date is not None:
            age = (today - measured_date).days
            if age > stale_after_days and not _nonempty_str(ev.get("staleness_note")):
                errors.append(
                    f"M8 row {row_id}: measurement {measured_at} is older than "
                    f"{stale_after_days} days and has no staleness_note"
                )
    else:
        for field in ("measured_at", "result_summary"):
            if field in ev:
                errors.append(
                    f"{prefix} {status} row must not carry {field!r} — a result "
                    "cannot ride an unrun or out-of-scope evaluation"
                )
        if status == "OUT_OF_SCOPE" and not _nonempty_str(ev.get("reason")):
            errors.append(f"{prefix} OUT_OF_SCOPE requires a non-empty reason")


def _check_claim(row, errors: list[str]) -> None:
    row_id = row.get("row_id", "?")
    claim = row.get("max_licensed_claim")
    if not _nonempty_str(claim):
        errors.append(f"M6 row {row_id}: max_licensed_claim must be non-empty")
        return
    status = (row.get("behavioral_evidence") or {}).get("status")
    if status not in ("MEASURED", "MIXED"):
        lowered = claim.lower()
        for stem in _OVERCLAIM_STEMS:
            if stem in lowered:
                errors.append(
                    f"M6 row {row_id}: claim ceiling contains effectiveness stem "
                    f"{stem!r} but behavioral evidence is {status}, not "
                    "MEASURED/MIXED"
                )


def _check_anchors(row, repo_root: Path, errors: list[str]) -> None:
    row_id = row.get("row_id", "?")
    anchors = row.get("claim_anchors")
    if anchors is None:
        return
    if not isinstance(anchors, list):
        errors.append(f"M7 row {row_id}: claim_anchors must be a list")
        return
    for anchor in anchors:
        if not isinstance(anchor, dict) or set(anchor) != {"file", "anchor"}:
            errors.append(
                f"M7 row {row_id}: each claim anchor is exactly "
                "{{file, anchor}}"
            )
            continue
        text = anchor["anchor"]
        if not _nonempty_str(text) or len(text) < _MIN_ANCHOR_LEN:
            errors.append(
                f"M7 row {row_id}: anchor must be >= {_MIN_ANCHOR_LEN} chars"
            )
            continue
        target = repo_root / anchor["file"]
        if not target.is_file():
            errors.append(
                f"M7 row {row_id}: anchor file {anchor['file']!r} does not exist"
            )
            continue
        if text not in target.read_text(encoding="utf-8"):
            errors.append(
                f"M7 row {row_id}: anchor not found verbatim in "
                f"{anchor['file']!r}: {text[:60]!r}"
            )


def run(
    matrix_path: Path,
    *,
    check_view: bool = True,
    view_path: Path | None = None,
    repo_root: Path = REPO_ROOT,
    today: datetime.date | None = None,
) -> list[str]:
    errors: list[str] = []
    today = today or datetime.date.today()
    try:
        data = json.loads(
            matrix_path.read_text(encoding="utf-8"),
            object_pairs_hook=_reject_duplicate_keys,
        )
    except (OSError, ValueError) as exc:
        return [f"M1: cannot load matrix {matrix_path}: {exc}"]
    if not isinstance(data, dict):
        return ["M1: matrix root must be an object"]
    if set(data) != _TOP_FIELDS:
        missing = _TOP_FIELDS - set(data)
        unknown = set(data) - _TOP_FIELDS
        errors.append(f"M1: top-level fields missing={sorted(missing)} unknown={sorted(unknown)}")
    if data.get("schema_version") != _SCHEMA_VERSION:
        errors.append(
            f"M1: schema_version must be {_SCHEMA_VERSION!r}, "
            f"got {data.get('schema_version')!r}"
        )
    stale_after_days = data.get("stale_after_days")
    if not isinstance(stale_after_days, int) or stale_after_days <= 0:
        errors.append("M1: stale_after_days must be a positive integer")
        stale_after_days = 365
    if errors and set(data) != _TOP_FIELDS:
        return errors

    if list(data.get("task_families") or []) != list(TASK_FAMILIES):
        errors.append(
            "M2: task_families must equal the frozen vocabulary exactly "
            f"(including order): {list(TASK_FAMILIES)}"
        )

    rows = data.get("rows")
    if not isinstance(rows, list) or not rows:
        errors.append("M3: rows must be a non-empty list")
        return errors

    seen_ids: set[str] = set()
    covered: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            errors.append("M3: every row must be an object")
            continue
        row_id = row.get("row_id", "?")
        missing = [f for f in _ROW_REQUIRED if f not in row]
        if missing:
            errors.append(f"M3 row {row_id}: missing fields {missing}")
        unknown = set(row) - set(_ROW_REQUIRED) - set(_ROW_OPTIONAL)
        if unknown:
            errors.append(f"M3 row {row_id}: unknown fields {sorted(unknown)}")
        if not _nonempty_str(row.get("row_id")):
            errors.append("M3: row_id must be a non-empty string")
        elif row_id in seen_ids:
            errors.append(f"M3: duplicate row_id {row_id!r}")
        else:
            seen_ids.add(row_id)
        family = row.get("task_family")
        if family not in TASK_FAMILIES:
            errors.append(f"M3 row {row_id}: unknown task_family {family!r}")
        else:
            covered.add(family)
        if row.get("mechanism_status") not in _MECHANISM_STATUSES:
            errors.append(
                f"M3 row {row_id}: mechanism_status must be one of "
                f"{_MECHANISM_STATUSES}"
            )
        if row.get("deterministic_conformance") not in _CONFORMANCE_STATUSES:
            errors.append(
                f"M3 row {row_id}: deterministic_conformance must be one of "
                f"{_CONFORMANCE_STATUSES}"
            )
        if not _nonempty_str(row.get("mechanism")):
            errors.append(f"M3 row {row_id}: mechanism must be non-empty")
        if not _nonempty_str(row.get("external_outcome_evidence")):
            errors.append(
                f"M3 row {row_id}: external_outcome_evidence must be non-empty "
                "(use 'none' explicitly)"
            )
        for list_field in ("known_exclusions", "transport_limits"):
            if list_field in row and not _str_list(row[list_field]):
                errors.append(
                    f"M3 row {row_id}: {list_field} must be a list of "
                    "non-empty strings"
                )

        _check_behavioral(
            row_id, row.get("behavioral_evidence"), today, stale_after_days,
            repo_root, errors,
        )
        _check_claim(row, errors)
        _check_anchors(row, repo_root, errors)

        status = (row.get("behavioral_evidence") or {}).get("status")
        if status != "OUT_OF_SCOPE" and not _nonempty_str(
            row.get("next_required_evaluation")
        ):
            errors.append(
                f"M9 row {row_id}: next_required_evaluation must be non-empty "
                "unless the row is OUT_OF_SCOPE"
            )

    uncovered = set(TASK_FAMILIES) - covered
    if uncovered:
        errors.append(
            f"M5: task families with no row: {sorted(uncovered)}"
        )

    if check_view:
        target = view_path or (repo_root / data.get("generated_view", ""))
        try:
            current = target.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"M10: cannot read generated view {target}: {exc}")
        else:
            if current != render(data):
                errors.append(
                    f"M10: {target} is out of sync with the matrix — "
                    "regenerate with --render"
                )
    return errors


def _cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def render(data: dict) -> str:
    """Deterministic human-readable view of the matrix (GENERATED FILE)."""
    lines = [
        "# ARS Stage Capability / Evidence Matrix",
        "",
        "<!-- GENERATED FILE — do not edit by hand. -->",
        "<!-- Source: shared/contracts/capability/stage_capability_matrix.json -->",
        "<!-- Regenerate: python3 scripts/check_stage_capability_matrix.py --render -->",
        "",
        "Machine-readable source of record for what evidence exists per pipeline",
        "stage and the maximum claim that evidence licenses (#745). A row is an",
        "index entry, not an endorsement: DESIGNED and NOT_RUN mean exactly that,",
        "and no consumer may state more than the row's recorded claim ceiling.",
        "",
    ]
    rows = data.get("rows", [])
    for family in data.get("task_families", []):
        family_rows = [r for r in rows if r.get("task_family") == family]
        lines.append(f"## `{family}`")
        lines.append("")
        for row in family_rows:
            ev = row.get("behavioral_evidence", {})
            status = ev.get("status", "?")
            lines.append(f"### {row.get('row_id')}")
            lines.append("")
            lines.append(f"- **Mechanism**: {_cell(row.get('mechanism', ''))}")
            lines.append(
                f"- **Mechanism status**: {row.get('mechanism_status', '')} / "
                f"deterministic conformance: {row.get('deterministic_conformance', '')}"
            )
            detail = [f"**Behavioral evidence**: {status}"]
            if status in ("MEASURED", "MIXED"):
                detail.append(
                    f"— {_cell(ev.get('result_summary', ''))} "
                    f"({_cell(ev.get('eval_ref', ''))}; model {_cell(ev.get('model', ''))}; "
                    f"population {_cell(ev.get('population', ''))}; {ev.get('measured_at', '')})"
                )
            if ev.get("staleness_note"):
                detail.append(f"— STALE: {_cell(ev['staleness_note'])}")
            if status == "OUT_OF_SCOPE" and ev.get("reason"):
                detail.append(f"— {_cell(ev['reason'])}")
            lines.append("- " + " ".join(detail))
            lines.append(
                "- **External/human outcome evidence**: "
                + _cell(row.get("external_outcome_evidence", ""))
            )
            if row.get("known_exclusions"):
                lines.append(
                    "- **Known exclusions**: "
                    + "; ".join(_cell(x) for x in row["known_exclusions"])
                )
            if row.get("transport_limits"):
                lines.append(
                    "- **Transport limits**: "
                    + "; ".join(_cell(x) for x in row["transport_limits"])
                )
            lines.append(
                "- **Maximum licensed claim**: "
                + _cell(row.get("max_licensed_claim", ""))
            )
            if row.get("next_required_evaluation"):
                lines.append(
                    "- **Next required evaluation**: "
                    + _cell(row.get("next_required_evaluation", ""))
                )
            lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", type=Path, default=DEFAULT_MATRIX)
    parser.add_argument(
        "--render",
        action="store_true",
        help="rewrite the generated view from the matrix, then exit",
    )
    args = parser.parse_args(argv)
    if args.render:
        data = json.loads(
            args.matrix.read_text(encoding="utf-8"),
            object_pairs_hook=_reject_duplicate_keys,
        )
        view = REPO_ROOT / data["generated_view"]
        view.write_text(render(data), encoding="utf-8")
        print(f"wrote {view}")
        return 0
    errors = run(args.matrix)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"{len(errors)} stage-capability-matrix violation(s)", file=sys.stderr)
        return 1
    print("PASS: stage capability matrix invariants hold")
    return 0


if __name__ == "__main__":
    sys.exit(main())
