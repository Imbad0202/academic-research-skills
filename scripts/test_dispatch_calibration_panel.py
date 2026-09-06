"""Mutation tests for dispatch_calibration_panel.py (#653). Offline via ScriptedTransport."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import dispatch_calibration_panel as mod
from _calibration_pdf_text import TEXT_NORMALIZATION, pdf_facts

pypdf = pytest.importorskip("pypdf")

ANALYSIS = """# Field Analysis

## Reviewer Configuration Cards

### Card #1: EIC
eic config

### Card #2: Methodology
methodology config

### Card #3: Domain
domain config

### Card #4: Perspective
perspective config

## Review Strategy Recommendations
panel-wide notes that must never reach a seat
"""

SEAT_REPORT = "## Review\n\nfindings\n\nWeighted Average: 61.0\n"
SYNTHESIS = "# Part 1\n\n### Decision: [Major Revision]\n\n# Part 2\nroadmap\n"


def make_pdf(path: Path, pages: int = 1) -> None:
    writer = pypdf.PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(width=200, height=200)
    with path.open("wb") as handle:
        writer.write(handle)


def pdf_hashes(path: Path) -> tuple[str, str]:
    pdf_sha, text_sha, _, _ = pdf_facts(path)
    return pdf_sha, text_sha


@pytest.fixture()
def env(tmp_path):
    corpus_dir = tmp_path / "suite"
    (corpus_dir / "corpus").mkdir(parents=True)
    (corpus_dir / "manifests").mkdir()
    pdf_cache = tmp_path / "pdfs"
    pdf_cache.mkdir()
    make_pdf(pdf_cache / "p1.pdf")
    pdf_sha, text_sha = pdf_hashes(pdf_cache / "p1.pdf")
    (corpus_dir / "corpus" / "papers.json").write_text(
        json.dumps(
            {
                "suite": "reviewer_calibration",
                "extraction": {
                    "tool": "pypdf",
                    "pypdf_version": pypdf.__version__,
                    "text_normalization": TEXT_NORMALIZATION,
                },
                "papers": [
                    {
                        "paper_id": "p1",
                        "title": "T",
                        "pdf_url": "https://openreview.net/pdf?id=p1",
                        "pdf_sha256": pdf_sha,
                        "extracted_text_sha256": text_sha,
                        "page_count": 1,
                        "retrieved_at": "2026-08-07T00:00:00Z",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    (corpus_dir / "manifests" / "gold_labels.json").write_text("{}", encoding="utf-8")
    work = tmp_path / "work"
    return {"corpus": corpus_dir, "cache": pdf_cache, "work": work}


def base_argv(env, stage, replicate=1):
    return [
        "--stage", stage, "--paper", "p1", "--replicate", str(replicate),
        "--corpus-dir", str(env["corpus"]), "--pdf-cache", str(env["cache"]),
        "--work-dir", str(env["work"]), "--date", "2026-08-07",
        "--generated-at", "2026-08-07T00:00:00Z", "--attempt-id", "attempt-1",
        "--transport", "scripted",
    ]


def scripted(tmp_path, responses):
    path = tmp_path / "responses.json"
    path.write_text(json.dumps(responses), encoding="utf-8")
    return ["--scripted-responses", str(path)]


def run_cards(env, tmp_path, analysis=ANALYSIS):
    return mod.main(
        base_argv(env, "cards") + scripted(tmp_path, {"field_analyst": [analysis]})
    )


def panel_responses():
    return {
        "seat-eic": [SEAT_REPORT],
        "seat-methodology": [SEAT_REPORT],
        "seat-domain": [SEAT_REPORT],
        "seat-perspective": [SEAT_REPORT],
        "seat-da": ["## DA Review\n\nchallenges\n"],
        "synthesis": [SYNTHESIS],
    }


def test_cards_stage_freezes_four_cards(env, tmp_path):
    assert run_cards(env, tmp_path) == 0
    cards_dir = env["work"] / "cards" / "p1"
    for index, expected in ((1, "eic config"), (2, "methodology config"),
                            (3, "domain config"), (4, "perspective config")):
        text = (cards_dir / f"card{index}.md").read_text()
        assert expected in text
        assert "panel-wide notes" not in text
    frozen = json.loads((cards_dir / "frozen.json").read_text())
    assert frozen["paper_id"] == "p1"


def test_cards_stage_refuses_missing_card(env, tmp_path):
    truncated = ANALYSIS.replace("### Card #4: Perspective\nperspective config\n", "")
    assert run_cards(env, tmp_path, analysis=truncated) == 1
    blocked = json.loads((env["work"] / "runs" / "blocked-cards-p1.json").read_text())
    assert "Card #4" in blocked["abort_reason"]
    assert [c["outcome"] for c in blocked["calls"]] == ["completed"]
    assert not (env["work"] / "cards" / "p1" / "frozen.json").exists()
    assert not (env["work"] / "cards" / "p1" / "card1.md").exists()


def test_panel_complete_record_and_raw(env, tmp_path):
    assert run_cards(env, tmp_path) == 0
    assert mod.main(base_argv(env, "panel") + scripted(tmp_path, panel_responses())) == 0
    record = json.loads((env["work"] / "runs" / "2026-08-07-p1-r1.json").read_text())
    assert record["status"] == "complete"
    assert record["substrate_plan"] == "primary_only"
    assert record["suite"] == "reviewer_calibration"
    assert len(record["completed_calls"]) == 6
    raw = env["work"] / "runs" / "2026-08-07-p1-r1" / "raw"
    assert (raw / "synthesis.md").read_text() == SYNTHESIS
    assert (raw / "seat-da.md").is_file()


def test_panel_without_frozen_cards_aborts(env, tmp_path):
    rc = mod.main(base_argv(env, "panel") + scripted(tmp_path, panel_responses()))
    assert rc == 1
    blocked = json.loads((env["work"] / "runs" / "blocked-2026-08-07-p1-r1.json").read_text())
    assert blocked["status"] == "aborted"
    assert "Card #1" in blocked["abort_reason"]


def test_panel_missing_response_emits_blocked_record(env, tmp_path):
    assert run_cards(env, tmp_path) == 0
    responses = panel_responses()
    responses.pop("synthesis")
    rc = mod.main(base_argv(env, "panel") + scripted(tmp_path, responses))
    assert rc == 1
    blocked = json.loads((env["work"] / "runs" / "blocked-2026-08-07-p1-r1.json").read_text())
    assert blocked["status"] == "aborted"
    assert "seat-da" in blocked["completed_calls"]


def test_synthesizer_never_sees_manuscript(env, tmp_path, monkeypatch):
    transports = []
    real_build = mod.build_transport

    def capture(args):
        transport = real_build(args)
        transports.append(transport)
        return transport

    monkeypatch.setattr(mod, "build_transport", capture)
    assert run_cards(env, tmp_path) == 0
    assert mod.main(base_argv(env, "panel") + scripted(tmp_path, panel_responses())) == 0
    seen = {call.label: call for transport in transports for call, _ in transport.calls}
    synthesis_call = seen["synthesis"]
    assert f"<{mod.MANUSCRIPT_TAG}>" not in synthesis_call.user
    assert not synthesis_call.paper_visible
    for seat in mod.SEATS:
        assert f"<{mod.MANUSCRIPT_TAG}>" in seen[f"seat-{seat}"].user


def test_gold_labels_never_on_read_path(env, tmp_path, monkeypatch):
    """Mutation guard: dispatching a full panel never opens gold_labels.json."""
    labels = env["corpus"] / "manifests" / "gold_labels.json"
    opened = []
    real_read_text = Path.read_text

    def spy(self, *a, **kw):
        if self.name == "gold_labels.json":
            opened.append(self)
        return real_read_text(self, *a, **kw)

    monkeypatch.setattr(Path, "read_text", spy)
    assert run_cards(env, tmp_path) == 0
    assert mod.main(base_argv(env, "panel") + scripted(tmp_path, panel_responses())) == 0
    assert opened == []
    assert labels.is_file()


def test_replicate_cannot_overwrite_existing_evidence(env, tmp_path):
    assert run_cards(env, tmp_path) == 0
    assert mod.main(base_argv(env, "panel") + scripted(tmp_path, panel_responses())) == 0
    with pytest.raises(mod.PreconditionFailure, match="already holds content"):
        mod.main(base_argv(env, "panel") + scripted(tmp_path, panel_responses()))


def test_pdf_hash_mismatch_refused(env, tmp_path):
    make_pdf(env["cache"] / "p1.pdf", pages=2)  # overwrite: different doc
    with pytest.raises(mod.PreconditionFailure, match="pdf_sha256 mismatch"):
        run_cards(env, tmp_path)


def test_symlink_in_pdf_cache_refused(env, tmp_path):
    os.symlink(
        env["corpus"] / "manifests" / "gold_labels.json", env["cache"] / "labels.json"
    )
    with pytest.raises(mod.PreconditionFailure, match="symlink"):
        run_cards(env, tmp_path)


def test_work_dir_inside_repo_refused(env, tmp_path, monkeypatch):
    monkeypatch.setattr(mod, "REPO", env["work"].parent)
    with pytest.raises(mod.PreconditionFailure, match="outside the repository"):
        run_cards(env, tmp_path)


def test_fence_collision_refused():
    with pytest.raises(mod.PreconditionFailure, match="closing delimiter"):
        mod._fence("paper_content", "text with </paper_content> inside")


def test_untrusted_blocks_carry_boundary_sentences(env, tmp_path, monkeypatch):
    """Mutation guard: the two whole-file calls (field analyst, synthesizer)
    state Iron Rule #7 at the call boundary, ahead of the fenced block."""
    seen = []
    real_build = mod.build_transport

    def capture(args):
        transport = real_build(args)
        seen.append(transport)
        return transport

    monkeypatch.setattr(mod, "build_transport", capture)
    assert run_cards(env, tmp_path) == 0
    assert mod.main(base_argv(env, "panel") + scripted(tmp_path, panel_responses())) == 0
    calls = {call.label: call for transport in seen for call, _ in transport.calls}
    analyst = calls["field_analyst"].user
    assert mod.DATA_BOUNDARY in analyst
    assert analyst.index(mod.DATA_BOUNDARY) < analyst.index(f"<{mod.MANUSCRIPT_TAG}>")
    synthesis = calls["synthesis"].user
    assert mod.REPORT_BOUNDARY in synthesis
    assert synthesis.index(mod.REPORT_BOUNDARY) < synthesis.index(f"<{mod.REPORT_TAG}>")


def _edit_manifest(env, mutate):
    path = env["corpus"] / "corpus" / "papers.json"
    payload = json.loads(path.read_text())
    mutate(payload)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_normalization_rule_drift_refused(env, tmp_path):
    _edit_manifest(env, lambda p: p["extraction"].update(text_normalization="NFC"))
    with pytest.raises(mod.PreconditionFailure, match="text_normalization"):
        run_cards(env, tmp_path)


def test_page_count_mismatch_refused(env, tmp_path):
    _edit_manifest(env, lambda p: p["papers"][0].update(page_count=7))
    with pytest.raises(mod.PreconditionFailure, match="page_count mismatch"):
        run_cards(env, tmp_path)


def test_symlinked_frozen_card_refused(env, tmp_path):
    """A card pointing at gold_labels.json must not reach any seat prompt."""
    assert run_cards(env, tmp_path) == 0
    card = env["work"] / "cards" / "p1" / "card1.md"
    card.unlink()
    card.symlink_to(env["corpus"] / "manifests" / "gold_labels.json")
    rc = mod.main(base_argv(env, "panel") + scripted(tmp_path, panel_responses()))
    assert rc == 1
    blocked = json.loads((env["work"] / "runs" / "blocked-2026-08-07-p1-r1.json").read_text())
    assert "frozen card" in blocked["abort_reason"] and "symlink" in blocked["abort_reason"]


def test_records_carry_per_call_timing_and_hashes(env, tmp_path):
    assert run_cards(env, tmp_path) == 0
    assert mod.main(base_argv(env, "panel") + scripted(tmp_path, panel_responses())) == 0
    record = json.loads((env["work"] / "runs" / "2026-08-07-p1-r1.json").read_text())
    assert [c["call"] for c in record["calls"]] == [f"seat-{s}" for s in mod.SEATS] + ["synthesis"]
    for row in record["calls"]:
        assert row["outcome"] == "completed"
        assert row["started_at"] <= row["completed_at"]
        assert len(row["prompt_sha256"]) == 64 and len(row["output_sha256"]) == 64
    frozen = json.loads((env["work"] / "cards" / "p1" / "frozen.json").read_text())
    assert frozen["calls"][0]["call"] == "field_analyst"


# --- 2026-09-06 rehearsal findings (#828) ----------------------------------

import urllib.error  # noqa: E402

from dispatch_e4_panel import TransportFailure  # noqa: E402


class _RaisingTransport:
    """Raises queued TransportFailures per label before replaying responses."""

    def __init__(self, failures: dict[str, list[TransportFailure]], responses: dict[str, list[str]]):
        self.failures = {k: list(v) for k, v in failures.items()}
        self.responses = {k: list(v) for k, v in responses.items()}
        self.calls: list[str] = []

    def __call__(self, call, sandbox):
        self.calls.append(call.label)
        queue = self.failures.get(call.label)
        if queue:
            raise queue.pop(0)
        return self.responses[call.label].pop(0)


def parsed(env, stage, extra=()):
    return mod.build_parser().parse_args(base_argv(env, stage) + list(extra))


AUTH_FAILURE = TransportFailure(
    "field_analyst", "[TRANSPORT: exit 1]",
    stdout="Failed to authenticate. API Error: 401 API key is invalid.\n",
)


def test_auth_failure_is_not_retried_and_cards_abort_leaves_blocked_record(env, tmp_path):
    transport = _RaisingTransport({"field_analyst": [AUTH_FAILURE, AUTH_FAILURE]}, {})
    assert mod.stage_cards(parsed(env, "cards"), transport) == 1
    assert transport.calls == ["field_analyst"], "a rejected credential must not burn a retry"
    blocked = json.loads((env["work"] / "runs" / "blocked-cards-p1.json").read_text())
    assert blocked["stage"] == "cards" and blocked["status"] == "aborted"
    assert "credential" in blocked["abort_reason"].lower()
    assert blocked["retries"] == []
    assert [c["outcome"] for c in blocked["calls"]] == ["transport_failure"]
    assert blocked["calls"][0]["started_at"] <= blocked["calls"][0]["completed_at"]
    assert not (env["work"] / "cards" / "p1" / "frozen.json").exists()
    assert "sk-" not in json.dumps(blocked)


def test_generic_transport_failure_still_retries_once(env, tmp_path):
    generic = TransportFailure("field_analyst", "[TRANSPORT: exit 1]", stderr="boom")
    transport = _RaisingTransport({"field_analyst": [generic]}, {"field_analyst": [ANALYSIS]})
    assert mod.stage_cards(parsed(env, "cards"), transport) == 0
    assert transport.calls == ["field_analyst", "field_analyst"]
    frozen = json.loads((env["work"] / "cards" / "p1" / "frozen.json").read_text())
    assert [c["outcome"] for c in frozen["calls"]] == ["transport_failure", "completed"]
    assert [c["attempt"] for c in frozen["calls"]] == [1, 2]
    assert len(frozen["retries"]) == 1
    assert frozen["attempt_id"] == "attempt-1" and len(frozen["suite_commit"]) == 40


def test_auth_failure_in_panel_stage_blocks_without_retry(env, tmp_path):
    assert run_cards(env, tmp_path) == 0
    seat_auth = TransportFailure("seat-eic", "[TRANSPORT: exit 1]", stdout="Not logged in\n")
    transport = _RaisingTransport({"seat-eic": [seat_auth, seat_auth]}, panel_responses())
    assert mod.stage_panel(parsed(env, "panel"), transport) == 1
    assert transport.calls == ["seat-eic"]
    record = json.loads((env["work"] / "runs" / "blocked-2026-08-07-p1-r1.json").read_text())
    assert record["retries"] == [] and record["completed_calls"] == []


class _Ctx:
    def __init__(self, status):
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def test_credential_preflight_refuses_rejected_key_without_echoing_it():
    seen = {}

    def opener(request, timeout):
        seen["url"] = request.full_url
        seen["key"] = request.get_header("X-api-key")
        raise urllib.error.HTTPError(request.full_url, 401, "Unauthorized", {}, None)

    with pytest.raises(mod.PreconditionFailure) as excinfo:
        mod.credential_preflight({"ANTHROPIC_API_KEY": "sk-ant-test-secret"}, opener=opener)
    assert "401" in str(excinfo.value) and "sk-ant-test-secret" not in str(excinfo.value)
    assert seen["url"].startswith("https://api.anthropic.com/v1/models")
    assert seen["key"] == "sk-ant-test-secret"


def test_credential_preflight_honours_base_url_and_reports_ok():
    def opener(request, timeout):
        assert request.full_url.startswith("https://proxy.example/v1/models")
        return _Ctx(200)

    env = {"ANTHROPIC_API_KEY": " sk-ant-x ", "ANTHROPIC_BASE_URL": "https://proxy.example/"}
    assert mod.credential_preflight(env, opener=opener) == "ok"


def test_credential_preflight_is_inconclusive_on_network_trouble_and_skips_without_key():
    def opener(request, timeout):
        raise urllib.error.URLError("no route")

    assert mod.credential_preflight({"ANTHROPIC_API_KEY": "k"}, opener=opener).startswith("inconclusive")

    def opener_500(request, timeout):
        raise urllib.error.HTTPError(request.full_url, 503, "down", {}, None)

    assert mod.credential_preflight({"ANTHROPIC_API_KEY": "k"}, opener=opener_500) == "inconclusive: HTTP 503"

    def never(request, timeout):  # pragma: no cover - must not be reached
        raise AssertionError("no key, no probe")

    assert mod.credential_preflight({}, opener=never).startswith("skipped")
    assert mod.credential_preflight({"ANTHROPIC_API_KEY": "   "}, opener=never).startswith("skipped")


def _manifest_argv(env, generated_at="2026-08-07T01:00:00Z", extra=()):
    return [
        "--stage", "manifest", "--work-dir", str(env["work"]),
        "--generated-at", generated_at, *extra,
    ]


def test_manifest_stage_assembles_completed_calls_and_is_write_once(env, tmp_path):
    assert run_cards(env, tmp_path) == 0
    assert mod.main(base_argv(env, "panel") + scripted(tmp_path, panel_responses())) == 0
    assert mod.main(_manifest_argv(env)) == 0
    path = env["work"] / "execution-manifest.json"
    manifest = json.loads(path.read_text())
    assert manifest["schema_version"] == "heldout-execution-manifest/1.0"
    assert manifest["suite"] == "reviewer_calibration" and manifest["write_once"] is True
    assert manifest["created_at"] == "2026-08-07T01:00:00Z"
    calls = manifest["calls"]
    ids = [c["call_id"] for c in calls]
    assert ids[0] == "cards-p1/field_analyst" and ids[-1] == "2026-08-07-p1-r1/synthesis"
    assert len(ids) == 7 == len(set(ids))
    assert [c["sequence_index"] for c in calls] == list(range(1, 8))
    for row in calls:
        assert row["attempt"] == 1 and row["concurrency_group"] is None
        assert row["started_at"] <= row["completed_at"]
    window = manifest["execution_window"]
    assert window["started_at"] == calls[0]["started_at"]
    assert window["completed_at"] == max(c["completed_at"] for c in calls)
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(
        (mod.REPO / "evals" / "heldout" / "execution_manifest.schema.json").read_text()
    )
    jsonschema.Draft202012Validator(schema).validate(manifest)
    before = path.read_bytes()
    with pytest.raises(mod.PreconditionFailure, match="write-once"):
        mod.main(_manifest_argv(env, generated_at="2026-08-07T02:00:00Z"))
    assert path.read_bytes() == before


def test_manifest_stage_keeps_retry_attempt_numbers_and_skips_failed_rows(env, tmp_path):
    generic = TransportFailure("field_analyst", "[TRANSPORT: exit 1]", stderr="boom")
    transport = _RaisingTransport({"field_analyst": [generic]}, {"field_analyst": [ANALYSIS]})
    assert mod.stage_cards(parsed(env, "cards"), transport) == 0
    assert mod.main(base_argv(env, "panel") + scripted(tmp_path, panel_responses())) == 0
    assert mod.main(_manifest_argv(env)) == 0
    calls = json.loads((env["work"] / "execution-manifest.json").read_text())["calls"]
    assert len(calls) == 7
    assert calls[0]["call_id"] == "cards-p1/field_analyst" and calls[0]["attempt"] == 2


def test_manifest_stage_refuses_mixed_attempts_and_blocked_only_work(env, tmp_path):
    assert run_cards(env, tmp_path) == 0
    argv = base_argv(env, "panel")
    argv[argv.index("--attempt-id") + 1] = "attempt-2"
    assert mod.main(argv + scripted(tmp_path, panel_responses())) == 0
    with pytest.raises(mod.PreconditionFailure, match="attempt_id"):
        mod.main(_manifest_argv(env))
    assert not (env["work"] / "execution-manifest.json").exists()

    other = {"corpus": env["corpus"], "cache": env["cache"], "work": tmp_path / "work2"}
    transport = _RaisingTransport({"field_analyst": [AUTH_FAILURE]}, {})
    assert mod.stage_cards(parsed(other, "cards"), transport) == 1
    with pytest.raises(mod.PreconditionFailure, match="no completed call"):
        mod.main(_manifest_argv(other))


def test_records_carry_credential_preflight_outcome(env, tmp_path):
    assert run_cards(env, tmp_path) == 0
    assert mod.main(base_argv(env, "panel") + scripted(tmp_path, panel_responses())) == 0
    record = json.loads((env["work"] / "runs" / "2026-08-07-p1-r1.json").read_text())
    frozen = json.loads((env["work"] / "cards" / "p1" / "frozen.json").read_text())
    assert record["credential_preflight"].startswith("skipped")
    assert frozen["credential_preflight"].startswith("skipped")


# --- codex round 2 (2026-09-06) --------------------------------------------

def test_auth_signature_ignores_partial_prose_and_timeouts(env, tmp_path):
    timeout = TransportFailure(
        "field_analyst", "[TRANSPORT: TimeoutExpired after 3600s]",
        stdout="Not logged in is what the reviewed UI displays; the paper argues...",
    )
    assert not mod._is_auth_failure(timeout)
    mid_text = TransportFailure("field_analyst", "[TRANSPORT: exit 1]", stdout="Review\n\nNot logged in\n")
    assert not mod._is_auth_failure(mid_text)
    assert mod._is_auth_failure(AUTH_FAILURE)
    assert mod._is_auth_failure(TransportFailure("x", "[TRANSPORT: exit 1]", stderr="Not logged in\n"))
    transport = _RaisingTransport({"field_analyst": [timeout]}, {"field_analyst": [ANALYSIS]})
    assert mod.stage_cards(parsed(env, "cards"), transport) == 0
    assert transport.calls == ["field_analyst", "field_analyst"]


def test_credential_preflight_never_follows_redirects_and_skips_plain_http():
    handler = mod._NoRedirect()
    assert handler.redirect_request(None, None, 302, "Found", {}, "https://elsewhere.example/") is None

    def opener(request, timeout):
        raise urllib.error.HTTPError(request.full_url, 302, "Found", {"Location": "https://elsewhere.example/"}, None)

    assert mod.credential_preflight({"ANTHROPIC_API_KEY": "k"}, opener=opener) == "inconclusive: HTTP 302"

    def never(request, timeout):  # pragma: no cover
        raise AssertionError("plain http must not carry the key")

    outcome = mod.credential_preflight({"ANTHROPIC_API_KEY": "k", "ANTHROPIC_BASE_URL": "http://proxy.local"}, opener=never)
    assert outcome.startswith("skipped") and "https" in outcome


def test_cards_rerun_refuses_reused_evidence_dir(env, tmp_path):
    transport = _RaisingTransport({"field_analyst": [AUTH_FAILURE]}, {})
    assert mod.stage_cards(parsed(env, "cards"), transport) == 1
    blocked = env["work"] / "runs" / "blocked-cards-p1.json"
    before = blocked.read_bytes()
    with pytest.raises(mod.PreconditionFailure, match="fresh work dir"):
        run_cards(env, tmp_path)
    assert blocked.read_bytes() == before


def test_manifest_admits_records_by_content_not_filename(env, tmp_path):
    assert run_cards(env, tmp_path) == 0
    seat_auth = TransportFailure("seat-eic", "[TRANSPORT: exit 1]", stdout="Not logged in\n")
    transport = _RaisingTransport({"seat-eic": [seat_auth]}, panel_responses())
    assert mod.stage_panel(parsed(env, "panel"), transport) == 1
    runs = env["work"] / "runs"
    (runs / "blocked-2026-08-07-p1-r1.json").rename(runs / "2026-08-07-p1-r1.json")
    assert mod.main(_manifest_argv(env)) == 0  # the aborted panel is still listed as blocked
    calls = json.loads((env["work"] / "execution-manifest.json").read_text())["calls"]
    assert [c["call_id"] for c in calls] == ["cards-p1/field_analyst"]


def test_manifest_refuses_edited_raw_output_and_foreign_stage(env, tmp_path):
    assert run_cards(env, tmp_path) == 0
    assert mod.main(base_argv(env, "panel") + scripted(tmp_path, panel_responses())) == 0
    synthesis = env["work"] / "runs" / "2026-08-07-p1-r1" / "raw" / "synthesis.md"
    synthesis.write_text(SYNTHESIS.replace("Major Revision", "Accept"))
    with pytest.raises(mod.PreconditionFailure, match="no longer hashes"):
        mod.main(_manifest_argv(env))
    synthesis.write_text(SYNTHESIS)
    frozen = env["work"] / "cards" / "p1" / "frozen.json"
    record = json.loads(frozen.read_text())
    record["stage"] = "panel"
    frozen.write_text(json.dumps(record))
    with pytest.raises(mod.PreconditionFailure, match="cards record"):
        mod.main(_manifest_argv(env))


def test_manifest_refuses_bad_timestamps(env, tmp_path):
    assert run_cards(env, tmp_path) == 0
    assert mod.main(base_argv(env, "panel") + scripted(tmp_path, panel_responses())) == 0
    with pytest.raises(mod.PreconditionFailure, match="RFC 3339"):
        mod.main(_manifest_argv(env, generated_at="not-a-timestamp"))
    assert not (env["work"] / "execution-manifest.json").exists()


def test_structured_auth_failure_is_not_retried(env, tmp_path):
    structured = TransportFailure(
        "field_analyst", "[TRANSPORT: result error_during_execution] Failed to authenticate.",
        stdout="Failed to authenticate. API Error: 401 API key is invalid.",
        raw_stdout='{"type":"result","is_error":true}',
    )
    assert mod._is_auth_failure(structured)
    transport = _RaisingTransport({"field_analyst": [structured, structured]}, {})
    assert mod.stage_cards(parsed(env, "cards"), transport) == 1
    assert transport.calls == ["field_analyst"]
    raw = env["work"] / "cards" / "p1" / "raw"
    assert (raw / "field_analyst.attempt1.transport-stream.jsonl").read_text().startswith("{")


def test_successful_calls_keep_the_raw_stream_when_the_transport_offers_it(env, tmp_path):
    class Streaming(_RaisingTransport):
        def __call__(self, call, sandbox):
            text = super().__call__(call, sandbox)
            self.last_raw_stdout = '{"type":"assistant"}\n{"type":"result","subtype":"success"}\n'
            return text

    transport = Streaming({}, {"field_analyst": [ANALYSIS]})
    assert mod.stage_cards(parsed(env, "cards"), transport) == 0
    raw = env["work"] / "cards" / "p1" / "raw"
    assert (raw / "field_analyst.transport-stream.jsonl").read_text().startswith('{"type":"assistant"}')
    assert (raw / "field_analyst.md").read_text() == ANALYSIS
