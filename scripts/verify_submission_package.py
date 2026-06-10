#!/usr/bin/env python3
"""verify_submission_package CLI — deterministic submission-package verifier
(#394; slices 1-2 shipped: Family C reference integrity + Family B venue
limits).

    python scripts/verify_submission_package.py <package_dir> \
        [--passport passport.yaml] [--join-map map.yaml] \
        [--venue-profile profile.yaml] [--report-out path]

Reads the files in an output package and runs the Family C two-way reference
integrity check (in-text citation keys <-> reference-list entries) plus the
Family B venue-limits checks (B1-B5, against a scholar-declared venue profile —
without one they report NOT-CHECKED, never a guess from the journal name),
writing `submission_verification_report.json` (validating against
shared/contracts/submission/submission_verification_report.schema.json) plus a
human-readable summary to stdout.

Design contract (spec docs/design/2026-06-10-394-submission-package-verifier-spec.md):

- Detection is unconditional; terminality is the policy evaluator's job. This
  script NEVER reads `terminal_policies` (§5.3) — `policy_slug` is emitted null.
- The joined marker path is deterministic; it needs a real prose-reference join
  (§3.3): the run's `citation_verification_summary[]` (via --passport), an
  explicit scholar-supplied join map (--join-map), or a package `.bib` whose
  keys map to slugs by the documented identity relation (draft_writer_agent.md:
  the slug IS the corpus `citation_key`). Markers with NO join source report
  `not_checked(missing prose-reference join)` — never a guessed comparison,
  and a slug an explicit join source does not cover is reported as unjoined,
  never identity-guessed.
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
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterator, Optional

import yaml

try:
    from audit_snapshot import sha256_hex
except ImportError:  # pragma: no cover - dual-path import
    from scripts.audit_snapshot import sha256_hex

REPORT_BASENAME = "submission_verification_report.json"

# Files scanned for in-text citations. provenance_summary.md is an advisory
# carrier that legitimately repeats ref_slugs / citation_keys (#333) — scanning
# it would manufacture false in-text hits.
_MANUSCRIPT_SUFFIXES = {".md", ".tex", ".txt"}
_SCAN_EXCLUDED_NAMES = {"provenance_summary.md", REPORT_BASENAME}

# v3.7.1+ marker grammar with the canonical slug charset (the lint-side
# REF_PATTERN in check_v3_7_3_three_layer_citation.py). The suffix handling is
# deliberately broader than REF_PATTERN's `[^-]*?` status group: a finalized
# package carries `LOW-WARN` / `CONTAMINATED-*` suffix tokens (formatter
# pass-through allowlist) that REF_PATTERN does not match, and missing those
# markers here would fabricate orphans. Anchor markers (`<!--anchor:...-->`)
# are a different grammar and never match.
_REF_MARKER_RE = re.compile(r"<!--ref:([A-Za-z][A-Za-z0-9_:-]*)(?:\s[^>]*)?-->")

# BibTeX entry heads after an `^@` split: `article{key,`. @comment/@preamble/
# @string carry no citation key and are excluded.
_BIB_ENTRY_HEAD_RE = re.compile(
    r"(?!comment|preamble|string)[A-Za-z]+\s*\{\s*([^,\s}]+)\s*,",
    re.IGNORECASE,
)

_LOCATION_CAP = 5  # findings listed per check detail before truncation

# Check registry mirroring the spec §3 family tables: id -> (family,
# fail_capable, fixed_signal_class). strict_eligible = fail_capable AND
# deterministic signal (§3.1 separate axes; a warn-only check is never
# policy-promotable, §5.3). fixed_signal_class None = path-dependent (Family
# C: deterministic on the joined marker path, heuristic on the fallback); a
# non-None class is bound HERE and wins over the call site, so a
# structurally-heuristic check (slice 3's A5/A6) is excluded from strict by
# CLASS, never "defaulted out of it" (§3.1) — a forgotten kwarg cannot
# fail open. build_report enforces the roster: a runner that silently omits
# a registered check cannot emit a report (the §1.4/#349 fail-open guard).
_CHECK_REGISTRY = {
    "B1": ("venue_limits", True, "deterministic"),   # manuscript word count
    "B2": ("venue_limits", True, "deterministic"),   # abstract word count
    "B3": ("venue_limits", True, "deterministic"),   # keyword count range
    "B4": ("venue_limits", True, "deterministic"),   # required sections
    "B5": ("venue_limits", True, "deterministic"),   # reference count ceiling
    "C1": ("reference_integrity", True, None),
    "C2": ("reference_integrity", False, None),
}

# --- Fallback (best-effort) extraction grammar (§3.3, heuristic-classed) -----

# \cite / \citep / \citet / \citealp / starred forms, up to two optional args.
_LATEX_CITE_RE = re.compile(r"\\cite[a-zA-Z]*\*?(?:\[[^\]]*\]){0,2}\{([^}]*)\}")

# Reference-list section titles — the single source for BOTH the fallback
# prose-scan boundary (Family C) and the B1 body_only word-count scope; one
# list so the two checks can never disagree about where the references start.
_REFS_TITLES = ("references", "bibliography", "參考文獻")
_REFS_HEADING_RE = re.compile(
    r"^#{0,6}\s*(?:" + "|".join(_REFS_TITLES) + r")\s*$",
    re.IGNORECASE | re.MULTILINE,
)

_NAME = r"[A-Z][\w'’-]+"
# Narrative: `Smith (2024)`, `Smith et al. (2024)`, `Smith and Chen (2024)`,
# with an optional page-locator tail: `Smith (2024, p. 12)`.
_NARRATIVE_CITE_RE = re.compile(
    r"(" + _NAME + r")(?:\s+et al\.?|\s+(?:and|&)\s+" + _NAME + r")?"
    r"\s+\((\d{4})[a-z]?(?:\s*,\s*pp?\.?[^)]*)?\)")
# Parenthetical group content is split on `;` and each segment matched:
# `(Smith, 2024)`, `(Chen & Lee, 2023)`, `(Smith et al., 2024a)`,
# `(Chen & Lee, 2023, pp. 45–67)`.
_PAREN_GROUP_RE = re.compile(r"\(([^()]+)\)")
_PAREN_SEGMENT_RE = re.compile(
    r"^\s*(" + _NAME + r")[^\d]*?(\d{4})[a-z]?(?:\s*,\s*pp?\.?[^;]*)?\s*$")


def compute_package_fingerprint(package_dir: Path,
                                report_relpath: Optional[str] = None) -> str:
    """Audit-snapshot manifest convention over the package files (§10 item 3):
    one `<package-relative-path>:<sha256>` line per file, LC_ALL=C byte-sorted,
    trailing newline; fingerprint = SHA-256 of the manifest text. The report
    file is excluded — the report cannot fingerprint its own bytes — including
    a custom --report-out path inside the package (report_relpath, as a
    package-relative posix path), or reruns would self-reference."""
    excluded = {REPORT_BASENAME, report_relpath}
    lines = []
    for path in package_dir.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(package_dir).as_posix()
        if rel in excluded:
            continue
        lines.append(f"{rel}:{sha256_hex(path.read_bytes())}")
    lines.sort()  # byte sort over the composed line, matching audit_snapshot
    manifest_text = "\n".join(lines) + "\n"
    return sha256_hex(manifest_text.encode("utf-8"))


def _collect_package_texts(package_dir: Path
                           ) -> tuple[dict[str, str], dict[str, str]]:
    """One walk, one read per file: ({manuscript rel: text}, {bib rel: text})."""
    manuscripts: dict[str, str] = {}
    bibs: dict[str, str] = {}
    for path in sorted(package_dir.rglob("*")):
        if not path.is_file() or path.name in _SCAN_EXCLUDED_NAMES:
            continue
        suffix = path.suffix.lower()
        if suffix not in _MANUSCRIPT_SUFFIXES and suffix != ".bib":
            continue
        rel = path.relative_to(package_dir).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        (bibs if suffix == ".bib" else manuscripts)[rel] = text
    return manuscripts, bibs


def extract_ref_markers(manuscripts: dict[str, str]) -> dict[str, str]:
    """{slug: first-seen package-relative location} from <!--ref:slug--> markers."""
    found: dict[str, str] = {}
    for rel in sorted(manuscripts):
        for m in _REF_MARKER_RE.finditer(manuscripts[rel]):
            found.setdefault(m.group(1), rel)
    return found


def _iter_bib_entries(bibs: dict[str, str]) -> Iterator[tuple[str, str]]:
    """Yield (citation_key, raw entry body) per BibTeX entry across the
    package's .bib files — the single entry-head grammar both the key set and
    the author-year metadata derive from, so they cannot drift."""
    for rel in sorted(bibs):
        for chunk in re.split(r"(?m)^\s*@", bibs[rel])[1:]:
            head = _BIB_ENTRY_HEAD_RE.match(chunk)
            if head:
                yield head.group(1), chunk


def parse_bib_keys(bibs: dict[str, str]) -> set[str]:
    return {key for key, _body in _iter_bib_entries(bibs)}


def _parse_bib_metadata(bibs: dict[str, str]) -> dict[tuple, set]:
    """{(first-author-surname-lower, year): {citation_key, ...}} from package
    .bib entries, for author-year fallback matching. Best-effort field parsing
    — the whole fallback path is heuristic-classed anyway (§3.3)."""
    metadata: dict[tuple, set] = {}
    for key, body in _iter_bib_entries(bibs):
        author = re.search(r"author\s*=\s*[{\"]([^}\"]+)", body, re.IGNORECASE)
        year = re.search(r"year\s*=\s*[{\"]?(\d{4})", body, re.IGNORECASE)
        if not (author and year):
            continue
        surname = _first_author_surname(author.group(1))
        if surname:
            metadata.setdefault(
                (surname.lower(), year.group(1)), set()).add(key)
    return metadata


def _first_author_surname(author_field: str) -> str:
    first = author_field.split(" and ")[0].strip()
    if "," in first:
        return first.split(",")[0].strip()
    parts = first.split()
    return parts[-1] if parts else ""


def _corpus_metadata(passport: dict[str, Any]) -> dict[tuple, set]:
    metadata: dict[tuple, set] = {}
    for e in passport.get("literature_corpus") or []:
        key = e.get("citation_key")
        year = e.get("year")
        authors = e.get("authors") or []
        family = authors[0].get("family") if (
            authors and isinstance(authors[0], dict)) else None
        if isinstance(key, str) and family and year is not None:
            metadata.setdefault((str(family).lower(), str(year)), set()).add(key)
    return metadata


def _strip_reference_section(text: str) -> str:
    m = _REFS_HEADING_RE.search(text)
    return text[: m.start()] if m else text


def _extract_fallback(manuscripts: dict[str, str],
                      metadata: dict[tuple, set]
                      ) -> tuple[dict[str, str], dict[str, str]]:
    """Best-effort in-text extraction (§3.3 fallback path): \\cite{} keys from
    .tex, author-year hits from .md/.txt matched against reference metadata.
    Returns (in_text {citation_key: location}, unresolved {display token:
    location}) — unresolved hits stay out of the citation-key namespace so a
    key that textually equals the token never silently merges."""
    in_text: dict[str, str] = {}
    unresolved: dict[str, str] = {}
    for rel in sorted(manuscripts):
        text = manuscripts[rel]
        if rel.lower().endswith(".tex"):
            for m in _LATEX_CITE_RE.finditer(text):
                for key in m.group(1).split(","):
                    key = key.strip()
                    if key:
                        in_text.setdefault(key, rel)
            continue
        prose = _strip_reference_section(text)
        hits = [(m.group(1), m.group(2))
                for m in _NARRATIVE_CITE_RE.finditer(prose)]
        for g in _PAREN_GROUP_RE.finditer(prose):
            for segment in g.group(1).split(";"):
                m = _PAREN_SEGMENT_RE.match(segment)
                if m:
                    hits.append((m.group(1), m.group(2)))
        for surname, year in hits:
            keys = metadata.get((surname.lower(), year))
            if keys:
                for key in keys:
                    in_text.setdefault(key, rel)
            else:
                unresolved.setdefault(f"{surname} ({year})", rel)
    return in_text, unresolved


def _check(check_id: str, status: str, detail: str, *,
           signal_class: str = "deterministic",
           location: Optional[str] = None) -> dict[str, Any]:
    family, fail_capable, fixed_class = _CHECK_REGISTRY[check_id]
    if fixed_class is not None:
        signal_class = fixed_class  # registry-bound class wins (§3.1)
    return {
        "id": check_id,
        "family": family,
        "signal_class": signal_class,
        "strict_eligible": fail_capable and signal_class == "deterministic",
        "status": status,
        "detail": detail,
        "location": location,
    }


def _not_checked_pair(reason: str) -> list[dict[str, Any]]:
    return [
        _check("C1", "not_checked", reason),
        _check("C2", "not_checked", reason),
    ]


def _listed(keys: set[str]) -> str:
    shown = sorted(keys)[:_LOCATION_CAP]
    extra = len(keys) - len(shown)
    listing = ", ".join(shown)
    if extra > 0:
        listing += f", … (+{extra} more)"
    return listing


def _compare_sets(in_text: dict[str, str], reference_keys: set[str],
                  *, signal_class: str, in_text_label: str,
                  reference_label: str,
                  unjoined: Optional[dict[str, str]] = None,
                  unjoined_label: str = ("with no join entry in the supplied "
                                         "join source")
                  ) -> list[dict[str, Any]]:
    """Two-way set check (§3.3): orphan in-text citation = fail (C1); uncited
    reference entry = warn (C2 — some venues allow further-reading entries).
    `unjoined` carries in-text hits that cannot be placed in the citation-key
    namespace (marker slugs the join source does not cover; fallback hits with
    no metadata match): they are a C1 fail in their own right — NEVER compared
    via an identity guess (§3.3), which would silently pass a slug that
    coincidentally equals a citation_key."""
    unjoined = unjoined or {}
    orphans = {k for k in in_text if k not in reference_keys}
    uncited = reference_keys - set(in_text)
    checks = []
    if orphans or unjoined:
        parts = []
        if orphans:
            parts.append(
                f"{len(orphans)} in-text citation(s) absent from "
                f"{reference_label}: {_listed(orphans)}")
        if unjoined:
            parts.append(
                f"{len(unjoined)} in-text citation(s) {unjoined_label}: "
                f"{_listed(set(unjoined))}")
        first_loc = min(
            [in_text[k] for k in orphans] + list(unjoined.values()))
        checks.append(_check(
            "C1", "fail",
            "; ".join(parts) + f" [{in_text_label}]",
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


def _load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"expected a YAML mapping in {path}")
    return data


def _join_from_passport(passport: dict[str, Any]) -> dict[str, str]:
    """{ref_slug: citation_key} from the passport's
    citation_verification_summary[] rows (the per-citation prose join the
    Stage 4->5 run already established, §3.3)."""
    join: dict[str, str] = {}
    for row in passport.get("citation_verification_summary") or []:
        slug = row.get("ref_slug")
        key = row.get("citation_key")
        if isinstance(slug, str) and slug and isinstance(key, str) and key:
            join[slug] = key
    return join


def _corpus_keys(passport: dict[str, Any]) -> set[str]:
    return {
        e.get("citation_key")
        for e in passport.get("literature_corpus") or []
        if isinstance(e.get("citation_key"), str)
    }


_NO_REFERENCE_LIST_REASON = (
    "no machine-readable reference list (no package .bib and no "
    "passport literature_corpus[])")
_NO_MANUSCRIPT_REASON = (
    "no manuscript found (no .md/.tex/.txt file in the package)")


def _reference_list(bib_keys: set[str],
                    passport: Optional[dict[str, Any]]
                    ) -> tuple[set[str], str]:
    """The machine-readable reference list both Family C and B5 compare
    against: package .bib keys, or the passport's declared
    literature_corpus[] keys. Empty set + empty label = no source."""
    if bib_keys:
        return bib_keys, "the package .bib reference list"
    corpus_keys = _corpus_keys(passport) if passport else set()
    if corpus_keys:
        return corpus_keys, "the passport literature_corpus reference list"
    return set(), ""


def run_family_c(manuscripts: dict[str, str], bibs: dict[str, str],
                 bib_keys: set[str],
                 reference_keys: set[str], reference_label: str,
                 passport: Optional[dict[str, Any]] = None,
                 join_map: Optional[dict[str, str]] = None
                 ) -> tuple[list[dict[str, Any]], str]:
    """Run Family C over the collected package texts.
    Returns (checks, extraction_path)."""
    if not manuscripts:
        return _not_checked_pair(_NO_MANUSCRIPT_REASON), "none"

    markers = extract_ref_markers(manuscripts)
    summary_join = _join_from_passport(passport) if passport else {}

    if not reference_keys:
        return _not_checked_pair(_NO_REFERENCE_LIST_REASON), "none"

    if markers:
        # Joined marker path (deterministic). Join precedence: explicit
        # scholar-supplied map > the run's citation_verification_summary[] >
        # .bib identity relation.
        if join_map is not None:
            join: Optional[dict[str, str]] = dict(join_map)
        elif summary_join:
            join = summary_join
        elif bib_keys:
            # Documented identity relation (draft_writer_agent.md: the slug IS
            # the corpus citation_key): every marker slug joins to itself, so
            # a slug that is not a .bib key is simply an orphan.
            join = None
        else:
            return _not_checked_pair(
                "missing prose-reference join: <!--ref:slug--> markers found "
                "but no citation_verification_summary, --join-map, or package "
                ".bib supplies the slug->citation_key join (§3.3 — never a "
                "guessed comparison)"), "none"
        if join is None:  # .bib identity relation
            in_text, unjoined = dict(markers), {}
        else:
            # An explicit join source (summary / --join-map) must cover every
            # cited slug; a slug it does not cover is reported as such — NEVER
            # compared via an identity guess, which would silently pass a slug
            # that coincidentally equals a citation_key (§3.3).
            in_text, unjoined = {}, {}
            for slug, loc in markers.items():
                if slug in join:
                    in_text.setdefault(join[slug], loc)
                else:
                    unjoined.setdefault(slug, loc)
        return _compare_sets(
            in_text, reference_keys, signal_class="deterministic",
            in_text_label="joined marker path",
            reference_label=reference_label, unjoined=unjoined), "joined_marker"

    # Fallback path (§3.3): no markers — non-ARS or post-converted source.
    # Format-aware best-effort extraction, heuristic-classed (advisory-only).
    metadata = _parse_bib_metadata(bibs)
    if passport:
        for k, v in _corpus_metadata(passport).items():
            metadata.setdefault(k, set()).update(v)
    in_text, unresolved = _extract_fallback(manuscripts, metadata)
    return _compare_sets(
        in_text, reference_keys, signal_class="heuristic",
        in_text_label="best-effort extraction",
        reference_label=reference_label, unjoined=unresolved,
        unjoined_label="unmatched against any reference metadata"
        ), "best_effort"


_FAMILY_B_IDS = tuple(
    cid for cid, (fam, _fc, _sc) in sorted(_CHECK_REGISTRY.items())
    if fam == "venue_limits")

_WORD_COUNT_TOLERANCE = 1.02  # §3.2: ±2% before fail (format-conversion noise)

_MD_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$", re.MULTILINE)
_KEYWORDS_LINE_RE = re.compile(
    r"^\s*(?:\*\*|__)?\s*keywords?\s*(?:\*\*|__)?\s*[:：]\s*(.+?)\s*$",
    re.IGNORECASE | re.MULTILINE)
_TEX_KEYWORDS_RE = re.compile(r"\\keywords\s*\{([^}]*)\}", re.IGNORECASE)
_TEX_SECTION_RE = re.compile(r"\\(?:sub)*section\*?\s*\{([^}]*)\}")
_TEX_ABSTRACT_RE = re.compile(
    r"\\begin\{abstract\}(.*?)\\end\{abstract\}", re.DOTALL)
_TEX_BIBLIO_RE = re.compile(
    r"\\begin\{thebibliography\}.*?\\end\{thebibliography\}|\\bibliography\s*\{[^}]*\}",
    re.DOTALL)
_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)


def _word_count(text: str) -> int:
    """Canonical whitespace-split (shared/references/word_count_conventions.md)."""
    return len(text.split())


def _md_sections(text: str) -> list[tuple[str, int, int]]:
    """[(heading title, content start, content end)] per markdown section."""
    heads = list(_MD_HEADING_RE.finditer(text))
    return [(m.group(2).strip(),
             m.end(),
             heads[i + 1].start() if i + 1 < len(heads) else len(text))
            for i, m in enumerate(heads)]


def _is_abstract_title(title: str) -> bool:
    return title.lower().strip("*_ ").startswith("abstract")


def _is_refs_title(title: str) -> bool:
    return title.lower().strip("*_ ") in _REFS_TITLES


def _md_drop_sections(text: str, title_predicates) -> str:
    """Remove every section (heading included) whose title matches any
    predicate."""
    heads = list(_MD_HEADING_RE.finditer(text))
    keep, cursor = [], 0
    for i, m in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        if any(p(m.group(2).strip()) for p in title_predicates):
            keep.append(text[cursor:m.start()])
            cursor = end
    keep.append(text[cursor:])
    return "".join(keep)


def _detex(text: str) -> str:
    """Naive detex (§10 item 4, adjudicated at slice 2: naive detex +
    whitespace-split, the method is DECLARED in the report and never promised
    venue-exact): drop comments and \\commands, unwrap braces/brackets."""
    text = re.sub(r"(?<!\\)%.*", " ", text)
    text = re.sub(r"\\[a-zA-Z]+\*?", " ", text)
    return re.sub(r"[{}\[\]]", " ", text)


def _countable_body(rel: str, text: str, scope: str) -> tuple[str, str]:
    """(countable text, human description of what was counted) for B1."""
    if rel.lower().endswith(".tex"):
        if scope == "body_only":
            return (_detex(_TEX_BIBLIO_RE.sub(
                        " ", _TEX_ABSTRACT_RE.sub(" ", text))),
                    "naive detex; abstract + bibliography excluded")
        if scope == "body_plus_references":
            return (_detex(_TEX_ABSTRACT_RE.sub(" ", text)),
                    "naive detex; abstract excluded")
        return _detex(text), "naive detex; everything counted"
    text = _HTML_COMMENT_RE.sub(" ", text)
    if scope == "body_only":
        return (_md_drop_sections(_KEYWORDS_LINE_RE.sub(" ", text),
                                  (_is_abstract_title, _is_refs_title)),
                "abstract + references + keywords line excluded")
    if scope == "body_plus_references":
        return (_md_drop_sections(_KEYWORDS_LINE_RE.sub(" ", text),
                                  (_is_abstract_title,)),
                "abstract + keywords line excluded")
    # `all` counts everything the author wrote — only the ARS tool markers
    # (HTML comments) are stripped, and that is declared.
    return text, "everything counted (tool markers stripped)"


def _abstract_text(rel: str, text: str) -> Optional[str]:
    if rel.lower().endswith(".tex"):
        m = _TEX_ABSTRACT_RE.search(text)
        return _detex(m.group(1)) if m else None
    for title, start, end in _md_sections(text):
        if _is_abstract_title(title):
            body = _HTML_COMMENT_RE.sub(" ", text[start:end])
            return _KEYWORDS_LINE_RE.sub(" ", body)
    return None


def _keyword_list(text: str) -> Optional[list[str]]:
    m = _KEYWORDS_LINE_RE.search(text) or _TEX_KEYWORDS_RE.search(text)
    if not m:
        return None
    return [k for k in re.split(r"[,;、；]", m.group(1)) if k.strip()]


def _headings(rel: str, text: str) -> list[str]:
    if rel.lower().endswith(".tex"):
        return [m.group(1).strip() for m in _TEX_SECTION_RE.finditer(text)]
    return [t for t, _s, _e in _md_sections(text)]


_CANONICAL_MANUSCRIPT_STEMS = frozenset({"paper", "manuscript", "main"})
_NON_MANUSCRIPT_PREFIXES = (
    "cover_letter", "cover-letter", "response", "rebuttal", "readme")


def _primary_manuscript(manuscripts: dict[str, str]
                        ) -> tuple[Optional[str], Optional[str], Optional[str]]:
    """(rel, text, blocked_reason) — the manuscript the limits are checked
    against; rel/text are None iff blocked_reason says why. Canonical
    filenames (paper/manuscript/main) win; known package-document names
    (cover letters, response letters, READMEs) are excluded; with several
    remaining non-canonical candidates the verifier reports ambiguity instead
    of silently picking the wordiest (it could be an appendix or a response
    letter). Which file was counted is declared in every detail string."""
    if not manuscripts:
        return None, None, _NO_MANUSCRIPT_REASON
    candidates = {
        rel: t for rel, t in manuscripts.items()
        if not Path(rel).name.lower().startswith(_NON_MANUSCRIPT_PREFIXES)}
    candidates = candidates or manuscripts
    canonical = {rel: t for rel, t in candidates.items()
                 if Path(rel).stem.lower() in _CANONICAL_MANUSCRIPT_STEMS}
    pool = canonical or candidates
    if not canonical and len(candidates) > 1:
        return None, None, (
            "ambiguous manuscript: several candidates and none carries a "
            f"canonical name (paper/manuscript/main): "
            f"{', '.join(sorted(candidates))} — rename the manuscript or "
            "remove the extras")
    rel = max(sorted(pool), key=lambda r: _word_count(pool[r]))
    return rel, pool[rel], None


def _ceiling_check(check_id: str, count: int, limit: int, what: str,
                   location: Optional[str] = None,
                   tolerance: float = 1.0) -> dict[str, Any]:
    tol_note = " (±2% tolerance)" if tolerance > 1.0 else ""
    status = "pass" if count <= limit * tolerance else "fail"
    return _check(check_id, status,
                  f"{what}: {count} vs declared limit {limit}{tol_note}",
                  location=location)


def run_family_b(manuscripts: dict[str, str],
                 reference_keys: set[str], reference_label: str,
                 profile: Optional[dict[str, Any]]
                 ) -> list[dict[str, Any]]:
    """Family B: venue-declared limits vs actuals (§3.2). Without a profile,
    every check is NOT-CHECKED — limits are never guessed from the journal
    name (R-L3-2-D mirror). A partially-declared profile runs the checks it
    can and NOT-CHECKEDs the rest (§4)."""
    if profile is None:
        return [_check(i, "not_checked",
                       "no venue profile declared — limits are never guessed "
                       "from the journal name (R-L3-2-D mirror)")
                for i in _FAMILY_B_IDS]

    checks: list[dict[str, Any]] = []
    rel, text, no_manuscript_reason = _primary_manuscript(manuscripts)

    def not_declared(check_id: str, field: str) -> dict[str, Any]:
        return _check(check_id, "not_checked",
                      f"{field} not declared in venue profile")

    # B1 — manuscript word count vs word_limit (±2%, §3.2)
    word_limit = profile.get("word_limit")
    if word_limit is None:
        checks.append(not_declared("B1", "word_limit"))
    elif rel is None:
        checks.append(_check("B1", "not_checked", no_manuscript_reason))
    else:
        scope = profile.get("word_count_scope")
        scope_decl = scope or "body_only (default — scope not declared)"
        body, counted_desc = _countable_body(rel, text, scope or "body_only")
        checks.append(_ceiling_check(
            "B1", _word_count(body), word_limit,
            f"manuscript word count of {rel}, scope {scope_decl} "
            f"({counted_desc}; whitespace-split per "
            f"shared/references/word_count_conventions.md)",
            location=rel, tolerance=_WORD_COUNT_TOLERANCE))

    # B2 — abstract word count vs abstract_word_limit (±2%)
    abstract_limit = profile.get("abstract_word_limit")
    if abstract_limit is None:
        checks.append(not_declared("B2", "abstract_word_limit"))
    elif rel is None:
        checks.append(_check("B2", "not_checked", no_manuscript_reason))
    else:
        abstract = _abstract_text(rel, text)
        if abstract is None:
            checks.append(_check(
                "B2", "not_checked",
                f"no abstract section found in {rel}", location=rel))
        else:
            checks.append(_ceiling_check(
                "B2", _word_count(abstract), abstract_limit,
                f"abstract word count of {rel} (whitespace-split)",
                location=rel, tolerance=_WORD_COUNT_TOLERANCE))

    # B3 — keyword count vs keyword_range (exact)
    keyword_range = profile.get("keyword_range")
    if keyword_range is None:
        checks.append(not_declared("B3", "keyword_range"))
    elif rel is None:
        checks.append(_check("B3", "not_checked", no_manuscript_reason))
    else:
        keywords = _keyword_list(text)
        if keywords is None:
            checks.append(_check(
                "B3", "not_checked",
                f"no keywords line found in {rel}", location=rel))
        else:
            lo, hi = keyword_range["min"], keyword_range["max"]
            ok = lo <= len(keywords) <= hi
            checks.append(_check(
                "B3", "pass" if ok else "fail",
                f"keyword count of {rel}: {len(keywords)} vs declared range "
                f"{lo}–{hi}", location=rel))

    # B4 — required sections present (set comparison)
    required = profile.get("required_sections")
    if required is None:
        checks.append(not_declared("B4", "required_sections"))
    elif rel is None:
        checks.append(_check("B4", "not_checked", no_manuscript_reason))
    else:
        headings = [h.lower() for h in _headings(rel, text)]
        missing = [s for s in required
                   if not any(s.lower() in h for h in headings)]
        if missing:
            checks.append(_check(
                "B4", "fail",
                f"required section(s) missing from {rel} (case-insensitive "
                f"heading containment): {', '.join(missing)}", location=rel))
        else:
            checks.append(_check(
                "B4", "pass",
                f"all {len(required)} required section(s) present in {rel}",
                location=rel))

    # B5 — reference count vs reference_limit (exact)
    reference_limit = profile.get("reference_limit")
    if reference_limit is None:
        checks.append(not_declared("B5", "reference_limit"))
    elif not reference_keys:
        checks.append(_check("B5", "not_checked", _NO_REFERENCE_LIST_REASON))
    else:
        checks.append(_ceiling_check(
            "B5", len(reference_keys), reference_limit,
            f"reference entries in {reference_label}"))

    return checks


_PROFILE_SCHEMA_PATH = (
    Path(__file__).resolve().parent.parent / "shared" / "contracts"
    / "submission" / "venue_profile.schema.json")
_profile_schema_cache: Optional[dict[str, Any]] = None


def _profile_schema() -> dict[str, Any]:
    """The formal venue-profile contract, loaded once. The validator derives
    its allowed-field set and enums FROM the schema file so the contract has
    one source of truth (a schema edit cannot silently desync the CLI gate)."""
    global _profile_schema_cache
    if _profile_schema_cache is None:
        _profile_schema_cache = json.loads(
            _PROFILE_SCHEMA_PATH.read_text(encoding="utf-8"))
    return _profile_schema_cache


def _schema_enum(field: str) -> tuple:
    return tuple(v for v in _profile_schema()["properties"][field]["enum"]
                 if v is not None)


def _is_int(v: Any) -> bool:
    """A real integer — bool is an int subclass and must not pass as one."""
    return isinstance(v, int) and not isinstance(v, bool)


def _validate_venue_profile(raw: dict[str, Any]) -> dict[str, Any]:
    """Shape validation for a --venue-profile file. The allowed-field set and
    enums are derived from the formal contract
    (shared/contracts/submission/venue_profile.schema.json,
    additionalProperties false included) so a malformed or typoed profile is a
    usage error, never a silently-skewed or silently-skipped comparison."""
    allowed = set(_profile_schema()["properties"])
    unknown = set(raw) - allowed
    if unknown:
        raise ValueError(
            f"venue profile has unknown field(s) {sorted(unknown)} — the "
            f"schema is closed (a typoed limit would otherwise be silently "
            f"ignored); allowed: {sorted(allowed)}")
    if raw.get("declared_by") != "scholar":
        raise ValueError(
            "venue profile must carry `declared_by: scholar` — the profile is "
            "scholar-declared only, never scraped or inferred (spec §4)")
    name = raw.get("venue_name")
    if name is not None and not isinstance(name, str):
        raise ValueError(f"venue profile venue_name must be a string or null, "
                         f"got {name!r}")
    for field in ("word_limit", "abstract_word_limit", "reference_limit"):
        v = raw.get(field)
        if v is not None and (not _is_int(v) or v < 1):
            raise ValueError(f"venue profile {field} must be a positive "
                             f"integer or null, got {v!r}")
    scope = raw.get("word_count_scope")
    if scope is not None and scope not in _schema_enum("word_count_scope"):
        raise ValueError(f"venue profile word_count_scope must be one of "
                         f"{'/'.join(_schema_enum('word_count_scope'))}/null, "
                         f"got {scope!r}")
    blind = raw.get("blind_review")
    if blind is not None and blind not in _schema_enum("blind_review"):
        raise ValueError(f"venue profile blind_review must be one of "
                         f"{'/'.join(_schema_enum('blind_review'))}/null, "
                         f"got {blind!r}")
    kr = raw.get("keyword_range")
    if kr is not None:
        if (not isinstance(kr, dict) or set(kr) != {"min", "max"}
                or not _is_int(kr.get("min")) or kr["min"] < 0
                or not _is_int(kr.get("max")) or kr["max"] < 1
                or kr["min"] > kr["max"]):
            raise ValueError(
                f"venue profile keyword_range must be {{min >= 0, max >= 1}} "
                f"integers with min <= max, got {kr!r}")
    sections = raw.get("required_sections")
    if sections is not None and (
            not isinstance(sections, list)
            or not all(isinstance(s, str) and s for s in sections)):
        raise ValueError("venue profile required_sections must be a list of "
                         "non-empty strings or null")
    return raw


def run_checks(package_dir: Path,
               passport: Optional[dict[str, Any]] = None,
               join_map: Optional[dict[str, str]] = None,
               venue_profile: Optional[dict[str, Any]] = None
               ) -> tuple[list[dict[str, Any]], str]:
    """Collect the package texts once and run every check family.
    Returns (checks sorted by id, extraction_path)."""
    manuscripts, bibs = _collect_package_texts(package_dir)
    bib_keys = parse_bib_keys(bibs)
    reference_keys, reference_label = _reference_list(bib_keys, passport)
    checks_c, extraction_path = run_family_c(
        manuscripts, bibs, bib_keys, reference_keys, reference_label,
        passport=passport, join_map=join_map)
    checks_b = run_family_b(
        manuscripts, reference_keys, reference_label, venue_profile)
    return sorted(checks_b + checks_c, key=lambda c: c["id"]), extraction_path


def build_report(package_dir: Path, checks: list[dict[str, Any]],
                 extraction_path: str,
                 report_path: Optional[Path] = None) -> dict[str, Any]:
    emitted = {c["id"] for c in checks}
    if emitted != set(_CHECK_REGISTRY):
        # Roster guard (§1.4/#349): a runner that silently omits a registered
        # check would read as "covered"; fail loud instead.
        raise ValueError(
            f"check roster mismatch: emitted {sorted(emitted)}, "
            f"registered {sorted(_CHECK_REGISTRY)}")
    report_relpath = None
    if report_path is not None:
        try:
            report_relpath = report_path.resolve().relative_to(
                package_dir.resolve()).as_posix()
        except ValueError:
            pass  # report written outside the package — nothing to exclude
    return {
        "header": {
            "extraction_path": extraction_path,
            "not_checked_count": sum(
                1 for c in checks if c["status"] == "not_checked"),
            "package_fingerprint": compute_package_fingerprint(
                package_dir, report_relpath),
            # §5.2/§5.3: stamped by the slice-4 policy evaluator, never here.
            "policy_slug": None,
        },
        "checks": checks,
    }


def render_human(report: dict[str, Any]) -> str:
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


def exit_code_for(report: dict[str, Any]) -> int:
    statuses = {c["status"] for c in report["checks"]}
    if "fail" in statuses:
        return 1
    if "not_checked" in statuses:
        return 3  # "passed what was checkable" (§8) — distinct from a full pass
    return 0


def run(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="verify_submission_package",
        description="Deterministic submission-package verifier (#394: Family "
                    "C reference integrity + Family B venue limits).",
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
        "--venue-profile", default=None,
        help="Scholar-declared venue profile YAML (schema shared/contracts/"
             "submission/venue_profile.schema.json) enabling the Family B "
             "limits checks. Absent: every Family B check reports "
             "NOT-CHECKED(no venue profile) — never guessed from the "
             "journal name.")
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
        join_map = {str(slug): str(key) for slug, key in raw.items()}

    venue_profile = None
    if args.venue_profile is not None:
        try:
            venue_profile = _validate_venue_profile(
                _load_yaml(Path(args.venue_profile)))
        except (OSError, ValueError, yaml.YAMLError) as e:
            print(f"[verify_submission_package ERROR] could not load venue "
                  f"profile: {e}", file=sys.stderr)
            return 2

    checks, extraction_path = run_checks(
        package_dir, passport=passport, join_map=join_map,
        venue_profile=venue_profile)
    report_path = (Path(args.report_out) if args.report_out
                   else package_dir / REPORT_BASENAME)
    report = build_report(package_dir, checks, extraction_path,
                          report_path=report_path)

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
