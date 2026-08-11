#!/usr/bin/env python3
"""Deterministic, advisory-only cross-run adjudication activity recorder.

The runtime intentionally has no default paths, clock, network, model, judge,
directory scan, or environment-variable inputs.  All authority comes from an
explicit terminal state, its sealed five-family inventory, and hash-bound
artifacts beneath an explicit artifact root.
"""

from __future__ import annotations

import argparse
import copy
import errno
import fcntl
import hashlib
import json
import os
import re
import stat
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path, PurePosixPath
from typing import Any, Iterator, Sequence

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource


REPO_ROOT = Path(__file__).resolve().parents[1]
INPUT_SCHEMA_PATH = REPO_ROOT / "shared/contracts/activity/adjudication_activity_input.schema.json"
STORE_SCHEMA_PATH = REPO_ROOT / "shared/contracts/activity/adjudication_activity_store.schema.json"
COMPLIANCE_SCHEMA_PATH = REPO_ROOT / "shared/compliance_report.schema.json"
REVISION_CONTRACTS = REPO_ROOT / "shared/contracts/revision"
REREVIEW_CONTRACTS = REPO_ROOT / "shared/contracts/re_review"

INPUT_VERSION = "adjudication-activity-input/1.0"
STORE_VERSION = "adjudication-activity-store/1.0"
SOURCE_FAMILIES = (
    "revision_author_adjudication",
    "compliance_report",
    "re_review_traceability",
    "explicit_user_request",
    "mandatory_checkpoint_response",
)
STAGES = (
    "pipeline_stage_1", "pipeline_stage_2", "pipeline_stage_2_5",
    "pipeline_stage_3", "pipeline_stage_3_prime", "pipeline_stage_4",
    "pipeline_stage_4_prime", "pipeline_stage_4_5", "pipeline_stage_5",
    "pipeline_stage_6",
)
RAW_TO_STAGE = {
    "1": STAGES[0], "2": STAGES[1], "2.5": STAGES[2], "3": STAGES[3],
    "3p": STAGES[4], "4": STAGES[5], "4p": STAGES[6], "4.5": STAGES[7],
    "5": STAGES[8], "6": STAGES[9],
}
STAGE_TO_RAW = {value: key for key, value in RAW_TO_STAGE.items()}
STATUS_VALUES = {"pending", "in_progress", "completed", "skipped", "blocked"}
REASON_UNAVAILABLE = {
    "source_not_provided", "source_unreadable", "source_invalid",
    "capture_not_supported",
}
ROLE_ORDER = {
    "revision_author_adjudication": ("author_adjudication_input", "author_adjudication"),
    "compliance_report": ("compliance_report", "compliance_override_action_receipt"),
    "re_review_traceability": ("input_manifest", "precommitment", "verdict_record", "traceability"),
    "explicit_user_request": ("explicit_user_request_log",),
    "mandatory_checkpoint_response": ("mandatory_checkpoint_response_log",),
}
OVERTURN_TYPES = {
    "author_triage_not_on_point", "compliance_block_override",
    "re_review_verdict_changed",
}
MAX_INPUT = 1 << 20
MAX_ARTIFACT = 8 << 20
MAX_ARTIFACT_TOTAL = 64 << 20
MAX_STORE = 16 << 20
MAX_EVENTS_RUN = 4096
MAX_EVENTS_STORE = 100000
MAX_RUNS = 10000
LIMITATION = "This records explicit adjudication activity only. It cannot determine correctness, attentiveness, engagement, or whether human ownership is real; genuine agreement and non-review can produce the same history."
ADVISORY = "This series is advisory only; it never gates, blocks, scores, or changes any verdict."
COVERAGE = "Coverage: only successfully retained records in this explicitly selected store are shown; runs without this store selection or whose append failed are not represented."
DATA_MINIMIZATION = {
    "raw_prose_embedded": False,
    "user_identity_embedded": False,
    "absolute_paths_embedded": False,
}
HEX_RE = re.compile(r"^[0-9a-f]{64}$")
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
GROUP_RE = re.compile(r"^SOURCE-GROUP-[A-Za-z0-9][A-Za-z0-9._-]{0,95}$")


class ActivityError(Exception):
    """Bounded public failure with a closed CLI error code."""

    def __init__(self, code: str, detail: str):
        super().__init__(detail)
        self.code = code
        self.detail = detail[:500]


EXIT_BY_CODE = {
    "USAGE": 2, "PATH": 3, "INPUT": 3, "SOURCE": 3, "STORE": 4,
    "CONFLICT": 5, "CAP": 5, "DELETE_CONFIRMATION": 6,
    "LOCK": 7, "WRITE": 7,
}


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate object key")
        result[key] = value
    return result


def _reject_number(token: str) -> None:
    raise ValueError(f"forbidden JSON number {token}")


def strict_json(raw: bytes, *, code: str) -> Any:
    if raw.startswith(b"\xef\xbb\xbf"):
        raise ActivityError(code, "UTF-8 BOM is forbidden")
    try:
        value = json.loads(
            raw.decode("utf-8"), object_pairs_hook=_pairs,
            parse_float=_reject_number, parse_constant=_reject_number,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise ActivityError(code, f"invalid strict JSON: {exc.__class__.__name__}") from None
    _canonical_domain(value, code=code)
    return value


def _canonical_domain(value: Any, *, code: str, depth: int = 0) -> None:
    if depth > 256:
        raise ActivityError(code, "JSON nesting exceeds contract bound")
    if isinstance(value, str):
        if any(0xD800 <= ord(char) <= 0xDFFF for char in value):
            raise ActivityError(code, "lone UTF-16 surrogate is forbidden")
        return
    if value is None or isinstance(value, bool):
        return
    if isinstance(value, int) and not isinstance(value, bool):
        return
    if isinstance(value, list):
        for child in value:
            _canonical_domain(child, code=code, depth=depth + 1)
        return
    if isinstance(value, dict):
        for key, child in value.items():
            if not isinstance(key, str) or not key.isascii():
                raise ActivityError(code, "contract object keys must be ASCII")
            _canonical_domain(child, code=code, depth=depth + 1)
        return
    raise ActivityError(code, "floats and non-contract JSON values are forbidden")


def canonical_bytes(value: Any, *, code: str = "INPUT") -> bytes:
    _canonical_domain(value, code=code)
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _digest(domain: bytes, value: Any) -> str:
    return hashlib.sha256(domain + canonical_bytes(value)).hexdigest()


def interaction_sha256(run_id: str, interaction_id: str) -> str:
    return _digest(
        b"ars.adjudication-activity.interaction/1.0\0",
        {"run_id": run_id, "interaction_id": interaction_id},
    )


def _load_schema(path: Path) -> dict[str, Any]:
    value = strict_json(path.read_bytes(), code="SOURCE")
    if not isinstance(value, dict):
        raise ActivityError("SOURCE", "schema root is not an object")
    return value


def _validator(path: Path, *, revision_registry: bool = False) -> Draft202012Validator:
    schema = _load_schema(path)
    registry = Registry()
    if revision_registry:
        for candidate_path in (
            REVISION_CONTRACTS / "author_adjudication.schema.json",
            REVISION_CONTRACTS / "author_adjudication_input.schema.json",
        ):
            candidate = _load_schema(candidate_path)
            if "$id" in candidate:
                registry = registry.with_resource(candidate["$id"], Resource.from_contents(candidate))
    return Draft202012Validator(schema, registry=registry, format_checker=FormatChecker())


def _schema_validate(value: Any, path: Path, *, code: str, revision_registry: bool = False) -> None:
    errors = sorted(
        _validator(path, revision_registry=revision_registry).iter_errors(value),
        key=lambda error: tuple(str(part) for part in error.absolute_path),
    )
    if errors:
        raise ActivityError(code, f"schema validation failed at {list(errors[0].absolute_path)!r}")


def _read_limited_identity(path: Path, limit: int, *, code: str) -> tuple[bytes, tuple[int, int, int]]:
    try:
        fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        try:
            info = os.fstat(fd)
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                raise ActivityError("PATH", "selected path is not a single-linked regular file")
            identity = (info.st_dev, info.st_ino, info.st_size)
            if info.st_size > limit:
                raise ActivityError("CAP", "file exceeds hard byte cap")
            chunks: list[bytes] = []
            size = 0
            while True:
                chunk = os.read(fd, min(1024 * 1024, limit + 1 - size))
                if not chunk:
                    break
                chunks.append(chunk)
                size += len(chunk)
                if size > limit:
                    raise ActivityError("CAP", "file exceeds hard byte cap")
            after = os.fstat(fd)
            if (after.st_dev, after.st_ino, after.st_size) != identity or size != info.st_size:
                raise ActivityError(code, "file changed while being read")
            return b"".join(chunks), identity
        finally:
            os.close(fd)
    except ActivityError:
        raise
    except OSError as exc:
        raise ActivityError(code, f"file read failed: {exc.__class__.__name__}") from None


def _read_limited(path: Path, limit: int, *, code: str) -> bytes:
    return _read_limited_identity(path, limit, code=code)[0]


def _path_identity(path: Path) -> tuple[int, int, int]:
    try:
        info = path.lstat()
    except OSError as exc:
        raise ActivityError("WRITE", f"target identity check failed: {exc.__class__.__name__}") from None
    return info.st_dev, info.st_ino, info.st_size


def _assert_identity(path: Path, expected: tuple[int, int, int]) -> None:
    if _path_identity(path) != expected:
        raise ActivityError("CONFLICT", "target changed after validated read")


def _relative_binding(root: Path, path: Path) -> str:
    try:
        root_real = root.resolve(strict=True)
        path_real = path.resolve(strict=True)
        relative = path_real.relative_to(root_real).as_posix()
    except (OSError, ValueError):
        raise ActivityError("PATH", "path is not contained beneath artifact root") from None
    _safe_relative(root, relative)
    return relative


def _safe_relative(root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative or len(relative) > 512:
        raise ActivityError("PATH", "invalid relative artifact path")
    pure = PurePosixPath(relative)
    if pure.is_absolute() or "\\" in relative or relative.endswith("/"):
        raise ActivityError("PATH", "unsafe relative artifact path")
    if re.match(r"^[A-Za-z]:/", relative) or any(part in {"", ".", ".."} for part in pure.parts):
        raise ActivityError("PATH", "unsafe relative artifact path")
    if any(ord(char) < 32 or ord(char) == 127 for char in relative):
        raise ActivityError("PATH", "unsafe relative artifact path")
    try:
        root_info = root.lstat()
        if stat.S_ISLNK(root_info.st_mode) or not stat.S_ISDIR(root_info.st_mode):
            raise ActivityError("PATH", "artifact root must be a non-symlink directory")
        cursor = root
        for part in pure.parts:
            cursor = cursor / part
            info = cursor.lstat()
            if stat.S_ISLNK(info.st_mode):
                raise ActivityError("PATH", "symlink artifact path is forbidden")
        resolved = cursor.resolve(strict=True)
        resolved.relative_to(root.resolve(strict=True))
        if not stat.S_ISREG(cursor.stat().st_mode):
            raise ActivityError("PATH", "artifact must be a regular file")
        return cursor
    except ActivityError:
        raise
    except (OSError, ValueError):
        raise ActivityError("PATH", "artifact path cannot be safely resolved") from None


def _read_artifact_relative(root: Path, relative: str, limit: int) -> bytes:
    """Descriptor-relative no-follow traversal prevents parent-component swaps."""
    if not isinstance(relative, str) or not relative or len(relative) > 512:
        raise ActivityError("PATH", "invalid relative artifact path")
    pure = PurePosixPath(relative)
    if (
        pure.is_absolute() or "\\" in relative or relative.endswith("/")
        or re.match(r"^[A-Za-z]:/", relative)
        or any(part in {"", ".", ".."} for part in pure.parts)
        or any(ord(char) < 32 or ord(char) == 127 for char in relative)
    ):
        raise ActivityError("PATH", "unsafe relative artifact path")
    directory_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    opened: list[int] = []
    try:
        directory_fd = os.open(root, directory_flags)
        opened.append(directory_fd)
        for part in pure.parts[:-1]:
            directory_fd = os.open(part, directory_flags, dir_fd=directory_fd)
            opened.append(directory_fd)
        fd = os.open(
            pure.parts[-1], os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
            dir_fd=directory_fd,
        )
        opened.append(fd)
        info = os.fstat(fd)
        identity = (info.st_dev, info.st_ino, info.st_size)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise ActivityError("PATH", "artifact must be a single-linked regular file")
        if info.st_size > limit:
            raise ActivityError("CAP", "artifact exceeds hard byte cap")
        chunks: list[bytes] = []
        size = 0
        while True:
            chunk = os.read(fd, min(1024 * 1024, limit + 1 - size))
            if not chunk:
                break
            chunks.append(chunk)
            size += len(chunk)
            if size > limit:
                raise ActivityError("CAP", "artifact exceeds hard byte cap")
        after = os.fstat(fd)
        if (after.st_dev, after.st_ino, after.st_size) != identity or size != info.st_size:
            raise ActivityError("SOURCE", "artifact changed while being read")
        return b"".join(chunks)
    except ActivityError:
        raise
    except OSError as exc:
        if exc.errno == errno.ELOOP:
            raise ActivityError("PATH", "symlink artifact path is forbidden") from None
        raise ActivityError("PATH", f"artifact traversal failed: {exc.__class__.__name__}") from None
    finally:
        for opened_fd in reversed(opened):
            os.close(opened_fd)


@contextmanager
def _store_lock(path: Path, *, exclusive: bool) -> Iterator[None]:
    lock_path = path.with_name(path.name + ".lock")
    try:
        fd = os.open(lock_path, os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0), 0o600)
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size != 0:
            raise ActivityError("LOCK", "lock metadata is not an empty single-linked regular file")
        operation = (fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH) | fcntl.LOCK_NB
        fcntl.flock(fd, operation)
    except ActivityError:
        if "fd" in locals():
            os.close(fd)
        raise
    except OSError as exc:
        if "fd" in locals():
            os.close(fd)
        raise ActivityError("LOCK", f"lock acquisition failed: {exc.__class__.__name__}") from None
    try:
        yield
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


def _write_all(fd: int, raw: bytes) -> None:
    view = memoryview(raw)
    while view:
        written = os.write(fd, view)
        if written <= 0:
            raise OSError("write made no progress")
        view = view[written:]


def _atomic_replace(path: Path, raw: bytes, *, expected_identity: tuple[int, int, int] | None = None) -> None:
    path.parent.mkdir(parents=False, exist_ok=True)
    temporary: str | None = None
    try:
        fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
        try:
            os.fchmod(fd, 0o600)
            _write_all(fd, raw)
            os.fsync(fd)
        finally:
            os.close(fd)
        if os.stat(temporary).st_size != len(raw):
            raise OSError("temporary file size mismatch")
        if expected_identity is not None:
            _assert_identity(path, expected_identity)
        os.replace(temporary, path)
        temporary = None
        directory_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    except OSError as exc:
        raise ActivityError("WRITE", f"atomic write failed: {exc.__class__.__name__}") from None
    finally:
        if temporary is not None:
            try:
                os.unlink(temporary)
            except OSError:
                pass


def _atomic_create(path: Path, raw: bytes) -> None:
    if path.exists() or path.is_symlink():
        raise ActivityError("CONFLICT", "output path already exists")
    temporary: str | None = None
    try:
        fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
        try:
            os.fchmod(fd, 0o600)
            _write_all(fd, raw)
            os.fsync(fd)
        finally:
            os.close(fd)
        if os.stat(temporary).st_size != len(raw):
            raise OSError("temporary file size mismatch")
        os.link(temporary, path)
        os.unlink(temporary)
        temporary = None
        directory_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    except FileExistsError:
        raise ActivityError("CONFLICT", "output path already exists") from None
    except OSError as exc:
        raise ActivityError("WRITE", f"atomic create failed: {exc.__class__.__name__}") from None
    finally:
        if temporary:
            try:
                os.unlink(temporary)
            except OSError:
                pass


def _state_replay(state: dict[str, Any]) -> tuple[str, str, str, str]:
    if not isinstance(state, dict) or not ID_RE.fullmatch(str(state.get("run_id", ""))):
        raise ActivityError("INPUT", "terminal state lacks a valid stable run_id")
    pipeline_state = state.get("pipeline_state")
    if pipeline_state not in {"completed", "aborted"}:
        raise ActivityError("INPUT", "pipeline state is not eligible terminal state")
    raw_stage = str(state.get("current_stage", ""))
    stage = RAW_TO_STAGE.get(raw_stage)
    stages = state.get("stages")
    if stage is None or not isinstance(stages, dict) or not isinstance(stages.get(raw_stage), dict):
        raise ActivityError("INPUT", "current stage cannot be strictly replayed")
    status = stages[raw_stage].get("status")
    if status not in STATUS_VALUES:
        raise ActivityError("INPUT", "current stage status is outside the closed vocabulary")
    if pipeline_state == "completed" and not (raw_stage == "6" and status in {"completed", "skipped"}):
        raise ActivityError("INPUT", "completed state must replay Stage 6 completed or skipped")
    return state["run_id"], pipeline_state, stage, status


def _terminal_receipt(state: dict[str, Any], state_raw: bytes, relative_path: str) -> dict[str, Any]:
    run_id, pipeline_state, stage, status = _state_replay(state)
    return {
        "artifact_id": "pipeline-state-terminal-receipt",
        "relative_path": relative_path,
        "sha256": hashlib.sha256(state_raw).hexdigest(),
        "run_id": run_id,
        "pipeline_state": pipeline_state,
        "current_stage": stage,
        "current_stage_status": status,
    }


def _validate_source_rows(rows: Any, *, pending: bool = False) -> None:
    if not isinstance(rows, list) or len(rows) != 5:
        raise ActivityError("SOURCE", "source inventory must contain exactly five rows")
    for index, (row, family) in enumerate(zip(rows, SOURCE_FAMILIES)):
        if not isinstance(row, dict) or row.get("source_family") != family:
            raise ActivityError("SOURCE", f"source family order mismatch at row {index}")
        if set(row) != {"source_family", "capture_state", "reason_code", "artifacts"}:
            raise ActivityError("SOURCE", "source row has unknown or missing fields")
        state = row.get("capture_state")
        reason = row.get("reason_code")
        artifacts = row.get("artifacts")
        if not isinstance(artifacts, list) or len(artifacts) > 64:
            raise ActivityError("SOURCE", "invalid source artifact list")
        if state == "captured":
            if reason is not None or not artifacts:
                raise ActivityError("SOURCE", "captured source requires artifacts and null reason")
        elif state == "not_applicable":
            if reason != "not_applicable_for_run" or artifacts:
                raise ActivityError("SOURCE", "not-applicable source shape is invalid")
        elif state == "unavailable":
            if reason not in REASON_UNAVAILABLE or artifacts:
                raise ActivityError("SOURCE", "unavailable source shape is invalid")
        else:
            raise ActivityError("SOURCE", "unknown capture state")
        for artifact in artifacts:
            expected = {
                "artifact_id", "artifact_role", "artifact_group_id",
                "artifact_group_stage", "relative_path",
            }
            if not pending:
                expected.add("sha256")
            if not isinstance(artifact, dict) or set(artifact) != expected:
                raise ActivityError("SOURCE", "artifact binding has unknown or missing fields")
            if not isinstance(artifact.get("artifact_id"), str) or not ID_RE.fullmatch(artifact["artifact_id"]):
                raise ActivityError("SOURCE", "artifact id is outside the closed identifier grammar")
            if artifact.get("artifact_role") not in ROLE_ORDER[family]:
                raise ActivityError("SOURCE", "artifact role is outside the source-family vocabulary")
            if not isinstance(artifact.get("artifact_group_id"), str) or not GROUP_RE.fullmatch(artifact["artifact_group_id"]):
                raise ActivityError("SOURCE", "artifact group id is invalid")
            group_stage = artifact.get("artifact_group_stage")
            if family == SOURCE_FAMILIES[0]:
                if group_stage not in {"pipeline_stage_3", "pipeline_stage_3_prime"}:
                    raise ActivityError("SOURCE", "author artifact group stage is invalid")
            elif group_stage is not None:
                raise ActivityError("SOURCE", "non-author artifact group stage must be null")
            relative_path = artifact.get("relative_path")
            if not isinstance(relative_path, str):
                raise ActivityError("SOURCE", "artifact relative path must be a string")
            if not pending and (not isinstance(artifact.get("sha256"), str) or not HEX_RE.fullmatch(artifact["sha256"])):
                raise ActivityError("SOURCE", "artifact hash is invalid")


def _group_artifacts(row: dict[str, Any]) -> list[list[dict[str, Any]]]:
    family = row["source_family"]
    artifacts = row["artifacts"]
    groups: list[list[dict[str, Any]]] = []
    seen_ids: set[str] = set()
    cursor = 0
    while cursor < len(artifacts):
        group_id = artifacts[cursor].get("artifact_group_id")
        if not isinstance(group_id, str) or not GROUP_RE.fullmatch(group_id) or group_id in seen_ids:
            raise ActivityError("SOURCE", "invalid or repeated artifact group id")
        seen_ids.add(group_id)
        group: list[dict[str, Any]] = []
        while cursor < len(artifacts) and artifacts[cursor].get("artifact_group_id") == group_id:
            group.append(artifacts[cursor])
            cursor += 1
        groups.append(group)
    if row["capture_state"] != "captured":
        return groups
    expected_roles = ROLE_ORDER[family]
    if family == "revision_author_adjudication":
        if len(groups) not in {1, 2}:
            raise ActivityError("SOURCE", "author family requires one or two groups")
        expected_stages = ["pipeline_stage_3", "pipeline_stage_3_prime"] if len(groups) == 2 else None
        for index, group in enumerate(groups):
            if tuple(item.get("artifact_role") for item in group) != expected_roles:
                raise ActivityError("SOURCE", "author group role order is invalid")
            stages = {item.get("artifact_group_stage") for item in group}
            if len(stages) != 1 or next(iter(stages)) not in {"pipeline_stage_3", "pipeline_stage_3_prime"}:
                raise ActivityError("SOURCE", "author group stage is invalid")
            if expected_stages and next(iter(stages)) != expected_stages[index]:
                raise ActivityError("SOURCE", "author group stage order is invalid")
    elif family == "compliance_report":
        if not 1 <= len(groups) <= 16:
            raise ActivityError("SOURCE", "compliance family requires 1..16 groups")
        for group in groups:
            roles = tuple(item.get("artifact_role") for item in group)
            if roles not in {(expected_roles[0],), expected_roles}:
                raise ActivityError("SOURCE", "compliance group role set/order is invalid")
            if any(item.get("artifact_group_stage") is not None for item in group):
                raise ActivityError("SOURCE", "non-author artifact stage must be null")
    else:
        if len(groups) != 1 or tuple(item.get("artifact_role") for item in groups[0]) != expected_roles:
            raise ActivityError("SOURCE", "captured family has invalid exact group roles")
        if any(item.get("artifact_group_stage") is not None for item in groups[0]):
            raise ActivityError("SOURCE", "non-author artifact stage must be null")
    return groups


def seal_terminal_inventory(state_path: str | Path, artifact_root: str | Path, pending_bindings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Post-terminal best-effort helper: hash explicit pending rows and seal them.

    ``pending_bindings`` is authority supplied by the state tracker's sole
    writer.  It contains no hashes.  This helper performs no discovery.
    """
    state_file = Path(state_path)
    root = Path(artifact_root)
    _validate_source_rows(pending_bindings, pending=True)
    with _store_lock(state_file, exclusive=True):
        state_raw, state_identity = _read_limited_identity(state_file, MAX_STORE, code="INPUT")
        state = strict_json(state_raw, code="INPUT")
        _state_replay(state)
        sealed_rows = copy.deepcopy(pending_bindings)
        total = 0
        for row in sealed_rows:
            _group_artifacts(row)
            for artifact in row["artifacts"]:
                raw = _read_artifact_relative(root, artifact["relative_path"], MAX_ARTIFACT)
                total += len(raw)
                if total > MAX_ARTIFACT_TOTAL:
                    raise ActivityError("CAP", "referenced artifacts exceed per-run byte cap")
                artifact["sha256"] = hashlib.sha256(raw).hexdigest()
        _validate_source_rows(sealed_rows)
        candidate = copy.deepcopy(state)
        existing = candidate.get("adjudication_activity_sources")
        if existing is not None and existing != sealed_rows:
            raise ActivityError("CONFLICT", "terminal source inventory is already sealed differently")
        if existing == sealed_rows:
            return sealed_rows
        candidate["adjudication_activity_sources"] = sealed_rows
        _atomic_replace(
            state_file, canonical_bytes(candidate) + b"\n",
            expected_identity=state_identity,
        )
    return sealed_rows


def author_source_record(adjudication: dict[str, Any], event: dict[str, Any], digest: str) -> dict[str, Any]:
    return {
        "item_id": adjudication["item_id"],
        "author_event_id": adjudication["author_event_id"],
        "author_triage": adjudication["author_triage"],
        "input_sha256": event["input_sha256"],
        "interaction_sha256": digest,
    }


def compliance_source_record(
    group_id: str, stage: str, blockers: list[str], report_hash: str,
    receipt_hash: str, receipt: dict[str, Any],
) -> dict[str, Any]:
    return {
        "artifact_group_id": group_id,
        "stage": stage,
        "blocking_contributor_ids": blockers,
        "report_sha256": report_hash,
        "action_receipt_sha256": receipt_hash,
        "interaction_id": receipt["interaction_id"],
        "interaction_sha256": receipt["interaction_sha256"],
    }


def re_review_source_record(
    round_id: str, dissent_id: str, item_id: str, reapplication_id: str,
    adjustment: dict[str, Any], traceability_hash: str,
) -> dict[str, Any]:
    return {
        "round_id": round_id,
        "dissent_id": dissent_id,
        "item_id": item_id,
        "reapplication_id": reapplication_id,
        "adjustment_id": adjustment["adjustment_id"],
        "from_verdict": adjustment["from_verdict"],
        "to_verdict": adjustment["to_verdict"],
        "traceability_sha256": traceability_hash,
    }


def explicit_source_record(record: dict[str, Any]) -> dict[str, Any]:
    return {key: record[key] for key in (
        "request_id", "actor_role", "source", "action", "stage", "finding_id",
        "interaction_id", "interaction_sha256",
    )}


def mandatory_source_record(record: dict[str, Any]) -> dict[str, Any]:
    return {key: record[key] for key in (
        "response_id", "checkpoint_id", "checkpoint_type", "actor_role", "source",
        "stage", "disposition", "interaction_id", "interaction_sha256",
    )}


def _event(
    run_id: str, family: str, event_type: str, stage: str, disposition: str,
    interaction: str | None, source_record: dict[str, Any],
) -> dict[str, Any]:
    source_hash = _digest(
        b"ars.adjudication-activity.source-event/1.0\0",
        {"source_family": family, "source_record": source_record},
    )
    payload = {
        "run_id": run_id, "source_family": family, "event_type": event_type,
        "stage": stage, "disposition": disposition,
        "interaction_sha256": interaction, "source_event_sha256": source_hash,
    }
    return {
        "event_id": "ACTIVITY-EVENT-" + _digest(b"ars.adjudication-activity.event-id/1.0\0", payload),
        "event_type": event_type, "stage": stage, "disposition": disposition,
        "interaction_sha256": interaction, "source_event_sha256": source_hash,
    }


def _load_artifact(root: Path, binding: dict[str, Any], total: list[int]) -> tuple[dict[str, Any], bytes]:
    raw = _read_artifact_relative(root, binding["relative_path"], MAX_ARTIFACT)
    total[0] += len(raw)
    if total[0] > MAX_ARTIFACT_TOTAL:
        raise ActivityError("CAP", "referenced artifacts exceed per-run byte cap")
    if hashlib.sha256(raw).hexdigest() != binding["sha256"]:
        raise ActivityError("SOURCE", "artifact raw-byte hash mismatch")
    value = strict_json(raw, code="SOURCE")
    if not isinstance(value, dict):
        raise ActivityError("SOURCE", "source artifact root must be an object")
    return value, raw


def _author_events(run_id: str, stage: str, group: list[dict[str, Any]], root: Path, total: list[int]) -> list[dict[str, Any]]:
    input_value, _ = _load_artifact(root, group[0], total)
    output_value, _ = _load_artifact(root, group[1], total)
    _schema_validate(input_value, REVISION_CONTRACTS / "author_adjudication_input.schema.json", code="SOURCE", revision_registry=True)
    _schema_validate(output_value, REVISION_CONTRACTS / "author_adjudication.schema.json", code="SOURCE", revision_registry=True)
    projection_keys = ("author_events", "author_adjudications", "display_order", "collateral_authorizations")
    if any(input_value[key] != output_value[key] for key in projection_keys):
        raise ActivityError("SOURCE", "author input/output projection mismatch")
    event_by_id: dict[str, dict[str, Any]] = {}
    for source_event in output_value["author_events"]:
        event_id = source_event["event_id"]
        if event_id in event_by_id:
            raise ActivityError("SOURCE", "duplicate author event id")
        event_by_id[event_id] = source_event
    derived: list[dict[str, Any]] = []
    for adjudication in output_value["author_adjudications"]:
        event_id = adjudication["author_event_id"]
        if event_id not in event_by_id:
            raise ActivityError("SOURCE", "author adjudication event id is unresolved")
        triage = adjudication["author_triage"]
        if triage == "will_address":
            continue
        digest = interaction_sha256(run_id, event_id)
        event_type, disposition = (
            ("author_triage_wont_address", "wont_address") if triage == "wont_address"
            else ("author_triage_not_on_point", "not_on_point")
        )
        derived.append(_event(
            run_id, SOURCE_FAMILIES[0], event_type, stage, disposition, digest,
            author_source_record(adjudication, event_by_id[event_id], digest),
        ))
    return derived


def _receipt_shape(value: dict[str, Any], keys: set[str], version: str) -> None:
    if set(value) != keys or value.get("schema_version") != version:
        raise ActivityError("SOURCE", "closed action receipt shape/version is invalid")


def _blocking_contributors(report: dict[str, Any]) -> list[str]:
    if report.get("mode") != "systematic_review":
        return []
    result: set[str] = set()
    prisma = report.get("prisma_trAIce")
    if isinstance(prisma, dict) and prisma.get("block_decision") == "block":
        failed = prisma["by_tier"]["mandatory"]["fail"]
        if len(failed) != len(set(failed)):
            raise ActivityError("SOURCE", "PRISMA blocking contributor ids must be unique")
        result.update(failed)
    raise_part = report.get("raise")
    if isinstance(raise_part, dict) and raise_part.get("block_decision") == "block":
        result.update(name for name, status_value in raise_part["principles"].items() if status_value == "fail")
    return sorted(result)


def _compliance_events(run_id: str, groups: list[list[dict[str, Any]]], root: Path, total: list[int]) -> list[dict[str, Any]]:
    derived: list[dict[str, Any]] = []
    expected_ordinal = {"pipeline_stage_2_5": 1, "pipeline_stage_4_5": 1}
    receipt_ids: set[str] = set()
    receipt_keys = {
        "schema_version", "receipt_id", "run_id", "actor_role", "source", "action",
        "stage", "scope", "report_sha256", "override_ordinal", "interaction_id",
        "interaction_sha256",
    }
    for group in groups:
        report, _ = _load_artifact(root, group[0], total)
        _schema_validate(report, COMPLIANCE_SCHEMA_PATH, code="SOURCE")
        has_override = "user_override" in report
        if not has_override and len(group) == 1:
            continue
        if not has_override or len(group) != 2:
            raise ActivityError("SOURCE", "compliance action receipt pairing is invalid")
        receipt, _ = _load_artifact(root, group[1], total)
        _receipt_shape(receipt, receipt_keys, "adjudication-compliance-override-action/1.0")
        receipt_id = receipt.get("receipt_id")
        interaction_id = receipt.get("interaction_id")
        scope = receipt.get("scope")
        ordinal = receipt.get("override_ordinal")
        if (
            not isinstance(receipt_id, str) or not ID_RE.fullmatch(receipt_id)
            or not isinstance(interaction_id, str) or not ID_RE.fullmatch(interaction_id)
            or not isinstance(scope, list) or not scope
            or any(not isinstance(item, str) or not ID_RE.fullmatch(item) for item in scope)
            or len(scope) != len(set(scope))
            or not isinstance(ordinal, int) or isinstance(ordinal, bool) or ordinal < 1
            or not isinstance(receipt.get("report_sha256"), str)
            or not HEX_RE.fullmatch(receipt["report_sha256"])
            or not isinstance(receipt.get("interaction_sha256"), str)
            or not HEX_RE.fullmatch(receipt["interaction_sha256"])
        ):
            raise ActivityError("SOURCE", "compliance action receipt field types are invalid")
        blockers = _blocking_contributors(report)
        report_stage = {"2.5": "pipeline_stage_2_5", "4.5": "pipeline_stage_4_5"}.get(report.get("stage"))
        override = report["user_override"]
        valid = (
            report.get("overall_decision") == "block"
            and report.get("user_action_required") is True
            and bool(blockers)
            and override.get("decision") is True
            and report_stage == receipt.get("stage")
            and receipt.get("run_id") == run_id
            and receipt.get("actor_role") == "user"
            and receipt.get("source") == "explicit_session_user_action"
            and receipt.get("action") == "acknowledge_compliance_limitation"
            and receipt.get("report_sha256") == group[0]["sha256"]
        )
        scopes = (override.get("scope"), receipt.get("scope"))
        for candidate_scope in scopes:
            if (
                not isinstance(candidate_scope, list)
                or any(not isinstance(item, str) for item in candidate_scope)
                or len(candidate_scope) != len(set(candidate_scope))
                or set(candidate_scope) != set(blockers)
            ):
                valid = False
        stage = receipt.get("stage")
        if stage not in expected_ordinal or ordinal != expected_ordinal.get(stage):
            valid = False
        else:
            expected_ordinal[stage] += 1
        rationale = override.get("rationale")
        if ordinal == 2 and (not isinstance(rationale, str) or not rationale):
            valid = False
        if isinstance(ordinal, int) and ordinal >= 3 and (not isinstance(rationale, str) or len(rationale) < 100):
            valid = False
        if receipt_id in receipt_ids:
            valid = False
        else:
            receipt_ids.add(receipt_id)
        expected_digest = interaction_sha256(run_id, interaction_id)
        if receipt.get("interaction_sha256") != expected_digest:
            valid = False
        if not valid:
            raise ActivityError("SOURCE", "qualifying compliance override replay failed")
        source = compliance_source_record(
            group[0]["artifact_group_id"], stage, blockers, group[0]["sha256"],
            group[1]["sha256"], receipt,
        )
        derived.append(_event(
            run_id, SOURCE_FAMILIES[1], "compliance_block_override", stage,
            "block_overridden", expected_digest, source,
        ))
    return derived


def _rereview_events(run_id: str, group: list[dict[str, Any]], root: Path, total: list[int]) -> list[dict[str, Any]]:
    names = ("input_manifest", "precommitment", "verdict_record", "traceability")
    values: dict[str, dict[str, Any]] = {}
    for name, binding in zip(names, group):
        value, _ = _load_artifact(root, binding, total)
        _schema_validate(value, REREVIEW_CONTRACTS / f"{name}.schema.json", code="SOURCE")
        values[name] = value
    round_ids = {values[name].get("round_id") for name in names}
    if len(round_ids) != 1:
        raise ActivityError("SOURCE", "re-review round ids do not agree")
    if values["precommitment"].get("input_manifest_hash") != hashlib.sha256(canonical_bytes(values["input_manifest"])).hexdigest():
        raise ActivityError("SOURCE", "re-review input/precommitment hash chain mismatch")
    if values["verdict_record"].get("precommitment_hash") != hashlib.sha256(canonical_bytes(values["precommitment"])).hexdigest():
        raise ActivityError("SOURCE", "re-review precommitment/verdict hash chain mismatch")
    if values["traceability"].get("verdict_record_hash") != hashlib.sha256(canonical_bytes(values["verdict_record"])).hexdigest():
        raise ActivityError("SOURCE", "re-review verdict/traceability hash chain mismatch")
    verdict = values["verdict_record"]
    trace = values["traceability"]
    dissent_item: dict[str, str] = {}
    for dissent in verdict["dissents"]:
        if dissent["dissent_id"] in dissent_item:
            raise ActivityError("SOURCE", "duplicate re-review dissent id")
        dissent_item[dissent["dissent_id"]] = dissent["item_id"]
    adjudications_by_id: dict[str, dict[str, Any]] = {}
    for item in trace["dissent_adjudications"]:
        if item["dissent_id"] in adjudications_by_id:
            raise ActivityError("SOURCE", "duplicate dissent adjudication id")
        adjudications_by_id[item["dissent_id"]] = item
    qualifying_dissents = {
        dissent_id: item for dissent_id, item in adjudications_by_id.items()
        if item["adjudicator"] == "user" and item["outcome"] == "original_upheld"
    }
    reapp_by_id: dict[str, dict[str, Any]] = {}
    for item in trace["reapplications"]:
        if item["reapplication_id"] in reapp_by_id:
            raise ActivityError("SOURCE", "duplicate reapplication id")
        reapp_by_id[item["reapplication_id"]] = item
    superseded_by: dict[str, str] = {}
    for item in trace["reapplications"]:
        previous = item.get("supersedes_reapplication_id")
        if previous is not None:
            previous_item = reapp_by_id.get(previous)
            if previous_item is None or previous_item["item_id"] != item["item_id"] or previous in superseded_by:
                raise ActivityError("SOURCE", "invalid reapplication supersession")
            superseded_by[previous] = item["reapplication_id"]
    for item in trace["reapplications"]:
        seen: set[str] = set()
        cursor: dict[str, Any] | None = item
        while cursor is not None:
            cursor_id = cursor["reapplication_id"]
            if cursor_id in seen:
                raise ActivityError("SOURCE", "reapplication supersession cycle")
            seen.add(cursor_id)
            previous = cursor.get("supersedes_reapplication_id")
            cursor = reapp_by_id.get(previous) if previous is not None else None
    current_reapps = [item for item in trace["reapplications"] if item["reapplication_id"] not in superseded_by]
    for reapp in trace["reapplications"]:
        for answer_ref in reapp["answer_refs"]:
            if answer_ref.startswith("adjudication:"):
                dissent_id = answer_ref.split(":", 1)[1]
                adjudication = adjudications_by_id.get(dissent_id)
                if (
                    adjudication is None
                    or adjudication["outcome"] != "original_upheld"
                    or dissent_item.get(dissent_id) != reapp["item_id"]
                ):
                    raise ActivityError("SOURCE", "reapplication adjudication ref is unresolved or cross-item")
    for dissent_id, adjudication in adjudications_by_id.items():
        if adjudication["outcome"] == "original_upheld":
            holders = [
                reapp for reapp in current_reapps
                if f"adjudication:{dissent_id}" in reapp["answer_refs"]
            ]
            if len(holders) != 1:
                raise ActivityError("SOURCE", "original-upheld dissent requires exactly one current reapplication")
            if (
                holders[0]["reapplied_verdict"] == "CANNOT_VERIFY"
                or holders[0]["reapplied_verdict"] == holders[0]["pre_reapplication_verdict"]
            ):
                raise ActivityError("SOURCE", "original-upheld current reapplication must prove a verdict change")
    adjustments_by_item: dict[str, list[dict[str, Any]]] = {}
    global_adjustment_ids: set[str] = set()
    for adjustment in trace["adjustments"]:
        if adjustment["adjustment_id"] in global_adjustment_ids:
            raise ActivityError("SOURCE", "duplicate adjustment id")
        global_adjustment_ids.add(adjustment["adjustment_id"])
        adjustments_by_item.setdefault(adjustment["item_id"], []).append(adjustment)
    row_by_item: dict[str, dict[str, Any]] = {}
    for row in trace["rows"]:
        if row["item_id"] in row_by_item:
            raise ActivityError("SOURCE", "duplicate traceability row item id")
        row_by_item[row["item_id"]] = row
    adjustments_by_source: dict[str, list[dict[str, Any]]] = {}
    for adjustment in trace["adjustments"]:
        source_ref = adjustment.get("source_ref")
        if source_ref is not None:
            if source_ref.startswith("reapplication:") and source_ref.split(":", 1)[1] not in reapp_by_id:
                raise ActivityError("SOURCE", "adjustment source_ref names an unknown reapplication")
            adjustments_by_source.setdefault(source_ref, []).append(adjustment)
    for reapp in trace["reapplications"]:
        derived = adjustments_by_source.get(f"reapplication:{reapp['reapplication_id']}", [])
        changing = (
            reapp["reapplied_verdict"] != "CANNOT_VERIFY"
            and reapp["reapplied_verdict"] != reapp["pre_reapplication_verdict"]
        )
        if not changing:
            if derived:
                raise ActivityError("SOURCE", "non-changing/CANNOT reapplication has a derived adjustment")
            continue
        if len(derived) != 1:
            raise ActivityError("SOURCE", "verdict-changing reapplication requires exactly one derived adjustment")
        adjustment = derived[0]
        if (
            adjustment["item_id"] != reapp["item_id"]
            or adjustment["basis"] != "cross_model_adjudication"
            or adjustment["from_verdict"] != reapp["pre_reapplication_verdict"]
            or adjustment["to_verdict"] != reapp["reapplied_verdict"]
            or adjustment["rationale"] != reapp["rationale"]
            or adjustment.get("residual_gap") != reapp.get("residual_gap")
            or adjustment.get("evidence_anchor") != reapp.get("evidence_anchor")
        ):
            raise ActivityError("SOURCE", "derived adjustment does not mirror its reapplication")
    candidates: list[tuple[int, dict[str, Any], str, str]] = []
    counted_adjustments: set[str] = set()
    for dissent_id in qualifying_dissents:
        item_id = dissent_item.get(dissent_id)
        if item_id is None:
            raise ActivityError("SOURCE", "adjudicated dissent does not resolve to verdict dissent")
        reapps = [item for item in current_reapps if item["item_id"] == item_id and f"adjudication:{dissent_id}" in item["answer_refs"]]
        if len(reapps) != 1:
            raise ActivityError("SOURCE", "dissent must resolve to one current reapplication")
        if (
            reapps[0]["reapplied_verdict"] == "CANNOT_VERIFY"
            or reapps[0]["reapplied_verdict"] == reapps[0]["pre_reapplication_verdict"]
        ):
            raise ActivityError("SOURCE", "original-upheld current reapplication must prove a verdict change")
        records = adjustments_by_item.get(item_id, [])
        by_id = {item["adjustment_id"]: item for item in records}
        if len(by_id) != len(records):
            raise ActivityError("SOURCE", "duplicate adjustment id")
        followers: dict[str, dict[str, Any]] = {}
        heads: list[dict[str, Any]] = []
        for adjustment in records:
            previous = adjustment.get("supersedes_adjustment_id")
            if previous is None:
                heads.append(adjustment)
            elif previous not in by_id or previous in followers:
                raise ActivityError("SOURCE", "forked or orphan adjustment chain")
            else:
                followers[previous] = adjustment
        if len(heads) != 1:
            raise ActivityError("SOURCE", "adjustment chain must have exactly one head")
        chain = [heads[0]]
        while chain[-1]["adjustment_id"] in followers:
            next_item = followers[chain[-1]["adjustment_id"]]
            if next_item["from_verdict"] != chain[-1]["to_verdict"]:
                raise ActivityError("SOURCE", "adjustment chain verdict join mismatch")
            chain.append(next_item)
        if len(chain) != len(records):
            raise ActivityError("SOURCE", "adjustment chain contains a cycle or disconnected record")
        row = row_by_item.get(item_id)
        if not row or row.get("adjustment_id") != chain[-1]["adjustment_id"] or row.get("final_verdict") != chain[-1]["to_verdict"]:
            raise ActivityError("SOURCE", "final row does not bind adjustment chain tail")
        reapp = reapps[0]
        for adjustment in chain:
            if (
                adjustment["basis"] == "cross_model_adjudication"
                and adjustment.get("source_ref") == f"reapplication:{reapp['reapplication_id']}"
                and adjustment["from_verdict"] != adjustment["to_verdict"]
            ):
                if adjustment["adjustment_id"] in counted_adjustments:
                    raise ActivityError("SOURCE", "one adjustment cannot produce multiple activity events")
                counted_adjustments.add(adjustment["adjustment_id"])
                numeric = int(adjustment["adjustment_id"].split("-", 1)[1])
                candidates.append((numeric, adjustment, dissent_id, reapp["reapplication_id"]))
    trace_hash = group[3]["sha256"]
    return [
        _event(
            run_id, SOURCE_FAMILIES[2], "re_review_verdict_changed",
            "pipeline_stage_3_prime", "verdict_changed", None,
            re_review_source_record(
                values["input_manifest"]["round_id"], dissent_id,
                adjustment["item_id"], reapplication_id, adjustment, trace_hash,
            ),
        )
        for _, adjustment, dissent_id, reapplication_id in sorted(candidates, key=lambda item: item[0])
    ]


def _validate_action_log(value: dict[str, Any], *, run_id: str, mandatory: bool) -> list[dict[str, Any]]:
    version = "adjudication-mandatory-checkpoint-log/1.0" if mandatory else "adjudication-explicit-user-request-log/1.0"
    if set(value) != {"schema_version", "run_id", "records"} or value.get("schema_version") != version or value.get("run_id") != run_id:
        raise ActivityError("SOURCE", "action log root is invalid")
    records = value.get("records")
    if not isinstance(records, list) or len(records) > MAX_EVENTS_RUN:
        raise ActivityError("SOURCE", "action log record list is invalid")
    ids: set[str] = set()
    for record in records:
        common = {"actor_role", "source", "stage", "interaction_id", "interaction_sha256"}
        expected = common | (
            {"response_id", "checkpoint_id", "checkpoint_type", "disposition"}
            if mandatory else {"request_id", "action", "finding_id"}
        )
        if not isinstance(record, dict) or set(record) != expected:
            raise ActivityError("SOURCE", "action log record closed shape is invalid")
        record_id = record["response_id" if mandatory else "request_id"]
        if not isinstance(record_id, str) or not ID_RE.fullmatch(record_id) or record_id in ids:
            raise ActivityError("SOURCE", "action log record id is invalid or repeated")
        ids.add(record_id)
        identifier_fields = (
            ("checkpoint_id", "interaction_id")
            if mandatory else ("finding_id", "interaction_id")
        )
        if any(
            not isinstance(record.get(field), str) or not ID_RE.fullmatch(record[field])
            for field in identifier_fields
        ):
            raise ActivityError("SOURCE", "action log identifier is outside the closed grammar")
        if record.get("actor_role") != "user" or record.get("source") != "explicit_session_user_action" or record.get("stage") not in STAGES:
            raise ActivityError("SOURCE", "action log authority/stage is invalid")
        interaction_id = record.get("interaction_id")
        if not isinstance(interaction_id, str) or not ID_RE.fullmatch(interaction_id) or record.get("interaction_sha256") != interaction_sha256(run_id, interaction_id):
            raise ActivityError("SOURCE", "action log interaction digest is invalid")
        if mandatory:
            if record.get("checkpoint_type") != "MANDATORY" or record.get("disposition") not in {"proceed", "skip", "pause", "adjust", "view_progress", "redo", "abort"}:
                raise ActivityError("SOURCE", "mandatory checkpoint record is invalid")
        elif record.get("action") not in {"justify_finding", "redo_finding"}:
            raise ActivityError("SOURCE", "explicit request action is invalid")
    return records


def _log_events(run_id: str, family: str, group: list[dict[str, Any]], root: Path, total: list[int]) -> tuple[list[dict[str, Any]], int]:
    value, _ = _load_artifact(root, group[0], total)
    mandatory = family == SOURCE_FAMILIES[4]
    records = _validate_action_log(value, run_id=run_id, mandatory=mandatory)
    result: list[dict[str, Any]] = []
    for record in records:
        if mandatory:
            source_disposition = record["disposition"]
            if source_disposition == "proceed":
                continue
            disposition = "skip_refused" if source_disposition == "skip" else source_disposition
            result.append(_event(
                run_id, family, "mandatory_checkpoint_non_proceed", record["stage"],
                disposition, record["interaction_sha256"], mandatory_source_record(record),
            ))
        else:
            event_type, disposition = (
                ("finding_justification_requested", "justification_requested")
                if record["action"] == "justify_finding"
                else ("finding_redo_requested", "redo_requested")
            )
            result.append(_event(
                run_id, family, event_type, record["stage"], disposition,
                record["interaction_sha256"], explicit_source_record(record),
            ))
    return result, len(records)


def _validate_manifest_authority(manifest: dict[str, Any], root: Path) -> tuple[dict[str, Any], bytes]:
    _schema_validate(manifest, INPUT_SCHEMA_PATH, code="INPUT")
    terminal = manifest["terminal_receipt"]
    state_raw = _read_artifact_relative(root, terminal["relative_path"], MAX_STORE)
    if hashlib.sha256(state_raw).hexdigest() != terminal["sha256"]:
        raise ActivityError("INPUT", "terminal receipt raw-byte hash mismatch")
    state = strict_json(state_raw, code="INPUT")
    run_id, pipeline_state, stage, status = _state_replay(state)
    exact = {
        "artifact_id": "pipeline-state-terminal-receipt",
        "relative_path": terminal["relative_path"],
        "sha256": hashlib.sha256(state_raw).hexdigest(),
        "run_id": run_id, "pipeline_state": pipeline_state,
        "current_stage": stage, "current_stage_status": status,
    }
    if terminal != exact:
        raise ActivityError("INPUT", "terminal receipt projection does not exactly replay")
    if manifest["run_id"] != run_id or manifest["terminal_state"] != pipeline_state or manifest["terminal_stage"] != stage:
        raise ActivityError("INPUT", "input root does not match terminal state authority")
    inventory = state.get("adjudication_activity_sources")
    if inventory != manifest["sources"]:
        raise ActivityError("INPUT", "input sources differ from sealed terminal inventory")
    _validate_source_rows(inventory)
    for row in inventory:
        _group_artifacts(row)
        if row["source_family"] == SOURCE_FAMILIES[0] and row["capture_state"] == "captured":
            for group in _group_artifacts(row):
                raw_stage = STAGE_TO_RAW[group[0]["artifact_group_stage"]]
                stage_row = state.get("stages", {}).get(raw_stage)
                if not isinstance(stage_row, dict) or stage_row.get("status") != "completed":
                    raise ActivityError("INPUT", "author source stage is not completed in terminal state")
    return state, state_raw


def _extract_run(manifest: dict[str, Any], root: Path, sequence: int) -> dict[str, Any]:
    _, _ = _validate_manifest_authority(manifest, root)
    run_id = manifest["run_id"]
    total = [0]
    source_rows: list[dict[str, Any]] = []
    all_events: list[list[dict[str, Any]]] = []
    action_log_record_count = 0
    for row in manifest["sources"]:
        groups = _group_artifacts(row)
        events: list[dict[str, Any]] = []
        if row["capture_state"] == "captured":
            family = row["source_family"]
            if family == SOURCE_FAMILIES[0]:
                for group in groups:
                    events.extend(_author_events(run_id, group[0]["artifact_group_stage"], group, root, total))
            elif family == SOURCE_FAMILIES[1]:
                events = _compliance_events(run_id, groups, root, total)
            elif family == SOURCE_FAMILIES[2]:
                events = _rereview_events(run_id, groups[0], root, total)
            else:
                events, source_record_count = _log_events(run_id, family, groups[0], root, total)
                action_log_record_count += source_record_count
                if action_log_record_count > MAX_EVENTS_RUN:
                    raise ActivityError("CAP", "combined action-log records exceed per-run cap")
        all_events.append(events)
        source_rows.append({
            "source_family": row["source_family"],
            "capture_state": row["capture_state"],
            "reason_code": row["reason_code"],
            "artifact_sha256s": [item["sha256"] for item in row["artifacts"]],
            "events": events,
        })
    winner: dict[str, int] = {}
    for family_index, events in enumerate(all_events):
        for event in events:
            digest = event["interaction_sha256"]
            if digest is not None and digest not in winner:
                winner[digest] = family_index
    for family_index, source in enumerate(source_rows):
        source["events"] = [
            event for event in source["events"]
            if event["interaction_sha256"] is None or winner[event["interaction_sha256"]] == family_index
        ]
    event_count = sum(len(row["events"]) for row in source_rows)
    if event_count > MAX_EVENTS_RUN:
        raise ActivityError("CAP", "derived events exceed per-run cap")
    record: dict[str, Any] = {
        "append_sequence": sequence,
        "run_id": run_id,
        "terminal_state": manifest["terminal_state"],
        "terminal_stage": manifest["terminal_stage"],
        "terminal_receipt_sha256": manifest["terminal_receipt"]["sha256"],
        "input_receipt_sha256": _digest(b"ars.adjudication-activity.input/1.0\0", manifest),
        "record_sha256": "",
        "sealed": True,
        "sources": source_rows,
    }
    preimage = {key: value for key, value in record.items() if key != "record_sha256"}
    record["record_sha256"] = _digest(b"ars.adjudication-activity.run/1.0\0", preimage)
    return record


def _empty_store(store_id: str) -> dict[str, Any]:
    return {
        "schema_version": STORE_VERSION, "store_id": store_id,
        "revision": 0, "next_sequence": 1, "runs": [],
        "data_minimization": copy.deepcopy(DATA_MINIMIZATION),
    }


def _validate_store(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ActivityError("STORE", "store root must be an object")
    _schema_validate(value, STORE_SCHEMA_PATH, code="STORE")
    runs = value["runs"]
    if len(runs) > MAX_RUNS:
        raise ActivityError("CAP", "retained runs exceed hard cap")
    sequences: list[int] = []
    identities: dict[str, set[Any]] = {
        "run": set(), "input": set(), "record": set(), "event": set(),
    }
    total_events = 0
    for run in runs:
        sequences.append(run["append_sequence"])
        checks = (("run", run["run_id"]), ("input", run["input_receipt_sha256"]), ("record", run["record_sha256"]))
        for kind, identity in checks:
            if identity in identities[kind]:
                raise ActivityError("STORE", f"duplicate {kind} identity")
            identities[kind].add(identity)
        preimage = {key: item for key, item in run.items() if key != "record_sha256"}
        if run["record_sha256"] != _digest(b"ars.adjudication-activity.run/1.0\0", preimage):
            raise ActivityError("STORE", "run record digest mismatch")
        if [row["source_family"] for row in run["sources"]] != list(SOURCE_FAMILIES):
            raise ActivityError("STORE", "stored source family order mismatch")
        captured_counts = (
            {2, 4}, set(range(1, 33)), {4}, {1}, {1},
        )
        cross_family: dict[str, int] = {}
        for family_index, row in enumerate(run["sources"]):
            artifact_count = len(row["artifact_sha256s"])
            if row["capture_state"] == "captured" and artifact_count not in captured_counts[family_index]:
                raise ActivityError("STORE", "captured source artifact count violates family contract")
            if row["capture_state"] != "captured" and artifact_count != 0:
                raise ActivityError("STORE", "non-captured source retains artifact hashes")
            for event in row["events"]:
                if event["event_id"] in identities["event"]:
                    raise ActivityError("STORE", "duplicate event id")
                identities["event"].add(event["event_id"])
                digest = event["interaction_sha256"]
                if digest is not None and digest in cross_family and cross_family[digest] != family_index:
                    raise ActivityError("STORE", "cross-family causal duplicate remains in store")
                if digest is not None:
                    cross_family[digest] = family_index
                payload = {
                    "run_id": run["run_id"], "source_family": row["source_family"],
                    "event_type": event["event_type"], "stage": event["stage"],
                    "disposition": event["disposition"],
                    "interaction_sha256": digest,
                    "source_event_sha256": event["source_event_sha256"],
                }
                expected_id = "ACTIVITY-EVENT-" + _digest(b"ars.adjudication-activity.event-id/1.0\0", payload)
                if event["event_id"] != expected_id:
                    raise ActivityError("STORE", "event id digest mismatch")
                total_events += 1
    if sequences != sorted(sequences) or len(sequences) != len(set(sequences)):
        raise ActivityError("STORE", "append sequences are not strictly increasing")
    if sequences and value["next_sequence"] <= sequences[-1]:
        raise ActivityError("STORE", "next_sequence does not exceed retained sequences")
    if value["revision"] < len(runs):
        raise ActivityError("STORE", "revision cannot be below retained append count")
    if value["revision"] < value["next_sequence"] - 1:
        raise ActivityError("STORE", "revision cannot be below allocated append sequences")
    if total_events > MAX_EVENTS_STORE:
        raise ActivityError("CAP", "store event count exceeds hard cap")
    return value


def _read_store(path: Path) -> tuple[dict[str, Any], bytes, tuple[int, int, int]]:
    raw, identity = _read_limited_identity(path, MAX_STORE, code="STORE")
    value = strict_json(raw, code="STORE")
    if raw != canonical_bytes(value, code="STORE") + b"\n":
        raise ActivityError("STORE", "store bytes are not canonical JSON plus one LF")
    return _validate_store(value), raw, identity


def _store_bytes(value: dict[str, Any]) -> bytes:
    _validate_store(value)
    raw = canonical_bytes(value, code="STORE") + b"\n"
    if len(raw) > MAX_STORE:
        raise ActivityError("CAP", "persisted store exceeds hard byte cap")
    return raw


def _json_id(value: str) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _cmd_init(args: argparse.Namespace) -> str:
    path = Path(args.store)
    with _store_lock(path, exclusive=True):
        if path.exists() or path.is_symlink():
            raise ActivityError("CONFLICT", "store path already exists")
        store = _empty_store(args.store_id)
        _schema_validate(store, STORE_SCHEMA_PATH, code="STORE")
        _atomic_create(path, _store_bytes(store))
    return f"[ARS-ADJUDICATION-ACTIVITY] initialized store_id={_json_id(args.store_id)}; revision=0; next_sequence=1"


def _cmd_build(args: argparse.Namespace) -> str:
    state_path, root = Path(args.state), Path(args.artifact_root)
    state_raw = _read_limited(state_path, MAX_STORE, code="INPUT")
    state = strict_json(state_raw, code="INPUT")
    run_id, pipeline_state, stage, _ = _state_replay(state)
    inventory = state.get("adjudication_activity_sources")
    _validate_source_rows(inventory)
    relative = _relative_binding(root, state_path)
    manifest = {
        "schema_version": INPUT_VERSION, "store_id": args.store_id,
        "run_id": run_id, "terminal_state": pipeline_state,
        "terminal_stage": stage,
        "terminal_receipt": _terminal_receipt(state, state_raw, relative),
        "sources": copy.deepcopy(inventory),
        "data_minimization": copy.deepcopy(DATA_MINIMIZATION),
    }
    _validate_manifest_authority(manifest, root)
    # Full extraction here proves every projected artifact before publishing input.
    _extract_run(manifest, root, 1)
    _atomic_create(Path(args.output), canonical_bytes(manifest) + b"\n")
    return f"[ARS-ADJUDICATION-ACTIVITY] built_input run_id={_json_id(run_id)}; source_count=5"


def _load_manifest(path: Path) -> dict[str, Any]:
    raw = _read_limited(path, MAX_INPUT, code="INPUT")
    value = strict_json(raw, code="INPUT")
    if not isinstance(value, dict):
        raise ActivityError("INPUT", "input manifest root must be an object")
    _schema_validate(value, INPUT_SCHEMA_PATH, code="INPUT")
    return value


def _cmd_append(args: argparse.Namespace) -> str:
    manifest = _load_manifest(Path(args.input))
    root, path = Path(args.artifact_root), Path(args.store)
    receipt = _digest(b"ars.adjudication-activity.input/1.0\0", manifest)
    with _store_lock(path, exclusive=True):
        if path.exists() or path.is_symlink():
            store, _, store_identity = _read_store(path)
            if store["store_id"] != manifest["store_id"]:
                raise ActivityError("CONFLICT", "store id differs from input store id")
        else:
            store = _empty_store(manifest["store_id"])
            store_identity = None
        for retained in store["runs"]:
            if retained["run_id"] == manifest["run_id"]:
                if retained["input_receipt_sha256"] == receipt:
                    return (
                        f"[ARS-ADJUDICATION-ACTIVITY] already_appended run_id={_json_id(retained['run_id'])}; "
                        f"append_sequence={retained['append_sequence']}; revision={store['revision']}"
                    )
                raise ActivityError("CONFLICT", "run id is retained with a different input receipt")
            if retained["input_receipt_sha256"] == receipt:
                raise ActivityError("CONFLICT", "input receipt is retained under a different run id")
        if len(store["runs"]) >= MAX_RUNS:
            raise ActivityError("CAP", "retained run cap reached")
        # Source and terminal replay occurs only for a genuinely new identity.
        record = _extract_run(manifest, root, store["next_sequence"])
        candidate = copy.deepcopy(store)
        candidate["runs"].append(record)
        candidate["next_sequence"] += 1
        candidate["revision"] += 1
        raw = _store_bytes(candidate)
        if store_identity is not None:
            _atomic_replace(path, raw, expected_identity=store_identity)
        else:
            _atomic_create(path, raw)
    return (
        f"[ARS-ADJUDICATION-ACTIVITY] appended run_id={_json_id(record['run_id'])}; "
        f"append_sequence={record['append_sequence']}; revision={candidate['revision']}"
    )


def _render(store: dict[str, Any], window: int) -> str:
    selected = store["runs"][-window:]
    count = sum(len(source["events"]) for run in selected for source in run["sources"])
    overturn = sum(
        event["event_type"] in OVERTURN_TYPES
        for run in selected for source in run["sources"] for event in source["events"]
    )
    unavailable_runs = sum(any(source["capture_state"] == "unavailable" for source in run["sources"]) for run in selected)
    lines: list[str] = []
    if len(selected) < 2:
        lines.append(
            f"[ARS-ADJUDICATION-ACTIVITY INSUFFICIENT_HISTORY] selected_retained_eligible_run_count={len(selected)}; "
            f"minimum_required=2; requested_window={window}."
        )
        lines.append(
            f"[ARS-ADJUDICATION-ACTIVITY COUNTS] adjudication_count={count} (denominator: {len(selected)} retained eligible terminal run records); "
            f"overturn_count={overturn} (denominator: {count} recorded adjudications); unavailable_run_count={unavailable_runs} "
            f"(denominator: {len(selected)} retained eligible terminal run records)."
        )
    else:
        lines.append(
            f"[ARS-ADJUDICATION-ACTIVITY] selected_retained_eligible_run_count={len(selected)}; requested_window={window}; "
            f"adjudication_count={count} (denominator: {len(selected)} retained eligible terminal run records); "
            f"overturn_count={overturn} (denominator: {count} recorded adjudications); unavailable_run_count={unavailable_runs} "
            f"(denominator: {len(selected)} retained eligible terminal run records)."
        )
    for run in selected:
        run_count = sum(len(source["events"]) for source in run["sources"])
        run_overturn = sum(event["event_type"] in OVERTURN_TYPES for source in run["sources"] for event in source["events"])
        unavailable = sum(source["capture_state"] == "unavailable" for source in run["sources"])
        lines.append(
            f"sequence={run['append_sequence']}; run_id={_json_id(run['run_id'])}; terminal_state={run['terminal_state']}; "
            f"adjudication_count={run_count} (denominator: 1 retained eligible terminal run record); "
            f"overturn_count={run_overturn} (denominator: {run_count} recorded adjudications); "
            f"unavailable_source_count={unavailable} (denominator: 5 source families)."
        )
    lines.extend((COVERAGE, LIMITATION, ADVISORY))
    return "\n".join(lines)


def _cmd_render(args: argparse.Namespace) -> str:
    path = Path(args.store)
    with _store_lock(path, exclusive=False):
        store, _, _ = _read_store(path)
    return _render(store, args.window)


def _cmd_validate(args: argparse.Namespace) -> str:
    path = Path(args.store)
    with _store_lock(path, exclusive=False):
        store, _, _ = _read_store(path)
    return (
        f"[ARS-ADJUDICATION-ACTIVITY] valid store_id={_json_id(store['store_id'])}; "
        f"retained_runs={len(store['runs'])}; revision={store['revision']}; next_sequence={store['next_sequence']}"
    )


def _confirmation(store_id: str, expected_hash: str, raw: bytes) -> None:
    if not HEX_RE.fullmatch(expected_hash) or hashlib.sha256(raw).hexdigest() != expected_hash:
        raise ActivityError("DELETE_CONFIRMATION", "store raw-byte hash confirmation mismatch")
    if store_id is None:
        raise ActivityError("DELETE_CONFIRMATION", "store id confirmation is required")


def _cmd_delete_runs(args: argparse.Namespace) -> str:
    path = Path(args.store)
    with _store_lock(path, exclusive=True):
        store, raw, store_identity = _read_store(path)
        _confirmation(args.store_id, args.expect_store_sha256, raw)
        if store["store_id"] != args.store_id:
            raise ActivityError("DELETE_CONFIRMATION", "store id confirmation mismatch")
        if args.run_id:
            if len(args.run_id) != len(set(args.run_id)):
                raise ActivityError("DELETE_CONFIRMATION", "run id deletion set has duplicates")
            wanted = set(args.run_id)
            existing = {run["run_id"] for run in store["runs"]}
            if not wanted or not wanted <= existing:
                raise ActivityError("DELETE_CONFIRMATION", "run id deletion target mismatch")
            survivors = [run for run in store["runs"] if run["run_id"] not in wanted]
        else:
            try:
                first_text, last_text = args.sequence_range.split(":", 1)
                first, last = int(first_text), int(last_text)
            except (AttributeError, ValueError):
                raise ActivityError("DELETE_CONFIRMATION", "invalid sequence range") from None
            if first < 1 or first > last:
                raise ActivityError("DELETE_CONFIRMATION", "invalid sequence range")
            selected = {run["append_sequence"] for run in store["runs"] if first <= run["append_sequence"] <= last}
            if not selected:
                raise ActivityError("DELETE_CONFIRMATION", "sequence range selects no retained run")
            survivors = [run for run in store["runs"] if run["append_sequence"] not in selected]
        deleted = len(store["runs"]) - len(survivors)
        candidate = copy.deepcopy(store)
        candidate["runs"] = survivors
        candidate["revision"] += 1
        _atomic_replace(path, _store_bytes(candidate), expected_identity=store_identity)
    return f"[ARS-ADJUDICATION-ACTIVITY] deleted_runs={deleted}; revision={candidate['revision']}; next_sequence={candidate['next_sequence']}"


def _cmd_delete_store(args: argparse.Namespace) -> str:
    if args.confirm != "DELETE-ADJUDICATION-ACTIVITY-STORE":
        raise ActivityError("DELETE_CONFIRMATION", "whole-store confirmation token mismatch")
    path = Path(args.store)
    with _store_lock(path, exclusive=True):
        raw, store_identity = _read_limited_identity(path, MAX_STORE, code="STORE")
        _confirmation(args.store_id, args.expect_store_sha256, raw)
        try:
            parsed = strict_json(raw, code="STORE")
            if raw != canonical_bytes(parsed, code="STORE") + b"\n":
                raise ActivityError("STORE", "store bytes are noncanonical")
            store = _validate_store(parsed)
        except ActivityError:
            store = None
        if store is not None and store["store_id"] != args.store_id:
            raise ActivityError("DELETE_CONFIRMATION", "store id confirmation mismatch")
        try:
            _assert_identity(path, store_identity)
            os.unlink(path)
            directory_fd = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
        except OSError as exc:
            raise ActivityError("WRITE", f"store deletion failed: {exc.__class__.__name__}") from None
    return "[ARS-ADJUDICATION-ACTIVITY] deleted_store=true"


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise ActivityError("USAGE", message)


def build_cli_parser() -> argparse.ArgumentParser:
    parser = _Parser(prog="adjudication_activity.py")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init-store")
    init_parser.add_argument("--store", required=True)
    init_parser.add_argument("--store-id", required=True)
    init_parser.set_defaults(handler=_cmd_init)

    build_parser = subparsers.add_parser("build-input")
    build_parser.add_argument("--state", required=True)
    build_parser.add_argument("--artifact-root", required=True)
    build_parser.add_argument("--store-id", required=True)
    build_parser.add_argument("--output", required=True)
    build_parser.set_defaults(handler=_cmd_build)

    append_parser = subparsers.add_parser("append-run")
    append_parser.add_argument("--store", required=True)
    append_parser.add_argument("--artifact-root", required=True)
    append_parser.add_argument("--input", required=True)
    append_parser.set_defaults(handler=_cmd_append)

    render_parser = subparsers.add_parser("render")
    render_parser.add_argument("--store", required=True)
    render_parser.add_argument("--window", type=int, default=10)
    render_parser.set_defaults(handler=_cmd_render)

    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("--store", required=True)
    validate_parser.set_defaults(handler=_cmd_validate)

    delete_runs_parser = subparsers.add_parser("delete-runs")
    delete_runs_parser.add_argument("--store", required=True)
    delete_runs_parser.add_argument("--store-id", required=True)
    delete_runs_parser.add_argument("--expect-store-sha256", required=True)
    selection = delete_runs_parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--run-id", action="append")
    selection.add_argument("--sequence-range")
    delete_runs_parser.set_defaults(handler=_cmd_delete_runs)

    delete_store_parser = subparsers.add_parser("delete-store")
    delete_store_parser.add_argument("--store", required=True)
    delete_store_parser.add_argument("--store-id", required=True)
    delete_store_parser.add_argument("--expect-store-sha256", required=True)
    delete_store_parser.add_argument("--confirm", required=True)
    delete_store_parser.set_defaults(handler=_cmd_delete_store)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    try:
        args = build_cli_parser().parse_args(argv)
        if getattr(args, "window", 10) not in range(2, 51):
            raise ActivityError("USAGE", "window must be in the closed range 2..50")
        output = args.handler(args)
        if output:
            print(output)
        return 0
    except ActivityError as exc:
        print(f"[ARS-ADJUDICATION-ACTIVITY ERROR:{exc.code}] {exc.detail}", file=sys.stderr)
        return EXIT_BY_CODE[exc.code]


if __name__ == "__main__":
    raise SystemExit(main())
