#!/usr/bin/env python3
"""Deterministic presentation of a #655 claim-standing probe (design §5.3/§5.4).

Renders the three inseparable parts — consent/recorded-search metadata, the
complete candidate ledger including culled records and failures, and the
selected-candidate distribution with per-source rows — as inert Markdown.
Every stance statement uses the search-bounded vocabulary; every category
renders even when empty, with the fixed empty wording; the primary denominator
is always all selected work families, and a performed-only distribution may
appear only beside it, marked secondary. Provider-controlled text is escaped
before rendering. A stance record is re-verified against the exact plan and
ledger before rendering, so a stale record cannot be presented as current.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

try:
    from scripts import build_claim_standing_candidate_ledger as substrate
    from scripts import claim_standing_stance_runner as stance_runner
except ImportError:  # direct script execution
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import build_claim_standing_candidate_ledger as substrate  # noqa: E402
    import claim_standing_stance_runner as stance_runner  # noqa: E402

STANCE_BUCKETS = (
    "support",
    "contradict",
    "mixed",
    "not_addressed",
    "INSUFFICIENT_EVIDENCE",
    "AMBIGUOUS",
)
COVERAGE_LABELS = {
    "abstract": "ABSTRACT",
    "session_held_full_text": "SESSION-HELD FULL TEXT",
    "metadata_only": "METADATA ONLY",
}


def _inert(value: Any) -> str:
    """Escape provider-controlled text so rendered Markdown stays inert."""
    if value is None:
        return "(none)"
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("`", "&#96;")
    )


def render_view(
    plan: dict[str, Any],
    ledger_value: dict[str, Any],
    stance_record: dict[str, Any] | None,
    evidence_rows: list[dict[str, Any]],
) -> str:
    substrate.validate_schema(
        plan, substrate.plan_schema_filename(plan), "query plan"
    )
    substrate.validate_plan(plan)
    substrate.validate_schema(
        ledger_value, "candidate_ledger.schema.json", "candidate ledger"
    )
    if ledger_value["query_plan_sha256"] != plan["plan_sha256"]:
        stance_runner._fail("candidate ledger is bound to a different query plan")
    if stance_record is not None:
        stance_runner.validate_stance_record(
            plan, ledger_value, stance_record, evidence_rows
        )

    consent = plan["consent"]
    out: list[str] = []
    out.append("STANCE CLASSIFICATION UNMEASURED")
    out.append("")
    out.append(f"# Claim-standing probe {_inert(plan['probe_id'])}")
    out.append("")
    out.append(
        "Advisory only (layer LLM-ADVISORY, gate effect none): this view "
        "reports what one recorded, capped search found. It is bounded by "
        "that search, fallible, and never a statement about anything beyond it."
    )
    out.append("")

    out.append("## Consent and recorded search")
    out.append("")
    out.append(f"- Claim `{_inert(plan['claim']['claim_id'])}`: {_inert(plan['claim']['claim_text'])}")
    out.append(
        f"- Consent receipt `{_inert(consent['consent_receipt_id'])}` — "
        f"decision {consent['decision']}, accepted {consent['accepted_at']}, "
        f"local persistence {consent['local_persistence']}"
    )
    for query in plan["queries"]:
        out.append(
            f"- Query `{_inert(query['query_id'])}` ({query['construction']}): "
            f"{_inert(query['accepted_query_text'])} → indexes "
            + ", ".join(_inert(index) for index in query["index_targets"])
        )
    caps = plan["caps"]
    out.append(
        f"- Caps: {caps['max_queries']} queries, {caps['max_indexes']} indexes, "
        f"{caps['max_hits_per_query_index']} hits per query/index, "
        f"{caps['max_raw_hits']} raw rows, "
        f"{caps['max_selected_work_families']} selected families"
    )
    failures = [
        attempt
        for attempt in ledger_value["attempts"]
        if attempt["outcome"] != "success"
    ]
    if failures:
        out.append(
            "- Recorded search with failures — every failed attempt stays "
            "visible below; nothing was topped up or silently retried:"
        )
        for attempt in failures:
            out.append(
                f"  - attempt `{_inert(attempt['attempt_id'])}` "
                f"({_inert(attempt['index_id'])} / {_inert(attempt['query_id'])}): "
                f"{attempt['outcome']}"
            )
    out.append(f"- Retrieval completed at {ledger_value['completed_at']}")
    out.append("")

    out.append("## Candidate ledger")
    out.append("")
    counts = ledger_value["counts"]
    out.append(
        f"- Raw hits {counts['raw_hits']}, work families "
        f"{counts['work_families']}, selected "
        f"{counts['selected_work_families']}"
    )
    for state, value in sorted(counts["raw_hit_state_counts"].items()):
        out.append(f"  - {state}: {value}")
    hits_by_id = {hit["raw_hit_id"]: hit for hit in ledger_value["raw_hits"]}
    for hit in ledger_value["raw_hits"]:
        detail = (
            f"- `{_inert(hit['raw_hit_id'])}` [{hit['terminal_state']}] "
            f"{_inert(hit['title'])} "
            f"({_inert(hit['index_id'])} rank {hit['provider_rank']}"
        )
        if hit.get("year") is not None:
            detail += f", {hit['year']}"
        detail += ")"
        if hit["terminal_state"] == "duplicate_version":
            detail += f" → retained family {_inert(hit.get('duplicate_of_work_family_id'))}"
        out.append(detail)
    out.append("")

    out.append("## Claim standing (advisory)")
    out.append("")
    if stance_record is None:
        out.append("Stance classification was not run under this consent.")
        out.append("")
        return "\n".join(out)

    distribution = stance_record["distribution"]
    selected_total = distribution["selected_total"]
    indexes = ", ".join(
        sorted({provider["index_id"] for provider in plan["provider_roster"]})
    )
    queries = ", ".join(query["query_id"] for query in plan["queries"])
    out.append(
        f"Denominator: all {selected_total} selected work families "
        "(including not-checked and failed candidates)."
    )
    for bucket in STANCE_BUCKETS:
        count = distribution[bucket]
        if count:
            out.append(
                f"- Within the recorded search of {_inert(indexes)} using "
                f"{_inert(queries)}, {count}/{selected_total} selected "
                f"candidates were classified {bucket}."
            )
        else:
            out.append(
                f"- No {bucket} sources were found among the selected "
                "candidates within this recorded search."
            )
    not_checked = distribution["not_checked"]
    if not_checked:
        out.append(
            f"- {not_checked}/{selected_total} selected candidates were not "
            "checked or failed; see the candidate ledger."
        )
    else:
        out.append(
            f"- 0/{selected_total} selected candidates were not checked or "
            "failed; see the candidate ledger."
        )
        out.append(
            "- No not_checked sources were found among the selected candidates "
            "within this recorded search."
        )
    performed = sum(distribution[bucket] for bucket in STANCE_BUCKETS)
    out.append(
        f"- Secondary view (performed-only, shown beside the all-selected "
        f"denominator, never instead of it): {performed} performed of "
        f"{selected_total} selected."
    )
    out.append("")
    out.append("### Per-source rows")
    out.append("")
    for row in stance_record["rows"]:
        hit = hits_by_id[row["canonical_raw_hit_id"]]
        outcome = (
            row["stance"] if row["check_state"] == "performed" else row["failure_state"]
        )
        line = (
            f"- {_inert(hit['title'])}"
            f" ({_inert(hit.get('year'))}) — coverage "
            f"{COVERAGE_LABELS[row['evidence_scope']]}, {row['check_state']}: "
            f"{outcome}"
        )
        if row["conditions_noted"]:
            line += f"; conditions noted: {_inert(row['conditions_noted'])}"
        if row["evidence_row_refs"]:
            refs = ", ".join(
                f"`{_inert(ref['row_id'])}`" for ref in row["evidence_row_refs"]
            )
            line += f"; evidence rows: {refs}"
        if hit.get("landing_url"):
            line += f"; source: {_inert(hit['landing_url'])}"
        out.append(line)
    out.append("")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query-plan", type=Path, required=True)
    parser.add_argument("--candidate-ledger", type=Path, required=True)
    parser.add_argument("--stance-record", type=Path)
    parser.add_argument("--evidence-rows", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        plan = substrate.load_json(args.query_plan)
        ledger_value = substrate.load_json(args.candidate_ledger)
        stance_record = (
            substrate.load_json(args.stance_record) if args.stance_record else None
        )
        evidence_rows = (
            substrate.load_json(args.evidence_rows)["rows"]
            if args.evidence_rows
            else []
        )
        text = render_view(plan, ledger_value, stance_record, evidence_rows)
        if args.output:
            if args.output.exists():
                stance_runner._fail(
                    f"refusing to overwrite existing output {args.output}"
                )
            args.output.write_text(text, encoding="utf-8", newline="\n")
        else:
            print(text, end="")
    except (
        stance_runner.StanceError,
        substrate.LedgerError,
        OSError,
        ValueError,
        KeyError,
    ) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
