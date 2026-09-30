#!/usr/bin/env python3
"""Merge reviewer decisions into final screening decisions and list what is still pending.

Usage:
  python merge_decisions.py --work W --from PATH [PATH ...] [--config screening_config.json]
                            [--stage ta|ft] [--overrides overrides.csv] [--audit]

PATH may be a Workflow run journal (journal.jsonl), a folder searched recursively for
journal.jsonl files and *.json decision files, or a JSON file holding objects like
{"label": "A:b001", "decisions": [{"id": "R00001", "d": "exclude", "code": "E2", "why": "..."}]}.
Labels: A:<batch>, B:<batch>, ADJ:<batch>, QC:<batch> (title/abstract) and FTA:<id>, FTB:<id>,
FTADJ:<id> (full text). Suffixes such as ":retry" are ignored; "·" is accepted as separator.

Rules (see references/decision_rules.md):
  * a record is final only when both reviewers decided it and, when they disagree on
    advance vs exclude, the adjudicator decided it too (or conflict_policy is "liberal");
  * a decision whose label and code disagree, or whose ID is not in the batch the agent
    was given, is discarded - the record is retried, never filled in by default;
  * when both reviewers exclude with different codes, the earlier code in protocol order wins;
  * QC rechecks and human overrides (overrides.csv: id,d,code,why[,by]) are applied last
    and logged on the record.

Writes decisions.json, pending.json, agreement.json, qc_candidates.json (title/abstract) or
ft_decisions.json, ft_pending.json, ft_agreement.json (full text) into the work folder.
"""
import argparse
import csv
import json
import os
import random
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import srlib  # noqa: E402

LABEL_TA = re.compile(r"^(A|B|ADJ|QC)[·:|_ ]([bq]\d+)")
LABEL_FT = re.compile(r"^(FTA|FTB|FTADJ)[·:|_ ](R\d+)")


def extract_json(obj):
    if isinstance(obj, list):
        for x in obj:
            yield from extract_json(x)
    elif isinstance(obj, dict):
        if isinstance(obj.get("label"), str) and isinstance(obj.get("decisions"), list):
            yield obj["label"], obj["decisions"]
        elif "result" in obj:
            yield from extract_json(obj["result"])
        elif isinstance(obj.get("decisions"), list):
            yield from extract_json(obj["decisions"])


def iter_results(paths):
    files = []
    for p in paths:
        if os.path.isdir(p):
            for root, _, fs in os.walk(p):
                for f in fs:
                    if f == "journal.jsonl" or (f.endswith(".json") and not f.endswith(".meta.json")):
                        files.append(os.path.join(root, f))
        elif os.path.isfile(p):
            files.append(p)
        else:
            raise SystemExit(f"--from path not found: {p}")
    files = sorted(set(files), key=lambda f: (os.path.getmtime(f), f))
    for f in files:
        if f.endswith(".jsonl"):
            labels = {}
            with open(f, encoding="utf-8") as fh:
                for line in fh:
                    try:
                        o = json.loads(line)
                    except ValueError:
                        continue
                    if o.get("type") == "started":
                        labels[o.get("agentId")] = o.get("label", "")
                    elif o.get("type") == "result":
                        res = o.get("result")
                        if isinstance(res, dict) and isinstance(res.get("decisions"), list):
                            yield f, labels.get(o.get("agentId"), ""), res["decisions"]
        else:
            try:
                with open(f, encoding="utf-8") as fh:
                    obj = json.load(fh)
            except (ValueError, UnicodeDecodeError):
                continue
            for label, decs in extract_json(obj):
                yield f, label, decs


def short(d):
    return f"{d['d']}/{d['code']}" if d else ""


def pick_code(codes_order, *decs):
    ds = [d for d in decs if d]
    return min(ds, key=lambda d: codes_order.index(d["code"]) if d["code"] in codes_order else 999)


def load_overrides(path, codes, valid_ids):
    """Human decisions (overrides.csv: id,d,code,why[,by]). They settle a record even when it is pending."""
    ov = {}
    if not path:
        return ov
    with open(path, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            rid = (row.get("id") or "").strip()
            dec = {"d": (row.get("d") or "").strip().lower(), "code": (row.get("code") or "").strip().upper(),
                   "why": (row.get("why") or "").strip()}
            if rid not in valid_ids:
                print(f"override skipped (unknown id): {rid}")
                continue
            if not srlib.valid_decision(dec, codes):
                print(f"override skipped (label/code mismatch): {rid} {dec['d']}/{dec['code']}")
                continue
            ov[rid] = dict(dec, by=(row.get("by") or "").strip() or "HUMAN")
    return ov


def settle(final, rid, rec, auto, ov):
    """Store the final decision: a human override wins over the automatic one (which is kept)."""
    if rid in ov:
        if auto:
            rec["pre_override"] = auto
        rec["final"] = ov[rid]
    elif auto:
        rec["final"] = auto
    else:
        return False
    final[rid] = rec
    return True


def merge_ta(a, cfg, work):
    manifest = srlib.load_json(os.path.join(work, "manifest.json"))
    if not manifest:
        raise SystemExit("manifest.json not found - run prepare_records.py first")
    codes = srlib.exclusion_codes(cfg, "ta")
    batch_ids = {m["batch"]: set(m["ids"]) for m in manifest}
    batch_ids.update({q: set(ids) for q, ids in (srlib.load_json(os.path.join(work, "qc_batches.json"), {}) or {}).items()})
    got = {"A": {}, "B": {}, "ADJ": {}, "QC": {}}
    stats = {"results": 0, "kept": 0, "dropped_invalid": 0, "dropped_wrong_batch": 0, "unlabelled": 0}
    for src, label, decs in iter_results(a.sources):
        m = LABEL_TA.match(label or "")
        if not m:
            stats["unlabelled"] += 1
            continue
        role, b = m.group(1), m.group(2)
        stats["results"] += 1
        allowed = batch_ids.get(b, set())
        for d in decs:
            if not isinstance(d, dict) or d.get("id") not in allowed:
                stats["dropped_wrong_batch"] += 1
                continue
            if not srlib.valid_decision(d, codes):
                stats["dropped_invalid"] += 1
                continue
            if d["id"] not in got[role]:
                got[role][d["id"]] = {k: d.get(k, "") for k in ("d", "code", "why")}
                stats["kept"] += 1

    if a.audit:
        return audit_report(work, manifest, got["QC"], codes)

    adv = lambda d: d["d"] in srlib.ADVANCE
    policy = cfg["conflict_policy"]
    ov = load_overrides(a.overrides, codes, {i for m in manifest for i in m["ids"]})
    final, pend_screen, pend_adj, pairs = {}, [], [], []
    for m in manifest:
        b = m["batch"]
        missA = [i for i in m["ids"] if i not in got["A"] and i not in ov]
        missB = [i for i in m["ids"] if i not in got["B"] and i not in ov]
        if missA or missB:
            pend_screen.append({"b": b, "missA": missA, "missB": missB})
        need = []
        for rid in m["ids"]:
            A, B = got["A"].get(rid), got["B"].get(rid)
            rec, auto, item = {"A": A, "B": B}, None, None
            if A and B:
                pairs.append((adv(A), adv(B)))
                if adv(A) == adv(B):
                    if adv(A):
                        src = A if A["d"] == "include" else (B if B["d"] == "include" else A)
                        auto = {"d": src["d"], "code": src["code"], "why": src["why"], "by": "A+B"}
                    else:
                        src = pick_code(codes, A, B)
                        auto = {"d": "exclude", "code": src["code"], "why": src["why"], "by": "A+B"}
                elif rid in got["ADJ"]:
                    rec["ADJ"] = got["ADJ"][rid]
                    auto = dict(got["ADJ"][rid], by="ADJ")
                elif policy == "liberal":
                    src = A if adv(A) else B
                    auto = {"d": src["d"], "code": src["code"], "why": src["why"], "by": "LIBERAL"}
                else:
                    item = {"id": rid, "A": short(A), "B": short(B)}
            if not settle(final, rid, rec, auto, ov) and item:
                need.append(item)
        if need:
            pend_adj.append({"b": b, "items": need})

    # QC rechecks: an exclusion the senior reviewer would advance is advanced (policy "advance") or flagged.
    # Human overrides are never changed by QC.
    qc_policy = cfg["qc"].get("policy", "advance")
    qc_changed = qc_flagged = 0
    for rid, Q in got["QC"].items():
        rec = final.get(rid)
        if not rec or rid in ov:
            continue
        rec["QC"] = Q
        if rec["final"]["d"] == "exclude" and Q["d"] in srlib.ADVANCE:
            if qc_policy == "advance":
                rec["pre_qc"] = rec["final"]
                rec["final"] = dict(Q, by="QC")
                qc_changed += 1
            else:
                rec["qc_flag"] = True
                qc_flagged += 1

    n_over = len(ov)

    agree = srlib.agreement(pairs)
    agree["conflicts"] = sum(1 for r in final.values() if r.get("A") and r.get("B") and adv(r["A"]) != adv(r["B"])) + \
        sum(len(p["items"]) for p in pend_adj)
    agree["resolved_by"] = {}
    for r in final.values():
        by = r["final"]["by"]
        agree["resolved_by"][by] = agree["resolved_by"].get(by, 0) + 1

    srlib.save_json(os.path.join(work, "decisions.json"), final)
    srlib.save_json(os.path.join(work, "pending.json"), {"screen": pend_screen, "adj": pend_adj}, indent=1)
    srlib.save_json(os.path.join(work, "agreement.json"), agree, indent=1)
    qc_cands = make_qc_candidates(work, cfg, manifest, final, set(got["QC"]) | set(ov))

    total = sum(len(m["ids"]) for m in manifest)
    fc = {}
    for r in final.values():
        fc[r["final"]["d"]] = fc.get(r["final"]["d"], 0) + 1
    n_ps = sum(len(set(p["missA"]) | set(p["missB"])) for p in pend_screen)
    n_pa = sum(len(p["items"]) for p in pend_adj)
    print(f"results read: {stats['results']}  decisions kept: {stats['kept']}  "
          f"dropped (label/code mismatch): {stats['dropped_invalid']}  dropped (ID not in that batch): "
          f"{stats['dropped_wrong_batch']}  results without a screening label: {stats['unlabelled']}")
    print(f"records: {total}  final: {len(final)} {fc}  by: {agree['resolved_by']}")
    print(f"agreement (advance vs exclude): n={agree['n']} observed={agree['observed_agreement']} "
          f"kappa={agree['kappa']} PABAK={agree['pabak']} conflicts={agree['conflicts']}")
    if got["QC"]:
        print(f"QC rechecks read: {len(got['QC'])}  exclusions advanced by QC: {qc_changed}  flagged: {qc_flagged}")
    if n_over:
        print(f"human overrides applied: {n_over}")
    if qc_cands is not None:
        print(f"QC candidates for recheck: {sum(len(c['ids']) for c in qc_cands)} (qc_candidates.json)")
    if n_ps or n_pa:
        print(f"PENDING: {n_ps} records still need a reviewer decision in {len(pend_screen)} batches; "
              f"{n_pa} conflicts need adjudication -> build_workflow.py ta --jobs pending")
    else:
        print("complete: every record has a final decision")


def make_qc_candidates(work, cfg, manifest, final, skip):
    """Select exclusions for a senior second look and pack them into their own batch files.

    Near-miss: matches at least one pattern in every qc.near_miss group. Random: a reproducible
    sample of the other exclusions, drawn once per review (never redrawn on later merges).
    Candidates go into QC batches (batches/qNNN.txt) listed in qc_batches.json; that registry
    only grows, so a QC run's labels always refer to the same records.
    """
    qc = cfg["qc"]
    groups = qc.get("near_miss") or {}
    k = int(qc.get("random_exclusion_sample") or 0)
    if not groups and not k:
        return None
    recs = {u["id"]: u for u in srlib.load_json(os.path.join(work, "records.json"))["unique"]}
    reg_path = os.path.join(work, "qc_batches.json")
    why_path = os.path.join(work, "qc_reasons.json")
    reg = srlib.load_json(reg_path, {}) or {}
    why = srlib.load_json(why_path, {}) or {}
    pats = {g: [re.compile(p, re.I) for p in ps] for g, ps in groups.items() if ps}
    order = {i: n for n, i in enumerate(i for m in manifest for i in m["ids"])}
    excluded = sorted((rid for rid, r in final.items() if r["final"]["d"] == "exclude"), key=order.get)
    for rid in excluded:
        u = recs[rid]
        text = " ".join([u["title"], u["abstract"], " ".join(u.get("kw", []))])
        if rid not in why and pats and all(any(p.search(text) for p in ps) for ps in pats.values()):
            why[rid] = "near-miss"
    if k and "random" not in why.values():
        rest = [r for r in excluded if r not in why and r not in skip]
        for rid in random.Random(int(qc.get("random_seed", 2026))).sample(rest, min(k, len(rest))):
            why[rid] = "random"
    in_reg = {i for ids in reg.values() for i in ids}
    new = [rid for rid in excluded if rid in why and rid not in in_reg and rid not in skip]
    bcfg = cfg["batching"]
    chunks, cur, size = [], [], 0
    for rid in new:
        block = srlib.record_block(recs[rid], bcfg["wrap"])
        if cur and (size + len(block) > bcfg["max_chars"] or len(cur) >= bcfg["max_records"]):
            chunks.append(cur)
            cur, size = [], 0
        cur.append((rid, block))
        size += len(block)
    if cur:
        chunks.append(cur)
    n = len(reg)
    for chunk in chunks:
        n += 1
        name = f"q{n:03d}"
        ids = [rid for rid, _ in chunk]
        with open(os.path.join(work, "batches", name + ".txt"), "w", encoding="utf-8", newline="\n") as f:
            f.write(f"BATCH {name} -- {len(ids)} records for QC recheck: {ids[0]} .. {ids[-1]}\n\n")
            f.write("\n".join(b for _, b in chunk))
            f.write(f"\n=== END OF BATCH {name} ({len(ids)} records) ===\n")
        reg[name] = ids
    srlib.save_json(reg_path, reg, indent=1)
    srlib.save_json(why_path, why, indent=1)
    still_excluded = set(excluded)
    out = []
    for name, ids in reg.items():
        todo = [i for i in ids if i in still_excluded and i not in skip]
        if todo:
            out.append({"b": name, "ids": todo, "full": todo == ids, "why": {i: why.get(i, "") for i in todo}})
    srlib.save_json(os.path.join(work, "qc_candidates.json"), out, indent=1)
    return out


def audit_report(work, manifest, qc, codes):
    recs = {u["id"]: u for u in srlib.load_json(os.path.join(work, "records.json"))["unique"]}
    rows = []
    for m in manifest:
        for rid in m["ids"]:
            q = qc.get(rid)
            u = recs[rid]
            rows.append([rid, q["d"] if q else "PENDING", q["code"] if q else "", q["why"] if q else "",
                         u["year"], u["title"], u["doi"], u["pmid"]])
    order = {"include": 0, "unclear": 1, "PENDING": 2, "exclude": 3}
    rows.sort(key=lambda r: (order.get(r[1], 9), r[0]))
    path = os.path.join(work, "audit_report.csv")
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "qc_decision", "code", "why", "year", "title", "doi", "pmid"])
        w.writerows(rows)
    n_adv = sum(1 for r in rows if r[1] in srlib.ADVANCE)
    n_pend = sum(1 for r in rows if r[1] == "PENDING")
    print(f"audit: {len(rows)} records, {n_adv} would advance (possible wrong exclusions), {n_pend} pending")
    print(f"report: {path}")


def merge_ft(a, cfg, work):
    man = srlib.load_json(os.path.join(work, "ft_manifest.json"))
    if man is None:
        raise SystemExit("ft_manifest.json not found - run prepare_fulltext.py first")
    codes = srlib.exclusion_codes(cfg, "ft")
    items = {x["id"]: x for x in man}
    got = {"FTA": {}, "FTB": {}, "FTADJ": {}}
    dropped = 0
    for src, label, decs in iter_results(a.sources):
        m = LABEL_FT.match(label or "")
        if not m:
            continue
        role, rid = m.group(1), m.group(2)
        for d in decs:
            if not isinstance(d, dict) or d.get("id") != rid or rid not in items or not srlib.valid_decision(d, codes):
                dropped += 1
                continue
            got[role].setdefault(rid, {k: d.get(k, "") for k in ("d", "code", "why", "where")})
    ov = load_overrides(a.overrides, codes, set(items))
    final, pend_items, pend_adj, pairs = {}, [], [], []
    for rid, x in items.items():
        A, B = got["FTA"].get(rid), got["FTB"].get(rid)
        rec, auto, item = {"A": A, "B": B}, None, None
        if not A or not B:
            if rid not in ov:
                pend_items.append({"id": rid, "pdf": x["pdf"], "title": x.get("title", ""), "A": not A, "B": not B})
        else:
            pairs.append((A["d"] == "include", B["d"] == "include"))
            if A["d"] == B["d"]:
                src = pick_code(codes, A, B) if A["d"] == "exclude" else A
                auto = dict(src, by="A+B")
            elif rid in got["FTADJ"]:
                rec["ADJ"] = got["FTADJ"][rid]
                auto = dict(got["FTADJ"][rid], by="ADJ")
            else:
                item = {"id": rid, "pdf": x["pdf"], "title": x.get("title", ""), "A": short(A), "B": short(B)}
        if not settle(final, rid, rec, auto, ov) and item:
            pend_adj.append(item)
    n_over = len(ov)
    agree = srlib.agreement(pairs)
    srlib.save_json(os.path.join(work, "ft_decisions.json"), final)
    srlib.save_json(os.path.join(work, "ft_pending.json"), {"items": pend_items, "adj": pend_adj}, indent=1)
    srlib.save_json(os.path.join(work, "ft_agreement.json"), agree, indent=1)
    fc = {}
    for r in final.values():
        fc[r["final"]["d"]] = fc.get(r["final"]["d"], 0) + 1
    print(f"reports: {len(items)}  final: {len(final)} {fc}  dropped decisions: {dropped}  overrides: {n_over}")
    print(f"agreement (include vs not): n={agree['n']} observed={agree['observed_agreement']} "
          f"kappa={agree['kappa']} PABAK={agree['pabak']}")
    if pend_items or pend_adj:
        print(f"PENDING: {len(pend_items)} reports need a reviewer decision, {len(pend_adj)} need adjudication "
              "-> build_workflow.py ft --jobs pending")
    else:
        print("complete: every report has a final decision")


def main():
    srlib.utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--work", required=True)
    ap.add_argument("--from", dest="sources", nargs="+", required=True)
    ap.add_argument("--config")
    ap.add_argument("--stage", choices=["ta", "ft"], default="ta")
    ap.add_argument("--overrides")
    ap.add_argument("--audit", action="store_true", help="report QC-recheck decisions of an audited set")
    a = ap.parse_args()
    cfg = srlib.load_config(a.config)
    work = os.path.abspath(a.work)
    if a.stage == "ta":
        merge_ta(a, cfg, work)
    else:
        merge_ft(a, cfg, work)


if __name__ == "__main__":
    main()
