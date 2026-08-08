#!/usr/bin/env python3
"""Validate a #668 committee-correspondence bundle.

This checker proves byte transport, source-comment accounting, degraded/profile
semantics, and response-skeleton coverage. It does not make a human-subjects
determination or judge whether a response will satisfy a committee.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA = (
    REPO_ROOT
    / "shared"
    / "contracts"
    / "human_subjects"
    / "committee_correspondence.schema.json"
)
SOURCE_NAME = "source_letter.txt"
TRACKER_NAME = "concern_tracker.json"
SKELETON_NAME = "response_skeleton.md"
STATUS_LINE = "Status: drafting aid — no concern is asserted resolved."
RESPONSE_PLACEHOLDER = "[AUTHOR RESPONSE REQUIRED — drafting aid; do not claim resolved]"
EVIDENCE_PLACEHOLDER = "[EVIDENCE OR ARTIFACT POINTER REQUIRED]"
BOUNDARY_LINE = (
    "> **Human-subjects boundary:** This output does not authorize recruitment, "
    "consent, access to identifiable data, intervention, or data collection."
)
MARKER = re.compile(r"<!-- concern:(CC-[0-9]{3}) -->")
RESOLUTION_CLAIM = re.compile(
    r"\b(?:resolved|addressed|approved|cleared|submission[- ]ready)\b", re.IGNORECASE
)


class DuplicateKeyError(ValueError):
    pass


def _object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _load_json(path: Path, errors: list[str]) -> dict[str, Any] | None:
    try:
        with path.open("r", encoding="utf-8") as handle:
            value = json.load(handle, object_pairs_hook=_object_pairs)
    except (OSError, json.JSONDecodeError, DuplicateKeyError) as exc:
        errors.append(f"{path}: cannot load JSON: {exc}")
        return None
    if not isinstance(value, dict):
        errors.append(f"{path}: top-level value must be an object")
        return None
    return value


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _bundle_member(bundle_root: Path, relative: str, errors: list[str]) -> Path | None:
    if "\\" in relative:
        errors.append(f"bundle path must use POSIX separators: {relative!r}")
        return None
    pure = PurePosixPath(relative)
    if pure.is_absolute() or not pure.parts or any(part in ("", ".", "..") for part in pure.parts):
        errors.append(f"bundle path must be a normalized relative path: {relative!r}")
        return None
    candidate = bundle_root.joinpath(*pure.parts)
    current = bundle_root
    for part in pure.parts:
        current = current / part
        if current.is_symlink():
            errors.append(f"bundle member cannot traverse a symlink: {relative!r}")
            return None
    try:
        resolved_root = bundle_root.resolve(strict=True)
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(resolved_root)
    except (OSError, ValueError) as exc:
        errors.append(f"bundle member is missing or outside bundle: {relative!r}: {exc}")
        return None
    if not resolved.is_file():
        errors.append(f"bundle member must be a regular file: {relative!r}")
        return None
    return resolved


def _schema_errors(
    tracker: dict[str, Any], schema_path: Path, errors: list[str]
) -> bool:
    schema = _load_json(schema_path, errors)
    if schema is None:
        return True
    try:
        Draft202012Validator.check_schema(schema)
    except Exception as exc:  # pragma: no cover - CLI failure path
        errors.append(f"{schema_path}: invalid schema: {exc}")
        return True
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    found = sorted(validator.iter_errors(tracker), key=lambda item: list(item.path))
    for item in found:
        location = ".".join(str(part) for part in item.path) or "<root>"
        errors.append(f"schema {location}: {item.message}")
    return bool(found)


def validate_bundle(tracker_path: Path, schema_path: Path = DEFAULT_SCHEMA) -> list[str]:
    errors: list[str] = []
    tracker_path = tracker_path.resolve()
    tracker = _load_json(tracker_path, errors)
    if tracker is None:
        return errors
    if _schema_errors(tracker, schema_path, errors):
        return errors

    bundle_root = tracker_path.parent
    source_meta = tracker["source_artifact"]
    source_path = _bundle_member(bundle_root, source_meta["path"], errors)
    skeleton_meta = tracker["response_skeleton"]
    skeleton_path = _bundle_member(bundle_root, skeleton_meta["path"], errors)
    if tracker_path.name != TRACKER_NAME:
        errors.append(f"tracker filename must be {TRACKER_NAME}")
    if source_meta["path"] != SOURCE_NAME:
        errors.append(f"source_artifact.path must be {SOURCE_NAME}")
    if skeleton_meta["path"] != SKELETON_NAME:
        errors.append(f"response_skeleton.path must be {SKELETON_NAME}")
    if source_path is None or skeleton_path is None:
        return errors

    try:
        source_bytes = source_path.read_bytes()
        source_text = source_bytes.decode("utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        errors.append(f"source letter must be readable UTF-8: {exc}")
        return errors
    source_digest = _sha256(source_bytes)
    if source_meta["sha256"] != source_digest:
        errors.append("source_artifact.sha256 does not match source_letter.txt")
    if source_meta["byte_length"] != len(source_bytes):
        errors.append("source_artifact.byte_length does not match source_letter.txt")
    if tracker["tracker_id"] != f"committee-{source_digest[:12]}":
        errors.append("tracker_id must bind to the first 12 hex characters of source SHA-256")
    if bundle_root.name != source_digest[:12]:
        errors.append("bundle directory name must equal the first 12 hex characters of source SHA-256")

    segments = source_meta["segments"]
    segment_by_id: dict[str, dict[str, Any]] = {}
    cursor = 0
    expected_orders = list(range(1, len(segments) + 1))
    actual_orders = [segment["source_order"] for segment in segments]
    if actual_orders != expected_orders:
        errors.append("source segments must be stored in canonical source order 1..N")
    for segment in segments:
        segment_id = segment["segment_id"]
        if segment_id in segment_by_id:
            errors.append(f"duplicate source segment id: {segment_id}")
        segment_by_id[segment_id] = segment
        start = segment["byte_start"]
        end = segment["byte_end"]
        if start != cursor:
            errors.append(f"{segment_id}: byte range must start at previous segment end {cursor}")
        if end <= start or end > len(source_bytes):
            errors.append(f"{segment_id}: invalid byte range [{start}, {end})")
            chunk = b""
        else:
            chunk = source_bytes[start:end]
            cursor = end
        if _sha256(chunk) != segment["sha256"]:
            errors.append(f"{segment_id}: segment SHA-256 mismatch")
        try:
            chunk.decode("utf-8")
        except UnicodeDecodeError:
            errors.append(f"{segment_id}: segment boundary splits invalid UTF-8")
    if cursor != len(source_bytes):
        errors.append("source segments must cover source_letter.txt through EOF")
    if source_text == "":  # schema byte_length already rejects this; explicit semantic message
        errors.append("source letter cannot be empty")

    concerns = tracker["concerns"]
    concern_ids = [concern["concern_id"] for concern in concerns]
    if len(set(concern_ids)) != len(concern_ids):
        errors.append("concern ids must be unique")
    comment_segments = [segment for segment in segments if segment["kind"] == "comment"]
    expected_concern_ids = [f"CC-{index:03d}" for index in range(1, len(comment_segments) + 1)]
    if concern_ids != expected_concern_ids:
        errors.append("concerns must use stable sequential ids in canonical source-comment order")
    expected_comment_ids = [segment["segment_id"] for segment in comment_segments]
    actual_comment_ids = [concern["source_comment_id"] for concern in concerns]
    if actual_comment_ids != expected_comment_ids:
        errors.append("every comment segment must map exactly once in canonical source order")
    if len(set(actual_comment_ids)) != len(actual_comment_ids):
        errors.append("a source comment cannot map to more than one concern")

    concern_id_set = set(concern_ids)
    profile = tracker["profile_context"]
    profile_derived = False
    for concern in concerns:
        concern_id = concern["concern_id"]
        segment = segment_by_id.get(concern["source_comment_id"])
        if segment is None:
            errors.append(f"{concern_id}: source comment id does not resolve")
            continue
        if segment["kind"] != "comment":
            errors.append(f"{concern_id}: source locator must name a comment segment")
        locator_expected = {
            "segment_id": segment["segment_id"],
            "source_order": segment["source_order"],
            "byte_start": segment["byte_start"],
            "byte_end": segment["byte_end"],
            "sha256": segment["sha256"],
        }
        if concern["source_locator"] != locator_expected:
            errors.append(f"{concern_id}: source locator does not exactly match segment manifest")
        if concern["source_order"] != segment["source_order"]:
            errors.append(f"{concern_id}: source_order does not match source segment")
        chunk = source_bytes[segment["byte_start"] : segment["byte_end"]]
        try:
            verbatim = chunk.decode("utf-8")
        except UnicodeDecodeError:
            verbatim = ""
        if concern["verbatim_text"] != verbatim:
            errors.append(f"{concern_id}: verbatim_text is not the exact source bytes")
        basis = concern["authority_basis"]
        if basis["provenance"] == "committee_explicit" and basis["exact_text"] not in verbatim:
            errors.append(f"{concern_id}: committee authority basis must be exact source text")

        artifact_names: set[str] = set()
        for artifact in concern["affected_artifacts"]:
            normalized_name = " ".join(artifact["name"].casefold().split())
            if normalized_name in artifact_names:
                errors.append(f"{concern_id}: duplicate affected artifact name")
            artifact_names.add(normalized_name)
            if artifact["provenance"] == "profile_resolved":
                profile_derived = True
        if concern["profile_requirement_ids"]:
            profile_derived = True

        dependency_ids: set[str] = set()
        for dependency in concern["dependencies"]:
            dependency_id = dependency["concern_id"]
            if dependency_id == concern_id:
                errors.append(f"{concern_id}: concern cannot depend on itself")
            if dependency_id not in concern_id_set:
                errors.append(f"{concern_id}: dependency does not resolve: {dependency_id}")
            if dependency_id in dependency_ids:
                errors.append(f"{concern_id}: duplicate dependency: {dependency_id}")
            dependency_ids.add(dependency_id)

    if profile["state"] == "not_selected" and profile_derived:
        errors.append("profile-derived artifacts or requirement ids require a selected profile")
    if profile["artifact_resolution_state"] != "profile_enriched" and profile_derived:
        errors.append("profile-derived fields require artifact_resolution_state=profile_enriched")
    if profile["artifact_resolution_state"] == "profile_enriched" and not profile_derived:
        errors.append("profile_enriched state requires at least one profile-derived field")

    view_ids: set[str] = set()
    for view in tracker["working_views"]:
        if view["view_id"] in view_ids:
            errors.append(f"duplicate working view id: {view['view_id']}")
        view_ids.add(view["view_id"])
        if len(view["concern_ids"]) != len(concern_ids) or set(view["concern_ids"]) != concern_id_set:
            errors.append(f"working view {view['view_id']} must be a full concern-id permutation")

    status = tracker["human_subjects_status"]
    auth_source = status["authorization_source_comment_id"]
    if auth_source is not None:
        segment = segment_by_id.get(auth_source)
        if segment is None or segment["kind"] != "comment" or auth_source not in actual_comment_ids:
            errors.append("authorization source must resolve to an accounted comment segment")

    try:
        skeleton_bytes = skeleton_path.read_bytes()
        skeleton = skeleton_bytes.decode("utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        errors.append(f"response skeleton must be readable UTF-8: {exc}")
        return errors
    if _sha256(skeleton_bytes) != skeleton_meta["sha256"]:
        errors.append("response_skeleton.sha256 does not match response_skeleton.md")
    if skeleton.count(STATUS_LINE) != 1:
        errors.append("response skeleton must carry the fixed drafting-aid status exactly once")
    if skeleton.count(BOUNDARY_LINE) != 1:
        errors.append("response skeleton must carry the fixed #665 boundary exactly once")
    markers = list(MARKER.finditer(skeleton))
    marker_ids = [match.group(1) for match in markers]
    if marker_ids != concern_ids:
        errors.append("response skeleton markers must cover every concern exactly once in source order")
    for index, match in enumerate(markers):
        concern_id = match.group(1)
        end = markers[index + 1].start() if index + 1 < len(markers) else len(skeleton)
        block = skeleton[match.start() : end]
        if block.count(f"### Concern {concern_id}") != 1:
            errors.append(f"response skeleton {concern_id}: missing unique concern heading")
        if block.count(RESPONSE_PLACEHOLDER) != 1:
            errors.append(f"response skeleton {concern_id}: response placeholder must appear once")
        if block.count(EVIDENCE_PLACEHOLDER) != 1:
            errors.append(f"response skeleton {concern_id}: evidence placeholder must appear once")
    claim_scan = skeleton.replace(STATUS_LINE, "").replace(RESPONSE_PLACEHOLDER, "")
    if RESOLUTION_CLAIM.search(claim_scan):
        errors.append("response skeleton contains a resolution/approval/readiness claim")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tracker", type=Path, help="path to concern_tracker.json")
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    args = parser.parse_args(argv)
    errors = validate_bundle(args.tracker, args.schema)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Committee correspondence bundle: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
