#!/usr/bin/env python3
"""Deterministic token-conservation audit between revision rounds (#570).

Compares the multisets of numeric tokens, citation tokens
(`<!--ref:-->` / `<!--anchor:-->` markers, bracketed groups, author-year
parentheticals), and optional protected terms between a source text and
its revision — either as a plain pair of drafts or per-op against a #390
revision patch document, attributing every delta to the op's
`roadmap_item_ids` and rendering `ADV-REV-<n>` advisory rows.

Contract boundaries (issue #570):

  - **Advisory, not a gate.** A delta is not a violation — the Revision
    Roadmap may authorize it. The checker surfaces every delta with its
    claimed roadmap items so the round checkpoint can judge; default exit
    is 0 regardless of deltas (`--strict` exits 1 on any delta, for
    fixtures and tests).
  - **Necessary but not sufficient.** Exact-token conservation cannot see
    negation, comparison direction, modality, causal strength, citation
    attachment, or paraphrase-level meaning change. Those stay with the
    LLM/human audit layers; a conserved result must never be presented as
    a semantic-fidelity guarantee.
  - **Fold before split.** The whole text is Unicode-normalized (NFKC +
    dash/minus folding) BEFORE any tokenization, so a fullwidth or
    homoglyph respelling can neither smuggle a changed value past the
    comparison nor false-flag an unchanged one (the #524 ordering
    lesson).
  - Tokens are compared verbatim after folding: `612,418` → `612418` is
    a reported delta, not a silent reformat — formatting changes are for
    the checkpoint to wave through, not for the checker to forgive.

Mechanism shape borrowed from Yila-AI/sci-ssci-skills
(`sci-ssci-polishing`, `scripts/check_invariants.py`), extended with
marker-aware citation tokens, patch-mode attribution, and fold-before-
split normalization.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

if __package__ in (None, ""):  # pragma: no cover - direct CLI invocation
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
# Canonical ref-marker grammar (scripts/verify_submission_package.py,
# pipeline_orchestrator_agent.md L3-1): the finalizer resolves a bare
# <!--ref:slug--> into 0/1/2-status-token + optional policy_hash forms, and
# revision reruns run on already-resolved drafts. Key the citation multiset on
# the SLUG alone — status/suffix tokens are derived metadata, not writer
# content — so bare↔resolved churn is not a spurious delta and a DROPPED
# resolved marker still surfaces (matching only the bare shape would let it
# vanish under COMMENT_RE, the exact miss this checker exists to prevent).
REF_MARKER_RE = re.compile(r"<!--ref:([A-Za-z][A-Za-z0-9_:-]*)(?:\s[^>]*)?-->")
ANCHOR_MARKER_RE = re.compile(r"<!--(anchor:[^>]+?)-->")
# Sign attaches only when preceded by start/whitespace/([/=/:/,/; — never
# between digits, so `0.58-0.92` stays two unsigned range endpoints while
# `β = -0.45`, `CI [-0.45, ...]`, and a comma-led `-1.3` keep their sign.
# Letter-adjacent embedded digits (H2, Model-A7, T0, v2.7.10a) are identifier
# fragments — entity-layer tokens for `--protected-terms`, not prose numbers —
# so the unsigned branch excludes them with an explicit [A-Za-z] guard (NOT
# \w: CJK-adjacent numbers like 共612名 must still count). A scientific
# exponent (`6.02e23`, `1.2E-5`) is part of the token, so `6.02e23`→`6.02e24`
# is a delta, not a truncation to a conserved `6.02`.
_MANTISSA = r"(?:\d+(?:,\d{3})*(?:\.\d+)?|\.\d+)"
_EXPONENT = r"(?:[eE][-+]?\d+)?"
NUMBER_RE = re.compile(
    rf"(?:(?<=[\s(\[=:,;])|^)-?{_MANTISSA}{_EXPONENT}%?"
    rf"|(?<![A-Za-z\d.]){_MANTISSA}{_EXPONENT}%?"
)
SQUARE_CITATION_RE = re.compile(r"\[(?:\d+[-,;\s]*)+\]")
# Parenthetical author-year: `(Li & Chen, 2023)`. Also capture an optional
# NARRATIVE author phrase immediately preceding a bare `(year)` —
# `Smith (2020)`, `Okonkwo and Vidal (2021)`, `Al-Masri et al. (2019)` — so a
# `Smith`→`Jones` swap that keeps the same year and the same ref marker still
# surfaces as a citation delta. The author phrase is capitalized-word runs
# joined by `&` / `and` / `et al.`; the year alone is the parenthetical form.
_NARRATIVE_AUTHOR = (
    r"(?:[A-Z][\w'’-]+(?:\s+(?:&|and|et\s+al\.?)\s*)?)+"
    r"(?:\s+et\s+al\.?)?\s+"
)
AUTHOR_YEAR_RE = re.compile(
    rf"(?:{_NARRATIVE_AUTHOR})?\((?:[^()]*\b(?:19|20)\d{{2}}[a-z]?\b[^()]*|(?:19|20)\d{{2}}[a-z]?)\)"
)

_DASH_FOLD = str.maketrans({"–": "-", "—": "-", "−": "-"})


def normalize_text(text: str) -> str:
    """NFKC + dash/minus folding over the WHOLE text, before any split."""
    return unicodedata.normalize("NFKC", text).translate(_DASH_FOLD)


def _prose(normalized: str) -> str:
    return COMMENT_RE.sub(" ", normalized)


def extract_numbers(text: str) -> Counter:
    return Counter(m.group(0) for m in NUMBER_RE.finditer(_prose(normalize_text(text))))


def extract_citation_tokens(text: str) -> Counter:
    normalized = normalize_text(text)
    tokens: Counter = Counter()
    for m in REF_MARKER_RE.finditer(normalized):
        tokens[f"ref:{m.group(1)}"] += 1  # keyed on slug, status tokens ignored
    for m in ANCHOR_MARKER_RE.finditer(normalized):
        tokens[m.group(1)] += 1
    prose = _prose(normalized)
    for pattern in (SQUARE_CITATION_RE, AUTHOR_YEAR_RE):
        for m in pattern.finditer(prose):
            tokens[re.sub(r"\s+", " ", m.group(0))] += 1
    return tokens


def protected_term_counts(text: str, protected_terms) -> Counter:
    """Case-sensitive counts with word boundaries on alphanumeric edges."""
    normalized = normalize_text(text)
    counts: Counter = Counter()
    for term in protected_terms:
        pattern = re.escape(normalize_text(term))
        if term and term[0].isalnum():
            pattern = r"(?<!\w)" + pattern
        if term and term[-1].isalnum():
            pattern = pattern + r"(?!\w)"
        counts[term] = len(re.findall(pattern, normalized))
    return counts


def _counter_delta(source: Counter, revision: Counter) -> dict:
    return {"removed": dict(source - revision), "added": dict(revision - source)}


def audit_pair(source: str, revision: str, protected_terms=()) -> dict:
    result = {
        "numbers_delta": _counter_delta(extract_numbers(source), extract_numbers(revision)),
        "citations_delta": _counter_delta(
            extract_citation_tokens(source), extract_citation_tokens(revision)
        ),
        "protected_terms_delta": _counter_delta(
            protected_term_counts(source, protected_terms),
            protected_term_counts(revision, protected_terms),
        ),
    }
    result["conserved"] = all(
        not delta[side]
        for delta in result.values()
        for side in ("removed", "added")
    )
    return result


def _op_texts(op: dict, blocks: dict) -> tuple[str, str]:
    kind = op["op"]
    block_id = op["block_id"]
    if kind == "insert_after":
        return "", op["new_text"]
    if block_id not in blocks:
        raise ValueError(f"op targets unknown block {block_id}")
    old = blocks[block_id].normalized_text
    if kind == "replace_block":
        return old, op["new_text"]
    if kind == "delete_block":
        return old, ""
    raise ValueError(f"unknown op kind {kind!r}")


def _summarize_delta(delta: dict) -> str:
    parts = []
    for label, key in (
        ("numbers", "numbers_delta"),
        ("citations", "citations_delta"),
        ("protected terms", "protected_terms_delta"),
    ):
        for side in ("removed", "added"):
            tokens = delta[key][side]
            if tokens:
                listed = ", ".join(sorted(tokens))
                parts.append(f"{label} {side} [{listed}]")
    return "; ".join(parts)


def audit_patch(patch: dict, base_text: str, protected_terms=()) -> dict:
    from scripts._block_parser import parse_document

    blocks = parse_document(base_text).block_by_id()
    op_reports = []
    advisory_rows = []
    for op_index, op in enumerate(patch["ops"]):
        old, new = _op_texts(op, blocks)
        delta = audit_pair(old, new, protected_terms)
        roadmap_ids = op.get("roadmap_item_ids", [])
        op_reports.append(
            {
                "op_index": op_index,
                "op": op["op"],
                "block_id": op["block_id"],
                "roadmap_item_ids": roadmap_ids,
                "delta": delta,
            }
        )
        if not delta["conserved"]:
            roadmap = ", ".join(roadmap_ids) or "(none)"
            advisory_rows.append(
                f"ADV-REV-{len(advisory_rows) + 1}: op {op_index} {op['op']} "
                f"{op['block_id']} (roadmap: {roadmap}) — {_summarize_delta(delta)}"
            )
    return {
        "conserved": not advisory_rows,
        "op_reports": op_reports,
        "advisory_rows": advisory_rows,
    }


def _split_terms(raw: str | None) -> list[str]:
    return [t.strip() for t in raw.split(",") if t.strip()] if raw else []


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="mode", required=True)

    pair = sub.add_parser("pair", help="audit two full drafts")
    pair.add_argument("--source", type=Path, required=True)
    pair.add_argument("--revision", type=Path, required=True)

    patch = sub.add_parser("patch", help="audit a #390 patch against its base")
    patch.add_argument("--patch", type=Path, required=True)
    patch.add_argument("--base", type=Path, required=True)

    for p in (pair, patch):
        p.add_argument("--protected-terms", help="comma-separated protected terms")
        p.add_argument(
            "--strict",
            action="store_true",
            help="exit 1 on any delta (advisory default: always exit 0)",
        )

    args = parser.parse_args(argv)
    terms = _split_terms(args.protected_terms)
    if args.mode == "pair":
        report = audit_pair(
            args.source.read_text(encoding="utf-8"),
            args.revision.read_text(encoding="utf-8"),
            terms,
        )
    else:
        report = audit_patch(
            json.loads(args.patch.read_text(encoding="utf-8")),
            args.base.read_text(encoding="utf-8"),
            terms,
        )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if (args.strict and not report["conserved"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
