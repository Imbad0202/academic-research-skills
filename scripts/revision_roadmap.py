#!/usr/bin/env python3
"""Validate and replay the #670 revision-authority contract.

The runtime is hermetic. It opens only explicitly named local artifacts, never
calls a model or network service, never reads an ambient clock, and never
supplies an author choice. Reviewer-owned roadmap bytes, explicit author-choice
bytes, registered claim surfaces, patch bytes, reports, and draft-chain bytes
remain separate and are joined only through exact SHA-256 bindings.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import re
import stat
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import jsonschema
from referencing import Registry, Resource

if __package__ in (None, ""):  # pragma: no cover - direct CLI invocation
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts._block_parser import (
    BlockParseError,
    ParsedDocument,
    atomic_write_bytes,
    base_draft_hash,
    parse_document,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
REVISION_CONTRACTS = REPO_ROOT / "shared" / "contracts" / "revision"
ROADMAP_SCHEMA_PATH = REVISION_CONTRACTS / "revision_roadmap.schema.json"
AUTHOR_SCHEMA_PATH = REVISION_CONTRACTS / "author_adjudication.schema.json"
AUTHOR_INPUT_SCHEMA_PATH = REVISION_CONTRACTS / "author_adjudication_input.schema.json"
CLAIM_SURFACE_SCHEMA_PATH = REVISION_CONTRACTS / "claim_surface_manifest.schema.json"
BUNDLE_SCHEMA_PATH = REVISION_CONTRACTS / "revision_evidence_bundle.schema.json"
INTEGRITY_RECEIPT_SCHEMA_PATH = REVISION_CONTRACTS / "integrity_pass_receipt.schema.json"
INTEGRITY_LIST_SCHEMA_PATH = REVISION_CONTRACTS / "integrity_correction_list.schema.json"
INTEGRITY_AUTH_SCHEMA_PATH = (
    REVISION_CONTRACTS / "integrity_correction_authorization.schema.json"
)
INTEGRITY_AUTH_INPUT_SCHEMA_PATH = (
    REVISION_CONTRACTS / "integrity_correction_authorization_input.schema.json"
)
REVISION_SCHEMA_PATHS = (
    ROADMAP_SCHEMA_PATH,
    AUTHOR_SCHEMA_PATH,
    AUTHOR_INPUT_SCHEMA_PATH,
    CLAIM_SURFACE_SCHEMA_PATH,
    BUNDLE_SCHEMA_PATH,
    INTEGRITY_RECEIPT_SCHEMA_PATH,
    INTEGRITY_LIST_SCHEMA_PATH,
    INTEGRITY_AUTH_SCHEMA_PATH,
    INTEGRITY_AUTH_INPUT_SCHEMA_PATH,
)
BLOCK_MANIFEST_SCHEMA_PATH = (
    REPO_ROOT / "shared" / "contracts" / "patch" / "block_manifest.schema.json"
)
CLAIM_INTENT_SCHEMA_PATH = (
    REPO_ROOT / "shared" / "contracts" / "passport" / "claim_intent_manifest.schema.json"
)
PATCH_SCHEMA_PATH = REPO_ROOT / "shared" / "contracts" / "patch" / "revision_patch.schema.json"

CURRENT_ROADMAP_VERSION = "revision-roadmap/1.0"
CURRENT_AUTHOR_VERSION = "author-adjudication/1.0"
CURRENT_PATCH_VERSION = "1.1"
CURRENT_REPORT_VERSION = "1.3"
OBLIGATION_CLASSES = ("must_fix", "should_fix", "consider")
DECLINED_TRIAGE = ("wont_address", "not_on_point")
OP_ORDER = {"replace_block": 0, "insert_after": 1, "delete_block": 2}
SEAT_ORDER = {"EIC": 0, "R1": 1, "R2": 2, "R3": 3, "DA": 4}
CHANNEL_ORDER = {"finding": 0, "question": 1, "editorial": 2}
MAX_ARTIFACT_BYTES = 64 * 1024 * 1024

_TIME_UNIT_RE = re.compile(r"\b(?:hours?|hrs?|days?|weeks?|months?)\b", re.IGNORECASE)
_WORK_RANK_RE = re.compile(
    r"\b(?:priority|rank)\s*(?:number\s*)?[123]\b|"
    r"\bp[123]\s+work\b|\branked\s+work\b|\bwork\s+rank\b|"
    r"\bhighest\s+priority\b|\bdo\b.{0,80}\bfirst\b|"
    r"\bfirst\s+(?:address|revise|complete|do)\b",
    re.IGNORECASE,
)
_PREDICTION_LANGUAGE_RE = re.compile(
    r"\b(?:odds|probabilit(?:y|ies)|chance|likelihood)\b|"
    r"\b(?:will|would|shall|certain(?:ly)?|guaranteed\s+to)\s+"
    r"(?:be\s+)?(?:accept(?:ed)?|reject(?:ed)?)\b|"
    r"\b(?:accepted|rejected)\b",
    re.IGNORECASE,
)


class ContractError(ValueError):
    """Closed validation failure collection; callers fail before writing."""

    def __init__(self, failures: list[str]):
        self.failures = failures
        super().__init__("; ".join(failures))


def bytes_hash(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _reject_non_jcs_numbers(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise ContractError([f"{path}: floating-point values are outside this contract's JCS value domain"])
    if isinstance(value, dict):
        for key, child in value.items():
            _reject_non_jcs_numbers(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_non_jcs_numbers(child, f"{path}[{index}]")


def canonical_bytes(value: Any) -> bytes:
    """Canonical UTF-8 JSON for the contract's string/int/bool/null domain."""
    _reject_non_jcs_numbers(value)
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    ).encode("utf-8")


def canonical_hash(value: Any) -> str:
    return bytes_hash(canonical_bytes(value))


def author_decision_projection(adjudication: dict) -> dict:
    """Exact author-owned state used for the stable JCS audit digest."""
    return {
        "author_events": copy.deepcopy(adjudication.get("author_events")),
        "display_order": copy.deepcopy(adjudication.get("display_order")),
        "author_adjudications": copy.deepcopy(adjudication.get("author_adjudications")),
        "collateral_authorizations": copy.deepcopy(
            adjudication.get("collateral_authorizations")
        ),
    }


def author_decision_digest(adjudication: dict) -> str:
    return canonical_hash(author_decision_projection(adjudication))


def source_finding_projection(roadmap: dict) -> list[dict]:
    """Project transported reviewer data only; never author/view authority."""
    fields = (
        "id",
        "source_refs",
        "description",
        "reviewer",
        "sub_claim_ids",
        "severity",
        "severity_source",
        "evidence_anchor",
        "confidence",
        "competence_basis",
        "confidence_source",
        "corroborating_sources",
        "source_kind",
    )
    return [
        {field: copy.deepcopy(item[field]) for field in fields if field in item}
        for item in roadmap.get("items", [])
    ]


def _load_schema(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _schema_validator(schema_path: Path) -> jsonschema.Draft202012Validator:
    schema = _load_schema(schema_path)
    registry = Registry()
    for path in REVISION_SCHEMA_PATHS:
        candidate = _load_schema(path)
        if "$id" in candidate:
            registry = registry.with_resource(
                candidate["$id"], Resource.from_contents(candidate)
            )
    return jsonschema.Draft202012Validator(schema, registry=registry)


def _schema_failures(value: Any, schema_path: Path, label: str) -> list[str]:
    errors = sorted(
        _schema_validator(schema_path).iter_errors(value),
        key=lambda error: [str(part) for part in error.absolute_path],
    )
    failures: list[str] = []
    for error in errors:
        path = "/".join(str(part) for part in error.absolute_path) or "(root)"
        failures.append(f"{label} schema {path}: {error.message}")
    return failures


def _json_from_raw(raw: bytes, label: str) -> dict:
    def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, child in pairs:
            if key in value:
                raise ValueError(f"duplicate object key {key!r}")
            value[key] = child
        return value

    def reject_constant(token: str) -> None:
        raise ValueError(f"non-finite JSON constant {token!r}")

    try:
        value = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=unique_object,
            parse_constant=reject_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise ContractError([f"{label}: invalid UTF-8 JSON: {exc}"]) from exc
    if not isinstance(value, dict):
        raise ContractError([f"{label}: top level must be an object"])
    return value


def _read_path_once(path: Path, label: str) -> bytes:
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        fd = os.open(path, flags)
    except OSError as exc:
        raise ContractError([f"{label}: cannot open regular non-symlink file {path}: {exc}"]) from exc
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode):
            raise ContractError([f"{label}: artifact is not a regular file"])
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = os.read(fd, min(1024 * 1024, MAX_ARTIFACT_BYTES + 1 - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
            if total > MAX_ARTIFACT_BYTES:
                raise ContractError([f"{label}: artifact exceeds {MAX_ARTIFACT_BYTES} bytes"])
        after = os.fstat(fd)
        fingerprint_before = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
        fingerprint_after = (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
        if fingerprint_before != fingerprint_after or total != after.st_size:
            raise ContractError([f"{label}: artifact changed while it was being read"])
        return b"".join(chunks)
    finally:
        os.close(fd)


def load_json_path(path: Path, label: str) -> tuple[dict, bytes]:
    raw = _read_path_once(path, label)
    return _json_from_raw(raw, label), raw


@dataclass(frozen=True)
class LoadedArtifact:
    relative_path: str
    raw: bytes

    def json(self, label: str) -> dict:
        return _json_from_raw(self.raw, label)


class ArtifactStore:
    """Containment-safe, no-symlink, hash-checked, read-once bundle store."""

    def __init__(self, root: Path):
        try:
            self.root = root.resolve(strict=True)
        except OSError as exc:
            raise ContractError([f"bundle root does not exist: {root}"]) from exc
        if not self.root.is_dir():
            raise ContractError([f"bundle root is not a directory: {root}"])
        self._cache: dict[str, LoadedArtifact] = {}
        self._declared_hashes: dict[str, str] = {}

    @staticmethod
    def _parts(relative: str, label: str) -> list[str]:
        if "\\" in relative:
            raise ContractError([f"bundle {label}: backslash path separators are forbidden"])
        parts = relative.split("/")
        if not parts or any(part in ("", ".", "..") for part in parts):
            raise ContractError([f"bundle {label}: path is not a normalized relative path"])
        if relative.startswith("/"):
            raise ContractError([f"bundle {label}: absolute path is forbidden"])
        return parts

    def _open_relative(self, relative: str, label: str) -> bytes:
        parts = self._parts(relative, label)
        dir_flags = os.O_RDONLY
        if hasattr(os, "O_DIRECTORY"):
            dir_flags |= os.O_DIRECTORY
        if hasattr(os, "O_NOFOLLOW"):
            dir_flags |= os.O_NOFOLLOW
        file_flags = os.O_RDONLY
        if hasattr(os, "O_NOFOLLOW"):
            file_flags |= os.O_NOFOLLOW
        try:
            current_fd = os.open(self.root, dir_flags)
        except OSError as exc:  # pragma: no cover - root was validated
            raise ContractError([f"bundle {label}: cannot open bundle root: {exc}"]) from exc
        file_fd: int | None = None
        try:
            for part in parts[:-1]:
                next_fd = os.open(part, dir_flags, dir_fd=current_fd)
                os.close(current_fd)
                current_fd = next_fd
            file_fd = os.open(parts[-1], file_flags, dir_fd=current_fd)
            before = os.fstat(file_fd)
            if not stat.S_ISREG(before.st_mode):
                raise ContractError([f"bundle {label}: artifact is not a regular file"])
            chunks: list[bytes] = []
            total = 0
            while True:
                chunk = os.read(file_fd, min(1024 * 1024, MAX_ARTIFACT_BYTES + 1 - total))
                if not chunk:
                    break
                chunks.append(chunk)
                total += len(chunk)
                if total > MAX_ARTIFACT_BYTES:
                    raise ContractError(
                        [f"bundle {label}: artifact exceeds {MAX_ARTIFACT_BYTES} bytes"]
                    )
            after = os.fstat(file_fd)
            before_fp = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
            after_fp = (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
            if before_fp != after_fp or total != after.st_size:
                raise ContractError([f"bundle {label}: artifact changed while read"])
            return b"".join(chunks)
        except OSError as exc:
            raise ContractError(
                [f"bundle {label}: cannot open regular no-symlink artifact {relative}: {exc}"]
            ) from exc
        finally:
            if file_fd is not None:
                os.close(file_fd)
            os.close(current_fd)

    def read(self, entry: dict, label: str) -> LoadedArtifact:
        relative = entry["path"]
        expected = entry["sha256"]
        prior_hash = self._declared_hashes.get(relative)
        if prior_hash is not None and prior_hash != expected:
            raise ContractError(
                [f"bundle {label}: one path is declared with conflicting sha256 values"]
            )
        self._declared_hashes[relative] = expected
        if relative in self._cache:
            return self._cache[relative]
        raw = self._open_relative(relative, label)
        actual = bytes_hash(raw)
        if actual != expected:
            raise ContractError(
                [f"bundle {label}: sha256 mismatch (expected {expected}, actual {actual})"]
            )
        artifact = LoadedArtifact(relative, raw)
        self._cache[relative] = artifact
        return artifact


def _parse_base(base_raw: bytes, label: str = "base draft") -> tuple[str, ParsedDocument]:
    try:
        text = base_raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ContractError([f"{label}: invalid UTF-8: {exc}"]) from exc
    try:
        parsed = parse_document(text)
    except BlockParseError as exc:
        raise ContractError([f"{label}: block parse rejected [{exc.kind}]: {exc}"]) from exc
    return text, parsed


def validate_block_manifest(manifest: dict, manifest_raw: bytes, base_raw: bytes) -> ParsedDocument:
    failures = _schema_failures(manifest, BLOCK_MANIFEST_SCHEMA_PATH, "block manifest")
    parsed: ParsedDocument | None = None
    try:
        _text, parsed = _parse_base(base_raw)
    except ContractError as exc:
        failures.extend(exc.failures)
    if failures:
        raise ContractError(failures)
    assert parsed is not None  # established by the failure gate above
    expected_base = base_draft_hash(base_raw)
    if manifest["base_draft_hash"] != expected_base:
        failures.append("block manifest base_draft_hash does not match exact base bytes")
    expected_blocks = [
        {"block_id": block.block_id, "old_hash": block.norm_hash}
        for block in parsed.blocks
    ]
    actual_blocks = [
        {"block_id": row["block_id"], "old_hash": row["old_hash"]}
        for row in manifest["blocks"]
    ]
    if actual_blocks != expected_blocks:
        failures.append("block manifest block_id/old_hash sequence does not match parsed base")
    if failures:
        raise ContractError(failures)
    return parsed


def _source_key(ref: dict) -> tuple[int, int, int, int]:
    return (
        SEAT_ORDER[ref["seat"]],
        ref["ordinal"],
        ref["subclaim_ordinal"],
        CHANNEL_ORDER[ref["channel"]],
    )


def _target_key(target: dict) -> tuple[int, str, tuple[int, ...]]:
    block_id = target["block_id"]
    if block_id == "DOC-BODY-START":
        block_order = -1
    else:
        block_order = int(block_id[1:])
    return (
        block_order,
        block_id,
        tuple(OP_ORDER[op] for op in target["allowed_operations"]),
    )


def _target_map(targets: Iterable[dict]) -> dict[str, set[str]]:
    return {target["block_id"]: set(target["allowed_operations"]) for target in targets}


def _validate_target_list(
    targets: list[dict],
    *,
    label: str,
    valid_block_ids: set[str] | None,
    failures: list[str],
) -> None:
    block_ids = [target["block_id"] for target in targets]
    if len(block_ids) != len(set(block_ids)):
        failures.append(f"{label}: each block_id may appear only once")
    for target in targets:
        operations = target["allowed_operations"]
        if operations != sorted(operations, key=OP_ORDER.__getitem__):
            failures.append(f"{label}: allowed_operations must use canonical operation order")
        if valid_block_ids is not None and target["block_id"] not in valid_block_ids:
            failures.append(f"{label}: block {target['block_id']} does not exist in the base")
    if targets != sorted(targets, key=_target_key):
        failures.append(f"{label}: target rows must use canonical block/operation order")


def _has_forbidden_work_language(text: str) -> bool:
    folded = " " + " ".join(text.lower().split()) + " "
    if _WORK_RANK_RE.search(folded):
        return True
    return _TIME_UNIT_RE.search(folded) is not None


def _has_forbidden_prediction_language(text: str) -> bool:
    return _PREDICTION_LANGUAGE_RE.search(" ".join(text.split())) is not None


def validate_roadmap(
    roadmap: dict,
    *,
    roadmap_raw: bytes | None = None,
    base_raw: bytes | None = None,
    block_manifest: dict | None = None,
    block_manifest_raw: bytes | None = None,
) -> None:
    failures = _schema_failures(roadmap, ROADMAP_SCHEMA_PATH, "roadmap")
    if failures:
        raise ContractError(failures)

    parsed: ParsedDocument | None = None
    if base_raw is not None:
        if roadmap["base_draft_sha256"] != bytes_hash(base_raw):
            failures.append("roadmap base_draft_sha256 does not match exact base bytes")
        try:
            _text, parsed = _parse_base(base_raw)
        except ContractError as exc:
            failures.extend(exc.failures)
    if block_manifest_raw is not None:
        if roadmap["block_manifest_sha256"] != bytes_hash(block_manifest_raw):
            failures.append("roadmap block_manifest_sha256 does not match exact manifest bytes")
        if block_manifest is None or base_raw is None:
            failures.append("roadmap block-manifest replay requires both manifest JSON and base bytes")
        else:
            try:
                parsed = validate_block_manifest(block_manifest, block_manifest_raw, base_raw)
            except ContractError as exc:
                failures.extend(exc.failures)

    items = roadmap["items"]
    item_ids = [item["id"] for item in items]
    if len(item_ids) != len(set(item_ids)):
        failures.append("roadmap items: duplicate id")
    if roadmap["total_items"] != len(items):
        failures.append("roadmap total_items does not equal items length")
    counts = {name: 0 for name in OBLIGATION_CLASSES}
    all_source_keys: list[tuple[int, int, int, int]] = []
    valid_blocks = None
    if parsed is not None:
        valid_blocks = {block.block_id for block in parsed.blocks if block.block_id}
        valid_blocks.add("DOC-BODY-START")
    for item in items:
        counts[item["obligation_class"]] += 1
        refs = item["source_refs"]
        keys = [_source_key(ref) for ref in refs]
        if keys != sorted(keys):
            failures.append(f"roadmap item {item['id']}: source_refs must be in immutable source order")
        all_source_keys.extend(keys)
        for field in ("suggested_action", "verification_criteria"):
            if _has_forbidden_work_language(item[field]):
                failures.append(
                    f"roadmap item {item['id']} {field}: work-rank or time-estimate language is forbidden"
                )
            if _has_forbidden_prediction_language(item[field]):
                failures.append(
                    f"roadmap item {item['id']} {field}: acceptance-prediction language is forbidden"
                )
        if _has_forbidden_work_language(item["cost_scope"]["locator"]):
            failures.append(
                f"roadmap item {item['id']} cost_scope.locator: describe a surface, not a work rank/time estimate"
            )
        if _has_forbidden_prediction_language(item["cost_scope"]["locator"]):
            failures.append(
                f"roadmap item {item['id']} cost_scope.locator: acceptance-prediction language is forbidden"
            )
        consequence_locator = item["consequence_if_unaddressed"]["target"]["locator"]
        if _has_forbidden_work_language(consequence_locator):
            failures.append(
                f"roadmap item {item['id']} consequence target: use a locator, not a work rank/time estimate"
            )
        if _has_forbidden_prediction_language(consequence_locator):
            failures.append(
                f"roadmap item {item['id']} consequence target: acceptance-prediction language is forbidden"
            )
        _validate_target_list(
            item["proposed_targets"],
            label=f"roadmap item {item['id']} proposed_targets",
            valid_block_ids=valid_blocks,
            failures=failures,
        )
    if len(all_source_keys) != len(set(all_source_keys)):
        failures.append("roadmap source_refs: each immutable source position must be unique")
    expected_order = sorted(items, key=lambda item: (_source_key(item["source_refs"][0]), item["id"]))
    if items != expected_order:
        failures.append("roadmap items must use deterministic primary-source order")
    if roadmap["obligation_counts"] != counts:
        failures.append("roadmap obligation_counts does not recompute from obligation_class")
    if failures:
        raise ContractError(failures)


def validate_claim_surface_manifest(
    claim_surface: dict,
    *,
    claim_surface_raw: bytes,
    roadmap: dict,
    roadmap_raw: bytes,
    base_raw: bytes,
    artifact_store: ArtifactStore,
) -> dict[str, dict]:
    failures = _schema_failures(
        claim_surface, CLAIM_SURFACE_SCHEMA_PATH, "claim surface manifest"
    )
    if failures:
        raise ContractError(failures)
    if claim_surface["roadmap_sha256"] != bytes_hash(roadmap_raw):
        failures.append("claim surface roadmap_sha256 does not match exact roadmap bytes")
    if claim_surface["base_draft_sha256"] != bytes_hash(base_raw):
        failures.append("claim surface base_draft_sha256 does not match exact base bytes")
    if claim_surface["revision_round"] != roadmap["revision_round"]:
        failures.append("claim surface revision_round does not match roadmap")

    text, parsed = _parse_base(base_raw)
    blocks = parsed.block_by_id()
    source_ids: set[str] = set()
    claims: dict[tuple[str, str], dict] = {}
    for index, source in enumerate(claim_surface["claim_intent_sources"]):
        manifest_id = source["scoped_manifest_id"]
        if manifest_id in source_ids:
            failures.append(f"claim intent sources: duplicate scoped_manifest_id {manifest_id}")
            continue
        source_ids.add(manifest_id)
        try:
            artifact = artifact_store.read(
                source["artifact"], f"claim_intent_sources[{index}]"
            )
            manifest = artifact.json(f"claim intent source {manifest_id}")
            failures.extend(
                _schema_failures(manifest, CLAIM_INTENT_SCHEMA_PATH, f"claim intent {manifest_id}")
            )
            if manifest.get("manifest_id") != manifest_id:
                failures.append(
                    f"claim intent source {manifest_id}: artifact manifest_id differs"
                )
            seen_claim_ids: set[str] = set()
            for claim in manifest.get("claims", []):
                claim_id = claim.get("claim_id")
                if claim_id in seen_claim_ids:
                    failures.append(
                        f"claim intent source {manifest_id}: duplicate claim_id {claim_id}"
                    )
                seen_claim_ids.add(claim_id)
                claims[(manifest_id, claim_id)] = claim
        except ContractError as exc:
            failures.extend(exc.failures)

    surfaces_by_id: dict[str, dict] = {}
    referenced_sources: set[str] = set()
    byte_ranges: list[tuple[int, int, str]] = []
    block_text_counts: dict[tuple[str, str], int] = {}
    for surface in claim_surface["surfaces"]:
        surface_id = surface["surface_id"]
        if surface_id in surfaces_by_id:
            failures.append(f"claim surfaces: duplicate surface_id {surface_id}")
        surfaces_by_id[surface_id] = surface
        key = (surface["scoped_manifest_id"], surface["claim_id"])
        referenced_sources.add(key[0])
        claim = claims.get(key)
        if claim is None:
            failures.append(
                f"claim surface {surface_id}: ({key[0]}, {key[1]}) does not resolve"
            )
        elif bytes_hash(claim["claim_text"].encode("utf-8")) != surface["intent_claim_text_sha256"]:
            failures.append(
                f"claim surface {surface_id}: intent_claim_text_sha256 does not match source claim"
            )
        elif surface["original_text"] != claim["claim_text"]:
            failures.append(
                f"claim surface {surface_id}: original_text must equal the referenced ClaimIntent claim_text exactly"
            )
        original_raw = surface["original_text"].encode("utf-8")
        if bytes_hash(original_raw) != surface["original_text_sha256"]:
            failures.append(f"claim surface {surface_id}: original_text_sha256 mismatch")
        start, end = surface["utf8_start"], surface["utf8_end"]
        if not (start < end <= len(base_raw)) or base_raw[start:end] != original_raw:
            failures.append(f"claim surface {surface_id}: UTF-8 span does not select exact original_text")
        block = blocks.get(surface["block_id"])
        if block is None:
            failures.append(f"claim surface {surface_id}: block does not exist")
        else:
            block_start = len(text[: block.span[0]].encode("utf-8"))
            block_end = len(text[: block.span[1]].encode("utf-8"))
            if not (block_start <= start < end <= block_end):
                failures.append(f"claim surface {surface_id}: UTF-8 span escapes declared block")
            count_key = (surface["block_id"], surface["original_text"])
            # Use the exact raw block slice. Normalization is appropriate for
            # block hashes, but a registered claim surface is an absolute
            # UTF-8 byte witness and must replay against the original bytes.
            count = text[block.span[0] : block.span[1]].count(surface["original_text"])
            block_text_counts[count_key] = count
            if count != 1:
                failures.append(
                    f"claim surface {surface_id}: original_text must occur exactly once in its block"
                )
        byte_ranges.append((start, end, surface_id))
    if referenced_sources != source_ids:
        failures.append(
            "claim intent sources must equal exactly the manifests referenced by surfaces"
        )
    byte_ranges.sort()
    for prior, current in zip(byte_ranges, byte_ranges[1:]):
        if current[0] < prior[1]:
            failures.append(
                f"claim surfaces {prior[2]} and {current[2]} overlap in the base draft"
            )
    if failures:
        raise ContractError(failures)
    return surfaces_by_id


def _claim_auth_projection(value: dict) -> dict:
    fields = (
        "authorization_id",
        "surface_id",
        "scoped_manifest_id",
        "claim_id",
        "block_id",
        "original_text_sha256",
        "replacement_text_sha256",
        "from_rung",
        "to_rung",
        "direction",
    )
    return {field: value[field] for field in fields}


def validate_author_adjudication(
    adjudication: dict,
    *,
    adjudication_raw: bytes,
    roadmap: dict,
    roadmap_raw: bytes,
    claim_surface: dict,
    claim_surface_raw: bytes,
    base_raw: bytes,
    surfaces_by_id: dict[str, dict],
) -> dict:
    failures = _schema_failures(adjudication, AUTHOR_SCHEMA_PATH, "author adjudication")
    if failures:
        raise ContractError(failures)
    if adjudication["roadmap_sha256"] != bytes_hash(roadmap_raw):
        failures.append("author adjudication roadmap_sha256 does not match exact roadmap bytes")
    if adjudication["base_draft_sha256"] != bytes_hash(base_raw):
        failures.append("author adjudication base_draft_sha256 does not match exact base bytes")
    if adjudication["claim_surface_manifest_sha256"] != bytes_hash(claim_surface_raw):
        failures.append(
            "author adjudication claim_surface_manifest_sha256 does not match exact bytes"
        )
    if adjudication["revision_round"] != roadmap["revision_round"]:
        failures.append("author adjudication revision_round does not match roadmap")

    event_ids = [event["event_id"] for event in adjudication["author_events"]]
    if len(event_ids) != len(set(event_ids)):
        failures.append("author adjudication author_events: duplicate event_id")
    event_set = set(event_ids)
    if adjudication["display_order"]["author_event_id"] not in event_set:
        failures.append("author adjudication display_order author_event_id does not resolve")

    roadmap_items = {item["id"]: item for item in roadmap["items"]}
    roadmap_ids = list(roadmap_items)
    display_ids = adjudication["display_order"]["item_ids"]
    if len(display_ids) != len(set(display_ids)) or set(display_ids) != set(roadmap_ids):
        failures.append("author display_order.item_ids must be a full unique roadmap permutation")
    if (
        adjudication["display_order"]["mode"] == "source_traceability"
        and display_ids != roadmap_ids
    ):
        failures.append("source_traceability author view must equal immutable roadmap order")

    records: dict[str, dict] = {}
    claim_auths: dict[str, tuple[str, dict]] = {}
    claim_auth_surface_ids: dict[str, str] = {}
    for record in adjudication["author_adjudications"]:
        item_id = record["item_id"]
        if item_id in records:
            failures.append(f"author adjudications: duplicate item_id {item_id}")
        records[item_id] = record
        item = roadmap_items.get(item_id)
        if item is None:
            failures.append(f"author adjudication item {item_id} does not resolve")
            continue
        if record["author_event_id"] not in event_set:
            failures.append(f"author adjudication {item_id}: author_event_id does not resolve")
        if record["author_triage"] == "will_address" and "author_reason" in record:
            failures.append(
                f"author adjudication {item_id}: will_address must not carry author_reason"
            )
        _validate_target_list(
            record["authorized_targets"],
            label=f"author adjudication {item_id} authorized_targets",
            valid_block_ids=None,
            failures=failures,
        )
        proposed = _target_map(item["proposed_targets"])
        for target in record["authorized_targets"]:
            proposed_ops = proposed.get(target["block_id"])
            if proposed_ops is None or not set(target["allowed_operations"]).issubset(proposed_ops):
                failures.append(
                    f"author adjudication {item_id}: authorized target exceeds reviewer-proposed scope"
                )
        authorized = _target_map(record["authorized_targets"])
        for authorization in record["claim_strength_authorizations"]:
            auth_id = authorization["authorization_id"]
            if auth_id in claim_auths:
                failures.append(f"claim authorizations: duplicate authorization_id {auth_id}")
            claim_auths[auth_id] = (item_id, authorization)
            surface_id = authorization["surface_id"]
            prior_auth_id = claim_auth_surface_ids.get(surface_id)
            if prior_auth_id is not None:
                failures.append(
                    f"claim authorizations: surface_id {surface_id} is authorized more than once "
                    f"({prior_auth_id}, {auth_id})"
                )
            else:
                claim_auth_surface_ids[surface_id] = auth_id
            if authorization["author_event_id"] not in event_set:
                failures.append(f"claim authorization {auth_id}: author_event_id does not resolve")
            surface = surfaces_by_id.get(authorization["surface_id"])
            if surface is None:
                failures.append(f"claim authorization {auth_id}: surface_id does not resolve")
            else:
                for field in (
                    "scoped_manifest_id",
                    "claim_id",
                    "block_id",
                    "original_text_sha256",
                ):
                    if authorization[field] != surface[field]:
                        failures.append(
                            f"claim authorization {auth_id}: {field} differs from registered surface"
                        )
                if authorization["from_rung"] != surface["current_rung"]:
                    failures.append(
                        f"claim authorization {auth_id}: from_rung differs from registered current_rung"
                    )
            if authorization["from_rung"] == authorization["to_rung"]:
                failures.append(f"claim authorization {auth_id}: from_rung and to_rung must differ")
            replacement = authorization["replacement_text"].encode("utf-8")
            if bytes_hash(replacement) != authorization["replacement_text_sha256"]:
                failures.append(f"claim authorization {auth_id}: replacement_text_sha256 mismatch")
            compatible_ops = authorized.get(authorization["block_id"], set())
            needed_op = "delete_block" if authorization["replacement_text"] == "" else "replace_block"
            if needed_op not in compatible_ops:
                failures.append(
                    f"claim authorization {auth_id}: authorized target lacks compatible {needed_op}"
                )
    if set(records) != set(roadmap_items):
        failures.append(
            "complete author adjudication must contain exactly one record per roadmap item"
        )

    collateral: dict[str, dict] = {}
    for authorization in adjudication["collateral_authorizations"]:
        auth_id = authorization["authorization_id"]
        if auth_id in collateral:
            failures.append(f"collateral authorizations: duplicate authorization_id {auth_id}")
        collateral[auth_id] = authorization
        if authorization["author_event_id"] not in event_set:
            failures.append(f"collateral authorization {auth_id}: author_event_id does not resolve")
        accepted = records.get(authorization["authorizing_item_id"])
        declined = records.get(authorization["constrained_item_id"])
        if accepted is None or accepted["author_triage"] != "will_address":
            failures.append(
                f"collateral authorization {auth_id}: authorizing_item_id must be will_address"
            )
        if declined is None or declined["author_triage"] not in DECLINED_TRIAGE:
            failures.append(
                f"collateral authorization {auth_id}: constrained_item_id must be declined"
            )
        if authorization["authorizing_item_id"] == authorization["constrained_item_id"]:
            failures.append(f"collateral authorization {auth_id}: item ids must differ")
        if accepted is not None:
            accepted_ops = _target_map(accepted["authorized_targets"]).get(
                authorization["block_id"], set()
            )
            if authorization["operation"] not in accepted_ops:
                failures.append(
                    f"collateral authorization {auth_id}: accepted item does not authorize exact target/op"
                )
        constrained_item = roadmap_items.get(authorization["constrained_item_id"])
        if constrained_item is not None:
            constrained_blocks = _target_map(constrained_item["proposed_targets"])
            if authorization["block_id"] not in constrained_blocks:
                failures.append(
                    f"collateral authorization {auth_id}: block is outside declined item's no-touch scope"
                )
    if failures:
        raise ContractError(failures)
    return {
        "records": records,
        "claim_authorizations": claim_auths,
        "collateral_authorizations": collateral,
        "author_decision_digest": author_decision_digest(adjudication),
    }


def build_author_adjudication(
    choice_input: dict,
    *,
    roadmap: dict,
    roadmap_raw: bytes,
    claim_surface: dict,
    claim_surface_raw: bytes,
    base_raw: bytes,
    surfaces_by_id: dict[str, dict],
) -> dict:
    failures = _schema_failures(choice_input, AUTHOR_INPUT_SCHEMA_PATH, "author choice input")
    if failures:
        raise ContractError(failures)
    adjudication = {
        "schema_version": CURRENT_AUTHOR_VERSION,
        "revision_round": roadmap["revision_round"],
        "roadmap_sha256": bytes_hash(roadmap_raw),
        "base_draft_sha256": bytes_hash(base_raw),
        "claim_surface_manifest_sha256": bytes_hash(claim_surface_raw),
        "adjudication_status": "complete",
        "author_events": copy.deepcopy(choice_input["author_events"]),
        "display_order": copy.deepcopy(choice_input["display_order"]),
        "author_adjudications": copy.deepcopy(choice_input["author_adjudications"]),
        "collateral_authorizations": copy.deepcopy(
            choice_input["collateral_authorizations"]
        ),
    }
    raw = canonical_bytes(adjudication)
    validate_author_adjudication(
        adjudication,
        adjudication_raw=raw,
        roadmap=roadmap,
        roadmap_raw=roadmap_raw,
        claim_surface=claim_surface,
        claim_surface_raw=claim_surface_raw,
        base_raw=base_raw,
        surfaces_by_id=surfaces_by_id,
    )
    return adjudication


def _op_authorized(record: dict, op: dict) -> bool:
    return op["op"] in _target_map(record["authorized_targets"]).get(op["block_id"], set())


def validate_review_patch_authorization(
    patch: dict,
    *,
    base_raw: bytes,
    roadmap: dict,
    roadmap_raw: bytes,
    adjudication: dict,
    adjudication_raw: bytes,
    claim_surface: dict,
    claim_surface_raw: bytes,
    surfaces_by_id: dict[str, dict],
) -> dict:
    failures = _schema_failures(patch, PATCH_SCHEMA_PATH, "review patch")
    if failures:
        raise ContractError(failures)
    if patch.get("patch_format_version") != CURRENT_PATCH_VERSION:
        failures.append(f"patch_format_version must be {CURRENT_PATCH_VERSION} for writes")
    if patch.get("authorization_context") != "review_roadmap":
        failures.append("review patch authorization_context must be review_roadmap")
    expected_bindings = {
        "roadmap_sha256": bytes_hash(roadmap_raw),
        "author_adjudication_sha256": bytes_hash(adjudication_raw),
        "author_decision_digest": author_decision_digest(adjudication),
        "claim_surface_manifest_sha256": bytes_hash(claim_surface_raw),
    }
    for field, expected in expected_bindings.items():
        if patch.get(field) != expected:
            failures.append(f"review patch {field} does not match bound artifact")
    if patch.get("revision_round") != roadmap["revision_round"]:
        failures.append("review patch revision_round does not match roadmap")
    if patch.get("base_draft_hash") != base_draft_hash(base_raw):
        failures.append("review patch base_draft_hash does not match exact base bytes")

    author_state = validate_author_adjudication(
        adjudication,
        adjudication_raw=adjudication_raw,
        roadmap=roadmap,
        roadmap_raw=roadmap_raw,
        claim_surface=claim_surface,
        claim_surface_raw=claim_surface_raw,
        base_raw=base_raw,
        surfaces_by_id=surfaces_by_id,
    )
    records = author_state["records"]
    claim_auths = author_state["claim_authorizations"]
    collateral = author_state["collateral_authorizations"]
    roadmap_items = {item["id"]: item for item in roadmap["items"]}
    declined_by_block: dict[str, set[str]] = {}
    for item_id, record in records.items():
        if record["author_triage"] in DECLINED_TRIAGE:
            for target in roadmap_items[item_id]["proposed_targets"]:
                declined_by_block.setdefault(target["block_id"], set()).add(item_id)
    surfaces_by_block: dict[str, list[dict]] = {}
    for surface in surfaces_by_id.values():
        surfaces_by_block.setdefault(surface["block_id"], []).append(surface)

    used_claim_auths: set[str] = set()
    used_collateral: set[str] = set()
    protected_surfaces_checked = 0
    for index, op in enumerate(patch.get("ops", [])):
        cited = op.get("roadmap_item_ids", [])
        if len(cited) != len(set(cited)):
            failures.append(f"patch op {index}: duplicate roadmap_item_ids")
        for item_id in cited:
            record = records.get(item_id)
            if record is None:
                failures.append(f"patch op {index}: roadmap item {item_id} does not resolve")
            elif record["author_triage"] != "will_address":
                failures.append(f"patch op {index}: declined item {item_id} cannot authorize work")
            elif not _op_authorized(record, op):
                failures.append(
                    f"patch op {index}: target/op is outside accepted item {item_id}'s exact scope"
                )

        op_claim_auths: dict[str, dict] = {}
        for move in op.get("claim_strength_changes", []):
            auth_id = move["authorization_id"]
            if auth_id in used_claim_auths:
                failures.append(f"patch op {index}: claim authorization {auth_id} is reused")
            used_claim_auths.add(auth_id)
            target = claim_auths.get(auth_id)
            if target is None:
                failures.append(f"patch op {index}: claim authorization {auth_id} does not resolve")
                continue
            owner_item, authorization = target
            if owner_item not in cited:
                failures.append(
                    f"patch op {index}: claim authorization {auth_id} belongs to uncited item {owner_item}"
                )
            if _claim_auth_projection(move) != _claim_auth_projection(authorization):
                failures.append(
                    f"patch op {index}: claim move {auth_id} differs from exact author authorization"
                )
            if authorization["block_id"] != op["block_id"]:
                failures.append(f"patch op {index}: claim authorization {auth_id} targets another block")
            op_claim_auths[authorization["surface_id"]] = authorization

        cited_collateral = op.get("collateral_authorization_ids", [])
        if len(cited_collateral) != len(set(cited_collateral)):
            failures.append(f"patch op {index}: duplicate collateral authorization ids")
        covered_declined: set[str] = set()
        for auth_id in cited_collateral:
            if auth_id in used_collateral:
                failures.append(f"patch op {index}: collateral authorization {auth_id} is reused")
            used_collateral.add(auth_id)
            authorization = collateral.get(auth_id)
            if authorization is None:
                failures.append(f"patch op {index}: collateral authorization {auth_id} does not resolve")
                continue
            if authorization["authorizing_item_id"] not in cited:
                failures.append(
                    f"patch op {index}: collateral {auth_id} belongs to an uncited accepted item"
                )
            if (
                authorization["block_id"] != op["block_id"]
                or authorization["operation"] != op["op"]
            ):
                failures.append(f"patch op {index}: collateral {auth_id} does not match exact target/op")
            covered_declined.add(authorization["constrained_item_id"])
        required_declined = declined_by_block.get(op["block_id"], set())
        if covered_declined != required_declined:
            missing = sorted(required_declined - covered_declined)
            extra = sorted(covered_declined - required_declined)
            failures.append(
                f"patch op {index}: declined no-touch coverage mismatch (missing {missing}, extra {extra})"
            )

        touched_surfaces = surfaces_by_block.get(op["block_id"], [])
        touched_surface_ids = {surface["surface_id"] for surface in touched_surfaces}
        if set(op_claim_auths) - touched_surface_ids:
            failures.append(f"patch op {index}: claim authorization cites a surface outside target block")
        for surface in touched_surfaces:
            protected_surfaces_checked += 1
            authorization = op_claim_auths.get(surface["surface_id"])
            original = surface["original_text"]
            if op["op"] == "insert_after":
                if authorization is not None:
                    failures.append(
                        f"patch op {index}: insert_after cannot rewrite registered surface {surface['surface_id']}"
                    )
                continue
            if op["op"] == "delete_block":
                if authorization is None or authorization["replacement_text"] != "":
                    failures.append(
                        f"patch op {index}: deleting registered surface {surface['surface_id']} requires exact empty replacement authorization"
                    )
                continue
            new_text = op["new_text"]
            if authorization is None:
                if new_text.count(original) != 1:
                    failures.append(
                        f"patch op {index}: registered surface {surface['surface_id']} must remain exact or use authorization"
                    )
            else:
                replacement = authorization["replacement_text"]
                if replacement == original:
                    failures.append(
                        f"patch op {index}: authorized claim replacement must differ from original bytes"
                    )
                if original in new_text or new_text.count(replacement) != 1:
                    failures.append(
                        f"patch op {index}: claim authorization for {surface['surface_id']} must replace exact original once with exact approved bytes"
                    )
    if failures:
        raise ContractError(failures)
    return {
        "status": "pass",
        **expected_bindings,
        "registered_claim_surfaces_checked": protected_surfaces_checked,
        "unregistered_claim_drift_review_required": True,
    }


def validate_integrity_correction_list(
    issue_list: dict,
    *,
    issue_list_raw: bytes,
    base_raw: bytes,
) -> dict[str, dict]:
    failures = _schema_failures(issue_list, INTEGRITY_LIST_SCHEMA_PATH, "integrity correction list")
    if failures:
        raise ContractError(failures)
    if issue_list["base_draft_sha256"] != bytes_hash(base_raw):
        failures.append("integrity correction list base_draft_sha256 does not match base")
    _text, parsed = _parse_base(base_raw)
    valid_blocks = {block.block_id for block in parsed.blocks if block.block_id}
    valid_blocks.add("DOC-BODY-START")
    issues: dict[str, dict] = {}
    for issue in issue_list["issues"]:
        issue_id = issue["correction_id"]
        if issue_id in issues:
            failures.append(f"integrity correction list: duplicate correction_id {issue_id}")
        issues[issue_id] = issue
        _validate_target_list(
            issue["proposed_targets"],
            label=f"integrity correction {issue_id} proposed_targets",
            valid_block_ids=valid_blocks,
            failures=failures,
        )
    if failures:
        raise ContractError(failures)
    return issues


def validate_integrity_authorization(
    authorization: dict,
    *,
    authorization_raw: bytes,
    issue_list: dict,
    issue_list_raw: bytes,
    patch: dict,
    patch_raw: bytes,
    base_raw: bytes,
) -> dict:
    """Replay explicit author approval of one exact integrity patch."""
    failures = _schema_failures(
        authorization,
        INTEGRITY_AUTH_SCHEMA_PATH,
        "integrity correction authorization",
    )
    if failures:
        raise ContractError(failures)
    issues = validate_integrity_correction_list(
        issue_list,
        issue_list_raw=issue_list_raw,
        base_raw=base_raw,
    )
    patch_failures = _schema_failures(patch, PATCH_SCHEMA_PATH, "integrity patch")
    failures.extend(patch_failures)
    if authorization["revision_round"] != issue_list["revision_round"]:
        failures.append("integrity authorization revision_round does not match issue list")
    if authorization["base_draft_sha256"] != bytes_hash(base_raw):
        failures.append("integrity authorization base_draft_sha256 does not match base")
    if authorization["issue_list_sha256"] != bytes_hash(issue_list_raw):
        failures.append("integrity authorization issue_list_sha256 does not match exact bytes")
    if authorization["revision_patch_sha256"] != bytes_hash(patch_raw):
        failures.append("integrity authorization revision_patch_sha256 does not match exact patch bytes")
    if patch.get("authorization_context") != "integrity_correction":
        failures.append("integrity authorization requires an integrity_correction patch")
    if patch.get("issue_list_sha256") != bytes_hash(issue_list_raw):
        failures.append("integrity patch issue_list_sha256 does not match exact issue-list bytes")
    if patch.get("base_draft_hash") != base_draft_hash(base_raw):
        failures.append("integrity patch base_draft_hash does not match exact base bytes")
    if patch.get("revision_round") != issue_list["revision_round"]:
        failures.append("integrity patch revision_round does not match issue list")

    event_ids = [event["event_id"] for event in authorization["author_events"]]
    if len(event_ids) != len(set(event_ids)):
        failures.append("integrity authorization author_events: duplicate event_id")
    event_set = set(event_ids)
    decisions: dict[str, dict] = {}
    for decision in authorization["author_decisions"]:
        correction_id = decision["correction_id"]
        if correction_id in decisions:
            failures.append(
                f"integrity authorization: duplicate correction_id {correction_id}"
            )
        decisions[correction_id] = decision
        issue = issues.get(correction_id)
        if issue is None:
            failures.append(
                f"integrity authorization correction_id {correction_id} does not resolve"
            )
            continue
        if decision["author_event_id"] not in event_set:
            failures.append(
                f"integrity authorization {correction_id}: author_event_id does not resolve"
            )
        _validate_target_list(
            decision["authorized_targets"],
            label=f"integrity authorization {correction_id} authorized_targets",
            valid_block_ids=None,
            failures=failures,
        )
        proposed = _target_map(issue["proposed_targets"])
        for target in decision["authorized_targets"]:
            proposed_ops = proposed.get(target["block_id"])
            if proposed_ops is None or not set(target["allowed_operations"]).issubset(
                proposed_ops
            ):
                failures.append(
                    f"integrity authorization {correction_id}: authorized target exceeds proposed scope"
                )
    if set(decisions) != set(issues):
        failures.append(
            "integrity authorization must contain exactly one author decision per correction"
        )
    if failures:
        raise ContractError(failures)
    return {
        "decisions": decisions,
        "integrity_authorization_sha256": bytes_hash(authorization_raw),
    }


def build_integrity_authorization(
    choice_input: dict,
    *,
    issue_list: dict,
    issue_list_raw: bytes,
    patch: dict,
    patch_raw: bytes,
    base_raw: bytes,
) -> dict:
    failures = _schema_failures(
        choice_input,
        INTEGRITY_AUTH_INPUT_SCHEMA_PATH,
        "integrity correction authorization input",
    )
    if failures:
        raise ContractError(failures)
    if choice_input["revision_patch_sha256"] != bytes_hash(patch_raw):
        raise ContractError(
            [
                "integrity authorization input revision_patch_sha256 does not match exact proposed patch bytes"
            ]
        )
    authorization = {
        "schema_version": "integrity-correction-authorization/1.0",
        "revision_round": issue_list["revision_round"],
        "base_draft_sha256": bytes_hash(base_raw),
        "issue_list_sha256": bytes_hash(issue_list_raw),
        "revision_patch_sha256": choice_input["revision_patch_sha256"],
        "author_events": copy.deepcopy(choice_input["author_events"]),
        "author_decisions": copy.deepcopy(choice_input["author_decisions"]),
    }
    validate_integrity_authorization(
        authorization,
        authorization_raw=canonical_bytes(authorization) + b"\n",
        issue_list=issue_list,
        issue_list_raw=issue_list_raw,
        patch=patch,
        patch_raw=patch_raw,
        base_raw=base_raw,
    )
    return authorization


def validate_integrity_patch_authorization(
    patch: dict,
    *,
    patch_raw: bytes,
    base_raw: bytes,
    issue_list: dict,
    issue_list_raw: bytes,
    integrity_authorization: dict,
    integrity_authorization_raw: bytes,
) -> dict:
    failures = _schema_failures(patch, PATCH_SCHEMA_PATH, "integrity patch")
    if failures:
        raise ContractError(failures)
    if patch.get("patch_format_version") != CURRENT_PATCH_VERSION:
        failures.append(f"integrity patch_format_version must be {CURRENT_PATCH_VERSION}")
    if patch.get("authorization_context") != "integrity_correction":
        failures.append("integrity patch authorization_context must be integrity_correction")
    if patch.get("issue_list_sha256") != bytes_hash(issue_list_raw):
        failures.append("integrity patch issue_list_sha256 does not match exact issue-list bytes")
    if patch.get("base_draft_hash") != base_draft_hash(base_raw):
        failures.append("integrity patch base_draft_hash does not match exact base bytes")
    if patch.get("revision_round") != issue_list["revision_round"]:
        failures.append("integrity patch revision_round does not match issue list")
    authorization_state = validate_integrity_authorization(
        integrity_authorization,
        authorization_raw=integrity_authorization_raw,
        issue_list=issue_list,
        issue_list_raw=issue_list_raw,
        patch=patch,
        patch_raw=patch_raw,
        base_raw=base_raw,
    )
    decisions = authorization_state["decisions"]
    for index, op in enumerate(patch.get("ops", [])):
        if op.get("claim_strength_changes"):
            failures.append(f"integrity patch op {index}: claim-strength changes are forbidden")
        if op.get("collateral_authorization_ids"):
            failures.append(f"integrity patch op {index}: collateral ids are forbidden")
        cited = op.get("roadmap_item_ids", [])
        if len(cited) != len(set(cited)):
            failures.append(f"integrity patch op {index}: duplicate correction ids")
        for correction_id in cited:
            decision = decisions.get(correction_id)
            if decision is None:
                failures.append(
                    f"integrity patch op {index}: correction id {correction_id} does not resolve"
                )
            elif decision["decision"] != "authorize":
                failures.append(
                    f"integrity patch op {index}: correction {correction_id} was stop_without_write"
                )
            elif op["op"] not in _target_map(decision["authorized_targets"]).get(
                op["block_id"], set()
            ):
                failures.append(
                    f"integrity patch op {index}: target/op exceeds correction {correction_id} scope"
                )
    if failures:
        raise ContractError(failures)
    return {
        "status": "pass",
        "authorization_kind": "explicit_author_exact_integrity_patch",
        "issue_list_sha256": bytes_hash(issue_list_raw),
        "integrity_authorization_sha256": bytes_hash(integrity_authorization_raw),
        "revision_patch_sha256": bytes_hash(patch_raw),
        "unregistered_claim_drift_review_required": True,
    }


def _validate_apply_report(
    report: dict,
    *,
    patch: dict,
    patch_raw: bytes,
    pre_raw: bytes,
    post_raw: bytes,
    witness: dict,
    label: str,
) -> list[str]:
    failures: list[str] = []
    expected = {
        "report_format_version": CURRENT_REPORT_VERSION,
        "mode": "patch",
        "base_draft_hash": base_draft_hash(pre_raw),
        "output_draft_hash": base_draft_hash(post_raw),
        "patch_digest": bytes_hash(patch_raw),
        "revision_round": patch["revision_round"],
        "authorization_witness": witness,
    }
    for field, value in expected.items():
        if report.get(field) != value:
            failures.append(f"{label}: {field} does not match replayed value")
    return failures


def _replay_patch_and_report(
    *,
    patch: dict,
    pre_raw: bytes,
    post_raw: bytes,
    report: dict,
    label: str,
) -> list[str]:
    """Re-run the deterministic patch engine and recompute report mechanics.

    Authorization replay alone proves that a patch was permitted; it does not
    prove that the declared post draft is what that patch produces. Bundle
    validation therefore runs the pure validate/apply functions in memory and
    compares both output bytes and every mechanically derived report field.
    """
    from scripts.ars_apply_revision_patch import (  # local: avoids import cycle
        ApplyRejection,
        apply_patch as apply_patch_bytes,
        validate_patch,
    )

    failures: list[str] = []
    structural = report.get("structural_flags")
    if not isinstance(structural, dict):
        return [f"{label}: structural_flags must be an object"]
    threshold = structural.get("touched_ratio_threshold")
    if threshold is not None and (
        isinstance(threshold, bool)
        or not isinstance(threshold, (int, float))
        or not math.isfinite(threshold)
        or not 0.0 <= threshold <= 1.0
    ):
        return [f"{label}: touched_ratio_threshold must be null or finite in [0, 1]"]
    acknowledged = structural.get("acknowledged")
    if not isinstance(acknowledged, bool):
        return [f"{label}: structural_flags.acknowledged must be boolean"]

    try:
        pre_text, parsed = _parse_base(pre_raw, f"{label} pre draft")
        analysis = validate_patch(
            patch,
            pre_raw,
            parsed,
            touched_ratio_threshold=threshold,
        )
        replayed_text, phase2 = apply_patch_bytes(pre_text, parsed, analysis)
    except ApplyRejection as exc:
        details = "; ".join(
            f"{row.get('kind')}: {row.get('message')}" for row in exc.failures
        )
        return [f"{label}: deterministic patch replay rejected ({details})"]
    except ContractError as exc:
        return [f"{label}: deterministic patch replay rejected ({'; '.join(exc.failures)})"]

    replayed_raw = replayed_text.encode("utf-8")
    if replayed_raw != post_raw:
        failures.append(f"{label}: deterministic patch output bytes do not equal post_round_draft")

    replayed_flags = copy.deepcopy(analysis["structural_flags"])
    replayed_flags["acknowledged"] = acknowledged
    if replayed_flags["any"] and not acknowledged:
        failures.append(
            f"{label}: structural patch could not have produced a report without acknowledgement"
        )
    counters_base = analysis["counters_base"]
    total = counters_base["blocks_total"]
    touched = counters_base["blocks_touched"]
    preserved = total - touched
    expected = {
        "authorization_context": patch["authorization_context"],
        "ops_applied": phase2["ops_applied"],
        "fresh_block_ids": phase2["fresh_block_ids"],
        "pure_move_pairs": phase2["pure_move_pairs"],
        "structural_flags": replayed_flags,
        "counters": {
            "blocks_total": total,
            "blocks_touched": touched,
            "blocks_preserved_byte_identical": preserved,
            "preserved_ratio": round(preserved / total, 4) if total else 0.0,
        },
    }
    for field, value in expected.items():
        if report.get(field) != value:
            failures.append(f"{label}: {field} does not match deterministic replay")
    return failures


def validate_bundle(bundle: dict, *, root: Path) -> None:
    failures = _schema_failures(bundle, BUNDLE_SCHEMA_PATH, "bundle")
    if failures:
        raise ContractError(failures)
    store = ArtifactStore(root)
    try:
        start_draft = store.read(bundle["chain_start"]["draft"], "chain_start.draft")
        start_manifest_artifact = store.read(
            bundle["chain_start"]["block_manifest"], "chain_start.block_manifest"
        )
        start_manifest = start_manifest_artifact.json("chain-start block manifest")
        validate_block_manifest(start_manifest, start_manifest_artifact.raw, start_draft.raw)
        receipt_artifact = store.read(
            bundle["chain_start"]["integrity_pass_receipt"],
            "chain_start.integrity_pass_receipt",
        )
        receipt = receipt_artifact.json("chain-start integrity PASS receipt")
        failures.extend(
            _schema_failures(receipt, INTEGRITY_RECEIPT_SCHEMA_PATH, "integrity PASS receipt")
        )
        if receipt.get("checked_draft_sha256") != bytes_hash(start_draft.raw):
            failures.append("chain-start integrity receipt is not bound to chain-start draft")
    except ContractError as exc:
        failures.extend(exc.failures)
        raise ContractError(failures)

    expected_round = bundle["chain_start"]["first_revision_round"]
    prior_post = start_draft
    for index, entry in enumerate(bundle["rounds"]):
        label = f"rounds[{index}]"
        try:
            if entry["revision_round"] != expected_round:
                raise ContractError(
                    [f"bundle {label}: revision rounds must be continuous from chain start"]
                )
            expected_round += 1
            pre = store.read(entry["pre_round_draft"], f"{label}.pre_round_draft")
            if bytes_hash(pre.raw) != bytes_hash(prior_post.raw):
                raise ContractError([f"bundle {label}: pre draft does not equal prior post draft"])
            manifest_artifact = store.read(
                entry["pre_round_block_manifest"], f"{label}.pre_round_block_manifest"
            )
            manifest = manifest_artifact.json(f"bundle {label} block manifest")
            validate_block_manifest(manifest, manifest_artifact.raw, pre.raw)
            post = store.read(entry["post_round_draft"], f"{label}.post_round_draft")

            if entry["kind"] in ("review_roadmap", "review_noop"):
                roadmap_artifact = store.read(
                    entry["revision_roadmap"], f"{label}.revision_roadmap"
                )
                roadmap = roadmap_artifact.json(f"bundle {label} roadmap")
                validate_roadmap(
                    roadmap,
                    roadmap_raw=roadmap_artifact.raw,
                    base_raw=pre.raw,
                    block_manifest=manifest,
                    block_manifest_raw=manifest_artifact.raw,
                )
                if roadmap["revision_round"] != entry["revision_round"]:
                    raise ContractError([f"bundle {label}: roadmap revision_round mismatch"])
                claim_artifact = store.read(
                    entry["claim_surface_manifest"], f"{label}.claim_surface_manifest"
                )
                claim_surface = claim_artifact.json(f"bundle {label} claim surface")
                surfaces = validate_claim_surface_manifest(
                    claim_surface,
                    claim_surface_raw=claim_artifact.raw,
                    roadmap=roadmap,
                    roadmap_raw=roadmap_artifact.raw,
                    base_raw=pre.raw,
                    artifact_store=store,
                )
                author_artifact = store.read(
                    entry["author_adjudication"], f"{label}.author_adjudication"
                )
                adjudication = author_artifact.json(f"bundle {label} author adjudication")
                author_state = validate_author_adjudication(
                    adjudication,
                    adjudication_raw=author_artifact.raw,
                    roadmap=roadmap,
                    roadmap_raw=roadmap_artifact.raw,
                    claim_surface=claim_surface,
                    claim_surface_raw=claim_artifact.raw,
                    base_raw=pre.raw,
                    surfaces_by_id=surfaces,
                )
                if entry["kind"] == "review_noop":
                    if any(
                        record["author_triage"] == "will_address"
                        for record in author_state["records"].values()
                    ):
                        raise ContractError(
                            [f"bundle {label}: review_noop requires zero will_address decisions"]
                        )
                    if pre.raw != post.raw:
                        raise ContractError(
                            [f"bundle {label}: review_noop pre/post draft bytes must be identical"]
                        )
                else:
                    patch_artifact = store.read(
                        entry["revision_patch"], f"{label}.revision_patch"
                    )
                    patch = patch_artifact.json(f"bundle {label} patch")
                    witness = validate_review_patch_authorization(
                        patch,
                        base_raw=pre.raw,
                        roadmap=roadmap,
                        roadmap_raw=roadmap_artifact.raw,
                        adjudication=adjudication,
                        adjudication_raw=author_artifact.raw,
                        claim_surface=claim_surface,
                        claim_surface_raw=claim_artifact.raw,
                        surfaces_by_id=surfaces,
                    )
                    report_artifact = store.read(
                        entry["apply_report"], f"{label}.apply_report"
                    )
                    report = report_artifact.json(f"bundle {label} apply report")
                    failures.extend(
                        _validate_apply_report(
                            report,
                            patch=patch,
                            patch_raw=patch_artifact.raw,
                            pre_raw=pre.raw,
                            post_raw=post.raw,
                            witness=witness,
                            label=f"bundle {label} apply report",
                        )
                    )
                    failures.extend(
                        _replay_patch_and_report(
                            patch=patch,
                            pre_raw=pre.raw,
                            post_raw=post.raw,
                            report=report,
                            label=f"bundle {label} apply replay",
                        )
                    )
            else:
                issue_artifact = store.read(entry["issue_list"], f"{label}.issue_list")
                issue_list = issue_artifact.json(f"bundle {label} integrity issue list")
                if issue_list.get("revision_round") != entry["revision_round"]:
                    raise ContractError(
                        [f"bundle {label}: integrity issue-list revision_round mismatch"]
                    )
                patch_artifact = store.read(entry["revision_patch"], f"{label}.revision_patch")
                patch = patch_artifact.json(f"bundle {label} patch")
                integrity_authorization_artifact = store.read(
                    entry["integrity_authorization"],
                    f"{label}.integrity_authorization",
                )
                integrity_authorization = integrity_authorization_artifact.json(
                    f"bundle {label} integrity authorization"
                )
                witness = validate_integrity_patch_authorization(
                    patch,
                    patch_raw=patch_artifact.raw,
                    base_raw=pre.raw,
                    issue_list=issue_list,
                    issue_list_raw=issue_artifact.raw,
                    integrity_authorization=integrity_authorization,
                    integrity_authorization_raw=integrity_authorization_artifact.raw,
                )
                report_artifact = store.read(entry["apply_report"], f"{label}.apply_report")
                report = report_artifact.json(f"bundle {label} apply report")
                failures.extend(
                    _validate_apply_report(
                        report,
                        patch=patch,
                        patch_raw=patch_artifact.raw,
                        pre_raw=pre.raw,
                        post_raw=post.raw,
                        witness=witness,
                        label=f"bundle {label} apply report",
                    )
                )
                failures.extend(
                    _replay_patch_and_report(
                        patch=patch,
                        pre_raw=pre.raw,
                        post_raw=post.raw,
                        report=report,
                        label=f"bundle {label} apply replay",
                    )
                )
            prior_post = post
        except ContractError as exc:
            failures.extend(exc.failures)
    try:
        final = store.read(bundle["final_draft"], "final_draft")
        if final.raw != prior_post.raw:
            failures.append("bundle final_draft does not equal last round post draft")
    except ContractError as exc:
        failures.extend(exc.failures)
    if failures:
        raise ContractError(failures)


_CONSEQUENCE_PHRASES = {
    "acceptance_criterion_unmet": "specified acceptance criterion remains unmet",
    "evidence_gap_remains": "identified evidence gap remains",
    "claim_scope_unsupported": "registered claim scope remains unsupported",
    "method_reproducibility_unresolved": "method reproducibility remains unresolved",
    "reporting_requirement_unmet": "specified reporting requirement remains unmet",
    "editorial_conformance_unmet": "editorial conformance requirement remains unmet",
    "interpretive_ambiguity_remains": "identified interpretive ambiguity remains",
    "reader_traceability_reduced": "reader traceability remains reduced",
}


def _md(value: Any) -> str:
    return str(value).replace("\r", " ").replace("\n", " ").replace("|", "\\|")


def _cost_label(value: dict) -> str:
    labels = {
        "sentence": "sentence",
        "section": "section",
        "re_analysis": "re-analysis",
        "new_data": "new data",
        "other": f"other ({value.get('surface_id', 'declared')})",
    }
    return f"{labels[value['kind']]} — {_md(value['locator'])}"


def _render_target_rows(targets: list[dict]) -> list[str]:
    return [
        "  - {block}: {operations}".format(
            block=_md(target["block_id"]),
            operations=", ".join(_md(op) for op in target["allowed_operations"]),
        )
        for target in targets
    ]


def render_markdown(
    roadmap: dict,
    adjudication: dict | None = None,
    *,
    adjudication_raw: bytes | None = None,
    roadmap_raw: bytes | None = None,
    claim_surface: dict | None = None,
    claim_surface_raw: bytes | None = None,
    base_raw: bytes | None = None,
    surfaces_by_id: dict[str, dict] | None = None,
) -> str:
    validate_roadmap(roadmap)
    records: dict[str, dict] = {}
    if adjudication is None:
        display = {"mode": "source_traceability", "item_ids": [item["id"] for item in roadmap["items"]]}
    else:
        required_inputs = {
            "adjudication_raw": adjudication_raw,
            "roadmap_raw": roadmap_raw,
            "claim_surface": claim_surface,
            "claim_surface_raw": claim_surface_raw,
            "base_raw": base_raw,
            "surfaces_by_id": surfaces_by_id,
        }
        missing = [name for name, value in required_inputs.items() if value is None]
        if missing:
            raise ContractError(
                [f"renderer: exact author-sidecar replay inputs required ({', '.join(missing)})"]
            )
        author_state = validate_author_adjudication(
            adjudication,
            adjudication_raw=adjudication_raw,
            roadmap=roadmap,
            roadmap_raw=roadmap_raw,
            claim_surface=claim_surface,
            claim_surface_raw=claim_surface_raw,
            base_raw=base_raw,
            surfaces_by_id=surfaces_by_id,
        )
        records = author_state["records"]
        display = adjudication["display_order"]
    by_id = {item["id"]: item for item in roadmap["items"]}
    lines = [
        "# Revision Roadmap",
        "",
        "> View order is presentation-only and changes no obligation or revision authority.",
        "",
        f"- Editorial decision: {_md(roadmap['editorial_decision'])}",
        f"- Revision round: {roadmap['revision_round']}",
        f"- View: {_md(display['mode'])}",
        "",
        "| Ref | Obligation class | Severity | Cost scope | Consequence if unaddressed | Author triage | Author reason |",
        "|---|---|---|---|---|---|---|",
    ]
    for item_id in display["item_ids"]:
        item = by_id[item_id]
        decision = records.get(item_id)
        triage = decision["author_triage"] if decision else "PENDING AUTHOR DECISION"
        reason = decision.get("author_reason", "—") if decision else "—"
        consequence = item["consequence_if_unaddressed"]
        target = consequence["target"]
        consequence_text = (
            f"{_CONSEQUENCE_PHRASES[consequence['code']]} at "
            f"{_md(target['kind'])} {_md(target['locator'])}"
        )
        lines.append(
            "| {ref} | {obligation} | {severity} | {cost} | {consequence} | {triage} | {reason} |".format(
                ref=_md(item_id),
                obligation=_md(item["obligation_class"]),
                severity=_md(item.get("severity", "not-applicable")),
                cost=_cost_label(item["cost_scope"]),
                consequence=consequence_text,
                triage=_md(triage),
                reason=_md(reason),
            )
        )
        lines.extend(
            [
                "",
                f"## {_md(item_id)} — {_md(item['description'])}",
                "",
                f"- Source reviewer(s): {_md(item['reviewer'])}",
                f"- Target section: {_md(item['target_section'])}",
                f"- Suggested action: {_md(item['suggested_action'])}",
                f"- Verification criteria: {_md(item['verification_criteria'])}",
                "- Proposed targets (proposal only; no write authority):",
            ]
        )
        lines.extend(_render_target_rows(item["proposed_targets"]))
        if decision is None:
            lines.append("- Exact authorized targets: PENDING AUTHOR DECISION — no write authority")
        elif decision["authorized_targets"]:
            lines.append("- Exact authorized targets:")
            lines.extend(_render_target_rows(decision["authorized_targets"]))
        else:
            lines.append("- Exact authorized targets: none — no write authority")
        if decision and decision["claim_strength_authorizations"]:
            lines.append("- Exact registered claim-surface authorizations:")
            for authorization in decision["claim_strength_authorizations"]:
                lines.append(
                    "  - {aid}: {manifest}/{claim}/{surface}, {before} → {after} ({direction})".format(
                        aid=_md(authorization["authorization_id"]),
                        manifest=_md(authorization["scoped_manifest_id"]),
                        claim=_md(authorization["claim_id"]),
                        surface=_md(authorization["surface_id"]),
                        before=_md(authorization["from_rung"]),
                        after=_md(authorization["to_rung"]),
                        direction=_md(authorization["direction"]),
                    )
                )
    return "\n".join(lines) + "\n"


def _standalone_store(root: Path) -> ArtifactStore:
    return ArtifactStore(root)


def _load_core_inputs(args: argparse.Namespace) -> tuple[dict, bytes, bytes, dict, bytes]:
    roadmap, roadmap_raw = load_json_path(args.roadmap, "roadmap")
    base_raw = _read_path_once(args.base, "base draft")
    block_manifest, block_raw = load_json_path(args.block_manifest, "block manifest")
    validate_roadmap(
        roadmap,
        roadmap_raw=roadmap_raw,
        base_raw=base_raw,
        block_manifest=block_manifest,
        block_manifest_raw=block_raw,
    )
    return roadmap, roadmap_raw, base_raw, block_manifest, block_raw


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    core_parent = argparse.ArgumentParser(add_help=False)
    core_parent.add_argument("roadmap", type=Path)
    core_parent.add_argument("--base", type=Path, required=True)
    core_parent.add_argument("--block-manifest", type=Path, required=True)

    sub.add_parser("validate-roadmap", parents=[core_parent])

    p_build = sub.add_parser("build-adjudication", parents=[core_parent])
    p_build.add_argument("--claim-surface", type=Path, required=True)
    p_build.add_argument("--author-choices", type=Path, required=True)
    p_build.add_argument("--artifact-root", type=Path, required=True)
    p_build.add_argument("--output", type=Path, required=True)

    p_author = sub.add_parser("validate-adjudication", parents=[core_parent])
    p_author.add_argument("adjudication", type=Path)
    p_author.add_argument("--claim-surface", type=Path, required=True)
    p_author.add_argument("--artifact-root", type=Path, required=True)

    p_render = sub.add_parser("render", parents=[core_parent])
    p_render.add_argument("--adjudication", type=Path)
    p_render.add_argument("--claim-surface", type=Path, required=True)
    p_render.add_argument("--artifact-root", type=Path, required=True)

    integrity_parent = argparse.ArgumentParser(add_help=False)
    integrity_parent.add_argument("issue_list", type=Path)
    integrity_parent.add_argument("--base", type=Path, required=True)
    integrity_parent.add_argument("--patch", type=Path, required=True)

    p_integrity_build = sub.add_parser(
        "build-integrity-authorization", parents=[integrity_parent]
    )
    p_integrity_build.add_argument("--author-choices", type=Path, required=True)
    p_integrity_build.add_argument("--output", type=Path, required=True)

    p_integrity_validate = sub.add_parser(
        "validate-integrity-authorization", parents=[integrity_parent]
    )
    p_integrity_validate.add_argument("authorization", type=Path)

    p_bundle = sub.add_parser("validate-bundle")
    p_bundle.add_argument("bundle", type=Path)
    p_bundle.add_argument("--root", type=Path)

    args = parser.parse_args(argv)
    try:
        if args.command in (
            "build-integrity-authorization",
            "validate-integrity-authorization",
        ):
            base_raw = _read_path_once(args.base, "base draft")
            issue_list, issue_list_raw = load_json_path(
                args.issue_list, "integrity correction list"
            )
            patch, patch_raw = load_json_path(args.patch, "integrity patch")
            if args.command == "build-integrity-authorization":
                if args.output.exists():
                    raise ContractError(
                        ["build-integrity-authorization output already exists"]
                    )
                choices, _choices_raw = load_json_path(
                    args.author_choices,
                    "integrity correction authorization input",
                )
                authorization = build_integrity_authorization(
                    choices,
                    issue_list=issue_list,
                    issue_list_raw=issue_list_raw,
                    patch=patch,
                    patch_raw=patch_raw,
                    base_raw=base_raw,
                )
                atomic_write_bytes(
                    args.output, canonical_bytes(authorization) + b"\n"
                )
                print(f"integrity correction authorization built: {args.output}")
            else:
                authorization, authorization_raw = load_json_path(
                    args.authorization, "integrity correction authorization"
                )
                validate_integrity_authorization(
                    authorization,
                    authorization_raw=authorization_raw,
                    issue_list=issue_list,
                    issue_list_raw=issue_list_raw,
                    patch=patch,
                    patch_raw=patch_raw,
                    base_raw=base_raw,
                )
                print("integrity correction authorization ok")
            return 0
        if args.command == "validate-bundle":
            bundle, _raw = load_json_path(args.bundle, "bundle")
            validate_bundle(bundle, root=args.root or args.bundle.parent)
            print("revision evidence bundle ok")
            return 0

        roadmap, roadmap_raw, base_raw, _manifest, _manifest_raw = _load_core_inputs(args)
        if args.command == "validate-roadmap":
            print("revision roadmap ok")
        else:
            claim_surface, claim_raw = load_json_path(args.claim_surface, "claim surface manifest")
            store = _standalone_store(args.artifact_root)
            surfaces = validate_claim_surface_manifest(
                claim_surface,
                claim_surface_raw=claim_raw,
                roadmap=roadmap,
                roadmap_raw=roadmap_raw,
                base_raw=base_raw,
                artifact_store=store,
            )
            if args.command == "render":
                author = None
                author_raw = None
                if args.adjudication is not None:
                    author, author_raw = load_json_path(
                        args.adjudication, "author adjudication"
                    )
                sys.stdout.write(
                    render_markdown(
                        roadmap,
                        author,
                        adjudication_raw=author_raw,
                        roadmap_raw=roadmap_raw,
                        claim_surface=claim_surface,
                        claim_surface_raw=claim_raw,
                        base_raw=base_raw,
                        surfaces_by_id=surfaces,
                    )
                )
            elif args.command == "build-adjudication":
                if args.output.exists():
                    raise ContractError(["build-adjudication output already exists"])
                choices, _choices_raw = load_json_path(args.author_choices, "author choice input")
                adjudication = build_author_adjudication(
                    choices,
                    roadmap=roadmap,
                    roadmap_raw=roadmap_raw,
                    claim_surface=claim_surface,
                    claim_surface_raw=claim_raw,
                    base_raw=base_raw,
                    surfaces_by_id=surfaces,
                )
                atomic_write_bytes(args.output, canonical_bytes(adjudication) + b"\n")
                print(f"author adjudication built: {args.output}")
            else:
                author, author_raw = load_json_path(args.adjudication, "author adjudication")
                validate_author_adjudication(
                    author,
                    adjudication_raw=author_raw,
                    roadmap=roadmap,
                    roadmap_raw=roadmap_raw,
                    claim_surface=claim_surface,
                    claim_surface_raw=claim_raw,
                    base_raw=base_raw,
                    surfaces_by_id=surfaces,
                )
                print("author adjudication ok")
    except ContractError as exc:
        print("revision authority contract invalid", file=sys.stderr)
        for failure in exc.failures:
            print(f"  - {failure}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
