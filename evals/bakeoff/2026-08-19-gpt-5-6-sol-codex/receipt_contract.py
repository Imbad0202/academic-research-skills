"""Closed receipt-contract validation shared by run_fleet.py and score_run.py.

One implementation, imported by both consumers, so the runner's persisted
cells and the scorer's metrics can never diverge on what counts as a valid
receipt (#788 rounds 13-15). Mirrors
`shared/contracts/cross_model/codex_citation_receipt.schema.json` semantics
in stdlib form: exact key set, per-field types/formats, and per-verdict
cross-field invariants.
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
    if rec["auth_mode"] not in ("chatgpt_subscription", None):
        bail(f"bad auth_mode {rec['auth_mode']!r}")
    if rec["containment"] != EXPECTED_CONTAINMENT:
        bail(f"containment flags {rec['containment']!r}")
    for field in ("request_id", "model", "detail"):
        if not isinstance(rec[field], str):
            bail(f"{field} is not a string")
    for field in ("request_digest", "event_stream_digest"):
        if not isinstance(rec[field], str) or not _HEX64.fullmatch(rec[field]):
            bail(f"{field} is not a sha256 hex digest")
    if rec["verdict"] not in VERDICTS:
        bail(f"unknown verdict {rec['verdict']!r}")
    if not isinstance(rec["searched"], bool):
        bail("searched is not a bool")
    if not isinstance(rec["search_queries"], list):
        bail("search_queries is not a list")
    for q in rec["search_queries"]:
        if not isinstance(q, dict) or not isinstance(q.get("query"), str) or not isinstance(q.get("search_item_id"), str):
            bail(f"malformed search_queries entry {q!r}")
    if not isinstance(rec["sources"], list):
        bail("sources is not a list")
    for s in rec["sources"]:
        if (
            not isinstance(s, dict)
            or not isinstance(s.get("url"), str)
            or not s["url"].startswith("https://")
            or not isinstance(s.get("search_item_id"), str)
            or not isinstance(s.get("result_index"), int)
            or not isinstance(s.get("search_result_digest"), str)
            or not _HEX64.fullmatch(s["search_result_digest"])
        ):
            bail(f"unbound or malformed source {s!r}")
    # Per-verdict cross-field invariants.
    if rec["verdict"] in {"VERIFIED", "MISMATCH"}:
        if not rec["searched"] or not rec["sources"]:
            bail(f"{rec['verdict']} without grounded bound sources")
        if rec["reason_code"] is not None:
            bail(f"{rec['verdict']} carries reason_code {rec['reason_code']!r}")
    elif rec["verdict"] == "NOT_FOUND":
        if not rec["searched"]:
            bail("NOT_FOUND without searched=true")
        if rec["sources"]:
            bail("NOT_FOUND carries sources")
        if rec["reason_code"] is not None:
            bail(f"NOT_FOUND carries reason_code {rec['reason_code']!r}")
    else:  # NOT_SEARCHED
        if rec["searched"]:
            bail("NOT_SEARCHED with searched=true")
        if rec["sources"]:
            bail("NOT_SEARCHED carries sources")
        if rec["reason_code"] not in (SHAPE_GUARD_CODES | BEHAVIOR_CODES):
            bail(f"unknown reason_code {rec['reason_code']!r}")
    if rec["searched"] and not rec["search_queries"]:
        bail("searched without search_queries")
