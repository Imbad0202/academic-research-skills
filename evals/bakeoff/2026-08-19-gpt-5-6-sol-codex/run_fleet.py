#!/usr/bin/env python3
"""#787 bakeoff fleet runner — probe_set x {gpt-5.5, gpt-5.6-sol} x 3 repeats
through scripts/cross_model_codex_verify.sh (live subscription calls; consumes
ChatGPT-subscription capacity). Resumable: existing receipt files are skipped.
Output dir: ./results (override with ARS_BAKEOFF_OUT). Score a reproduced
fleet with: python3 score_run.py <that output dir> — the scorer applies the
same completeness and identity-binding gates to runner output as to the
committed gate-run JSONLs."""
import json, os, subprocess, sys, time

from receipt_contract import validate_receipt
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
TODAY = time.strftime("%Y-%m-%d")

CARRIED_FAILURES: list[str] = []
jobs = []
for model, short in MODELS.items():
    for ref in refs:
        for r in range(1, REPEATS + 1):
            out = OUT / model / f"{ref['id']}-r{r}.json"
            if out.exists():
                # Same-day comparison is a gate requirement: a resumed cell
                # from an earlier date poisons the fleet (#788 round-7 P2).
                cell = json.loads(out.read_text())
                cell_day = str(cell.get("ts", ""))[:10]
                if cell_day != TODAY:
                    raise SystemExit(
                        f"STALE CELL: {out} is from {cell_day or 'unknown'}, not {TODAY}. "
                        "Archive the output dir and run a fresh same-day fleet."
                    )
                # A recorded failed trial is PART of the fleet's outcome —
                # deleting and retrying it would let a flaky model be re-
                # rolled until every retained row succeeds, biasing measures
                # 1/4/5 (#788 round-11 P1). Resume fills only MISSING cells;
                # a failure is carried forward and forces a nonzero exit, so
                # the only path past it is rerunning the ENTIRE fleet in a
                # fresh output directory.
                cell_bad = cell.get("receipt") is None or cell.get("error")
                if not cell_bad:
                    # Resumed cells face the same full contract as fresh ones
                    # (#788 round-15 P2).
                    try:
                        validate_receipt(cell["receipt"], f"resumed {out.name}")
                    except SystemExit as bad:
                        raise SystemExit(f"RESUMED CELL INVALID: {bad}. Archive the output dir and rerun.")
                if cell_bad:
                    CARRIED_FAILURES.append(f"{model}/{out.name}: {cell.get('error')}")
                    print(f"[carried-failure] {out.name} ({cell.get('error')})", flush=True)
                # A carried cell must come from the same pinned-effort
                # configuration; mixing pre-pin or differently-configured
                # cells into a fleet is not comparable (#788 round-13 P2).
                elif cell.get("reasoning_effort") != "provider-default (env unset)":
                    raise SystemExit(
                        f"EFFORT UNPINNED CELL: {out} has reasoning_effort="
                        f"{cell.get('reasoning_effort')!r}. Archive the output dir and rerun."
                    )
                continue
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
    # Reasoning effort is PINNED to the provider default: an inherited
    # ARS_CROSS_MODEL_REASONING_EFFORT would silently change both models'
    # calls without being recorded (#788 round-12 P2). Every row records the
    # effective setting.
    env.pop("ARS_CROSS_MODEL_REASONING_EFFORT", None)
    # Fleet-private temp root: the transport's ars-codex-citation-* dirs land
    # here, so the timeout sweep can never touch another invocation's dirs.
    env["TMPDIR"] = str(FLEET_TMP)
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
                # Parsed-but-malformed output must be a recorded failure, not
                # a silent ERR row the exit code ignores (#788 round-14 P2).
                try:
                    validate_receipt(receipt, f"{model} {ref['id']} r{r}")
                except SystemExit as bad:
                    err = f"RECEIPT_INVALID: {bad}"
                    receipt = None
        else:
            err = f"EXIT {proc.returncode}: {proc.stderr[:300]}"
    except subprocess.TimeoutExpired:
        # The backstop kill reaps only the verifier; its detached codex
        # app-server exits on stdin EOF, but the verifier's finally-block
        # cleanup (the ephemeral CODEX_HOME holding the copied auth.json)
        # never runs. Sweep any adapter temp dirs left behind (#788
        # round-8 P2).
        wall = time.monotonic() - t0
        receipt, err = None, "CALL_TIMEOUT"
        TIMEOUT_OCCURRED.append(out.name)
    row = {"model": model, "ref_id": ref["id"], "repeat": r, "wall_seconds": round(wall, 2),
           "receipt": receipt, "error": err, "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
           "reasoning_effort": "provider-default (env unset)"}
    tmp = out.with_suffix(".tmp")
    tmp.write_text(json.dumps(row, ensure_ascii=False, indent=1))
    tmp.rename(out)
    v = receipt.get("verdict") if receipt else "ERR"
    s = receipt.get("searched") if receipt else "-"
    return f"{model} {ref['id']} r{r}: {v} searched={s} {wall:.0f}s" + (f" [{err}]" if err else "")

def _sweep_orphan_tempdirs() -> None:
    """Remove adapter temp dirs left by outer-timeout kills.

    Runs ONLY after the executor has drained (no live worker owns a dir any
    more, #788 round-9 P2) and sweeps ONLY the fleet-private temp root, so it
    can never touch another invocation's dirs (#788 round-12 P2). Every
    removal is logged.
    """
    import shutil
    root = FLEET_TMP
    for d in root.glob("ars-codex-citation-*"):
        try:
            if d.is_dir() and d.stat().st_mtime >= FLEET_START - 5:
                shutil.rmtree(d, ignore_errors=True)
                print(f"[sweep] removed orphan temp dir {d}", flush=True)
        except OSError:
            pass


import tempfile as _tempfile
FLEET_TMP = Path(_tempfile.mkdtemp(prefix="ars-bakeoff-fleet-"))
FLEET_START = time.time()
TIMEOUT_OCCURRED: list[str] = []
done = 0
failures = 0
try:
    with ThreadPoolExecutor(max_workers=CONCURRENCY) as ex:
        futs = [ex.submit(run_one, j) for j in jobs]
        for f in as_completed(futs):
            done += 1
            try:
                line = f.result()
                print(f"[{done}/{len(jobs)}]", line, flush=True)
                if any(tag in line for tag in ("[CALL_TIMEOUT]", "[EXIT ", "[RECEIPT_PARSE", "[RECEIPT_INVALID")):
                    failures += 1
            except Exception as e:
                failures += 1
                print(f"[{done}/{len(jobs)}] WORKER-ERROR {e!r}", flush=True)
finally:
    # The fleet-private root is swept on EVERY outcome once workers have
    # drained — a verifier killed by a signal/OOM leaves its ephemeral
    # CODEX_HOME (with the copied auth.json) behind without raising
    # TimeoutExpired, so timeout-only sweeping is not enough (#788
    # round-13 P2). The root is private to this fleet, so removing it
    # whole is safe here.
    import shutil as _shutil
    _sweep_orphan_tempdirs()
    _shutil.rmtree(FLEET_TMP, ignore_errors=True)
failures += len(CARRIED_FAILURES)
if failures:
    # An incomplete or error-bearing fleet must never look like success to
    # automation (#788 round-8 P2); the scorer's completeness gate is the
    # second line of defense, not the only one.
    raise SystemExit(f"FLEET INCOMPLETE: {failures} of {len(jobs)} calls failed")
print("ALL DONE", flush=True)
