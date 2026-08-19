"""Closed receipt-contract validation shared by run_fleet.py and score_run.py.

One implementation, imported by both consumers, so the runner's persisted
cells and the scorer's metrics can never diverge on what counts as a valid
receipt (#788 rounds 13-17). A COMPLETE stdlib mirror of
`shared/contracts/cross_model/codex_citation_receipt.schema.json`: exact key
sets (additionalProperties: false at every level), per-field patterns and
length bounds, array caps, and the per-verdict conditional constraints.
"""
import hashlib
import json
import re
from datetime import datetime

MODEL_SHORT = {"gpt-5.5": "bk55", "gpt-5.6-sol": "bk56"}
REPEATS = 3

# Frozen probe-set digest (the sha256 recorded in the audit report), shared by
# the runner's pre-flight and the scorer's gate so 180 paid calls can never be
# spent on a fixture the scorer will refuse (#788 round-24 P2). Hashing
# normalizes CRLF to LF first: a Windows checkout with core.autocrlf must not
# read as probe drift (#788 round-24 P2).
EXPECTED_PROBE_SHA256 = "6db7c1ffeb20d4b6819010f7c7ca79f422acfef560c14cfbaf6896c78db305c2"


def verify_probe_bytes(raw: bytes) -> bytes:
    normalized = raw.replace(b"\r\n", b"\n")
    actual = hashlib.sha256(normalized).hexdigest()
    if actual != EXPECTED_PROBE_SHA256:
        raise SystemExit(
            f"PROBE SET DRIFT: sha256 {actual} != frozen {EXPECTED_PROBE_SHA256} — "
            "labels/ground truth changed; refusing."
        )
    return normalized

RECEIPT_KEYS = {
    "schema_version", "request_id", "transport", "auth_mode", "model",
    "request_digest", "event_stream_digest", "verdict", "searched",
    "reason_code", "detail", "search_queries", "sources", "containment",
}
VERDICTS = {"VERIFIED", "MISMATCH", "NOT_FOUND", "NOT_SEARCHED"}
SHAPE_GUARD_CODES = {
    "EVENT_STREAM_INVALID", "FINAL_OUTPUT_INVALID", "TURN_NOT_COMPLETED",
    "FORBIDDEN_TOOL_EVENT",
}
BEHAVIOR_CODES = {
    "MODEL_RETURNED_NOT_SEARCHED", "NO_BOUND_SEARCH_RESULTS",
    "NO_REFERENCE_BOUND_QUERY", "MISSING_SOURCE_FOR_VERDICT",
    "SOURCE_NOT_IN_SEARCH_RESULTS",
}
EXPECTED_CONTAINMENT = {
    "empty_working_root": True,
    "ephemeral_auth_home": True,
    "forbidden_event_scan": True,
    "local_tools_disabled": True,
    "standalone_search_results_required": True,
}
_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_IDENTIFIER = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
_MODEL_ID = re.compile(r"^gpt-[a-z0-9][a-z0-9._-]*$")
_EVENT_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]*$")
_HTTPS_URL = re.compile(r"^https://[^\s\x00-\x1f\x7f]+$")


def validate_receipt(rec: dict, where: str) -> None:
    """Raise SystemExit on the first contract violation; return on success."""
    def bail(msg: str) -> None:
        raise SystemExit(f"RECEIPT CONTRACT: {msg} at {where}")

    if not isinstance(rec, dict):
        bail("receipt is not an object")
    if set(rec) != RECEIPT_KEYS:
        extra = sorted(set(rec) - RECEIPT_KEYS)
        missing = sorted(RECEIPT_KEYS - set(rec))
        bail(f"key set mismatch (missing={missing} extra={extra})")
    if rec["schema_version"] != "ars-codex-citation-receipt/1.0":
        bail(f"bad schema_version {rec['schema_version']!r}")
    if rec["transport"] != "codex_subscription":
        bail(f"bad transport {rec['transport']!r}")
    if rec["auth_mode"] != "chatgpt_subscription":
        bail(f"bad auth_mode {rec['auth_mode']!r}")
    containment = rec["containment"]
    if (
        not isinstance(containment, dict)
        or set(containment) != set(EXPECTED_CONTAINMENT)
        # `1 == True` in Python; the schema requires boolean constants, so
        # identity, not equality (#788 round-18 P2).
        or any(containment[k] is not True for k in EXPECTED_CONTAINMENT)
    ):
        bail(f"containment flags {containment!r}")
    if not isinstance(rec["request_id"], str) or not (1 <= len(rec["request_id"]) <= 128) or not _IDENTIFIER.fullmatch(rec["request_id"]):
        bail(f"bad request_id {rec['request_id']!r}")
    if not isinstance(rec["model"], str) or len(rec["model"]) > 128 or not _MODEL_ID.fullmatch(rec["model"]):
        bail(f"bad model {rec['model']!r}")
    if not isinstance(rec["detail"], str) or len(rec["detail"]) > 2048:
        bail("detail is not a string within 2048 chars")
    for field in ("request_digest", "event_stream_digest"):
        if not isinstance(rec[field], str) or not _HEX64.fullmatch(rec[field]):
            bail(f"{field} is not a sha256 hex digest")
    # Membership tests need hashable operands: an array/object verdict must
    # become a contract failure, not an uncaught TypeError that escapes the
    # runner's SystemExit handling (#788 round-18 P2).
    if not isinstance(rec["verdict"], str) or rec["verdict"] not in VERDICTS:
        bail(f"unknown verdict {rec['verdict']!r}")
    if not isinstance(rec["searched"], bool):
        bail("searched is not a bool")
    if rec["reason_code"] is not None and (
        not isinstance(rec["reason_code"], str)
        or rec["reason_code"] not in (SHAPE_GUARD_CODES | BEHAVIOR_CODES)
    ):
        bail(f"unknown reason_code {rec['reason_code']!r}")

    queries = rec["search_queries"]
    if not isinstance(queries, list) or len(queries) > 32:
        bail("search_queries is not a list of at most 32 entries")
    for q in queries:
        if (
            not isinstance(q, dict)
            or set(q) != {"search_item_id", "query"}
            or not isinstance(q["search_item_id"], str)
            or not (1 <= len(q["search_item_id"]) <= 200)
            or not _EVENT_ID.fullmatch(q["search_item_id"])
            or not isinstance(q["query"], str)
            or not (1 <= len(q["query"]) <= 2048)
        ):
            bail(f"malformed search_queries entry {q!r}")

    sources = rec["sources"]
    if not isinstance(sources, list) or len(sources) > 16:
        bail("sources is not a list of at most 16 entries")
    for s in sources:
        if (
            not isinstance(s, dict)
            or set(s) != {"url", "search_item_id", "result_index", "search_result_digest"}
            or not isinstance(s["url"], str)
            or len(s["url"]) > 2048
            or not _HTTPS_URL.fullmatch(s["url"])
            or len(s["url"]) <= len("https://")
            or not isinstance(s["search_item_id"], str)
            or not (1 <= len(s["search_item_id"]) <= 200)
            or not _EVENT_ID.fullmatch(s["search_item_id"])
            or not isinstance(s["result_index"], int)
            or isinstance(s["result_index"], bool)
            or not 0 <= s["result_index"] <= 127
            or not isinstance(s["search_result_digest"], str)
            or not _HEX64.fullmatch(s["search_result_digest"])
        ):
            bail(f"unbound or malformed source {s!r}")

    # Every source must bind to a RETAINED search query: a source whose
    # search_item_id has no corresponding entry in search_queries carries no
    # retained evidence and must not count as grounding (#788 round-20 P2).
    query_ids = {q["search_item_id"] for q in queries}
    for s in sources:
        if s["search_item_id"] not in query_ids:
            bail(f"source bound to unretained search item {s['search_item_id']!r}")

    # Per-verdict cross-field invariants (schema allOf + transport semantics).
    if rec["verdict"] in {"VERIFIED", "MISMATCH"}:
        if not rec["searched"] or not sources:
            bail(f"{rec['verdict']} without grounded bound sources")
        if rec["reason_code"] is not None:
            bail(f"{rec['verdict']} carries reason_code {rec['reason_code']!r}")
    elif rec["verdict"] == "NOT_FOUND":
        if not rec["searched"]:
            bail("NOT_FOUND without searched=true")
        if sources:
            bail("NOT_FOUND carries sources")
        if rec["reason_code"] is not None:
            bail(f"NOT_FOUND carries reason_code {rec['reason_code']!r}")
    else:  # NOT_SEARCHED
        if rec["searched"]:
            bail("NOT_SEARCHED with searched=true")
        if sources:
            bail("NOT_SEARCHED carries sources")
        if queries:
            bail("NOT_SEARCHED carries search_queries")
        if not isinstance(rec["reason_code"], str):
            bail("NOT_SEARCHED without a reason_code")
    if rec["searched"] and not queries:
        bail("searched without search_queries")


def canonical_json(value) -> bytes:
    # Byte-identical to scripts/cross_model_codex_transport.py::canonical_json.
    return json.dumps(
        value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def validate_row(row: dict, expected_model: str, ref: dict) -> None:
    """Complete row-level validation shared by the scorer and the runner's
    resume preflight (#788 round-25 P1): contradictory receipt+error rows,
    outer identity, exact-integer repeat, full ISO timestamp, sane latency,
    the receipt identity binding to the probe row, and the closed receipt
    contract. Raises SystemExit on the first violation.
    """
    where = f"{expected_model} {row.get('ref_id')} r{row.get('repeat')}"
    if row.get("error") and row.get("receipt") is not None:
        raise SystemExit(f"CONTRADICTORY ROW: {where} carries both a receipt and error={row.get('error')!r}")
    if row.get("model") != expected_model:
        raise SystemExit(f"IDENTITY: row model {row.get('model')!r} in the {expected_model} fleet")
    if row.get("ref_id") != ref["id"]:
        raise SystemExit(f"IDENTITY: row ref_id {row.get('ref_id')!r} != {ref['id']!r}")
    rep = row.get("repeat")
    if isinstance(rep, bool) or not isinstance(rep, int) or not 1 <= rep <= REPEATS:
        raise SystemExit(f"IDENTITY: non-integer repeat {rep!r} at {where}")
    try:
        datetime.strptime(str(row.get("ts", "")), "%Y-%m-%dT%H:%M:%S%z")
    except ValueError:
        raise SystemExit(f"UNDATED ROW: {where} has ts={row.get('ts')!r}")
    ws = row.get("wall_seconds")
    if isinstance(ws, bool) or not isinstance(ws, (int, float)) or not (0 <= ws < 10_000):
        raise SystemExit(f"BAD LATENCY: {where} wall_seconds={ws!r}")
    rec = row.get("receipt")
    if rec is None:
        return  # failed trial; carried as a misfire by both consumers
    expected_id = f"{MODEL_SHORT[expected_model]}-{ref['id']}-r{rep}"
    expected_digest = hashlib.sha256(canonical_json({
        "schema_version": "ars-codex-citation-request/1.0",
        "request_id": expected_id,
        "reference_text": ref["reference_text"],
        "citation_context": ref["citation_context"],
    })).hexdigest()
    if rec.get("model") != expected_model:
        raise SystemExit(f"IDENTITY: receipt.model {rec.get('model')!r} != {expected_model} at {expected_id}")
    if rec.get("request_id") != expected_id:
        raise SystemExit(f"IDENTITY: receipt.request_id {rec.get('request_id')!r} != {expected_id}")
    if rec.get("request_digest") != expected_digest:
        raise SystemExit(
            f"IDENTITY: request_digest mismatch at {expected_id} — the receipt does not "
            f"bind to this probe row (edited fixture or mis-associated fleet)"
        )
    validate_receipt(rec, where)
