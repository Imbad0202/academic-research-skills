#!/usr/bin/env python3
"""Fail-closed integrity audit of a bakeoff run, BEFORE it is scored.

`score_bakeoff.py` trusts the record it is handed: it does not recompute the
fixture hash, check that the job set is complete, reject duplicates, or look at
exit codes. A hand-written JSONL can therefore make it print ALL FIVE PASS.
This script is the missing gate. Run it first; score only on PASS.

Usage:
    python3 audit_run.py --run <run.jsonl> [--fixture probe_set_v2.json]
                         [--models gpt-5.6-sol,gpt-5.5] [--repeats 3]

Exit 0 = every check passed. Exit 1 = at least one FAIL (do not score).
"""
import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(run_path):
    meta, calls = {}, []
    with open(run_path) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if "_meta" in rec:
                meta = rec["_meta"]
            else:
                calls.append(rec)
    return meta, calls


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--fixture", default=str(HERE / "probe_set_v2.json"))
    ap.add_argument("--models", default="gpt-5.6-sol,gpt-5.5")
    ap.add_argument("--repeats", type=int, default=3)
    a = ap.parse_args()

    meta, calls = load(a.run)
    blob = open(a.fixture, "rb").read()
    fx_sha = hashlib.sha256(blob).hexdigest()
    refs = json.loads(blob)["references"]
    models = a.models.split(",")

    expected = {(m, r["ref_id"], rep)
                for m in models for r in refs
                for rep in range(1, a.repeats + 1)}
    actual = {(c.get("model"), c.get("ref_id"), c.get("repeat")) for c in calls}
    threads = [c.get("thread_id") for c in calls if c.get("thread_id")]

    checks = []

    def check(name, ok, detail):
        checks.append((name, bool(ok), detail))

    check("fixture sha256 recomputed and matches _meta",
          meta.get("fixture_sha256") == fx_sha,
          f"run={meta.get('fixture_sha256', '(absent)')} recomputed={fx_sha}")
    check("call count equals the full job set",
          len(calls) == len(expected),
          f"{len(calls)} calls, expected {len(expected)}")
    check("job set is complete (no missing cells)",
          not (expected - actual),
          f"{len(expected - actual)} missing, e.g. {sorted(expected - actual)[:3]}")
    check("no cells outside the declared job set",
          not (actual - expected),
          f"{len(actual - expected)} unexpected, e.g. {sorted(actual - expected)[:3]}")
    check("no duplicate (model, ref, repeat) rows",
          len(calls) == len(actual),
          f"{len(calls) - len(actual)} duplicate row(s)")
    check("every call exited 0",
          all(c.get("exit") == 0 for c in calls),
          f"{sum(1 for c in calls if c.get('exit') != 0)} non-zero/timeout")
    check("every call carries a thread_id",
          len(threads) == len(calls),
          f"{len(calls) - len(threads)} without thread_id")
    check("thread_ids are unique (one Codex thread per call)",
          len(set(threads)) == len(threads),
          f"{len(threads) - len(set(threads))} repeated thread_id(s)")
    check("raw adapter output retained for every call",
          all(c.get("stdout_raw") for c in calls),
          f"{sum(1 for c in calls if not c.get('stdout_raw'))} without stdout_raw")
    check("every call is timestamped",
          all(c.get("started_at") and c.get("finished_at") for c in calls),
          f"{sum(1 for c in calls if not c.get('started_at'))} without timestamps")
    check("auth mode recorded as a ChatGPT subscription",
          meta.get("auth_mode") == "chatgpt",
          f"auth_mode={meta.get('auth_mode')!r} "
          f"api_key_present={meta.get('auth_api_key_present')!r}")
    check("adapter identified by hash",
          bool(meta.get("adapter_sha256")),
          f"adapter_sha256={meta.get('adapter_sha256')}")
    check("verdicts are drawn from the closed set",
          all(c.get("verdict") in
              {"VERIFIED", "MISMATCH", "NOT_FOUND", "NOT_SEARCHED", None}
              for c in calls),
          str(Counter(c.get("verdict") for c in calls).most_common()))

    # Everything above checks the record against itself. These two re-derive the
    # adapter's decisions from the Codex events the run retained, which is the
    # only way an auditor checks the grounding guard rather than the harness.
    # Requires ARS_CODEX_EMIT_EVENTS=1 at run time.
    with_events = [c for c in calls if c.get("events")]
    check("Codex event stream retained (enables the two checks below)",
          len(with_events) == len(calls),
          f"{len(with_events)}/{len(calls)} calls carry events"
          + ("" if with_events else "; re-run with ARS_CODEX_EMIT_EVENTS=1"))

    if with_events:
        bad_ground, bad_thread = [], []
        for c in with_events:
            evs = c["events"]
            searched = any(
                isinstance(e, dict) and e.get("type") == "item.completed"
                and isinstance(e.get("item"), dict)
                and e["item"].get("type") == "web_search"
                for e in evs)
            if searched != (c.get("searched") is True):
                bad_thread_id = f"{c['ref_id']}/{c['model']}/r{c['repeat']}"
                bad_ground.append(bad_thread_id)
            tids = [e.get("thread_id") for e in evs
                    if isinstance(e, dict) and e.get("type") == "thread.started"]
            if not tids or tids[0] != c.get("thread_id"):
                bad_thread.append(f"{c['ref_id']}/{c['model']}/r{c['repeat']}")
        check("grounding flag re-derived from the retained events",
              not bad_ground,
              f"{len(bad_ground)} mismatch(es)"
              + (f", e.g. {bad_ground[:3]}" if bad_ground else ""))
        check("thread_id matches the events' own thread.started",
              not bad_thread,
              f"{len(bad_thread)} mismatch(es)"
              + (f", e.g. {bad_thread[:3]}" if bad_thread else ""))

    width = max(len(n) for n, _, _ in checks)
    print(f"run     : {a.run}")
    print(f"fixture : {a.fixture}\n")
    for name, ok, detail in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name:<{width}}  {detail}")

    failed = [n for n, ok, _ in checks if not ok]
    print()
    if failed:
        print(f"AUDIT FAILED — {len(failed)} check(s). Do NOT score this run.")
        return 1
    print("AUDIT PASSED — the record is internally complete; safe to score.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
