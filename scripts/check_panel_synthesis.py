#!/usr/bin/env python3
"""Executable sprint-contract panel checker (#510).

Recomputes both decision layers of the v3.6.2 sprint-contract reviewer
machinery from the primary artifacts and fails on mismatch:

  Layer 1 (per reviewer): own scores -> own declared fired conditions ->
      own ``## Editorial Decision``.
  Layer 2 (panel): scoring matrix -> quantifier thresholds -> precedence ->
      the synthesizer's declared fired set AND emitted decision.

This is a self-consistency gate on LLM output, not a correctness gate: it
proves the stated decisions follow from the stated scores under the
published rules (protocol §8/§8.1/§9); it does not judge the scores.

Exit codes (classified by artifact source; multi-failure precedence 2 > 3 > 1):
  0  pass
  1  synthesis-layer failure (panel mismatch OR malformed synthesis output)
  2  contract/infra failure (contract, cardinality/roles, expression, IO)
  3  reviewer-report failure (unparseable OR internally inconsistent)

Usage:
  python scripts/check_panel_synthesis.py --contract C.json \\
      --report r1.md ... --report rN.md --synthesis synth.md
  python scripts/check_panel_synthesis.py --contract C.json \\
      --report r1.md --layer1-only

Design: docs/design/2026-07-15-510-panel-synthesis-checker-design.md
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_sprint_contract  # noqa: E402  reused, never forked

EXIT_PASS = 0
EXIT_SYNTHESIS = 1
EXIT_CONTRACT = 2
EXIT_REVIEWER = 3

ACTION_ENUM = frozenset({
    "editorial_decision=accept",
    "editorial_decision=minor_revision",
    "editorial_decision=major_revision",
    "editorial_decision=reject_or_major_revision",
    "editorial_decision=reject",
})
SCORE_ORDER = {"pass": 0, "warn": 1, "block": 2}
ROLE_SETS = {
    "reviewer_full": frozenset({"eic", "methodology", "domain", "perspective", "da"}),
    "reviewer_methodology_focus": frozenset({"eic", "methodology"}),
}


class ContractError(Exception):
    """Contract/infra failure -> exit 2."""


class ReportError(Exception):
    """Reviewer-report failure -> exit 3."""


class SynthesisError(Exception):
    """Synthesis-output failure -> exit 1."""


# --- §9 expression grammar (closed vocabulary; fail-closed) --------------------

_SCORE_PART = r"'(?P<score>block|warn|pass)'"
_ATOM_RES = (
    ("any_priority", re.compile(
        r"^any (?:(?P<p1>[a-z]+) dimension"
        r"|dimension with priority=(?P<p2>[a-z]+)"
        r"|(?P<p3>[a-z]+)-priority dimension) scores " + _SCORE_PART + r"$")),
    ("count_priority", re.compile(
        r"^two or more (?:(?P<p1>[a-z]+) dimensions"
        r"|dimensions with priority=(?P<p2>[a-z]+)) score "
        + _SCORE_PART + r" or worse$")),
    ("every_priority", re.compile(
        r"^every (?P<p1>[a-z]+) dimension scores " + _SCORE_PART + r"$")),
    ("dim_literal", re.compile(r"^(?P<dim>D\d+) scores " + _SCORE_PART + r"$")),
)


def parse_expression(expression, dims_by_priority, dim_ids, condition_id):
    """Compile a §9 expression into a predicate over one reviewer's scores.

    Returns callable(scores: dict[dim_id, score_token]) -> bool.
    Raises ContractError on unrecognised syntax, an orphan dimension
    literal, or a priority scope matching zero dimensions (no vacuous truth).
    """
    atoms = []
    for part in expression.split(" AND "):
        for kind, rx in _ATOM_RES:
            m = rx.fullmatch(part)
            if m:
                break
        else:
            raise ContractError(
                f"[EXPRESSION-UNRECOGNISED: condition_id={condition_id}, "
                f"expression={expression}]")
        score = m.group("score")
        if kind == "dim_literal":
            dim = m.group("dim")
            if dim not in dim_ids:
                raise ContractError(
                    f"[EXPRESSION-SEMANTIC: condition_id={condition_id}: "
                    f"unknown dimension {dim}]")
            atoms.append(lambda scores, d=dim, s=score: scores[d] == s)
            continue
        prio = m.group("p1") or m.group("p2") or m.group("p3")
        scoped = tuple(dims_by_priority.get(prio, ()))
        if not scoped:
            raise ContractError(
                f"[EXPRESSION-SEMANTIC: condition_id={condition_id}: "
                f"priority '{prio}' matches no contract dimension]")
        if kind == "any_priority":
            atoms.append(lambda scores, ds=scoped, s=score: any(
                scores[d] == s for d in ds))
        elif kind == "count_priority":
            floor = SCORE_ORDER[score]
            atoms.append(lambda scores, ds=scoped, f=floor: sum(
                1 for d in ds if SCORE_ORDER[scores[d]] >= f) >= 2)
        else:  # every_priority
            atoms.append(lambda scores, ds=scoped, s=score: all(
                scores[d] == s for d in ds))
    return lambda scores, _atoms=tuple(atoms): all(a(scores) for a in _atoms)


# --- quantifiers + precedence (protocol §8, majority corrected per #531) --------

def quantifier_fires(quant, per_reviewer, warnings):
    n = len(per_reviewer)
    k = sum(1 for b in per_reviewer if b)
    if quant == "any":
        return k >= 1
    if quant == "all":
        return k == n
    if quant == "majority":
        if n == 1:
            warnings.append(
                "WARNING: majority quantifier with panel_size=1 never fires "
                "(protocol §8)")
            return False
        threshold = 2 if n == 2 else n // 2 + 1
        return k >= threshold
    raise ContractError(f"unknown cross_reviewer_quantifier '{quant}'")


def accept_grade_action(conditions):
    for cond in conditions:
        if cond["action"] == "editorial_decision=accept":
            return cond["action"]
    raise ContractError(
        "[CONTRACT-INELIGIBLE: no accept-grade failure_conditions entry "
        "(action=editorial_decision=accept); zero-fired fallback undefined]")


def resolve_decision(conditions, fired_ids):
    fired = [(i, c) for i, c in enumerate(conditions)
             if c["condition_id"] in fired_ids]
    if not fired:
        return accept_grade_action(conditions)
    best = max(fired, key=lambda ic: (ic[1]["severity"], -ic[0]))
    return best[1]["action"]
