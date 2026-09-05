"""Authenticated OpenReview fetch for the #653 reviewer-calibration corpus.

Operator tool (network, needs an OpenReview account; no CI path). Reads
OPENREVIEW_USERNAME / OPENREVIEW_PASSWORD from the environment (never from
argv), fetches per-paper metadata + the public Decision note + the PDF for the
candidate ids in `runs/raw/selection.json`, and writes:

  <out>/fetched_metadata.json   (freeze input for assemble_calibration_corpus.py)
  <pdf_dir>/<paper_id>.pdf       (local cache; never committed — manuscript
                                  licenses vary, the manifest ships hashes only)

Usage:
  python3 scripts/fetch_calibration_corpus.py \
      --selection evals/heldout/reviewer_calibration/runs/raw/selection.json \
      --out <dir> --pdf-dir <dir> [--per-class N] [--only ID ...] [--dry-run]

--per-class N fetches the first N candidates of each class (default 8: the 6
selected plus 2 spares so a page-cap exclusion at freeze can promote the next
candidate without a second fetch round). Third-party reconstruction: run this,
then `assemble_calibration_corpus.py verify` against the committed manifest.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import time
from pathlib import Path

import openreview

VENUE_ID = "ICLR.cc/2026/Conference"
PAPER_ID_RE = re.compile(r"^[A-Za-z0-9_-]+$")  # ids become file names below


def utcnow() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def val(content: dict, key: str, default=None):
    v = content.get(key)
    if isinstance(v, dict) and "value" in v:
        return v["value"]
    return v if v is not None else default


def fetch_one(client, paper_id: str, pdf_dir: Path, dry: bool) -> dict:
    note = client.get_note(paper_id)
    c = note.content
    title = val(c, "title")
    venue_string = val(c, "venue")
    venueid = val(c, "venueid")
    number = note.number
    # Decision note: a reply on the forum under the Submission<N>/-/Decision invitation.
    dec_inv = f"{VENUE_ID}/Submission{number}/-/Decision"
    decisions = client.get_notes(forum=paper_id, invitation=dec_inv)
    if not decisions:
        # fallback: scan all replies for a `decision` field
        replies = client.get_notes(forum=paper_id)
        decisions = [r for r in replies if "decision" in (r.content or {})]
    if len(decisions) != 1:
        raise SystemExit(f"{paper_id}: expected exactly one Decision note, got {len(decisions)}")
    dec = decisions[0]
    decision_raw = val(dec.content, "decision")
    if not isinstance(decision_raw, str) or not decision_raw:
        raise SystemExit(f"{paper_id}: Decision note {dec.id} has no decision string")

    pdf_url = f"https://openreview.net/pdf?id={paper_id}"
    pdf_path = pdf_dir / f"{paper_id}.pdf"
    if not dry:
        if not pdf_path.is_file():
            data = client.get_attachment("pdf", paper_id)
            if not data or data[:4] != b"%PDF":
                raise SystemExit(f"{paper_id}: attachment is not a PDF ({len(data or b'')} bytes)")
            pdf_path.write_bytes(data)
    return {
        "paper_id": paper_id,
        "number": number,
        "title": title,
        "venue_string": venue_string,
        "venueid": venueid,
        "decision_note_id": dec.id,
        "decision_raw": decision_raw,
        "pdf_url": pdf_url,
        "retrieved_at": utcnow(),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selection", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--pdf-dir", required=True)
    ap.add_argument("--per-class", type=int, default=8)
    ap.add_argument("--only", nargs="*", default=None)
    ap.add_argument("--dry-run", action="store_true", help="metadata only, no PDF download")
    args = ap.parse_args()

    user = os.environ.get("OPENREVIEW_USERNAME")
    pw = os.environ.get("OPENREVIEW_PASSWORD")
    if not user or not pw:
        print("OPENREVIEW_USERNAME / OPENREVIEW_PASSWORD not in environment", file=sys.stderr)
        return 2

    sel = json.loads(Path(args.selection).read_text(encoding="utf-8"))
    ids: list[tuple[str, str]] = []
    for cls in ("accepted", "rejected"):
        for pid in sel["candidates"][cls][: args.per_class]:
            if not PAPER_ID_RE.match(pid):
                raise SystemExit(f"malformed paper id in selection: {pid!r}")
            ids.append((cls, pid))
    if args.only:
        ids = [(c, p) for c, p in ids if p in set(args.only)]

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    pdf_dir = Path(args.pdf_dir)
    pdf_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "fetched_metadata.json"
    existing: dict[str, dict] = {}
    if out_path.is_file():
        existing = {p["paper_id"]: p for p in json.loads(out_path.read_text())["papers"]}

    client = openreview.api.OpenReviewClient(
        baseurl="https://api2.openreview.net", username=user, password=pw
    )
    papers = dict(existing)
    for cls, pid in ids:
        if pid in papers and (args.dry_run or (pdf_dir / f"{pid}.pdf").is_file()):
            print(f"skip {cls} {pid} (cached)")
            continue
        rec = fetch_one(client, pid, pdf_dir, args.dry_run)
        papers[pid] = rec
        pdf_path = pdf_dir / f"{pid}.pdf"
        size = pdf_path.stat().st_size if pdf_path.is_file() else None
        print(f"ok   {cls} {pid} n={rec['number']} decision={rec['decision_raw']!r} pdf_bytes={size}")
        out_path.write_text(
            json.dumps({"venue_id": VENUE_ID, "papers": list(papers.values())}, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        time.sleep(1.0)
    print(f"wrote {out_path} ({len(papers)} papers)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
