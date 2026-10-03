#!/usr/bin/env python3
"""Merge reviewer decisions into final screening decisions and list what is still pending.

Usage:
  python merge_decisions.py --work W --from PATH [PATH ...] [--config screening_config.json]
                            [--stage ta|ft] [--protocol confirmed_protocol.md]
                            [--overrides overrides.csv] [--pilot-labels pilot_labels.csv] [--audit]

PATH may be a Workflow run journal (journal.jsonl), a folder searched recursively for
journal.jsonl files and *.json decision files, or a JSON file holding objects like
{"label": "A:b001@<context_id from index.json>", "decisions": [{"id": "R00001", "d": "exclude", "code": "E2", "why": "..."}]}.
Labels: A:<batch>, B:<batch>, ADJ:<batch>, QC:<batch> (title/abstract) and FTA:<id>, FTB:<id>,
FTADJ:<id> (full text). Suffixes such as ":retry" are ignored; "·" is accepted as separator.
Every result must carry the current review/revision identity. Missing identities are rejected,
unless the team verifies and explicitly imports old files with --legacy-import-reason "<reason>".
Bound results from other reviews/revisions are never imported. Old decisions remain in the audit.

Rules (see references/decision_rules.md):
  * a record is final only when both reviewers decided it and, when they disagree on
    advance vs exclude, the adjudicator decided it too (or conflict_policy is "liberal");
  * a decision whose label and code disagree, or whose ID is not in the batch the agent
    was given, is discarded - the record is retried, never filled in by default;
  * when both reviewers exclude with different codes, the earlier code in protocol order wins;
  * QC rechecks and human overrides (overrides.csv: id,d,code,why[,by]) are applied last
    and logged on the record;
  * the QC recheck is required: once screening is complete, a reproducible sample of the records
    BOTH reviewers excluded (qc.random_exclusion_sample, all of them when fewer) plus the
    near-miss exclusions go to the senior reviewer, and those records count as pending until
    it has decided them (a joint exclusion never reaches the adjudicator);
  * --pilot-labels compares the AI decisions with the review team's own labels for the pilot
    records (same columns as overrides.csv) and writes pilot_check.json; build_workflow.py
    refuses to screen outside the recorded pilot (including --jobs pending) until every labelled
    record has been compared and the AI missed no record the team advanced.

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


def load_overrides(path, codes, valid_ids, strict=False):
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
                if strict:
                    raise SystemExit(f"pilot label has an unknown/out-of-scope ID: {rid}")
                print(f"override skipped (unknown id): {rid}")
                continue
            if not srlib.valid_decision(dec, codes):
                if strict:
                    raise SystemExit(f"pilot label has an invalid label/code: {rid}")
                print(f"override skipped (label/code mismatch): {rid} {dec['d']}/{dec['code']}")
                continue
            ov[rid] = dict(dec, by=(row.get("by") or "").strip() or "HUMAN")
    return ov


def current_results(a, work, context):
    """Results without provenance fail closed; explicit legacy imports are separately audited."""
    audit_path = os.path.join(work, "decision_audit.json")
    audit = srlib.load_json(audit_path, []) or []
    seen = {srlib.digest(row) for row in audit}
    accepted = []
    rejected = 0
    for src, label, decs in iter_results(a.sources):
        plain, separator, identity = (label or "").partition("@")
        valid = identity == context["context_id"] if separator else bool(a.legacy_import_reason.strip())
        row = {"source": os.path.abspath(src), "label": label, "decisions": decs,
               "accepted_context": context["context_id"] if valid else None}
        if not separator and valid:
            row["legacy_import_reason"] = a.legacy_import_reason.strip()
        key = srlib.digest(row)
        if key not in seen:
            audit.append(row)
            seen.add(key)
        if valid:
            accepted.append((src, plain, decs))
        else:
            rejected += 1
    srlib.save_json(audit_path, audit, indent=1)
    if rejected:
        print(f"results rejected (different review/revision or missing identity): {rejected}")
    return accepted


def settle(final, rid, rec, auto, ov):
    """Store the final decision: a human override wins over the automatic one (which is kept)."""
    if rid in ov:
        if auto:
            rec["pre_override"] = auto
        rec["final"] = ov[rid]
        rec["human_override"] = True
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
    context = srlib.current_context(work, "ta", cfg)
    for src, label, decs in current_results(a, work, context):
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
    srlib.save_json(os.path.join(work, "decisions_meta.json"), {"context_id": context["context_id"]}, indent=1)
    srlib.save_json(os.path.join(work, "agreement.json"), agree, indent=1)
    screening_done = not pend_screen and not pend_adj
    qc_cands = make_qc_candidates(work, cfg, manifest, final, set(got["QC"]) | set(ov), screening_done)
    pend_qc = [{"b": c["b"], "ids": c["ids"]} for c in (qc_cands or []) if c["ids"]]
    srlib.save_json(os.path.join(work, "pending.json"),
                    {"screen": pend_screen, "adj": pend_adj, "qc": pend_qc}, indent=1)
    if a.pilot_labels:
        pilot_check(a.pilot_labels, final, codes, {i for m in manifest for i in m["ids"]}, work, ov)

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
    n_pq = sum(len(p["ids"]) for p in pend_qc)
    if n_ps or n_pa:
        print(f"PENDING: {n_ps} records still need a reviewer decision in {len(pend_screen)} batches; "
              f"{n_pa} conflicts need adjudication -> build_workflow.py ta --jobs pending")
        print("the required QC recheck of joint exclusions is drawn once screening is complete")
    elif n_pq:
        print(f"PENDING QC: {n_pq} exclusions (joint-exclusion sample and near-miss) await the required senior "
              "recheck -> build_workflow.py ta --jobs recheck")
    else:
        print("complete: every record has a final decision and the required QC recheck is done")


def make_qc_candidates(work, cfg, manifest, final, skip, screening_done=True):
    """Select exclusions for a senior second look and pack them into their own batch files.

    Near-miss: matches at least one pattern in every qc.near_miss group. Random (required): a
    reproducible sample of the records BOTH reviewers excluded (decided by "A+B"), drawn once per
    review after screening is complete (never redrawn on later merges), so the sample covers
    every batch.
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
    if k and screening_done and "random" not in why.values():
        rest = [r for r in excluded if r not in why and r not in skip and final[r]["final"].get("by") == "A+B"]
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


def pilot_check(path, final, codes, valid_ids, work, ov):
    """Compare the AI decisions with the review team's labels for the pilot records.

    The costly error is a wrong exclusion, so the check lists every record the team advanced
    (include or unclear) that the AI excluded. The AI side is the automatic decision, before any
    human override.
    """
    scope = set(srlib.load_json(os.path.join(work, "pilot_batches.json"), []) or [])
    pilot_ids = {rid for m in srlib.load_json(os.path.join(work, "manifest.json"))
                 if m["batch"] in scope for rid in m["ids"]}
    labels = load_overrides(path, codes, valid_ids & pilot_ids, strict=True)
    rows, missed, extra, not_screened = [], [], 0, []
    for rid, h in sorted(labels.items()):
        rec = final.get(rid)
        ai = rec.get("pre_override") if rec and "pre_override" in rec else None
        if ai is None and rec and rid not in ov:
            ai = rec["final"]
        if not ai:
            not_screened.append(rid)
            continue
        h_adv, ai_adv = h["d"] in srlib.ADVANCE, ai["d"] in srlib.ADVANCE
        rows.append((h_adv, ai_adv))
        if h_adv and not ai_adv:
            missed.append({"id": rid, "human": f"{h['d']}/{h['code']}", "ai": f"{ai['d']}/{ai['code']}",
                           "ai_why": ai.get("why", ""), "ai_by": ai.get("by", "")})
        elif ai_adv and not h_adv:
            extra += 1
    human_adv = sum(1 for h, _ in rows if h)
    both = sum(1 for h, x in rows if h and x)
    context = srlib.load_json(os.path.join(work, "review_state.json"))["ta"]
    out = {"labels_file": os.path.abspath(path), "labelled": len(labels), "compared": len(rows),
           "context_id": context["context_id"],
           "context": {k: v for k, v in context.items() if k != "protocol_path"},
           "labels_hash": srlib.digest(srlib.read_text(path)),
           "not_screened_by_ai": not_screened, "human_advanced": human_adv,
           "ai_advanced": sum(1 for _, x in rows if x), "both_advanced": both,
           "sensitivity": round(both / human_adv, 3) if human_adv else None,
           "missed_advances": missed, "extra_advances": extra, "agreement": srlib.agreement(rows)}
    srlib.save_json(os.path.join(work, "pilot_check.json"), out, indent=1)
    print(f"pilot vs human labels: {len(rows)} compared, team advanced {human_adv}, AI advanced "
          f"{out['ai_advanced']}, AI missed {len(missed)}, AI advanced {extra} the team excluded"
          + (f", {len(not_screened)} labelled records without an AI decision yet" if not_screened else ""))
    for m in missed:
        print(f"  MISSED {m['id']}: team {m['human']}, AI {m['ai']} ({m['ai_by']}) - {m['ai_why']}")
    if missed:
        print("STOP: fix the protocol wording for these records, amend, and re-run the pilot before the full run")
    elif not_screened:
        print("STOP: finish the AI decisions for all labelled records and merge again with --pilot-labels")
    elif not rows:
        print("no pilot record has both an AI decision and a team label yet")
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
        w = csv.writer(f, quoting=csv.QUOTE_ALL)
        w.writerow(["id", "qc_decision", "code", "why", "year", "title", "doi", "pmid"])
        w.writerows([srlib.spreadsheet_text(v) for v in row] for row in rows)
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
    context = srlib.current_context(work, "ft", cfg)
    for src, label, decs in current_results(a, work, context):
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
    srlib.save_json(os.path.join(work, "ft_decisions_meta.json"), {"context_id": context["context_id"]}, indent=1)
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
    ta_ids, qc_ids, problems, uncovered, stale = srlib.fulltext_status(work, cfg)
    if ta_ids or problems or stale:
        print("INCOMPLETE: title/abstract screening or required title/abstract QC is still pending; "
              "full-text counts and methods remain provisional until those items are decided")
    elif not pend_items and not pend_adj:
        print("complete: every report has a final decision")


def main():
    srlib.utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--work", required=True)
    ap.add_argument("--from", dest="sources", nargs="+", required=True)
    ap.add_argument("--config")
    ap.add_argument("--protocol", help="activate the confirmed protocol/config revision before merging")
    ap.add_argument("--legacy-import-reason", default="",
                    help="explicit, audited import of old result files that have no review/revision identity")
    ap.add_argument("--stage", choices=["ta", "ft"], default="ta")
    ap.add_argument("--overrides")
    ap.add_argument("--pilot-labels", help="the team's own labels for pilot records (id,d,code,why,by)")
    ap.add_argument("--audit", action="store_true", help="report QC-recheck decisions of an audited set")
    a = ap.parse_args()
    cfg = srlib.load_config(a.config)
    work = os.path.abspath(a.work)
    if a.protocol:
        srlib.activate_context(work, a.stage, a.protocol, cfg)
    if not srlib.current_context(work, a.stage, cfg):
        raise SystemExit("no current review/protocol/config identity: regenerate the workflow or pass --protocol "
                         "with the confirmed protocol before merging")
    if a.stage == "ta":
        merge_ta(a, cfg, work)
    else:
        merge_ft(a, cfg, work)


if __name__ == "__main__":
    main()
