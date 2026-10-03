#!/usr/bin/env python3
"""Full-text stage, step 1: match the PDFs of advanced records.

Usage:
  python prepare_fulltext.py --work W --pdf-dir PDFS [--config screening_config.json] [--map map.csv]

Takes every record whose title/abstract decision is include or unclear (decisions.json) and
looks for its PDF. A PDF matches when its file name contains the whole record ID (R00012), the DOI
(with "/" written as "_" or "-"), or the PMID. For anything else, give a CSV map with the
columns id,pdf. Records without a PDF are listed as "not retrieved" for the PRISMA flow.

Writes ft_manifest.json ([{id, title, pdf}]), ft_not_retrieved.json and ft_not_retrieved.csv.
Preparation waits for every title/abstract decision and required QC recheck. The TA decision
snapshot and retrieval partition are saved in ft_preparation.json; later changes make it stale.
Ambiguous matches require an explicit --map entry. Record-ID matches take priority over DOI/PMID.
Tip: name PDFs by record ID (for example "R00012 Smith 2019.pdf") - it is the most reliable match.
"""
import argparse
import csv
import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import srlib  # noqa: E402


def whole_identifier(name, key):
    stem = os.path.splitext(name.lower())[0]
    # Record IDs and PMIDs use alphanumeric boundaries; DOI punctuation is part of its token.
    boundary = "a-z0-9" if re.fullmatch(r"r\d+|\d+", key.lower()) else "a-z0-9._-"
    return bool(re.search(r"(?<![" + boundary + r"])" + re.escape(key.lower()) +
                          r"(?![" + boundary + r"])", stem))


def match_pdf(rid, record, names):
    exact_id = [p for p, n in names if whole_identifier(n, rid)]
    keys = []
    if record.get("doi"):
        doi = record["doi"].lower()
        keys += [doi.replace("/", sep) for sep in ("_", "-", "")]
    if record.get("pmid"):
        keys.append(record["pmid"])
    candidates = exact_id or [p for p, n in names if any(whole_identifier(n, k) for k in keys)]
    if len(candidates) > 1:
        raise SystemExit(f"ambiguous PDF match for {rid}: {len(candidates)} files; supply an explicit --map entry")
    return candidates[0] if candidates else None


def main():
    srlib.utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--work", required=True)
    ap.add_argument("--pdf-dir", required=True)
    ap.add_argument("--map")
    ap.add_argument("--config", help="the same effective screening config used for title/abstract decisions")
    ap.add_argument("--only-include", action="store_true", help="skip records whose TA decision is unclear")
    a = ap.parse_args()

    work = os.path.abspath(a.work)
    D = srlib.load_json(os.path.join(work, "decisions.json"))
    if D is None:
        raise SystemExit("decisions.json not found - finish title/abstract screening first")
    cfg = srlib.load_config(a.config)
    pending_ids, qc_ids, problems = srlib.ta_status(work, cfg)
    if qc_ids:
        raise SystemExit("full-text preparation blocked: the required title/abstract QC recheck is pending. "
                         "Run build_workflow.py ta --jobs recheck and merge the decisions first; QC may "
                         "advance more records into the full-text set.")
    if pending_ids or problems:
        raise SystemExit("full-text preparation blocked: finish every title/abstract decision and merge the "
                         "current protocol/config revision first")
    U = {u["id"]: u for u in srlib.load_json(os.path.join(work, "records.json"))["unique"]}
    wanted = ("include",) if a.only_include else srlib.ADVANCE
    if a.only_include and any(r["final"]["d"] == "unclear" for r in D.values()):
        raise SystemExit("--only-include would omit advanced unclear records; retrieve them or settle them first")
    ids = sorted(rid for rid, r in D.items() if r["final"]["d"] in wanted)

    pdfs = [p for p in glob.glob(os.path.join(a.pdf_dir, "**", "*"), recursive=True) if p.lower().endswith(".pdf")]
    names = [(p, os.path.basename(p).lower()) for p in pdfs]
    mapped = {}
    if a.map:
        with open(a.map, encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                if row.get("id") and row.get("pdf"):
                    mapped[row["id"].strip()] = row["pdf"].strip()

    man, missing = [], []
    for rid in ids:
        u = U[rid]
        pdf = mapped.get(rid)
        if not pdf:
            pdf = match_pdf(rid, u, names)
        elif not os.path.isfile(pdf):
            raise SystemExit(f"mapped PDF not found for {rid}: {pdf}")
        if pdf and os.path.exists(pdf):
            man.append({"id": rid, "title": u["title"], "pdf": os.path.abspath(pdf).replace("\\", "/")})
        else:
            missing.append({"id": rid, "title": u["title"], "doi": u.get("doi", ""), "pmid": u.get("pmid", ""),
                            "ta_decision": D[rid]["final"]["d"]})

    srlib.save_json(os.path.join(work, "ft_manifest.json"), man, indent=1)
    srlib.save_json(os.path.join(work, "ft_not_retrieved.json"), missing, indent=1)
    srlib.save_json(os.path.join(work, "ft_preparation.json"),
                    {"ta_snapshot": srlib.ta_snapshot(work),
                     "retrieval_hash": srlib.digest({"manifest": man, "not_retrieved": missing})}, indent=1)
    with open(os.path.join(work, "ft_not_retrieved.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id", "ta_decision", "doi", "pmid", "title"], quoting=csv.QUOTE_ALL)
        w.writeheader()
        w.writerows({k: srlib.spreadsheet_text(v) for k, v in row.items()} for row in missing)
    print(f"records advanced at title/abstract: {len(ids)}")
    print(f"PDF found: {len(man)}   not retrieved: {len(missing)} (ft_not_retrieved.csv)")
    if missing:
        print("Add the missing PDFs (name them by record ID) and run this again before the full-text run,")
        print("or report them as 'reports not retrieved' in the PRISMA flow.")


if __name__ == "__main__":
    main()
