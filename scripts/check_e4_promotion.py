#!/usr/bin/env python3
"""Verify that an E4 record and raw bundle were promoted byte-for-byte.

This checker validates only the copy boundary. It never reinterprets model
output, checker verdicts, adjudication, or the four closed status fields.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _e4_evidence as evidence  # noqa: E402


class PromotionError(RuntimeError):
    pass


@dataclass(frozen=True)
class PromotionReceipt:
    stem: str
    files_checked: int
    source_record: Path
    destination_record: Path


def _lexists(path: Path) -> bool:
    return os.path.lexists(path)


def _record(root: Path, stem: str) -> Path:
    runs = evidence.lexical_path(root) / "runs"
    candidates = [runs / f"{stem}.json", runs / "blocked" / f"{stem}.json"]
    found = [path for path in candidates if _lexists(path)]
    if len(found) != 1:
        raise PromotionError(
            f"expected exactly one record namespace for {stem}, found "
            f"{len(found)}")
    try:
        evidence.assert_plain_file(found[0], runs)
    except evidence.EvidencePathError as failure:
        raise PromotionError(str(failure)) from failure
    return found[0]


def _load_record(path: Path) -> dict:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as failure:
        raise PromotionError(
            f"record is not readable JSON: {path}: {type(failure).__name__}") \
            from failure
    if not isinstance(loaded, dict):
        raise PromotionError(f"record top level is not an object: {path}")
    return loaded


def _declared(record_path: Path, value: object, runs: Path, *, label: str,
              directory: bool = False) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise PromotionError(f"{label} must be a non-empty relative path")
    if Path(value).is_absolute():
        raise PromotionError(f"{label} must be record-relative, got {value!r}")
    target = evidence.lexical_path(record_path.parent / value)
    if not evidence.within(target, runs):
        raise PromotionError(f"{label} escapes runs/: {value!r}")
    try:
        if directory:
            evidence.assert_plain_directory(target, runs)
        else:
            evidence.assert_plain_file(target, runs)
    except evidence.EvidencePathError as failure:
        raise PromotionError(
            f"{label} is missing or does not resolve safely: {failure}") \
            from failure
    return target


def _locations(value: object):
    if isinstance(value, dict):
        for key, child in value.items():
            if key.endswith("_location"):
                yield key, child
            yield from _locations(child)
    elif isinstance(value, list):
        for child in value:
            yield from _locations(child)


def _scope(root: Path, stem: str) -> tuple[Path, dict[str, dict]]:
    root = evidence.lexical_path(root)
    try:
        evidence.assert_plain_directory(root, root)
    except evidence.EvidencePathError as failure:
        raise PromotionError(str(failure)) from failure
    runs = root / "runs"
    record_path = _record(root, stem)
    record = _load_record(record_path)
    blocked = record_path.parent.name == "blocked"
    expected_raw = (runs / "raw" / "blocked" / stem if blocked
                    else runs / "raw" / stem)
    expected_declared_raw = os.path.relpath(
        expected_raw, record_path.parent).replace(os.sep, "/") + "/"
    declared_raw = record.get("raw_bundle")
    if not isinstance(declared_raw, str) or not declared_raw.strip() \
            or Path(declared_raw).is_absolute():
        raise PromotionError("raw_bundle must be a non-empty relative path")
    lexical_raw = evidence.lexical_path(record_path.parent / declared_raw)
    if declared_raw != expected_declared_raw \
            or lexical_raw != evidence.lexical_path(expected_raw):
        raise PromotionError(
            f"raw_bundle is not the canonical layout for {stem}: expected "
            f"{expected_declared_raw!r}, got {declared_raw!r}")
    raw = _declared(
        record_path, declared_raw, runs,
        label="raw_bundle", directory=True)

    for label, declared in _locations(record):
        target = _declared(record_path, declared, runs, label=label)
        if not evidence.within(target, raw):
            raise PromotionError(
                f"{label} resolves outside the declared raw_bundle: {declared}")

    scope: dict[str, dict] = {}
    record_rel = record_path.relative_to(root).as_posix()
    scope[record_rel] = {
        "type": "file", "sha256": evidence.sha256_file(record_path)}
    raw_rel = raw.relative_to(root).as_posix()
    scope[raw_rel] = {"type": "directory"}
    for entry in evidence.tree_manifest(raw):
        if entry["type"] not in {"file", "directory"}:
            raise PromotionError(
                f"raw bundle contains forbidden {entry['type']} path: "
                f"{entry['path']}")
        scope[f"{raw_rel}/{entry['path']}"] = {
            key: value for key, value in entry.items() if key != "path"
        }
    return record_path, scope


def verify_promotion(source_root: Path, destination_root: Path,
                     stem: str) -> PromotionReceipt:
    if not stem or Path(stem).parts != (stem,) or stem in {".", ".."}:
        raise PromotionError("stem must be one non-empty path component")
    source_root = evidence.lexical_path(Path(source_root))
    destination_root = evidence.lexical_path(Path(destination_root))
    if source_root == destination_root:
        raise PromotionError("source and destination roots must be distinct")
    source_record, source = _scope(source_root, stem)
    destination_record, destination = _scope(destination_root, stem)
    if source.keys() != destination.keys():
        missing = sorted(source.keys() - destination.keys())
        extra = sorted(destination.keys() - source.keys())
        raise PromotionError(
            f"promoted path set differs; missing={missing}, extra={extra}")
    changed = [path for path in source if source[path] != destination[path]]
    if changed:
        details = [
            f"{path}: {source[path]} -> {destination[path]}"
            for path in changed
        ]
        raise PromotionError("promoted file type or bytes changed: "
                             + "; ".join(details))
    return PromotionReceipt(
        stem=stem,
        files_checked=sum(1 for item in source.values()
                          if item["type"] == "file"),
        source_record=source_record,
        destination_record=destination_record,
    )


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--destination-root", required=True, type=Path)
    parser.add_argument("--stem", required=True)
    args = parser.parse_args(argv)
    try:
        receipt = verify_promotion(
            args.source_root, args.destination_root, args.stem)
    except PromotionError as failure:
        print(f"FAIL: {failure}", file=sys.stderr)
        return 1
    print(f"PASS: {receipt.stem}; {receipt.files_checked} files byte-identical")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
