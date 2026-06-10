#!/usr/bin/env python3
"""verify_submission_package CLI — deterministic submission-package verifier
(#394 Slice 1: CLI skeleton + Family C reference integrity).

    python scripts/verify_submission_package.py <package_dir> \
        [--passport passport.yaml] [--join-map map.yaml] [--report-out path]

Reads the files in an output package and runs the Family C two-way reference
integrity check (in-text citation keys <-> reference-list entries), writing
`submission_verification_report.json` (validating against
shared/contracts/submission/submission_verification_report.schema.json) plus a
human-readable summary to stdout.

Design contract (spec docs/design/2026-06-10-394-submission-package-verifier-spec.md):

- Detection is unconditional; terminality is the policy evaluator's job. This
  script NEVER reads `terminal_policies` (§5.3) — `policy_slug` is emitted null.
- The joined marker path is deterministic; it needs a real prose-reference join
  (§3.3): the run's `citation_verification_summary[]` (via --passport), an
  explicit scholar-supplied join map (--join-map), or a parsed `.bib` whose keys
  map to slugs by the documented identity relation (draft_writer_agent.md: the
  slug IS the corpus `citation_key`). Markers with NO join source report
  `not_checked(missing prose-reference join)` — never a guessed comparison.
- Fallback extraction (`\\cite{}` for LaTeX, author-year regex for Markdown
  text) is heuristic-classed: advisory-only, `strict_eligible: false`, header
  `extraction_path: best_effort` (§3.3).
- Every check reports pass | fail | warn | not_checked; `not_checked` is
  surfaced in the header count, never folded into pass (§1.4).
- `package_fingerprint` reuses the audit-snapshot manifest convention
  (scripts/audit_snapshot.py; spec §10 open item 3, adjudicated at slice 1):
  `<relative-path>:<sha256>` lines, byte-sorted, trailing newline, fingerprint
  = SHA-256 of the manifest text. The report file itself is excluded.

Exit codes: 0 = no fail (warns allowed) and everything checked; 1 = >=1 fail;
2 = usage/IO error; 3 = no fail but >=1 not_checked ("passed what was
checkable", §8).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Optional

import yaml

REPORT_BASENAME = "submission_verification_report.json"

# Files scanned for in-text citations. provenance_summary.md is an advisory
# carrier that legitimately repeats ref_slugs / citation_keys (#333) — scanning
# it would manufacture false in-text hits.
_MANUSCRIPT_SUFFIXES = {".md", ".tex", ".txt"}
_SCAN_EXCLUDED_NAMES = {"provenance_summary.md", REPORT_BASENAME}

# v3.7.1+ marker grammar: `<!--ref:slug-->` optionally followed by status /
# advisory / policy tokens after the first space (e.g. `<!--ref:slug ok-->`).
# Anchor markers (`<!--anchor:...-->`) are a different grammar and never match.
_REF_MARKER_RE = re.compile(r"<!--ref:([^\s>]+)(?:\s[^>]*)?-->")

# BibTeX entry heads: `@article{key,`. @comment/@preamble/@string carry no
# citation key and are excluded.
_BIB_KEY_RE = re.compile(
    r"^\s*@(?!comment|preamble|string)[A-Za-z]+\s*\{\s*([^,\s}]+)\s*,",
    re.IGNORECASE | re.MULTILINE,
)

_LOCATION_CAP = 5  # findings listed per check detail before truncation


def sha256_hex(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def compute_package_fingerprint(package_dir: Path) -> str:
    """Audit-snapshot manifest convention over the package files (§10 item 3):
    one `<package-relative-path>:<sha256>` line per file, LC_ALL=C byte-sorted,
    trailing newline; fingerprint = SHA-256 of the manifest text. The report
    file is excluded — the report cannot fingerprint its own bytes."""
    lines = []
    for path in sorted(package_dir.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(package_dir).as_posix()
        if rel == REPORT_BASENAME:
            continue
        lines.append(f"{rel}:{sha256_hex(path.read_bytes())}")
    lines.sort()  # byte sort over the composed line, matching audit_snapshot
    manifest_text = "\n".join(lines) + "\n"
    return sha256_hex(manifest_text.encode("utf-8"))


def _manuscript_files(package_dir: Path) -> list:
    return sorted(
        p for p in package_dir.rglob("*")
        if p.is_file()
        and p.suffix.lower() in _MANUSCRIPT_SUFFIXES
        and p.name not in _SCAN_EXCLUDED_NAMES
    )


def _bib_files(package_dir: Path) -> list:
    return sorted(p for p in package_dir.rglob("*.bib") if p.is_file())


def extract_ref_markers(package_dir: Path) -> "dict[str, str]":
    """{slug: first-seen package-relative location} from <!--ref:slug--> markers."""
    found: "dict[str, str]" = {}
    for path in _manuscript_files(package_dir):
        text = path.read_text(encoding="utf-8", errors="replace")
        rel = path.relative_to(package_dir).as_posix()
        for m in _REF_MARKER_RE.finditer(text):
            found.setdefault(m.group(1), rel)
    return found


def parse_bib_keys(package_dir: Path) -> "set[str]":
    keys: "set[str]" = set()
    for path in _bib_files(package_dir):
        text = path.read_text(encoding="utf-8", errors="replace")
        keys.update(_BIB_KEY_RE.findall(text))
    return keys


def _check(check_id: str, status: str, detail: str, *,
           signal_class: str = "deterministic",
           location: "Optional[str]" = None) -> "dict[str, Any]":
    # strict_eligible mirrors signal_class for Family C (§3.3: deterministic on
    # the joined marker path; the fallback path is heuristic-classed,
    # advisory-only). The schema additionally forbids heuristic+strict.
    return {
        "id": check_id,
        "family": "reference_integrity",
        "signal_class": signal_class,
        "strict_eligible": signal_class == "deterministic",
        "status": status,
        "detail": detail,
        "location": location,
    }


def _not_checked_pair(reason: str) -> "list[dict[str, Any]]":
    return [
        _check("C1", "not_checked", reason),
        _check("C2", "not_checked", reason),
    ]


def _listed(keys: "set[str]") -> str:
    shown = sorted(keys)[:_LOCATION_CAP]
    extra = len(keys) - len(shown)
    listing = ", ".join(shown)
    if extra > 0:
        listing += f", … (+{extra} more)"
    return listing


def _compare_sets(in_text: "dict[str, str]", reference_keys: "set[str]",
                  *, signal_class: str, in_text_label: str,
                  reference_label: str) -> "list[dict[str, Any]]":
    """Two-way set check (§3.3): orphan in-text citation = fail (C1); uncited
    reference entry = warn (C2 — some venues allow further-reading entries)."""
    orphans = {k for k in in_text if k not in reference_keys}
    uncited = reference_keys - set(in_text)
    checks = []
    if orphans:
        first_loc = min(in_text[k] for k in orphans)
        checks.append(_check(
            "C1", "fail",
            f"{len(orphans)} in-text citation(s) absent from {reference_label}: "
            f"{_listed(orphans)} [{in_text_label}]",
            signal_class=signal_class, location=first_loc))
    else:
        checks.append(_check(
            "C1", "pass",
            f"all {len(in_text)} in-text citation(s) present in "
            f"{reference_label} [{in_text_label}]",
            signal_class=signal_class))
    if uncited:
        checks.append(_check(
            "C2", "warn",
            f"{len(uncited)} reference entr(ies) never cited in text: "
            f"{_listed(uncited)} [{in_text_label}]",
            signal_class=signal_class))
    else:
        checks.append(_check(
            "C2", "pass",
            f"all {len(reference_keys)} reference entr(ies) cited in text "
            f"[{in_text_label}]",
            signal_class=signal_class))
    return checks


def _load_yaml(path: Path) -> "dict[str, Any]":
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"expected a YAML mapping in {path}")
    return data


def _join_from_passport(passport: "dict[str, Any]") -> "dict[str, str]":
    """{ref_slug: citation_key} from the passport's
    citation_verification_summary[] rows (the per-citation prose join the
    Stage 4->5 run already established, §3.3)."""
    join: "dict[str, str]" = {}
    for row in passport.get("citation_verification_summary") or []:
        slug = row.get("ref_slug")
        key = row.get("citation_key")
        if isinstance(slug, str) and slug and isinstance(key, str) and key:
            join[slug] = key
    return join


def _corpus_keys(passport: "dict[str, Any]") -> "set[str]":
    return {
        e.get("citation_key")
        for e in passport.get("literature_corpus") or []
        if isinstance(e.get("citation_key"), str)
    }


def run_family_c(package_dir: Path,
                 passport: "Optional[dict[str, Any]]" = None,
                 join_map: "Optional[dict[str, str]]" = None
                 ) -> "tuple[list[dict[str, Any]], str]":
    """Run Family C over the package. Returns (checks, extraction_path)."""
    manuscripts = _manuscript_files(package_dir)
    if not manuscripts:
        return _not_checked_pair(
            "no manuscript found (no .md/.tex/.txt file in the package)"), "none"

    markers = extract_ref_markers(package_dir)
    bib_keys = parse_bib_keys(package_dir)
    corpus_keys = _corpus_keys(passport) if passport else set()

    # Reference-list side: a machine-readable source — package .bib keys, or
    # the passport's declared literature_corpus[] keys.
    if bib_keys:
        reference_keys, reference_label = bib_keys, "the package .bib reference list"
    elif corpus_keys:
        reference_keys, reference_label = (
            corpus_keys, "the passport literature_corpus reference list")
    else:
        reference_keys, reference_label = set(), ""

    if markers:
        # Joined marker path (deterministic). Join precedence: explicit
        # scholar-supplied map > the run's citation_verification_summary[] >
        # .bib identity relation (slug IS the citation_key,
        # draft_writer_agent.md two-layer contract).
        if join_map is not None:
            join = dict(join_map)
        elif passport is not None and _join_from_passport(passport):
            join = _join_from_passport(passport)
        elif bib_keys:
            join = {k: k for k in bib_keys}
        else:
            return _not_checked_pair(
                "missing prose-reference join: <!--ref:slug--> markers found "
                "but no citation_verification_summary, --join-map, or package "
                ".bib supplies the slug->citation_key join (§3.3 — never a "
                "guessed comparison)"), "none"
        if not reference_keys:
            return _not_checked_pair(
                "no machine-readable reference list (no package .bib and no "
                "passport literature_corpus[])"), "none"
        # Unjoinable slugs stay as-is: a slug with no join entry cannot be in
        # the reference list under any honest join, so it surfaces as a C1
        # orphan rather than being silently dropped.
        in_text = {join.get(slug, slug): loc for slug, loc in markers.items()}
        return _compare_sets(
            in_text, reference_keys, signal_class="deterministic",
            in_text_label="joined marker path",
            reference_label=reference_label), "joined_marker"

    # Fallback extraction lands in round 3.
    return _not_checked_pair(
        "no <!--ref:slug--> markers found and fallback extraction is not "
        "available"), "none"


def build_report(package_dir: Path, checks: "list[dict[str, Any]]",
                 extraction_path: str) -> "dict[str, Any]":
    return {
        "header": {
            "extraction_path": extraction_path,
            "not_checked_count": sum(
                1 for c in checks if c["status"] == "not_checked"),
            "package_fingerprint": compute_package_fingerprint(package_dir),
            # §5.2/§5.3: stamped by the slice-4 policy evaluator, never here.
            "policy_slug": None,
        },
        "checks": checks,
    }


def render_human(report: "dict[str, Any]") -> str:
    h = report["header"]
    lines = [
        "submission package verification "
        f"(extraction: {h['extraction_path']}, "
        f"not-checked: {h['not_checked_count']}, "
        f"fingerprint: {h['package_fingerprint'][:12]}…)",
    ]
    for c in report["checks"]:
        status = c["status"].upper().replace("NOT_CHECKED", "NOT-CHECKED")
        loc = f" @ {c['location']}" if c["location"] else ""
        lines.append(
            f"  [{status}] {c['id']} ({c['family']}, {c['signal_class']})"
            f"{loc}: {c['detail']}")
    return "\n".join(lines)


def exit_code_for(report: "dict[str, Any]") -> int:
    statuses = {c["status"] for c in report["checks"]}
    if "fail" in statuses:
        return 1
    if "not_checked" in statuses:
        return 3  # "passed what was checkable" (§8) — distinct from a full pass
    return 0


def run(argv: "Optional[list[str]]" = None) -> int:
    parser = argparse.ArgumentParser(
        prog="verify_submission_package",
        description="Deterministic submission-package verifier (#394 Slice 1: "
                    "Family C reference integrity).",
        epilog="Exit codes: 0 all-checked no-fail; 1 at least one fail; "
               "2 usage/IO error; 3 no fail but at least one NOT-CHECKED.")
    parser.add_argument("package_dir", help="Output package directory to verify.")
    parser.add_argument(
        "--passport", default=None,
        help="Material Passport YAML supplying citation_verification_summary[] "
             "(the prose-reference join) and/or literature_corpus[] (the "
             "declared reference list).")
    parser.add_argument(
        "--join-map", default=None,
        help="Explicit scholar-supplied {ref_slug: citation_key} YAML/JSON "
             "mapping (overrides every other join source).")
    parser.add_argument(
        "--report-out", default=None,
        help=f"Report path (default: <package_dir>/{REPORT_BASENAME}).")
    args = parser.parse_args(argv)

    package_dir = Path(args.package_dir)
    if not package_dir.is_dir():
        print(f"[verify_submission_package ERROR] not a directory: "
              f"{package_dir}", file=sys.stderr)
        return 2

    passport = None
    if args.passport is not None:
        try:
            passport = _load_yaml(Path(args.passport))
        except (OSError, ValueError, yaml.YAMLError) as e:
            print(f"[verify_submission_package ERROR] could not load passport: "
                  f"{e}", file=sys.stderr)
            return 2

    join_map = None
    if args.join_map is not None:
        try:
            raw = _load_yaml(Path(args.join_map))
        except (OSError, ValueError, yaml.YAMLError) as e:
            print(f"[verify_submission_package ERROR] could not load join map: "
                  f"{e}", file=sys.stderr)
            return 2
        join_map = {
            str(slug): str(key) for slug, key in raw.items()
        }

    checks, extraction_path = run_family_c(
        package_dir, passport=passport, join_map=join_map)
    report = build_report(package_dir, checks, extraction_path)

    report_path = (Path(args.report_out) if args.report_out
                   else package_dir / REPORT_BASENAME)
    try:
        report_path.write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8")
    except OSError as e:
        print(f"[verify_submission_package ERROR] could not write report: {e}",
              file=sys.stderr)
        return 2

    print(render_human(report))
    return exit_code_for(report)


if __name__ == "__main__":
    sys.exit(run())
