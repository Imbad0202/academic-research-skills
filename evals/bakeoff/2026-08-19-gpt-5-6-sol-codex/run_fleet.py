#!/usr/bin/env python3
"""#787 bakeoff fleet runner — probe_set x {gpt-5.5, gpt-5.6-sol} x 3 repeats
through scripts/cross_model_codex_verify.sh (live subscription calls; consumes
ChatGPT-subscription capacity). Resumable: existing receipt files are skipped.
Output dir: ./results (override with ARS_BAKEOFF_OUT). Score a reproduced
fleet with: python3 score_run.py <that output dir> — the scorer applies the
same completeness and identity-binding gates to runner output as to the
committed gate-run JSONLs."""
import json, os, signal, subprocess, sys, time

from receipt_contract import validate_receipt, validate_row, verify_probe_bytes
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

# Digest preflight BEFORE any paid call: a locally modified fixture must
# fail here, not after 180 subscription calls (#788 round-24 P2).
refs = json.loads(verify_probe_bytes(PROBE.read_bytes()).decode("utf-8"))["references"]
TODAY = time.strftime("%Y-%m-%d")

# Exclusive fleet lock: two concurrent runners on one output dir would both
# see cells as missing, duplicate paid calls, and race on the same .tmp and
# destination paths (#788 round-25 P2). flock is advisory but both writers
# are this script.
# POSIX-only, stated up front (#788 round-29 P1): the #630 transport's
# process-group containment (start_new_session + os.killpg in
# _stop_process) is POSIX-only, so a native-Windows fleet would consume
# paid calls and fail every cell during cleanup. Windows users reproduce
# under WSL or another POSIX environment.
if os.name != "posix":
    raise SystemExit(
        "UNSUPPORTED PLATFORM: the bakeoff fleet requires a POSIX environment "
        "(the #630 transport's process-group cleanup is POSIX-only). On "
        "Windows, run under WSL."
    )

OUT.mkdir(parents=True, exist_ok=True)
_LOCK_FH = open(OUT / ".fleet.lock", "a+")
try:
    import fcntl
    fcntl.flock(_LOCK_FH, fcntl.LOCK_EX | fcntl.LOCK_NB)
except OSError:
    raise SystemExit(f"FLEET LOCKED: another run_fleet.py holds {OUT / '.fleet.lock'}")

CARRIED_FAILURES: list[str] = []
jobs = []
# Counterbalanced scheduling (#788 round-32 P1): the two models' calls for
# each (reference, repeat) cell are adjacent in the queue, with the pair
# order alternating deterministically by (reference index + repeat) parity —
# model identity is decorrelated from execution time, so provider load or
# search-state drift during the fleet cannot masquerade as a model effect.
_MODEL_ITEMS = list(MODELS.items())
_cell_plan = []
for ref_idx, ref in enumerate(refs):
    for r in range(1, REPEATS + 1):
        pair = _MODEL_ITEMS if (ref_idx + r) % 2 == 0 else list(reversed(_MODEL_ITEMS))
        for model, short in pair:
            _cell_plan.append((model, short, ref, r))

for model, short, ref, r in _cell_plan:
    out = OUT / model / f"{ref['id']}-r{r}.json"
    if out.exists():
        # Same-day comparison is a gate requirement: a resumed cell
        # from an earlier date poisons the fleet (#788 round-7 P2).
        cell = json.loads(out.read_text(encoding="utf-8"))
        cell_day = str(cell.get("ts", ""))[:10]
        if cell_day != TODAY:
            raise SystemExit(
                f"STALE CELL: {out} is from {cell_day or 'unknown'}, not {TODAY}. "
                "Archive the output dir and run a fresh same-day fleet."
            )
        # EVERY resumed cell — failed ones included — faces the
        # scorer-equivalent row validation and the effort check, so a
        # copied/misnamed/corrupted cell of either kind fails before
        # any further quota is spent (#788 round-27 P2).
        try:
            validate_row(cell, model, ref)
        except SystemExit as bad:
            raise SystemExit(f"RESUMED CELL INVALID: {bad}. Archive the output dir and rerun.")
        if cell.get("reasoning_effort") != "provider-default (env unset)":
            raise SystemExit(
                f"EFFORT UNPINNED CELL: {out} has reasoning_effort="
                f"{cell.get('reasoning_effort')!r}. Archive the output dir and rerun."
            )
        # A recorded failed trial is PART of the fleet's outcome —
        # deleting and retrying it would let a flaky model be re-
        # rolled until every retained row succeeds, biasing measures
        # 1/4/5 (#788 round-11 P1). Resume fills only MISSING cells;
        # a failure is carried forward and forces a nonzero exit, so
        # the only path past it is rerunning the ENTIRE fleet in a
        # fresh output directory.
        if cell.get("receipt") is None or cell.get("error"):
            CARRIED_FAILURES.append(f"{model}/{out.name}: {cell.get('error')}")
            print(f"[carried-failure] {out.name} ({cell.get('error')})", flush=True)
        continue
    jobs.append((model, short, ref, r, out))

# Unexpected files in the output dir make the fleet unscoreable (the scorer
# loads every <model>/*.json); refuse BEFORE spending quota (#788 round-30 P2).
expected_names = {f"{ref['id']}-r{r}.json" for ref in refs for r in range(1, REPEATS + 1)}
for model in MODELS:
    mdir = OUT / model
    if mdir.is_dir():
        stray = sorted(p.name for p in mdir.glob("*.json") if p.name not in expected_names)
        if stray:
            raise SystemExit(f"UNEXPECTED FILES in {mdir}: {stray[:5]} — archive the output dir and rerun.")
        # An orphaned atomic-write temp file means a prior run died between
        # write and rename: the paid call happened but left no destination
        # cell, and silently rescheduling it would re-roll a completed trial
        # (#788 round-31 P2). Refuse and let the operator inspect.
        orphans = sorted(p.name for p in mdir.glob("*.tmp"))
        if orphans:
            raise SystemExit(f"ORPHANED TEMP CELLS in {mdir}: {orphans[:5]} — inspect/archive before resuming.")

# Pair-completeness on resume (#788 round-33 P1): an interruption that left
# only one model's cell for a (reference, repeat) pair would make the resumed
# counterpart run far from its partner, silently reintroducing the
# model-vs-time confound the counterbalanced schedule eliminates. Every pair
# must be wholly present or wholly missing.
_present = {
    (model, ref["id"], r)
    for model in MODELS
    for ref in refs
    for r in range(1, REPEATS + 1)
    if (OUT / model / f"{ref['id']}-r{r}.json").exists()
}
_model_names = list(MODELS)
for ref in refs:
    for r in range(1, REPEATS + 1):
        sides = sum(1 for m in _model_names if (m, ref["id"], r) in _present)
        if sides == 1:
            raise SystemExit(
                f"HALF-COMPLETE PAIR: {ref['id']} r{r} has only one model's cell — "
                "resuming would break counterbalanced pairing. Archive the output dir and rerun."
            )

print(f"total pending calls: {len(jobs)}", flush=True)

def run_one(job):
    model, short, ref, r, out = job
    if STOP is not None and STOP.is_set():
        return f"{model} {ref['id']} r{r}: SKIPPED (termination requested) [CANCELLED]"
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
        # The transport is invoked via sys.executable, not the .sh wrapper
        # (no shebang dependence), and text I/O is pinned to strict UTF-8 so
        # multilingual receipts survive non-UTF-8 locales (#788 round-27).
        # start_new_session detaches the verifier from the runner's
        # foreground process group: an interactive Ctrl-C then reaches only
        # the runner, in-flight verifiers finish (or hit their own deadline)
        # and their cells persist normally instead of becoming EXIT failures
        # that poison resumability (#788 round-30 P2).
        proc = subprocess.run(
            [sys.executable, str(REPO / "scripts/cross_model_codex_transport.py"), "verify"],
            input=json.dumps(request, ensure_ascii=False), capture_output=True,
            text=True, encoding="utf-8", timeout=CALL_TIMEOUT, env=env, cwd=str(REPO),
            start_new_session=True,
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
                # Parsed-but-malformed OR mis-identified output must be a
                # recorded failure: fresh cells face the same validate_row
                # identity binding as resumed cells and the scorer, so a
                # receipt with the wrong model/request_id/digest can never be
                # persisted as success (#788 rounds 14 + 31).
                candidate_row = {
                    "model": model, "ref_id": ref["id"], "repeat": r,
                    "wall_seconds": round(wall, 2), "receipt": receipt,
                    "error": None, "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                    "reasoning_effort": "provider-default (env unset)",
                }
                try:
                    validate_row(candidate_row, model, ref)
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
    tmp.write_text(json.dumps(row, ensure_ascii=False, indent=1), encoding="utf-8")
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
import threading as _threading
STOP = _threading.Event()
FLEET_TMP = Path(_tempfile.mkdtemp(prefix="ars-bakeoff-fleet-"))
FLEET_START = time.time()
TIMEOUT_OCCURRED: list[str] = []
# SIGTERM/SIGINT must unwind through the finally-block sweep below —
# Python's default SIGTERM handler would kill the process without running
# cleanup, leaving copied auth.json dirs under FLEET_TMP (#788 round-18 P2).
# In-flight verifier calls finish or hit their own deadline first; the sweep
# then runs on the drained, fleet-private root.
def _terminate(signum, frame):
    # Queued futures must not keep consuming paid quota after a termination
    # signal: STOP makes every not-yet-started job a no-op, so shutdown only
    # waits for the (at most CONCURRENCY) in-flight calls (#788 round-21 P1).
    if STOP is not None:
        STOP.set()
    raise SystemExit(128 + signum)

signal.signal(signal.SIGTERM, _terminate)
signal.signal(signal.SIGINT, _terminate)

done = 0
failures = 0
try:
    with ThreadPoolExecutor(max_workers=CONCURRENCY) as ex:
        futs = {ex.submit(run_one, j): j for j in jobs}
        for f in as_completed(futs):
            done += 1
            try:
                line = f.result()
                print(f"[{done}/{len(jobs)}]", line, flush=True)
                if any(tag in line for tag in ("[CALL_TIMEOUT]", "[EXIT ", "[RECEIPT_PARSE", "[RECEIPT_INVALID", "[CANCELLED]")):
                    failures += 1
            except Exception as e:
                failures += 1
                model, short, ref, r_, out = futs[f]
                print(f"[{done}/{len(jobs)}] WORKER-ERROR {model} {ref['id']} r{r_}: {e!r}", flush=True)
                # A worker exception after the paid call must leave a
                # persisted failed cell — otherwise the next resume treats
                # the trial as missing and silently re-rolls it (#788
                # round-21 P2).
                if not out.exists():
                    try:
                        out.parent.mkdir(parents=True, exist_ok=True)
                        out.write_text(json.dumps({
                            "model": model, "ref_id": ref["id"], "repeat": r_,
                            "wall_seconds": 0.0, "receipt": None,
                            "error": f"WORKER_EXCEPTION: {e!r}",
                            "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                            "reasoning_effort": "provider-default (env unset)",
                        }, ensure_ascii=False, indent=1))
                    except OSError:
                        pass
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
# A fresh fleet that crossed local midnight is unscoreable (the scorer's
# same-day gate will reject it); fail HERE so the quota loss is visible
# immediately, not at scoring time (#788 round-20 P2).
fleet_dates = set()
for model in MODELS:
    for p in sorted((OUT / model).glob("*.json")):
        fleet_dates.add(str(json.loads(p.read_text(encoding="utf-8")).get("ts", ""))[:10])
if len(fleet_dates) > 1:
    raise SystemExit(f"MIXED-DATE FLEET: cells span {sorted(fleet_dates)} — archive and rerun in one calendar day.")
if failures:
    # An incomplete or error-bearing fleet must never look like success to
    # automation (#788 round-8 P2); the scorer's completeness gate is the
    # second line of defense, not the only one.
    raise SystemExit(f"FLEET INCOMPLETE: {failures} of {len(jobs)} calls failed")
print("ALL DONE", flush=True)
