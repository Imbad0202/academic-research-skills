"""Closed receipt-contract validation shared by run_fleet.py and score_run.py.

One implementation, imported by both consumers, so the runner's persisted
cells and the scorer's metrics can never diverge on what counts as a valid
receipt (#788 rounds 13-17). A COMPLETE stdlib mirror of
`shared/contracts/cross_model/codex_citation_receipt.schema.json`: exact key
sets (additionalProperties: false at every level), per-field patterns and
length bounds, array caps, and the per-verdict conditional constraints.
"""
import re

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
    if rec["containment"] != EXPECTED_CONTAINMENT:
        bail(f"containment flags {rec['containment']!r}")
    if not isinstance(rec["request_id"], str) or not (1 <= len(rec["request_id"]) <= 128) or not _IDENTIFIER.fullmatch(rec["request_id"]):
        bail(f"bad request_id {rec['request_id']!r}")
    if not isinstance(rec["model"], str) or len(rec["model"]) > 128 or not _MODEL_ID.fullmatch(rec["model"]):
        bail(f"bad model {rec['model']!r}")
    if not isinstance(rec["detail"], str) or len(rec["detail"]) > 2048:
        bail("detail is not a string within 2048 chars")
    for field in ("request_digest", "event_stream_digest"):
        if not isinstance(rec[field], str) or not _HEX64.fullmatch(rec[field]):
            bail(f"{field} is not a sha256 hex digest")
    if rec["verdict"] not in VERDICTS:
        bail(f"unknown verdict {rec['verdict']!r}")
    if not isinstance(rec["searched"], bool):
        bail("searched is not a bool")
    if rec["reason_code"] is not None and rec["reason_code"] not in (SHAPE_GUARD_CODES | BEHAVIOR_CODES):
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
