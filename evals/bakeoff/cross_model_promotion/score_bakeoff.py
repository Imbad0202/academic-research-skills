#!/usr/bin/env python3
"""Score the #518 Promotion Bakeoff against the five non-inferiority thresholds.

Spec: shared/cross_model_verification.md -- Promotion Bakeoff.
  - per-reference verdict = verdict returned by >=2 of 3 repeats
  - 1-1-1 split = indeterminate, scored CONSERVATIVELY AGAINST the model:
      a miss for recall (measure 2), a false disagreement (measure 3)
  - measure 1 (grounded-search completion) is per CALL, not per reference
"""
import argparse
import json
from collections import Counter, defaultdict

FLAG = {"NOT_FOUND", "MISMATCH"}


def majority(verdicts):
    """>=2 of 3 wins; otherwise indeterminate."""
    c = Counter(v for v in verdicts if v is not None)
    if not c:
        return "INDETERMINATE"
    top, n = c.most_common(1)[0]
    return top if n >= 2 else "INDETERMINATE"


def pct(a, b):
    return round(100.0 * a / b, 1) if b else 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--baseline", default="gpt-5.5")
    ap.add_argument("--candidate", default="gpt-5.6-sol")
    ap.add_argument("--json-out", default=None)
    a = ap.parse_args()

    calls, meta = [], {}
    for line in open(a.run):
        d = json.loads(line)
        if "_meta" in d:
            meta = d["_meta"]
            continue
        calls.append(d)

    by = defaultdict(list)          # (model, ref_id) -> [verdict...]
    info = {}                       # ref_id -> (leg, label)
    for c in calls:
        by[(c["model"], c["ref_id"])].append(c["verdict"])
        info[c["ref_id"]] = (c["leg"], c["label"])

    report = {"fixture_sha256": meta.get("fixture_sha256"), "n_calls": len(calls),
              "models": {}}

    for model in (a.baseline, a.candidate):
        sub = [c for c in calls if c["model"] == model]
        # --- measure 1: grounded-search completion, per call ---
        grounded = sum(1 for c in sub if c["searched"] is True)
        m1 = pct(grounded, len(sub))
        # --- measure 4: guard misfire candidates ---
        misfires = [c for c in sub if c.get("candidate_guard_misfire")]
        # --- measure 5: p95 latency ---
        lat = sorted(c["latency_s"] for c in sub if isinstance(c["latency_s"], (int, float)))
        p95 = lat[min(int(len(lat) * 0.95), len(lat) - 1)] if lat else 0.0

        # --- per-reference majority verdicts ---
        verdicts = {}
        for rid, (leg, label) in info.items():
            verdicts[rid] = majority(by[(model, rid)])

        fabs = [r for r, (leg, lab) in info.items() if lab == "fabricated"]
        reals = [r for r, (leg, lab) in info.items() if lab == "real"]

        # measure 2: recall on fabrications (indeterminate = miss)
        caught = [r for r in fabs if verdicts[r] in FLAG]
        m2 = pct(len(caught), len(fabs))
        # measure 3: false disagreement on reals (indeterminate = false disagreement)
        fd = [r for r in reals if verdicts[r] in FLAG or verdicts[r] == "INDETERMINATE"]
        m3 = pct(len(fd), len(reals))

        per_leg = defaultdict(lambda: Counter())
        for rid, (leg, lab) in info.items():
            per_leg[leg][verdicts[rid]] += 1

        report["models"][model] = {
            "m1_grounded_pct": m1, "grounded_calls": grounded, "total_calls": len(sub),
            "m2_recall_pct": m2, "fabrications_caught": len(caught), "fabrications": len(fabs),
            "m2_missed": [r for r in fabs if r not in caught],
            "m3_false_disagreement_pct": m3, "false_disagreements": fd, "reals": len(reals),
            "m4_candidate_misfires": len(misfires),
            "m4_misfire_refs": [f"{c['ref_id']}/r{c['repeat']}" for c in misfires],
            "m5_p95_latency_s": p95,
            "per_leg": {k: dict(v) for k, v in per_leg.items()},
            "verdicts": verdicts,
        }

    b = report["models"][a.baseline]
    c = report["models"][a.candidate]
    checks = [
        ("1 grounded-search completion >= baseline-5pp",
         c["m1_grounded_pct"] >= b["m1_grounded_pct"] - 5,
         f"{c['m1_grounded_pct']}% vs baseline {b['m1_grounded_pct']}%"),
        ("2 citation-mismatch recall >= baseline-5pp AND >= 80% absolute",
         (c["m2_recall_pct"] >= b["m2_recall_pct"] - 5) and (c["m2_recall_pct"] >= 80.0),
         f"{c['m2_recall_pct']}% vs baseline {b['m2_recall_pct']}% (absolute floor 80%)"),
        ("3 false-disagreement rate <= baseline+5pp",
         c["m3_false_disagreement_pct"] <= b["m3_false_disagreement_pct"] + 5,
         f"{c['m3_false_disagreement_pct']}% vs baseline {b['m3_false_disagreement_pct']}%"),
        ("4 jq-guard shape stability == zero misfires (HARD)",
         c["m4_candidate_misfires"] == 0,
         f"{c['m4_candidate_misfires']} candidate misfire(s)"),
        ("5 p95 latency <= 2x baseline",
         c["m5_p95_latency_s"] <= 2 * b["m5_p95_latency_s"],
         f"{c['m5_p95_latency_s']}s vs 2x baseline {round(2 * b['m5_p95_latency_s'], 1)}s"),
    ]
    report["checks"] = [{"name": n, "pass": bool(p), "detail": d} for n, p, d in checks]
    report["all_pass"] = all(p for _, p, _ in checks)
    report["outcome"] = ("ALL FIVE PASS -> eligible for provisional->validated"
                         if report["all_pass"] else "FAIL -> stays provisional; results recorded")

    print(f"fixture sha256 : {report['fixture_sha256']}")
    print(f"calls          : {report['n_calls']}\n")
    for m in (a.baseline, a.candidate):
        r = report["models"][m]
        tag = "BASELINE " if m == a.baseline else "CANDIDATE"
        print(f"[{tag}] {m}")
        print(f"   m1 grounded          : {r['m1_grounded_pct']}%  ({r['grounded_calls']}/{r['total_calls']} calls)")
        print(f"   m2 recall on fabs    : {r['m2_recall_pct']}%  ({r['fabrications_caught']}/{r['fabrications']})"
              + (f"  missed={r['m2_missed']}" if r["m2_missed"] else ""))
        print(f"   m3 false disagree    : {r['m3_false_disagreement_pct']}%  ({len(r['false_disagreements'])}/{r['reals']})"
              + (f"  {r['false_disagreements']}" if r["false_disagreements"] else ""))
        print(f"   m4 cand. misfires    : {r['m4_candidate_misfires']}"
              + (f"  {r['m4_misfire_refs']}" if r["m4_misfire_refs"] else ""))
        print(f"   m5 p95 latency       : {r['m5_p95_latency_s']}s")
        print(f"   per-leg              : {json.dumps(r['per_leg'])}\n")
    print("=== THRESHOLDS (all five must pass) ===")
    for ch in report["checks"]:
        print(f"  [{'PASS' if ch['pass'] else 'FAIL'}] {ch['name']}\n         {ch['detail']}")
    print(f"\nOUTCOME: {report['outcome']}")

    if a.json_out:
        json.dump(report, open(a.json_out, "w"), indent=2)
        print(f"\nwrote {a.json_out}")


if __name__ == "__main__":
    main()
