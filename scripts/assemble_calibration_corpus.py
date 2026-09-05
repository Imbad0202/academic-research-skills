"""Gold-corpus manifest assembly for the reviewer-calibration suite (#653).

The calibration protocol's resolved design decisions REJECT shipping a built-in
gold set (domain-coverage bias, staleness). What ships instead is a ONE-RUN
PROVENANCE MANIFEST: pointers (forum/decision note ids), content hashes,
retrieval dates, the label transform, and the exclusion ledger — enough for a
third party to reconstruct the corpus, never the paper text itself (manuscript
licenses vary; OpenReview submission metadata rides each note's own license).

Three subcommands, all deterministic given their inputs:

  select  Pool snapshots (paginated OpenReview API responses, fetched by the
          operator and retained as raw evidence) -> stratified candidate order.
          Ordering is a seeded shuffle: candidates sort by
          sha256(seed US class US paper_id) so the order is reproducible from
          the committed seed alone and cannot be steered per-paper without
          changing the seed string recorded in the manifest. Exclusions (e.g.
          contamination-probe hits) are applied by paper id with a closed
          reason enum; each exclusion promotes the next candidate in order.

  freeze  Selection + fetched per-paper metadata + local PDF cache ->
          corpus/papers.json (label-free) + manifests/gold_labels.json
          (labels; the dispatcher's read fence must never include this file)
          + corpus/pool_<class>_ids.txt (full sorted id lists, so the pool
          membership hash is reconstructable byte-for-byte). Freeze refuses
          to write a papers.json whose non-title payload carries decision
          vocabulary — the label side lives in gold_labels.json only.

  verify  Committed manifest + PDF cache -> recompute every hash and count,
          cross-check papers.json against gold_labels.json, and re-derive the
          pool hashes from the committed id lists. Exit 1 on any mismatch.

Label transform (ICLR-style binary corpus): a decision string matching
"Accept (Poster|Spotlight|Oral)" maps to gold label `accept`; the rejected
pool's decisions map to `reject`. Revision labels (minor/major) do not exist
at this venue, so the Minor/Major boundary sub-matrix publishes as
NOT ESTIMABLE per the calibration protocol Phase 2.5.

Extracted-text hashes are pinned to the extractor: pypdf's text extraction is
version-sensitive, so the manifest records `pypdf_version` alongside
`extracted_text_sha256` and `verify` compares only when the installed version
matches (a version drift downgrades that check to a named warning, never a
silent pass). The normalization RULE (`_calibration_pdf_text.TEXT_NORMALIZATION`,
shared with the dispatcher) is also recorded and mismatches are hard failures.

Stdlib + pypdf (existing repo dependency: pdf_read_preflight.py).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _calibration_pdf_text import (  # noqa: E402
    TEXT_NORMALIZATION,
    pdf_facts,
    pypdf,
    sha256_hex,
)

US = "\x1f"  # unit separator: unambiguous key joiner (ids are ASCII base64-ish)

CLASSES = ("accepted", "rejected")

EXCLUSION_REASONS = frozenset(
    {
        "no_pdf",
        "contamination_probe_hit",
        "page_count_exceeds_cap",
        "pdf_fetch_failed",
        "duplicate_of_selected",
        "other",
    }
)

ACCEPT_DECISION_RE = re.compile(r"^Accept \((Poster|Spotlight|Oral)\)$")

# OpenReview forum ids are URL-safe base64-ish tokens; ids are later spliced
# into file names (`<id>.pdf`, cards/<id>/), so anything else is refused here.
PAPER_ID_RE = re.compile(r"^[A-Za-z0-9_-]+$")

# Decision vocabulary that must never appear in papers.json outside title text.
# Guard is substring-based over a title-redacted serialization: keys, venue
# strings, and decision strings are all structural, so any hit is a leak.
LABEL_LEAK_TOKENS = (
    "accept",
    "reject",
    "poster",
    "spotlight",
    "oral",
    "decision",
    "withdrawn",
    "desk",
    "label",
)


def order_key(seed: str, cls: str, paper_id: str) -> str:
    return sha256_hex(f"{seed}{US}{cls}{US}{paper_id}".encode("utf-8"))


def load_pool(paths: list[Path]) -> dict[str, dict]:
    """Merge paginated pool snapshots into {paper_id: note}, refusing dupes
    with conflicting payloads (same-id re-fetches must be byte-identical)."""
    pool: dict[str, dict] = {}
    for path in paths:
        notes = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(notes, list):
            raise SystemExit(f"pool file is not a JSON array: {path}")
        for note in notes:
            paper_id = note.get("id")
            if not isinstance(paper_id, str) or not PAPER_ID_RE.match(paper_id):
                raise SystemExit(f"pool note with missing or malformed id in {path}: {paper_id!r}")
            prior = pool.get(paper_id)
            if prior is not None and prior != note:
                raise SystemExit(f"conflicting duplicate for {paper_id} in {path}")
            pool[paper_id] = note
    return pool


def pool_ids_hash(ids: list[str]) -> str:
    return sha256_hex("\n".join(sorted(ids)).encode("utf-8"))


def load_exclusions(path: Path | None) -> dict[str, dict]:
    """{paper_id: {"reason", "note"}} from the operator's exclusion ledger."""
    if path is None:
        return {}
    rows = json.loads(path.read_text(encoding="utf-8"))
    out: dict[str, dict] = {}
    for row in rows:
        reason = row["reason"]
        if reason not in EXCLUSION_REASONS:
            raise SystemExit(f"unknown exclusion reason {reason!r} for {row['paper_id']}")
        if reason == "other" and not row.get("note", "").strip():
            raise SystemExit(f"exclusion reason 'other' requires a note ({row['paper_id']})")
        out[row["paper_id"]] = {"reason": reason, "note": row.get("note", "")}
    return out


def pool_list_mismatches(corpus_dir: Path, pools: dict[str, dict]) -> list[str]:
    """Compare the committed `pool_<cls>_ids.txt` lists against a pools
    snapshot ({cls: {count, ids_sha256}}); one message per mismatch."""
    problems: list[str] = []
    for cls, ref in pools.items():
        ids_file = corpus_dir / f"pool_{cls}_ids.txt"
        if not ids_file.is_file():
            problems.append(f"missing pool id list: {ids_file}")
            continue
        ids = ids_file.read_text(encoding="utf-8").split()
        if len(ids) != ref["count"]:
            problems.append(f"pool {cls}: id list count {len(ids)} != snapshot {ref['count']}")
        if pool_ids_hash(ids) != ref["ids_sha256"]:
            problems.append(f"pool {cls}: ids_sha256 mismatch")
    return problems


def cmd_select(args: argparse.Namespace) -> int:
    pools = {
        "accepted": load_pool([Path(p) for p in args.accepted_pool]),
        "rejected": load_pool([Path(p) for p in args.rejected_pool]),
    }
    overlap = set(pools["accepted"]) & set(pools["rejected"])
    if overlap:
        raise SystemExit(f"papers present in both pools: {sorted(overlap)[:5]}")
    exclusions = load_exclusions(Path(args.exclusions) if args.exclusions else None)
    quotas = {"accepted": args.n_accepted, "rejected": args.n_rejected}

    result: dict = {
        "seed": args.seed,
        "selection_rule": (
            "per class, sort pool ids by sha256(seed US class US id); walk in that "
            "order; skip ids in the exclusion ledger; take the first N remaining"
        ),
        "quotas": quotas,
        "pools": {},
        "candidates": {},
        "selected": {},
        "exclusions_applied": [],
    }
    for cls in CLASSES:
        ids = list(pools[cls])
        ordered = sorted(ids, key=lambda i: order_key(args.seed, cls, i))
        picked: list[str] = []
        candidates: list[str] = []
        for paper_id in ordered:
            if len(picked) >= quotas[cls] and len(candidates) >= args.candidate_depth:
                break
            candidates.append(paper_id)
            if paper_id in exclusions:
                exc = exclusions[paper_id]
                result["exclusions_applied"].append(
                    {"paper_id": paper_id, "class": cls, "reason": exc["reason"], "note": exc["note"]}
                )
                continue
            if len(picked) < quotas[cls]:
                picked.append(paper_id)
        if len(picked) < quotas[cls]:
            raise SystemExit(f"pool {cls} exhausted before quota: {len(picked)}/{quotas[cls]}")
        result["pools"][cls] = {"count": len(ids), "ids_sha256": pool_ids_hash(ids)}
        result["candidates"][cls] = candidates
        result["selected"][cls] = picked
        if args.ids_out_dir:
            ids_dir = Path(args.ids_out_dir)
            ids_dir.mkdir(parents=True, exist_ok=True)
            (ids_dir / f"pool_{cls}_ids.txt").write_text(
                "\n".join(sorted(ids)) + "\n", encoding="utf-8"
            )

    out = Path(args.out)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"selection written: {out}")
    for cls in CLASSES:
        print(f"  {cls}: {len(result['selected'][cls])}/{result['pools'][cls]['count']}")
    return 0


def leak_scan(papers_payload: dict) -> list[str]:
    """Decision-vocabulary hits in the PER-PAPER entries, titles exempt.

    The guard's scope is per-paper label leakage: papers.json is the one
    corpus file on the dispatcher's read path, so no individual entry may
    carry decision vocabulary (titles are exempt — a paper may legitimately
    be titled "Rejection sampling..."). Corpus-LEVEL composition (pool names
    and counts) is public information carried elsewhere in the manifest and
    in the README; it does not identify any paper's label.
    """
    redacted = json.loads(json.dumps(papers_payload.get("papers", [])))
    for paper in redacted:
        paper["title"] = ""
    haystack = json.dumps(redacted, ensure_ascii=False).lower()
    return [tok for tok in LABEL_LEAK_TOKENS if tok in haystack]


def cmd_freeze(args: argparse.Namespace) -> int:
    selection = json.loads(Path(args.selection).read_text(encoding="utf-8"))
    metadata = json.loads(Path(args.metadata).read_text(encoding="utf-8"))
    meta_by_id = {m["paper_id"]: m for m in metadata["papers"]}
    pdf_dir = Path(args.pdf_dir)
    out_dir = Path(args.out_dir)

    if pypdf is None:
        raise SystemExit("pypdf is required for freeze/verify")
    excluded = {e["paper_id"] for e in selection["exclusions_applied"]}
    papers: list[dict] = []
    labels: list[dict] = []
    freeze_exclusions: list[dict] = []
    for cls in CLASSES:
        quota = selection["quotas"][cls]
        taken = 0
        for paper_id in selection["candidates"][cls]:
            if taken >= quota:
                break
            if paper_id in excluded:
                continue
            meta = meta_by_id.get(paper_id)
            if meta is None:
                raise SystemExit(
                    f"candidate {paper_id} ({cls}) reached without fetched metadata; "
                    f"fetch more candidates or record an exclusion"
                )
            pdf_path = pdf_dir / f"{paper_id}.pdf"
            if not pdf_path.is_file():
                raise SystemExit(f"missing cached PDF for {paper_id}: {pdf_path}")
            pdf_sha, text_sha, pages, _ = pdf_facts(pdf_path)
            if pages > args.page_cap:
                freeze_exclusions.append(
                    {
                        "paper_id": paper_id,
                        "class": cls,
                        "reason": "page_count_exceeds_cap",
                        "note": f"{pages} pages > cap {args.page_cap}",
                    }
                )
                continue
            decision_raw = meta["decision_raw"]
            if cls == "accepted":
                if not ACCEPT_DECISION_RE.match(decision_raw):
                    raise SystemExit(f"{paper_id}: unexpected accepted decision {decision_raw!r}")
                label = "accept"
            else:
                if "reject" not in decision_raw.lower():
                    raise SystemExit(f"{paper_id}: unexpected rejected decision {decision_raw!r}")
                label = "reject"
            papers.append(
                {
                    "paper_id": paper_id,
                    "title": meta["title"],
                    "pdf_url": meta["pdf_url"],
                    "pdf_sha256": pdf_sha,
                    "extracted_text_sha256": text_sha,
                    "page_count": pages,
                    "retrieved_at": meta["retrieved_at"],
                }
            )
            labels.append(
                {
                    "paper_id": paper_id,
                    "label": label,
                    "decision_raw": decision_raw,
                    "decision_note_id": meta["decision_note_id"],
                    "openreview_venue_string": meta["venue_string"],
                }
            )
            taken += 1
        if taken < quota:
            raise SystemExit(f"freeze could not fill quota for {cls}: {taken}/{quota}")

    papers.sort(key=lambda p: p["paper_id"])  # id order: never class-blocked
    labels.sort(key=lambda p: p["paper_id"])

    papers_payload = {
        "suite": "reviewer_calibration",
        "source": {
            "api": "OpenReview API v2 (api2.openreview.net)",
            "venue_id": metadata["venue_id"],
            "pools": selection["pools"],
            "pool_id_lists": {
                cls: f"corpus/pool_{cls}_ids.txt" for cls in CLASSES
            },
        },
        "selection": {
            "seed": selection["seed"],
            "rule": selection["selection_rule"],
            "quotas": selection["quotas"],
            "page_cap": args.page_cap,
            "exclusions": selection["exclusions_applied"] + freeze_exclusions,
        },
        "extraction": {
            "tool": "pypdf",
            "pypdf_version": pypdf.__version__,
            "text_normalization": TEXT_NORMALIZATION,
        },
        "papers": papers,
    }
    hits = leak_scan(papers_payload)
    if hits:
        raise SystemExit(f"label-leak guard: decision vocabulary in papers.json: {hits}")

    corpus_dir = out_dir / "corpus"
    manifests_dir = out_dir / "manifests"
    corpus_dir.mkdir(parents=True, exist_ok=True)
    manifests_dir.mkdir(parents=True, exist_ok=True)
    (corpus_dir / "papers.json").write_text(
        json.dumps(papers_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    labels_payload = {
        "label_transform": (
            "ICLR 2026 public decision -> binary gold label: 'Accept "
            "(Poster|Spotlight|Oral)' -> accept; Rejected_Submission pool "
            "decisions -> reject. Withdrawn and desk-rejected submissions sit "
            "in separate OpenReview venue partitions and never enter a pool."
        ),
        "labels": labels,
    }
    (manifests_dir / "gold_labels.json").write_text(
        json.dumps(labels_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    problems = pool_list_mismatches(corpus_dir, selection["pools"])
    if problems:
        raise SystemExit(
            "pool id lists do not match the selection snapshot (run `select "
            f"--ids-out-dir {corpus_dir}` first): " + "; ".join(problems)
        )
    print(f"frozen: {corpus_dir / 'papers.json'} ({len(papers)} papers)")
    print(f"frozen: {manifests_dir / 'gold_labels.json'}")
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    out_dir = Path(args.out_dir)
    papers_payload = json.loads((out_dir / "corpus" / "papers.json").read_text(encoding="utf-8"))
    labels_payload = json.loads(
        (out_dir / "manifests" / "gold_labels.json").read_text(encoding="utf-8")
    )
    pdf_dir = Path(args.pdf_dir)
    failures: list[str] = []
    warnings: list[str] = []

    paper_ids = [p["paper_id"] for p in papers_payload["papers"]]
    label_ids = [r["paper_id"] for r in labels_payload["labels"]]
    if paper_ids != sorted(paper_ids):
        failures.append("papers.json not sorted by paper_id")
    if sorted(paper_ids) != sorted(label_ids):
        failures.append("papers.json and gold_labels.json id sets differ")
    for row in labels_payload["labels"]:
        if row["label"] not in ("accept", "reject"):
            failures.append(f"{row['paper_id']}: invalid label {row['label']!r}")

    recorded_norm = papers_payload["extraction"].get("text_normalization")
    if recorded_norm != TEXT_NORMALIZATION:
        failures.append(
            f"text_normalization rule mismatch: manifest {recorded_norm!r} vs "
            f"checker {TEXT_NORMALIZATION!r} (a rule, not a version: re-freeze)"
        )
    version_match = pypdf is not None and (
        pypdf.__version__ == papers_payload["extraction"]["pypdf_version"]
    )
    if not version_match:
        warnings.append(
            "pypdf version differs from manifest; extracted_text_sha256 not compared"
        )
    for paper in papers_payload["papers"]:
        pdf_path = pdf_dir / f"{paper['paper_id']}.pdf"
        if not pdf_path.is_file():
            warnings.append(f"{paper['paper_id']}: PDF not in local cache; hash not recomputed")
            continue
        pdf_sha, text_sha, pages, _ = pdf_facts(pdf_path, extract_text=version_match)
        if pdf_sha != paper["pdf_sha256"]:
            failures.append(f"{paper['paper_id']}: pdf_sha256 mismatch")
        if pages != paper["page_count"]:
            failures.append(f"{paper['paper_id']}: page_count mismatch ({pages})")
        if version_match and text_sha != paper["extracted_text_sha256"]:
            failures.append(f"{paper['paper_id']}: extracted_text_sha256 mismatch")

    failures.extend(pool_list_mismatches(out_dir / "corpus", papers_payload["source"]["pools"]))

    hits = leak_scan(papers_payload)
    if hits:
        failures.append(f"label-leak guard: {hits}")

    for line in warnings:
        print(f"WARN: {line}")
    if failures:
        for line in failures:
            print(f"FAIL: {line}", file=sys.stderr)
        return 1
    print(f"verify PASS: {len(paper_ids)} papers, all recomputable facts match")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    p_sel = sub.add_parser("select", help="deterministic stratified candidate selection")
    p_sel.add_argument("--accepted-pool", nargs="+", required=True)
    p_sel.add_argument("--rejected-pool", nargs="+", required=True)
    p_sel.add_argument("--seed", required=True)
    p_sel.add_argument("--n-accepted", type=int, default=6)
    p_sel.add_argument("--n-rejected", type=int, default=6)
    p_sel.add_argument("--candidate-depth", type=int, default=18)
    p_sel.add_argument("--exclusions")
    p_sel.add_argument("--ids-out-dir")
    p_sel.add_argument("--out", required=True)
    p_sel.set_defaults(func=cmd_select)

    p_frz = sub.add_parser("freeze", help="write papers.json + gold_labels.json")
    p_frz.add_argument("--selection", required=True)
    p_frz.add_argument("--metadata", required=True)
    p_frz.add_argument("--pdf-dir", required=True)
    p_frz.add_argument("--out-dir", required=True)
    p_frz.add_argument("--page-cap", type=int, default=60)
    p_frz.set_defaults(func=cmd_freeze)

    p_ver = sub.add_parser("verify", help="recompute and cross-check the manifest")
    p_ver.add_argument("--out-dir", required=True)
    p_ver.add_argument("--pdf-dir", required=True)
    p_ver.set_defaults(func=cmd_verify)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
