#!/usr/bin/env python3
"""Mutation tests for the #616 E4 promotion-copy boundary."""
from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

import pytest

from scripts import check_e4_promotion as promotion


STEM = "2026-08-01-ms00_clean-post-r1"


def _write_run(root: Path, *, blocked: bool = False) -> Path:
    runs = root / "runs"
    record_dir = runs / "blocked" if blocked else runs
    raw = (runs / "raw" / "blocked" / STEM if blocked
           else runs / "raw" / STEM)
    record_dir.mkdir(parents=True, exist_ok=True)
    raw.mkdir(parents=True, exist_ok=True)
    (raw / "dispatch.log").write_text(
        "[PHASE1-GRAMMAR: synthetic diagnostic]\n", encoding="utf-8")
    (raw / "methodology.phase1.a1.md").write_text(
        "rejected response\n", encoding="utf-8")
    prefix = os.path.relpath(raw, record_dir).replace(os.sep, "/") + "/"
    record = {
        "measurement_status": "blocked" if blocked else "completed",
        "provenance_status": "valid",
        "panel_completion_status": "aborted" if blocked else "completed",
        "score_eligible": not blocked,
        "evidence_contract": "reviewer-e4/2026-07-27",
        "raw_bundle": prefix,
        "phase1_retries": [{
            "role": "methodology",
            "diagnostic": "[PHASE1-GRAMMAR: synthetic diagnostic]",
            "diagnostic_form": "verbatim",
            "rejected_response_preserved": True,
            "rejected_response_location": (
                prefix + "methodology.phase1.a1.md"),
            "checker_output_preserved": True,
            "checker_output_location": prefix + "dispatch.log",
        }],
    }
    record_path = record_dir / f"{STEM}.json"
    record_path.write_text(
        json.dumps(record, indent=1) + "\n", encoding="utf-8")
    return record_path


def _pair(tmp_path: Path, *, blocked: bool = False) -> tuple[Path, Path]:
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    _write_run(source, blocked=blocked)
    shutil.copytree(source / "runs", destination / "runs")
    return source, destination


@pytest.mark.parametrize("blocked", [False, True])
def test_a_pristine_promoted_copy_passes(tmp_path, blocked):
    source, destination = _pair(tmp_path, blocked=blocked)
    receipt = promotion.verify_promotion(source, destination, STEM)
    assert receipt.stem == STEM
    assert receipt.files_checked == 3


def test_a_changed_file_fails(tmp_path):
    source, destination = _pair(tmp_path)
    (destination / "runs" / "raw" / STEM / "dispatch.log").write_text(
        "changed\n", encoding="utf-8")
    with pytest.raises(promotion.PromotionError, match="changed"):
        promotion.verify_promotion(source, destination, STEM)


def test_an_omitted_file_fails(tmp_path):
    source, destination = _pair(tmp_path)
    (destination / "runs" / "raw" / STEM
     / "methodology.phase1.a1.md").unlink()
    with pytest.raises(promotion.PromotionError, match="missing|path set"):
        promotion.verify_promotion(source, destination, STEM)


def test_an_inserted_file_fails(tmp_path):
    source, destination = _pair(tmp_path)
    (destination / "runs" / "raw" / STEM / "extra.txt").write_text(
        "not in source\n", encoding="utf-8")
    with pytest.raises(promotion.PromotionError, match="extra|path set"):
        promotion.verify_promotion(source, destination, STEM)


def test_a_symlink_substitution_fails_even_when_the_bytes_match(tmp_path):
    source, destination = _pair(tmp_path)
    raw = destination / "runs" / "raw" / STEM
    answer = raw / "methodology.phase1.a1.md"
    answer.unlink()
    answer.symlink_to("dispatch.log")
    with pytest.raises(promotion.PromotionError, match="symlink|file type"):
        promotion.verify_promotion(source, destination, STEM)


def test_a_redirected_promotion_root_fails(tmp_path):
    source, destination = _pair(tmp_path)
    redirected = tmp_path / "destination-link"
    redirected.symlink_to(destination, target_is_directory=True)
    with pytest.raises(promotion.PromotionError, match="symlink"):
        promotion.verify_promotion(source, redirected, STEM)


def test_a_redirected_raw_bundle_fails_canonical_layout(tmp_path):
    source, destination = _pair(tmp_path)
    record = source / "runs" / f"{STEM}.json"
    loaded = json.loads(record.read_text(encoding="utf-8"))
    loaded["raw_bundle"] = f"raw/other-{STEM}/"
    record.write_text(json.dumps(loaded) + "\n", encoding="utf-8")
    shutil.copy2(record, destination / "runs" / f"{STEM}.json")
    with pytest.raises(promotion.PromotionError, match="canonical"):
        promotion.verify_promotion(source, destination, STEM)


def test_a_lexically_aliased_raw_bundle_fails_canonical_layout(tmp_path):
    source, destination = _pair(tmp_path)
    for root in (source, destination):
        record = root / "runs" / f"{STEM}.json"
        loaded = json.loads(record.read_text(encoding="utf-8"))
        loaded["raw_bundle"] = f"raw/../raw/{STEM}/"
        for retry in loaded["phase1_retries"]:
            for key in (
                "rejected_response_location", "checker_output_location",
            ):
                retry[key] = retry[key].replace("raw/", "raw/../raw/", 1)
        record.write_text(json.dumps(loaded) + "\n", encoding="utf-8")
    with pytest.raises(promotion.PromotionError, match="canonical"):
        promotion.verify_promotion(source, destination, STEM)


def test_an_unresolved_declared_location_fails_even_when_both_copies_match(
    tmp_path,
):
    source, destination = _pair(tmp_path)
    for root in (source, destination):
        (root / "runs" / "raw" / STEM
         / "methodology.phase1.a1.md").unlink()
    with pytest.raises(promotion.PromotionError, match="does not resolve"):
        promotion.verify_promotion(source, destination, STEM)


def test_source_and_destination_must_be_distinct(tmp_path):
    source, _destination = _pair(tmp_path)
    with pytest.raises(promotion.PromotionError, match="distinct"):
        promotion.verify_promotion(source, source, STEM)


def test_two_record_namespaces_for_one_identity_are_ambiguous(tmp_path):
    source, destination = _pair(tmp_path)
    for root in (source, destination):
        blocked = root / "runs" / "blocked" / f"{STEM}.json"
        blocked.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(root / "runs" / f"{STEM}.json", blocked)
    with pytest.raises(promotion.PromotionError, match="exactly one"):
        promotion.verify_promotion(source, destination, STEM)
