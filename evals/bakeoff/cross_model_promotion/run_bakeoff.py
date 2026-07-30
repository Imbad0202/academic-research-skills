#!/usr/bin/env python3
"""#518 Promotion Bakeoff runner: paired baseline/candidate over the pinned probe set.

Calls the SHIPPED adapter (scripts/cross_model_codex_verify.sh) so the bakeoff
measures the path ARS actually ships, not a reimplementation.

Measure-4 note: the adapter emits only {verdict,sources,searched}. A guard misfire
(0 or >=2 verdict tokens, or VERIFIED with no URL) collapses to verdict=NOT_SEARCHED
while searched stays true. So (searched=true AND verdict=NOT_SEARCHED) is recorded as
a CANDIDATE misfire needing adjudication -- it is not automatically a misfire, since a
model may legitimately emit the NOT_SEARCHED token itself.
"""
import argparse
import hashlib
import json
import os
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = str(HERE.parents[2])
ADAPTER = os.path.join(REPO, "scripts/cross_model_codex_verify.sh")

PROMPT_TMPL = """Verify this academic reference. Check: Does it exist? Are the author
names, year, title, journal, and DOI correct? Search the web to
confirm — do not answer from memory.

Respond with exactly one verdict:
- VERIFIED  — found online; include at least one source URL or DOI you found
- MISMATCH  — found, but a field is wrong (state which); include the source
- NOT_FOUND — searched, no matching record exists
- NOT_SEARCHED — you could not actually search the web for this reference

Reference: {ref}"""


def one_call(ref, model, rep, timeout):
    prompt = PROMPT_TMPL.format(ref=ref["reference_text"])
    env = dict(os.environ, ARS_CROSS_MODEL=model)
    env.pop("OPENAI_API_KEY", None)
    t0 = time.time()
    try:
        p = subprocess.run(["bash", ADAPTER, prompt], cwd=REPO, env=env,
                           capture_output=True, text=True, timeout=timeout)
        dt = round(time.time() - t0, 1)
        try:
            out = json.loads(p.stdout.strip() or "{}")
        except json.JSONDecodeError:
            out = {}
        rec = {
            "ref_id": ref["ref_id"], "leg": ref["leg"], "label": ref["label"],
            "model": model, "repeat": rep, "latency_s": dt, "exit": p.returncode,
            "verdict": out.get("verdict"), "sources": out.get("sources", []),
            "searched": out.get("searched"),
            "stdout_raw": p.stdout.strip()[:400] if not out else None,
            "stderr_tail": p.stderr.strip()[-200:] or None,
        }
    except subprocess.TimeoutExpired:
        rec = {"ref_id": ref["ref_id"], "leg": ref["leg"], "label": ref["label"],
               "model": model, "repeat": rep, "latency_s": round(time.time() - t0, 1),
               "exit": "TIMEOUT", "verdict": None, "sources": [], "searched": None,
               "stdout_raw": None, "stderr_tail": "timeout"}
    rec["candidate_guard_misfire"] = bool(rec.get("searched") is True and
                                          rec.get("verdict") == "NOT_SEARCHED")
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixture", default=str(HERE / "probe_set_v2.json"))
    ap.add_argument("--models", default="gpt-5.6-sol,gpt-5.5")
    ap.add_argument("--repeats", type=int, default=3)
    ap.add_argument("--only", default="", help="comma-separated ref_ids; empty = all")
    ap.add_argument("--concurrency", type=int, default=4)
    ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    blob = open(a.fixture, "rb").read()
    sha = hashlib.sha256(blob).hexdigest()
    fx = json.loads(blob)
    refs = fx["references"]
    if a.only:
        keep = set(a.only.split(","))
        refs = [r for r in refs if r["ref_id"] in keep]
    models = a.models.split(",")

    jobs = [(r, m, i) for r in refs for m in models for i in range(1, a.repeats + 1)]
    print(f"fixture sha256={sha}")
    print(f"refs={len(refs)} models={models} repeats={a.repeats} -> {len(jobs)} calls "
          f"(concurrency {a.concurrency})", flush=True)

    done = []
    with open(a.out, "w") as fh:
        fh.write(json.dumps({"_meta": {"fixture_sha256": sha, "models": models,
                                       "repeats": a.repeats, "n_calls": len(jobs)}}) + "\n")
        with ThreadPoolExecutor(max_workers=a.concurrency) as ex:
            futs = {ex.submit(one_call, r, m, i, a.timeout): (r, m, i) for r, m, i in jobs}
            for n, f in enumerate(as_completed(futs), 1):
                rec = f.result()
                done.append(rec)
                fh.write(json.dumps(rec) + "\n")
                fh.flush()
                flag = " !MISFIRE?" if rec["candidate_guard_misfire"] else ""
                print(f"[{n:3d}/{len(jobs)}] {rec['ref_id']:20s} {rec['model']:12s} "
                      f"r{rec['repeat']} {str(rec['verdict']):13s} searched={rec['searched']} "
                      f"{rec['latency_s']}s{flag}", flush=True)

    print("\n=== per-model summary ===")
    for m in models:
        sub = [d for d in done if d["model"] == m]
        ok = sum(1 for d in sub if d["searched"] is True)
        mis = sum(1 for d in sub if d["candidate_guard_misfire"])
        lat = sorted(d["latency_s"] for d in sub)
        p95 = lat[int(len(lat) * 0.95)] if lat else 0
        print(f"  {m:12s} calls={len(sub):3d} grounded={ok:3d} candidate_misfires={mis} "
              f"p95_latency={p95}s")


if __name__ == "__main__":
    main()
