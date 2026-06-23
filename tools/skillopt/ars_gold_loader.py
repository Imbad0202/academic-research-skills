"""SkillOpt data loader for the ARS rq_framing_patterns gold set.

Reads ``evals/gold/rq_framing_patterns/gold_set.json`` (the #257 Socratic
wording-pattern advisory calibration set) and normalises each entry into the
flat dict shape SkillOpt expects. Supports both SkillOpt split modes:

  * ``split_mode: ratio``    — point ``env.data_path`` at the single gold_set.json
    and let SkillOpt build a deterministic train/val/test split (recommended;
    the 40-item set is balanced 20/20).
  * ``split_mode: split_dir`` — point ``env.split_dir`` at a directory whose
    train/ val/ test/ subdirs each hold one JSON array of normalised items.

This module imports SkillOpt's ``SplitDataLoader`` base class, so it only loads
when SkillOpt is installed (``pip install skillopt``). The pure label/scoring
logic lives in ``ars_scoring.py`` with no such dependency.
"""
from __future__ import annotations

import json
from pathlib import Path

from skillopt.datasets.base import SplitDataLoader

from tools.skillopt.ars_scoring import NEGATIVE_LABEL, POSITIVE_LABEL, expected_trigger


def _normalize_item(raw: dict) -> dict:
    """Normalise one gold tuple into SkillOpt's item shape.

    Hard requirement is ``id``; we also carry ``question`` (the RQ text the target
    model classifies), ``label`` / ``ground_truth`` (the gold class), a precomputed
    ``expected_trigger`` boolean, and ``task_type`` (= label) for stratified
    sampling.
    """
    label = str(raw.get("label") or "").strip()
    if label not in {POSITIVE_LABEL, NEGATIVE_LABEL}:
        raise ValueError(
            f"item {raw.get('id')!r}: invalid label {label!r}; "
            f"expected {POSITIVE_LABEL!r} or {NEGATIVE_LABEL!r}")
    text = str(raw.get("text") or raw.get("question") or "").strip()
    if not text:
        raise ValueError(f"item {raw.get('id')!r}: missing non-empty text")
    return {
        "id": str(raw.get("id") or ""),
        "question": text,
        "label": label,
        "ground_truth": label,
        "expected_trigger": expected_trigger(label),
        "expected_pattern_ids": list(raw.get("expected_pattern_ids") or []),
        "task_type": label,
    }


def _read_items_array(payload) -> list[dict]:
    """Accept either ``{"items": [...]}`` (gold_set.json) or a bare ``[...]``."""
    if isinstance(payload, dict):
        items = payload.get("items")
    else:
        items = payload
    if not isinstance(items, list):
        raise ValueError("expected an items[] array (or {'items': [...]})")
    return [_normalize_item(row) for row in items]


class ARSRQFramingLoader(SplitDataLoader):
    """Loader for the rq_framing_patterns gold set."""

    def load_raw_items(self, data_path: str) -> list[dict]:
        """Ratio mode: load every item from the single gold_set.json file."""
        path = Path(data_path)
        with path.open(encoding="utf-8") as f:
            payload = json.load(f)
        return _read_items_array(payload)

    def load_split_items(self, split_path: str) -> list[dict]:
        """split_dir mode: load all items from one split directory's JSON file."""
        path = Path(split_path)
        json_files = sorted(path.glob("*.json"))
        if not json_files:
            raise FileNotFoundError(f"no .json file found in {split_path}")
        with json_files[0].open(encoding="utf-8") as f:
            payload = json.load(f)
        return _read_items_array(payload)
