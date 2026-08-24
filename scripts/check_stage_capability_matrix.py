#!/usr/bin/env python3
"""Stage capability/evidence matrix lint + renderer (#745).

Pins shared/contracts/capability/stage_capability_matrix.json — the single
machine-readable source for what each pipeline stage's mechanisms are, what
evidence exists for them, and the maximum claim that evidence licenses — so
capability language can never silently outrun the recorded evidence:

  M1.  Matrix parses, carries the exact schema_version, no unknown top-level
       fields, no duplicate JSON object keys, a positive integer
       stale_after_days (fail-closed: a missing or unparseable matrix is an
       error, never a silent pass; an invalid staleness policy is an error,
       never a fabricated default).
  M2.  task_families equals the frozen TASK_FAMILIES vocabulary exactly,
       including order (the same closed list the #742 profile contract
       consumes — additions require touching this lint in the same commit).
  M3.  Rows are closed shapes: required fields present and non-empty
       (known_exclusions / transport_limits each carry at least one entry —
       write "none known" explicitly rather than an empty list), no unknown
       fields, unique row_id, task_family from the vocabulary,
       mechanism_status and deterministic_conformance from closed enums.
  M4.  behavioral_evidence.status is one of DESIGNED / NOT_RUN / MEASURED /
       MIXED / OUT_OF_SCOPE and the statuses cannot collapse in either
       direction: MEASURED/MIXED require full provenance (eval_ref existing
       in-repo, model, population, measured_at ISO date, result_summary);
       every other status refuses model / population / measured_at /
       result_summary / staleness_note; OUT_OF_SCOPE requires a reason and
       reason is refused elsewhere; eval_ref is allowed on any status (a
       DESIGNED row may name its frozen suite) and existence-checked
       wherever it appears.
  M5.  Every task family has at least one row (no silently uncovered stage).
  M6.  max_licensed_claim is non-empty, and on a row whose behavioral status
       is not MEASURED/MIXED neither the claim nor the mechanism /
       external_outcome_evidence text may contain effectiveness stems
       (improve/outperform/guarantee/proven/state-of-the-art) — conservative
       language discipline, not semantic parsing.
  M7.  Every claim_anchors entry names an existing repo file (repo-relative,
       no absolute paths, resolved path contained in the checkout) and its
       anchor (>= 16 chars) appears VERBATIM in that file, so top-level
       capability claims resolve to a matrix row and fail the build when
       reworded without touching the matrix.
  M8.  A MEASURED/MIXED row older than stale_after_days must carry a
       staleness_note (stale evidence stays visible, never silently current).
  M9.  next_required_evaluation is non-empty except on OUT_OF_SCOPE rows.
  M10. docs/STAGE_CAPABILITY_MATRIX.md is byte-identical to render(matrix)
       (the human view is generated, never hand-drifted).
  M11. A MEASURED/MIXED row whose suite publishes measurement reports
       (measurement-*.json under eval_ref) must bind one via
       measurement_report: the file exists inside eval_ref, parses, its
       measurement_date equals the row's measured_at, and no sibling report
       carries a later measurement_date unless the row says why in a
       staleness_note — so a re-measurement cannot leave a stale row
       silently authoritative.
  M12. deterministic_conformance is falsifiable: CI_GATED/TESTED rows carry
       conformance_pinned_by entries ('path' or 'path::function', existing,
       function defined for .py paths — the degradation-registry D4
       convention); NONE rows carry none.

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
import re
import sys
from functools import lru_cache
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
_ROW_FIELDS = frozenset(_ROW_REQUIRED) | {"claim_anchors", "conformance_pinned_by"}
_MECHANISM_STATUSES = ("IMPLEMENTED", "PARTIAL", "DESIGNED")
_CONFORMANCE_STATUSES = ("CI_GATED", "TESTED", "NONE")
_BEHAVIORAL_STATUSES = ("DESIGNED", "NOT_RUN", "MEASURED", "MIXED", "OUT_OF_SCOPE")
_MEASURED_ONLY_FIELDS = ("model", "population", "measured_at", "result_summary", "staleness_note")
_EVIDENCE_FIELDS = frozenset(
    ("status", "reason", "eval_ref", "measurement_report") + _MEASURED_ONLY_FIELDS
)
# Conservative effectiveness stems: forbidden in claim-bearing prose unless the
# row's behavioral evidence is MEASURED/MIXED (which records what was measured).
# Never licensed by any recorded evaluation, on any row.
_NEVER_LICENSED_STEMS = (
    "guarantee",
    "proven",
    "state-of-the-art",
    "state of the art",
)
# Licensed only when the row's behavioral evidence is MEASURED/MIXED.
_MEASURED_LICENSED_STEMS = (
    "improv",
    "outperform",
)
_PERCENT_RE = re.compile(r"\d+(?:\.\d+)?\s*(?:%|percent)")
_CLAIM_FIELDS = ("max_licensed_claim", "mechanism", "external_outcome_evidence")
_MIN_ANCHOR_LEN = 16
_REPORT_NAME_RE = re.compile(r"^measurement-.+\.json$")

# Shipped-inventory locks (degradation-registry D5 convention): silently
# deleting a shipped row or a shipped row's claim anchors cannot pass —
# adding/removing requires touching this lint in the same commit.
_EXPECTED_ROW_IDS = frozenset({
    "rq_formation.wording_advisory",
    "rq_formation.ideation_diversity",
    "rq_formation.research_workflow_profile",
    "rq_formation.inquiry_branch_ledger",
    "retrieval.citation_existence_gate",
    "retrieval.claim_standing_probe",
    "methodology.blueprint",
    "synthesis.cross_source",
    "drafting.citation_emission",
    "integrity_check.claim_verification",
    "integrity_check.tortured_phrase_screen",
    "integrity_check.inquiry_branch_ledger",
    "review.seeded_defect_panel",
    "review.calibration",
    "revision.claim_drift_guard",
    "finalization.format_and_disclosure",
})
_EXPECTED_ANCHOR_MINIMUMS = {
    "rq_formation.wording_advisory": 1,
    "retrieval.citation_existence_gate": 1,
    "revision.claim_drift_guard": 1,
}
_PIN_RE = re.compile(r"^(?P<path>[^:]+)(::(?P<func>[A-Za-z_][A-Za-z0-9_]*))?$")


def _reject_duplicate_keys(pairs):
    seen = set()
    for key, _ in pairs:
        if key in seen:
            raise ValueError(f"duplicate JSON object key: {key!r}")
        seen.add(key)
    return dict(pairs)


def _load(path: Path) -> dict:
    """Strict matrix loader shared by the lint and --render."""
    data = json.loads(
        path.read_text(encoding="utf-8"), object_pairs_hook=_reject_duplicate_keys
    )
    if not isinstance(data, dict):
        raise ValueError("matrix root must be an object")
    return data


def _contained(relative) -> Path | None:
    """Resolve a repo-relative path, refusing absolute paths and escapes."""
    if not isinstance(relative, str) or not relative.strip():
        return None
    if relative.startswith(("/", "\\")) or ":" in relative.split("/")[0]:
        return None
    target = (REPO_ROOT / relative).resolve()
    try:
        target.relative_to(REPO_ROOT)
    except ValueError:
        return None
    return target


@lru_cache(maxsize=None)
def _read_repo_file(relative: str) -> str | None:
    """Containment-checked, memoized repo-relative read (None = unreadable)."""
    target = _contained(relative)
    if target is None or not target.is_file():
        return None
    return target.read_text(encoding="utf-8")


def _nonempty_str(value) -> bool:
    return isinstance(value, str) and value.strip() != ""


def _nonempty_str_list(value) -> bool:
    return (
        isinstance(value, list)
        and len(value) >= 1
        and all(_nonempty_str(v) for v in value)
    )


def _check_behavioral(row_id: str, ev, today: datetime.date,
                      stale_after_days: int | None, errors: list[str]) -> None:
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
    eval_ref = ev.get("eval_ref")
    if eval_ref is not None:
        resolved = _contained(eval_ref)
        if resolved is None or not resolved.is_dir():
            errors.append(
                f"{prefix} eval_ref {eval_ref!r} must be an existing "
                "repo-contained suite directory"
            )
            eval_ref = None
    measured = status in ("MEASURED", "MIXED")
    if measured:
        if not _nonempty_str(ev.get("eval_ref")):
            errors.append(f"{prefix} {status} requires non-empty 'eval_ref' provenance")
        for field in ("model", "population", "measured_at", "result_summary"):
            if not _nonempty_str(ev.get(field)):
                errors.append(
                    f"{prefix} {status} requires non-empty {field!r} provenance"
                )
        measured_date = None
        measured_at = ev.get("measured_at")
        if _nonempty_str(measured_at):
            try:
                measured_date = datetime.date.fromisoformat(measured_at)
            except ValueError:
                errors.append(
                    f"{prefix} measured_at {measured_at!r} is not an ISO date"
                )
        if measured_date is not None and measured_date > today:
            errors.append(
                f"{prefix} measured_at {measured_date.isoformat()} is in the "
                "future"
            )
            measured_date = None
        if measured_date is not None and stale_after_days is not None:
            age = (today - measured_date).days
            if age > stale_after_days and not _nonempty_str(ev.get("staleness_note")):
                errors.append(
                    f"M8 row {row_id}: measurement {measured_at} is older than "
                    f"{stale_after_days} days and has no staleness_note"
                )
        _check_report_binding(row_id, ev, eval_ref, measured_date, errors)
    else:
        for field in _MEASURED_ONLY_FIELDS + ("measurement_report",):
            if field in ev:
                errors.append(
                    f"{prefix} {status} row must not carry {field!r} — measurement "
                    "provenance cannot ride an unrun or out-of-scope evaluation"
                )
        if status == "OUT_OF_SCOPE":
            if not _nonempty_str(ev.get("reason")):
                errors.append(f"{prefix} OUT_OF_SCOPE requires a non-empty reason")
        elif "reason" in ev:
            errors.append(f"{prefix} 'reason' is only lawful on OUT_OF_SCOPE rows")
    if measured and "reason" in ev:
        errors.append(f"{prefix} 'reason' is only lawful on OUT_OF_SCOPE rows")


def _check_report_binding(row_id: str, ev: dict, eval_ref: str | None,
                          measured_date: datetime.date | None,
                          errors: list[str]) -> None:
    """M11: bind measured rows to their suite's latest measurement report."""
    prefix = f"M11 row {row_id}:"
    suite_dir = (REPO_ROOT / eval_ref) if eval_ref else None
    published = (
        sorted(suite_dir.glob("measurement-*.json"))
        if suite_dir is not None and suite_dir.is_dir()
        else []
    )
    binding = ev.get("measurement_report")
    if binding is None:
        if published:
            errors.append(
                f"{prefix} suite {eval_ref!r} publishes measurement reports; "
                "bind one via 'measurement_report'"
            )
        return
    if not _nonempty_str(binding):
        errors.append(f"{prefix} measurement_report must be a non-empty path")
        return
    report_path = REPO_ROOT / binding
    if not _REPORT_NAME_RE.fullmatch(report_path.name):
        errors.append(
            f"{prefix} measurement_report {binding!r} must be a "
            "measurement-*.json report file"
        )
        return
    if suite_dir is None or report_path.parent != suite_dir:
        errors.append(
            f"{prefix} measurement_report {binding!r} must live directly inside "
            f"eval_ref {eval_ref!r}"
        )
        return
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        errors.append(f"{prefix} cannot load measurement_report {binding!r}: {exc}")
        return
    if not isinstance(report, dict):
        errors.append(
            f"{prefix} measurement_report {binding!r} must be a JSON object"
        )
        return
    # heldout-measurement/1.0 uses measurement_date; pre-#654 legacy reports
    # carry measured_at instead — accept either, prefer the contract field.
    report_date = report.get("measurement_date") or report.get("measured_at")
    if measured_date is not None and report_date != measured_date.isoformat():
        errors.append(
            f"{prefix} measured_at {measured_date.isoformat()} does not equal the "
            f"bound report's measurement_date {report_date!r}"
        )
    dates = []
    for sibling in published:
        try:
            sibling_report = json.loads(sibling.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            errors.append(
                f"{prefix} sibling report {sibling.name!r} is unreadable "
                f"({exc}) — supersession cannot be assessed"
            )
            continue
        if not isinstance(sibling_report, dict):
            errors.append(
                f"{prefix} sibling report {sibling.name!r} is not a JSON "
                "object — supersession cannot be assessed"
            )
            continue
        sibling_date = sibling_report.get("measurement_date") or sibling_report.get(
            "measured_at"
        )
        if isinstance(sibling_date, str):
            dates.append(sibling_date)
    if (
        isinstance(report_date, str)
        and dates
        and max(dates) > report_date
        and not _nonempty_str(ev.get("staleness_note"))
    ):
        errors.append(
            f"{prefix} a sibling report dated {max(dates)} supersedes the bound "
            f"{report_date} report — rebind or explain in a staleness_note"
        )


def _status(row) -> str | None:
    ev = row.get("behavioral_evidence")
    return ev.get("status") if isinstance(ev, dict) else None


def _check_claim_language(row, errors: list[str]) -> None:
    row_id = row.get("row_id", "?")
    if not _nonempty_str(row.get("max_licensed_claim")):
        errors.append(f"M6 row {row_id}: max_licensed_claim must be non-empty")
    status = _status(row)
    measured = status in ("MEASURED", "MIXED")
    for field in _CLAIM_FIELDS:
        value = row.get(field)
        if not isinstance(value, str):
            continue
        lowered = value.lower()
        for stem in _NEVER_LICENSED_STEMS:
            if stem in lowered:
                errors.append(
                    f"M6 row {row_id}: {field} contains stem {stem!r}, which "
                    "no recorded evaluation licenses on any row"
                )
        if measured:
            continue
        for stem in _MEASURED_LICENSED_STEMS:
            if stem in lowered:
                errors.append(
                    f"M6 row {row_id}: {field} contains effectiveness stem "
                    f"{stem!r} but behavioral evidence is {status}, not "
                    "MEASURED/MIXED"
                )
        if _PERCENT_RE.search(lowered):
            errors.append(
                f"M6 row {row_id}: {field} states a percentage but behavioral "
                f"evidence is {status}, not MEASURED/MIXED"
            )


def _check_anchors(row, errors: list[str]) -> None:
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
        content = (
            _read_repo_file(anchor["file"])
            if _nonempty_str(anchor["file"])
            else None
        )
        if content is None:
            errors.append(
                f"M7 row {row_id}: anchor file {anchor['file']!r} is not a "
                "readable repo-relative file inside the checkout"
            )
            continue
        if text not in content:
            errors.append(
                f"M7 row {row_id}: anchor not found verbatim in "
                f"{anchor['file']!r}: {text[:60]!r}"
            )


def _check_conformance_pins(row, errors: list[str]) -> None:
    row_id = row.get("row_id", "?")
    conformance = row.get("deterministic_conformance")
    pins = row.get("conformance_pinned_by")
    if conformance == "NONE":
        if pins is not None:
            errors.append(
                f"M12 row {row_id}: NONE conformance must not carry "
                "conformance_pinned_by"
            )
        return
    if conformance not in ("CI_GATED", "TESTED"):
        return  # M3 already reported the bad enum value
    if not _nonempty_str_list(pins):
        errors.append(
            f"M12 row {row_id}: {conformance} requires a non-empty "
            "conformance_pinned_by list ('path' or 'path::function')"
        )
        return
    for pin in pins:
        match = _PIN_RE.match(pin)
        if match is None:
            errors.append(f"M12 row {row_id}: malformed pin {pin!r}")
            continue
        path, func = match.group("path"), match.group("func")
        content = _read_repo_file(path)
        if content is None:
            errors.append(
                f"M12 row {row_id}: pin {pin!r} names a missing file"
            )
            continue
        if func is not None:
            if not path.endswith(".py"):
                errors.append(
                    f"M12 row {row_id}: '::function' pins require a .py path "
                    f"({pin!r})"
                )
            elif not re.search(rf"^def {re.escape(func)}\(", content, re.M):
                errors.append(
                    f"M12 row {row_id}: pin {pin!r} names a function not "
                    "defined in the file"
                )


def run(
    matrix_path: Path,
    *,
    check_view: bool = True,
    view_path: Path | None = None,
    today: datetime.date | None = None,
    inventory_lock: bool = True,
) -> list[str]:
    errors: list[str] = []
    today = today or datetime.date.today()
    try:
        data = _load(matrix_path)
    except (OSError, ValueError) as exc:
        return [f"M1: cannot load matrix {matrix_path}: {exc}"]
    shape_ok = set(data) == _TOP_FIELDS
    if not shape_ok:
        missing = _TOP_FIELDS - set(data)
        unknown = set(data) - _TOP_FIELDS
        errors.append(
            f"M1: top-level fields missing={sorted(missing)} unknown={sorted(unknown)}"
        )
    if data.get("schema_version") != _SCHEMA_VERSION:
        errors.append(
            f"M1: schema_version must be {_SCHEMA_VERSION!r}, "
            f"got {data.get('schema_version')!r}"
        )
    stale_after_days = data.get("stale_after_days")
    if type(stale_after_days) is not int or stale_after_days <= 0:
        errors.append("M1: stale_after_days must be a positive integer")
        stale_after_days = None  # skip M8 rather than invent a policy
    if not shape_ok:
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
        unknown = set(row) - _ROW_FIELDS
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
            if list_field in row and not _nonempty_str_list(row[list_field]):
                errors.append(
                    f"M3 row {row_id}: {list_field} must carry at least one "
                    "non-empty string (write 'none known' explicitly)"
                )

        _check_behavioral(
            row_id, row.get("behavioral_evidence"), today, stale_after_days, errors
        )
        _check_claim_language(row, errors)
        _check_anchors(row, errors)
        _check_conformance_pins(row, errors)

        status = _status(row)
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

    if inventory_lock:
        missing_rows = _EXPECTED_ROW_IDS - seen_ids
        if missing_rows:
            errors.append(
                "M13: shipped row inventory drift — rows missing: "
                f"{sorted(missing_rows)} (removing a row requires editing "
                "_EXPECTED_ROW_IDS in the same commit)"
            )
        anchors_by_id = {
            r.get("row_id"): (
                len(r["claim_anchors"])
                if isinstance(r.get("claim_anchors"), list)
                else 0
            )
            for r in rows
            if isinstance(r, dict)
        }
        for row_id, minimum in _EXPECTED_ANCHOR_MINIMUMS.items():
            if anchors_by_id.get(row_id, 0) < minimum:
                errors.append(
                    f"M13 row {row_id}: shipped claim-anchor minimum is "
                    f"{minimum}; removing an anchor requires editing "
                    "_EXPECTED_ANCHOR_MINIMUMS in the same commit"
                )

    if check_view:
        target = view_path or DEFAULT_VIEW
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


def _flat(text: str) -> str:
    return " ".join(str(text).splitlines())


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
            lines.append(f"- **Mechanism**: {_flat(row.get('mechanism', ''))}")
            conformance_line = (
                f"- **Mechanism status**: {row.get('mechanism_status', '')} / "
                f"deterministic conformance: {row.get('deterministic_conformance', '')}"
            )
            if row.get("conformance_pinned_by"):
                conformance_line += (
                    " (pinned by "
                    + "; ".join(_flat(p) for p in row["conformance_pinned_by"])
                    + ")"
                )
            lines.append(conformance_line)
            detail = [f"**Behavioral evidence**: {status}"]
            if status in ("MEASURED", "MIXED"):
                detail.append(
                    f"— {_flat(ev.get('result_summary', ''))} "
                    f"({_flat(ev.get('eval_ref', ''))}; model {_flat(ev.get('model', ''))}; "
                    f"population {_flat(ev.get('population', ''))}; {ev.get('measured_at', '')})"
                )
                if ev.get("measurement_report"):
                    detail.append(f"— report: {_flat(ev['measurement_report'])}")
            if ev.get("staleness_note"):
                detail.append(f"— STALE: {_flat(ev['staleness_note'])}")
            if status == "OUT_OF_SCOPE" and ev.get("reason"):
                detail.append(f"— {_flat(ev['reason'])}")
            lines.append("- " + " ".join(detail))
            lines.append(
                "- **External/human outcome evidence**: "
                + _flat(row.get("external_outcome_evidence", ""))
            )
            if row.get("known_exclusions"):
                lines.append(
                    "- **Known exclusions**: "
                    + "; ".join(_flat(x) for x in row["known_exclusions"])
                )
            if row.get("transport_limits"):
                lines.append(
                    "- **Transport limits**: "
                    + "; ".join(_flat(x) for x in row["transport_limits"])
                )
            if row.get("claim_anchors"):
                lines.append(
                    "- **Claim anchors**: "
                    + "; ".join(
                        f"{a.get('file')} — \"{_flat(a.get('anchor', ''))}\""
                        for a in row["claim_anchors"]
                        if isinstance(a, dict)
                    )
                )
            lines.append(
                "- **Maximum licensed claim**: "
                + _flat(row.get("max_licensed_claim", ""))
            )
            if row.get("next_required_evaluation"):
                lines.append(
                    "- **Next required evaluation**: "
                    + _flat(row.get("next_required_evaluation", ""))
                )
            lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--render",
        action="store_true",
        help="validate, then rewrite the generated view from the matrix",
    )
    args = parser.parse_args(argv)
    if args.render:
        errors = run(DEFAULT_MATRIX, check_view=False)
        if errors:
            for error in errors:
                print(f"ERROR: {error}", file=sys.stderr)
            print("refusing to render an invalid matrix", file=sys.stderr)
            return 1
        DEFAULT_VIEW.write_text(render(_load(DEFAULT_MATRIX)), encoding="utf-8")
        print(f"wrote {DEFAULT_VIEW}")
        return 0
    errors = run(DEFAULT_MATRIX)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"{len(errors)} stage-capability-matrix violation(s)", file=sys.stderr)
        return 1
    print("PASS: stage capability matrix invariants hold")
    return 0


if __name__ == "__main__":
    sys.exit(main())
