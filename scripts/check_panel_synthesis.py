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


# --- markdown grammar (pinned; fenced code stripped; anchored full lines) -------

_FENCE_RE = re.compile(r"^\s*```")
_H2_RE = re.compile(r"^## (.+?)\s*$")
_H3_RE = re.compile(r"^### (.+?)\s*$")
_ROLE_RE = re.compile(r"^contract_role: (?P<role>[a-z_]+)\s*$")
_SCORE_LINE_RE = re.compile(r"^score: (?P<score>block|warn|pass)\s*$")
_FIRED_LINE_RE = re.compile(r"^fired: (?P<fired>true|false)\s*$")
_DECISION_LINE_RE = re.compile(r"^(?P<action>editorial_decision=[a-z_]+)\s*$")
_DIM_H3_RE = re.compile(r"^(?P<dim>D\d+): (?P<name>.+)$")

REQUIRED_REPORT_SECTIONS = (
    "Dimension Scores", "Failure Condition Checks", "Editorial Decision")


def strip_fences(text):
    out, in_fence = [], False
    for line in text.split("\n"):
        if _FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append(line)
    return out


def _split_by(lines, heading_re):
    sections, dupes, current = {}, set(), None
    for line in lines:
        m = heading_re.match(line)
        if m:
            title = m.group(1)
            if title in sections:
                dupes.add(title)
            current = sections.setdefault(title, [])
            continue
        if current is not None:
            current.append(line)
    return sections, dupes


def split_sections(lines):
    return _split_by(lines, _H2_RE)


def split_subsections(lines):
    return _split_by(lines, _H3_RE)


def _exactly_one(lines, rx, what, path, group):
    hits = [m.group(group) for line in lines if (m := rx.match(line))]
    if len(hits) != 1:
        raise ReportError(
            f"[REPORT-PARSE: {path}: expected exactly one {what} line, "
            f"found {len(hits)}]")
    return hits[0]


@dataclass
class ReviewerReport:
    path: str
    role: str
    scores: dict
    fired: dict
    decision: str


def parse_report(path, text, contract):
    lines = strip_fences(text)
    sections, dupes = split_sections(lines)
    for req in REQUIRED_REPORT_SECTIONS:
        if req in dupes:
            raise ReportError(
                f"[REPORT-PARSE: {path}: duplicated required section '## {req}']")
        if req not in sections:
            raise ReportError(
                f"[REPORT-PARSE: {path}: missing required section '## {req}']")
    role = _exactly_one(lines, _ROLE_RE, "contract_role", path, "role")

    dim_ids = [d["id"] for d in contract["acceptance_dimensions"]]
    subs, sub_dupes = split_subsections(sections["Dimension Scores"])
    if sub_dupes:
        raise ReportError(
            f"[REPORT-PARSE: {path}: duplicated Dimension Scores subsection(s) "
            f"{sorted(sub_dupes)}]")
    scores = {}
    for title, sublines in subs.items():
        m = _DIM_H3_RE.match(title)
        if not m or m.group("dim") not in dim_ids:
            raise ReportError(
                f"[REPORT-PARSE: {path}: unknown Dimension Scores subsection "
                f"'### {title}']")
        scores[m.group("dim")] = _exactly_one(
            sublines, _SCORE_LINE_RE, f"score ({m.group('dim')})", path, "score")
    missing = [d for d in dim_ids if d not in scores]
    if missing:
        raise ReportError(
            f"[REPORT-PARSE: {path}: missing Dimension Scores for {missing}]")

    cond_ids = [c["condition_id"] for c in contract["failure_conditions"]]
    fsubs, fdupes = split_subsections(sections["Failure Condition Checks"])
    if fdupes:
        raise ReportError(
            f"[REPORT-PARSE: {path}: duplicated Failure Condition Checks "
            f"subsection(s) {sorted(fdupes)}]")
    fired = {}
    for title, sublines in fsubs.items():
        if title not in cond_ids:
            raise ReportError(
                f"[REPORT-PARSE: {path}: unknown Failure Condition Checks "
                f"subsection '### {title}']")
        fired[title] = _exactly_one(
            sublines, _FIRED_LINE_RE, f"fired ({title})", path, "fired") == "true"
    missing = [c for c in cond_ids if c not in fired]
    if missing:
        raise ReportError(
            f"[REPORT-PARSE: {path}: missing Failure Condition Checks for {missing}]")

    decision = _exactly_one(lines, _DECISION_LINE_RE, "decision", path, "action")
    if decision not in ACTION_ENUM:
        raise ReportError(
            f"[REPORT-PARSE: {path}: unknown decision action token '{decision}']")
    in_section = [m.group("action") for line in sections["Editorial Decision"]
                  if (m := _DECISION_LINE_RE.match(line))]
    if len(in_section) != 1:
        raise ReportError(
            f"[REPORT-PARSE: {path}: decision line must sit inside "
            f"'## Editorial Decision']")
    return ReviewerReport(path=path, role=role, scores=scores,
                          fired=fired, decision=decision)


# --- synthesis output parser ----------------------------------------------------

_FIREDLIST_RE = re.compile(r"^fired_conditions: \[(?P<body>[^\]]*)\]\s*$")


def parse_synthesis(path, text, contract):
    lines = strip_fences(text)
    bodies = [m.group("body") for line in lines
              if (m := _FIREDLIST_RE.match(line))]
    if len(bodies) != 1:
        raise SynthesisError(
            f"[SYNTHESIS-PARSE: {path}: expected exactly one fired_conditions "
            f"line, found {len(bodies)}]")
    body = bodies[0].strip()
    fired = [t.strip() for t in body.split(",") if t.strip()] if body else []
    cond_ids = {c["condition_id"] for c in contract["failure_conditions"]}
    unknown = [f for f in fired if f not in cond_ids]
    if unknown:
        raise SynthesisError(
            f"[SYNTHESIS-PARSE: {path}: unknown condition id(s) {unknown}]")
    if len(fired) != len(set(fired)):
        raise SynthesisError(
            f"[SYNTHESIS-PARSE: {path}: duplicate condition id in fired list]")
    decisions = [m.group("action") for line in lines
                 if (m := _DECISION_LINE_RE.match(line))]
    if len(decisions) != 1:
        raise SynthesisError(
            f"[SYNTHESIS-PARSE: {path}: expected exactly one decision line, "
            f"found {len(decisions)}]")
    if decisions[0] not in ACTION_ENUM:
        raise SynthesisError(
            f"[SYNTHESIS-PARSE: {path}: unknown decision action token "
            f"'{decisions[0]}']")
    return fired, decisions[0]


# --- contract loading + hard eligibility ----------------------------------------

def _read_text(path):
    try:
        return Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise ContractError(f"[IO-ERROR: {path}: {exc}]") from exc


def load_contract(path):
    try:
        contract = json.loads(_read_text(path))
    except json.JSONDecodeError as exc:
        raise ContractError(f"[CONTRACT-INVALID: {path}: {exc}]") from exc
    problems = check_sprint_contract.validate(contract)
    problems += check_sprint_contract.check_structural_invariants(contract)
    if problems:
        raise ContractError(
            f"[CONTRACT-INVALID: {path}: " + "; ".join(problems) + "]")
    mode = contract.get("mode")
    if mode not in ROLE_SETS:
        raise ContractError(
            f"[CONTRACT-INELIGIBLE: mode '{mode}' has no published panel "
            f"mapping (protocol §7); supported: {sorted(ROLE_SETS)}]")
    expected_size = check_sprint_contract.EXPECTED_PANEL_SIZE[mode]
    if contract.get("panel_size") != expected_size:
        raise ContractError(
            f"[CONTRACT-INELIGIBLE: panel_size={contract.get('panel_size')} "
            f"inconsistent with mode={mode}; expected {expected_size}]")
    accept_grade_action(contract["failure_conditions"])
    dims_by_priority, dim_ids = {}, set()
    for d in contract["acceptance_dimensions"]:
        dims_by_priority.setdefault(d["priority"], []).append(d["id"])
        dim_ids.add(d["id"])
    predicates = {
        c["condition_id"]: parse_expression(
            c["expression"], dims_by_priority, dim_ids, c["condition_id"])
        for c in contract["failure_conditions"]
    }
    return contract, predicates


# --- Layer 1: per-reviewer self-consistency --------------------------------------

def layer1_check(report, contract, predicates, warnings):
    diags = []
    for cond in contract["failure_conditions"]:
        cid = cond["condition_id"]
        recomputed = predicates[cid](report.scores)
        declared = report.fired[cid]
        if recomputed != declared:
            diags.append(
                f"[REVIEWER-SELF-INCONSISTENT: reviewer={report.path}, "
                f"condition={cid}, declared={str(declared).lower()}, "
                f"recomputed={str(recomputed).lower()}]")
    declared_fired = {cid for cid, f in report.fired.items() if f}
    expected = resolve_decision(contract["failure_conditions"], declared_fired)
    if expected != report.decision:
        diags.append(
            f"[REVIEWER-SELF-INCONSISTENT: reviewer={report.path}, "
            f"decision_declared={report.decision}, "
            f"decision_recomputed={expected}]")
    return diags


# --- Layer 2: panel synthesis recomputation --------------------------------------

def layer2_check(reports, contract, predicates, declared_fired,
                 declared_decision, warnings):
    recomputed_fired = []
    for cond in contract["failure_conditions"]:
        cid = cond["condition_id"]
        per_reviewer = [predicates[cid](r.scores) for r in reports]
        if quantifier_fires(cond["cross_reviewer_quantifier"],
                            per_reviewer, warnings):
            recomputed_fired.append(cid)
    recomputed_decision = resolve_decision(
        contract["failure_conditions"], set(recomputed_fired))
    if (sorted(recomputed_fired) != sorted(declared_fired)
            or recomputed_decision != declared_decision):
        return [
            f"[PANEL-SYNTHESIS-MISMATCH: recomputed_fired={recomputed_fired}, "
            f"declared_fired={list(declared_fired)}, "
            f"recomputed={recomputed_decision}, stated={declared_decision}]"]
    return []


# --- CLI --------------------------------------------------------------------------

def _parse_args(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--report", required=True, action="append",
                        type=Path, dest="reports")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--synthesis", type=Path)
    group.add_argument("--layer1-only", action="store_true")
    return parser.parse_args(argv)


def main(argv=None):
    args = _parse_args(argv)
    warnings, infra, reviewer_diags, synthesis_diags = [], [], [], []

    try:
        contract, predicates = load_contract(args.contract)
    except ContractError as exc:
        print(exc)
        return EXIT_CONTRACT

    panel_size = contract["panel_size"]
    role_set = ROLE_SETS[contract["mode"]]

    # cardinality: paths + content identity (both modes)
    resolved = {p: p.resolve() for p in args.reports}
    if len(set(resolved.values())) != len(args.reports):
        infra.append("[PANEL-CARDINALITY: duplicate report paths]")
    if not args.layer1_only and len(args.reports) != panel_size:
        infra.append(f"[PANEL-CARDINALITY: got={len(args.reports)}, "
                     f"panel_size={panel_size}]")
    if args.layer1_only and not (1 <= len(args.reports) <= panel_size):
        infra.append(f"[PANEL-CARDINALITY: layer1-only accepts 1..{panel_size} "
                     f"reports, got={len(args.reports)}]")

    texts, hashes, seen_resolved = {}, set(), set()
    for p in args.reports:
        try:
            texts[p] = _read_text(p)
        except ContractError as exc:
            infra.append(str(exc))
            continue
        resolved_p = resolved[p]
        if resolved_p in seen_resolved:
            # Already processed under a prior --report occurrence of this same
            # resolved path; the duplicate-path diagnostic above already
            # covers it, so skip re-hashing to avoid a second, redundant
            # byte-identical diagnostic for the identical file.
            continue
        seen_resolved.add(resolved_p)
        digest = hashlib.sha256(texts[p].encode("utf-8")).hexdigest()
        if digest in hashes:
            infra.append(f"[PANEL-CARDINALITY: byte-identical report contents "
                         f"({p})]")
        hashes.add(digest)

    reports, parse_failed = [], False
    for p in args.reports:
        if p not in texts:
            parse_failed = True
            continue
        try:
            reports.append(parse_report(str(p), texts[p], contract))
        except ReportError as exc:
            reviewer_diags.append(str(exc))
            parse_failed = True

    roles = [r.role for r in reports]
    if not parse_failed:
        if args.layer1_only:
            bad = [x for x in roles if x not in role_set]
            if bad or len(set(roles)) != len(roles):
                infra.append(f"[PANEL-CARDINALITY: roles {roles} invalid for "
                             f"mode {contract['mode']}]")
        elif set(roles) != role_set or len(set(roles)) != len(roles):
            infra.append(f"[PANEL-CARDINALITY: roles {sorted(roles)} != "
                         f"required {sorted(role_set)}]")

    for r in reports:
        reviewer_diags.extend(layer1_check(r, contract, predicates, warnings))

    if not args.layer1_only:
        if parse_failed or infra:
            synthesis_diags.append(
                "[SUPPRESSED: panel recomputation skipped — upstream "
                "reviewer/cardinality failure]")
        else:
            try:
                declared_fired, declared_decision = parse_synthesis(
                    str(args.synthesis), _read_text(args.synthesis), contract)
            except ContractError as exc:      # IO on synthesis file
                infra.append(str(exc))
            except SynthesisError as exc:
                synthesis_diags.append(str(exc))
            else:
                synthesis_diags.extend(layer2_check(
                    reports, contract, predicates, declared_fired,
                    declared_decision, warnings))

    for line in warnings + infra + reviewer_diags + synthesis_diags:
        print(line)
    if infra:
        return EXIT_CONTRACT
    if reviewer_diags:
        return EXIT_REVIEWER
    if any(not d.startswith("[SUPPRESSED") for d in synthesis_diags):
        return EXIT_SYNTHESIS
    print("PANEL-SYNTHESIS: PASS" if not args.layer1_only
          else "LAYER1-ONLY: PASS")
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
