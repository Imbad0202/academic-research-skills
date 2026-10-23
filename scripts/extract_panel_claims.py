#!/usr/bin/env python3
"""Extract the claims a review panel makes, for the factuality audit (#1002).

Reads E4 raw panel bundles (``evals/heldout/reviewer_seeded_defects/runs/raw``)
and never changes them. No model call. One claim is:

  - one ``### W<n>: <title>`` subsection of the ``## Review Body`` in the Phase 2
    report of the EIC, Methodology, Domain, or Perspective seat (title, body,
    and Evidence Anchor, verbatim); or
  - one row of the Devil's Advocate ``#### CRITICAL`` or ``#### MAJOR`` table,
    read with the shared DA table parser in ``check_panel_synthesis.py``:
    every cell except ``#``, the Confidence columns, and the Evidence Anchor,
    verbatim and in column order, one paragraph each, then the Evidence Anchor
    as ``**Evidence Anchor**: <anchor>``, the line a weakness ends with. Seats
    name the columns differently (``Issue`` or ``Finding``, sometimes ``Why it
    matters`` or ``Required Remedy``), so every such column is kept, and the
    column names are left out so a row reads like a weakness.

The judge-visible text keeps what the reviewer wrote, so it can still show the
seat (a DA row has no title; a Perspective weakness can name its outsider
view). The blinding is of metadata: the seat label, the file, and the order.

Strengths are not claims here (the #1002 plan scope: only what can move a
decision).

A bundle is read when its run record (``runs/<name>.json``) says
``score_eligible: true`` and names a ``raw_bundle`` directory that resolves
inside ``runs/raw/``. No path that resolves under the suite's ``manifests/``
directory is ever opened (the suite's own ``manifests/`` is fixed, whatever
``--runs`` says); a run record, report, or gate log that is a symlink or
resolves outside its directory is refused, and a second record naming the same
bundle is listed, not read again. For
each seat the script reads the highest Phase 2 attempt whose gate log says
``PHASE-CONFORMANCE: PASS``; a seat with no passing attempt is listed in the
summary and contributes no claim.

Two files go to ``--out``:

  claims.jsonl  {claim_id, bundle, fixture, text}: what the auditor sees. The
                seat is held back, and claims are ordered by a hash of their
                source, so neither the id nor the order shows the seat.
  key.jsonl     {claim_id, bundle, fixture, condition, replicate, seat,
                 source_file, source_sha256, finding_id}: the join back to the
                source, for scoring after the audit. Never sent to the auditor.

The last stdout line is one JSON object of counts (the eval-plan summarizer
contract). The exit code is 0 only when every eligible seat had a passing
attempt, every DA report parsed, and, with ``--expect-bundles`` and
``--expect-claims``, the counts equal the expected ones; otherwise it is 1 and
the files are still written for inspection, or 2 when no bundle was found.

    python3 scripts/extract_panel_claims.py --runs evals/heldout/reviewer_seeded_defects/runs --out <dir>
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    from check_panel_synthesis import (
        ReportError,
        _markdown_cells,
        _parse_da_table_block,
        _require_single_da_table_heading,
        split_sections,
        strip_fences,
    )
except ImportError:  # pragma: no cover - dual-path import
    from scripts.check_panel_synthesis import (
        ReportError,
        _markdown_cells,
        _parse_da_table_block,
        _require_single_da_table_heading,
        split_sections,
        strip_fences,
    )

CHECKER = "extract_panel_claims/1"
# The suite's held-out manifests, fixed: a --runs argument cannot move it.
MANIFESTS = (Path(__file__).resolve().parent.parent / "evals" / "heldout" / "reviewer_seeded_defects"
             / "manifests").resolve()
W_SEATS = ("eic", "methodology", "domain", "perspective")
DA_SEAT = "da"
_W_HEADING_RE = re.compile(r"^###\s+(W[1-9]\d*):\s*(.+?)\s*$")
# A W subsection ends at the next heading of its own level or higher.
_SECTION_END_RE = re.compile(r"^#{1,3}\s")
_ATTEMPT_RE = re.compile(r"\.phase2\.a([1-9]\d*)\.md$")
_PASS = "PHASE-CONFORMANCE: PASS"


def passing_attempt(bundle: Path, seat: str) -> Path | None:
    """The highest Phase 2 attempt of ``seat`` whose gate log passed. A gate
    log that is a symlink, or resolves outside the bundle, does not pass and
    is not read."""
    best: tuple[int, Path] | None = None
    for path in bundle.glob(f"{seat}.phase2.a*.md"):
        m = _ATTEMPT_RE.search(path.name)
        if not m:
            continue
        log = path.with_name(path.name[:-3] + ".gate.log")
        try:
            passed = _safe(log, bundle) and _PASS in log.read_text(encoding="utf-8")
        except OSError:
            passed = False
        if passed and (best is None or int(m.group(1)) > best[0]):
            best = (int(m.group(1)), path)
    return best[1] if best else None


def w_claims(text: str) -> list[tuple[str, str]]:
    """Return (finding_id, text) for each ``### W<n>`` subsection of the Review Body."""
    sections, _dupes = split_sections(strip_fences(text, preserve_fenced_blocks=True))
    body = sections.get("Review Body", [])
    claims: list[tuple[str, str]] = []
    current: tuple[str, list[str]] | None = None
    for line in body:
        m = _W_HEADING_RE.match(line)
        if m or _SECTION_END_RE.match(line):
            if current:
                claims.append((current[0], "\n".join(current[1]).strip()))
            current = (m.group(1), [m.group(2)]) if m else None
            continue
        if current:
            current[1].append(line)
    if current:
        claims.append((current[0], "\n".join(current[1]).strip()))
    return claims


def da_claims(text: str, path: str) -> list[tuple[str, str]]:
    """Return (finding_id, text) for each CRITICAL and MAJOR row of the DA report."""
    sections, _dupes = split_sections(strip_fences(text, preserve_fenced_blocks=True))
    review = sections.get("Review Body", [])
    critical = _require_single_da_table_heading(review, "CRITICAL", path)
    major = _require_single_da_table_heading(review, "MAJOR", path)
    claims: list[tuple[str, str]] = []
    for heading, start, end in (("CRITICAL", critical, major), ("MAJOR", major, len(review))):
        rows, id_col, anchor_col = _parse_da_table_block(review, heading, path, start, end)
        header = _markdown_cells(next(line for line in review[start + 1:end] if line.strip()))
        shown = [i for i, name in enumerate(header)
                 if i not in (id_col, anchor_col) and not name.startswith("Confidence")]
        for n, cells in enumerate(rows, start=1):
            finding_id = cells[id_col] or f"{heading[0]}{n}"
            parts = [cells[i] for i in shown if cells[i]]
            parts.append(f"**Evidence Anchor**: {cells[anchor_col]}")
            claims.append((finding_id, "\n\n".join(parts)))
    return claims


def _protected_roots(runs: Path) -> tuple[Path, Path]:
    """The suite's manifests directory, and the ``manifests`` beside ``runs``."""
    return MANIFESTS, (runs.resolve().parent / "manifests").resolve()


def _inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def guard_runs_dir(runs: Path) -> None:
    """Refuse a runs directory that is, or holds, or sits in a manifests directory."""
    resolved = runs.resolve()
    for protected in _protected_roots(runs):
        if _inside(resolved, protected) or _inside(protected, resolved):
            raise SystemExit(f"refused: {runs} overlaps the held-out manifests directory")


def _safe(path: Path, root: Path) -> bool:
    """True when ``path`` is no symlink, resolves inside ``root``, and is in no
    manifests directory."""
    resolved = path.resolve()
    return (not path.is_symlink() and _inside(resolved, root.resolve())
            and not any(_inside(resolved, p) for p in (MANIFESTS, (root.resolve().parent / "manifests").resolve())))


def eligible_bundles(runs: Path, summary: dict[str, Any] | None = None) -> list[tuple[dict[str, Any], Path]]:
    found = []
    raw_root = (runs / "raw").resolve()
    protected = _protected_roots(runs)
    seen: set[Path] = set()
    for record_path in sorted(runs.glob("*.json")):
        if not _safe(record_path, runs):
            if summary is not None:
                summary["refused_bundle_paths"].append(record_path.name)
            continue
        try:
            record = json.loads(record_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            if summary is not None:
                summary["unreadable_records"].append(record_path.name)
            continue
        raw = str(record.get("raw_bundle") or "")
        if record.get("score_eligible") is not True or not raw:
            continue
        bundle = (runs / raw).resolve()
        if Path(raw).is_absolute() or not _inside(bundle, raw_root) or any(_inside(bundle, p) for p in protected):
            if summary is not None:
                summary["refused_bundle_paths"].append(record_path.name)
            continue
        if bundle in seen:
            if summary is not None:
                summary["duplicate_bundle_records"].append(record_path.name)
            continue
        if bundle.is_dir():
            seen.add(bundle)
            found.append((record, bundle))
    return found


def extract(runs: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    guard_runs_dir(runs)
    summary: dict[str, Any] = {"checker": CHECKER, "bundles": 0, "claims": 0,
                               "by_seat": {s: 0 for s in (*W_SEATS, DA_SEAT)},
                               "seats_without_passing_attempt": [], "unparsed_da_reports": [],
                               "unreadable_records": [], "refused_bundle_paths": [],
                               "duplicate_bundle_records": []}
    for record, bundle in eligible_bundles(runs, summary):
        summary["bundles"] += 1
        for seat in (*W_SEATS, DA_SEAT):
            path = passing_attempt(bundle, seat)
            if path is None:
                summary["seats_without_passing_attempt"].append(f"{bundle.name}/{seat}")
                continue
            if not _safe(path, bundle):
                summary["refused_bundle_paths"].append(f"{bundle.name}/{path.name}")
                continue
            raw = path.read_bytes()
            text = raw.decode("utf-8").replace("\r\n", "\n")
            try:
                found = da_claims(text, path.name) if seat == DA_SEAT else w_claims(text)
            except ReportError:
                summary["unparsed_da_reports"].append(f"{bundle.name}/{path.name}")
                continue
            for finding_id, claim_text in found:
                source = f"{bundle.name}/{path.name}#{finding_id}"
                rows.append({
                    "order": hashlib.sha256(source.encode("utf-8")).hexdigest(),
                    "bundle": bundle.name, "fixture": record.get("fixture"),
                    "condition": record.get("condition"), "replicate": record.get("replicate"),
                    "seat": seat, "source_file": f"{bundle.name}/{path.name}",
                    "source_sha256": hashlib.sha256(raw).hexdigest(),
                    "finding_id": finding_id, "text": claim_text,
                })
                summary["by_seat"][seat] += 1
    rows.sort(key=lambda r: r["order"])
    claims, key = [], []
    for n, row in enumerate(rows, start=1):
        claim_id = f"c{n:04d}"
        claims.append({"claim_id": claim_id, "bundle": row["bundle"], "fixture": row["fixture"],
                       "text": row["text"]})
        key.append({"claim_id": claim_id, **{k: row[k] for k in (
            "bundle", "fixture", "condition", "replicate", "seat", "source_file",
            "source_sha256", "finding_id")}})
    summary["claims"] = len(claims)
    return claims, key, summary


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Extract panel claims for the #1002 audit.")
    parser.add_argument("--runs", type=Path, required=True, help="The suite's runs/ directory.")
    parser.add_argument("--out", type=Path, required=True, help="Directory for claims.jsonl and key.jsonl.")
    parser.add_argument("--expect-bundles", type=int, help="Fail unless exactly this many bundles are read.")
    parser.add_argument("--expect-claims", type=int, help="Fail unless exactly this many claims are read.")
    args = parser.parse_args(argv)
    claims, key, summary = extract(args.runs)
    args.out.mkdir(parents=True, exist_ok=True)
    _write_jsonl(args.out / "claims.jsonl", claims)
    _write_jsonl(args.out / "key.jsonl", key)
    summary["problems"] = problems(summary, args.expect_bundles, args.expect_claims)
    (args.out / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
                                           encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    if not summary["bundles"]:
        return 2
    return 1 if summary["problems"] else 0


def problems(summary: dict[str, Any], expect_bundles: int | None, expect_claims: int | None) -> list[str]:
    found = [f"{k}: {len(summary[k])}" for k in ("seats_without_passing_attempt", "unparsed_da_reports",
                                                 "unreadable_records", "refused_bundle_paths",
                                                 "duplicate_bundle_records") if summary[k]]
    if expect_bundles is not None and summary["bundles"] != expect_bundles:
        found.append(f"bundles: {summary['bundles']} != expected {expect_bundles}")
    if expect_claims is not None and summary["claims"] != expect_claims:
        found.append(f"claims: {summary['claims']} != expected {expect_claims}")
    return found


if __name__ == "__main__":
    sys.exit(main())
