#!/usr/bin/env python3
"""#787 bakeoff fleet runner — probe_set x {gpt-5.5, gpt-5.6-sol} x 3 repeats
through scripts/cross_model_codex_verify.sh (live subscription calls; consumes
ChatGPT-subscription capacity). Resumable: existing receipt files are skipped.
Output dir: ./results (override with ARS_BAKEOFF_OUT)."""
import json, os, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
PROBE = HERE / "probe_set.json"
OUT = Path(os.environ.get("ARS_BAKEOFF_OUT", str(HERE / "results")))
VERIFY = REPO / "scripts/cross_model_codex_verify.sh"
MODELS = {"gpt-5.5": "bk55", "gpt-5.6-sol": "bk56"}
REPEATS = 3
CONCURRENCY = 3
# Outer backstop only: it MUST exceed the transport's own 300 s app-server
# deadline plus detection/setup/drain margin, so the transport's finally-block
# cleanup (ephemeral CODEX_HOME with the copied auth.json; process-group reap)
# always fires before this kill. An outer kill at exactly the inner deadline
# could orphan the detached codex child and leak the temp auth copy (#788
# codex round-4 P2).
CALL_TIMEOUT = 420

refs = json.loads(PROBE.read_text())["references"]
jobs = []
for model, short in MODELS.items():
    for ref in refs:
        for r in range(1, REPEATS + 1):
            out = OUT / model / f"{ref['id']}-r{r}.json"
            if not out.exists():
                jobs.append((model, short, ref, r, out))

print(f"total pending calls: {len(jobs)}", flush=True)

def run_one(job):
    model, short, ref, r, out = job
    out.parent.mkdir(parents=True, exist_ok=True)
    request = {
        "schema_version": "ars-codex-citation-request/1.0",
        "request_id": f"{short}-{ref['id']}-r{r}",
        "reference_text": ref["reference_text"],
        "citation_context": ref["citation_context"],
    }
    env = dict(os.environ)
    env["ARS_CROSS_MODEL_TRANSPORT"] = "codex"
    env["ARS_CROSS_MODEL"] = model
    t0 = time.monotonic()
    try:
        proc = subprocess.run(
            [str(VERIFY)], input=json.dumps(request), capture_output=True,
            text=True, timeout=CALL_TIMEOUT, env=env, cwd=str(REPO),
        )
        wall = time.monotonic() - t0
        receipt = None
        err = None
        if proc.returncode == 0:
            try:
                receipt = json.loads(proc.stdout)
            except Exception as e:
                err = f"RECEIPT_PARSE: {e}; stdout head: {proc.stdout[:200]}"
        else:
            err = f"EXIT {proc.returncode}: {proc.stderr[:300]}"
    except subprocess.TimeoutExpired:
        wall = time.monotonic() - t0
        receipt, err = None, "CALL_TIMEOUT"
    row = {"model": model, "ref_id": ref["id"], "repeat": r, "wall_seconds": round(wall, 2),
           "receipt": receipt, "error": err, "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
    tmp = out.with_suffix(".tmp")
    tmp.write_text(json.dumps(row, ensure_ascii=False, indent=1))
    tmp.rename(out)
    v = receipt.get("verdict") if receipt else "ERR"
    s = receipt.get("searched") if receipt else "-"
    return f"{model} {ref['id']} r{r}: {v} searched={s} {wall:.0f}s" + (f" [{err}]" if err else "")

done = 0
with ThreadPoolExecutor(max_workers=CONCURRENCY) as ex:
    futs = [ex.submit(run_one, j) for j in jobs]
    for f in as_completed(futs):
        done += 1
        try:
            print(f"[{done}/{len(jobs)}]", f.result(), flush=True)
        except Exception as e:
            print(f"[{done}/{len(jobs)}] WORKER-ERROR {e!r}", flush=True)
print("ALL DONE", flush=True)
