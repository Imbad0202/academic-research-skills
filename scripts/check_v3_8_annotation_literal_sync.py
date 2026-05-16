"""ARS v3.8 §3.6 + §5 — annotation literal sync lint.

The 8-row finalizer matrix in `scripts/claim_audit_finalizer.py` emits five
HIGH-WARN annotation classes that the formatter's terminal hard gate
(`academic-paper/agents/formatter_agent.md`) MUST refuse on. The annotation
literals appear in two places:

1. `scripts/claim_audit_finalizer.py` as `ANNOTATION_HIGH_WARN_*` constants
   (the finalizer write side — `apply_finalizer` returns these on
   gate_refuse=True rows).
2. `academic-paper/agents/formatter_agent.md` REFUSE rules 6-10 (the
   formatter read side — terminal hard gate scans the draft for these
   literals before emitting LaTeX/DOCX/PDF).

A literal drift between the two sides silently breaks the gate: if the
finalizer is renamed from `[HIGH-WARN-CLAIM-NOT-SUPPORTED]` to
`[HIGH-WARN-CLAIM-UNSUPPORTED]` and the formatter rule 6 is not updated,
the formatter will pass output that the orchestrator marked HIGH-WARN.

This lint extracts the five `ANNOTATION_HIGH_WARN_*` constant values from
the finalizer module and asserts each one's bracket prefix appears in the
formatter agent prompt's REFUSE list. The check uses bracket-prefix
matching (NOT byte-equivalence on the full annotation) because the
NEGATIVE-CONSTRAINT-VIOLATION + CONSTRAINT-VIOLATION-UNCITED literals
carry a runtime `({violated_constraint_id})` interpolation that the
formatter prose cannot duplicate verbatim — the prefix up to but not
including the interpolation hole is the contract.

Spec: docs/design/2026-05-15-issue-103-claim-alignment-audit-spec.md §5.

Lint exit codes:
  0 = pass (all five HIGH-WARN annotation prefixes present in formatter).
  1 = at least one annotation prefix missing from formatter REFUSE list.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FINALIZER_MODULE = REPO_ROOT / "scripts" / "claim_audit_finalizer.py"
FORMATTER_AGENT = REPO_ROOT / "academic-paper" / "agents" / "formatter_agent.md"


def _annotation_prefix(annotation_literal: str) -> str:
    """Return the matchable prefix of the annotation literal.

    Annotation literals follow three shapes:
      - Closed plain:        `[HIGH-WARN-CLAIM-NOT-SUPPORTED]`
      - Interpolated suffix: `[HIGH-WARN-NEGATIVE-CONSTRAINT-VIOLATION ({violated_constraint_id})]`
      - Em-dash suffix:      `[HIGH-WARN-CLAIM-AUDIT-ANCHORLESS — v3.7.3 R-L3-1-A VIOLATION REACHED AUDIT]`

    The prefix-match contract cuts at the first occurrence of any of:
      `{` (runtime interpolation hole — the variable part the formatter
      prose cannot duplicate verbatim);
      ` (` (the space-paren opening a parenthesized variable carrier);
      ` —` (the em-dash opening a contextual suffix that the formatter
      prose may abbreviate);
      `]` (closing bracket of a plain literal).

    Whichever appears first wins. Closed plain literals reduce to
    byte-equivalent matching; interpolated and em-dash literals match
    the formatter prose's prefix form (which omits the variable suffix).
    """
    cut = len(annotation_literal)
    for terminator in ("{", " (", " —", "]"):
        idx = annotation_literal.find(terminator)
        if idx != -1 and idx < cut:
            cut = idx
    return annotation_literal[:cut].rstrip()


def _extract_finalizer_high_warn_constants(source: str) -> dict[str, str]:
    """Parse the finalizer module source for `ANNOTATION_HIGH_WARN_*` constants.

    Uses runtime exec to evaluate the string literals as defined — the
    constants are plain string assignments, so AST-walking + literal_eval
    would also work. exec keeps the lint simple and matches the runtime
    truth (the same string Python sees at import time).

    Filters to `ANNOTATION_HIGH_WARN_*` names only. The five canonical
    HIGH-WARN classes are:
      - ANNOTATION_HIGH_WARN_CLAIM_NOT_SUPPORTED
      - ANNOTATION_HIGH_WARN_NEGATIVE_CONSTRAINT_VIOLATION
      - ANNOTATION_HIGH_WARN_FABRICATED_REFERENCE
      - ANNOTATION_HIGH_WARN_ANCHORLESS
      - ANNOTATION_HIGH_WARN_CONSTRAINT_VIOLATION_UNCITED
    """
    ns: dict[str, object] = {}
    # The module's import of `INV14_FAULT_CLASS_TAGS` from
    # `_claim_audit_constants` is part of module init. Use the module
    # import path so the load succeeds end-to-end.
    sys.path.insert(0, str(REPO_ROOT))
    try:
        from scripts import claim_audit_finalizer  # noqa: F401  (import for side effect: load constants)

        for name in dir(claim_audit_finalizer):
            if name.startswith("ANNOTATION_HIGH_WARN_"):
                ns[name] = getattr(claim_audit_finalizer, name)
    finally:
        sys.path.remove(str(REPO_ROOT))
    return {name: value for name, value in ns.items() if isinstance(value, str)}


def main() -> int:
    if not FINALIZER_MODULE.exists():
        print(f"[v3.8 annotation-sync] FAIL: missing {FINALIZER_MODULE}")
        return 1
    if not FORMATTER_AGENT.exists():
        print(f"[v3.8 annotation-sync] FAIL: missing {FORMATTER_AGENT}")
        return 1

    constants = _extract_finalizer_high_warn_constants(FINALIZER_MODULE.read_text())
    if len(constants) != 5:
        print(
            f"[v3.8 annotation-sync] FAIL: expected exactly 5 ANNOTATION_HIGH_WARN_* "
            f"constants in claim_audit_finalizer.py; found {len(constants)}: "
            f"{sorted(constants)}"
        )
        return 1

    formatter_text = FORMATTER_AGENT.read_text()
    missing: list[tuple[str, str]] = []
    for name, literal in sorted(constants.items()):
        prefix = _annotation_prefix(literal)
        if prefix not in formatter_text:
            missing.append((name, prefix))

    if missing:
        print(
            f"[v3.8 annotation-sync] FAIL: {len(missing)} HIGH-WARN annotation "
            f"literal(s) missing from formatter REFUSE list (spec §5 + §1 "
            f"deliverable 5):"
        )
        for name, prefix in missing:
            print(f"  - {name}: prefix {prefix!r} not found in {FORMATTER_AGENT.name}")
        return 1

    print(
        f"[v3.8 annotation-sync] PASS: all {len(constants)} HIGH-WARN annotation "
        f"prefixes present in formatter_agent.md REFUSE list"
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
