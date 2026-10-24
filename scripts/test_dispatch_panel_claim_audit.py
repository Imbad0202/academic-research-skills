#!/usr/bin/env python3
"""Tests for scripts/dispatch_panel_claim_audit.py (#1002). No model call:
transports are replaced by a fake runner, and claims and pairs are synthetic."""
from __future__ import annotations

import copy
import json
import os
import re
import subprocess
import sys
import time
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


def gemini_body(text, finish="STOP", parts=None, version="gemini-4-argon"):
    """A generateContent response body for a reply, with a thought part."""
    parts = [{"text": "thinking", "thought": True}, {"text": text, "thoughtSignature": "sig"}] \
        if parts is None else parts
    return json.dumps({"candidates": [{"content": {"role": "model", "parts": parts}, "finishReason": finish}],
                       "modelVersion": version, "usageMetadata": {"promptTokenCount": 1, "totalTokenCount": 2}})


def claude_events(text, blocks=None, extra=(), result=None):
    """claude -p stream-json output for a reply."""
    blocks = [{"type": "text", "text": text}] if blocks is None else blocks
    events = [{"type": "system", "subtype": "init"}, *extra,
              {"type": "assistant", "uuid": "u1", "message": {"content": blocks}},
              result or {"type": "result", "subtype": "success", "is_error": False}]
    return "\n".join(json.dumps(e) for e in events) + "\n"


def _reply(cmd, text):
    if cmd[0] == "claude":
        out = claude_events(text)
    elif cmd[0] == "agy":
        out = stream(text)
    elif "gemini-api-call" in cmd:
        out = gemini_body(text)
    else:
        out = codex_events(text)
    return subprocess.CompletedProcess(cmd, 0, stdout=out, stderr="")


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


def _build(tmp_path, claims=None, pairs=None, plan=None, match_manifest=None, **pair_kw):
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
    args = type("A", (), {"claims": work / "claims" / "claims.jsonl", "pairs_dir": pdir, "out": work / "batches",
                          "match_manifest": match_manifest})
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
    cmd, stdin = d.TRANSPORTS["claude_agy"]("P")
    assert cmd[:2] == ["agy", "--model=Claude Opus 5.5 (High)"] and stdin is None
    assert cmd[cmd.index("-p") + 1] == "P" and {"--disable-slash-commands", "stream-json"} <= set(cmd)


def test_the_gemini_transport_runs_the_api_helper_with_the_prompt_on_stdin():
    cmd, stdin = d.TRANSPORTS["gemini"]("P")
    assert cmd[1:] == ["-I", str(Path(d.__file__).resolve()), "gemini-api-call"] and stdin == "P"
    body = d.gemini_api_request("P")
    assert body["contents"] == [{"role": "user", "parts": [{"text": "P"}]}]
    assert set(body) == {"contents", "generationConfig"}  # no tools, no system instruction
    assert body["generationConfig"] == {"thinkingConfig": {"thinkingLevel": "medium"}, "maxOutputTokens": 32768}


@pytest.mark.parametrize("body,problem", [
    (gemini_body("x", finish="MAX_TOKENS"), "finish reason MAX_TOKENS"),
    (gemini_body("x", finish="SAFETY"), "finish reason SAFETY"),
    (gemini_body("x", parts=[{"functionCall": {"name": "f"}}]), "parts other than the reply: functionCall"),
    (gemini_body("x", version="gemini-3.8-flash"), "model version"),
    ('{"error": {"code": 429, "status": "RESOURCE_EXHAUSTED"}}', "API error RESOURCE_EXHAUSTED"),
    ('{"candidates": [], "modelVersion": "gemini-4-argon"}', "0 candidates"),
    ("not json", "unreadable API response"),
])
def test_a_gemini_reply_that_is_not_a_plain_answer_is_a_transport_failure(tmp_path, body, problem):
    assert d.gemini_api_answer(body)[1].startswith(problem)
    proc = subprocess.CompletedProcess([], 0, stdout=body, stderr="")
    with pytest.raises(d.Stop, match="transport failed"):
        d.call_model("gemini", "P", tmp_path / "x.out", tmp_path / "calls.jsonl", "c1", runner=lambda *a, **k: proc)


def test_a_gemini_reply_leaves_out_thought_parts():
    assert d.gemini_api_answer(gemini_body("answer")) == ("answer", None)


def test_the_gemini_helper_needs_the_key_and_never_calls_without_it(monkeypatch, capsys):
    monkeypatch.delenv(d.GEMINI_API_KEY_ENV, raising=False)
    monkeypatch.setattr(d.urllib.request, "urlopen", lambda *a, **k: pytest.fail("called without a key"))
    assert d.main(["gemini-api-call"]) == 3
    assert d.GEMINI_API_KEY_ENV in capsys.readouterr().err


def test_an_agy_reply_that_uses_a_tool_is_a_transport_failure(tmp_path):
    tool = stream("x").replace('"agent_response", "text_delta": "x"', '"run_command"')
    proc = subprocess.CompletedProcess([], 0, stdout=tool, stderr="")
    with pytest.raises(d.Stop, match="steps other than the reply: run_command"):
        d.call_model("claude_agy", "P", tmp_path / "x.out", tmp_path / "calls.jsonl", "c1",
                     runner=lambda *a, **k: proc)
    assert d.agy_answer(stream("hello")) == ("hello", None)


def test_usage_words_in_a_reply_or_on_stderr_are_not_failures(tmp_path):
    reply = '{"claim_id": "i0001", "reason": "quota sampling of 401 participants"}\n'
    proc = subprocess.CompletedProcess([], 0, stdout=codex_events(reply), stderr="rate limit 401 " + reply)
    assert d.call_model("codex", "P", tmp_path / "x.out", tmp_path / "c.jsonl", "c1",
                        runner=lambda *a, **k: proc) == reply


def test_an_empty_agy_reply_is_a_transport_failure(tmp_path):
    proc = subprocess.CompletedProcess([], 0, stdout=stream(""), stderr="")
    with pytest.raises(d.Stop, match="empty reply"):
        d.call_model("claude_agy", "P", tmp_path / "x.out", tmp_path / "c.jsonl", "c1", runner=lambda *a, **k: proc)


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
        d.run_judge("gemini", 1, work / "batches", work / "runs", runner=judge, cap_usd=50)
    assert len(judge.calls) == 2


def _full_run(work, policies):
    for judge, policy in policies.items():
        for rep in (1, 2):
            d.run_judge(judge, rep, work / "batches", work / "runs", runner=FakeJudge(policy), cap_usd=50)


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
    assert plan["judge_models"]["gemini"]["api_model"] == d.GEMINI_API_MODEL
    assert "gemini-api-call" in d.TRANSPORTS["gemini"]("P")[0]
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


def test_initials_pass_the_script_and_the_verifier_checks_single_sentences():
    assert d._one_sentence("The study by A. Smith enrolled 120 participants at one university.")
    assert "single_sentences" in d.PAIR_QUESTIONS
    assert "single_sentences" in (d.SUITE / "prompts" / "contrast_verify.md").read_text(encoding="utf-8")


def test_events_split_on_lf_only_and_unreadable_lines_fail():
    tool = {"type": "command_execution", "command": "printf 'a\u2028b'"}
    events = [{"type": "turn.started"}, {"type": "item.completed", "item": tool},
              {"type": "item.completed", "item": {"type": "agent_message", "text": "OK"}},
              {"type": "turn.completed"}]
    stream = "\n".join(json.dumps(e, ensure_ascii=False) for e in events)
    assert d.codex_answer(stream) == ("", "items other than the reply: command_execution")
    assert d.codex_answer(stream + "\nnot json")[1] == "1 unreadable event lines"
    assert d.codex_answer(codex_events("a\u2028b")) == ("a\u2028b", None)


def test_a_non_ascii_initial_is_not_a_sentence_end():
    assert d._one_sentence("The study by É. Durkheim enrolled 120 participants at one university.")


def test_jsonl_with_u2028_reads_back(tmp_path):
    rows = [{"pair_id": "p01\u2028x", "text": "a"}, {"pair_id": "p02", "text": "b"}]
    d.write_jsonl(tmp_path / "x.jsonl", rows)
    assert d.read_jsonl(tmp_path / "x.jsonl") == rows


# ---------- plan v4: the paid Gemini API judge ----------


def test_the_paid_judge_needs_a_cap_and_stops_before_a_call_over_it(tmp_path, small_plan, capsys):
    work, _rc = _build(tmp_path)
    capsys.readouterr()
    judge = FakeJudge(honest)
    with pytest.raises(d.Stop, match="--cap-usd"):
        d.run_judge("gemini", 1, work / "batches", work / "runs", runner=judge)
    with pytest.raises(d.Stop, match="budget_exhausted"):
        d.run_judge("gemini", 1, work / "batches", work / "runs", runner=judge, cap_usd=0.01)
    assert judge.calls == []  # stopped before any call
    one_call = d.worst_case_usd(d.batch_prompt(d.load_build(work / "batches")[0][0]))

    def unpriced(cmd, **kw):  # a reply without usage: the run counts it at its worst case
        reply = judge(cmd, **kw)
        body = json.loads(reply.stdout)
        del body["usageMetadata"]
        return subprocess.CompletedProcess(cmd, 0, stdout=json.dumps(body), stderr="")
    with pytest.raises(d.Stop, match="budget_exhausted"):
        d.run_judge("gemini", 1, work / "batches", work / "runs", runner=unpriced, cap_usd=one_call * 1.5)
    assert len(judge.calls) == 1


def test_gemini_cost_is_logged_from_usage_and_thinking_counts_as_output(tmp_path):
    body = json.dumps({"candidates": [{"content": {"parts": [{"text": "a"}]}, "finishReason": "STOP"}],
                       "modelVersion": "gemini-4-argon",
                       "usageMetadata": {"promptTokenCount": 1000, "candidatesTokenCount": 100,
                                         "thoughtsTokenCount": 900, "totalTokenCount": 2000}})
    proc = subprocess.CompletedProcess([], 0, stdout=body, stderr="")
    log = tmp_path / "gemini" / "r1" / "calls.jsonl"
    d.call_model("gemini", "P", log.parent / "x.out", log, "c1", runner=lambda *a, **k: proc)
    done = d.read_jsonl(log)[-1]
    assert done["transport"] == "gemini_api" and done["tokens_out"] == 1000
    assert done["usd"] == pytest.approx(1000 * 2e-6 + 1000 * 10e-6)
    assert d.gemini_spent(tmp_path) == pytest.approx(done["usd"])


def test_a_logged_agy_gemini_call_is_not_reused_by_the_api_judge(tmp_path):
    out, log = tmp_path / "x.out", tmp_path / "calls.jsonl"
    out.write_text("answer\n", encoding="utf-8")
    d._log(log, {"call_id": "c1", "sequence_index": 1, "status": "completed", "transport": "gemini",
                 "prompt_sha256": d._sha("P"), "output_sha256": d._sha("answer\n")})
    with pytest.raises(d.Stop, match="no completed call"):
        d.completed_output(log, "c1", out, "P", "gemini")
    d._log(log, {"call_id": "c2", "sequence_index": 2, "status": "completed", "transport": "codex",
                 "prompt_sha256": d._sha("P"), "output_sha256": d._sha("answer\n")})
    assert d.completed_output(log, "c2", out, "P", "codex") == "answer\n"


def test_only_the_gemini_helper_gets_the_key(tmp_path, monkeypatch):
    monkeypatch.setenv(d.GEMINI_API_KEY_ENV, "k")
    seen = {}

    def runner(cmd, **kw):
        seen[cmd[0]] = kw["env"]
        return _reply(cmd, "answer\n")
    d.call_model("codex", "P", tmp_path / "a.out", tmp_path / "c.jsonl", "c1", runner=runner)
    d.call_model("gemini", "P", tmp_path / "b.out", tmp_path / "c.jsonl", "c2", runner=runner)
    assert d.GEMINI_API_KEY_ENV not in seen["codex"] and seen[sys.executable][d.GEMINI_API_KEY_ENV] == "k"


@pytest.mark.parametrize("body,problem", [
    (json.dumps({"error": "bad gateway"}), "API error"),
    (json.dumps({"candidates": "x", "modelVersion": "gemini-4-argon"}), "no candidates"),
    (json.dumps({"candidates": ["x"], "modelVersion": "gemini-4-argon"}), "unreadable candidate"),
    (gemini_body("x", parts=[{"text": "a"}, {"text": 123}]), "a reply part without text"),
    (gemini_body("x", parts=[{"text": "a"}, {"thoughtSignature": "s"}]), "a reply part without text"),
    (gemini_body("x", parts="nope"), "unreadable reply parts"),
    (gemini_body("x", version="gemini-4-argon-001"), "model version"),
])
def test_malformed_gemini_bodies_are_problems_not_crashes(body, problem):
    assert d.gemini_api_answer(body)[1].startswith(problem)


class _Response:
    def __init__(self, body, status=200):
        self.body, self.status = body, status

    def read(self, size=-1):
        return self.body if size is None or size < 0 else self.body[:size]

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class _Opener:
    def __init__(self, result):
        self.result, self.requests = result, []

    def open(self, request, timeout):
        self.requests.append(request)
        if isinstance(self.result, Exception):
            raise self.result
        return self.result


def _helper(monkeypatch, opener, key="KEY123", prompt="Prompt é"):
    monkeypatch.setenv(d.GEMINI_API_KEY_ENV, key)
    out = type("B", (), {"buffer": __import__("io").BytesIO()})()
    monkeypatch.setattr(d.sys, "stdin", type("S", (), {"buffer": __import__("io").BytesIO(prompt.encode())})())
    monkeypatch.setattr(d.sys, "stdout", out)
    return d.cmd_gemini_api_call(None, opener=opener), out.buffer.getvalue()


def test_the_helper_sends_the_key_only_in_the_header(monkeypatch):
    opener = _Opener(_Response(b'{"ok": 1}'))
    rc, out = _helper(monkeypatch, opener)
    req = opener.requests[0]
    assert rc == 0 and out == b'{"ok": 1}'
    assert req.full_url == d.GEMINI_API_URL.format(model="gemini-4-argon") and "KEY123" not in req.full_url
    assert req.get_header("X-goog-api-key") == "KEY123" and b"KEY123" not in req.data
    assert json.loads(req.data)["contents"][0]["parts"][0]["text"] == "Prompt é"


def test_the_helper_prints_no_body_unless_http_200(monkeypatch, capsys):
    assert _helper(monkeypatch, _Opener(_Response(b'{"e": "KEY123"}', status=203))) == (1, b"")
    err = d.urllib.error.HTTPError("u", 429, "x", {}, __import__("io").BytesIO(b'{"e": "K\\u0045Y123"}'))
    assert _helper(monkeypatch, _Opener(err)) == (1, b"")
    assert capsys.readouterr().err.splitlines()[-1] == "HTTP 429"
    rc, _out = _helper(monkeypatch, _Opener(ValueError("Invalid header value KEY123")))
    assert rc == 1 and "KEY123" not in capsys.readouterr().err


def test_the_helper_refuses_a_key_a_header_cannot_carry(monkeypatch, capsys):
    opener = _Opener(_Response(b"{}"))
    assert _helper(monkeypatch, opener, key="KEY123\n")[0] == 3 and opener.requests == []
    assert "KEY123" not in capsys.readouterr().err


def test_the_helper_does_not_follow_redirects():
    handler = d._NoRedirect()
    assert handler.redirect_request(None, None, 302, "Found", {}, "https://elsewhere.example/") is None


def test_build_can_require_the_batches_of_an_earlier_build(tmp_path, small_plan, capsys):
    work, rc = _build(tmp_path)
    assert rc == 0
    manifest = work / "batches" / "build_manifest.json"
    again, rc = _build(tmp_path / "again", match_manifest=manifest)
    assert rc == 0
    changed = json.loads(manifest.read_text(encoding="utf-8"))
    changed["batches"][sorted(changed["batches"])[0]] = "0" * 64
    (tmp_path / "m.json").write_text(json.dumps(changed), encoding="utf-8")
    third, rc = _build(tmp_path / "third", match_manifest=tmp_path / "m.json")
    assert rc == 1 and "differ" in capsys.readouterr().out and not (third / "batches").exists()


# ---------- plan v4, round 2 ----------


@pytest.mark.parametrize("cap", [None, 0, -1, float("nan"), float("inf"), 100.01])
def test_a_cap_outside_the_plan_never_reaches_a_call(tmp_path, small_plan, capsys, cap):
    work, _rc = _build(tmp_path)
    capsys.readouterr()
    judge = FakeJudge(honest)
    with pytest.raises(d.Stop, match="--cap-usd"):
        d.run_judge("gemini", 1, work / "batches", work / "runs", runner=judge, cap_usd=cap)
    assert judge.calls == []


def test_a_second_paid_run_on_the_same_runs_directory_stops(tmp_path, small_plan, capsys):
    work, _rc = _build(tmp_path)
    capsys.readouterr()
    (work / "runs" / "gemini").mkdir(parents=True)
    (work / "runs" / "gemini" / "run.lock").write_text("", encoding="utf-8")
    judge = FakeJudge(honest)
    with pytest.raises(d.Stop, match="another gemini run"):
        d.run_judge("gemini", 2, work / "batches", work / "runs", runner=judge, cap_usd=50)
    assert judge.calls == []
    (work / "runs" / "gemini" / "run.lock").unlink()
    d.run_judge("gemini", 2, work / "batches", work / "runs", runner=judge, cap_usd=50, limit=1)
    assert not (work / "runs" / "gemini" / "run.lock").exists()  # released after the run


def test_the_price_date_is_checked_before_each_new_paid_call_only(tmp_path, small_plan, capsys, monkeypatch):
    work, _rc = _build(tmp_path)
    capsys.readouterr()
    judge = FakeJudge(honest)
    d.run_judge("gemini", 1, work / "batches", work / "runs", runner=judge, cap_usd=50, limit=1)
    monkeypatch.setattr(d, "_now", lambda: "2026-12-01T00:00:00+00:00")
    d.run_judge("gemini", 1, work / "batches", work / "runs", runner=judge, cap_usd=50, limit=1)  # reuse only
    with pytest.raises(d.Stop, match="price table"):
        d.run_judge("gemini", 1, work / "batches", work / "runs", runner=judge, cap_usd=50, limit=2)
    assert len(judge.calls) == 1


@pytest.mark.parametrize("meta", [
    {}, {"promptTokenCount": 10}, {"promptTokenCount": 10, "candidatesTokenCount": 5},
    {"promptTokenCount": "bad", "totalTokenCount": 20}, {"promptTokenCount": -5, "totalTokenCount": 20},
    {"promptTokenCount": 30, "totalTokenCount": 20}, {"promptTokenCount": True, "totalTokenCount": 20},
    {"promptTokenCount": 10, "totalTokenCount": 10 ** 309},
])
def test_usage_that_cannot_be_priced_counts_at_the_worst_case(meta):
    assert d.gemini_usage(json.dumps({"usageMetadata": meta}), 0, 0) == {"usd": None}


def test_output_cost_is_total_minus_prompt():
    usage = d.gemini_usage(json.dumps({"usageMetadata": {"promptTokenCount": 10, "totalTokenCount": 210}}), 40, 800)
    assert usage["tokens_out"] == 200 and usage["usd"] == pytest.approx(10 * 2e-6 + 200 * 10e-6)


def test_the_price_date_is_checked_inside_a_run(tmp_path, small_plan, capsys, monkeypatch):
    work, _rc = _build(tmp_path)
    capsys.readouterr()
    judge = FakeJudge(honest)

    def runner(cmd, **kw):  # the date passes the price table after the first call
        monkeypatch.setattr(d, "_now", lambda: "2026-12-01T00:00:00+00:00")
        return judge(cmd, **kw)
    with pytest.raises(d.Stop, match="price table"):
        d.run_judge("gemini", 1, work / "batches", work / "runs", runner=runner, cap_usd=50, limit=2)
    assert len(judge.calls) == 1


def test_an_http_error_whose_body_cannot_be_read_still_fails_cleanly(monkeypatch, capsys):
    class Broken(__import__("io").BytesIO):
        def read(self, *a):
            raise ValueError("chunk KEY123")
    err = d.urllib.error.HTTPError("u", 429, "x", {}, Broken())
    rc, out = _helper(monkeypatch, _Opener(err))
    assert rc == 1 and out == b"" and "KEY123" not in capsys.readouterr().err


# ---------- plan v5: one resend after the output limit ----------


class MaxTokensFirst:
    """A Gemini judge whose listed calls spend the whole output limit."""

    def __init__(self, fail_calls):
        self.inner, self.fail_calls, self.n = FakeJudge(honest), set(fail_calls), 0

    def __call__(self, cmd, **kw):
        self.n += 1
        if self.n in self.fail_calls:
            body = json.loads(gemini_body("", finish="MAX_TOKENS", parts=[]))
            body["usageMetadata"] = {"promptTokenCount": 1, "totalTokenCount": 32769}  # the limit, spent
            return subprocess.CompletedProcess(cmd, 0, stdout=json.dumps(body), stderr="")
        return self.inner(cmd, **kw)


def test_a_max_tokens_call_is_sent_once_more_and_scored_from_the_resend(tmp_path, small_plan, capsys):
    work, _rc = _build(tmp_path)
    capsys.readouterr()
    judge = MaxTokensFirst({1})
    d.run_judge("gemini", 1, work / "batches", work / "runs", runner=judge, cap_usd=50, limit=1)
    assert judge.n == 2
    log = work / "runs" / "gemini" / "r1" / "calls.jsonl"
    assert [(e["call_id"], e["status"]) for e in d.read_jsonl(log) if e["status"] != "started"] == [
        ("gemini-r1-b001-a1", "failed"), ("gemini-r1-b001-a1-r", "completed")]
    batches, _key = d.load_build(work / "batches")
    assert d.load_replicate(work / "runs", "gemini", 1, batches[:1])


def test_a_second_max_tokens_stops_and_is_never_sent_a_third_time(tmp_path, small_plan, capsys):
    work, _rc = _build(tmp_path)
    capsys.readouterr()
    judge = MaxTokensFirst({1, 2})
    with pytest.raises(d.Stop, match="transport failed"):
        d.run_judge("gemini", 1, work / "batches", work / "runs", runner=judge, cap_usd=50, limit=1)
    with pytest.raises(d.Stop, match="the one resend"):
        d.run_judge("gemini", 1, work / "batches", work / "runs", runner=judge, cap_usd=50, limit=1)
    assert judge.n == 2


def test_other_failures_get_no_resend(tmp_path, small_plan, capsys):
    work, _rc = _build(tmp_path)
    capsys.readouterr()
    calls = []

    def safety(cmd, **kw):
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, stdout=gemini_body("x", finish="SAFETY"), stderr="")
    with pytest.raises(d.Stop, match="SAFETY"):
        d.run_judge("gemini", 1, work / "batches", work / "runs", runner=safety, cap_usd=50, limit=1)
    assert len(calls) == 1


def test_a_resumed_run_goes_to_the_resend_not_a_fresh_first_attempt(tmp_path, small_plan, capsys):
    work, _rc = _build(tmp_path)
    capsys.readouterr()
    one_call = d.worst_case_usd(d.batch_prompt(d.load_build(work / "batches")[0][0]))
    judge = MaxTokensFirst({1})
    with pytest.raises(d.Stop, match="budget_exhausted"):  # the failed call's cost leaves no room
        d.run_judge("gemini", 1, work / "batches", work / "runs", runner=judge, cap_usd=one_call * 1.2, limit=1)
    d.run_judge("gemini", 1, work / "batches", work / "runs", runner=judge, cap_usd=50, limit=1)
    log = work / "runs" / "gemini" / "r1" / "calls.jsonl"
    ids = [e["call_id"] for e in d.read_jsonl(log) if e["status"] == "started"]
    assert ids == ["gemini-r1-b001-a1", "gemini-r1-b001-a1-r"]


def test_a_max_tokens_reply_with_a_forbidden_part_stops_without_a_resend(tmp_path, small_plan, capsys):
    work, _rc = _build(tmp_path)
    capsys.readouterr()
    calls = []

    def tool(cmd, **kw):
        calls.append(cmd)
        body = gemini_body("", finish="MAX_TOKENS", parts=[{"text": ""}, {"functionCall": {"name": "f"}}])
        return subprocess.CompletedProcess(cmd, 0, stdout=body, stderr="")
    with pytest.raises(d.Stop, match="functionCall"):
        d.run_judge("gemini", 1, work / "batches", work / "runs", runner=tool, cap_usd=50, limit=1)
    assert len(calls) == 1


def test_a_max_tokens_failure_with_another_prompt_is_not_resent(tmp_path):
    log = tmp_path / "calls.jsonl"
    d._log(log, {"call_id": "c1", "sequence_index": 1, "status": "failed", "transport": "gemini_api",
                 "prompt_sha256": d._sha("OLD"), "error": d.MAX_TOKENS_FAILURE})
    assert d.failed_resendable(log, "c1", "OLD") and not d.failed_resendable(log, "c1", "NEW")
    d._log(log, {"call_id": "c2", "sequence_index": 2, "status": "failed", "transport": "gemini",
                 "prompt_sha256": d._sha("OLD"), "error": d.MAX_TOKENS_FAILURE})
    assert not d.failed_resendable(log, "c2", "OLD")  # an agy-era record


def test_a_format_retry_that_hits_max_tokens_is_resent_and_scored(tmp_path, small_plan, capsys):
    work, _rc = _build(tmp_path)
    capsys.readouterr()
    good = FakeJudge(honest)
    n = {"calls": 0}
    prompts = []

    def runner(cmd, input=None, **kw):
        n["calls"] += 1
        prompts.append(input)
        if n["calls"] == 1:  # a1: unreadable
            return _reply(cmd, "not json\n")
        if n["calls"] == 2:  # a2: the output limit
            body = json.loads(gemini_body("", finish="MAX_TOKENS", parts=[{"text": ""}]))
            return subprocess.CompletedProcess(cmd, 0, stdout=json.dumps(body), stderr="")
        return good(cmd, input=input, **kw)
    d.run_judge("gemini", 1, work / "batches", work / "runs", runner=runner, cap_usd=50, limit=1)
    assert n["calls"] == 3 and prompts[1] == prompts[2] and prompts[1] != prompts[0]
    log = work / "runs" / "gemini" / "r1" / "calls.jsonl"
    assert [e["call_id"] for e in d.read_jsonl(log) if e["status"] == "completed"] == [
        "gemini-r1-b001-a1", "gemini-r1-b001-a2-r"]
    batches, _key = d.load_build(work / "batches")
    ids = [i["claim_id"] for i in batches[0]["items"]]
    assert set(d.load_replicate(work / "runs", "gemini", 1, batches[:1])) == set(ids)
    d.run_judge("gemini", 1, work / "batches", work / "runs", runner=runner, cap_usd=50, limit=1)
    assert n["calls"] == 3  # a resumed run adds no call


def test_a_partial_answer_cut_by_max_tokens_is_resent_too():
    body = gemini_body("half an answer", finish="MAX_TOKENS", parts=[{"text": "half an answer"}])
    assert d.gemini_api_answer(body)[1] == d.MAX_TOKENS_FAILURE


def test_a_resume_stops_on_a_first_output_with_no_completed_call(tmp_path, small_plan, capsys):
    work, _rc = _build(tmp_path)
    capsys.readouterr()
    one_call = d.worst_case_usd(d.batch_prompt(d.load_build(work / "batches")[0][0]))
    judge = MaxTokensFirst({1})
    with pytest.raises(d.Stop, match="budget_exhausted"):
        d.run_judge("gemini", 1, work / "batches", work / "runs", runner=judge, cap_usd=one_call * 1.2, limit=1)
    (work / "runs" / "gemini" / "r1" / "b001.a1.out").write_text("copied in\n", encoding="utf-8")
    with pytest.raises(d.Stop, match="no completed call"):
        d.run_judge("gemini", 1, work / "batches", work / "runs", runner=judge, cap_usd=50, limit=1)
    assert judge.n == 1


@pytest.mark.parametrize("candidate", [
    {"finishReason": "MAX_TOKENS"}, {"finishReason": "MAX_TOKENS", "content": {"role": "model"}}])
def test_a_max_tokens_reply_without_content_is_resent_too(candidate):
    body = json.dumps({"candidates": [candidate], "modelVersion": "gemini-4-argon"})
    assert d.gemini_api_answer(body)[1] == d.MAX_TOKENS_FAILURE
    stop = json.dumps({"candidates": [{"finishReason": "STOP"}], "modelVersion": "gemini-4-argon"})
    assert d.gemini_api_answer(stop)[1] == "unreadable reply parts"


def test_a_malformed_response_is_resent_once_and_safety_is_not_resendable(tmp_path, small_plan, capsys):
    work, _rc = _build(tmp_path)
    capsys.readouterr()
    good, n = FakeJudge(honest), {"calls": 0}

    def runner(cmd, **kw):
        n["calls"] += 1
        if n["calls"] == 1:
            body = json.dumps({"candidates": [{"finishReason": "MALFORMED_RESPONSE", "index": 0,
                                               "content": {"parts": [{"text": "", "thoughtSignature": "s"}]}}],
                               "modelVersion": "gemini-4-argon",
                               "usageMetadata": {"promptTokenCount": 10, "totalTokenCount": 10}})
            return subprocess.CompletedProcess(cmd, 0, stdout=body, stderr="")
        return good(cmd, **kw)
    d.run_judge("gemini", 1, work / "batches", work / "runs", runner=runner, cap_usd=50, limit=1)
    log = work / "runs" / "gemini" / "r1" / "calls.jsonl"
    assert [e["call_id"] for e in d.read_jsonl(log) if e["status"] == "completed"] == ["gemini-r1-b001-a1-r"]
    assert d.gemini_api_answer(json.dumps({"candidates": [{"finishReason": "MALFORMED_RESPONSE"}],
                                           "modelVersion": "gemini-4-argon"}))[1] == "finish reason MALFORMED_RESPONSE"
    assert "finish reason SAFETY" not in d.RESEND_FAILURES


def test_a_second_malformed_response_names_its_reason_and_stops(tmp_path, small_plan, capsys):
    work, _rc = _build(tmp_path)
    capsys.readouterr()

    def runner(cmd, **kw):
        body = json.dumps({"candidates": [{"finishReason": "MALFORMED_RESPONSE"}], "modelVersion": "gemini-4-argon"})
        return subprocess.CompletedProcess(cmd, 0, stdout=body, stderr="")
    with pytest.raises(d.Stop):
        d.run_judge("gemini", 1, work / "batches", work / "runs", runner=runner, cap_usd=50, limit=1)
    with pytest.raises(d.Stop, match="the one resend after finish reason MALFORMED_RESPONSE failed"):
        d.run_judge("gemini", 1, work / "batches", work / "runs", runner=runner, cap_usd=50, limit=1)


def test_a_resumed_run_names_both_failure_reasons(tmp_path, small_plan, capsys):
    work, _rc = _build(tmp_path)
    capsys.readouterr()
    n = {"calls": 0}

    def runner(cmd, **kw):
        n["calls"] += 1
        reason = "MALFORMED_RESPONSE" if n["calls"] == 1 else "MAX_TOKENS"
        body = json.dumps({"candidates": [{"finishReason": reason}], "modelVersion": "gemini-4-argon"})
        return subprocess.CompletedProcess(cmd, 0, stdout=body, stderr="")
    with pytest.raises(d.Stop, match="MAX_TOKENS"):
        d.run_judge("gemini", 1, work / "batches", work / "runs", runner=runner, cap_usd=50, limit=1)
    with pytest.raises(d.Stop, match=r"after finish reason MALFORMED_RESPONSE failed \(finish reason MAX_TOKENS\)"):
        d.run_judge("gemini", 1, work / "batches", work / "runs", runner=runner, cap_usd=50, limit=1)
    assert n["calls"] == 2


def test_a_malformed_response_with_a_forbidden_part_stops_without_a_resend(tmp_path, small_plan, capsys):
    work, _rc = _build(tmp_path)
    capsys.readouterr()
    calls = []

    def runner(cmd, **kw):
        calls.append(cmd)
        body = gemini_body("", finish="MALFORMED_RESPONSE", parts=[{"functionCall": {"name": "f"}}])
        return subprocess.CompletedProcess(cmd, 0, stdout=body, stderr="")
    with pytest.raises(d.Stop, match="functionCall"):
        d.run_judge("gemini", 1, work / "batches", work / "runs", runner=runner, cap_usd=50, limit=1)
    assert len(calls) == 1


# ---------- security review round 1 (#1002) ----------


def test_zero_output_usage_counts_at_the_worst_case():
    for meta in ({"promptTokenCount": 0, "totalTokenCount": 0}, {"promptTokenCount": 7000, "totalTokenCount": 7000}):
        assert d.gemini_usage(json.dumps({"usageMetadata": meta}), 0, 0) == {"usd": None}


def test_a_failed_paid_call_counts_at_its_worst_case_whatever_it_reports(tmp_path):
    body = json.loads(gemini_body("", finish="MAX_TOKENS", parts=[]))
    body["usageMetadata"] = {"promptTokenCount": 1, "totalTokenCount": 2}  # under-reported

    def runner(cmd, **kw):
        return subprocess.CompletedProcess(cmd, 0, stdout=json.dumps(body), stderr="")
    log = tmp_path / "gemini" / "r1" / "calls.jsonl"
    log.parent.mkdir(parents=True)
    with pytest.raises(d.Stop):
        d.call_model("gemini", "P", log.parent / "b.out", log, "c1", runner=runner)
    failed = [e for e in d.read_jsonl(log) if e["status"] == "failed"][0]
    assert failed["usd"] is None and failed["reported_usd"] is not None
    assert d.gemini_spent(tmp_path) == pytest.approx(d.worst_case_usd("P"))


def test_the_helper_refuses_an_oversized_body(monkeypatch, capsys):
    monkeypatch.setattr(d, "RESPONSE_MAX_BYTES", 10)
    rc, out = _helper(monkeypatch, _Opener(_Response(b"x" * 11)))
    assert rc == 1 and out == b"" and "over 10 bytes" in capsys.readouterr().err


def test_the_helper_checks_the_price_date(monkeypatch, capsys):
    monkeypatch.setattr(d, "_now", lambda: "2026-12-01T00:00:00+00:00")
    opener = _Opener(_Response(b"{}"))
    rc, _out = _helper(monkeypatch, opener)
    assert rc == 3 and opener.requests == [] and "price table" in capsys.readouterr().err


def test_an_oversized_stream_saves_nothing(tmp_path, monkeypatch):
    monkeypatch.setattr(d, "STREAM_MAX_CHARS", 5)

    def runner(cmd, **kw):
        return subprocess.CompletedProcess(cmd, 0, stdout="x" * 6, stderr="")
    with pytest.raises(d.Stop, match="stream over 5"):
        d.call_model("codex", "P", tmp_path / "a.out", tmp_path / "c.jsonl", "c1", runner=runner)
    assert sorted(p.name for p in tmp_path.iterdir()) == ["a.out.lock", "c.jsonl"]


@pytest.mark.parametrize("batch_id,ok", [("b001", True), ("b1040", True), ("../x", False),
                                         ("/tmp/panel-escape", False), ("b001/../../x", False), ("b01", False)])
def test_batch_ids_are_file_name_stems(batch_id, ok):
    assert bool(d.BATCH_ID_RE.fullmatch(batch_id)) is ok


def test_side_files_do_not_follow_a_symlink(tmp_path):
    target = tmp_path / "target.txt"
    target.write_text("keep", encoding="utf-8")
    link = tmp_path / "b001.a1.out.stream"
    link.symlink_to(target)
    with pytest.raises(OSError):
        d._write_aux(link, "overwrite")
    assert target.read_text(encoding="utf-8") == "keep"


@pytest.mark.parametrize("status", ["X\n\u001b[2J", "fake STOP: all good", 7, None])
def test_an_unexpected_api_error_status_is_not_echoed(status):
    _text, problem = d.gemini_api_answer(json.dumps({"error": {"status": status}}))
    assert problem == "API error (unrecognized status)"


def test_a_known_api_error_status_is_named():
    assert d.gemini_api_answer(json.dumps({"error": {"status": "RESOURCE_EXHAUSTED"}}))[1] == \
        "API error RESOURCE_EXHAUSTED"


@pytest.mark.parametrize("role", ["generator", "verifier"])
def test_the_pair_steps_never_use_the_paid_gemini_api(role):
    plan = {"contrast_pairs": {"generator": {"transport": "codex"}, "verifier": {"transport": "codex"}}}
    plan["contrast_pairs"][role]["transport"] = "gemini"
    with pytest.raises(d.Stop, match="paid Gemini API"):
        d._pair_transport(plan, role)



# ---------- security review round 2 (#1002) ----------


@pytest.mark.parametrize("prompt_bytes,reply_bytes,trusted", [
    (5000, 400, True), (16 * 1000, 400, True), (16 * 1000 + 1, 400, False), (5000, 16 * 200 + 1, False)])
def test_reported_usage_below_its_floor_counts_at_the_worst_case(prompt_bytes, reply_bytes, trusted):
    body = json.dumps({"usageMetadata": {"promptTokenCount": 1000, "totalTokenCount": 1200}})
    assert (d.gemini_usage(body, prompt_bytes, reply_bytes)["usd"] is not None) is trusted


def test_a_successful_call_that_under_reports_counts_at_its_worst_case(tmp_path):
    body = json.loads(gemini_body("a reply long enough to need more than one output token"))
    body["usageMetadata"] = {"promptTokenCount": 1, "totalTokenCount": 2}
    prompt = "P" * 5000
    log = tmp_path / "gemini" / "r1" / "calls.jsonl"
    log.parent.mkdir(parents=True)
    d.call_model("gemini", prompt, log.parent / "b.out", log,
                 "c1", runner=lambda cmd, **kw: subprocess.CompletedProcess(cmd, 0, stdout=json.dumps(body), stderr=""))
    assert d.gemini_spent(tmp_path) == pytest.approx(d.worst_case_usd(prompt))


def test_a_logged_failure_counts_at_its_worst_case_even_with_a_usd(tmp_path):
    log = tmp_path / "gemini" / "r1" / "calls.jsonl"
    log.parent.mkdir(parents=True)
    log.write_text(json.dumps({"call_id": "c1", "sequence_index": 1, "status": "failed",
                               "usd": 0.0001, "worst_case_usd": 0.5}) + "\n", encoding="utf-8")
    assert d.gemini_spent(tmp_path) == pytest.approx(0.5)


def test_bounded_run_returns_the_streams(tmp_path):
    proc = d.bounded_run([sys.executable, "-c", "import sys; print(sys.stdin.read().upper()); "
                          "print('e', file=sys.stderr)"], input="hi", cwd=str(tmp_path), env=dict(os.environ),
                         timeout=30)
    assert (proc.returncode, proc.stdout, proc.stderr) == (0, "HI\n", "e\n")


@pytest.mark.parametrize("stream", ["stdout", "stderr"])
def test_bounded_run_stops_a_runaway_stream(tmp_path, stream):
    code = f"import sys\nwhile True: sys.{stream}.write('x' * 65536); sys.{stream}.flush()"
    with pytest.raises(d.StreamOverflow):
        d.bounded_run([sys.executable, "-c", code], input=None, cwd=str(tmp_path), env=dict(os.environ),
                      timeout=30, limit=1_000_000)


def test_bounded_run_times_out(tmp_path):
    with pytest.raises(subprocess.TimeoutExpired):
        d.bounded_run([sys.executable, "-c", "import time; time.sleep(30)"], input=None, cwd=str(tmp_path),
                      env=dict(os.environ), timeout=1)


def test_an_overflowing_stream_saves_nothing(tmp_path):
    def runner(cmd, **kw):
        raise d.StreamOverflow
    with pytest.raises(d.Stop, match="stream over"):
        d.call_model("codex", "P", tmp_path / "a.out", tmp_path / "c.jsonl", "c1", runner=runner)
    assert sorted(p.name for p in tmp_path.iterdir()) == ["a.out.lock", "c.jsonl"]


def test_the_helper_does_not_forward_an_http_200_error_body(monkeypatch, capsys):
    body = json.dumps({"error": {"status": "INVALID_ARGUMENT", "message": "key KEY123 echoed"}}).encode()
    rc, out = _helper(monkeypatch, _Opener(_Response(body)))
    err = capsys.readouterr().err
    assert rc == 1 and out == b"" and "API error INVALID_ARGUMENT" in err and "KEY123" not in err


def test_finish_reasons_and_part_keys_are_not_echoed_raw():
    text, problem = d.gemini_api_answer(gemini_body("x", finish="X\n\u001b[2J"))
    assert problem == "finish reason (unrecognized)"
    text, problem = d.gemini_api_answer(gemini_body("x", parts=[{"text": "x", "k\u001b[2J": 1}]))
    assert problem == "parts other than the reply: (unrecognized key)"
    assert d.gemini_api_answer(gemini_body("x", finish="MAX_TOKENS"))[1] in d.RESEND_FAILURES


def test_stop_messages_reach_the_terminal_escaped(monkeypatch, capsys):
    def boom(_args):
        raise d.Stop("bad\n\u001b[2Jfake line")
    monkeypatch.setattr(d, "cmd_score", boom)
    assert d.main(["score", "--batches", "b", "--runs", "r", "--out", "o"]) == 2
    err = capsys.readouterr().err
    assert "\u001b" not in err and err.count("\n") == 1 and "\\x1b" in err


def test_side_files_refuse_a_symlink_without_o_nofollow(tmp_path, monkeypatch):
    target = tmp_path / "target.txt"
    target.write_text("keep", encoding="utf-8")
    link = tmp_path / "b001.a1.out.err"
    link.symlink_to(target)
    monkeypatch.delattr(d.os, "O_NOFOLLOW")
    with pytest.raises(d.Stop, match="symlink"):
        d._write_aux(link, "overwrite")
    assert target.read_text(encoding="utf-8") == "keep"


# ---------- security review round 3 (#1002) ----------


def test_bounded_run_times_out_when_the_process_never_reads_its_input(tmp_path):
    started = time.monotonic()
    with pytest.raises(subprocess.TimeoutExpired):
        d.bounded_run([sys.executable, "-c", "import time; time.sleep(30)"], input="x" * 4_000_000,
                      cwd=str(tmp_path), env=dict(os.environ), timeout=1)
    assert time.monotonic() - started < 15


# ---------- transport runner, second approach (#1002) ----------


def _gone(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return True
    return False


def _wait_gone(pid: int) -> bool:
    for _ in range(100):
        if _gone(pid):
            return True
        time.sleep(0.05)
    return False


SPAWN = ("import subprocess, sys; p = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)']); "
         "open(sys.argv[1], 'w').write(str(p.pid))")


def test_bounded_run_kills_a_child_left_behind_after_a_clean_exit(tmp_path):
    pid_file = tmp_path / "pid"
    proc = d.bounded_run([sys.executable, "-c", SPAWN, str(pid_file)], input=None, cwd=str(tmp_path),
                         env=dict(os.environ), timeout=30)
    assert proc.returncode == 0
    assert _wait_gone(int(pid_file.read_text()))


def test_bounded_run_kills_the_group_on_ctrl_c(tmp_path):
    import signal
    import threading
    pid_file = tmp_path / "pid"
    code = SPAWN + "; import time; time.sleep(60)"
    timer = threading.Timer(1.5, lambda: os.kill(os.getpid(), signal.SIGINT))
    timer.start()
    try:
        with pytest.raises(KeyboardInterrupt):
            d.bounded_run([sys.executable, "-c", code, str(pid_file)], input=None, cwd=str(tmp_path),
                          env=dict(os.environ), timeout=30)
    finally:
        timer.cancel()
    assert _wait_gone(int(pid_file.read_text()))


def test_bounded_run_feeds_a_large_input_from_a_file(tmp_path):
    proc = d.bounded_run([sys.executable, "-c", "import sys; print(len(sys.stdin.read()))"],
                         input="x" * 4_000_000, cwd=str(tmp_path), env=dict(os.environ), timeout=30)
    assert proc.stdout.strip() == "4000000"


def test_bounded_run_refuses_a_non_posix_system(tmp_path, monkeypatch):
    monkeypatch.setattr(d.os, "name", "nt")
    with pytest.raises(d.Stop, match="POSIX"):
        d.bounded_run(["true"], input=None, cwd=str(tmp_path), env={}, timeout=1)


def test_an_over_long_pair_skips_the_token_diff(monkeypatch):
    monkeypatch.setattr(d, "changed_tokens", lambda a, b: pytest.fail("diff ran on an over-long pair"))
    checks = d.mechanical_checks({"accurate_sentence": "word " * 20000, "false_sentence": "word " * 20001,
                                  "evidence_quote": "x"}, "x")
    assert checks["word_counts_8_to_50"] is False and checks["changed_tokens_1_to_4"] is False


def test_output_files_do_not_follow_a_symlink(tmp_path):
    target = tmp_path / "target.json"
    target.write_text("keep", encoding="utf-8")
    (tmp_path / "out").mkdir()
    (tmp_path / "out" / "rows.jsonl").symlink_to(target)
    with pytest.raises(OSError):
        d.write_jsonl(tmp_path / "out" / "rows.jsonl", [{"a": 1}])
    log = tmp_path / "out" / "calls.jsonl"
    log.symlink_to(target)
    with pytest.raises(OSError):
        d._log(log, {"a": 1})
    assert target.read_text(encoding="utf-8") == "keep"


def test_the_transport_starts_with_sigint_unblocked(tmp_path):
    code = "import signal; print(signal.SIGINT in signal.pthread_sigmask(signal.SIG_BLOCK, set()))"
    proc = d.bounded_run([sys.executable, "-c", code], input=None, cwd=str(tmp_path), env=dict(os.environ),
                         timeout=30)
    assert proc.stdout.strip() == "False"
    import signal
    assert signal.SIGINT not in signal.pthread_sigmask(signal.SIG_BLOCK, set())


def test_output_bytes_are_written_unchanged_and_not_through_a_symlink(tmp_path):
    d._write_aux(tmp_path / "a.bin", b"\x00\xffraw")
    assert (tmp_path / "a.bin").read_bytes() == b"\x00\xffraw"
    (tmp_path / "b.bin").symlink_to(tmp_path / "a.bin")
    with pytest.raises(OSError):
        d._write_aux(tmp_path / "b.bin", b"x")


@pytest.mark.parametrize("limit", ["0", "-1"])
def test_a_limit_below_one_is_refused(limit, capsys):
    with pytest.raises(SystemExit):
        d.main(["run", "--judge", "codex", "--replicate", "1", "--batches", "b", "--out", "o", "--limit", limit])
    with pytest.raises(d.Stop, match="at least 1"):
        d.run_judge("codex", 1, Path("b"), Path("o"), limit=int(limit))


def test_a_ctrl_c_to_the_main_thread_kills_the_group_first(tmp_path):
    import signal
    import threading
    pid_file = tmp_path / "pid"
    code = SPAWN + "; import time; time.sleep(60)"
    main = threading.main_thread().ident
    timer = threading.Timer(1.5, lambda: signal.pthread_kill(main, signal.SIGINT))
    timer.start()
    try:
        with pytest.raises(KeyboardInterrupt):
            d.bounded_run([sys.executable, "-c", code, str(pid_file)], input=None, cwd=str(tmp_path),
                          env=dict(os.environ), timeout=30)
    finally:
        timer.cancel()
    assert _wait_gone(int(pid_file.read_text()))
    assert signal.SIGINT not in signal.pthread_sigmask(signal.SIG_BLOCK, set())


# ---------- plan v10: the Claude contrast-only judges ----------


@pytest.fixture
def claude_token(tmp_path, monkeypatch):
    token = tmp_path / "oauth_token"
    token.write_text("tok-123\n", encoding="utf-8")
    monkeypatch.setattr(d, "CLAUDE_TOKEN_FILE", token)
    return token


def test_the_claude_transport_is_fenced():
    for judge, model in d.CLAUDE_JUDGES.items():
        cmd, stdin = d.TRANSPORTS[judge]("PROMPT")
        assert cmd[:4] == ["claude", "-p", "--model", model] and stdin == "PROMPT"
        assert "--bare" not in cmd and "PROMPT" not in cmd
        assert cmd[cmd.index("--tools") + 1] == "" and "--strict-mcp-config" in cmd
        assert cmd[cmd.index("--output-format") + 1] == "stream-json"


@pytest.mark.parametrize("stream_text,answer,problem", [
    (claude_events("hi\n"), "hi\n", None),
    (claude_events("", blocks=[{"type": "tool_use", "name": "Read"}]), "", "a tool use"),
    (claude_events("x", result={"type": "result", "subtype": "error_during_execution", "is_error": True}),
     "", "not exactly one successful result event"),
    (claude_events("x", result={"type": "result", "subtype": "success", "is_error": True}),
     "", "not exactly one successful result event"),
    ("not json\n" + claude_events("x"), "", "1 unreadable event lines"),
    (claude_events("x", extra=[{"type": "result", "subtype": "error_during_execution", "is_error": True}]),
     "", "not exactly one successful result event"),
    (claude_events("x") + json.dumps({"type": "result", "subtype": "success", "is_error": False}) + "\n",
     "", "not exactly one successful result event"),
])
def test_claude_answer(stream_text, answer, problem):
    assert d.claude_answer(stream_text) == (answer, problem)


def test_claude_answer_drops_superseded_and_retracted_messages():
    events = [{"type": "assistant", "uuid": "a", "message": {"content": [{"type": "text", "text": "old "}]}},
              {"type": "assistant", "uuid": "b", "supersedes": ["a"],
               "message": {"content": [{"type": "text", "text": "new "}]}},
              {"type": "assistant", "uuid": "c", "message": {"content": [{"type": "text", "text": "refused"}]}},
              {"type": "system", "subtype": "model_refusal_fallback", "retracted_message_uuids": ["c"]},
              {"type": "assistant", "uuid": "e", "message": {"content": [{"type": "text", "text": "end"}]}},
              {"type": "result", "subtype": "success", "is_error": False}]
    assert d.claude_answer("\n".join(json.dumps(e) for e in events)) == ("new end", None)


def test_a_claude_call_gets_only_the_allowlisted_environment(tmp_path, claude_token, monkeypatch):
    monkeypatch.setenv("CLAUDECODE", "1")
    monkeypatch.setenv(d.GEMINI_API_KEY_ENV, "secret")
    monkeypatch.setenv("LANG", "C")
    seen = {}

    def runner(cmd, input=None, env=None, cwd=None, **kw):
        seen.update(env=env, cwd=cwd, config=Path(env["CLAUDE_CONFIG_DIR"]))
        assert not any(seen["config"].iterdir())  # an empty configuration directory
        return _reply(cmd, "answer\n")

    out, log = tmp_path / "x.out", tmp_path / "calls.jsonl"
    assert d.call_model("claude_opus", "PROMPT", out, log, "c1", runner=runner) == "answer\n"
    env = seen["env"]
    assert set(env) <= set(d.CLAUDE_ENV_KEEP) | {"CLAUDE_CONFIG_DIR", "CLAUDE_CODE_OAUTH_TOKEN"}
    assert env["CLAUDE_CODE_OAUTH_TOKEN"] == "tok-123" and env["LANG"] == "C"
    assert "CLAUDECODE" not in env and d.GEMINI_API_KEY_ENV not in env
    assert not seen["config"].exists() and not Path(seen["cwd"]).exists()
    assert "tok-123" not in log.read_text(encoding="utf-8")
    assert not any("tok-123" in f.read_text(encoding="utf-8") for f in tmp_path.glob("x.out*"))


def test_a_claude_call_without_a_token_stops_before_the_lock(tmp_path, monkeypatch):
    monkeypatch.setattr(d, "CLAUDE_TOKEN_FILE", tmp_path / "missing")
    out, log = tmp_path / "x.out", tmp_path / "calls.jsonl"
    with pytest.raises(d.Stop, match="no Claude OAuth token"):
        d.call_model("claude_fable", "PROMPT", out, log, "c1", runner=_ok)
    assert not log.exists() and not list(tmp_path.glob("*.lock"))


@pytest.mark.parametrize("marker", ["CLAUDE.md", ".claude", ".git", None])
def test_a_claude_call_stops_before_the_lock_when_the_temp_folder_is_not_fenced(tmp_path, claude_token,
                                                                                monkeypatch, marker):
    base = tmp_path / "proj" / "tmp"
    base.mkdir(parents=True)
    if marker:
        (tmp_path / "proj" / marker).mkdir()
        monkeypatch.setattr(d.Path, "home", classmethod(lambda cls: Path("/nonexistent-home")))
    else:  # under $HOME
        monkeypatch.setattr(d.Path, "home", classmethod(lambda cls: tmp_path))
    monkeypatch.setattr(d.tempfile, "gettempdir", lambda: str(base))
    out, log = tmp_path / "x.out", tmp_path / "calls.jsonl"
    with pytest.raises(d.Stop, match="TMPDIR"):
        d.call_model("claude_opus", "PROMPT", out, log, "c1", runner=_ok)
    assert not log.exists() and not list(tmp_path.glob("*.lock"))


def test_a_claude_call_runs_in_a_new_folder_under_the_checked_base(tmp_path, claude_token):
    seen = {}
    d.call_model("claude_opus", "PROMPT", tmp_path / "x.out", tmp_path / "calls.jsonl", "c1",
                 runner=lambda cmd, cwd=None, **kw: seen.update(cwd=cwd) or _ok(cmd))
    assert Path(seen["cwd"]).parent == d._claude_workdir_base()


def test_contrast_batches_leave_out_batches_of_claims_only():
    key = [{"item_id": "i0001", "kind": "claim"}, {"item_id": "i0002", "kind": "contrast_false"},
           {"item_id": "i0003", "kind": "claim"}, {"item_id": "i0004", "kind": "contrast_accurate"}]
    batches = [{"batch_id": "b001", "items": [{"claim_id": "i0001"}, {"claim_id": "i0002"}]},
               {"batch_id": "b002", "items": [{"claim_id": "i0003"}]},
               {"batch_id": "b003", "items": [{"claim_id": "i0004"}]}]
    assert [b["batch_id"] for b in d.contrast_batches(batches, key)] == ["b001", "b003"]


def test_contrast_only_is_for_the_claude_judges_and_they_need_it(tmp_path, small_plan, capsys):
    work, _rc = _build(tmp_path)
    capsys.readouterr()
    with pytest.raises(d.Stop, match="contrast-only"):
        d.run_judge("claude_opus", 1, work / "batches", work / "runs", runner=FakeJudge(honest))
    with pytest.raises(d.Stop, match="contrast-only"):
        d.run_judge("codex", 1, work / "batches", work / "runs", runner=FakeJudge(honest), contrast_only=True)


def test_the_claude_judges_read_only_the_contrast_batches_and_are_gated(tmp_path, small_plan, claude_token,
                                                                        capsys):
    work, _rc = _build(tmp_path)
    capsys.readouterr()
    batches, key = d.load_build(work / "batches")
    wanted = d.contrast_batches(batches, key)
    assert 0 < len(wanted) <= len(batches)
    contrast = {k["item_id"] for k in key if k["kind"] != "claim"}
    assert all(any(i["claim_id"] in contrast for i in b["items"]) for b in wanted)

    def blind(text):
        return {"verdict": "true"}

    for judge, policy in (("claude_opus", honest), ("claude_fable", blind)):
        for rep in (1, 2):
            fake = FakeJudge(policy)
            d.run_judge(judge, rep, work / "batches", work / "runs", runner=fake, contrast_only=True)
            assert len(fake.calls) == len(wanted)
    gates = d.contrast_score(work / "batches", work / "runs", ["claude_opus", "claude_fable"])
    assert gates["claude_opus"]["pass"] and gates["claude_opus"]["missing_contrast_verdicts"] == 0
    assert not gates["claude_fable"]["pass"] and gates["claude_fable"]["detected"] == 0
    assert d.main(["contrast-score", "--batches", str(work / "batches"), "--runs", str(work / "runs"),
                   "--judge", "claude_opus"]) == 0
    assert json.loads(capsys.readouterr().out)["claude_opus"]["pass"]


def test_the_plan_names_the_claude_contrast_judges():
    plan = d.load_plan()
    named = plan["contrast_only_judges"]
    assert {j: named[j]["model_id"] for j in d.CLAUDE_JUDGES} == d.CLAUDE_JUDGES
    assert plan["amendments"][-1]["version"] == plan["plan_version"] == "10"
