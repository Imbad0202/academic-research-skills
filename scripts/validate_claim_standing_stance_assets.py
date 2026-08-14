#!/usr/bin/env python3
"""Offline validator for the #655 claim-standing stance seed set.

Validates `evals/heldout/claim_standing_probe/heldout_stance_set.json` against
its closed schema and the structural invariants below. File-only; no network,
model, retrieval, or dispatch surface.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

REPO_ROOT = Path(__file__).resolve().parents[1]
SUITE_ROOT = REPO_ROOT / "evals" / "heldout" / "claim_standing_probe"
SET_PATH = SUITE_ROOT / "heldout_stance_set.json"
SET_SCHEMA = SUITE_ROOT / "heldout_stance_set.schema.json"
EXPERT_SCHEMA = SUITE_ROOT / "expert_label.schema.json"
SUITE_REGISTRY = SUITE_ROOT.parent / "suite_registry.json"

EXPECTED_SLOTS = {
    "support": 2,
    "contradict": 2,
    "mixed": 2,
    "notaddr": 2,
    "insuff": 2,
    "ambig": 2,
    "absmiss": 1,
    "metaonly": 1,
    "irrel": 1,
    "fulltext": 1,
}
SLOT_STANCE = {
    "support": "support",
    "contradict": "contradict",
    "mixed": "mixed",
    "notaddr": "not_addressed",
    "insuff": "INSUFFICIENT_EVIDENCE",
    "ambig": "AMBIGUOUS",
    "fulltext": "support",
}
SLOT_COVERAGE = {"fulltext": "session_held_full_text", "metaonly": "metadata_only"}
# Heuristic screen only: a curated list of characters that are simplified-only
# in ordinary academic prose. A hit is a likely defect, not proof; characters
# with common Traditional readings (e.g. 后, 云, 从) are deliberately excluded.
SIMPLIFIED_CHARS = set(
    "们会学习语记观认证论试变对关发体历礼国广边办应问题网络电产农动传"
    "亚区医药币岁苏软热顾风龙买卖读书写这为么样点让还时实现"
)


class AssetError(RuntimeError):
    pass


def _fail(message: str) -> None:
    raise AssetError(message)


def _reject_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON key {key!r}")
        value[key] = item
    return value


def _strict_loads(raw: bytes, label: str) -> dict[str, Any]:
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


def load_set() -> dict[str, Any]:
    return _strict_loads(SET_PATH.read_bytes(), "seed set")


def _slot(item_id: str) -> str:
    return item_id.split("-")[2]


def validate_set(value: dict[str, Any]) -> None:
    schema = json.loads(SET_SCHEMA.read_bytes())
    errors = sorted(
        Draft202012Validator(schema).iter_errors(value), key=lambda e: str(e.path)
    )
    if errors:
        first = errors[0]
        _fail(f"schema: {list(first.path)!r}: {first.message}")

    items = value["items"]
    ids = [item["item_id"] for item in items]
    if len(set(ids)) != len(ids):
        _fail("item ids must be unique")

    for prefix, language in (("csp-en-", "en"), ("csp-zh-", "zh-TW")):
        subset = [item for item in items if item["item_id"].startswith(prefix)]
        if len(subset) != sum(EXPECTED_SLOTS.values()):
            _fail(
                f"language block {language} must contain exactly "
                f"{sum(EXPECTED_SLOTS.values())} items"
            )
        for item in subset:
            if item["language"] != language:
                _fail(f"{item['item_id']}: id prefix and language field disagree")
        slots = Counter(_slot(item["item_id"]) for item in subset)
        if slots != EXPECTED_SLOTS:
            _fail(
                f"language block {language} design-slot coverage is not exact: "
                f"{dict(slots)!r}"
            )
        disciplines = [item["discipline"] for item in subset]
        if len(set(disciplines)) != len(disciplines):
            _fail(f"language block {language} disciplines must be distinct")

    for item in items:
        item_id = item["item_id"]
        slot = _slot(item_id)
        candidate = item["candidate"]
        target = item["design_target"]
        if candidate["doi"] != f"10.99999/{item_id}":
            _fail(f"{item_id}: doi must be 10.99999/{item_id}")
        if candidate["work_family_id"] != f"wf-{item_id}":
            _fail(f"{item_id}: work_family_id must be wf-{item_id}")

        if slot in SLOT_STANCE:
            if (
                item["relevance_design"] != "relevant"
                or candidate["coverage"] != SLOT_COVERAGE.get(slot, "abstract")
                or candidate["content_state"] != "available"
                or target
                != {
                    "check_state": "performed",
                    "stance": SLOT_STANCE[slot],
                    "failure_state": None,
                }
            ):
                _fail(f"{item_id}: does not realize its design slot ({slot})")
        elif slot in ("absmiss", "metaonly"):
            if (
                item["relevance_design"] != "relevant"
                or candidate["coverage"] != SLOT_COVERAGE.get(slot, "abstract")
                or candidate["content_state"] != "abstract_missing"
                or candidate["evidence_text"] is not None
                or target
                != {
                    "check_state": "not_checked",
                    "stance": None,
                    "failure_state": "abstract_missing",
                }
            ):
                _fail(
                    f"{item_id}: missing-evidence slot must target "
                    "not_checked with failure_state abstract_missing"
                )
        else:
            # The slot table is exact, so only "irrel" can reach here.
            if item["relevance_design"] != "not_relevant":
                _fail(f"{item_id}: the irrelevant-candidate slot must be not_relevant")
            if target != {
                "check_state": "not_checked",
                "stance": None,
                "failure_state": None,
            }:
                _fail(f"{item_id}: not_relevant target is not_checked with null failure")

        if item["language"] == "zh-TW":
            text = "".join(
                [
                    item["claim_text"],
                    item["discipline"],
                    candidate["title"],
                    candidate["venue"],
                    candidate["evidence_text"] or "",
                ]
            )
            hits = sorted(set(text) & SIMPLIFIED_CHARS)
            if hits:
                _fail(f"{item_id}: simplified-Chinese characters present: {hits!r}")

    registry = _strict_loads(SUITE_REGISTRY.read_bytes(), "suite registry")
    if value["suite"] in registry:
        _fail(
            "the seed set is unmeasured: claim_standing_probe must not be "
            "registered in suite_registry.json until the implementation PR "
            "carries a valid baseline row"
        )


def validate_expert_file(value: dict[str, Any], set_value: dict[str, Any]) -> None:
    schema = json.loads(EXPERT_SCHEMA.read_bytes())
    errors = sorted(
        Draft202012Validator(schema).iter_errors(value), key=lambda e: str(e.path)
    )
    if errors:
        first = errors[0]
        _fail(f"expert file schema: {list(first.path)!r}: {first.message}")
    labeled = [row["item_id"] for row in value["labels"]]
    if len(set(labeled)) != len(labeled):
        _fail("expert file labels the same item more than once")
    set_ids = {item["item_id"] for item in set_value["items"]}
    if set(labeled) != set_ids:
        _fail("expert file must label exactly the seed set's 32 distinct items")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("validate-assets", help="validate the shipped seed set")
    expert_parser = subparsers.add_parser(
        "validate-expert-file",
        help="validate one expert label file against the seed set",
    )
    expert_parser.add_argument("--expert-file", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        set_value = load_set()
        if args.command == "validate-expert-file":
            validate_expert_file(
                _strict_loads(args.expert_file.read_bytes(), "expert file"),
                set_value,
            )
            print("expert label file: complete distinct coverage of the seed set")
            return 0
        validate_set(set_value)
    except AssetError as exc:
        print(str(exc))
        return 1
    print("claim-standing stance seed set: all invariants hold (32 items)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
