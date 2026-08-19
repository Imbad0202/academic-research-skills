#!/usr/bin/env python3
"""Deterministic scorer for the 2026-08-19 codex-transport Promotion Bakeoff (#787).

Replays the five § Promotion Bakeoff measures from the committed artifacts in
this directory alone: `probe_set.json` + `run4_receipts_<model>.jsonl`.
Offline; stdlib-only. Run: python3 score_run.py
"""
import json
import statistics
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODELS = ["gpt-5.5", "gpt-5.6-sol"]
REPEATS = 3
DISAGREE = {"NOT_FOUND", "MISMATCH"}
SHAPE_GUARD_CODES = {
    "EVENT_STREAM_INVALID", "FINAL_OUTPUT_INVALID", "TURN_NOT_COMPLETED",
    "FORBIDDEN_TOOL_EVENT", "MULTIPLE_FINAL_ANSWERS", "UNBOUND_SOURCE",
}

refs = {r["id"]: r for r in json.loads((HERE / "probe_set.json").read_text())["references"]}
fab_ids = [i for i, r in refs.items() if r["label"] == "fabricated"]
real_ids = [i for i, r in refs.items() if r["label"] == "real"]

summary = {}
for model in MODELS:
    rows = [json.loads(line) for line in (HERE / f"run4_receipts_{model}.jsonl").read_text().splitlines() if line]
    n_calls = len(rows)
    grounded = sum(1 for r in rows if r["receipt"] and r["receipt"].get("searched") is True)
    latencies = sorted(r["wall_seconds"] for r in rows)
    p95 = latencies[int(0.95 * len(latencies)) - 1]
    misfires = [
        {"ref": r["ref_id"], "repeat": r["repeat"], "reason": (r["receipt"] or {}).get("reason_code") or r["error"]}
        for r in rows
        if (r["receipt"] and r["receipt"].get("reason_code") in SHAPE_GUARD_CODES) or (r["receipt"] is None)
    ]

    by_ref: dict[str, list[str]] = {}
    for r in rows:
        if r["receipt"]:
            by_ref.setdefault(r["ref_id"], []).append(r["receipt"]["verdict"])

    def majority(rid: str) -> str:
        c = Counter(by_ref.get(rid, []))
        if c and c.most_common(1)[0][1] >= 2:
            return c.most_common(1)[0][0]
        return "INDETERMINATE"

    fab_verdicts = {i: majority(i) for i in fab_ids}
    real_verdicts = {i: majority(i) for i in real_ids}
    recall = sum(1 for v in fab_verdicts.values() if v in DISAGREE) / len(fab_ids)
    false_dis = sum(1 for v in real_verdicts.values() if v in DISAGREE or v == "INDETERMINATE") / len(real_ids)

    summary[model] = {
        "calls_scored": n_calls,
        "m1_grounded_completion": round(grounded / n_calls, 4),
        "m2_fabrication_recall": round(recall, 4),
        "m3_false_disagreement": round(false_dis, 4),
        "m4_shape_guard_misfires": misfires,
        "m5_p95_latency_s": p95,
        "median_latency_s": statistics.median(latencies),
        "fab_verdicts": fab_verdicts,
    }

b, c = summary["gpt-5.5"], summary["gpt-5.6-sol"]
gate = {
    "1_grounded_completion (cand >= base - 5pp)": c["m1_grounded_completion"] >= b["m1_grounded_completion"] - 0.05,
    "2_recall (cand >= base - 5pp AND >= 0.80)": c["m2_fabrication_recall"] >= b["m2_fabrication_recall"] - 0.05 and c["m2_fabrication_recall"] >= 0.80,
    "3_false_disagreement (cand <= base + 5pp)": c["m3_false_disagreement"] <= b["m3_false_disagreement"] + 0.05,
    "4_zero_shape_guard_misfires (cand)": len(c["m4_shape_guard_misfires"]) == 0,
    "5_p95_latency (cand <= 2x base)": c["m5_p95_latency_s"] <= 2 * b["m5_p95_latency_s"],
}
print(json.dumps({"models": summary, "gate": gate, "all_pass": all(gate.values())}, ensure_ascii=False, indent=1))
