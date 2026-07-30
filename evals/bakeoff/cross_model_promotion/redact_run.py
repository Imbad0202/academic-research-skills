#!/usr/bin/env python3
"""Redact local-filesystem content out of a bakeoff run before publishing it.

Why this exists: the Codex transport runs `-s read-only`, which prevents writes
but not command execution. During the 2026-07-30 run the verifier shelled out and
read files from the operator's machine, and those reads landed in the retained
event stream as `command_execution` items carrying full file contents. That is
not publishable, and it is also not evidence about citation verification.

What is removed: every `command_execution` item's `aggregated_output` (the file
contents), and its `command` string (which carries absolute local paths). The
item itself is KEPT, with its id/status/exit_code, so the record still shows that
the verifier executed commands and how many. Deleting the items outright would
hide the finding.

What is preserved, because `audit_run.py` recomputes the grounding decision from
it: `thread.started` (thread_id), `web_search` items (including the query),
`agent_message` items (the verdict text), `turn.*`, and `error` items.

Usage:
    python3 redact_run.py --in <run.jsonl> --out <redacted.jsonl>
    python3 redact_run.py --in <run.jsonl> --check     # report only, no write
"""
import argparse
import json
import sys

REDACTED = "[REDACTED: local command output, see redact_run.py]"


def redact_event(ev):
    """Return (event, n_fields_redacted)."""
    if not isinstance(ev, dict):
        return ev, 0
    item = ev.get("item")
    if not isinstance(item, dict) or item.get("type") != "command_execution":
        return ev, 0
    n = 0
    if item.get("aggregated_output"):
        item["aggregated_output"] = REDACTED
        n += 1
    if item.get("command"):
        item["command"] = REDACTED
        n += 1
    return ev, n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="src", required=True)
    ap.add_argument("--out", dest="dst")
    ap.add_argument("--check", action="store_true",
                    help="report what would be redacted; write nothing")
    a = ap.parse_args()
    if not a.check and not a.dst:
        ap.error("--out is required unless --check is given")

    out_lines, n_fields, n_events, calls = [], 0, 0, set()
    for line in open(a.src):
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        if "_meta" not in rec:
            for ev in (rec.get("events") or []):
                ev, k = redact_event(ev)
                if k:
                    n_fields += k
                    n_events += 1
                    calls.add((rec.get("ref_id"), rec.get("model"),
                               rec.get("repeat")))
        out_lines.append(json.dumps(rec, ensure_ascii=False))

    print(f"command_execution events redacted : {n_events}")
    print(f"fields cleared                    : {n_fields}")
    print(f"calls affected                    : {len(calls)}")

    if a.check:
        return 0

    with open(a.dst, "w") as fh:
        fh.write("\n".join(out_lines) + "\n")
    print(f"wrote {a.dst}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
