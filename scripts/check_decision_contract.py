#!/usr/bin/env python3
"""Pin the four-value decision enum and its per-mode authority.

Threat model: accidental drift. Historical records and design documents are
excluded deliberately; they may truthfully mention retired grammar.

Exit 0 pass / 1 drift / 2 missing input.
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path

from _skill_lint import heading_section, norm_ws, read_or_exit2

REPO_ROOT = Path(__file__).resolve().parents[1]
ACTIONS = (
    "editorial_decision=accept",
    "editorial_decision=minor_revision",
    "editorial_decision=major_revision",
    "editorial_decision=reject",
)
VALUES = ("Accept", "Minor Revision", "Major Revision", "Reject")
QUALITY = "academic-paper-reviewer/references/quality_rubrics.md"
RE_REVIEW_PROTOCOL = "academic-paper-reviewer/references/re_review_mode_protocol.md"
# #576 Spec B: the re-review protocol's §6 decision derivation carries
# ITEM-PROPORTION quantifiers that share numerals (50/80) with the retired
# 0-100 rubric scale but are a different decision system — verdict counts
# over roadmap items, normatively defined in the #576 spec and recomputed by
# scripts/check_re_review_synthesis.py. EXACTLY these literals are sanctioned;
# they are masked out before the score-scale scans run, so any OTHER
# decision-linked numeric threshold (e.g. a reintroduced "Accept: score >= 80")
# in that file still fails the residency rule.
RE_REVIEW_SANCTIONED_LITERALS = (
    "≥ 50% of P1 items",
    "`p2_addressed_rate < 80%`",
    "`p2_addressed_rate ≥ 80%`",
)
STANDARDS = "academic-paper-reviewer/references/editorial_decision_standards.md"
SKILL = "academic-paper-reviewer/SKILL.md"
HANDOFF = "shared/handoff_schemas.md"
SCHEMA = "shared/sprint_contract.schema.json"
PANEL = "scripts/check_panel_synthesis.py"
CONTRACTS = (
    "shared/contracts/reviewer/full.json",
    "shared/contracts/reviewer/methodology_focus.json",
)
CONDITION_FIELDS = (
    "condition_id", "severity", "cross_reviewer_quantifier", "expression", "action",
)
EXPECTED_CONDITIONS = {
    CONTRACTS[0]: (
        ("F1", 95, "any", "any mandatory dimension has a fatal block",
         "editorial_decision=reject"),
        ("F2", 90, "any", "any mandatory dimension scores 'block'",
         "editorial_decision=major_revision"),
        ("F3", 70, "majority",
         "two or more mandatory dimensions score 'warn' or worse",
         "editorial_decision=major_revision"),
        ("F4", 60, "any", "any high-priority dimension scores 'block'",
         "editorial_decision=major_revision"),
        ("F5", 40, "any", "any dimension scores 'warn' or worse",
         "editorial_decision=minor_revision"),
        ("F0", 10, "all", "every dimension scores 'pass'",
         "editorial_decision=accept"),
    ),
    CONTRACTS[1]: (
        ("F1", 95, "any", "D1 has a fatal block",
         "editorial_decision=reject"),
        ("F2", 90, "any", "D1 scores 'block'",
         "editorial_decision=major_revision"),
        ("F3", 70, "any", "D1 scores 'warn'",
         "editorial_decision=major_revision"),
        ("F4", 40, "any", "D2 scores 'warn' or worse",
         "editorial_decision=minor_revision"),
        ("F0", 10, "all", "every dimension scores 'pass'",
         "editorial_decision=accept"),
    ),
}
EXPECTED_AUTHORITY_ROWS = (
    (
        "`full` (sprint contract)",
        "Mechanical synthesizer over reviewer contract v2; the matrix below "
        "never overrides it",
        "`block/warn/pass` + `block_class`",
        "Accept / Minor Revision / Major Revision / Reject",
    ),
    (
        "`methodology-focus` (sprint contract)",
        "Same mechanical engine, scoped to methods + presentation; no "
        "venue-fit dimension",
        "same",
        "four-value enum",
    ),
    (
        "`full` / `methodology-focus` without a contract",
        "Synthesis Protocol + the qualitative criteria and recommendation "
        "matrix in this file",
        "reviewer recommendations",
        "four-value enum",
    ),
    (
        "`re-review`",
        "#576 three-gate contract: `re_review_mode_protocol.md` § Decision "
        "Derivation, recomputed by `scripts/check_re_review_synthesis.py`",
        "item verdicts (FULLY/PARTIALLY/NOT_ADDRESSED/MADE_WORSE/CANNOT_VERIFY)",
        "Accept / Minor Revision / Major Revision / user_review_required "
        "(Reject is not a Stage 3' decision)",
    ),
    ("`quick`", "EIC assessment only; advisory, not an editorial decision",
     "—", "signal"),
    ("`guided`", "Issue-list dialogue; no editorial decision letter",
     "—", "—"),
    (
        "`calibration`",
        "`quality_rubrics.md` 0–100 Decision Mapping, measurement-only",
        "0–100",
        "four-value labels against the gold set",
    ),
)
LIVE_ROOTS = (
    "academic-paper-reviewer",
    "shared/contracts/reviewer",
)
LIVE_FILES = (
    SCHEMA, HANDOFF, PANEL, "scripts/check_sprint_contract.py",
)
THRESHOLD_DRIFT_PATTERNS = (
    (
        "decision-linked boundary",
        re.compile(
            r"(?i)(?:accept(?:ance)?|minor revision|major revision|reject(?:ion)?)"
            r".{0,80}(?:(?:>=|≥|>|at least|no lower than|begins? at|"
            r"starts? at|from)\s*)"
            r"(?:80|65|50)\b"
        ),
    ),
    (
        "decision-linked trailing comparator",
        re.compile(
            r"(?i)(?:accept(?:ance)?|minor revision|major revision|reject(?:ion)?)"
            r".{0,80}\b(?:80|65|50)(?:\s+points?)?\s*"
            r"(?:(?:or|and)\s+(?:higher|above|better|greater|stronger)|\+)"
        ),
    ),
    (
        "boundary-linked decision",
        re.compile(
            r"(?i)\b(?:80|65|50)\s*points?.{0,80}"
            r"(?:accept(?:ance)?|minor revision|major revision|reject(?:ion)?)"
        ),
    ),
    (
        "decision-linked out-of-scale boundary",
        re.compile(
            r"(?i)(?:accept(?:ance)?|minor revision|major revision|reject(?:ion)?)"
            r".{0,80}(?<![\d.])(?:80|65|50)\s+out of\s+100\b"
        ),
    ),
    (
        "decision-linked labelled score",
        re.compile(
            r"(?i)(?:accept(?:ance)?|minor revision|major revision|reject(?:ion)?)"
            r"\s*(?::|=|[-–—])\s*(?:80|65|50)(?:\s+points?)?\b"
        ),
    ),
    (
        "numeric decision range",
        re.compile(
            r"(?i)(?:(?:accept(?:ance)?|minor revision|major revision|"
            r"reject(?:ion)?).{0,80}\b(?:65|50)"
            r"(?:\s*[-–—]\s*|\s+(?:to|through)\s+)(?:79|64)\b|"
            r"\b(?:65|50)(?:\s*[-–—]\s*|\s+(?:to|through)\s+)"
            r"(?:79|64)\b.{0,80}"
            r"(?:accept(?:ance)?|minor revision|major revision|reject(?:ion)?))"
        ),
    ),
    (
        "below-50 decision boundary",
        re.compile(
            r"(?i)(?:(?:accept(?:ance)?|minor revision|major revision|reject(?:ion)?)"
            r".{0,80}(?:<|below|under|beneath|less than)\s*50\b|"
            r"(?:<|below|under|beneath|less than)\s*50\b.{0,80}"
            r"(?:accept(?:ance)?|minor revision|major revision|reject(?:ion)?))"
        ),
    ),
)
DECISION_LABEL_RE = re.compile(
    r"(?i)(?:accept(?:ance)?|minor revision|major revision|reject(?:ion)?)"
)
THRESHOLD_ATOM_RE = re.compile(
    r"(?ix)"
    r"(?:"
    r"(?:>=|≥|>|<=|≤|<|at\s+least|at\s+or\s+above|no\s+less\s+than|"
    r"no\s+lower\s+than|"
    r"minimum(?:\s+of)?|begins?\s+at|starts?\s+at|opens?\s+at|from|"
    r"below|under|beneath|less\s+than)\s*(?:80|65|50)\b"
    r"|(?<![\d.])(?:80|65|50)(?:\s+points?)?\s*"
    r"(?:(?:or|and)\s+(?:higher|above|more|over|up|better|greater|stronger)|\+)"
    r"|(?<![\d.])(?:80|65|50)"
    r"(?:\s*[-–—]\s*|\s+(?:to|through)\s+)(?:100|79|64)\b"
    r"|(?<![\d.])(?:80|65|50)\s+out\s+of\s+100\b"
    r"|(?<![\d.])(?:80|65|50)\s*/\s*100\b"
    r"|(?:score|average|rubric|composite|threshold|cutoff|band)"
    r"(?:\s+score)?\s*(?:of|is|:|=)?\s*(?:80|65|50)\b"
    r"|(?<![\d.])(?:80|65|50)\s+points?\b"
    r")"
)
HEADING_RE = re.compile(r"^(?P<marks>#{1,6})\s+(?P<title>\S.*)$")
SCHEMA6_ENUM_ROW = (
    '| `editorial_decision` | enum | `"Accept"` / `"Minor Revision"` / '
    '`"Major Revision"` / `"Reject"` |'
)
DECISION_MAPPING_ROWS = (
    "| >= 80 | Accept |",
    "| 65-79 | Minor Revision |",
    "| 50-64 | Major Revision |",
    "| < 50 | Reject |",
)


def _read(root: Path, rel: str) -> str:
    return read_or_exit2(root, rel)


def _panel_action_enum(panel: str) -> tuple[str, ...] | None:
    """Return the literal ACTION_ENUM, rejecting aliases and computed values."""
    try:
        tree = ast.parse(panel)
    except SyntaxError:
        return None
    matches: list[tuple[str, ...]] = []
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(
            isinstance(target, ast.Name) and target.id == "ACTION_ENUM"
            for target in node.targets
        ):
            continue
        value = node.value
        if not (
            isinstance(value, ast.Call)
            and isinstance(value.func, ast.Name)
            and value.func.id == "frozenset"
            and len(value.args) == 1
            and not value.keywords
            and isinstance(value.args[0], ast.Set)
        ):
            return None
        elements = value.args[0].elts
        if not all(
            isinstance(element, ast.Constant) and isinstance(element.value, str)
            for element in elements
        ):
            return None
        matches.append(tuple(element.value for element in elements))
    return matches[0] if len(matches) == 1 else None


def _heading_threshold_drift(text: str) -> bool:
    """Detect threshold atoms anywhere inside a decision-labelled section."""
    active_level: int | None = None
    for line in text.splitlines():
        heading = HEADING_RE.match(line)
        if heading:
            level = len(heading.group("marks"))
            if active_level is not None and level <= active_level:
                active_level = None
            if DECISION_LABEL_RE.search(heading.group("title")):
                active_level = level
            continue
        if active_level is not None and THRESHOLD_ATOM_RE.search(line):
            return True
    return False


def _inline_threshold_drift(text: str) -> bool:
    """Detect a decision label and threshold atom within 80 chars on one line."""
    for line in text.splitlines():
        labels = tuple(DECISION_LABEL_RE.finditer(line))
        atoms = tuple(THRESHOLD_ATOM_RE.finditer(line))
        for label in labels:
            for atom in atoms:
                gap = max(
                    atom.start() - label.end(),
                    label.start() - atom.end(),
                    0,
                )
                if gap <= 80:
                    return True
    return False


def _nearby_threshold_drift(text: str) -> bool:
    """Detect a label and threshold atom across a compact Markdown block."""
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if not DECISION_LABEL_RE.search(line):
            continue
        start = index
        while start > 0 and index - start < 2 and lines[start - 1].strip():
            start -= 1
        end = index + 1
        while (
            end < len(lines)
            and end - index <= 2
            and lines[end].strip()
            and not HEADING_RE.match(lines[end])
        ):
            end += 1
        block = "\n".join(lines[start:end])
        if THRESHOLD_ATOM_RE.search(block):
            return True
    return False


def check(root: Path) -> list[str]:
    errors: list[str] = []
    schema = json.loads(_read(root, SCHEMA))
    branch4 = schema["allOf"][3]["then"]["properties"]["failure_conditions"][
        "items"]["properties"]["action"]["enum"]
    if tuple(branch4) != ACTIONS:
        errors.append(f"{SCHEMA}: branch 4 enum drift: {branch4}")

    panel = _read(root, PANEL)
    panel_actions = _panel_action_enum(panel)
    if panel_actions is None or len(panel_actions) != len(ACTIONS) or \
            set(panel_actions) != set(ACTIONS):
        errors.append(f"{PANEL}: ACTION_ENUM must be exactly {list(ACTIONS)}")

    for rel in CONTRACTS:
        conditions = json.loads(_read(root, rel))["failure_conditions"]
        actions = {condition["action"] for condition in conditions}
        if not actions <= set(ACTIONS) or not set(ACTIONS) <= actions:
            errors.append(f"{rel}: four-action coverage drift: {sorted(actions)}")
        actual = tuple(
            tuple(condition[field] for field in CONDITION_FIELDS)
            for condition in conditions
        )
        if actual != EXPECTED_CONDITIONS[rel]:
            errors.append(f"{rel}: failure-condition table drift: {actual}")

    handoff = heading_section(
        _read(root, HANDOFF),
        "## Schema 6: Review Report (academic-paper-reviewer -> pipeline)",
    )
    if handoff is None:
        errors.append(f"{HANDOFF}: Schema 6 section missing")
    else:
        if handoff.count(SCHEMA6_ENUM_ROW) != 1:
            errors.append(
                f"{HANDOFF}: Schema 6 decision enum must be exactly {list(VALUES)}"
            )

    authority = heading_section(_read(root, STANDARDS), "## 0. Decision Authority by Mode")
    if authority is None:
        errors.append(f"{STANDARDS}: §0 authority table missing")
    else:
        authority_rows = []
        for line in authority.splitlines():
            stripped = line.strip()
            if "|" not in stripped:
                continue
            if stripped.startswith("|"):
                stripped = stripped[1:]
            if stripped.endswith("|"):
                stripped = stripped[:-1]
            cells = tuple(cell.strip() for cell in stripped.split("|"))
            if cells == ("Mode", "Decision engine", "Working scale", "Output"):
                continue
            if len(cells) == 4 and all(
                re.fullmatch(r":?-{3,}:?", cell) for cell in cells
            ):
                continue
            authority_rows.append(cells)
        if tuple(authority_rows) != EXPECTED_AUTHORITY_ROWS:
            errors.append(
                f"{STANDARDS}: authority table semantic drift: {authority_rows}"
            )
        if norm_ws("Under a sprint contract, the mechanical synthesizer governs") \
                not in norm_ws(authority):
            errors.append(f"{STANDARDS}: mechanical governor sentence missing")
    if "canonical per-mode decision authority table" not in _read(root, SKILL):
        errors.append(f"{SKILL}: §0 authority pointer missing")

    for rel in LIVE_FILES:
        if "reject_or_major_revision" in _read(root, rel):
            errors.append(f"{rel}: retired hybrid decision token present")
    for live_root in LIVE_ROOTS:
        base = root / live_root
        for path in base.rglob("*"):
            if path.is_file() and path.suffix in {".md", ".json", ".py"}:
                if "reject_or_major_revision" in path.read_text(encoding="utf-8"):
                    errors.append(
                        f"{path.relative_to(root)}: retired hybrid decision token present"
                    )

    thresholds = (">= 80", "65-79", "50-64", "< 50")
    quality = _read(root, QUALITY)
    for threshold in thresholds:
        if quality.count(threshold) != 1:
            errors.append(f"{QUALITY}: threshold residency drift for {threshold}")
    for row in DECISION_MAPPING_ROWS:
        if quality.count(row) != 1:
            errors.append(f"{QUALITY}: decision mapping row drift for {row}")
    live_paths: set[Path] = set()
    for live_root in LIVE_ROOTS:
        base = root / live_root
        for path in base.rglob("*"):
            if path.is_file() and path.suffix in {".md", ".json", ".py"}:
                live_paths.add(path)
    live_paths.update(root / rel for rel in LIVE_FILES)
    for path in sorted(live_paths):
        rel = str(path.relative_to(root))
        if rel == QUALITY:
            continue
        text = path.read_text(encoding="utf-8")
        if rel == RE_REVIEW_PROTOCOL:
            # Mask ONLY the sanctioned #576 §6 item-proportion literals
            # (see RE_REVIEW_SANCTIONED_LITERALS above); every scan below
            # still runs on the residue, so a reintroduced 0-100 score rule
            # in this file fails exactly like anywhere else.
            for literal in RE_REVIEW_SANCTIONED_LITERALS:
                text = text.replace(literal, "<§6-item-proportion>")
        for threshold in thresholds:
            if threshold in text:
                errors.append(
                    f"{rel}: decision threshold {threshold} must reside only "
                    f"in {QUALITY}"
                )
        for label, pattern in THRESHOLD_DRIFT_PATTERNS:
            if pattern.search(text):
                errors.append(
                    f"{rel}: {label} must reside only in {QUALITY}"
                )
        if (
            _inline_threshold_drift(text)
            or _nearby_threshold_drift(text)
            or _heading_threshold_drift(text)
        ):
            errors.append(
                f"{rel}: decision-linked threshold variant must reside only "
                f"in {QUALITY}"
            )
    standards = _read(root, STANDARDS)
    for retired in ("4.0", "3.5", "2.5-3.4", "< 2.5", "score = 1", "score = 2"):
        if retired in standards:
            errors.append(f"{STANDARDS}: retired 1-5 threshold residue {retired}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    args = parser.parse_args()
    errors = check(args.root)
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("check_decision_contract: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
