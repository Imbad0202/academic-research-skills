"""Hermetic contract and runtime tests for the #630 Codex subscription transport."""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any

from jsonschema import Draft202012Validator
import pytest


REPO = Path(__file__).resolve().parent.parent
RUNTIME_PATH = REPO / "scripts" / "cross_model_codex_transport.py"
WRAPPER = REPO / "scripts" / "cross_model_codex_verify.sh"
FIXTURES = REPO / "scripts" / "fixtures" / "cross_model_codex_transport"
REQUEST_SCHEMA_PATH = (
    REPO / "shared" / "contracts" / "cross_model" / "codex_citation_request.schema.json"
)
RECEIPT_SCHEMA_PATH = (
    REPO / "shared" / "contracts" / "cross_model" / "codex_citation_receipt.schema.json"
)


def _load_runtime():
    spec = importlib.util.spec_from_file_location("codex_transport_630", RUNTIME_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


runtime = _load_runtime()


def _request(**updates: str) -> dict[str, str]:
    value = {
        "schema_version": runtime.REQUEST_SCHEMA_VERSION,
        "request_id": "vaswani-2017",
        "reference_text": (
            "Vaswani, Shazeer, Parmar, Uszkoreit, Jones, Gomez, Kaiser, and "
            "Polosukhin (2017). Attention Is All You Need."
        ),
        "citation_context": "Cited as the source introducing the Transformer architecture.",
    }
    value.update(updates)
    return value


def _fixture(name: str) -> tuple[list[dict[str, Any]], bytes]:
    raw = (FIXTURES / name).read_bytes()
    messages = [runtime.strict_json_loads(line) for line in raw.splitlines()]
    return messages, raw


def _receipt(name: str) -> dict[str, Any]:
    messages, raw = _fixture(name)
    return runtime.parse_app_server_messages(
        messages,
        raw_stream=raw,
        request=_request(),
        model="gpt-5.6",
    )


def _schema(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _base_env(fake_bin: Path, codex_home: Path) -> dict[str, str]:
    return {
        "PATH": f"{fake_bin}{os.pathsep}{os.defpath}",
        "HOME": str(codex_home.parent),
        "TMPDIR": str(codex_home.parent),
        "CODEX_HOME": str(codex_home),
        "ARS_CROSS_MODEL_TRANSPORT": "codex",
        "ARS_CROSS_MODEL": "gpt-5.6",
        "OPENAI_API_KEY": "must-not-reach-child",
        "ANTHROPIC_API_KEY": "must-not-reach-child",
    }


def _make_fake_codex(
    tmp_path: Path,
    *,
    events: list[dict[str, Any]] | None = None,
    late_events_after_eof: list[dict[str, Any]] | None = None,
    late_raw_after_eof: bytes = b"",
    version: str = "codex-cli 0.147.0",
    status: str = "Logged in using ChatGPT",
    status_to_stderr: bool = False,
    fail_app_server: bool = False,
    silent_app_server: bool = False,
    hang_after_eof: bool = False,
    exit_code_after_eof: int = 0,
    stderr_bytes_after_eof: int = 0,
) -> tuple[Path, Path]:
    fake_bin = tmp_path / "fake-bin"
    fake_bin.mkdir()
    executable = fake_bin / "codex"
    capture = fake_bin / "app-server-capture.json"
    event_rows = events if events is not None else _fixture("grounded_verified.jsonl")[0]
    late_event_rows = late_events_after_eof if late_events_after_eof is not None else []
    source = f"""#!{sys.executable}
import json
import os
from pathlib import Path
import sys
import threading

VERSION = {version!r}
STATUS = {status!r}
STATUS_TO_STDERR = {status_to_stderr!r}
EVENTS = {event_rows!r}
LATE_EVENTS_AFTER_EOF = {late_event_rows!r}
LATE_RAW_AFTER_EOF = {late_raw_after_eof!r}
FAIL_APP_SERVER = {fail_app_server!r}
SILENT_APP_SERVER = {silent_app_server!r}
HANG_AFTER_EOF = {hang_after_eof!r}
EXIT_CODE_AFTER_EOF = {exit_code_after_eof!r}
STDERR_BYTES_AFTER_EOF = {stderr_bytes_after_eof!r}
CAPTURE = Path(__file__).with_name("app-server-capture.json")

if sys.argv[1:] == ["--version"]:
    print(VERSION)
    raise SystemExit(0)
if sys.argv[1:] == ["login", "status"]:
    print(STATUS, file=sys.stderr if STATUS_TO_STDERR else sys.stdout)
    raise SystemExit(0)
if not sys.argv[1:] or sys.argv[1] != "app-server":
    raise SystemExit(9)
if FAIL_APP_SERVER:
    raise SystemExit(7)

home = Path(os.environ["CODEX_HOME"])
record = {{
    "argv": sys.argv[1:],
    "cwd": os.getcwd(),
    "env": dict(os.environ),
    "pid": os.getpid(),
    "codex_home_files": sorted(path.name for path in home.iterdir()),
    "requests": [],
    "stdin_eof": False,
}}

def emit(value):
    sys.stdout.write(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\\n")
    sys.stdout.flush()

for line in sys.stdin:
    message = json.loads(line)
    record["requests"].append(message)
    CAPTURE.write_text(json.dumps(record, sort_keys=True), encoding="utf-8")
    if SILENT_APP_SERVER:
        continue
    if message.get("id") == 1:
        emit({{"id": 1, "result": {{}}}})
    elif message.get("id") == 2:
        emit({{"id": 2, "result": {{"thread": {{"id": "thread-1"}}}}}})
    elif message.get("id") == 3:
        emit({{"id": 3, "result": {{"turn": {{"id": "turn-1"}}}}}})
        for event in EVENTS:
            emit(event)

record["stdin_eof"] = True
CAPTURE.write_text(json.dumps(record, sort_keys=True), encoding="utf-8")
for event in LATE_EVENTS_AFTER_EOF:
    emit(event)
if LATE_RAW_AFTER_EOF:
    sys.stdout.buffer.write(LATE_RAW_AFTER_EOF)
    sys.stdout.buffer.flush()
if STDERR_BYTES_AFTER_EOF:
    sys.stderr.buffer.write(b"x" * STDERR_BYTES_AFTER_EOF)
    sys.stderr.buffer.flush()
if HANG_AFTER_EOF:
    threading.Event().wait()
raise SystemExit(EXIT_CODE_AFTER_EOF)
"""
    executable.write_text(source, encoding="utf-8")
    executable.chmod(0o755)
    return fake_bin, capture


def _make_auth(codex_home: Path) -> None:
    codex_home.mkdir()
    (codex_home / "auth.json").write_text('{"tokens":{"access_token":"fake"}}', encoding="utf-8")
    (codex_home / "config.toml").write_text("model = 'must-not-copy'\n", encoding="utf-8")
    (codex_home / "skills").mkdir()


def _assert_helper_start_failure_cleanup(
    tmp_path: Path, monkeypatch, *, fail_on_start: int
) -> list[Any]:
    home = tmp_path / "custom-home"
    _make_auth(home)
    fake_bin, _ = _make_fake_codex(tmp_path)
    real_popen = runtime.subprocess.Popen
    real_thread_start = runtime.threading.Thread.start
    spawned: list[Any] = []
    started_threads: list[Any] = []
    start_attempt = 0

    def recording_popen(*args, **kwargs):
        proc = real_popen(*args, **kwargs)
        spawned.append(proc)
        return proc

    def controlled_start(thread) -> None:
        nonlocal start_attempt
        start_attempt += 1
        if start_attempt == fail_on_start:
            raise RuntimeError(f"forced helper start failure {fail_on_start}")
        real_thread_start(thread)
        started_threads.append(thread)

    monkeypatch.setattr(runtime.subprocess, "Popen", recording_popen)
    monkeypatch.setattr(runtime.threading.Thread, "start", controlled_start)
    with pytest.raises(RuntimeError, match=f"forced helper start failure {fail_on_start}"):
        runtime.run_app_server(
            _request(),
            model="gpt-5.6",
            codex=str(fake_bin / "codex"),
            source_auth=home / "auth.json",
            environ=_base_env(fake_bin, home),
        )
    assert start_attempt == fail_on_start
    assert len(spawned) == 1
    assert spawned[0].poll() is not None
    with pytest.raises(ProcessLookupError):
        os.killpg(spawned[0].pid, 0)
    assert all(not thread.is_alive() for thread in started_threads)
    return started_threads


def test_schemas_are_valid_draft_2020_12_and_closed() -> None:
    request_schema = _schema(REQUEST_SCHEMA_PATH)
    receipt_schema = _schema(RECEIPT_SCHEMA_PATH)
    Draft202012Validator.check_schema(request_schema)
    Draft202012Validator.check_schema(receipt_schema)
    assert request_schema["additionalProperties"] is False
    assert receipt_schema["additionalProperties"] is False
    for definition in receipt_schema["$defs"].values():
        if isinstance(definition, dict) and definition.get("type") == "object":
            assert definition.get("additionalProperties") is False


def test_positive_request_and_grounded_receipt_validate() -> None:
    request_validator = Draft202012Validator(_schema(REQUEST_SCHEMA_PATH))
    receipt_validator = Draft202012Validator(_schema(RECEIPT_SCHEMA_PATH))
    request_validator.validate(_request())
    receipt = _receipt("grounded_verified.jsonl")
    receipt_validator.validate(receipt)
    assert receipt["verdict"] == "VERIFIED"
    assert receipt["searched"] is True
    assert receipt["sources"][0]["search_item_id"] == "search:One"


@pytest.mark.parametrize(
    "field,value",
    [
        ("searched", False),
        ("reason_code", "FINAL_OUTPUT_INVALID"),
        ("search_queries", []),
        ("sources", []),
    ],
)
def test_receipt_schema_rejects_cross_field_forgery(field: str, value: Any) -> None:
    receipt = _receipt("grounded_verified.jsonl")
    receipt[field] = value
    assert list(Draft202012Validator(_schema(RECEIPT_SCHEMA_PATH)).iter_errors(receipt))


@pytest.mark.parametrize(
    "mutation",
    [
        lambda value: value.update(extra="open"),
        lambda value: value.update(request_id="UPPERCASE"),
        lambda value: value.update(reference_text=""),
        lambda value: value.update(schema_version="wrong"),
    ],
    ids=["open-root", "bad-id", "empty-reference", "wrong-version"],
)
def test_request_schema_rejects_negative_payloads(mutation) -> None:
    value = _request()
    mutation(value)
    assert list(Draft202012Validator(_schema(REQUEST_SCHEMA_PATH)).iter_errors(value))


def test_runtime_rejects_duplicate_keys_nonfinite_and_surrogate() -> None:
    with pytest.raises(ValueError, match="duplicate"):
        runtime.strict_json_loads('{"a":1,"a":2}')
    with pytest.raises(ValueError, match="non-finite"):
        runtime.strict_json_loads('{"a":NaN}')
    with pytest.raises(ValueError, match="control"):
        runtime.validate_request(_request(reference_text="bad\ud800scalar"))


@pytest.mark.parametrize(
    "fixture,reason",
    [
        ("missing_search.jsonl", "NO_BOUND_SEARCH_RESULTS"),
        # results as a dict is a protocol-shape violation, not a mere absence
        # of bindable results — it must carry the unambiguous shape code so
        # bakeoff measure 4 can attribute it (#788 round-6 P2).
        ("wrong_search_shape.jsonl", "EVENT_STREAM_INVALID"),
        ("multiple_finals.jsonl", "FINAL_OUTPUT_INVALID"),
        ("unbound_source.jsonl", "SOURCE_NOT_IN_SEARCH_RESULTS"),
        ("forbidden_event.jsonl", "FORBIDDEN_TOOL_EVENT"),
        ("malformed.jsonl", "FINAL_OUTPUT_INVALID"),
    ],
)
def test_fixture_failures_are_closed_and_visible(fixture: str, reason: str) -> None:
    receipt = _receipt(fixture)
    Draft202012Validator(_schema(RECEIPT_SCHEMA_PATH)).validate(receipt)
    assert receipt["verdict"] == "NOT_SEARCHED"
    assert receipt["searched"] is False
    assert receipt["reason_code"] == reason
    assert receipt["sources"] == []


def test_not_found_requires_a_reference_bound_search_result() -> None:
    receipt = _receipt("not_found.jsonl")
    assert receipt["verdict"] == "NOT_FOUND"
    assert receipt["searched"] is True
    assert receipt["reason_code"] is None
    assert receipt["sources"] == []


def test_grounded_mismatch_and_model_not_searched_are_closed() -> None:
    messages, raw = _fixture("grounded_verified.jsonl")
    model_output = {
        "verdict": "MISMATCH",
        "detail": "The supplied year conflicts with the record.",
        "sources": ["https://arxiv.org/abs/1706.03762"],
    }
    messages[1]["params"]["item"]["text"] = json.dumps(model_output)
    receipt = runtime.parse_app_server_messages(
        messages, raw_stream=raw, request=_request(), model="gpt-5.6"
    )
    assert receipt["verdict"] == "MISMATCH"
    assert receipt["searched"] is True
    assert receipt["sources"][0]["search_result_digest"]

    model_output = {"verdict": "NOT_SEARCHED", "detail": "Search unavailable.", "sources": []}
    messages[1]["params"]["item"]["text"] = json.dumps(model_output)
    receipt = runtime.parse_app_server_messages(
        messages, raw_stream=raw, request=_request(), model="gpt-5.6"
    )
    assert receipt["verdict"] == "NOT_SEARCHED"
    assert receipt["reason_code"] == "MODEL_RETURNED_NOT_SEARCHED"


def _page_open_event(url: str = "https://example.org/toc") -> dict[str, Any]:
    # codex-cli 0.147.0 emits follow-up page opens as webSearch items with a
    # non-"search" action type and no query string (#787).
    return {
        "method": "item/completed",
        "params": {
            "item": {
                "id": "exec-view-1",
                "type": "webSearch",
                "action": {"type": "other"},
                "results": [{"type": "text_result", "url": url, "title": "TOC"}],
            }
        },
    }


def test_page_open_web_search_items_are_skipped_not_stream_fatal() -> None:
    messages, raw = _fixture("grounded_verified.jsonl")
    messages = [_page_open_event()] + messages
    receipt = runtime.parse_app_server_messages(
        messages, raw_stream=raw, request=_request(), model="gpt-5.6"
    )
    assert receipt["verdict"] == "VERIFIED"
    assert receipt["searched"] is True

    # A page-open's URL never becomes a bindable source.
    model_output = {
        "verdict": "VERIFIED",
        "detail": "Claimed from an opened page, not a search result.",
        "sources": ["https://example.org/toc"],
    }
    messages2, raw2 = _fixture("grounded_verified.jsonl")
    messages2 = [_page_open_event()] + messages2
    messages2[2]["params"]["item"]["text"] = json.dumps(model_output)
    receipt = runtime.parse_app_server_messages(
        messages2, raw_stream=raw2, request=_request(), model="gpt-5.6"
    )
    assert receipt["reason_code"] == "SOURCE_NOT_IN_SEARCH_RESULTS"

    # A stream whose only webSearch items are page opens has no bound search.
    messages3, raw3 = _fixture("grounded_verified.jsonl")
    messages3 = [_page_open_event()] + [
        m for m in messages3 if m.get("params", {}).get("item", {}).get("type") != "webSearch"
    ]
    receipt = runtime.parse_app_server_messages(
        messages3, raw_stream=raw3, request=_request(), model="gpt-5.6"
    )
    assert receipt["verdict"] == "NOT_SEARCHED"
    assert receipt["reason_code"] == "NO_BOUND_SEARCH_RESULTS"


def test_all_first_party_non_search_actions_are_skipped() -> None:
    # The exemption covers exactly the non-search members of the protocol's
    # closed WebSearchAction set, both spellings.
    # Bare discriminators are DELIBERATELY accepted: every non-search variant
    # of the protocol's closed WebSearchAction schema requires only "type"
    # (url/pattern are nullable optionals per generate-json-schema on
    # 0.147.0), and a skipped item can never contribute a bound source —
    # demanding optional fields is the run-1/run-3 false-fatality class.
    for ok_action in (
        {"type": "other"},
        {"type": "openPage", "url": "https://example.org/toc"},
        {"type": "openPage"},
        {"type": "open_page", "url": "https://example.org/toc"},
        {"type": "findInPage", "url": "https://example.org/toc", "pattern": "x"},
        {"type": "findInPage"},
        {"type": "find_in_page", "url": "https://example.org/toc", "pattern": "x"},
    ):
        messages, raw = _fixture("grounded_verified.jsonl")
        opener = _page_open_event()
        opener["params"]["item"]["action"] = ok_action
        receipt = runtime.parse_app_server_messages(
            [opener] + messages, raw_stream=raw, request=_request(), model="gpt-5.6"
        )
        assert receipt["verdict"] == "VERIFIED", ok_action
        assert receipt["searched"] is True, ok_action


def test_rejected_url_value_under_recognized_key_stays_behavioral() -> None:
    # A recognized URL key holding an unusable value (http://) is a
    # value-level outcome, not key-shape drift — it must stay in the
    # behavior family (#788 round-27 P2).
    messages, raw = _fixture("grounded_verified.jsonl")
    for m in messages:
        item = m.get("params", {}).get("item", {})
        if item.get("type") == "webSearch":
            item["results"] = [{"type": "text_result", "url": "http://arxiv.org/abs/1706.03762"}]
        elif item.get("type") == "agentMessage":
            item["text"] = json.dumps(
                {"verdict": "NOT_FOUND", "detail": "No matching work found.", "sources": []}
            )
    receipt = runtime.parse_app_server_messages(
        messages, raw_stream=raw, request=_request(), model="gpt-5.6"
    )
    assert receipt["reason_code"] == "NO_BOUND_SEARCH_RESULTS"


def test_url_key_drift_fatal_even_when_model_says_not_searched() -> None:
    # The key-drift determination runs pre-verdict (#788 round-28 P2): a
    # NOT_SEARCHED answer on a stream whose bound entries carry a renamed URL
    # key must surface EVENT_STREAM_INVALID, not the model verdict.
    messages, raw = _fixture("grounded_verified.jsonl")
    for m in messages:
        item = m.get("params", {}).get("item", {})
        if item.get("type") == "webSearch":
            item["results"] = [{"type": "text_result", "canonical_url": "https://arxiv.org/abs/1706.03762"}]
        elif item.get("type") == "agentMessage":
            item["text"] = json.dumps(
                {"verdict": "NOT_SEARCHED", "detail": "Search unavailable.", "sources": []}
            )
    receipt = runtime.parse_app_server_messages(
        messages, raw_stream=raw, request=_request(), model="gpt-5.6"
    )
    assert receipt["reason_code"] == "EVENT_STREAM_INVALID"


def test_url_key_drift_in_bound_results_is_stream_fatal() -> None:
    # A bound search whose non-empty result entries yield no extractable URL
    # means the provider moved/renamed the URL key — shape drift, not a
    # zero-hit behavior outcome (#788 round-26 P1).
    messages, raw = _fixture("grounded_verified.jsonl")
    for m in messages:
        item = m.get("params", {}).get("item", {})
        if item.get("type") == "webSearch":
            item["results"] = [{"type": "text_result", "canonical_url": "https://arxiv.org/abs/1706.03762"}]
        elif item.get("type") == "agentMessage":
            item["text"] = json.dumps(
                {"verdict": "NOT_FOUND", "detail": "No matching work found.", "sources": []}
            )
    receipt = runtime.parse_app_server_messages(
        messages, raw_stream=raw, request=_request(), model="gpt-5.6"
    )
    assert receipt["reason_code"] == "EVENT_STREAM_INVALID"


def test_wrong_typed_action_payload_fields_are_stream_fatal() -> None:
    # A recognized discriminator with a wrong-typed payload field is
    # protocol drift, not a benign skip (#788 round-15 P2).
    for bad_action in (
        {"type": "openPage", "url": 7},
        {"type": "findInPage", "pattern": 3},
        {"type": "other", "url": ["x"]},
        {"type": "search", "queries": [7]},
        {"type": "search", "query": 9},
    ):
        messages, raw = _fixture("grounded_verified.jsonl")
        bad = _page_open_event()
        bad["params"]["item"]["action"] = bad_action
        receipt = runtime.parse_app_server_messages(
            [bad] + messages, raw_stream=raw, request=_request(), model="gpt-5.6"
        )
        assert receipt["reason_code"] == "EVENT_STREAM_INVALID", bad_action


def test_unknown_web_search_action_shapes_stay_stream_fatal() -> None:
    # Only the closed first-party non-search set is exempt; an empty action
    # object, an unknown type, or a non-dict action fails the stream closed
    # even when a valid search item is also present (codex round-1 P2 on
    # #788: the exemption must not become a catch-all).
    for bad_action in ({}, {"type": "browse"}, "other", {"kind": "other"}):
        messages, raw = _fixture("grounded_verified.jsonl")
        bad = _page_open_event()
        bad["params"]["item"]["action"] = bad_action
        receipt = runtime.parse_app_server_messages(
            [bad] + messages, raw_stream=raw, request=_request(), model="gpt-5.6"
        )
        assert receipt["verdict"] == "NOT_SEARCHED", bad_action
        assert receipt["reason_code"] == "EVENT_STREAM_INVALID", bad_action


def test_model_not_searched_never_masks_malformed_result_entries() -> None:
    # Result-entry object shape is validated for EVERY search item — bound or
    # unbound — before any verdict branch, so a NOT_SEARCHED answer cannot
    # mask a malformed stream (#788 round-10 P2 + round-11 P1).
    for unbound_query in (False, True):
        messages, raw = _fixture("grounded_verified.jsonl")
        for m in messages:
            item = m.get("params", {}).get("item", {})
            if item.get("type") == "webSearch":
                item["results"] = [42]
                if unbound_query:
                    item["query"] = "completely unrelated gardening tips"
            elif item.get("type") == "agentMessage":
                item["text"] = json.dumps(
                    {"verdict": "NOT_SEARCHED", "detail": "Search unavailable.", "sources": []}
                )
        receipt = runtime.parse_app_server_messages(
            messages, raw_stream=raw, request=_request(), model="gpt-5.6"
        )
        assert receipt["reason_code"] == "EVENT_STREAM_INVALID", f"unbound={unbound_query}"


def test_search_item_id_shape_is_validated_pre_verdict() -> None:
    # The item id is a consumed field (bindings reference it); a missing or
    # non-string id is stream-fatal regardless of verdict (#788 round-11 —
    # instrument fixpoint: every consumed field validated).
    for bad_id in (None, 7, ""):
        messages, raw = _fixture("grounded_verified.jsonl")
        for m in messages:
            item = m.get("params", {}).get("item", {})
            if item.get("type") == "webSearch":
                if bad_id is None:
                    item.pop("id", None)
                else:
                    item["id"] = bad_id
        receipt = runtime.parse_app_server_messages(
            messages, raw_stream=raw, request=_request(), model="gpt-5.6"
        )
        assert receipt["reason_code"] == "EVENT_STREAM_INVALID", repr(bad_id)


def test_not_searched_with_sources_is_an_output_contract_violation() -> None:
    # NOT_SEARCHED must carry an empty sources array; a populated one fails
    # closed instead of being silently dropped by the early return (#788
    # round-9 P2).
    messages, raw = _fixture("grounded_verified.jsonl")
    messages[1]["params"]["item"]["text"] = json.dumps(
        {
            "verdict": "NOT_SEARCHED",
            "detail": "Claimed unavailable yet cites a source.",
            "sources": ["https://arxiv.org/abs/1706.03762"],
        }
    )
    receipt = runtime.parse_app_server_messages(
        messages, raw_stream=raw, request=_request(), model="gpt-5.6"
    )
    assert receipt["reason_code"] == "FINAL_OUTPUT_INVALID"


def test_model_not_searched_never_masks_results_shape_drift() -> None:
    # Same ordering class as the action-shape check: a NOT_SEARCHED final
    # answer on a stream whose search item carries dict-shaped results must
    # surface EVENT_STREAM_INVALID, not the model verdict (#788 round-7 P2).
    messages, raw = _fixture("wrong_search_shape.jsonl")
    for m in messages:
        item = m.get("params", {}).get("item", {})
        if item.get("type") == "agentMessage":
            item["text"] = json.dumps(
                {"verdict": "NOT_SEARCHED", "detail": "Search unavailable.", "sources": []}
            )
    receipt = runtime.parse_app_server_messages(
        messages, raw_stream=raw, request=_request(), model="gpt-5.6"
    )
    assert receipt["reason_code"] == "EVENT_STREAM_INVALID"


def test_model_not_searched_never_masks_action_shape_drift() -> None:
    # Shape validation runs BEFORE the MODEL_RETURNED_NOT_SEARCHED early
    # return: a NOT_SEARCHED final answer on a stream carrying an unknown
    # action shape must surface EVENT_STREAM_INVALID, not the model verdict
    # (#788 round-3 P2 — measure 4 depends on this ordering).
    messages, raw = _fixture("grounded_verified.jsonl")
    bad = _page_open_event()
    bad["params"]["item"]["action"] = {"type": "browse"}
    messages[1]["params"]["item"]["text"] = json.dumps(
        {"verdict": "NOT_SEARCHED", "detail": "Search unavailable.", "sources": []}
    )
    receipt = runtime.parse_app_server_messages(
        [bad] + messages, raw_stream=raw, request=_request(), model="gpt-5.6"
    )
    assert receipt["reason_code"] == "EVENT_STREAM_INVALID"


def test_positive_without_source_fails_closed() -> None:
    messages, raw = _fixture("grounded_verified.jsonl")
    messages[1]["params"]["item"]["text"] = json.dumps(
        {"verdict": "VERIFIED", "detail": "Claimed without evidence.", "sources": []}
    )
    receipt = runtime.parse_app_server_messages(
        messages, raw_stream=raw, request=_request(), model="gpt-5.6"
    )
    assert receipt["reason_code"] == "MISSING_SOURCE_FOR_VERDICT"


def test_search_count_and_event_size_caps_fail_closed(monkeypatch) -> None:
    messages, raw = _fixture("grounded_verified.jsonl")
    search = messages[0]
    messages = [search, json.loads(json.dumps(search)), *messages[1:]]
    messages[1]["params"]["item"]["id"] = "search-2"
    monkeypatch.setattr(runtime, "MAX_SEARCH_ITEMS", 1)
    receipt = runtime.parse_app_server_messages(
        messages, raw_stream=raw, request=_request(), model="gpt-5.6"
    )
    assert receipt["reason_code"] == "EVENT_STREAM_INVALID"

    monkeypatch.setattr(runtime, "MAX_EVENT_BYTES", 1)
    receipt = runtime.parse_app_server_messages(
        messages[:1], raw_stream=b"too large", request=_request(), model="gpt-5.6"
    )
    assert receipt["reason_code"] == "EVENT_STREAM_INVALID"


def test_post_terminal_forbidden_event_is_not_ignored(tmp_path: Path) -> None:
    home = tmp_path / "custom-home"
    _make_auth(home)
    late_forbidden = {
        "method": "item/completed",
        "params": {
            "item": {
                "id": "late-tool",
                "type": "commandExecution",
                "status": "completed",
            }
        },
    }
    fake_bin, capture_path = _make_fake_codex(
        tmp_path, late_events_after_eof=[late_forbidden]
    )
    completed = subprocess.run(
        [str(WRAPPER)],
        input=runtime.canonical_json(_request()),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=_base_env(fake_bin, home),
        timeout=15,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr.decode()
    receipt = runtime.strict_json_loads(completed.stdout)
    assert receipt["reason_code"] == "FORBIDDEN_TOOL_EVENT"
    base_events, _ = _fixture("grounded_verified.jsonl")
    complete_stream = b"".join(
        runtime.canonical_json(message) + b"\n"
        for message in [
            {"id": 1, "result": {}},
            {"id": 2, "result": {"thread": {"id": "thread-1"}}},
            {"id": 3, "result": {"turn": {"id": "turn-1"}}},
            *base_events,
            late_forbidden,
        ]
    )
    assert receipt["event_stream_digest"] == runtime.sha256_hex(complete_stream)
    assert json.loads(capture_path.read_text(encoding="utf-8"))["stdin_eof"] is True


def test_first_helper_start_failure_reaps_process_group(tmp_path: Path, monkeypatch) -> None:
    started_threads = _assert_helper_start_failure_cleanup(
        tmp_path, monkeypatch, fail_on_start=1
    )
    assert started_threads == []


def test_second_helper_start_failure_reaps_process_group_and_stdout_helper(
    tmp_path: Path, monkeypatch
) -> None:
    started_threads = _assert_helper_start_failure_cleanup(
        tmp_path, monkeypatch, fail_on_start=2
    )
    assert len(started_threads) == 1


def test_post_terminal_hang_hits_bounded_drain_and_is_reaped(
    tmp_path: Path, monkeypatch
) -> None:
    home = tmp_path / "custom-home"
    _make_auth(home)
    fake_bin, capture_path = _make_fake_codex(tmp_path, hang_after_eof=True)
    monkeypatch.setattr(runtime, "APP_SERVER_TIMEOUT_SECONDS", 5.0)
    monkeypatch.setattr(runtime, "APP_SERVER_DRAIN_GRACE_SECONDS", 0.05)
    with pytest.raises(runtime.TransportError) as exc_info:
        runtime.run_app_server(
            _request(),
            model="gpt-5.6",
            codex=str(fake_bin / "codex"),
            source_auth=home / "auth.json",
            environ=_base_env(fake_bin, home),
        )
    assert exc_info.value.code == "APP_SERVER_DRAIN_TIMEOUT"
    capture = json.loads(capture_path.read_text(encoding="utf-8"))
    assert capture["stdin_eof"] is True
    with pytest.raises(ProcessLookupError):
        os.kill(capture["pid"], 0)


def test_forced_cleanup_reaps_parent_and_process_group_descendant(tmp_path: Path) -> None:
    ready = tmp_path / "process-tree-ready.json"
    child_ready = tmp_path / "process-tree-child-ready"
    source = f"""
import json
from pathlib import Path
import subprocess
import sys
import threading
import time

child = subprocess.Popen([
    sys.executable,
    "-c",
    "import signal, threading; from pathlib import Path; "
    "signal.signal(signal.SIGTERM, signal.SIG_IGN); "
    "Path({str(child_ready)!r}).write_text('ready', encoding='utf-8'); "
    "threading.Event().wait()",
])
while not Path({str(child_ready)!r}).exists():
    time.sleep(0.01)
Path({str(ready)!r}).write_text(json.dumps({{"child_pid": child.pid}}), encoding="utf-8")
threading.Event().wait()
"""
    proc = subprocess.Popen([sys.executable, "-c", source], start_new_session=True)
    try:
        wait_deadline = time.monotonic() + 2.0
        while not ready.exists() and time.monotonic() < wait_deadline:
            time.sleep(0.01)
        assert ready.exists()
        runtime._stop_process(proc)
        reap_deadline = time.monotonic() + 1.0
        while time.monotonic() < reap_deadline:
            try:
                os.killpg(proc.pid, 0)
            except ProcessLookupError:
                break
            time.sleep(0.01)
        with pytest.raises(ProcessLookupError):
            os.killpg(proc.pid, 0)
    finally:
        runtime._stop_process(proc)
    assert proc.returncode is not None


def test_late_message_limit_breach_is_fail_visible(tmp_path: Path, monkeypatch) -> None:
    home = tmp_path / "custom-home"
    _make_auth(home)
    late_event = {"method": "transport/notice", "params": {}}
    fake_bin, _ = _make_fake_codex(tmp_path, late_events_after_eof=[late_event])
    monkeypatch.setattr(runtime, "MAX_EVENT_MESSAGES", 6)
    with pytest.raises(runtime.TransportError) as exc_info:
        runtime.run_app_server(
            _request(),
            model="gpt-5.6",
            codex=str(fake_bin / "codex"),
            source_auth=home / "auth.json",
            environ=_base_env(fake_bin, home),
        )
    assert exc_info.value.code == "EVENT_MESSAGE_LIMIT_EXCEEDED"


def test_late_byte_limit_breach_is_fail_visible(tmp_path: Path, monkeypatch) -> None:
    home = tmp_path / "custom-home"
    _make_auth(home)
    late_event = {"method": "transport/notice", "padding": "x" * 8192}
    fake_bin, _ = _make_fake_codex(tmp_path, late_events_after_eof=[late_event])
    monkeypatch.setattr(runtime, "MAX_EVENT_BYTES", 4096)
    with pytest.raises(runtime.TransportError) as exc_info:
        runtime.run_app_server(
            _request(),
            model="gpt-5.6",
            codex=str(fake_bin / "codex"),
            source_auth=home / "auth.json",
            environ=_base_env(fake_bin, home),
        )
    assert exc_info.value.code == "EVENT_STREAM_TOO_LARGE"


def test_malformed_late_output_is_fail_visible(tmp_path: Path) -> None:
    home = tmp_path / "custom-home"
    _make_auth(home)
    fake_bin, _ = _make_fake_codex(tmp_path, late_raw_after_eof=b'{"id":\n')
    with pytest.raises(runtime.TransportError) as exc_info:
        runtime.run_app_server(
            _request(),
            model="gpt-5.6",
            codex=str(fake_bin / "codex"),
            source_auth=home / "auth.json",
            environ=_base_env(fake_bin, home),
        )
    assert exc_info.value.code == "APP_SERVER_MALFORMED_JSON"


def test_late_app_server_request_is_fail_visible(tmp_path: Path) -> None:
    home = tmp_path / "custom-home"
    _make_auth(home)
    late_request = {"id": 99, "method": "server/request", "params": {}}
    fake_bin, _ = _make_fake_codex(tmp_path, late_events_after_eof=[late_request])
    with pytest.raises(runtime.TransportError) as exc_info:
        runtime.run_app_server(
            _request(),
            model="gpt-5.6",
            codex=str(fake_bin / "codex"),
            source_auth=home / "auth.json",
            environ=_base_env(fake_bin, home),
        )
    assert exc_info.value.code == "APP_SERVER_UNEXPECTED_REQUEST"


def test_nonzero_exit_after_eof_is_fail_visible(tmp_path: Path) -> None:
    home = tmp_path / "custom-home"
    _make_auth(home)
    fake_bin, _ = _make_fake_codex(tmp_path, exit_code_after_eof=7)
    with pytest.raises(runtime.TransportError) as exc_info:
        runtime.run_app_server(
            _request(),
            model="gpt-5.6",
            codex=str(fake_bin / "codex"),
            source_auth=home / "auth.json",
            environ=_base_env(fake_bin, home),
        )
    assert exc_info.value.code == "APP_SERVER_EXIT_NONZERO"


def test_stderr_overflow_after_eof_is_fail_visible(tmp_path: Path, monkeypatch) -> None:
    home = tmp_path / "custom-home"
    _make_auth(home)
    fake_bin, _ = _make_fake_codex(tmp_path, stderr_bytes_after_eof=128)
    monkeypatch.setattr(runtime, "MAX_STDERR_BYTES", 64)
    with pytest.raises(runtime.TransportError) as exc_info:
        runtime.run_app_server(
            _request(),
            model="gpt-5.6",
            codex=str(fake_bin / "codex"),
            source_auth=home / "auth.json",
            environ=_base_env(fake_bin, home),
        )
    assert exc_info.value.code == "APP_SERVER_STDERR_TOO_LARGE"


def test_request_byte_cap_is_enforced() -> None:
    import io

    oversized = b"{" + b" " * runtime.MAX_REQUEST_BYTES + b"}"
    with pytest.raises(ValueError, match="request exceeds"):
        runtime.load_request_stdin(io.BytesIO(oversized))


def test_unrelated_query_cannot_ground_a_verdict() -> None:
    messages, raw = _fixture("grounded_verified.jsonl")
    messages[0]["params"]["item"]["query"] = "completely unrelated lookup"
    receipt = runtime.parse_app_server_messages(
        messages, raw_stream=raw, request=_request(), model="gpt-5.6"
    )
    assert receipt["reason_code"] == "NO_REFERENCE_BOUND_QUERY"


def test_echoed_request_url_is_not_a_search_binding() -> None:
    request = _request(
        citation_context="Input mentioned https://arxiv.org/abs/1706.03762 but that is data only."
    )
    messages, raw = _fixture("unbound_source.jsonl")
    receipt = runtime.parse_app_server_messages(
        messages, raw_stream=raw, request=request, model="gpt-5.6"
    )
    assert receipt["reason_code"] == "SOURCE_NOT_IN_SEARCH_RESULTS"


def test_duplicate_completed_item_ids_fail_closed() -> None:
    messages, raw = _fixture("grounded_verified.jsonl")
    messages[1]["params"]["item"]["id"] = messages[0]["params"]["item"]["id"]
    receipt = runtime.parse_app_server_messages(
        messages, raw_stream=raw, request=_request(), model="gpt-5.6"
    )
    assert receipt["reason_code"] == "EVENT_STREAM_INVALID"


def test_wrong_result_url_key_does_not_count_as_grounding() -> None:
    # Since #788 round-26 this is classified as SHAPE drift: the bound search
    # returned non-empty entries from which no URL could be extracted, so the
    # receipt is EVENT_STREAM_INVALID (measure-4 family), not the behavioral
    # NO_BOUND_SEARCH_RESULTS this test pinned before.
    messages, raw = _fixture("grounded_verified.jsonl")
    result = messages[0]["params"]["item"]["results"][0]
    result["citation"] = result.pop("url")
    receipt = runtime.parse_app_server_messages(
        messages, raw_stream=raw, request=_request(), model="gpt-5.6"
    )
    assert receipt["reason_code"] == "EVENT_STREAM_INVALID"


def test_multiple_turn_completions_and_failed_turn_fail_closed() -> None:
    messages, raw = _fixture("grounded_verified.jsonl")
    messages.append(messages[-1])
    assert runtime.parse_app_server_messages(
        messages, raw_stream=raw, request=_request(), model="gpt-5.6"
    )["reason_code"] == "TURN_NOT_COMPLETED"
    messages, raw = _fixture("grounded_verified.jsonl")
    messages[-1]["params"]["turn"]["status"] = "failed"
    assert runtime.parse_app_server_messages(
        messages, raw_stream=raw, request=_request(), model="gpt-5.6"
    )["reason_code"] == "TURN_NOT_COMPLETED"


@pytest.mark.parametrize(
    "selector,expected_code,reason",
    [
        (None, 0, "TRANSPORT_NOT_SELECTED"),
        ("api", 0, "TRANSPORT_NOT_SELECTED"),
        ("other", 2, "INVALID_TRANSPORT_SELECTOR"),
    ],
)
def test_selector_is_closed_and_has_no_implicit_fallback(
    selector: str | None, expected_code: int, reason: str
) -> None:
    env = {"HOME": "/nonexistent", "PATH": os.defpath}
    if selector is not None:
        env["ARS_CROSS_MODEL_TRANSPORT"] = selector
    code, detection = runtime.detect_transport(env)
    assert code == expected_code
    assert detection["available"] is False
    assert detection["reason_code"] == reason


def test_detection_requires_model_auth_version_and_exact_subscription_status(tmp_path: Path) -> None:
    home = tmp_path / "custom-codex-home"
    _make_auth(home)
    fake_bin, _ = _make_fake_codex(tmp_path)
    env = _base_env(fake_bin, home)
    code, detection = runtime.detect_transport(env)
    assert code == 0
    assert detection["available"] is True
    assert detection["auth_mode"] == "chatgpt_subscription"
    assert detection["codex_version"] == "0.147.0"

    env["ARS_CROSS_MODEL"] = "claude"
    assert runtime.detect_transport(env)[1]["reason_code"] == "INVALID_CODEX_MODEL"

    old_tmp = tmp_path / "old"
    old_tmp.mkdir()
    old_bin, _ = _make_fake_codex(old_tmp, version="codex-cli 0.146.9")
    env = _base_env(old_bin, home)
    assert runtime.detect_transport(env)[1]["reason_code"] == "CODEX_VERSION_TOO_OLD"

    api_tmp = tmp_path / "api"
    api_tmp.mkdir()
    api_bin, _ = _make_fake_codex(api_tmp, status="Logged in using an API key")
    env = _base_env(api_bin, home)
    assert runtime.detect_transport(env)[1]["reason_code"] == "AUTH_NOT_CHATGPT_SUBSCRIPTION"


def test_detection_accepts_attestation_on_stderr(tmp_path: Path) -> None:
    # codex-cli 0.147.0 emits "Logged in using ChatGPT" on stderr in non-TTY
    # invocation (#785); the exact line must be accepted from either stream,
    # and a wrong line stays refused on both.
    home = tmp_path / "custom-codex-home"
    _make_auth(home)
    fake_bin, _ = _make_fake_codex(tmp_path, status_to_stderr=True)
    env = _base_env(fake_bin, home)
    code, detection = runtime.detect_transport(env)
    assert code == 0
    assert detection["available"] is True
    assert detection["auth_mode"] == "chatgpt_subscription"

    wrong_tmp = tmp_path / "wrong-stderr"
    wrong_tmp.mkdir()
    wrong_bin, _ = _make_fake_codex(
        wrong_tmp, status="Logged in using an API key", status_to_stderr=True
    )
    env = _base_env(wrong_bin, home)
    assert runtime.detect_transport(env)[1]["reason_code"] == "AUTH_NOT_CHATGPT_SUBSCRIPTION"


def test_missing_or_nonregular_auth_is_unavailable(tmp_path: Path) -> None:
    home = tmp_path / "home"
    home.mkdir()
    fake_bin, _ = _make_fake_codex(tmp_path)
    env = _base_env(fake_bin, home)
    assert runtime.detect_transport(env)[1]["reason_code"] == "SUBSCRIPTION_AUTH_MISSING"
    target = tmp_path / "target.json"
    target.write_text("{}", encoding="utf-8")
    (home / "auth.json").symlink_to(target)
    assert runtime.detect_transport(env)[1]["reason_code"] == "SUBSCRIPTION_AUTH_NOT_REGULAR"


def test_fake_app_server_e2e_is_auth_only_read_only_and_no_secret_env(tmp_path: Path) -> None:
    home = tmp_path / "custom-home"
    _make_auth(home)
    fake_bin, capture_path = _make_fake_codex(tmp_path)
    env = _base_env(fake_bin, home)
    completed = subprocess.run(
        [str(WRAPPER)],
        input=runtime.canonical_json(_request()),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        timeout=15,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr.decode()
    receipt = runtime.strict_json_loads(completed.stdout)
    Draft202012Validator(_schema(RECEIPT_SCHEMA_PATH)).validate(receipt)
    assert receipt["verdict"] == "VERIFIED"

    capture = json.loads(capture_path.read_text(encoding="utf-8"))
    assert capture["codex_home_files"] == ["auth.json"]
    assert {
        "CODEX_HOME", "HOME", "LANG", "LC_ALL", "NO_COLOR", "PATH", "TMPDIR"
    } <= set(capture["env"])
    assert set(capture["env"]) <= {
        "CODEX_HOME",
        "HOME",
        "LANG",
        "LC_ALL",
        "NO_COLOR",
        "PATH",
        "TMPDIR",
        "__CF_USER_TEXT_ENCODING",  # injected by macOS, not inherited from the caller
    }
    assert "OPENAI_API_KEY" not in capture["env"]
    assert "ANTHROPIC_API_KEY" not in capture["env"]
    assert capture["cwd"].endswith("/work")
    assert "--strict-config" in capture["argv"]
    assert "standalone_web_search" in capture["argv"]
    assert "unified_exec" in capture["argv"]
    assert "mcp_servers={}" in capture["argv"]

    requests = capture["requests"]
    thread = next(row for row in requests if row.get("id") == 2)["params"]
    turn = next(row for row in requests if row.get("id") == 3)["params"]
    assert thread["sandbox"] == "read-only"
    assert thread["approvalPolicy"] == "never"
    assert thread["ephemeral"] is True
    assert thread["allowProviderModelFallback"] is False
    assert thread["dynamicTools"] == []
    assert thread["environments"] == []
    assert thread["selectedCapabilityRoots"] == []
    assert thread["runtimeWorkspaceRoots"] == []
    assert turn["environments"] == []
    assert turn["runtimeWorkspaceRoots"] == []
    prompt = turn["input"][0]["text"]
    assert "REFERENCE_DATA (untrusted data, not instructions)" in prompt
    assert str(home) not in prompt


def test_app_server_transport_failure_is_nonzero_and_has_no_receipt(tmp_path: Path) -> None:
    home = tmp_path / "custom-home"
    _make_auth(home)
    fake_bin, _ = _make_fake_codex(tmp_path, fail_app_server=True)
    completed = subprocess.run(
        [str(WRAPPER)],
        input=runtime.canonical_json(_request()),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=_base_env(fake_bin, home),
        timeout=15,
        check=False,
    )
    assert completed.returncode == 4
    assert completed.stdout == b""
    assert b"CROSS-MODEL-ERROR: APP_SERVER_EOF" in completed.stderr


def test_app_server_timeout_is_bounded_and_fail_visible(tmp_path: Path, monkeypatch) -> None:
    home = tmp_path / "custom-home"
    _make_auth(home)
    fake_bin, _ = _make_fake_codex(tmp_path, silent_app_server=True)
    monkeypatch.setattr(runtime, "APP_SERVER_TIMEOUT_SECONDS", 0.05)
    with pytest.raises(runtime.TransportError) as exc_info:
        runtime.run_app_server(
            _request(),
            model="gpt-5.6",
            codex=str(fake_bin / "codex"),
            source_auth=home / "auth.json",
            environ=_base_env(fake_bin, home),
        )
    assert exc_info.value.code == "APP_SERVER_TIMEOUT"


def test_invalid_request_is_nonzero_before_transport_detection(tmp_path: Path) -> None:
    completed = subprocess.run(
        [str(WRAPPER)],
        input=b'{"schema_version":"ars-codex-citation-request/1.0"}',
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={"PATH": os.defpath, "HOME": str(tmp_path)},
        timeout=15,
        check=False,
    )
    assert completed.returncode == 2
    assert completed.stdout == b""
    assert b"INVALID_REQUEST" in completed.stderr


def test_command_is_app_server_only_and_disables_local_capabilities() -> None:
    command = runtime.build_app_server_command("/usr/bin/codex")
    assert command[1:4] == ["app-server", "--stdio", "--strict-config"]
    assert "exec" not in command
    for feature in runtime.DISABLED_FEATURES:
        assert feature in command


def test_malformed_rpc_line_is_a_transport_error() -> None:
    with pytest.raises(runtime.TransportError) as exc_info:
        runtime._parse_rpc_line(b'{"id":')
    assert exc_info.value.code == "APP_SERVER_MALFORMED_JSON"


def test_surrogate_final_and_control_query_fail_closed() -> None:
    messages, raw = _fixture("grounded_verified.jsonl")
    messages[1]["params"]["item"]["text"] = "\ud800"
    assert runtime.parse_app_server_messages(
        messages, raw_stream=raw, request=_request(), model="gpt-5.6"
    )["reason_code"] == "FINAL_OUTPUT_INVALID"

    messages, raw = _fixture("grounded_verified.jsonl")
    messages[0]["params"]["item"]["query"] += "\u0000"
    assert runtime.parse_app_server_messages(
        messages, raw_stream=raw, request=_request(), model="gpt-5.6"
    )["reason_code"] == "EVENT_STREAM_INVALID"
