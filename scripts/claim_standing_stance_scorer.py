#!/usr/bin/env python3
"""Mechanical stance scorer for the #655 claim-standing seed set.

Compares one subject run's frozen enum outputs against adjudicated expert
labels, without asking any model to reinterpret either side. Deterministic and
file-only. The emitted report is a raw comparison artifact, NOT a
heldout-measurement contract row.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

REPO_ROOT = Path(__file__).resolve().parents[1]
SUITE_ROOT = REPO_ROOT / "evals" / "heldout" / "claim_standing_probe"
SET_SCHEMA = SUITE_ROOT / "heldout_stance_set.schema.json"
ADJUDICATED_SCHEMA = SUITE_ROOT / "adjudicated_labels.schema.json"
SUBJECT_SCHEMA = SUITE_ROOT / "subject_output.schema.json"
REPORT_SCHEMA = SUITE_ROOT / "stance_score_report.schema.json"

FULL_ROW_FIELDS = (
    "relevance",
    "check_state",
    "stance",
    "failure_state",
    "evidence_scope",
)
# Column for a gold-performed row whose subject abstained: the abstention
# stays in every stance-recall denominator instead of vanishing from it.
ABSTAINED = "NOT_CHECKED"


class ScoreError(RuntimeError):
    pass


def _fail(message: str) -> None:
    raise ScoreError(message)


def _reject_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON key {key!r}")
        value[key] = item
    return value


def strict_loads(raw: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_reject_pairs,
            parse_constant=lambda token: (_ for _ in ()).throw(
                ValueError(f"non-finite JSON value {token!r}")
            ),
        )
    except (UnicodeError, ValueError) as exc:
        _fail(f"{label}: invalid strict JSON: {exc}")
    if not isinstance(value, dict):
        _fail(f"{label}: JSON root must be an object")
    return value


def _validate(schema_path: Path, value: dict[str, Any], label: str) -> None:
    schema = json.loads(schema_path.read_bytes())
    errors = sorted(
        Draft202012Validator(schema).iter_errors(value), key=lambda e: str(e.path)
    )
    if errors:
        first = errors[0]
        _fail(f"{label} schema: {list(first.path)!r}: {first.message}")


def _empty_block() -> dict[str, Any]:
    return {
        "scored_rows": 0,
        "micro_full_row_accuracy": None,
        "stance_macro_recall": None,
        "stance_confusion": {},
        "relevance_confusion": {},
        "check_state_confusion": {},
        "failure_state_distribution": {},
        "evidence_scope_agreement": {"agree": 0, "disagree": 0},
    }


def _bump(nested: dict[str, dict[str, int]], gold: str, subject: str) -> None:
    nested.setdefault(gold, {})
    nested[gold][subject] = nested[gold].get(subject, 0) + 1


def _finalize_block(block: dict[str, Any], correct_rows: int) -> None:
    scored = block["scored_rows"]
    block["micro_full_row_accuracy"] = (
        round(correct_rows / scored, 6) if scored else None
    )
    recalls = []
    for gold_stance, row in sorted(block["stance_confusion"].items()):
        total = sum(row.values())
        if total:
            recalls.append(row.get(gold_stance, 0) / total)
    block["stance_macro_recall"] = (
        round(sum(recalls) / len(recalls), 6) if recalls else None
    )


def score(
    set_value: dict[str, Any],
    adjudicated: dict[str, Any],
    subject: dict[str, Any],
) -> dict[str, Any]:
    _validate(SET_SCHEMA, set_value, "seed set")
    _validate(ADJUDICATED_SCHEMA, adjudicated, "adjudicated labels")
    _validate(SUBJECT_SCHEMA, subject, "subject output")

    expert_files = adjudicated["expert_label_files"]
    expert_ids = {row["expert_id"] for row in expert_files}
    expert_hashes = {row["sha256"] for row in expert_files}
    if len(expert_ids) < 2 or len(expert_hashes) < len(expert_files):
        _fail(
            "adjudicated labels must bind at least two distinct independent "
            "expert label files with distinct file hashes"
        )

    language_by_item = {
        item["item_id"]: item["language"] for item in set_value["items"]
    }
    gold_by_item: dict[str, dict[str, Any]] = {}
    for row in adjudicated["rows"]:
        if row["item_id"] in gold_by_item:
            _fail(f"adjudicated labels carry duplicate item {row['item_id']}")
        if row["item_id"] not in language_by_item:
            _fail(f"adjudicated labels name an unknown item {row['item_id']}")
        gold_by_item[row["item_id"]] = row
    if set(gold_by_item) != set(language_by_item):
        _fail("adjudicated labels must cover exactly the seed set's items")

    seen: set[tuple[str, int]] = set()
    scored_per_item: dict[str, int] = {item_id: 0 for item_id in language_by_item}
    blocks = {"en": _empty_block(), "zh-TW": _empty_block(), "overall": _empty_block()}
    correct = {"en": 0, "zh-TW": 0, "overall": 0}
    rows_summary = {"scored": 0, "blocked": 0, "partial": 0}

    for row in subject["rows"]:
        key = (row["item_id"], row["replicate"])
        if key in seen:
            _fail(f"subject output carries a duplicate row for {key!r}")
        seen.add(key)
        if row["item_id"] not in language_by_item:
            _fail(f"subject output names an unknown item {row['item_id']}")
        rows_summary[row["row_state"]] += 1
        language = language_by_item[row["item_id"]]
        if row["failure_state"] is not None:
            # Counted for every row state, so a blocked judge_timeout or a
            # partial parse_error stays visible in the failure-class report.
            for block in (blocks[language], blocks["overall"]):
                distribution = block["failure_state_distribution"]
                distribution[row["failure_state"]] = (
                    distribution.get(row["failure_state"], 0) + 1
                )
        if row["row_state"] != "scored":
            continue
        scored_per_item[row["item_id"]] += 1
        gold = gold_by_item[row["item_id"]]
        for block in (blocks[language], blocks["overall"]):
            block["scored_rows"] += 1
            _bump(block["relevance_confusion"], gold["relevance"], row["relevance"])
            _bump(block["check_state_confusion"], gold["check_state"], row["check_state"])
            if gold["check_state"] == "performed":
                subject_stance = (
                    row["stance"] if row["check_state"] == "performed" else ABSTAINED
                )
                _bump(block["stance_confusion"], gold["stance"], subject_stance)
            if row["evidence_scope"] == gold["evidence_scope"]:
                block["evidence_scope_agreement"]["agree"] += 1
            else:
                block["evidence_scope_agreement"]["disagree"] += 1
        if all(row[field] == gold[field] for field in FULL_ROW_FIELDS):
            correct[language] += 1
            correct["overall"] += 1

    for name, block in blocks.items():
        _finalize_block(block, correct[name])

    scored_counts = scored_per_item.values()
    report = {
        "schema_version": "claim-standing-stance-score-report/0.1",
        "suite": "claim_standing_probe",
        "subject_run_id": subject["subject_run_id"],
        "not_a_measurement_contract_row": True,
        "items": len(set_value["items"]),
        "replicates": {
            "min_scored_per_item": min(scored_counts),
            "max_scored_per_item": max(scored_counts),
            "decision_relevant_two_replicates": min(scored_counts) >= 2,
        },
        "rows": rows_summary,
        "by_language": {"en": blocks["en"], "zh-TW": blocks["zh-TW"]},
        "overall": blocks["overall"],
    }
    _validate(REPORT_SCHEMA, report, "score report")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--set", type=Path, default=SUITE_ROOT / "heldout_stance_set.json")
    parser.add_argument("--adjudicated", type=Path, required=True)
    parser.add_argument("--subject", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        report = score(
            strict_loads(args.set.read_bytes(), "seed set"),
            strict_loads(args.adjudicated.read_bytes(), "adjudicated labels"),
            strict_loads(args.subject.read_bytes(), "subject output"),
        )
    except ScoreError as exc:
        print(str(exc))
        return 1
    rendered = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        if args.output.exists():
            print(f"refusing to overwrite {args.output}")
            return 1
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
