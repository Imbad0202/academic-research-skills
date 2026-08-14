#!/usr/bin/env python3
"""Offline validator for the #655 claim-standing stance seed set.

Validates `evals/heldout/claim_standing_probe/heldout_stance_set.json` against
its closed schema and the structural invariants below. File-only; no network,
model, retrieval, or dispatch surface.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

REPO_ROOT = Path(__file__).resolve().parents[1]
SUITE_ROOT = REPO_ROOT / "evals" / "heldout" / "claim_standing_probe"
SET_PATH = SUITE_ROOT / "heldout_stance_set.json"
SET_SCHEMA = SUITE_ROOT / "heldout_stance_set.schema.json"
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
# Heuristic screen only: a curated list of common simplified-only characters.
# Passing it does not certify the text; failing it is always a real defect.
SIMPLIFIED_CHARS = set(
    "们会学习语记观认证论试变对从关后发体历云礼国广边办应问题网络电产农动传"
    "亚区医药币厂儿师听劳岁苏软热顾风龙买卖读书写这为么样点让还时实现"
)


class AssetError(RuntimeError):
    pass


def _fail(message: str) -> None:
    raise AssetError(message)


def load_set() -> dict[str, Any]:
    return json.loads(SET_PATH.read_bytes())


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
        if len(subset) != 16:
            _fail(f"language block {language} must contain exactly 16 items")
        slots: dict[str, int] = {}
        for item in subset:
            if item["language"] != language:
                _fail(f"{item['item_id']}: id prefix and language field disagree")
            slots[_slot(item["item_id"])] = slots.get(_slot(item["item_id"]), 0) + 1
        if slots != EXPECTED_SLOTS:
            _fail(f"language block {language} design-slot coverage is not exact: {slots!r}")
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
            expected_coverage = (
                "session_held_full_text" if slot == "fulltext" else "abstract"
            )
            if (
                item["relevance_design"] != "relevant"
                or candidate["coverage"] != expected_coverage
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
            expected_coverage = "metadata_only" if slot == "metaonly" else "abstract"
            if (
                item["relevance_design"] != "relevant"
                or candidate["coverage"] != expected_coverage
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
        elif slot == "irrel":
            if item["relevance_design"] != "not_relevant":
                _fail(f"{item_id}: the irrelevant-candidate slot must be not_relevant")
            if target != {
                "check_state": "not_checked",
                "stance": None,
                "failure_state": None,
            }:
                _fail(f"{item_id}: not_relevant target is not_checked with null failure")
        else:
            _fail(f"{item_id}: unknown design slot {slot!r}")

        if (
            item["relevance_design"] == "relevant"
            and target["check_state"] == "not_checked"
            and target["failure_state"] is None
        ):
            _fail(
                f"{item_id}: a relevant not_checked target requires a failure state"
            )

        if item["language"] == "zh-TW":
            text = "".join(
                [
                    item["claim_text"],
                    candidate["title"],
                    candidate["venue"],
                    candidate["evidence_text"] or "",
                ]
            )
            hits = sorted(set(text) & SIMPLIFIED_CHARS)
            if hits:
                _fail(f"{item_id}: simplified-Chinese characters present: {hits!r}")

    registry = json.loads(SUITE_REGISTRY.read_bytes())
    if value["suite"] in registry:
        _fail(
            "the seed set is unmeasured: claim_standing_probe must not be "
            "registered in suite_registry.json until the implementation PR "
            "carries a valid baseline row"
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("validate-assets", help="validate the shipped seed set")
    parser.parse_args(argv)
    try:
        validate_set(load_set())
    except AssetError as exc:
        print(str(exc))
        return 1
    print("claim-standing stance seed set: all invariants hold (32 items)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
