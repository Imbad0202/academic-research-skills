#!/usr/bin/env python3
"""Absolute-threshold verdict for the eval harness (#184 Delta 3 / Fix 1).

Phase 1b has no ``main`` baseline, so the CI gate is an ABSOLUTE-threshold check,
not a lift comparison. This module reads a ``run_evals`` report and returns the
list of measured tasks whose aggregate metric failed its declared threshold.

Kept out of the workflow YAML (no inline heredoc) so the gate's only load-bearing
logic is unit-testable rather than asserted via brittle YAML string matching.

CLI::

    python -m scripts._eval_threshold_gate <report.json>

prints a comma-separated list of ``<task>.aggregate.<metric>`` failures (empty
line if none) to stdout.
"""
from __future__ import annotations

import json
import sys
from typing import Any


def failed_tasks(report: dict[str, Any]) -> list[str]:
    """Return ``<task>.aggregate.<metric>`` for each measured task below threshold.

    Only tasks with ``status == "measured"`` that declare a threshold (so the
    measurer set ``aggregate_metric.passed``) are gated. ``passed is False`` is
    the failure signal — a task without a threshold (``passed`` absent) is not
    gated, and a pending/skipped task is never gated.
    """
    failures: list[str] = []
    for task in report.get("per_task", []):
        if task.get("status") != "measured":
            continue
        agg = task.get("aggregate_metric") or {}
        if agg.get("passed") is False:
            failures.append(f"{task['task_name']}.aggregate.{agg.get('metric', '?')}")
    return failures


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print("usage: python -m scripts._eval_threshold_gate <report.json>",
              file=sys.stderr)
        return 2
    report = json.loads(open(args[0], encoding="utf-8").read())
    print(",".join(failed_tasks(report)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
