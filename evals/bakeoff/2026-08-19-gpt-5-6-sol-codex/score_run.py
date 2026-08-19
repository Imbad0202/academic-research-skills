#!/usr/bin/env python3
"""Deterministic scorer for the 2026-08-19 codex-transport Promotion Bakeoff (#787).

Replays the five § Promotion Bakeoff measures from `probe_set.json` plus either
the committed `run7_receipts_<model>.jsonl` files (default) or a fleet-runner
output directory (`python3 score_run.py <results_dir>`, i.e. the runner's
`results/` or `$ARS_BAKEOFF_OUT`, holding `<model>/<ref>-r<k>.json` cells).
Every scored row must pass an identity binding — outer model/ref/repeat,
`receipt.model`, `receipt.request_id`, and a recomputed `request_digest`
against the probe set — so a mis-associated or edited fleet cannot certify a
result. Offline; stdlib-only.
"""
import hashlib
import json
from datetime import datetime
import re
import statistics
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODEL_SHORT = {"gpt-5.5": "bk55", "gpt-5.6-sol": "bk56"}


def canonical_json(value) -> bytes:
    # Byte-identical to scripts/cross_model_codex_transport.py::canonical_json.
    return json.dumps(
        value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
MODELS = ["gpt-5.5", "gpt-5.6-sol"]
REPEATS = 3
DISAGREE = {"NOT_FOUND", "MISMATCH"}
# Measure-4 shape/protocol family — exactly the reason codes the transport
# emits for stream/output SHAPE violations (a receipt-less row counts too).
# Since the round-6 transport fix, a malformed search-results shape emits
# EVENT_STREAM_INVALID directly, so shape drift can no longer hide inside
# NO_BOUND_SEARCH_RESULTS. The behavior-family codes — MODEL_RETURNED_
# NOT_SEARCHED, NO_BOUND_SEARCH_RESULTS, NO_REFERENCE_BOUND_QUERY,
# MISSING_SOURCE_FOR_VERDICT, SOURCE_NOT_IN_SEARCH_RESULTS — are model
# behavior: they count against measures 1-3, never against measure 4.
from receipt_contract import SHAPE_GUARD_CODES, validate_row  # noqa: E402

# The scoring populations (real/fabricated labels, difficulty tiers) come
# from the probe set, which the per-receipt request_digest does NOT cover —
# the whole frozen file is pinned via the shared, line-ending-normalized
# digest check (#788 rounds 10/24).
from receipt_contract import verify_probe_bytes  # noqa: E402

probe_bytes = verify_probe_bytes((HERE / "probe_set.json").read_bytes())
refs = {r["id"]: r for r in json.loads(probe_bytes.decode("utf-8"))["references"]}
fab_ids = [i for i, r in refs.items() if r["label"] == "fabricated"]
real_ids = [i for i, r in refs.items() if r["label"] == "real"]

def p95_nearest_rank(values: list[float]) -> float:
    """Nearest-rank percentile: the ceil(0.95 * n)-th smallest observation."""
    import math
    ordered = sorted(values)
    return ordered[math.ceil(0.95 * len(ordered)) - 1]


RESULTS_DIR = Path(sys.argv[1]) if len(sys.argv) > 1 else None


def load_rows(model: str) -> list[dict]:
    if RESULTS_DIR is not None:
        return [json.loads(p.read_text(encoding="utf-8")) for p in sorted((RESULTS_DIR / model).glob("*.json"))]
    return [json.loads(line) for line in (HERE / f"run7_receipts_{model}.jsonl").read_text(encoding="utf-8").splitlines() if line]


summary = {}
fleet_days: set[str] = set()
for model in MODELS:
    rows = load_rows(model)
    for row in rows:
        ref = refs.get(row.get("ref_id"))
        if ref is None:
            raise SystemExit(f"IDENTITY: unknown ref_id {row.get('ref_id')!r} in {model} rows")
        # Shared row validation — identical to the runner's resume preflight
        # (#788 round-25 P1): contradiction, identity binding, ts, latency,
        # full receipt contract.
        validate_row(row, model, ref)
        # Reproduced fleets (results-dir mode) must be single-effort: every
        # row carries the runner's pinned-effort marker (#788 round-13 P2).
        # The committed gate-run rows predate the marker; the audit report
        # attests their unset-effort configuration.
        if RESULTS_DIR is not None and row.get("reasoning_effort") != "provider-default (env unset)":
            raise SystemExit(
                f"EFFORT UNPINNED: {model} {row.get('ref_id')} r{row.get('repeat')} "
                f"reasoning_effort={row.get('reasoning_effort')!r} — mixed- or unpinned-effort fleets are not scorable."
            )
        # ts already validated by validate_row; aggregate the calendar day
        # for the same-day gate.
        parsed_ts = datetime.strptime(str(row["ts"]), "%Y-%m-%dT%H:%M:%S%z")
        fleet_days.add(parsed_ts.strftime("%Y-%m-%d"))
    # Fleet completeness gate: exactly one row per (ref_id, repeat) across the
    # declared 30 x 3 design — a truncated, duplicated, or partial receipt
    # file must never certify a passing result.
    seen = Counter((r["ref_id"], r["repeat"]) for r in rows)
    expected = {(rid, k) for rid in refs for k in range(1, REPEATS + 1)}
    if set(seen) != expected or any(v != 1 for v in seen.values()):
        missing = sorted(expected - set(seen))[:5]
        dupes = sorted(k for k, v in seen.items() if v > 1)[:5]
        extra = sorted(set(seen) - expected)[:5]
        raise SystemExit(
            f"FLEET INCOMPLETE for {model}: rows={len(rows)} "
            f"missing={missing} duplicates={dupes} unexpected={extra}"
        )
    n_calls = len(rows)
    grounded = sum(1 for r in rows if r["receipt"] and r["receipt"].get("searched") is True)
    latencies = [r["wall_seconds"] for r in rows]
    p95 = p95_nearest_rank(latencies)
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

# Same-day paired comparison is a gate requirement: baseline and candidate
# fleets must all carry the same calendar date (#788 round-7 P2).
if len(fleet_days) != 1:
    raise SystemExit(f"MIXED-DATE FLEET: calls span {sorted(fleet_days)} — the gate requires one same-day paired run.")

b, c = summary["gpt-5.5"], summary["gpt-5.6-sol"]
gate = {
    "1_grounded_completion (cand >= base - 5pp)": c["m1_grounded_completion"] >= b["m1_grounded_completion"] - 0.05,
    "2_recall (cand >= base - 5pp AND >= 0.80)": c["m2_fabrication_recall"] >= b["m2_fabrication_recall"] - 0.05 and c["m2_fabrication_recall"] >= 0.80,
    "3_false_disagreement (cand <= base + 5pp)": c["m3_false_disagreement"] <= b["m3_false_disagreement"] + 0.05,
    # Hard-zero across ALL calls, BOTH fleets: a baseline suppressed by guard
    # misfires cannot anchor a fair comparison (the run-3 lesson).
    "4_zero_shape_guard_misfires (both fleets)": len(c["m4_shape_guard_misfires"]) == 0 and len(b["m4_shape_guard_misfires"]) == 0,
    "5_p95_latency (cand <= 2x base)": c["m5_p95_latency_s"] <= 2 * b["m5_p95_latency_s"],
}
all_pass = all(gate.values())
print(json.dumps({"models": summary, "gate": gate, "all_pass": all_pass}, ensure_ascii=False, indent=1))
if not all_pass:
    # A failed gate must be a nonzero exit — automation using this scorer as
    # a promotion gate must never read a failing candidate as success (#788
    # round-10 P2).
    raise SystemExit(2)
