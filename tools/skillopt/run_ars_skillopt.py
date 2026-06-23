#!/usr/bin/env python3
"""Launcher: run SkillOpt training/eval on an ARS gold set without forking SkillOpt.

SkillOpt resolves its environment adapter from a module-global registry
(``scripts.train._ENV_REGISTRY``) that ``_register_builtins()`` only ever *adds*
to — so we can register the ARS adapter into it before handing control to
SkillOpt's own ``main()``. No edit to the installed SkillOpt package is required.

Usage (from the ARS repo root, with SkillOpt installed: ``pip install skillopt``):

    PYTHONPATH=. python tools/skillopt/run_ars_skillopt.py \\
        --config tools/skillopt/configs/rq_framing_patterns.yaml

    # evaluate an already-optimized skill instead of training:
    PYTHONPATH=. python tools/skillopt/run_ars_skillopt.py --eval \\
        --config tools/skillopt/configs/rq_framing_patterns.yaml

Any flags after ``--config`` are SkillOpt's own (see ``skillopt-train --help``).
This launcher only injects the registry entry; it changes nothing else.
"""
from __future__ import annotations

import sys

ENV_KEY = "ars_rq_framing_patterns"


def _register() -> None:
    """Insert the ARS adapter into SkillOpt's env registry (idempotent)."""
    try:
        from scripts import train as skillopt_train
    except ImportError as exc:  # pragma: no cover - depends on external install
        raise SystemExit(
            "SkillOpt is not importable. Install it first: `pip install skillopt` "
            "(or clone microsoft/SkillOpt and `pip install -e .`). "
            f"Underlying import error: {exc}"
        )
    from tools.skillopt.ars_adapter import ARSRQFramingAdapter

    skillopt_train._ENV_REGISTRY[ENV_KEY] = ARSRQFramingAdapter


def main() -> None:
    eval_mode = "--eval" in sys.argv
    if eval_mode:
        sys.argv.remove("--eval")
    _register()
    if eval_mode:
        from scripts import eval_only
        eval_only.main()
    else:
        from scripts import train
        train.main()


if __name__ == "__main__":
    main()
