#!/usr/bin/env python3
"""Tests for scripts/dispatch_panel_claim_audit.py (#1002). No model call:
transports are replaced by a fake runner, and claims and pairs are synthetic."""
from __future__ import annotations

import copy
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

import dispatch_panel_claim_audit as d  # noqa: E402

FIXTURES = tuple(d.FIXTURE_FILES)
CHECKED = {q: True for q in d.PAIR_QUESTIONS}
MECH = {"one_sentence_each": True, "word_counts_8_to_50": True, "changed_tokens_1_to_4": True,
        "evidence_quote_in_manuscript": True}


# ---------- helpers ----------


def _claims(per_bundle=2, size=40):
    rows = []
    for fixture in FIXTURES:
        for b in (1, 2):
            for i in range(per_bundle):
                rows.append({"claim_id": f"c-{fixture}-{b}-{i}", "bundle": f"{fixture}-bundle{b}",
                             "fixture": fixture, "text": f"Claim {i} of {fixture} bundle {b}. " + "x" * size})
    return rows


def _pairs(n=1):
    return [{"pair_id": f"{f}-p{i:02d}", "fixture": f, "mechanical": dict(MECH), "verify": dict(CHECKED),
             "accurate_sentence": f"The authors report result number {i} for {f} in the methods section.",
             "false_sentence": f"The authors report finding number {i} for {f} in the methods section.",
             "evidence_quote": f"result number {i} for {f}"}
            for f in FIXTURES for i in range(n)]


# Synthetic manuscripts: every test reads these, never the real ones.
MANUSCRIPTS = {f: f"Manuscript {f}. " + " ".join(f"We report result number {i} for {f}." for i in range(5))
               for f in FIXTURES}


@pytest.fixture
def small_plan(monkeypatch):
    plan = copy.deepcopy(d.load_plan())
    plan["claims"]["expected_counts"] = {"bundles": 6, "claims": 12}
    plan["contrast_pairs"]["min_accepted_per_fixture"] = 1
    plan["contrast_pairs"]["per_fixture_requested"] = 2
    plan["contrast_gate"] = {"min_detection": 1.0, "max_false_flag": 0.0, "rule": "test"}
    monkeypatch.setattr(d, "load_plan", lambda: plan)
    monkeypatch.setattr(d, "manuscript_text", lambda fixture: MANUSCRIPTS[fixture])
    return plan


def stream(text):
    """agy stream-json output for a plain reply."""
    events = [{"event": "init"}, {"event": "step_update", "step_update": {"step_type": "user_input"}},
              {"event": "step_update", "step_update": {"step_type": "agent_response", "text_delta": text}},
              {"event": "result", "result": {"status": "SUCCESS", "response": text}}]
    return "\n".join(json.dumps(e) for e in events) + "\n"


def codex_events(text, extra_items=()):
    """codex exec --json output for a reply, with a startup warning item."""
    events = [{"type": "thread.started"},
              {"type": "item.completed", "item": {"type": "error", "message": "config warning"}},
              {"type": "turn.started"}, *({"type": "item.completed", "item": i} for i in extra_items),
              {"type": "item.completed", "item": {"type": "agent_message", "text": text}},
              {"type": "turn.completed", "usage": {"input_tokens": 1, "output_tokens": 1}}]
    return "\n".join(json.dumps(e) for e in events) + "\n"


def _reply(cmd, text):
    return subprocess.CompletedProcess(cmd, 0, stdout=stream(text) if cmd[0] == "agy" else codex_events(text),
                                       stderr="")


def _pairs_dir(work, plan, pairs=None, answers=None, verifier=None):
    """Log a generator call and a verifier call per manuscript, as the CLI would."""
    pairs = _pairs() if pairs is None else pairs
    pdir = work / "pairs"
    pdir.mkdir(parents=True, exist_ok=True)
    log = pdir / "calls.jsonl"
    for f in FIXTURES:
        if not any(p["fixture"] == f for p in pairs):
            continue
        lines = [json.dumps({**{k: p[k] for k in ("accurate_sentence", "false_sentence", "evidence_quote")},
                             "pair_id": p["pair_id"].split("-", 1)[1]}) for p in pairs if p["fixture"] == f]
        d.call_model(plan["contrast_pairs"]["generator"]["transport"], d.generate_prompt(f, plan),
                     pdir / f"{f}.generate.out", log, f"generate-{f}",
                     runner=lambda cmd, input=None, _t="\n".join(lines) + "\n", **kw: _reply(cmd, _t))
    valid = d._group(d.mechanically_valid(d.generated_pairs(pdir, plan)), "fixture")
    for f, fpairs in valid.items():
        text = answers(fpairs) if answers else "\n".join(json.dumps({"pair_id": p["pair_id"], **CHECKED})
                                                         for p in fpairs) + "\n"
        d.call_model(verifier or plan["contrast_pairs"]["verifier"]["transport"], d.verify_prompt(f, fpairs),
                     pdir / f"{f}.verify.out", log, f"verify-{f}",
                     runner=lambda cmd, input=None, _t=text, **kw: _reply(cmd, _t))
    return pdir


def _build(tmp_path, claims=None, pairs=None, plan=None, **pair_kw):
    work = tmp_path / "work"
    (work / "claims").mkdir(parents=True)
    claims = _claims() if claims is None else claims
    d.write_jsonl(work / "claims" / "claims.jsonl", claims)
    d.write_jsonl(work / "claims" / "key.jsonl", [
        {"claim_id": c["claim_id"], "bundle": c["bundle"], "seat": "eic" if n % 2 else "da"}
        for n, c in enumerate(claims)])
    bundles = len({c["bundle"] for c in claims})
    (work / "claims" / "summary.json").write_text(json.dumps({"bundles": bundles, "claims": len(claims),
                                                              "problems": []}), encoding="utf-8")
    pdir = _pairs_dir(work, plan or d.load_plan(), pairs, **pair_kw)
    args = type("A", (), {"claims": work / "claims" / "claims.jsonl", "pairs_dir": pdir, "out": work / "batches"})
    return work, d.cmd_build(args)


_ITEM_RE = re.compile(r'^\{"claim_id": "(i\d{4})", "text": (".*")\}$')


class FakeJudge:
    """Answers every item in the prompt. ``policy(text) -> row fields``."""

    def __init__(self, policy, fail_after=None, stdout_override=None):
        self.policy, self.calls, self.fail_after, self.stdout_override = policy, [], fail_after, stdout_override

    def __call__(self, cmd, input=None, **kwargs):
        prompt = input if input is not None else cmd[cmd.index("-p") + 1]
        self.calls.append(prompt)
        if self.fail_after is not None and len(self.calls) > self.fail_after:
            return subprocess.CompletedProcess(cmd, 1, stdout="", stderr="Individual quota reached (429)")
        if self.stdout_override is not None:
            return _reply(cmd, self.stdout_override)
        claims = prompt.split("<claims>", 1)[1]
        lines = []
        for line in claims.splitlines():
            m = _ITEM_RE.match(line.strip())
            if m:
                lines.append(json.dumps({"claim_id": m.group(1), "severity": "minor", "reason": "r",
                                         **self.policy(json.loads(m.group(2)))}))
        return _reply(cmd, "\n".join(lines) + "\n")


def honest(text):
    """Calls the false contrast sentences false; flags one claim with an absent quotation."""
    if "finding number" in text:
        return {"verdict": "false", "evidence": "absent_quotation", "quote": "finding number", "locator": "absent"}
    if "Claim 0 of ms00_clean bundle 1" in text:
        return {"verdict": "false", "evidence": "absent_quotation", "quote": "Claim 0 of ms00_clean bundle 1",
                "locator": "absent"}
    return {"verdict": "true"}


# ---------- contrast pairs ----------


@pytest.mark.parametrize("a,b,n", [
    ("The study surveyed 120 students in 2023.", "The study surveyed 210 students in 2023.", 1),
    ("The study surveyed 120 students in 2023.", "The study interviewed 120 teachers in 2021.", 3),
    ("The study surveyed 120 students.", "The study surveyed 120 students.", 0),
    ("A B C D E F G H.", "A X Y Z W V G H.", 5),
])
def test_changed_tokens(a, b, n):
    assert d.changed_tokens(a, b) == n


def test_mechanical_checks():
    ms = "Methods. We surveyed 120 undergraduate students at one university in spring 2023."
    good = {"accurate_sentence": "The authors surveyed 120 undergraduate students at one university in 2023.",
            "false_sentence": "The authors surveyed 210 undergraduate students at one university in 2023.",
            "evidence_quote": "We surveyed 120 undergraduate students"}
    assert all(d.mechanical_checks(good, ms).values())
    bad = dict(good, false_sentence="The authors surveyed 210 students. They used a scale.", evidence_quote="We surveyed 210")
    checks = d.mechanical_checks(bad, ms)
    assert not checks["one_sentence_each"] and not checks["evidence_quote_in_manuscript"]


def test_pair_problems_enforce_counts_uniqueness_and_checks(small_plan):
    empty = _pairs(1)
    empty[0]["mechanical"] = {}
    assert any("mechanical check" in p for p in d.pair_problems(empty, small_plan))
    assert d.pair_problems(_pairs(1), small_plan) == []
    assert any("outside 1-2" in p for p in d.pair_problems(_pairs(3), small_plan))
    assert any("ms01_quant: 0" in p for p in d.pair_problems([p for p in _pairs(1) if p["fixture"] != "ms01_quant"], small_plan))
    twice = _pairs(1) + [dict(_pairs(1)[0])]
    assert any("repeated" in p for p in d.pair_problems(twice, small_plan))
    unchecked = _pairs(1)
    unchecked[0]["verify"]["no_tell"] = False
    assert any("verifier answer" in p for p in d.pair_problems(unchecked, small_plan))


# ---------- build ----------


def test_build_refuses_a_wrong_inventory_or_too_few_pairs(tmp_path, small_plan, capsys):
    _work, rc = _build(tmp_path, claims=_claims()[:-1])
    assert rc == 1 and "claims: 11 != 12" in capsys.readouterr().out
    _work, rc = _build(tmp_path / "2", pairs=[p for p in _pairs() if p["fixture"] != "ms02_qual"])
    assert rc == 1 and "ms02_qual: 0 accepted pairs" in capsys.readouterr().out


def test_build_writes_a_manifest_and_refuses_a_used_directory(tmp_path, small_plan, capsys):
    work, rc = _build(tmp_path)
    assert rc == 0
    manifest = json.loads((work / "batches" / "build_manifest.json").read_text(encoding="utf-8"))
    assert set(manifest) >= {"inputs", "snapshots", "seat_key_sha256", "item_key_sha256", "batches"}
    assert set(manifest["snapshots"]) == set(d.SNAPSHOTS)
    assert {"plan.json", "PREREGISTRATION.md", "extract_panel_claims.py"} <= {Path(k).name for k in manifest["inputs"]}
    args = type("A", (), {"claims": work / "claims" / "claims.jsonl", "pairs_dir": work / "pairs",
                          "out": work / "batches"})
    with pytest.raises(d.Stop):
        d.cmd_build(args)
    capsys.readouterr()


def test_pair_sentences_never_share_a_batch(small_plan):
    batches, key = d.build_batches(_claims(), _pairs(2))
    batch_of = {i["claim_id"]: b["batch_id"] for b in batches for i in b["items"]}
    by_pair = {}
    for k in key:
        if k["kind"].startswith("contrast"):
            by_pair.setdefault(k["pair_id"], []).append(batch_of[k["item_id"]])
    assert len(by_pair) == 6 and all(len(set(v)) == 2 for v in by_pair.values())


def test_items_have_neutral_ids_and_the_key_holds_the_kind(small_plan):
    batches, key = d.build_batches(_claims(), _pairs())
    shown = [i for b in batches for i in b["items"]]
    assert all(set(i) == {"claim_id", "text"} for i in shown)
    assert sorted(i["claim_id"] for i in shown) == [f"i{n:04d}" for n in range(1, len(shown) + 1)]
    assert [k["kind"] for k in key].count("contrast_false") == 3 and all("text" not in k for k in key)


def test_every_batch_prompt_leaves_room_for_the_retry_note(small_plan):
    batches, _key = d.build_batches(_claims(per_bundle=40, size=900), _pairs())
    assert len(batches) > 6
    for b in batches:
        first = len(d.batch_prompt(b).encode("utf-8"))
        assert first <= d.PROMPT_BUDGET
        assert first + len(d.RETRY_NOTE.format(reason="x" * 300).encode("utf-8")) <= d.PROMPT_LIMIT


def test_an_item_too_large_for_any_batch_stops_the_build(small_plan):
    claims = _claims()
    claims[0]["text"] = "x" * 28_000
    with pytest.raises(d.Stop):
        d.build_batches(claims, _pairs())


def test_a_changed_input_after_the_build_stops_the_run(tmp_path, small_plan, capsys):
    work, _rc = _build(tmp_path)
    capsys.readouterr()
    batch = work / "batches" / "b001.json"
    data = json.loads(batch.read_text(encoding="utf-8"))
    data["items"][0]["text"] = "edited"
    batch.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(d.Stop, match="prompt changed"):
        d.load_build(work / "batches")


# ---------- reading verdicts ----------


def _row(cid, **kw):
    return json.dumps({"claim_id": cid, "verdict": "true", "severity": "minor", **kw})


def test_read_verdicts_requires_the_schema_and_one_line_per_item():
    rows, problem = d.read_verdicts("\n".join([_row("i0001"), _row("i0002", verdict="not_verifiable")]),
                                    ["i0001", "i0002"])
    assert problem is None and rows["i0002"]["verdict"] == "not_verifiable"
    _rows, problem = d.read_verdicts("\n".join([_row("i0001"), _row("i0001", verdict="false")]), ["i0001"])
    assert "answered twice" in problem
    _rows, problem = d.read_verdicts(_row("i0001", severity="huge"), ["i0001"])
    assert "invalid severity" in problem
    _rows, problem = d.read_verdicts(_row("i0001", verdict="false"), ["i0001"])
    assert "invalid evidence" in problem
    _rows, problem = d.read_verdicts(_row("i0001"), ["i0001", "i0002"])
    assert problem == "1 of 2 items have no verdict line"


def test_evidence_is_checked_against_the_manuscript_and_the_claim():
    ms = "We report attrition of 12 students in Section 3."
    claim = 'The paper says "attrition was not tracked" and reports no attrition.'
    assert d.evidence_ok({"evidence": "contradiction", "quote": "attrition of 12 students"}, claim, ms)
    assert not d.evidence_ok({"evidence": "contradiction", "quote": "attrition of 21 students"}, claim, ms)
    assert d.evidence_ok({"evidence": "absent_quotation", "quote": "attrition was not tracked"}, claim, ms)
    assert not d.evidence_ok({"evidence": "absent_quotation", "quote": "attrition of 12"}, claim, ms)


@pytest.mark.parametrize("rows,flag", [
    ([None, {"verdict": "true"}], "missing"),
    ([{"verdict": "true"}, {"verdict": "not_verifiable"}], "false"),
    ([{"verdict": "false", "evidence": "absent_quotation", "quote": "zz"}] * 2, "true"),
    ([{"verdict": "false", "evidence": "absent_quotation", "quote": "zz"}, {"verdict": "true"}], "unresolved"),
    ([{"verdict": "false", "evidence": "contradiction", "quote": "not in it"}] * 2, "unresolved"),
])
def test_judge_flag(rows, flag):
    assert d.judge_flag(rows, 'claim "zz"', "manuscript text") == flag


@pytest.mark.parametrize("flags,name", [
    ({"a": "true", "b": "true"}, "agreed_false"), ({"a": "false", "b": "false"}, "agreed_not_false"),
    ({"a": "true", "b": "false"}, "cross_judge_divergence"), ({"a": "unresolved", "b": "true"}, "replicate_instability"),
    ({"a": "missing", "b": "unresolved"}, "missing"),
])
def test_classify(flags, name):
    assert d.classify(flags) == name


def test_a_missing_contrast_verdict_fails_the_gate():
    key = [{"item_id": "f", "kind": "contrast_false"}, {"item_id": "t", "kind": "contrast_accurate"}]
    full = {"f": {"verdict": "false"}, "t": {"verdict": "true"}}
    bar = {"min_detection": 0.95, "max_false_flag": 0.05}
    assert d.contrast_gate(key, [full, full], bar)["pass"]
    gate = d.contrast_gate(key, [full, {"f": {"verdict": "false"}}], bar)
    assert not gate["pass"] and gate["missing_contrast_verdicts"] == 1


# ---------- calls ----------


def _ok(cmd, input=None, **kw):
    return _reply(cmd, "answer\n")


def test_a_completed_call_is_reused_only_for_the_same_prompt(tmp_path):
    out, log = tmp_path / "x.out", tmp_path / "calls.jsonl"
    calls = []
    runner = lambda cmd, **kw: calls.append(cmd) or _ok(cmd)  # noqa: E731
    assert d.call_model("codex", "PROMPT", out, log, "c1", runner=runner) == "answer\n"
    assert d.call_model("codex", "PROMPT", out, log, "c1", runner=runner) == "answer\n"
    assert len(calls) == 1
    with pytest.raises(d.Stop, match="no completed call"):
        d.call_model("gemini", "PROMPT", out, log, "c1", runner=runner)  # another transport
    assert calls[0][:6] == ["codex", "exec", "-m", "gpt-6-astra", "-c", 'model_reasoning_effort="xhigh"']
    with pytest.raises(d.Stop, match="no completed call with this prompt"):
        d.call_model("codex", "OTHER", out, log, "c1", runner=runner)
    statuses = [e["status"] for e in d.read_jsonl(log)]
    assert statuses == ["started", "completed"] and not (tmp_path / "x.out.lock").exists()
    out.write_text("changed\n", encoding="utf-8")
    with pytest.raises(d.Stop, match="no completed call"):
        d.call_model("codex", "PROMPT", out, log, "c1", runner=runner)


def test_an_interrupted_call_stops_the_next_one(tmp_path):
    (tmp_path / "x.out.lock").write_text("", encoding="utf-8")
    with pytest.raises(d.Stop, match="interrupted"):
        d.call_model("codex", "P", tmp_path / "x.out", tmp_path / "calls.jsonl", "c1", runner=_ok)


@pytest.mark.parametrize("proc", [
    subprocess.CompletedProcess([], 1, stdout="", stderr="boom"),
    subprocess.CompletedProcess([], 0, stdout=codex_events("  \n"), stderr=""),
    subprocess.CompletedProcess([], 0, stdout='{"error": "RESOURCE_EXHAUSTED", "status": 429}\n', stderr=""),
    subprocess.CompletedProcess([], 0, stdout='{"type": "turn.started"}\n{"type": "turn.failed", "error": {}}\n',
                                stderr=""),
    subprocess.CompletedProcess([], 0, stdout=codex_events('{"claim_id": "i0001"}', [
        {"type": "command_execution", "command": "cat /etc/hosts"}]), stderr=""),
])
def test_a_transport_failure_stops_and_is_logged(tmp_path, proc):
    with pytest.raises(d.Stop, match="transport failed"):
        d.call_model("codex", "P", tmp_path / "x.out", tmp_path / "calls.jsonl", "c1", runner=lambda *a, **k: proc)
    assert [e["status"] for e in d.read_jsonl(tmp_path / "calls.jsonl")] == ["started", "failed"]
    assert not (tmp_path / "x.out").exists() and (tmp_path / "x.out.lock").exists()


def test_a_timeout_stops_and_keeps_the_partial_output(tmp_path):
    def runner(cmd, **kw):
        raise subprocess.TimeoutExpired(cmd, 1, output="half")
    with pytest.raises(d.Stop, match="TimeoutExpired"):
        d.call_model("codex", "P", tmp_path / "x.out", tmp_path / "calls.jsonl", "c1", runner=runner)
    assert (tmp_path / "x.out.partial").read_text(encoding="utf-8") == "half"


def test_an_oversized_prompt_is_never_sent(tmp_path):
    with pytest.raises(d.Stop, match="over the"):
        d.call_model("gemini", "x" * (d.PROMPT_LIMIT + 1), tmp_path / "x.out", tmp_path / "c.jsonl", "c1",
                     runner=_ok)


def test_the_agy_transport_passes_the_prompt_as_an_argument():
    cmd, stdin = d.TRANSPORTS["gemini"]("P")
    assert cmd[:2] == ["agy", "--model=Gemini 3.8 Flash (High)"] and stdin is None
    assert cmd[cmd.index("-p") + 1] == "P" and {"--disable-slash-commands", "stream-json"} <= set(cmd)


def test_an_agy_reply_that_uses_a_tool_is_a_transport_failure(tmp_path):
    tool = stream("x").replace('"agent_response", "text_delta": "x"', '"run_command"')
    proc = subprocess.CompletedProcess([], 0, stdout=tool, stderr="")
    with pytest.raises(d.Stop, match="steps other than the reply: run_command"):
        d.call_model("gemini", "P", tmp_path / "x.out", tmp_path / "calls.jsonl", "c1", runner=lambda *a, **k: proc)
    assert d.agy_answer(stream("hello")) == ("hello", None)


def test_usage_words_in_a_reply_or_on_stderr_are_not_failures(tmp_path):
    reply = '{"claim_id": "i0001", "reason": "quota sampling of 401 participants"}\n'
    proc = subprocess.CompletedProcess([], 0, stdout=codex_events(reply), stderr="rate limit 401 " + reply)
    assert d.call_model("codex", "P", tmp_path / "x.out", tmp_path / "c.jsonl", "c1",
                        runner=lambda *a, **k: proc) == reply


def test_an_empty_agy_reply_is_a_transport_failure(tmp_path):
    proc = subprocess.CompletedProcess([], 0, stdout=stream(""), stderr="")
    with pytest.raises(d.Stop, match="empty reply"):
        d.call_model("gemini", "P", tmp_path / "x.out", tmp_path / "c.jsonl", "c1", runner=lambda *a, **k: proc)


def test_no_path_under_the_manifests_directory_is_read(tmp_path):
    with pytest.raises(d.Stop, match="manifests"):
        d.read_text(d.PROTECTED / "ms01_quant.defects.json")
    with pytest.raises(d.Stop, match="manifests"):
        d.guard(d.SEEDED)


# ---------- run and score ----------


def test_run_stops_when_output_stays_unreadable(tmp_path, small_plan, capsys):
    work, _rc = _build(tmp_path)
    capsys.readouterr()
    judge = FakeJudge(honest, stdout_override="not json\n")
    with pytest.raises(d.Stop, match="unreadable after one retry"):
        d.run_judge("codex", 1, work / "batches", work / "runs", runner=judge)
    assert len(judge.calls) == 2  # the first batch and its one retry, then stop


def test_run_stops_at_a_usage_limit(tmp_path, small_plan, capsys):
    work, _rc = _build(tmp_path)
    capsys.readouterr()
    judge = FakeJudge(honest, fail_after=1)
    with pytest.raises(d.Stop, match="transport failed"):
        d.run_judge("gemini", 1, work / "batches", work / "runs", runner=judge)
    assert len(judge.calls) == 2


def _full_run(work, policies):
    for judge, policy in policies.items():
        for rep in (1, 2):
            d.run_judge(judge, rep, work / "batches", work / "runs", runner=FakeJudge(policy))


def test_score_end_to_end_keeps_the_maintainer_decisions(tmp_path, small_plan, capsys):
    work, _rc = _build(tmp_path)
    capsys.readouterr()

    def dissent(text):
        return {"verdict": "true"} if "Claim 1 of ms01_quant bundle 2" not in text else \
            {"verdict": "false", "evidence": "absent_quotation", "quote": "Claim 1 of ms01_quant bundle 2",
             "locator": "absent"}

    def mixed(text):
        return honest(text) if "finding number" in text else dissent(text) if "ms01_quant bundle 2" in text \
            else honest(text)

    _full_run(work, {"codex": honest, "gemini": mixed})
    result = d.score(work / "batches", work / "runs", work / "score")
    assert result["status"] == "decision_relevant" and result["valid_judges"] == ["codex", "gemini"]
    lists = result["lists"]
    assert len(lists["agreed_false"]) == 1 and len(lists["cross_judge_divergence"]) == 1
    assert result["headline"] == {"computed": False, "reason": "1 adjudication decisions pending"}
    decisions = json.loads((work / "score" / "adjudication_decisions.json").read_text(encoding="utf-8"))
    for item in decisions["decisions"]:
        decisions["decisions"][item].update(verdict="false", criterion="TBD")
    (work / "score" / "adjudication_decisions.json").write_text(json.dumps(decisions), encoding="utf-8")
    assert not d.score(work / "batches", work / "runs", work / "score")["headline"]["computed"]
    for item in decisions["decisions"]:
        decisions["decisions"][item]["criterion"] = "R5"
    (work / "score" / "adjudication_decisions.json").write_text(json.dumps(decisions), encoding="utf-8")
    again = d.score(work / "batches", work / "runs", work / "score", work / "claims" / "key.jsonl")
    assert again["headline"]["computed"] and again["headline"]["false_claims"] == 2
    assert sum(v["claims"] for v in again["headline"]["by_seat"].values()) == 12
    kept = json.loads((work / "score" / "adjudication_decisions.json").read_text(encoding="utf-8"))
    assert all(v["verdict"] == "false" for v in kept["decisions"].values())
    packet = (work / "score" / "adjudication_packet.md").read_text(encoding="utf-8")
    assert "codex" not in packet and "gemini" not in packet
    manifest = json.loads((work / "score" / "execution_manifest.json").read_text(encoding="utf-8"))
    assert manifest["schema_version"] == "heldout-execution-manifest/1.0"
    assert len(manifest["calls"]) == 4 * 6 + 3 + 3  # judges, then the generator and verifier calls
    attempts = json.loads((work / "score" / "call_attempts.json").read_text(encoding="utf-8"))["attempts"]
    assert {e["log"] for e in attempts} == {"pairs", "codex/r1", "codex/r2", "gemini/r1", "gemini/r2"}


def test_a_judge_that_fails_the_gate_is_left_out(tmp_path, small_plan, capsys):
    work, _rc = _build(tmp_path)
    capsys.readouterr()

    def blind(text):
        return {"verdict": "true"}

    _full_run(work, {"codex": honest, "gemini": blind})
    result = d.score(work / "batches", work / "runs", work / "score")
    assert result["valid_judges"] == ["codex"] and result["status"] == "exploratory_one_valid_judge"
    assert not result["contrast_gate"]["gemini"]["pass"]
    assert result["headline"] == {"computed": False, "reason": "exploratory_one_valid_judge"}
    assert len(result["lists"]["agreed_false"]) == 1  # codex alone, no gemini vote counted


# ---------- the frozen files ----------


def test_the_prompts_and_plan_agree_with_the_script():
    plan = d.load_plan()
    assert plan["judges"] == ["codex", "gemini"] and plan["prompt_budget_bytes"] == d.PROMPT_BUDGET
    assert plan["prompt_limit_bytes"] == d.PROMPT_LIMIT
    auditor = (d.SUITE / "prompts" / "auditor.md").read_text(encoding="utf-8")
    assert all(v in auditor for v in d.VERDICTS + d.SEVERITIES + d.EVIDENCE)
    assert "{manuscript}" in auditor and "{claims}" in auditor
    verify = (d.SUITE / "prompts" / "contrast_verify.md").read_text(encoding="utf-8")
    assert all(q in verify for q in d.PAIR_QUESTIONS) and "{pairs}" in verify
    assert set(d.FIXTURE_FILES.values()) <= {p.name for p in d.MANUSCRIPTS.glob("*.md")}


# ---------- round-2 review regressions ----------


def test_score_refuses_an_output_that_its_log_does_not_match(tmp_path, small_plan, capsys):
    work, _rc = _build(tmp_path)
    capsys.readouterr()
    _full_run(work, {"codex": honest, "gemini": honest})
    (work / "runs" / "codex" / "r1" / "b001.a1.out").write_text(_row("i0001") + "\n", encoding="utf-8")
    with pytest.raises(d.Stop, match="no completed call"):
        d.score(work / "batches", work / "runs", work / "score")


def test_decisions_from_another_build_or_claim_text_stop(tmp_path, small_plan, capsys):
    work, _rc = _build(tmp_path)
    capsys.readouterr()
    _full_run(work, {"codex": honest, "gemini": honest})
    score_dir = work / "score"
    d.score(work / "batches", work / "runs", score_dir)
    path = score_dir / "adjudication_decisions.json"
    good = json.loads(path.read_text(encoding="utf-8"))
    path.write_text(json.dumps({**good, "build_manifest_sha256": "0" * 64}), encoding="utf-8")
    with pytest.raises(d.Stop, match="another build"):
        d.score(work / "batches", work / "runs", score_dir)
    item = next(k["item_id"] for k in d.read_jsonl(work / "batches" / "item_key.jsonl") if k["kind"] == "claim")
    good["decisions"][item] = {"text_sha256": "0" * 64, "verdict": "true", "criterion": "V2"}
    path.write_text(json.dumps(good), encoding="utf-8")
    with pytest.raises(d.Stop, match="another claim text"):
        d.score(work / "batches", work / "runs", score_dir)


def test_a_seat_key_that_is_not_the_built_one_stops(tmp_path, small_plan, capsys):
    work, _rc = _build(tmp_path)
    capsys.readouterr()
    _full_run(work, {"codex": honest, "gemini": honest})
    other = work / "other_key.jsonl"
    rows = d.read_jsonl(work / "claims" / "key.jsonl")
    d.write_jsonl(other, [dict(r, seat="domain") for r in rows])
    with pytest.raises(d.Stop, match="seat key"):
        d.score(work / "batches", work / "runs", work / "score", other)


def test_a_changed_snapshot_stops_the_run(tmp_path, small_plan, capsys):
    work, _rc = _build(tmp_path)
    capsys.readouterr()
    with (work / "batches" / "accepted_pairs.jsonl").open("a", encoding="utf-8") as f:
        f.write("{}\n")
    with pytest.raises(d.Stop, match="accepted_pairs.jsonl changed"):
        d.load_build(work / "batches")


def test_the_inventory_counts_distinct_bundles_not_the_summary(small_plan):
    claims = [dict(c, bundle=c["bundle"].replace("bundle2", "bundle1")) for c in _claims()]
    found = d.inventory_problems(claims, {"bundles": 6, "claims": 12, "problems": []}, small_plan)
    assert any(p.startswith("bundles: 3 in the claims") for p in found)
    mixed = _claims()
    mixed[0]["fixture"] = "ms02_qual"
    found = d.inventory_problems(mixed, {"bundles": 6, "claims": 12, "problems": []}, small_plan)
    assert any("more than one fixture" in p for p in found)


def test_wrongly_typed_fields_are_problems_not_crashes():
    text = "\n".join([json.dumps({"claim_id": ["i0001"], "verdict": "true", "severity": "minor"}),
                      json.dumps({"claim_id": "i0002", "verdict": "false", "severity": "minor",
                                  "evidence": "contradiction", "quote": 7, "locator": "s1"})])
    _rows, problem = d.read_verdicts(text, ["i0001", "i0002"])
    assert "i0002 has an invalid quote" in problem


def test_a_repeated_verifier_answer_rejects_the_pair(tmp_path, small_plan, capsys):
    def twice(fpairs):
        rows = [json.dumps({"pair_id": p["pair_id"], **CHECKED}) for p in fpairs]
        return "\n".join(rows + rows[:1]) + "\n"
    work, rc = _build(tmp_path, pairs=_pairs(2), answers=twice)
    assert rc == 0  # one of two pairs per manuscript is left, inside the 1-2 range
    kept = d.read_jsonl(work / "batches" / "accepted_pairs.jsonl")
    assert len(kept) == 3 and all(p["pair_id"].endswith("p01") for p in kept)
    capsys.readouterr()


def test_a_second_sentence_that_starts_with_a_digit_is_caught():
    assert not d._one_sentence("The study enrolled 120 participants. 80 completed the follow-up assessment.")
    assert not d._one_sentence('The authors wrote "we stopped." Then they resumed the study in May.')
    assert d._one_sentence("The authors report an alpha of 0.82 for the scale.")


def test_pairs_verified_through_another_transport_stop_the_build(tmp_path, small_plan, capsys):
    with pytest.raises(d.Stop, match="verify-ms00_clean"):
        _build(tmp_path, verifier="gemini")
    capsys.readouterr()


def test_the_plan_names_the_models_the_script_calls():
    plan = d.load_plan()
    gemini = d.TRANSPORTS["gemini"]("P")[0]
    assert f"--model={plan['judge_models']['gemini']['agy_model']}" in gemini
    generator = d.TRANSPORTS[plan["contrast_pairs"]["generator"]["transport"]]("P")[0]
    assert f"--model={plan['contrast_pairs']['generator']['agy_model']}" in generator
    assert plan["contrast_pairs"]["verifier"]["transport"] == "codex"
    assert plan["judge_models"]["codex"]["model_id"] in d.TRANSPORTS["codex"]("P")[0]


def test_an_interrupted_judge_call_stops_scoring(tmp_path, small_plan, capsys):
    work, _rc = _build(tmp_path)
    capsys.readouterr()
    _full_run(work, {"codex": honest, "gemini": honest})
    r1 = work / "runs" / "codex" / "r1"
    (r1 / "b002.a1.out").unlink()
    (r1 / "b002.a1.out.lock").write_text("", encoding="utf-8")
    with (r1 / "calls.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps({"call_id": "codex-r1-b002-a1", "status": "started", "started_at": "x"}) + "\n")
    with pytest.raises(d.Stop, match="interrupted"):
        d.score(work / "batches", work / "runs", work / "score")


def test_a_batch_file_holding_another_batch_stops(tmp_path, small_plan, capsys):
    work, _rc = _build(tmp_path)
    capsys.readouterr()
    b = work / "batches"
    (b / "b001.json").write_text((b / "b002.json").read_text(encoding="utf-8"), encoding="utf-8")
    with pytest.raises(d.Stop, match="b001.json holds batch b002"):
        d.load_build(b)


def test_abbreviations_are_not_sentence_ends():
    assert d._one_sentence("The study enrolled 120 participants from the U.S. population.")
    assert d._one_sentence("Smith et al. Report a mean of 4.2 in the second wave of the survey.")


def test_a_crlf_reply_reads_back_with_its_logged_hash(tmp_path):
    proc = subprocess.CompletedProcess([], 0, stdout=codex_events("line one\r\nline two\r\n"), stderr="")
    out, log = tmp_path / "x.out", tmp_path / "c.jsonl"
    first = d.call_model("codex", "P", out, log, "c1", runner=lambda *a, **k: proc)
    assert first == "line one\nline two\n"
    assert d.call_model("codex", "P", out, log, "c1", runner=lambda *a, **k: proc) == first


def test_a_completed_call_whose_output_is_gone_stops(tmp_path):
    out, log = tmp_path / "x.out", tmp_path / "c.jsonl"
    d.call_model("codex", "P", out, log, "c1", runner=_ok)
    out.unlink()
    with pytest.raises(d.Stop, match="lost its output"):
        d.call_model("codex", "P", out, log, "c1", runner=_ok)


def test_a_lone_letter_before_a_period_still_ends_a_sentence():
    assert not d._one_sentence("The authors enrolled 120 participants in group A. The controls received saline.")
