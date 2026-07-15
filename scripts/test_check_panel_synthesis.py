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


def test_pattern2_or_worse_boundaries_beyond_warn():
    # 'or worse' floor semantics must hold at both the 'warn' and 'block'
    # anchors, not just the 'warn' anchor already covered above.
    p_warn = pred("two or more mandatory dimensions score 'warn' or worse")
    assert p_warn({**ALL_PASS, "D1": "pass", "D2": "pass"}) is False  # both pass: no fire

    p_block = pred("two or more mandatory dimensions score 'block' or worse")
    assert p_block({**ALL_PASS, "D1": "warn", "D2": "warn"}) is False  # warns don't reach block
    assert p_block({**ALL_PASS, "D1": "block", "D2": "block"}) is True  # two blocks: fires


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


# --- synthesis parser -----------------------------------------------------------

def make_synthesis(fired_list, decision):
    inner = ", ".join(fired_list)
    return (f"## Synthesis\n\nfired_conditions: [{inner}]\n{decision}\n")


def test_parse_synthesis_happy_and_empty_list():
    fired, dec = cps.parse_synthesis(
        "s.md", make_synthesis(["F2"], "editorial_decision=major_revision"),
        FULL_CONTRACT)
    assert fired == ["F2"] and dec == "editorial_decision=major_revision"
    fired, dec = cps.parse_synthesis(
        "s.md", make_synthesis([], "editorial_decision=accept"), FULL_CONTRACT)
    assert fired == [] and dec == "editorial_decision=accept"


@pytest.mark.parametrize("text", [
    "editorial_decision=accept\n",                                  # missing fired list
    "fired_conditions: [F2]\n",                                     # missing decision
    make_synthesis(["F9"], "editorial_decision=accept"),            # unknown condition id
    make_synthesis(["F2", "F2"], "editorial_decision=accept"),      # duplicate id
    make_synthesis(["F2"], "editorial_decision=accept")
        + "editorial_decision=accept\n",                            # duplicate decision line
    make_synthesis(["F2"], "editorial_decision=sideways"),          # unknown token
    "fired_conditions: [F2]\nfired_conditions: [F1]\n"
        + "editorial_decision=accept\n",                            # duplicate fired list
])
def test_parse_synthesis_mutations_raise(text):
    with pytest.raises(cps.SynthesisError):
        cps.parse_synthesis("s.md", text, FULL_CONTRACT)


# --- contract loader ------------------------------------------------------------

def test_load_contract_shipped_templates(tmp_path):
    for rel in ("shared/contracts/reviewer/full.json",
                "shared/contracts/reviewer/methodology_focus.json"):
        contract, predicates = cps.load_contract(REPO / rel)
        assert set(predicates) == {c["condition_id"]
                                   for c in contract["failure_conditions"]}


def _write(tmp_path, obj):
    p = tmp_path / "c.json"
    p.write_text(json.dumps(obj), encoding="utf-8")
    return p


def test_load_contract_rejects_unsupported_mode(tmp_path):
    bad = dict(FULL_CONTRACT)
    bad["mode"] = "writer_full"
    with pytest.raises(cps.ContractError):
        cps.load_contract(_write(tmp_path, bad))


def test_load_contract_rejects_evaluator_mode(tmp_path):
    # evaluator_full is a real Schema 13.1 mode (v3.6.8), but this checker
    # only publishes a panel mapping for reviewer_* modes (protocol §7).
    bad = json.loads(json.dumps(FULL_CONTRACT))
    bad["mode"] = "evaluator_full"
    with pytest.raises(cps.ContractError):
        cps.load_contract(_write(tmp_path, bad))


def test_load_contract_rejects_panel_size_mismatch(tmp_path):
    bad = json.loads(json.dumps(FULL_CONTRACT))
    bad["panel_size"] = 4
    with pytest.raises(cps.ContractError):
        cps.load_contract(_write(tmp_path, bad))


def test_load_contract_rejects_schema_invalid(tmp_path):
    bad = json.loads(json.dumps(FULL_CONTRACT))
    del bad["failure_conditions"]
    with pytest.raises(cps.ContractError):
        cps.load_contract(_write(tmp_path, bad))


# --- layer engines ----------------------------------------------------------------

WARN2 = {**ALL_PASS, "D1": "warn", "D2": "warn"}   # F2 predicate true
FIRED_F2 = {"F1": False, "F2": True, "F3": False, "F0": False}
FIRED_F0 = {"F1": False, "F2": False, "F3": False, "F0": True}


def _predicates():
    return cps.load_contract(REPO / "shared/contracts/reviewer/full.json")[1]


def test_layer1_consistent_report_no_diags():
    r = cps.parse_report("r.md", make_report(
        scores=WARN2, fired=FIRED_F2,
        decision="editorial_decision=major_revision"), FULL_CONTRACT)
    assert cps.layer1_check(r, FULL_CONTRACT, _predicates(), []) == []


def test_layer1_fired_flag_contradicts_scores():
    r = cps.parse_report("r.md", make_report(
        scores=WARN2, fired=FIRED_F0,             # claims F0 despite 2 warns
        decision="editorial_decision=accept"), FULL_CONTRACT)
    diags = cps.layer1_check(r, FULL_CONTRACT, _predicates(), [])
    assert any("condition=F2" in d for d in diags)
    assert any("condition=F0" in d for d in diags)


def test_layer1_decision_contradicts_declared_fired():
    r = cps.parse_report("r.md", make_report(
        scores=WARN2, fired=FIRED_F2,
        decision="editorial_decision=accept"), FULL_CONTRACT)
    diags = cps.layer1_check(r, FULL_CONTRACT, _predicates(), [])
    assert any("decision_declared=editorial_decision=accept" in d for d in diags)


def test_layer1_zero_fired_fallback_reviewer_level():
    one_warn = {**ALL_PASS, "D1": "warn"}          # fires nothing
    none_fired = {"F1": False, "F2": False, "F3": False, "F0": False}
    r = cps.parse_report("r.md", make_report(
        scores=one_warn, fired=none_fired,
        decision="editorial_decision=accept"), FULL_CONTRACT)
    assert cps.layer1_check(r, FULL_CONTRACT, _predicates(), []) == []


def _panel(scores_by_role, fired_by_role, decision_by_role):
    return [cps.parse_report(f"{role}.md", make_report(
                role=role, scores=scores_by_role[role],
                fired=fired_by_role[role], decision=decision_by_role[role]),
            FULL_CONTRACT)
            for role in ("eic", "methodology", "domain", "perspective", "da")]


def _consistent_panel_majority_f2():
    scores = {"eic": WARN2, "methodology": WARN2, "domain": WARN2,
              "perspective": ALL_PASS, "da": ALL_PASS}
    fired = {"eic": FIRED_F2, "methodology": FIRED_F2, "domain": FIRED_F2,
             "perspective": FIRED_F0, "da": FIRED_F0}
    dec = {"eic": "editorial_decision=major_revision",
           "methodology": "editorial_decision=major_revision",
           "domain": "editorial_decision=major_revision",
           "perspective": "editorial_decision=accept",
           "da": "editorial_decision=accept"}
    return _panel(scores, fired, dec)


def test_layer2_consistent_panel():
    reports = _consistent_panel_majority_f2()
    diags = cps.layer2_check(reports, FULL_CONTRACT, _predicates(),
                             ["F2"], "editorial_decision=major_revision", [])
    assert diags == []


def test_layer2_flipped_decision_fails():
    reports = _consistent_panel_majority_f2()
    diags = cps.layer2_check(reports, FULL_CONTRACT, _predicates(),
                             ["F2"], "editorial_decision=minor_revision", [])
    assert any("PANEL-SYNTHESIS-MISMATCH" in d for d in diags)


def test_layer2_fabricated_fired_list_fails_despite_right_decision():
    reports = _consistent_panel_majority_f2()
    diags = cps.layer2_check(reports, FULL_CONTRACT, _predicates(),
                             ["F3"], "editorial_decision=major_revision", [])
    assert any("PANEL-SYNTHESIS-MISMATCH" in d for d in diags)


def test_layer2_one_flipped_score_changes_outcome():
    reports = _consistent_panel_majority_f2()
    reports[2].scores["D2"] = "pass"   # domain drops to 1 warn -> F2 only 2-of-5
    diags = cps.layer2_check(reports, FULL_CONTRACT, _predicates(),
                             ["F2"], "editorial_decision=major_revision", [])
    assert any("PANEL-SYNTHESIS-MISMATCH" in d for d in diags)


def test_layer2_panel_zero_fired_accepts():
    scores = {r: ALL_PASS for r in ("eic", "methodology", "domain",
                                    "perspective", "da")}
    scores["eic"] = {**ALL_PASS, "D1": "warn"}     # breaks F0, fires nothing
    fired = {r: FIRED_F0 for r in scores}
    fired["eic"] = {"F1": False, "F2": False, "F3": False, "F0": False}
    dec = {r: "editorial_decision=accept" for r in scores}
    reports = _panel(scores, fired, dec)
    diags = cps.layer2_check(reports, FULL_CONTRACT, _predicates(),
                             [], "editorial_decision=accept", [])
    assert diags == []


def test_duplicate_path_emits_single_cardinality_diag(tmp_path, capsys):
    r = tmp_path / "r_eic.md"
    r.write_text(make_report(), encoding="utf-8")
    synth = tmp_path / "synth.md"
    synth.write_text(make_synthesis([], "editorial_decision=accept"),
                     encoding="utf-8")
    contract = str(REPO / "shared/contracts/reviewer/full.json")
    rc = cps.main(["--contract", contract] +
                  ["--report", str(r)] * 5 +
                  ["--synthesis", str(synth)])
    assert rc == 2
    out = capsys.readouterr().out
    # A single reused path must not be re-hashed on every repeated
    # occurrence: the byte-identical diagnostic must fire at most once
    # (previously fired once per repeat beyond the first, i.e. 4 times
    # here). The separate, legitimate "duplicate report paths" and
    # "roles ... != required" diagnostics are independent infra checks
    # that correctly still fire for this same 5x-identical-path input and
    # are out of scope for this fix.
    assert out.count("[PANEL-CARDINALITY: byte-identical report contents") == 0
    assert out.count("[PANEL-CARDINALITY:") == 2


# --- CLI integration over the canonical on-disk fixture ---------------------------

FIX = REPO / "tests/fixtures/panel-synthesis/full-consistent"
CONTRACT_PATH = str(REPO / "shared/contracts/reviewer/full.json")
ROLES = ("eic", "methodology", "domain", "perspective", "da")


def cli(*extra, reports=None):
    argv = ["--contract", CONTRACT_PATH]
    for p in (reports if reports is not None
              else [FIX / f"r_{r}.md" for r in ROLES]):
        argv += ["--report", str(p)]
    argv += list(extra)
    return cps.main(argv)


def test_cli_full_consistent_passes(capsys):
    assert cli("--synthesis", str(FIX / "synthesis.md")) == 0
    assert "PANEL-SYNTHESIS: PASS" in capsys.readouterr().out


def test_cli_layer1_only_single_report_passes(capsys):
    assert cli("--layer1-only", reports=[FIX / "r_eic.md"]) == 0
    out = capsys.readouterr().out
    assert "LAYER1-ONLY: PASS" in out
    assert "PANEL-SYNTHESIS" not in out          # never emits Layer-2 verdicts


def test_cli_layer1_only_rejects_synthesis_flag():
    with pytest.raises(SystemExit):
        cli("--layer1-only", "--synthesis", str(FIX / "synthesis.md"))


def test_cli_flipped_synthesis_decision_exit1(tmp_path, capsys):
    bad = tmp_path / "synth.md"
    bad.write_text(make_synthesis(["F2"], "editorial_decision=minor_revision"),
                   encoding="utf-8")
    assert cli("--synthesis", str(bad)) == 1
    assert "PANEL-SYNTHESIS-MISMATCH" in capsys.readouterr().out


def test_cli_inconsistent_reviewer_exit3(tmp_path):
    bad = tmp_path / "r_eic.md"
    bad.write_text(make_report(role="eic", scores=WARN2, fired=FIRED_F0,
                               decision="editorial_decision=accept"),
                   encoding="utf-8")
    reports = [bad] + [FIX / f"r_{r}.md" for r in ROLES[1:]]
    assert cli("--synthesis", str(FIX / "synthesis.md"), reports=reports) == 3


def test_cli_duplicate_report_path_exit2():
    reports = [FIX / "r_eic.md"] * 5
    assert cli("--synthesis", str(FIX / "synthesis.md"), reports=reports) == 2


def test_cli_byte_identical_contents_exit2(tmp_path):
    clone = tmp_path / "clone.md"
    clone.write_text((FIX / "r_eic.md").read_text(encoding="utf-8"),
                     encoding="utf-8")
    reports = [FIX / f"r_{r}.md" for r in ROLES[:4]] + [clone]
    assert cli("--synthesis", str(FIX / "synthesis.md"), reports=reports) == 2


def test_cli_wrong_report_count_exit2():
    reports = [FIX / f"r_{r}.md" for r in ROLES[:4]]
    assert cli("--synthesis", str(FIX / "synthesis.md"), reports=reports) == 2


def test_cli_role_set_mismatch_exit2(tmp_path):
    dup_role = tmp_path / "r_extra_eic.md"
    dup_role.write_text(make_report(role="eic", scores={**ALL_PASS, "D3": "warn"},
                                    fired={"F1": False, "F2": False,
                                           "F3": False, "F0": False},
                                    decision="editorial_decision=accept"),
                        encoding="utf-8")
    reports = [FIX / f"r_{r}.md" for r in ROLES[:4]] + [dup_role]
    assert cli("--synthesis", str(FIX / "synthesis.md"), reports=reports) == 2


def test_cli_unknown_contract_role_token_exit2(tmp_path):
    # 'banana' is well-formed per the contract_role line grammar but is not
    # in the mode's published role vocabulary (protocol §7) -> cardinality
    # failure, not a report-parse failure.
    bad_role = tmp_path / "r_banana.md"
    bad_role.write_text(make_report(role="banana", scores={**ALL_PASS, "D3": "warn"},
                                    fired={"F1": False, "F2": False,
                                           "F3": False, "F0": False},
                                    decision="editorial_decision=accept"),
                        encoding="utf-8")
    reports = [FIX / f"r_{r}.md" for r in ROLES[:4]] + [bad_role]
    assert cli("--synthesis", str(FIX / "synthesis.md"), reports=reports) == 2


def test_cli_layer1_only_too_many_reports_exit2():
    # layer1-only accepts 1..panel_size reports; panel_size+1 must reject.
    reports = [FIX / f"r_{r}.md" for r in ROLES] + [FIX / "r_eic.md"]
    assert cli("--layer1-only", reports=reports) == 2


def test_cli_exit_precedence_2_beats_3_and_1(tmp_path):
    # inconsistent reviewer (3) + duplicate paths (2) + flipped synthesis (1) -> 2
    bad = tmp_path / "r_eic.md"
    bad.write_text(make_report(role="eic", scores=WARN2, fired=FIRED_F0,
                               decision="editorial_decision=accept"),
                   encoding="utf-8")
    synth = tmp_path / "synth.md"
    synth.write_text(make_synthesis([], "editorial_decision=reject"),
                     encoding="utf-8")
    reports = [bad, bad] + [FIX / f"r_{r}.md" for r in ROLES[1:4]]
    assert cli("--synthesis", str(synth), reports=reports) == 2


def test_cli_exit_precedence_3_beats_1(tmp_path):
    bad = tmp_path / "r_eic.md"
    bad.write_text(make_report(role="eic", scores=WARN2, fired=FIRED_F0,
                               decision="editorial_decision=accept"),
                   encoding="utf-8")
    synth = tmp_path / "synth.md"
    synth.write_text(make_synthesis([], "editorial_decision=reject"),
                     encoding="utf-8")
    reports = [bad] + [FIX / f"r_{r}.md" for r in ROLES[1:]]
    assert cli("--synthesis", str(synth), reports=reports) == 3


def test_cli_unreadable_report_exit2(tmp_path):
    missing = tmp_path / "nope.md"
    reports = [missing] + [FIX / f"r_{r}.md" for r in ROLES[1:]]
    assert cli("--synthesis", str(FIX / "synthesis.md"), reports=reports) == 2


def test_cli_non_utf8_report_exit2(tmp_path):
    binary = tmp_path / "bin.md"
    binary.write_bytes(b"\xff\xfe\x00bad")
    reports = [binary] + [FIX / f"r_{r}.md" for r in ROLES[1:]]
    assert cli("--synthesis", str(FIX / "synthesis.md"), reports=reports) == 2


def test_cli_methodology_focus_round(tmp_path, capsys):
    mcontract = REPO / "shared/contracts/reviewer/methodology_focus.json"
    mc = json.loads(mcontract.read_text(encoding="utf-8"))
    dims = {d["id"]: d["name"] for d in mc["acceptance_dimensions"]}

    def mreport(role, d1, fired, decision):
        return "\n".join([
            f"contract_role: {role}", "", "## Dimension Scores", "",
            f"### D1: {dims['D1']}", f"score: {d1}", "",
            f"### D2: {dims['D2']}", "score: pass", "",
            "## Failure Condition Checks", "",
            "### F1", f"fired: {str(fired['F1']).lower()}", "",
            "### F2", f"fired: {str(fired['F2']).lower()}", "",
            "### F0", f"fired: {str(fired['F0']).lower()}", "",
            "## Review Body", "", "Fixture body.", "",
            "## Editorial Decision", "", decision, ""])

    r1 = tmp_path / "r_eic.md"
    r1.write_text(mreport("eic", "pass",
                          {"F1": False, "F2": False, "F0": True},
                          "editorial_decision=accept"), encoding="utf-8")
    r2 = tmp_path / "r_methodology.md"
    r2.write_text(mreport("methodology", "warn",
                          {"F1": False, "F2": True, "F0": False},
                          "editorial_decision=major_revision"), encoding="utf-8")
    synth = tmp_path / "synth.md"
    synth.write_text(make_synthesis(["F2"], "editorial_decision=major_revision"),
                     encoding="utf-8")
    assert cps.main(["--contract", str(mcontract),
                     "--report", str(r1), "--report", str(r2),
                     "--synthesis", str(synth)]) == 0


# --- Unicode line-separator bypass (#524 separator-class discipline) -------------

def test_unicode_line_separators_do_not_create_anchored_lines():
    # NEL-embedded decision token must not satisfy the exactly-once rule
    # when the real decision line is absent (#524 separator-class discipline).
    base = make_report()
    real = "editorial_decision=accept"
    mangled = base.replace(
        real, "prose\x85editorial_decision=accept\x85tail")
    with pytest.raises(cps.ReportError):
        cps.parse_report("r.md", mangled, FULL_CONTRACT)


def test_crlf_report_still_parses(tmp_path):
    p = tmp_path / "r.md"
    p.write_bytes(make_report().replace("\n", "\r\n").encode("utf-8"))
    text = cps._read_text(p)
    r = cps.parse_report("r.md", text, FULL_CONTRACT)
    assert r.decision == "editorial_decision=accept"
