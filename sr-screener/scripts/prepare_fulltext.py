#!/usr/bin/env python3
"""Full-text stage, step 1: match the PDFs of advanced records.

Usage:
  python prepare_fulltext.py --work W --pdf-dir PDFS [--map map.csv] [--only-include]

Takes every record whose title/abstract decision is include or unclear (decisions.json) and
looks for its PDF. A PDF matches when its file name contains the record ID (R00012), the DOI
(with "/" written as "_" or "-"), or the PMID. For anything else, give a CSV map with the
columns id,pdf. Records without a PDF are listed as "not retrieved" for the PRISMA flow.

Writes ft_manifest.json ([{id, title, pdf}]), ft_not_retrieved.json and ft_not_retrieved.csv.
Preparation is blocked while the required title/abstract QC recheck is pending: it may advance
more records, so the full-text set cannot be fixed yet.
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


def main():
    srlib.utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--work", required=True)
    ap.add_argument("--pdf-dir", required=True)
    ap.add_argument("--map")
    ap.add_argument("--only-include", action="store_true", help="skip records whose TA decision is unclear")
    a = ap.parse_args()

    work = os.path.abspath(a.work)
    D = srlib.load_json(os.path.join(work, "decisions.json"))
    if D is None:
        raise SystemExit("decisions.json not found - finish title/abstract screening first")
    pend = srlib.load_json(os.path.join(work, "pending.json"), {"screen": [], "adj": []})
    if pend.get("qc"):
        raise SystemExit("full-text preparation blocked: the required title/abstract QC recheck is pending. "
                         "Run build_workflow.py ta --jobs recheck and merge the decisions first; QC may "
                         "advance more records into the full-text set.")
    if pend["screen"] or pend["adj"]:
        print("WARNING: title/abstract screening still has pending records; they are not in this full-text set.")
    U = {u["id"]: u for u in srlib.load_json(os.path.join(work, "records.json"))["unique"]}
    wanted = ("include",) if a.only_include else srlib.ADVANCE
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
            keys = [rid.lower()]
            if u.get("doi"):
                d = u["doi"].lower()
                keys += [d.replace("/", "_"), d.replace("/", "-"), d.replace("/", "")]
            if u.get("pmid"):
                keys.append(u["pmid"])
            for p, n in names:
                if any((k.isdigit() and re.search(r"(?<!\d)" + k + r"(?!\d)", n)) or (not k.isdigit() and k in n)
                       for k in keys):
                    pdf = p
                    break
        if pdf and os.path.exists(pdf):
            man.append({"id": rid, "title": u["title"], "pdf": os.path.abspath(pdf).replace("\\", "/")})
        else:
            missing.append({"id": rid, "title": u["title"], "doi": u.get("doi", ""), "pmid": u.get("pmid", ""),
                            "ta_decision": D[rid]["final"]["d"]})

    srlib.save_json(os.path.join(work, "ft_manifest.json"), man, indent=1)
    srlib.save_json(os.path.join(work, "ft_not_retrieved.json"), missing, indent=1)
    with open(os.path.join(work, "ft_not_retrieved.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id", "ta_decision", "doi", "pmid", "title"])
        w.writeheader()
        w.writerows(missing)
    print(f"records advanced at title/abstract: {len(ids)}")
    print(f"PDF found: {len(man)}   not retrieved: {len(missing)} (ft_not_retrieved.csv)")
    if missing:
        print("Add the missing PDFs (name them by record ID) and run this again before the full-text run,")
        print("or report them as 'reports not retrieved' in the PRISMA flow.")


if __name__ == "__main__":
    main()
