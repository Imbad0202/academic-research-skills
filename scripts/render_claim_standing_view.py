#!/usr/bin/env python3
"""Deterministic presentation of a #655 claim-standing probe (design §5.3/§5.4).

Renders the three inseparable parts — consent/recorded-search metadata, the
complete candidate ledger including culled records and failures, and the
selected-candidate distribution with per-source rows — as inert Markdown.
Every stance statement uses the search-bounded vocabulary; every category
renders even when empty, with the fixed empty wording; the primary denominator
is always all selected work families, and a performed-only distribution may
appear only beside it, marked secondary. Provider-controlled text is escaped
and line-break-flattened before rendering so it can neither forge a bounded
sentence nor smuggle active Markdown. A stance record is re-verified against
the exact plan and ledger before rendering, so a stale record cannot be
presented as current. Persisting the view requires the same
`explicit_local_export` consent and hash-bound output path discipline as every
other Track A artifact.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import sys
import unicodedata
from typing import Any

try:
    from scripts import build_claim_standing_candidate_ledger as substrate
    from scripts import claim_standing_stance_runner as stance_runner
except ImportError:  # direct script execution
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import build_claim_standing_candidate_ledger as substrate  # noqa: E402
    import claim_standing_stance_runner as stance_runner  # noqa: E402

VIEW_SUFFIX = ".view.md"
COVERAGE_LABELS = {
    "abstract": "ABSTRACT",
    "session_held_full_text": "SESSION-HELD FULL TEXT",
    "metadata_only": "METADATA ONLY",
}
COVERAGE_PROSE = {
    "abstract": "abstract",
    "session_held_full_text": "full text",
    "metadata_only": "metadata only",
}
_LINE_BREAKS = re.compile(r"[\r\n\u0085\u2028\u2029]+")
_CONTROL_OR_FORMAT = re.compile(
    r"[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f-\u009f"
    r"\u200e\u200f\u202a-\u202e\u2066-\u2069]"
)


def _fail(message: str) -> None:
    raise stance_runner.StanceError(message)


def _inert(value: Any) -> str:
    """Escape and flatten provider-controlled text so rendered Markdown stays
    inert: no HTML, no backticks, no links/images, and no injected lines that
    could forge a bounded sentence."""
    if value is None:
        return "(none)"
    text = _LINE_BREAKS.sub(" ", str(value))
    # Every control (Cc) and format (Cf) character is stripped — terminal
    # escapes, bidi controls, zero-width marks — with tab flattened to space.
    text = "".join(
        " " if ch == "\t" else ch
        for ch in text
        if ch == "\t" or unicodedata.category(ch) not in ("Cc", "Cf")
    )
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("`", "&#96;")
        .replace("[", "&#91;")
        .replace("]", "&#93;")
        .replace("!", "&#33;")
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
    stance_runner._require_bound_ledger(plan, ledger_value)
    if stance_record is not None:
        stance_runner.validate_stance_record(
            plan, ledger_value, stance_record, evidence_rows
        )

    consent = plan["consent"]
    out: list[str] = []
    out.append(stance_runner.UNMEASURED_BANNER)
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
    out.append(
        f"- Claim `{_inert(plan['claim']['claim_id'])}`: "
        f"{_inert(plan['claim']['claim_text'])}"
    )
    out.append(
        f"- Consent receipt `{_inert(consent['consent_receipt_id'])}` — "
        f"decision {consent['decision']}, accepted {consent['accepted_at']}, "
        f"local persistence {consent['local_persistence']}"
    )
    if plan.get("stance_plan"):
        stance_plan = plan["stance_plan"]
        retention = (
            _inert(stance_plan["retention_reference"])
            if stance_plan["retention_state"] == "known"
            else "unknown"
        )
        out.append(
            f"- Stance provider (consented): {_inert(stance_plan['provider_identity'])} / "
            f"{_inert(stance_plan['model_identity'])}; provider retention: {retention}"
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
    out.append("- Index attempts:")
    for attempt in ledger_value["attempts"]:
        out.append(
            f"  - `{_inert(attempt['attempt_id'])}` "
            f"({_inert(attempt['index_id'])} / {_inert(attempt['query_id'])}): "
            f"{attempt['outcome']}, retained {attempt['retained_hit_count']}"
        )
    if any(a["outcome"] != "success" for a in ledger_value["attempts"]):
        out.append(
            "- This is a recorded search with failures — every failed attempt "
            "stays visible above; nothing was topped up or silently retried."
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
            detail += f" → retained hit `{_inert(hit.get('retained_raw_hit_id'))}`"
        out.append(detail)
    out.append("")

    out.append("## Claim standing (advisory)")
    out.append("")
    if stance_record is None:
        out.append("Stance classification was not run under this consent.")
        out.append("")
        return "\n".join(out)

    families_by_id = {
        family["work_family_id"]: family
        for family in ledger_value["work_families"]
    }
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
    for bucket in stance_runner.STANCES:
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
    out.append(
        f"- {not_checked}/{selected_total} selected candidates were not "
        "checked or failed; see the candidate ledger."
    )
    if not not_checked:
        out.append(
            "- No not_checked sources were found among the selected candidates "
            "within this recorded search."
        )
    performed = sum(distribution[bucket] for bucket in stance_runner.STANCES)
    out.append(
        f"- Secondary view (performed-only, shown beside the all-selected "
        f"denominator, never instead of it): {performed} performed of "
        f"{selected_total} selected."
    )
    out.append("")
    out.append("### Per-source rows")
    out.append("")
    for row in stance_record["rows"]:
        hit = hits_by_id.get(row["canonical_raw_hit_id"])
        family = families_by_id.get(row["work_family_id"])
        if hit is None or family is None:
            _fail(
                f"stance row {row['work_family_id']!r} names a candidate "
                "absent from the ledger"
            )
        authors = ", ".join(
            _inert(author.get("family"))
            for author in hit["authors"][:3]
        ) or "(no authors returned)"
        outcome = (
            row["stance"] if row["check_state"] == "performed" else row["failure_state"]
        )
        line = (
            f"- {_inert(hit['title'])} — {authors}"
            f" ({_inert(hit.get('year'))}); found by "
            + ", ".join(f"`{_inert(q)}`" for q in family["query_ids"])
            + " on "
            + ", ".join(_inert(i) for i in family["index_ids"])
            + f"; provider rank {hit['provider_rank']}"
            f"; relevance {family['relevance']['state']}"
            f"; coverage {COVERAGE_LABELS[row['evidence_scope']]}"
        )
        if row["check_state"] == "performed":
            line += (
                f". This candidate's inspected "
                f"{COVERAGE_PROSE[row['evidence_scope']]} was classified "
                f"{outcome} relative to claim "
                f"`{_inert(plan['claim']['claim_id'])}`."
            )
        else:
            line += f"; {row['check_state']}: {outcome}."
        if row["conditions_noted"]:
            line += f" Conditions noted: {_inert(row['conditions_noted'])}."
        if row["evidence_row_refs"]:
            refs = ", ".join(
                f"`{_inert(ref['row_id'])}`" for ref in row["evidence_row_refs"]
            )
            line += f" Evidence rows: {refs}."
        other_versions = [
            hits_by_id[member]
            for member in family["member_raw_hit_ids"]
            if member != family["canonical_raw_hit_id"]
        ]
        if other_versions:
            line += " Other versions: " + "; ".join(
                f"`{_inert(v['raw_hit_id'])}` ({_inert(v['index_id'])} rank "
                f"{v['provider_rank']})"
                for v in other_versions
            ) + "."
        if hit.get("landing_url"):
            line += f" Source: {_inert(hit['landing_url'])}"
        out.append(line)
    out.append("")
    return "\n".join(out)


def _write_view_exclusive(path: Path, text: str) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if os.name != "nt":
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
        handle.flush()
        os.fsync(handle.fileno())
    if os.name != "nt":
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query-plan", type=Path, required=True)
    parser.add_argument("--candidate-ledger", type=Path, required=True)
    parser.add_argument("--stance-record", type=Path)
    parser.add_argument("--evidence-rows", type=Path)
    parser.add_argument(
        "--output",
        type=Path,
        help=(
            "requires explicit_local_export consent; must equal the consent's "
            f"authorized_output_path plus '{VIEW_SUFFIX}'"
        ),
    )
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
            consent = plan["consent"]
            if consent["local_persistence"] != "explicit_local_export":
                _fail(
                    "the hash-bound consent says session_only: this CLI "
                    "refuses to persist a rendered view"
                )
            expected = substrate.authorized_export_path(plan, VIEW_SUFFIX)
            if str(args.output) != str(expected):
                _fail(
                    "output does not match the hash-bound consent: the view "
                    f"may be written only to {expected}"
                )
            if args.output.exists():
                _fail(f"refusing to overwrite existing output {args.output}")
            _write_view_exclusive(args.output, text)
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
