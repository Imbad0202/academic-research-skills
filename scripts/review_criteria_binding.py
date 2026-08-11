#!/usr/bin/env python3
"""Build and validate #684 review-criteria consumer bindings.

The tool is deterministic and stdlib-only.  It reads only explicitly named
paths, never invokes a model or network service, and never derives a review
verdict.
"""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import re
import stat
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator, NoReturn

from resolve_review_target_context import ContractError as ResolverError
from resolve_review_target_context import resolve


SCHEMA_VERSION = "review-criteria-binding/1.0"
FINDINGS_VERSION = "constructive-review-findings/1.0"
MAX_JSON_BYTES = 4 * 1024 * 1024
MAX_ARTIFACT_BYTES = 2 * 1024 * 1024
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
CRITERION_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
CONSUMERS = ("formative_planning", "internal_evaluator", "external_panel")
ROLES = {
    "formative_planning": ("FORMATIVE",),
    "internal_evaluator": ("INTERNAL",),
    "external_panel": ("EIC", "R1", "R2", "R3", "DA"),
}
DIMENSIONS = ("scientific_validity", "venue_fit", "submission_readiness")
ANCHOR_TYPES = ("text", "table", "figure", "equation", "dataset", "absence")
OPTION_SCOPES = ("sentence", "section", "re_analysis", "new_data", "other")
INTENT_STATES = (
    "no",
    "yes_author_choice_required",
    "uncertain_author_choice_required",
)


class BindingError(ValueError):
    """Raised for malformed, mismatched, or unsafe binding artifacts."""


class ConflictError(BindingError):
    """Raised when a stable identity is reused for different content."""


def _fail(path: str, message: str) -> NoReturn:
    raise BindingError(f"{path}: {message}")


def _canonical_bytes(value: Any) -> bytes:
    try:
        return json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError, UnicodeEncodeError) as exc:
        raise BindingError(f"value is not canonical JSON: {exc}") from exc


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _reject_constant(value: str) -> NoReturn:
    raise BindingError(f"non-finite JSON number is not allowed: {value}")


def _reject_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise BindingError(f"duplicate JSON key is not allowed: {key}")
        result[key] = value
    return result


def _open_nofollow(path: Path, flags: int) -> int:
    """Open one explicit path without traversing a symlinked component."""
    directory_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    parts = path.parts
    if path.is_absolute():
        directory_fd = os.open(os.sep, directory_flags)
        components = parts[1:]
    else:
        directory_fd = os.open(".", directory_flags)
        components = parts
    if not components:
        os.close(directory_fd)
        raise BindingError(f"explicit input must name a file: {path}")
    try:
        for component in components[:-1]:
            next_fd = os.open(
                component,
                directory_flags | nofollow,
                dir_fd=directory_fd,
            )
            os.close(directory_fd)
            directory_fd = next_fd
        return os.open(components[-1], flags | nofollow, dir_fd=directory_fd)
    except OSError as exc:
        raise BindingError(
            f"cannot traverse explicit input without symlinks {path}: {exc}"
        ) from exc
    finally:
        os.close(directory_fd)


def _read_bytes(path: Path, limit: int) -> bytes:
    try:
        fd = _open_nofollow(path, os.O_RDONLY)
    except BindingError:
        raise
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode):
            raise BindingError(f"explicit input is not a regular file: {path}")
        if info.st_size > limit:
            raise BindingError(f"explicit input exceeds {limit} bytes: {path}")
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = os.read(fd, min(65536, limit + 1 - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
            if total > limit:
                raise BindingError(f"explicit input exceeds {limit} bytes: {path}")
        final = os.fstat(fd)
        if (final.st_dev, final.st_ino, final.st_size, final.st_mtime_ns, final.st_ctime_ns) != (
            info.st_dev,
            info.st_ino,
            info.st_size,
            info.st_mtime_ns,
            info.st_ctime_ns,
        ):
            raise BindingError(f"explicit input changed while being read: {path}")
        raw = b"".join(chunks)
        if len(raw) != final.st_size:
            raise BindingError(f"short read from explicit input: {path}")
        return raw
    finally:
        os.close(fd)


def _read_json(path: Path) -> tuple[dict[str, Any], bytes]:
    raw = _read_bytes(path, MAX_JSON_BYTES)
    try:
        value = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_reject_pairs,
            parse_constant=_reject_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BindingError(f"cannot parse strict JSON input {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise BindingError(f"top-level JSON value must be an object: {path}")
    return value, raw


def _object(value: Any, path: str, keys: set[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        _fail(path, "must be an object")
    missing = keys - set(value)
    extra = set(value) - keys
    if missing:
        _fail(path, f"missing field(s): {', '.join(sorted(missing))}")
    if extra:
        _fail(path, f"undeclared field(s): {', '.join(sorted(extra))}")
    return value


def _string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        _fail(path, "must be a non-empty string")
    return value


def _id(value: Any, path: str) -> str:
    text = _string(value, path)
    if ID_RE.fullmatch(text) is None:
        _fail(path, "must be 1..128 ASCII identifier characters")
    return text


def _sha(value: Any, path: str) -> str:
    text = _string(value, path)
    if SHA_RE.fullmatch(text) is None:
        _fail(path, "must be a lowercase SHA-256 digest")
    return text


def _portable_ref(value: Any, path: str) -> str:
    text = _string(value, path)
    if len(text) > 512 or text.startswith("/") or "\\" in text:
        _fail(path, "must be a portable relative POSIX reference")
    if any(part in ("", ".", "..") for part in text.split("/")):
        _fail(path, "must not contain empty, dot, or parent components")
    return text


def _criterion_ids(value: Any, path: str) -> list[str]:
    if not isinstance(value, list):
        _fail(path, "must be an array")
    result: list[str] = []
    for index, item in enumerate(value):
        text = _string(item, f"{path}[{index}]")
        if CRITERION_ID_RE.fullmatch(text) is None:
            _fail(f"{path}[{index}]", "must be a canonical criterion id")
        if text in result:
            _fail(path, f"duplicate criterion id: {text}")
        result.append(text)
    return result


def _manifest_payload(manifest: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in manifest.items() if key != "manifest_digest"}


def _receipt_payload(receipt: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in receipt.items() if key != "receipt_digest"}


def _authority(context: dict[str, Any], context_raw: bytes, registry_raw: bytes,
               context_ref: str, registry_ref: str) -> dict[str, Any]:
    pointers = []
    for item in context["selected_criteria"]:
        pointers.append(
            {
                "criterion_id": item["criterion_id"],
                "criterion_version": item["criterion_version"],
                "criterion_digest": item["criterion_digest"],
                "dimension": item["dimension"],
                "blocking_eligible": item["blocking_eligible"],
            }
        )
    conflicts = [
        {
            "conflict_group": item["conflict_group"],
            "criterion_ids": item["criterion_ids"],
        }
        for item in context["parallel_conflicts"]
    ]
    unresolved = [
        {"code": item["code"], "dimension": item["dimension"]}
        for item in context["unresolved"]
    ]
    return {
        "context_ref": _portable_ref(context_ref, "context_ref"),
        "context_sha256": hashlib.sha256(context_raw).hexdigest(),
        "registry_ref": _portable_ref(registry_ref, "registry_ref"),
        "registry_sha256": hashlib.sha256(registry_raw).hexdigest(),
        "resolved_digest": context["resolved_digest"],
        "selected_criterion_ids": context["selected_criterion_ids"],
        "selected_criteria": pointers,
        "parallel_conflicts": conflicts,
        "unresolved": unresolved,
        "phase1_safe": True,
    }


def _validate_context_pair(context: dict[str, Any], registry: dict[str, Any]) -> None:
    try:
        expected = resolve(context.get("declaration"), registry)
    except (ResolverError, TypeError, KeyError) as exc:
        raise BindingError(f"ReviewTargetContext cannot be recomputed: {exc}") from exc
    if context != expected:
        raise BindingError(
            "ReviewTargetContext does not equal deterministic #683 resolution"
        )


def _validate_authority(value: Any, path: str) -> dict[str, Any]:
    keys = {
        "context_ref", "context_sha256", "registry_ref", "registry_sha256",
        "resolved_digest", "selected_criterion_ids", "selected_criteria",
        "parallel_conflicts", "unresolved", "phase1_safe",
    }
    obj = _object(value, path, keys)
    _portable_ref(obj["context_ref"], f"{path}.context_ref")
    _sha(obj["context_sha256"], f"{path}.context_sha256")
    _portable_ref(obj["registry_ref"], f"{path}.registry_ref")
    _sha(obj["registry_sha256"], f"{path}.registry_sha256")
    _sha(obj["resolved_digest"], f"{path}.resolved_digest")
    ids = _criterion_ids(obj["selected_criterion_ids"], f"{path}.selected_criterion_ids")
    if obj["phase1_safe"] is not True:
        _fail(f"{path}.phase1_safe", "must equal true")
    if not isinstance(obj["selected_criteria"], list):
        _fail(f"{path}.selected_criteria", "must be an array")
    pointer_ids: list[str] = []
    for index, item in enumerate(obj["selected_criteria"]):
        p = _object(
            item,
            f"{path}.selected_criteria[{index}]",
            {"criterion_id", "criterion_version", "criterion_digest", "dimension", "blocking_eligible"},
        )
        criterion_id = _string(p["criterion_id"], f"{path}.selected_criteria[{index}].criterion_id")
        if CRITERION_ID_RE.fullmatch(criterion_id) is None:
            _fail(f"{path}.selected_criteria[{index}].criterion_id", "invalid criterion id")
        _string(p["criterion_version"], f"{path}.selected_criteria[{index}].criterion_version")
        _sha(p["criterion_digest"], f"{path}.selected_criteria[{index}].criterion_digest")
        if p["dimension"] not in DIMENSIONS:
            _fail(f"{path}.selected_criteria[{index}].dimension", "invalid dimension")
        if type(p["blocking_eligible"]) is not bool:
            _fail(f"{path}.selected_criteria[{index}].blocking_eligible", "must be boolean")
        pointer_ids.append(criterion_id)
    if pointer_ids != ids:
        _fail(path, "selected criterion ids and pointers must have identical order")
    if not isinstance(obj["parallel_conflicts"], list):
        _fail(f"{path}.parallel_conflicts", "must be an array")
    for index, item in enumerate(obj["parallel_conflicts"]):
        c = _object(item, f"{path}.parallel_conflicts[{index}]", {"conflict_group", "criterion_ids"})
        _string(c["conflict_group"], f"{path}.parallel_conflicts[{index}].conflict_group")
        conflict_ids = _criterion_ids(c["criterion_ids"], f"{path}.parallel_conflicts[{index}].criterion_ids")
        if len(conflict_ids) < 2 or not set(conflict_ids) <= set(ids):
            _fail(f"{path}.parallel_conflicts[{index}]", "must name two or more selected criteria")
    if not isinstance(obj["unresolved"], list):
        _fail(f"{path}.unresolved", "must be an array")
    for index, item in enumerate(obj["unresolved"]):
        u = _object(item, f"{path}.unresolved[{index}]", {"code", "dimension"})
        _string(u["code"], f"{path}.unresolved[{index}].code")
        if u["dimension"] not in DIMENSIONS:
            _fail(f"{path}.unresolved[{index}].dimension", "invalid dimension")
    return obj


def _validate_manifest(value: dict[str, Any], *, require_complete: bool = False) -> None:
    obj = _object(
        value,
        "manifest",
        {"schema_version", "target_review_id", "context_authority", "predecessor", "receipts", "manifest_digest"},
    )
    if obj["schema_version"] != SCHEMA_VERSION:
        _fail("manifest.schema_version", f"must equal {SCHEMA_VERSION}")
    _id(obj["target_review_id"], "manifest.target_review_id")
    authority = _validate_authority(obj["context_authority"], "manifest.context_authority")
    predecessor = obj["predecessor"]
    if predecessor is not None:
        p = _object(predecessor, "manifest.predecessor", {"target_review_id", "resolved_digest", "comparability"})
        _id(p["target_review_id"], "manifest.predecessor.target_review_id")
        _sha(p["resolved_digest"], "manifest.predecessor.resolved_digest")
        if p["target_review_id"] == obj["target_review_id"]:
            _fail("manifest.predecessor.target_review_id", "must identify a different target review")
        if p["comparability"] != "new_target_review_not_comparable":
            _fail("manifest.predecessor.comparability", "invalid comparability state")
    if not isinstance(obj["receipts"], list) or len(obj["receipts"]) > 3:
        _fail("manifest.receipts", "must be an array with at most three receipts")
    seen: list[str] = []
    for index, item in enumerate(obj["receipts"]):
        path = f"manifest.receipts[{index}]"
        receipt = _object(
            item,
            path,
            {"consumer_id", "context_ref", "context_sha256", "resolved_digest", "selected_criterion_ids", "artifacts", "receipt_digest"},
        )
        consumer = receipt["consumer_id"]
        if consumer not in CONSUMERS:
            _fail(f"{path}.consumer_id", "invalid consumer")
        if consumer in seen:
            _fail("manifest.receipts", f"duplicate consumer: {consumer}")
        seen.append(consumer)
        for key in ("context_ref", "context_sha256", "resolved_digest", "selected_criterion_ids"):
            if receipt[key] != authority[key]:
                _fail(path, f"{key} does not match context authority")
        if not isinstance(receipt["artifacts"], list):
            _fail(f"{path}.artifacts", "must be an array")
        roles: list[str] = []
        for artifact_index, artifact in enumerate(receipt["artifacts"]):
            artifact_path = f"{path}.artifacts[{artifact_index}]"
            binding = _object(artifact, artifact_path, {"role", "artifact_ref", "artifact_sha256"})
            if binding["role"] not in ROLES[consumer]:
                _fail(f"{artifact_path}.role", "role is not legal for consumer")
            if binding["role"] in roles:
                _fail(f"{path}.artifacts", f"duplicate role: {binding['role']}")
            roles.append(binding["role"])
            _portable_ref(binding["artifact_ref"], f"{artifact_path}.artifact_ref")
            _sha(binding["artifact_sha256"], f"{artifact_path}.artifact_sha256")
        if tuple(roles) != ROLES[consumer]:
            _fail(f"{path}.artifacts", f"roles must be exactly {', '.join(ROLES[consumer])}")
        _sha(receipt["receipt_digest"], f"{path}.receipt_digest")
        if receipt["receipt_digest"] != _digest(_receipt_payload(receipt)):
            _fail(f"{path}.receipt_digest", "does not match receipt content")
    expected_order = [item for item in CONSUMERS if item in seen]
    if seen != expected_order:
        _fail("manifest.receipts", "receipts must use canonical consumer order")
    if require_complete and tuple(seen) != CONSUMERS:
        _fail("manifest.receipts", "all three consumer receipts are required")
    _sha(obj["manifest_digest"], "manifest.manifest_digest")
    if obj["manifest_digest"] != _digest(_manifest_payload(obj)):
        _fail("manifest.manifest_digest", "does not match manifest content")


def _render_marker(manifest: dict[str, Any], consumer: str, role: str) -> str:
    if consumer not in CONSUMERS or role not in ROLES[consumer]:
        raise BindingError(f"role {role!r} is not legal for consumer {consumer!r}")
    authority = manifest["context_authority"]
    ids = json.dumps(authority["selected_criterion_ids"], separators=(",", ":"))
    return "\n".join(
        [
            "[REVIEW-TARGET-BINDING v1]",
            f"target_review_id={manifest['target_review_id']}",
            f"consumer_id={consumer}",
            f"role={role}",
            f"context_ref={authority['context_ref']}",
            f"context_sha256={authority['context_sha256']}",
            f"resolved_digest={authority['resolved_digest']}",
            f"selected_criterion_ids={ids}",
            "[/REVIEW-TARGET-BINDING]",
        ]
    )


def _render_conflict_line(manifest: dict[str, Any]) -> str:
    conflicts = json.dumps(
        manifest["context_authority"]["parallel_conflicts"],
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return f"criteria_parallel_conflicts: {conflicts}"


def _write_all(fd: int, raw: bytes) -> None:
    view = memoryview(raw)
    while view:
        written = os.write(fd, view)
        if written <= 0:
            raise BindingError("atomic write made no progress")
        view = view[written:]


def _atomic_create(path: Path, value: dict[str, Any]) -> None:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2).encode("utf-8") + b"\n"
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        fd = os.open(path, flags, 0o600)
    except OSError as exc:
        raise BindingError(f"cannot create output {path}: {exc}") from exc
    try:
        _write_all(fd, raw)
        os.fsync(fd)
        if os.fstat(fd).st_size != len(raw):
            raise BindingError(f"short atomic create for {path}")
    except Exception:
        try:
            path.unlink()
        except OSError:
            pass
        raise
    finally:
        os.close(fd)


def _atomic_replace(path: Path, value: dict[str, Any]) -> None:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2).encode("utf-8") + b"\n"
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temp = Path(temp_name)
    try:
        os.fchmod(fd, 0o600)
        _write_all(fd, raw)
        os.fsync(fd)
        if os.fstat(fd).st_size != len(raw):
            raise BindingError(f"short atomic replace for {path}")
        os.close(fd)
        fd = -1
        os.replace(temp, path)
    finally:
        if fd >= 0:
            os.close(fd)
        try:
            temp.unlink()
        except FileNotFoundError:
            pass


@contextmanager
def _locked(path: Path) -> Iterator[None]:
    lock_path = path.with_name(f".{path.name}.lock")
    flags = os.O_RDWR | os.O_CREAT
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        fd = os.open(lock_path, flags, 0o600)
    except OSError as exc:
        raise BindingError(f"cannot open lock {lock_path}: {exc}") from exc
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


def init_manifest(args: argparse.Namespace) -> int:
    context, context_raw = _read_json(args.context)
    registry, registry_raw = _read_json(args.registry)
    _validate_context_pair(context, registry)
    authority = _authority(
        context,
        context_raw,
        registry_raw,
        args.context_ref,
        args.registry_ref,
    )
    predecessor = None
    if args.prior_manifest is not None:
        prior, _ = _read_json(args.prior_manifest)
        _validate_manifest(prior)
        if prior["target_review_id"] == args.target_review_id:
            if prior["context_authority"] != authority:
                raise ConflictError(
                    "same target_review_id cannot bind a changed review target"
                )
        else:
            predecessor = {
                "target_review_id": prior["target_review_id"],
                "resolved_digest": prior["context_authority"]["resolved_digest"],
                "comparability": "new_target_review_not_comparable",
            }
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "target_review_id": _id(args.target_review_id, "target_review_id"),
        "context_authority": authority,
        "predecessor": predecessor,
        "receipts": [],
        "manifest_digest": "",
    }
    manifest["manifest_digest"] = _digest(_manifest_payload(manifest))
    _validate_manifest(manifest)
    _atomic_create(args.output, manifest)
    return 0


def marker(args: argparse.Namespace) -> int:
    manifest, _ = _read_json(args.manifest)
    _validate_manifest(manifest)
    sys.stdout.write(_render_marker(manifest, args.consumer, args.role) + "\n")
    return 0


def _artifact_specs(values: list[str], consumer: str, manifest: dict[str, Any]) -> list[dict[str, str]]:
    parsed: dict[str, str] = {}
    for value in values:
        if "=" not in value:
            raise BindingError("--artifact must use ROLE=portable/path syntax")
        role, ref = value.split("=", 1)
        if role in parsed:
            raise BindingError(f"duplicate artifact role: {role}")
        _portable_ref(ref, f"artifact[{role}]")
        parsed[role] = ref
    if tuple(parsed) != ROLES[consumer]:
        raise BindingError(
            f"{consumer} artifacts must be ordered exactly: {', '.join(ROLES[consumer])}"
        )
    result = []
    for role, ref in parsed.items():
        raw = _read_bytes(Path(ref), MAX_ARTIFACT_BYTES)
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise BindingError(f"artifact is not UTF-8 text: {ref}") from exc
        expected = _render_marker(manifest, consumer, role)
        expected_conflicts = _render_conflict_line(manifest)
        if (
            text.count(expected) != 1
            or text.count("[REVIEW-TARGET-BINDING v1]") != 1
            or text.count("[/REVIEW-TARGET-BINDING]") != 1
            or text.splitlines().count(expected_conflicts) != 1
        ):
            raise BindingError(
                f"artifact {ref} must contain exactly one exact binding marker "
                "and parallel-conflict line"
            )
        result.append(
            {
                "role": role,
                "artifact_ref": ref,
                "artifact_sha256": hashlib.sha256(raw).hexdigest(),
            }
        )
    return result


def record_receipt(args: argparse.Namespace) -> int:
    with _locked(args.manifest):
        manifest, _ = _read_json(args.manifest)
        _validate_manifest(manifest)
        artifacts = _artifact_specs(args.artifact, args.consumer, manifest)
        authority = manifest["context_authority"]
        receipt = {
            "consumer_id": args.consumer,
            "context_ref": authority["context_ref"],
            "context_sha256": authority["context_sha256"],
            "resolved_digest": authority["resolved_digest"],
            "selected_criterion_ids": authority["selected_criterion_ids"],
            "artifacts": artifacts,
            "receipt_digest": "",
        }
        receipt["receipt_digest"] = _digest(_receipt_payload(receipt))
        current = next(
            (item for item in manifest["receipts"] if item["consumer_id"] == args.consumer),
            None,
        )
        if current is not None:
            if current == receipt:
                return 0
            raise ConflictError(
                f"consumer {args.consumer} already has a different receipt"
            )
        manifest["receipts"].append(receipt)
        manifest["receipts"].sort(key=lambda item: CONSUMERS.index(item["consumer_id"]))
        manifest["manifest_digest"] = _digest(_manifest_payload(manifest))
        _validate_manifest(manifest)
        _atomic_replace(args.manifest, manifest)
    return 0


def validate_manifest_command(args: argparse.Namespace) -> int:
    manifest, _ = _read_json(args.manifest)
    context, context_raw = _read_json(args.context)
    registry, registry_raw = _read_json(args.registry)
    _validate_context_pair(context, registry)
    _validate_manifest(manifest, require_complete=args.require_complete)
    expected = _authority(
        context,
        context_raw,
        registry_raw,
        manifest["context_authority"]["context_ref"],
        manifest["context_authority"]["registry_ref"],
    )
    if manifest["context_authority"] != expected:
        raise BindingError("manifest context authority does not match explicit inputs")
    return 0


def _validate_anchor(value: Any, path: str) -> None:
    if not isinstance(value, dict):
        _fail(path, "must be an object")
    allowed = {"anchor_type", "locator", "quote", "absence_scope", "check_performed"}
    if set(value) - allowed:
        _fail(path, f"undeclared field(s): {', '.join(sorted(set(value) - allowed))}")
    if set(value) < {"anchor_type", "locator"}:
        _fail(path, "anchor_type and locator are required")
    anchor_type = value["anchor_type"]
    if anchor_type not in ANCHOR_TYPES:
        _fail(f"{path}.anchor_type", "invalid anchor type")
    _string(value["locator"], f"{path}.locator")
    extras = set(value) - {"anchor_type", "locator"}
    if anchor_type == "text":
        if extras != {"quote"}:
            _fail(path, "text anchor requires only quote")
        quote = _string(value["quote"], f"{path}.quote")
        if len(quote.split()) > 25:
            _fail(f"{path}.quote", "must contain at most 25 whitespace-delimited words")
    elif anchor_type == "absence":
        if extras != {"absence_scope", "check_performed"}:
            _fail(path, "absence anchor requires only absence_scope and check_performed")
        _string(value["absence_scope"], f"{path}.absence_scope")
        _string(value["check_performed"], f"{path}.check_performed")
    elif extras:
        _fail(path, "non-text/non-absence anchor has undeclared conditional fields")


def _validate_option(value: Any, path: str) -> None:
    obj = _object(
        value,
        path,
        {"action", "resource_effort", "trade_offs", "changes_research_intent", "requires_new_data", "proposed_result_values"},
    )
    _string(obj["action"], f"{path}.action")
    effort = _object(obj["resource_effort"], f"{path}.resource_effort", {"scope", "description"})
    if effort["scope"] not in OPTION_SCOPES:
        _fail(f"{path}.resource_effort.scope", "invalid effort scope")
    _string(effort["description"], f"{path}.resource_effort.description")
    _string(obj["trade_offs"], f"{path}.trade_offs")
    if obj["changes_research_intent"] not in INTENT_STATES:
        _fail(f"{path}.changes_research_intent", "invalid author-intent state")
    if type(obj["requires_new_data"]) is not bool:
        _fail(f"{path}.requires_new_data", "must be boolean")
    if (effort["scope"] == "new_data") != obj["requires_new_data"]:
        _fail(path, "new_data scope and requires_new_data must agree")
    if obj["proposed_result_values"] is not False:
        _fail(f"{path}.proposed_result_values", "must equal false")


def _validate_findings(value: dict[str, Any], manifest: dict[str, Any],
                       registry: dict[str, Any]) -> None:
    obj = _object(
        value,
        "findings",
        {"schema_version", "target_review_id", "resolved_digest", "selected_criterion_ids", "findings"},
    )
    if obj["schema_version"] != FINDINGS_VERSION:
        _fail("findings.schema_version", f"must equal {FINDINGS_VERSION}")
    authority = manifest["context_authority"]
    for key in ("target_review_id", "resolved_digest", "selected_criterion_ids"):
        expected = manifest["target_review_id"] if key == "target_review_id" else authority[key]
        if obj[key] != expected:
            _fail(f"findings.{key}", "does not match binding manifest")
    if not isinstance(obj["findings"], list):
        _fail("findings.findings", "must be an array")
    pointer_by_id = {item["criterion_id"]: item for item in authority["selected_criteria"]}
    seen: set[str] = set()
    for index, item in enumerate(obj["findings"]):
        path = f"findings.findings[{index}]"
        finding = _object(
            item,
            path,
            {
                "finding_id", "consumer_id", "reviewer_id", "severity",
                "criterion_refs", "evidence_anchor", "scholarly_relevance",
                "confirmed_target_relevance", "remedy_status",
                "minimum_viable_remedy", "stronger_option",
                "stronger_option_reason", "no_honest_remedy_reason",
            },
        )
        finding_id = _id(finding["finding_id"], f"{path}.finding_id")
        if finding_id in seen:
            _fail("findings.findings", f"duplicate finding_id: {finding_id}")
        seen.add(finding_id)
        consumer = finding["consumer_id"]
        reviewer = finding["reviewer_id"]
        if consumer == "internal_evaluator":
            if reviewer != "INTERNAL":
                _fail(f"{path}.reviewer_id", "internal evaluator requires INTERNAL")
        elif consumer == "external_panel":
            if reviewer not in ROLES["external_panel"]:
                _fail(f"{path}.reviewer_id", "invalid external-panel role")
        else:
            _fail(f"{path}.consumer_id", "invalid finding consumer")
        if finding["severity"] not in ("critical", "major"):
            _fail(f"{path}.severity", "sidecar accepts only critical or major")
        refs = finding["criterion_refs"]
        if not isinstance(refs, list) or not refs:
            _fail(f"{path}.criterion_refs", "must be a non-empty array")
        ref_ids: set[str] = set()
        blocking = False
        for ref_index, ref_value in enumerate(refs):
            ref_path = f"{path}.criterion_refs[{ref_index}]"
            ref = _object(ref_value, ref_path, {"criterion_id", "criterion_version", "criterion_digest"})
            criterion_id = _string(ref["criterion_id"], f"{ref_path}.criterion_id")
            if criterion_id in ref_ids:
                _fail(f"{path}.criterion_refs", f"duplicate criterion: {criterion_id}")
            ref_ids.add(criterion_id)
            pointer = pointer_by_id.get(criterion_id)
            if pointer is None:
                _fail(ref_path, "criterion is not selected in the active context")
            if ref != {key: pointer[key] for key in ("criterion_id", "criterion_version", "criterion_digest")}:
                _fail(ref_path, "criterion pointer does not match active context")
            blocking = blocking or pointer["blocking_eligible"]
        if not blocking:
            _fail(f"{path}.criterion_refs", "Critical/Major finding needs a blocking-eligible criterion")
        _validate_anchor(finding["evidence_anchor"], f"{path}.evidence_anchor")
        _string(finding["scholarly_relevance"], f"{path}.scholarly_relevance")
        target = _object(
            finding["confirmed_target_relevance"],
            f"{path}.confirmed_target_relevance",
            {"status", "rationale"},
        )
        if target["status"] not in ("confirmed", "not_applicable", "unresolved"):
            _fail(f"{path}.confirmed_target_relevance.status", "invalid status")
        _string(target["rationale"], f"{path}.confirmed_target_relevance.rationale")
        remedy_status = finding["remedy_status"]
        if remedy_status == "available":
            if finding["minimum_viable_remedy"] is None:
                _fail(f"{path}.minimum_viable_remedy", "required when remedy is available")
            _validate_option(finding["minimum_viable_remedy"], f"{path}.minimum_viable_remedy")
            if finding["no_honest_remedy_reason"] is not None:
                _fail(f"{path}.no_honest_remedy_reason", "must be null when remedy is available")
        elif remedy_status == "none":
            if finding["minimum_viable_remedy"] is not None or finding["stronger_option"] is not None:
                _fail(path, "no-honest-remedy finding cannot carry remedy options")
            _string(finding["no_honest_remedy_reason"], f"{path}.no_honest_remedy_reason")
        else:
            _fail(f"{path}.remedy_status", "invalid remedy status")
        if finding["stronger_option"] is None:
            _string(finding["stronger_option_reason"], f"{path}.stronger_option_reason")
        else:
            if remedy_status != "available":
                _fail(f"{path}.stronger_option", "requires an available minimum remedy")
            _validate_option(finding["stronger_option"], f"{path}.stronger_option")
            if finding["stronger_option_reason"] is not None:
                _fail(f"{path}.stronger_option_reason", "must be null when stronger option exists")
    rendered = _canonical_bytes(value).decode("utf-8")
    for row in registry["criteria"]:
        for field in ("title", "statement"):
            prose = row.get(field)
            if isinstance(prose, str) and prose and prose in rendered:
                raise BindingError(
                    f"findings copy criterion {field} for {row['criterion_id']}; "
                    "use pointers only"
                )


def validate_findings_command(args: argparse.Namespace) -> int:
    manifest, _ = _read_json(args.manifest)
    context, context_raw = _read_json(args.context)
    registry, registry_raw = _read_json(args.registry)
    findings, _ = _read_json(args.findings)
    _validate_context_pair(context, registry)
    _validate_manifest(manifest, require_complete=args.require_complete)
    expected = _authority(
        context,
        context_raw,
        registry_raw,
        manifest["context_authority"]["context_ref"],
        manifest["context_authority"]["registry_ref"],
    )
    if manifest["context_authority"] != expected:
        raise BindingError("manifest context authority does not match explicit inputs")
    _validate_findings(findings, manifest, registry)
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="create a new binding manifest")
    init.add_argument("--context", required=True, type=Path)
    init.add_argument("--context-ref", required=True)
    init.add_argument("--registry", required=True, type=Path)
    init.add_argument("--registry-ref", required=True)
    init.add_argument("--target-review-id", required=True)
    init.add_argument("--prior-manifest", type=Path)
    init.add_argument("--output", required=True, type=Path)
    init.set_defaults(func=init_manifest)

    mark = sub.add_parser("marker", help="render one exact consumer marker")
    mark.add_argument("--manifest", required=True, type=Path)
    mark.add_argument("--consumer", required=True, choices=CONSUMERS)
    mark.add_argument("--role", required=True)
    mark.set_defaults(func=marker)

    record = sub.add_parser("record", help="record one complete consumer receipt")
    record.add_argument("--manifest", required=True, type=Path)
    record.add_argument("--consumer", required=True, choices=CONSUMERS)
    record.add_argument("--artifact", action="append", required=True)
    record.set_defaults(func=record_receipt)

    validate = sub.add_parser("validate", help="validate authority and receipts")
    validate.add_argument("--manifest", required=True, type=Path)
    validate.add_argument("--context", required=True, type=Path)
    validate.add_argument("--registry", required=True, type=Path)
    validate.add_argument("--require-complete", action="store_true")
    validate.set_defaults(func=validate_manifest_command)

    findings = sub.add_parser("validate-findings", help="validate constructive finding sidecar")
    findings.add_argument("--manifest", required=True, type=Path)
    findings.add_argument("--context", required=True, type=Path)
    findings.add_argument("--registry", required=True, type=Path)
    findings.add_argument("--findings", required=True, type=Path)
    findings.add_argument("--require-complete", action="store_true")
    findings.set_defaults(func=validate_findings_command)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        return args.func(args)
    except ConflictError as exc:
        print(f"review-criteria binding conflict: {exc}", file=sys.stderr)
        return 3
    except BindingError as exc:
        print(f"review-criteria binding failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
