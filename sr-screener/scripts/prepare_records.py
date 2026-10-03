#!/usr/bin/env python3
"""Phase 1 (Records Librarian): parse exports, remove duplicates, write screening batches.

Usage:
  python prepare_records.py --inputs EXPORTS_DIR_OR_FILES... --work WORK_DIR [--config screening_config.json]
                            [--db "file.ris=Scopus" ...] [--force]

Reads RIS, PubMed/MEDLINE (.nbib or .txt, also when saved with a .ris extension),
Web of Science plain text and CSV exports. The input files are never modified.

Writes into WORK_DIR:
  records.json        unique records (screening IDs R00001...)
  raw_records.json    every raw record, used later to re-export RIS with labels
  manifest.json       batches: [{batch, path, ids}]
  batches/bNNN.txt    what the reviewers read: "### Rxxxxx | year | type | Lang" blocks
  identification.json PRISMA identification counts (per database / per file, duplicates)
  duplicates.csv      every merged group, for audit
  seeds.json          where the protocol's seed studies landed (if the config lists seeds)
"""
import argparse
import collections
import csv
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import srlib  # noqa: E402


def collect_inputs(paths):
    files = []
    for p in paths:
        if os.path.isdir(p):
            for ext in ("*.ris", "*.nbib", "*.txt", "*.csv", "*.tsv", "*.RIS", "*.NBIB", "*.TXT", "*.CSV"):
                files += glob.glob(os.path.join(p, ext))
        elif os.path.isfile(p):
            files.append(p)
        else:
            raise SystemExit(f"input not found: {p}")
    seen, out = set(), []
    for f in sorted(files, key=lambda x: os.path.basename(x).lower()):
        key = os.path.normcase(os.path.abspath(f))
        if key not in seen:
            seen.add(key)
            out.append(f)
    return out


def main():
    srlib.utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--inputs", nargs="+", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--config")
    ap.add_argument("--db", action="append", default=[], help='override database label: "filename=Database"')
    ap.add_argument("--force", action="store_true", help="overwrite an existing work folder (IDs will change!)")
    a = ap.parse_args()

    cfg = srlib.load_config(a.config)
    work = os.path.abspath(a.work)
    if os.path.exists(os.path.join(work, "records.json")) and not a.force:
        raise SystemExit(
            f"{work} already holds prepared records. Screening IDs must stay stable once screening starts; "
            "use a new --work folder, or --force only if no decisions exist yet.")
    batch_dir = os.path.join(work, "batches")
    os.makedirs(batch_dir, exist_ok=True)
    for old in glob.glob(os.path.join(batch_dir, "b*.txt")):
        os.remove(old)

    db_over = dict(x.split("=", 1) for x in a.db)
    files = collect_inputs(a.inputs)
    in_abs = {os.path.normcase(os.path.abspath(os.path.dirname(f))) for f in files}
    if os.path.normcase(work) in in_abs:
        raise SystemExit("--work must not be one of the input folders")

    all_recs, raw_store, per_file = [], [], []
    for f in files:
        base = os.path.basename(f)
        fmt, recs = srlib.load_export(f)
        if fmt is None:
            print(f"skipped (format not recognised): {base}")
            continue
        fallback = db_over.get(base) or os.path.splitext(base)[0]
        n_before = len(all_recs)
        for r in recs:
            db = db_over.get(base) or srlib.infer_db(r, fallback)
            if not r.get("DB"):
                r["DB"] = [db]
            idx = len(all_recs)
            all_recs.append(srlib.unify(r, db, base, idx))
            raw_store.append(r)
        per_file.append(dict(file=base, format=fmt, records=len(all_recs) - n_before,
                             databases=dict(collections.Counter(x["db"] for x in all_recs[n_before:]))))
        print(f"{base}: {fmt}, {len(all_recs) - n_before} records")
    if not all_recs:
        raise SystemExit("no records found")

    # ---------------------------------------------------------- de-duplication
    parent = list(range(len(all_recs)))
    how = {}
    identifiers = [{k: {r[k]} if r[k] else set() for k in ("doi", "pmid")} for r in all_recs]

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i, j, why):
        ri, rj = find(i), find(j)
        if ri != rj:
            if any(identifiers[ri][k] and identifiers[rj][k] and
                   identifiers[ri][k] != identifiers[rj][k] for k in ("doi", "pmid")):
                return  # Conflicting identifiers, including transitive title-only bridges, need human review.
            low, high = min(ri, rj), max(ri, rj)
            parent[high] = low
            for key in ("doi", "pmid"):
                identifiers[low][key] |= identifiers[high][key]
            how.setdefault(max(i, j), why)

    ntitle = [srlib.norm_title(r["title"]) for r in all_recs]
    # A shared DOI merges two records only when their titles are compatible: supplements and
    # letter/reply pairs sometimes carry one DOI for several different items.
    guard = cfg["dedup"].get("doi_title_guard", True)
    for key in ("pmid", "doi"):
        seen = {}
        for i, r in enumerate(all_recs):
            v = r[key]
            if not v:
                continue
            if v in seen:
                j = seen[v]
                if key == "pmid" or not guard or srlib.titles_compatible(ntitle[i], ntitle[j]):
                    union(i, j, key)
            else:
                seen[v] = i
    seen = {}
    for i, r in enumerate(all_recs):
        nt = ntitle[i]
        if len(nt) < 25:
            continue
        k = (nt, r["year"])
        for j in seen.get(k, []):
            union(i, j, "title+year")
        seen.setdefault(k, []).append(i)
        if r["year"].isdigit():
            for dy in (-1, 1):
                k2 = (nt, str(int(r["year"]) + dy))
                for j in seen.get(k2, []):
                    union(i, j, "title+year(+-1)")

    groups = collections.defaultdict(list)
    for i in range(len(all_recs)):
        groups[find(i)].append(i)

    unique = []
    for members in groups.values():
        ms = [all_recs[i] for i in members]
        rep = max(ms, key=lambda r: (len(r["abstract"]), -srlib.db_rank(r["db"])))
        by_db = sorted(ms, key=lambda r: srlib.db_rank(r["db"]))
        types = []
        for r in by_db:
            if r["type"] and all(r["type"] != t.split(": ", 1)[-1] for t in types):
                types.append(r["type"] if not types else f"{r['db']}: {r['type']}")
        kw_src = next((r for r in by_db if r["db"] == "PubMed" and r["kw"]), None) or rep
        unique.append(dict(
            members=sorted(members),
            sources=sorted({r["db"] for r in ms}, key=srlib.db_rank),
            title=rep["title"] or next((r["title"] for r in ms if r["title"]), ""),
            abstract=rep["abstract"],
            year=rep["year"] or next((r["year"] for r in ms if r["year"]), ""),
            journal=by_db[0]["journal"] or rep["journal"],
            type=" | ".join(types[:3]),
            lang=next((r["lang"] for r in by_db if r["lang"]), ""),
            doi=next((r["doi"] for r in by_db if r["doi"]), ""),
            pmid=next((r["pmid"] for r in by_db if r["pmid"]), ""),
            authors=next((r["authors"] for r in by_db if r["authors"]), []),
            kw=kw_src["kw"][:18],
        ))
    unique.sort(key=lambda u: u["members"][0])
    width = srlib.id_width(len(unique))
    for n, u in enumerate(unique, 1):
        u["id"] = "R" + str(n).zfill(width)

    # ----------------------------------------------------------------- batches
    bcfg = cfg["batching"]
    batches, cur, size = [], [], 0
    for u in unique:
        block = srlib.record_block(u, bcfg["wrap"])
        if cur and (size + len(block) > bcfg["max_chars"] or len(cur) >= bcfg["max_records"]):
            batches.append(cur)
            cur, size = [], 0
        cur.append((u, block))
        size += len(block)
    if cur:
        batches.append(cur)

    manifest, max_lines = [], 0
    bw = max(3, len(str(len(batches))))
    for bi, b in enumerate(batches, 1):
        name = "b" + str(bi).zfill(bw)
        path = os.path.join(batch_dir, name + ".txt")
        ids = [u["id"] for u, _ in b]
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(f"BATCH {name} -- {len(ids)} records: {ids[0]} .. {ids[-1]}\n\n")
            f.write("\n".join(t for _, t in b))
            f.write(f"\n=== END OF BATCH {name} ({len(ids)} records) ===\n")
        for u, t in b:
            u["batch"] = name
            max_lines = max(max_lines, t.count("\n") + 1)
        manifest.append(dict(batch=name, path=path.replace("\\", "/"), ids=ids))

    # ----------------------------------------------------------------- outputs
    srlib.save_json(os.path.join(work, "manifest.json"), manifest)
    srlib.save_json(os.path.join(work, "records.json"),
                    dict(unique=unique, id_width=width, review_id=str(srlib.uuid.uuid4())))
    srlib.save_json(os.path.join(work, "raw_records.json"), [dict(r) for r in raw_store])

    no_abs = sum(1 for u in unique if not u["abstract"])
    ident = dict(
        tool=f"{srlib.TOOL} {srlib.VERSION}",
        files=per_file,
        by_database=dict(collections.Counter(r["db"] for r in all_recs)),
        raw_total=len(all_recs),
        unique_total=len(unique),
        duplicates_removed=len(all_recs) - len(unique),
        no_abstract=no_abs,
        overlap=dict(collections.Counter(" + ".join(u["sources"]) for u in unique)),
        batches=len(manifest),
        max_record_lines=max_lines,
    )
    srlib.save_json(os.path.join(work, "identification.json"), ident, indent=1)

    with open(os.path.join(work, "duplicates.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, quoting=csv.QUOTE_ALL)
        w.writerow(["kept_as", "member_index", "matched_on", "database", "file", "year", "doi", "pmid", "title"])
        for u in unique:
            if len(u["members"]) < 2:
                continue
            for i in u["members"]:
                r = all_recs[i]
                w.writerow([srlib.spreadsheet_text(v) for v in
                            [u["id"], i, how.get(i, "first"), r["db"], r["src_file"], r["year"], r["doi"],
                             r["pmid"], r["title"]]])

    seeds_out = []
    if cfg.get("seeds"):
        by_doi = {u["doi"]: u["id"] for u in unique if u["doi"]}
        by_pmid = {u["pmid"]: u["id"] for u in unique if u["pmid"]}
        titles = [(srlib.norm_title(u["title"]), u["id"]) for u in unique]
        for s in cfg["seeds"]:
            hit, on = None, None
            if s.get("doi") and srlib.norm_doi(s["doi"]) in by_doi:
                hit, on = by_doi[srlib.norm_doi(s["doi"])], "doi"
            elif s.get("pmid") and str(s["pmid"]) in by_pmid:
                hit, on = by_pmid[str(s["pmid"])], "pmid"
            elif s.get("title") and len(srlib.norm_title(s["title"])) >= 20:
                t = srlib.norm_title(s["title"])
                hit = next((i for nt, i in titles
                            if len(nt) >= 20 and (nt.startswith(t[:60]) or t.startswith(nt[:60]))), None)
                on = "title" if hit else None
            seeds_out.append(dict(label=s.get("label") or s.get("title") or s.get("doi"), id=hit, matched_on=on))
        srlib.save_json(os.path.join(work, "seeds.json"), seeds_out, indent=1)

    print(f"\nraw records: {len(all_recs)}  by database: {ident['by_database']}")
    print(f"unique after de-duplication: {len(unique)}  (duplicates removed: {ident['duplicates_removed']})")
    print(f"records without abstract: {no_abs}")
    print(f"batches: {len(manifest)}  (max {bcfg['max_records']} records / {bcfg['max_chars']} chars each)")
    for s in seeds_out:
        print(f"seed {s['label']!r}: " + (f"found as {s['id']} ({s['matched_on']})" if s["id"] else
                                          "NOT FOUND in the search results - check the search strategy"))
    print(f"work folder: {work}")


if __name__ == "__main__":
    main()
