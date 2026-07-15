"""Tests for scripts/check_panel_synthesis.py (#510).

Fixture strategy: unit layers use in-test builders; one canonical on-disk
round under tests/fixtures/panel-synthesis/full-consistent/ exercises the
CLI end-to-end (Task 5). Mutations are in-code transforms of builder output.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_panel_synthesis as cps

REPO = Path(__file__).resolve().parent.parent
FULL_CONTRACT = json.loads(
    (REPO / "shared/contracts/reviewer/full.json").read_text(encoding="utf-8")
)

# --- helpers -----------------------------------------------------------------

def full_dims_by_priority():
    by_p: dict[str, list[str]] = {}
    for d in FULL_CONTRACT["acceptance_dimensions"]:
        by_p.setdefault(d["priority"], []).append(d["id"])
    return by_p


def full_dim_ids():
    return {d["id"] for d in FULL_CONTRACT["acceptance_dimensions"]}


def pred(expr, cid="Fx"):
    return cps.parse_expression(expr, full_dims_by_priority(), full_dim_ids(), cid)


ALL_PASS = {"D1": "pass", "D2": "pass", "D3": "pass", "D4": "pass", "D5": "pass"}


# --- expression grammar (§9, all five patterns + variants) --------------------

def test_pattern1_any_priority_bare():
    p = pred("any mandatory dimension scores 'block'")
    assert p({**ALL_PASS, "D1": "block"}) is True
    assert p({**ALL_PASS, "D4": "block"}) is False  # D4 is high, not mandatory
    assert p(ALL_PASS) is False


def test_pattern1_priority_eq_variant():
    p = pred("any dimension with priority=high scores 'block'")
    assert p({**ALL_PASS, "D4": "block"}) is True
    assert p(ALL_PASS) is False


def test_pattern1_hyphen_priority_variant():
    p = pred("any high-priority dimension scores 'block'")
    assert p({**ALL_PASS, "D4": "block"}) is True


def test_pattern2_count_or_worse_boundaries():
    p = pred("two or more mandatory dimensions score 'warn' or worse")
    assert p({**ALL_PASS, "D1": "warn", "D2": "warn"}) is True
    assert p({**ALL_PASS, "D1": "warn", "D2": "block"}) is True   # block >= warn
    assert p({**ALL_PASS, "D1": "warn"}) is False                 # only one
    assert p({**ALL_PASS, "D1": "warn", "D4": "warn"}) is False   # D4 not mandatory


def test_pattern2_priority_eq_variant():
    p = pred("two or more dimensions with priority=mandatory score 'warn' or worse")
    assert p({**ALL_PASS, "D1": "block", "D3": "warn"}) is True


def test_pattern3_every_priority():
    p = pred("every mandatory dimension scores 'pass'")
    assert p(ALL_PASS) is True
    assert p({**ALL_PASS, "D3": "warn"}) is False


def test_pattern4_dim_literal():
    p = pred("D1 scores 'block'")
    assert p({**ALL_PASS, "D1": "block"}) is True
    assert p(ALL_PASS) is False


def test_pattern5_conjunction():
    p = pred("D1 scores 'warn' AND every high dimension scores 'pass'")
    assert p({**ALL_PASS, "D1": "warn"}) is True
    assert p({**ALL_PASS, "D1": "warn", "D4": "warn"}) is False


@pytest.mark.parametrize("bad", [
    "any mandatory dimension scores 'BLOCK'",          # case mutation
    "any mandatory dimension scores \"block\"",        # quote mutation
    "any  mandatory dimension scores 'block'",         # internal whitespace
    "some mandatory dimension scores 'block'",         # unknown verb
    "any mandatory dimension scores 'fatal'",          # unknown score
    "D1 scores 'block' OR D2 scores 'block'",          # OR not in vocabulary
])
def test_unrecognised_expressions_raise(bad):
    with pytest.raises(cps.ContractError):
        pred(bad)


def test_orphan_dimension_literal_raises():
    with pytest.raises(cps.ContractError):
        pred("D9 scores 'block'")


def test_empty_priority_scope_raises_no_vacuous_truth():
    with pytest.raises(cps.ContractError):
        pred("every critical dimension scores 'pass'")  # no 'critical' dims


# --- quantifiers ---------------------------------------------------------------

def test_quantifier_any():
    assert cps.quantifier_fires("any", [False, True, False, False, False], []) is True
    assert cps.quantifier_fires("any", [False] * 5, []) is False


def test_quantifier_all():
    assert cps.quantifier_fires("all", [True] * 5, []) is True
    assert cps.quantifier_fires("all", [True, True, True, True, False], []) is False


def test_quantifier_majority_simple_majority_n5():
    # Corrected bar (#531): floor(5/2)+1 == 3. 2-of-5 must NOT fire, 3-of-5 MUST.
    assert cps.quantifier_fires("majority", [True, True, False, False, False], []) is False
    assert cps.quantifier_fires("majority", [True, True, True, False, False], []) is True


def test_quantifier_majority_n3():
    assert cps.quantifier_fires("majority", [True, True, False], []) is True
    assert cps.quantifier_fires("majority", [True, False, False], []) is False


def test_quantifier_majority_n2_collapses_to_all():
    assert cps.quantifier_fires("majority", [True, False], []) is False
    assert cps.quantifier_fires("majority", [True, True], []) is True


def test_quantifier_majority_n1_never_fires_and_warns():
    warnings: list[str] = []
    assert cps.quantifier_fires("majority", [True], warnings) is False
    assert any("panel_size=1" in w for w in warnings)


# --- precedence + zero-fired fallback ------------------------------------------

def test_precedence_higher_severity_wins_regardless_of_order():
    conds = FULL_CONTRACT["failure_conditions"]  # F1(90), F2(70), F3(60), F0(10)
    assert cps.resolve_decision(conds, {"F2", "F1"}) == "editorial_decision=reject_or_major_revision"
    assert cps.resolve_decision(conds, {"F3", "F2"}) == "editorial_decision=major_revision"  # F2 sev 70 > F3 60


def test_precedence_equal_severity_ordinal_tiebreak():
    conds = [
        {"condition_id": "FA", "severity": 50, "action": "editorial_decision=major_revision"},
        {"condition_id": "FB", "severity": 50, "action": "editorial_decision=minor_revision"},
        {"condition_id": "F0", "severity": 10, "action": "editorial_decision=accept"},
    ]
    assert cps.resolve_decision(conds, {"FA", "FB"}) == "editorial_decision=major_revision"


def test_zero_fired_falls_back_to_contract_accept_grade():
    conds = FULL_CONTRACT["failure_conditions"]
    assert cps.resolve_decision(conds, set()) == "editorial_decision=accept"


def test_missing_accept_grade_entry_raises():
    conds = [{"condition_id": "F1", "severity": 90, "action": "editorial_decision=reject"}]
    with pytest.raises(cps.ContractError):
        cps.resolve_decision(conds, set())


# --- report parser --------------------------------------------------------------

def make_report(role="eic", scores=None, fired=None,
                decision="editorial_decision=accept"):
    scores = scores or ALL_PASS
    fired = fired if fired is not None else {"F1": False, "F2": False,
                                             "F3": False, "F0": True}
    dim_names = {d["id"]: d["name"] for d in FULL_CONTRACT["acceptance_dimensions"]}
    parts = [f"contract_role: {role}", "", "## Dimension Scores", ""]
    for did in sorted(scores):
        parts += [f"### {did}: {dim_names[did]}", f"score: {scores[did]}", ""]
    parts += ["## Failure Condition Checks", ""]
    for cid in ["F1", "F2", "F3", "F0"]:
        parts += [f"### {cid}", f"fired: {str(fired[cid]).lower()}", ""]
    parts += ["## Review Body", "", "Fixture body.", "",
              "## Editorial Decision", "", decision, ""]
    return "\n".join(parts)


def test_parse_report_happy_path():
    r = cps.parse_report("r.md", make_report(), FULL_CONTRACT)
    assert r.role == "eic"
    assert r.scores == ALL_PASS
    assert r.fired == {"F1": False, "F2": False, "F3": False, "F0": True}
    assert r.decision == "editorial_decision=accept"


@pytest.mark.parametrize("mutate,frag", [
    (lambda t: t.replace("## Editorial Decision", "## Renamed"), "missing required section"),
    (lambda t: t + "\n## Dimension Scores\n", "duplicated required section"),
    (lambda t: t.replace("contract_role: eic\n", ""), "contract_role"),
    (lambda t: t.replace("contract_role: eic", "contract_role: eic\ncontract_role: da"), "contract_role"),
    (lambda t: t.replace("### D5: writing_and_structure\nscore: pass\n", ""), "D5"),
    (lambda t: t.replace("### D5:", "### D9:"), "D9"),
    (lambda t: t.replace("score: pass", "score: pass\nscore: warn", 1), "score"),
    (lambda t: t.replace("score: pass", "score: fatal", 1), "score"),
    (lambda t: t.replace("### F3\nfired: false\n", ""), "F3"),
    (lambda t: t.replace("fired: true", "fired: yes"), "fired"),
    (lambda t: t.replace("editorial_decision=accept",
                         "editorial_decision=accept\neditorial_decision=accept"), "decision"),
    (lambda t: t.replace("editorial_decision=accept", "editorial_decision=maybe"), "decision"),
    (lambda t: t.replace("editorial_decision=accept", "the decision is accept"), "decision"),
])
def test_parse_report_mutations_raise(mutate, frag):
    with pytest.raises(cps.ReportError) as exc:
        cps.parse_report("r.md", mutate(make_report()), FULL_CONTRACT)
    assert frag.lower() in str(exc.value).lower()


def test_decoy_tokens_inside_fences_ignored():
    decoy = ("```\nscore: block\nfired: true\neditorial_decision=reject\n```\n\n")
    text = decoy + make_report()
    r = cps.parse_report("r.md", text, FULL_CONTRACT)
    assert r.decision == "editorial_decision=accept"


def test_prose_embedded_decision_not_matched():
    # Anchored-line rule: a token inside prose must not count as the decision line.
    text = make_report().replace(
        "Fixture body.",
        "Fixture body mentioning editorial_decision=reject inline in prose.")
    r = cps.parse_report("r.md", text, FULL_CONTRACT)
    assert r.decision == "editorial_decision=accept"
