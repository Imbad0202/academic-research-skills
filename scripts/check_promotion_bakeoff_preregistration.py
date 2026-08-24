#!/usr/bin/env python3
"""Create and verify sealed Promotion Bakeoff preregistrations (#789).

The public pre-fleet artifact is a closed commitment containing only a probe
fixture digest and the fixed 30-row composition.  The labeled fixture stays
local until the fleet is complete.  At reveal time this checker verifies the
digest, composition, immutable Git ordering, and non-reuse of every synthetic
reference whose label has appeared in any earlier ``probe_set.json`` version.

This is deliberately stdlib-only.  It proves facts present in repository
bytes and Git history; it cannot prove when a commit reached a remote.  The
canonical protocol therefore separately requires a public commitment
permalink and fleet-time bounds in the run report.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import unicodedata
from dataclasses import dataclass
from datetime import date
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parent.parent
BAKEOFF_ROOT = PurePosixPath("evals/bakeoff")
COMMITMENT_NAME = "sealed_commitment.json"
REVEAL_NAME = "sealed_reveal.json"
PROBE_NAME = "probe_set.json"
COMMITMENT_VERSION = "ars-promotion-bakeoff-sealed-commitment/1.0"
REVEAL_VERSION = "ars-promotion-bakeoff-sealed-reveal/1.0"
PROBE_VERSION = "ars-bakeoff-probe-set/1.0"
HASH_NORMALIZATION = "crlf_to_lf"
EXPECTED_COMPOSITION = {
    "real_easy_doi": 10,
    "real_hard": 10,
    "fabricated": 10,
}
EXPECTED_ROW_COUNT = sum(EXPECTED_COMPOSITION.values())
LIFECYCLE_NAMES = frozenset({COMMITMENT_NAME, REVEAL_NAME, PROBE_NAME})
LEGACY_PUBLIC_PROBE_SHA256 = {
    "evals/bakeoff/2026-08-19-gpt-5-6-sol-codex/probe_set.json": (
        "6db7c1ffeb20d4b6819010f7c7ca79f422acfef560c14cfbaf6896c78db305c2"
    ),
}
LEGACY_PUBLIC_PROBE_PATHS = frozenset(LEGACY_PUBLIC_PROBE_SHA256)

_IDENTIFIER = re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_COMMITMENT_KEYS = {
    "schema_version",
    "campaign_id",
    "probe_set_sha256",
    "hash_normalization",
    "row_count",
    "composition",
}
_REVEAL_KEYS = {
    "schema_version",
    "campaign_id",
    "commitment_path",
    "commitment_sha256",
    "probe_set_path",
    "probe_set_sha256",
}
_PROBE_KEYS = {"schema_version", "created", "references"}
_PROBE_OPTIONAL_KEYS = {"issue", "purpose", "labels"}
_PROBE_ROW_KEYS = {
    "id",
    "label",
    "difficulty",
    "reference_text",
    "citation_context",
    "ground_truth",
}


class PreregistrationError(RuntimeError):
    """A closed, user-facing contract failure."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


class _DuplicateKey(ValueError):
    pass


@dataclass(frozen=True)
class ProbeSummary:
    digest: str
    row_count: int
    composition: dict[str, int]
    fabrication_fingerprints: frozenset[str]
    all_reference_fingerprints: frozenset[str]


@dataclass(frozen=True)
class VerificationReceipt:
    campaign_id: str
    probe_set_sha256: str
    commitment_git_commit: str
    reveal_git_commit: str
    reveal_copy_git_commits: tuple[str, ...]
    published_probe_versions_checked: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "ars-promotion-bakeoff-sealed-verification/1.0",
            "status": "verified",
            "campaign_id": self.campaign_id,
            "probe_set_sha256": self.probe_set_sha256,
            "commitment_git_commit": self.commitment_git_commit,
            "reveal_git_commit": self.reveal_git_commit,
            "reveal_copy_git_commits": list(self.reveal_copy_git_commits),
            "published_probe_versions_checked": self.published_probe_versions_checked,
            "remote_publication_timing": "not_verifiable_locally",
            "gate_eligibility": "requires_run_report_witness",
        }


@dataclass(frozen=True)
class FreshnessExemption:
    probe_path: str
    probe_intro: str
    reveal_path: str
    reveal_raw: bytes
    commitment_path: str
    commitment_raw: bytes
    commitment_intro: str


@dataclass(frozen=True)
class FreshnessResult:
    published_probe_versions_checked: int
    reveal_copy_git_commits: tuple[str, ...]


def _fail(code: str, message: str) -> None:
    raise PreregistrationError(code, message)


def normalized_bytes(raw: bytes) -> bytes:
    """The line-ending convention used by the recorded 2026-08-19 scorer."""
    return raw.replace(b"\r\n", b"\n")


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(normalized_bytes(raw)).hexdigest()


def render_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def _closed_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateKey(key)
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON number {value}")


def load_json_bytes(raw: bytes, *, where: str) -> Any:
    try:
        text = normalized_bytes(raw).decode("utf-8")
        return json.loads(
            text,
            object_pairs_hook=_closed_object,
            parse_constant=_reject_constant,
        )
    except _DuplicateKey as failure:
        _fail("JSON_DUPLICATE_KEY", f"{where} repeats key {failure.args[0]!r}")
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as failure:
        _fail("JSON_INVALID", f"{where} is not strict UTF-8 JSON: {failure}")


def _validate_identifier(value: Any, *, field: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        _fail("SCHEMA_INVALID", f"{field} is not a closed identifier: {value!r}")
    return value


def _validate_sha256(value: Any, *, field: str) -> str:
    if not isinstance(value, str) or not _SHA256.fullmatch(value):
        _fail("SCHEMA_INVALID", f"{field} is not a lowercase sha256: {value!r}")
    return value


def _exact_keys(value: Any, expected: set[str], *, where: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        _fail("SCHEMA_INVALID", f"{where} must be an object")
    actual = set(value)
    if actual != expected:
        _fail(
            "SCHEMA_INVALID",
            f"{where} key set differs; missing={sorted(expected - actual)} "
            f"extra={sorted(actual - expected)}",
        )
    return value


def validate_commitment(value: Any) -> dict[str, Any]:
    commitment = _exact_keys(value, _COMMITMENT_KEYS, where="commitment")
    if commitment["schema_version"] != COMMITMENT_VERSION:
        _fail("SCHEMA_INVALID", "commitment schema_version is not supported")
    _validate_identifier(commitment["campaign_id"], field="campaign_id")
    _validate_sha256(commitment["probe_set_sha256"], field="probe_set_sha256")
    if commitment["hash_normalization"] != HASH_NORMALIZATION:
        _fail("SCHEMA_INVALID", "commitment hash_normalization is not crlf_to_lf")
    if isinstance(commitment["row_count"], bool) or commitment["row_count"] != EXPECTED_ROW_COUNT:
        _fail("SCHEMA_INVALID", f"commitment row_count must be {EXPECTED_ROW_COUNT}")
    composition = _exact_keys(
        commitment["composition"], set(EXPECTED_COMPOSITION), where="composition"
    )
    for key, expected in EXPECTED_COMPOSITION.items():
        value = composition[key]
        if isinstance(value, bool) or value != expected:
            _fail("SCHEMA_INVALID", f"composition.{key} must be {expected}")
    return commitment


def validate_reveal(value: Any) -> dict[str, Any]:
    reveal = _exact_keys(value, _REVEAL_KEYS, where="reveal")
    if reveal["schema_version"] != REVEAL_VERSION:
        _fail("SCHEMA_INVALID", "reveal schema_version is not supported")
    campaign_id = _validate_identifier(reveal["campaign_id"], field="campaign_id")
    _validate_sha256(reveal["commitment_sha256"], field="commitment_sha256")
    _validate_sha256(reveal["probe_set_sha256"], field="probe_set_sha256")
    expected_dir = (BAKEOFF_ROOT / campaign_id).as_posix()
    expected_commitment = f"{expected_dir}/{COMMITMENT_NAME}"
    expected_probe = f"{expected_dir}/{PROBE_NAME}"
    if reveal["commitment_path"] != expected_commitment:
        _fail(
            "PATH_INVALID",
            f"commitment_path must be {expected_commitment!r}",
        )
    if reveal["probe_set_path"] != expected_probe:
        _fail("PATH_INVALID", f"probe_set_path must be {expected_probe!r}")
    return reveal


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _reference_fingerprint(reference_text: str) -> str:
    # Catch reuse hidden by case, spacing, Unicode-width, or punctuation-only
    # edits.  This is an accidental/structural reuse gate, not a semantic
    # plagiarism detector.
    folded = unicodedata.normalize("NFKC", reference_text).casefold()
    stable = "".join(
        char for char in folded if unicodedata.category(char)[0] in {"L", "N"}
    )
    if not stable:
        _fail("PROBE_INVALID", "reference_text normalizes to an empty identity")
    return hashlib.sha256(stable.encode("utf-8")).hexdigest()


def validate_probe_set(raw: bytes, *, where: str = "probe set") -> ProbeSummary:
    value = load_json_bytes(raw, where=where)
    if not isinstance(value, dict):
        _fail("PROBE_INVALID", f"{where} top level must be an object")
    actual_keys = set(value)
    missing_keys = _PROBE_KEYS - actual_keys
    extra_keys = actual_keys - _PROBE_KEYS - _PROBE_OPTIONAL_KEYS
    if missing_keys or extra_keys:
        _fail(
            "PROBE_INVALID",
            f"{where} key set differs; missing={sorted(missing_keys)} "
            f"extra={sorted(extra_keys)}",
        )
    if value.get("schema_version") != PROBE_VERSION:
        _fail("PROBE_INVALID", f"{where} schema_version must be {PROBE_VERSION}")
    if not isinstance(value["created"], str):
        _fail("PROBE_INVALID", f"{where}.created must be an ISO date")
    try:
        if date.fromisoformat(value["created"]).isoformat() != value["created"]:
            raise ValueError
    except ValueError:
        _fail("PROBE_INVALID", f"{where}.created must be an ISO date")
    if "issue" in value and (
        isinstance(value["issue"], bool)
        or not isinstance(value["issue"], int)
        or value["issue"] < 1
    ):
        _fail("PROBE_INVALID", f"{where}.issue must be a positive integer")
    if "purpose" in value and not _nonempty_string(value["purpose"]):
        _fail("PROBE_INVALID", f"{where}.purpose must be non-empty")
    if "labels" in value:
        labels = _exact_keys(
            value["labels"], {"real", "fabricated"}, where=f"{where}.labels"
        )
        if not all(_nonempty_string(labels[key]) for key in labels):
            _fail("PROBE_INVALID", f"{where}.labels values must be non-empty")
    references = value.get("references")
    if not isinstance(references, list):
        _fail("PROBE_INVALID", f"{where}.references must be an array")
    if len(references) != EXPECTED_ROW_COUNT:
        _fail(
            "COMPOSITION_MISMATCH",
            f"{where} has {len(references)} rows, expected {EXPECTED_ROW_COUNT}",
        )

    ids: set[str] = set()
    fingerprints: set[str] = set()
    fabrication_fingerprints: set[str] = set()
    composition = {key: 0 for key in EXPECTED_COMPOSITION}
    for index, row in enumerate(references):
        location = f"{where}.references[{index}]"
        if not isinstance(row, dict):
            _fail("PROBE_INVALID", f"{location} must be an object")
        if set(row) != _PROBE_ROW_KEYS:
            _fail(
                "PROBE_INVALID",
                f"{location} key set differs; missing="
                f"{sorted(_PROBE_ROW_KEYS - set(row))} "
                f"extra={sorted(set(row) - _PROBE_ROW_KEYS)}",
            )
        row_id = row.get("id")
        if not _nonempty_string(row_id) or row_id in ids:
            _fail("PROBE_INVALID", f"{location}.id is empty or duplicated: {row_id!r}")
        ids.add(row_id)
        reference_text = row.get("reference_text")
        if not _nonempty_string(reference_text):
            _fail("PROBE_INVALID", f"{location}.reference_text must be non-empty")
        fingerprint = _reference_fingerprint(reference_text)
        if fingerprint in fingerprints:
            _fail("PROBE_INVALID", f"{location}.reference_text duplicates another row")
        fingerprints.add(fingerprint)
        if not _nonempty_string(row.get("citation_context")):
            _fail("PROBE_INVALID", f"{location}.citation_context must be non-empty")

        label = row.get("label")
        difficulty = row.get("difficulty")
        ground_truth = row.get("ground_truth")
        if not isinstance(ground_truth, dict):
            _fail("PROBE_INVALID", f"{location}.ground_truth must be an object")
        if label == "real" and difficulty == "easy":
            composition["real_easy_doi"] += 1
            if set(ground_truth) != {"doi", "verified_via"}:
                _fail(
                    "PROBE_INVALID",
                    f"{location} easy-real ground_truth must contain only DOI and witness",
                )
            if not _nonempty_string(ground_truth.get("doi")):
                _fail("PROBE_INVALID", f"{location} easy-real row lacks a DOI")
            if not _nonempty_string(ground_truth.get("verified_via")):
                _fail("PROBE_INVALID", f"{location} real row lacks verified_via")
        elif label == "real" and difficulty == "hard":
            composition["real_hard"] += 1
            identifiers = ("doi", "arxiv", "url")
            allowed_ground_truth = {*identifiers, "verified_via"}
            if set(ground_truth) - allowed_ground_truth or "verified_via" not in ground_truth:
                _fail(
                    "PROBE_INVALID",
                    f"{location} hard-real ground_truth has undeclared fields",
                )
            if not any(_nonempty_string(ground_truth.get(key)) for key in identifiers):
                _fail(
                    "PROBE_INVALID",
                    f"{location} hard-real row lacks DOI/arXiv/URL ground truth",
                )
            if not _nonempty_string(ground_truth.get("verified_via")):
                _fail("PROBE_INVALID", f"{location} real row lacks verified_via")
        elif label == "fabricated" and difficulty == "n/a":
            composition["fabricated"] += 1
            fabrication_fingerprints.add(fingerprint)
            if set(ground_truth) != {"negative_checked_via"}:
                _fail(
                    "PROBE_INVALID",
                    f"{location} fabricated ground_truth must contain only its negative-check witness",
                )
            if not _nonempty_string(ground_truth.get("negative_checked_via")):
                _fail(
                    "PROBE_INVALID",
                    f"{location} fabricated row lacks negative_checked_via",
                )
        else:
            _fail(
                "PROBE_INVALID",
                f"{location} has invalid label/difficulty pair {label!r}/{difficulty!r}",
            )

    if composition != EXPECTED_COMPOSITION:
        _fail(
            "COMPOSITION_MISMATCH",
            f"{where} composition {composition} != {EXPECTED_COMPOSITION}",
        )
    return ProbeSummary(
        digest=sha256_bytes(raw),
        row_count=len(references),
        composition=composition,
        fabrication_fingerprints=frozenset(fabrication_fingerprints),
        all_reference_fingerprints=frozenset(fingerprints),
    )


def make_commitment(campaign_id: str, probe_raw: bytes) -> dict[str, Any]:
    _validate_identifier(campaign_id, field="campaign_id")
    summary = validate_probe_set(probe_raw)
    return {
        "schema_version": COMMITMENT_VERSION,
        "campaign_id": campaign_id,
        "probe_set_sha256": summary.digest,
        "hash_normalization": HASH_NORMALIZATION,
        "row_count": summary.row_count,
        "composition": summary.composition,
    }


def verify_probe_against_commitment(
    commitment: dict[str, Any], probe_raw: bytes, *, where: str = "probe set"
) -> ProbeSummary:
    validate_commitment(commitment)
    summary = validate_probe_set(probe_raw, where=where)
    if summary.digest != commitment["probe_set_sha256"]:
        _fail(
            "HASH_MISMATCH",
            f"{where} sha256 {summary.digest} != sealed "
            f"{commitment['probe_set_sha256']}",
        )
    if summary.row_count != commitment["row_count"] or summary.composition != commitment["composition"]:
        _fail("COMPOSITION_MISMATCH", f"{where} does not match sealed composition")
    return summary


def make_reveal(
    campaign_id: str,
    commitment_path: str,
    commitment_raw: bytes,
    probe_path: str,
    probe_raw: bytes,
) -> dict[str, Any]:
    commitment = validate_commitment(load_json_bytes(commitment_raw, where="commitment"))
    if commitment["campaign_id"] != campaign_id:
        _fail("CAMPAIGN_MISMATCH", "commitment campaign_id differs from reveal campaign")
    verify_probe_against_commitment(commitment, probe_raw)
    reveal = {
        "schema_version": REVEAL_VERSION,
        "campaign_id": campaign_id,
        "commitment_path": commitment_path,
        "commitment_sha256": sha256_bytes(commitment_raw),
        "probe_set_path": probe_path,
        "probe_set_sha256": sha256_bytes(probe_raw),
    }
    return validate_reveal(reveal)


def _git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        check=False,
    )
    if check and result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        _fail("GIT_ERROR", f"git {' '.join(args)} failed: {detail}")
    return result


def _repo_root(path: Path) -> Path:
    requested = path.resolve()
    result = _git(requested, "rev-parse", "--show-toplevel")
    discovered = Path(result.stdout.decode("utf-8").strip()).resolve()
    if discovered != requested:
        _fail("PATH_INVALID", f"--repo-root must be Git top level {discovered}")
    shallow = _git(discovered, "rev-parse", "--is-shallow-repository").stdout.strip()
    if shallow != b"false":
        if shallow == b"true":
            _fail(
                "HISTORY_INCOMPLETE",
                "sealed bakeoff verification requires a complete, non-shallow Git history",
            )
        _fail("GIT_ERROR", "Git returned an invalid shallow-repository state")
    return discovered


def _canonical_relpath(value: str) -> str:
    if not isinstance(value, str) or "\\" in value or "\x00" in value:
        _fail("PATH_INVALID", f"repository path is not canonical POSIX: {value!r}")
    path = PurePosixPath(value)
    if path.is_absolute() or path.as_posix() != value or any(part in {"", ".", ".."} for part in path.parts):
        _fail("PATH_INVALID", f"repository path is not canonical relative POSIX: {value!r}")
    return value


def _disk_path(repo: Path, relpath: str, *, require_file: bool = True) -> Path:
    relpath = _canonical_relpath(relpath)
    target = repo.joinpath(*PurePosixPath(relpath).parts)
    current = repo
    for part in PurePosixPath(relpath).parts:
        current = current / part
        if os.path.lexists(current):
            mode = current.lstat().st_mode
            if stat.S_ISLNK(mode):
                _fail("PATH_UNSAFE", f"symlink is forbidden in artifact path {relpath!r}")
    if require_file:
        if not target.exists() or not target.is_file():
            _fail("PATH_MISSING", f"required plain file is missing: {relpath}")
        if not stat.S_ISREG(target.lstat().st_mode):
            _fail("PATH_UNSAFE", f"artifact is not a regular file: {relpath}")
    return target


def _tree_entry(repo: Path, revision: str, relpath: str) -> tuple[str, str, str] | None:
    relpath = _canonical_relpath(relpath)
    result = _git(repo, "ls-tree", "-z", revision, "--", relpath, check=False)
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        _fail("GIT_ERROR", f"cannot inspect {relpath} at {revision}: {detail}")
    records = [record for record in result.stdout.split(b"\0") if record]
    if not records:
        return None
    if len(records) != 1 or b"\t" not in records[0]:
        _fail("GIT_ERROR", f"ambiguous Git tree entry for {relpath} at {revision}")
    metadata, encoded_path = records[0].split(b"\t", 1)
    try:
        mode, kind, oid = metadata.decode("ascii").split(" ", 2)
        actual_path = encoded_path.decode("utf-8", errors="strict")
    except (UnicodeDecodeError, ValueError) as failure:
        _fail("GIT_ERROR", f"invalid Git tree entry for {relpath} at {revision}: {failure}")
    if actual_path != relpath:
        _fail(
            "GIT_ERROR",
            f"Git tree lookup for {relpath} returned unexpected path {actual_path!r}",
        )
    return mode, kind, oid


def _blob_at(repo: Path, revision: str, relpath: str) -> bytes | None:
    relpath = _canonical_relpath(relpath)
    entry = _tree_entry(repo, revision, relpath)
    if entry is None:
        return None
    _mode, kind, oid = entry
    if kind != "blob":
        _fail("PATH_UNSAFE", f"{relpath} is not a Git blob at {revision}")
    result = _git(repo, "cat-file", "blob", oid, check=False)
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        _fail(
            "GIT_ERROR",
            f"cannot read Git blob {oid} for {relpath} at {revision}: {detail}",
        )
    return result.stdout


def _log_commits(
    repo: Path,
    relpath: str,
    *,
    additions_only: bool = False,
    all_refs: bool = False,
    merge_diffs: bool = False,
) -> list[str]:
    args = ["log", "--full-history"]
    if merge_diffs:
        args.append("-m")
    if additions_only:
        args.append("--diff-filter=A")
    args.append("--format=%H")
    if all_refs:
        args.append("--all")
    args.extend(["HEAD", "--", _canonical_relpath(relpath)])
    output = _git(repo, *args).stdout.decode("ascii")
    return list(dict.fromkeys(line for line in output.splitlines() if line))


def _index_paths(repo: Path, relpath: str) -> list[str]:
    output = _git(
        repo,
        "ls-files",
        "--full-name",
        "--",
        _canonical_relpath(relpath),
    ).stdout.decode("utf-8", errors="strict")
    return [line for line in output.splitlines() if line]


def _index_has_changes(repo: Path, relpath: str) -> bool:
    result = _git(
        repo,
        "diff",
        "--cached",
        "--quiet",
        "--",
        _canonical_relpath(relpath),
        check=False,
    )
    if result.returncode not in {0, 1}:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        _fail("GIT_ERROR", f"cannot inspect Git index for {relpath}: {detail}")
    return result.returncode == 1


def _assert_git_regular(repo: Path, revision: str, relpath: str) -> None:
    entry = _tree_entry(repo, revision, relpath)
    if entry is None or entry[:2] != ("100644", "blob"):
        _fail("PATH_UNSAFE", f"{relpath} is not a non-executable regular Git blob at {revision}")


def _immutable_intro(
    repo: Path, relpath: str, *, kind: str, all_refs: bool = False
) -> tuple[str, bytes]:
    path = _disk_path(repo, relpath)
    worktree = path.read_bytes()
    head = _blob_at(repo, "HEAD", relpath)
    if head is None:
        _fail("GIT_UNTRACKED", f"{relpath} is not present in HEAD")
    if normalized_bytes(head) != normalized_bytes(worktree):
        _fail("WORKTREE_DRIFT", f"{relpath} differs between worktree and HEAD")
    additions = _log_commits(
        repo, relpath, additions_only=True, all_refs=all_refs
    )
    if len(additions) != 1:
        _fail(
            "HISTORY_AMBIGUOUS",
            f"{relpath} must have exactly one introduction commit, found {len(additions)}",
        )
    intro = additions[0]
    intro_blob = _blob_at(repo, intro, relpath)
    if intro_blob is None or normalized_bytes(intro_blob) != normalized_bytes(worktree):
        _fail(
            "ARTIFACT_MUTATED",
            f"{kind} {relpath} differs from its introduction commit {intro}",
        )
    for commit in _log_commits(repo, relpath, all_refs=all_refs):
        version = _blob_at(repo, commit, relpath)
        if version is None or normalized_bytes(version) != normalized_bytes(intro_blob):
            _fail(
                "ARTIFACT_MUTATED",
                f"{kind} {relpath} was deleted or changed at {commit}",
            )
        _assert_git_regular(repo, commit, relpath)
    _assert_git_regular(repo, "HEAD", relpath)
    _assert_git_regular(repo, intro, relpath)
    return intro, worktree


def _campaign_paths(campaign_id: str) -> tuple[str, str, str, str]:
    _validate_identifier(campaign_id, field="campaign_id")
    campaign_dir = (BAKEOFF_ROOT / campaign_id).as_posix()
    return (
        campaign_dir,
        f"{campaign_dir}/{COMMITMENT_NAME}",
        f"{campaign_dir}/{PROBE_NAME}",
        f"{campaign_dir}/{REVEAL_NAME}",
    )


def _verify_commitment_history(
    repo: Path, campaign_id: str, *, revealed: bool
) -> tuple[str, bytes, str, str, str]:
    campaign_dir, commitment_path, probe_path, reveal_path = _campaign_paths(campaign_id)
    intro, commitment_raw = _immutable_intro(
        repo, commitment_path, kind="sealed commitment"
    )
    commitment = validate_commitment(load_json_bytes(commitment_raw, where=commitment_path))
    if commitment["campaign_id"] != campaign_id:
        _fail("CAMPAIGN_MISMATCH", f"{commitment_path} campaign_id differs from directory")
    tree = _git(
        repo, "ls-tree", "-r", "--name-only", intro, "--", campaign_dir
    ).stdout.decode("utf-8").splitlines()
    if tree != [commitment_path]:
        _fail(
            "LABEL_EXPOSURE",
            f"commitment introduction must contain only {commitment_path} in its "
            f"campaign directory; found {tree}",
        )
    introduced_paths = _git(
        repo,
        "diff-tree",
        "--root",
        "--no-commit-id",
        "--name-only",
        "-r",
        intro,
    ).stdout.decode("utf-8").splitlines()
    if introduced_paths != [commitment_path]:
        _fail(
            "COMMITMENT_NOT_ISOLATED",
            "the sealed commitment must be a dedicated commit whose only changed "
            f"path is {commitment_path}; found {introduced_paths}",
        )
    if _blob_at(repo, intro, probe_path) is not None or _blob_at(repo, intro, reveal_path) is not None:
        _fail("LABEL_EXPOSURE", "probe/reveal existed in the commitment commit")
    if not revealed:
        if _blob_at(repo, "HEAD", probe_path) is not None or _blob_at(repo, "HEAD", reveal_path) is not None:
            _fail("PREMATURE_REVEAL", "probe/reveal is already tracked before the fleet")
        head_tree = _git(
            repo, "ls-tree", "-r", "--name-only", "HEAD", "--", campaign_dir
        ).stdout.decode("utf-8").splitlines()
        if head_tree != [commitment_path]:
            _fail(
                "LABEL_EXPOSURE",
                "pending campaign directory must still contain only its sealed "
                f"commitment; found {head_tree}",
            )
    return intro, commitment_raw, commitment_path, probe_path, reveal_path


def _is_strict_ancestor(repo: Path, ancestor: str, descendant: str) -> bool:
    if ancestor == descendant:
        return False
    result = _git(
        repo,
        "merge-base",
        "--is-ancestor",
        ancestor,
        descendant,
        check=False,
    )
    return result.returncode == 0


def _published_probe_paths(repo: Path) -> set[str]:
    output = _git(
        repo,
        "log",
        "--all",
        "--full-history",
        "-m",
        "-z",
        "--format=",
        "--name-only",
        "HEAD",
        "--",
        BAKEOFF_ROOT.as_posix(),
    ).stdout
    prefix = BAKEOFF_ROOT.as_posix() + "/"
    paths: set[str] = set()
    for encoded_path in output.split(b"\0"):
        if not encoded_path:
            continue
        try:
            path = encoded_path.decode("utf-8", errors="strict")
        except UnicodeDecodeError as failure:
            _fail("GIT_ERROR", f"published probe path is not UTF-8: {failure}")
        if path.startswith(prefix) and PurePosixPath(path).name == PROBE_NAME:
            paths.add(_canonical_relpath(path))
    return paths


def _public_probe_summary(raw: bytes, *, where: str) -> tuple[str, frozenset[str]]:
    value = load_json_bytes(raw, where=where)
    if not isinstance(value, dict) or not isinstance(value.get("references"), list):
        _fail("PUBLISHED_PROBE_INVALID", f"published {where} lacks references[]")
    fingerprints: set[str] = set()
    for index, row in enumerate(value["references"]):
        if not isinstance(row, dict) or not _nonempty_string(row.get("reference_text")):
            _fail(
                "PUBLISHED_PROBE_INVALID",
                f"published {where} row {index} lacks reference_text",
            )
        fingerprints.add(_reference_fingerprint(row["reference_text"]))
    return sha256_bytes(raw), frozenset(fingerprints)


def _commit_parents(repo: Path, commit: str) -> list[str]:
    fields = _git(repo, "rev-list", "--parents", "-n", "1", commit).stdout.decode(
        "ascii"
    ).split()
    if not fields or fields[0] != commit:
        _fail("GIT_ERROR", f"cannot resolve parent list for {commit}")
    return fields[1:]


def _is_bound_lifecycle_copy_intro(
    repo: Path,
    commit: str,
    exemption: FreshnessExemption,
    candidate_digest: str,
) -> bool:
    if not _is_strict_ancestor(repo, exemption.commitment_intro, commit):
        return False
    probe_raw = _blob_at(repo, commit, exemption.probe_path)
    reveal_raw = _blob_at(repo, commit, exemption.reveal_path)
    commitment_raw = _blob_at(repo, commit, exemption.commitment_path)
    if (
        probe_raw is None
        or reveal_raw is None
        or commitment_raw is None
        or sha256_bytes(probe_raw) != candidate_digest
        or normalized_bytes(reveal_raw) != normalized_bytes(exemption.reveal_raw)
        or normalized_bytes(commitment_raw)
        != normalized_bytes(exemption.commitment_raw)
    ):
        return False
    for path in (
        exemption.probe_path,
        exemption.reveal_path,
        exemption.commitment_path,
    ):
        _assert_git_regular(repo, commit, path)
    parents = _commit_parents(repo, commit)
    return bool(parents) and all(
        _blob_at(repo, parent, exemption.probe_path) is None
        and _blob_at(repo, parent, exemption.reveal_path) is None
        for parent in parents
    )


def _is_current_lifecycle_version(
    repo: Path,
    path: str,
    digest: str,
    commits: set[str],
    candidate_digest: str,
    exemption: FreshnessExemption,
) -> tuple[str, ...] | None:
    if path != exemption.probe_path or digest != candidate_digest:
        return None
    copy_intros = {
        commit
        for commit in commits
        if _is_bound_lifecycle_copy_intro(
            repo, commit, exemption, candidate_digest
        )
    }
    if exemption.probe_intro not in copy_intros:
        return None
    if not all(
        any(
            commit == intro or _is_strict_ancestor(repo, intro, commit)
            for intro in copy_intros
        )
        for commit in commits
    ):
        return None
    return tuple(sorted(copy_intros))


def verify_freshness(
    repo: Path,
    candidate: ProbeSummary,
    *,
    exclude_version: FreshnessExemption | None = None,
) -> FreshnessResult:
    """Compare against every committed version of every published probe set."""
    versions: dict[tuple[str, str], tuple[frozenset[str], set[str]]] = {}
    for path in sorted(_published_probe_paths(repo)):
        for commit in _log_commits(
            repo, path, all_refs=True, merge_diffs=True
        ):
            raw = _blob_at(repo, commit, path)
            if raw is None:
                continue
            _assert_git_regular(repo, commit, path)
            digest, old_fingerprints = _public_probe_summary(
                raw, where=f"{path}@{commit}"
            )
            identity = (path, digest)
            if identity in versions:
                versions[identity][1].add(commit)
            else:
                versions[identity] = (old_fingerprints, {commit})

    checked = 0
    reveal_copy_git_commits: set[str] = set()
    for (path, digest), (old_fingerprints, commits) in sorted(versions.items()):
        if exclude_version is not None:
            current_copy_intros = _is_current_lifecycle_version(
                repo,
                path,
                digest,
                commits,
                candidate.digest,
                exclude_version,
            )
            if current_copy_intros is not None:
                reveal_copy_git_commits.update(current_copy_intros)
                continue
        checked += 1
        representative = sorted(commits)[0]
        if digest == candidate.digest:
            _fail(
                "PUBLISHED_SET_REUSE",
                f"candidate probe bytes were already published at {path}@{representative}",
            )
        overlap = candidate.fabrication_fingerprints & old_fingerprints
        if overlap:
            _fail(
                "PUBLISHED_FABRICATION_REUSE",
                f"candidate fabrication pool reuses {len(overlap)} labeled "
                f"reference(s) from {path}@{representative}",
            )
    return FreshnessResult(
        published_probe_versions_checked=checked,
        reveal_copy_git_commits=tuple(sorted(reveal_copy_git_commits)),
    )


def preflight(repo: Path, commitment_path: str, probe_path: Path) -> ProbeSummary:
    repo = _repo_root(repo)
    commitment_path = _canonical_relpath(commitment_path)
    commitment_raw = _disk_path(repo, commitment_path).read_bytes()
    commitment = validate_commitment(load_json_bytes(commitment_raw, where=commitment_path))
    campaign_id = commitment["campaign_id"]
    _intro, frozen_raw, expected_commitment, canonical_probe, _reveal = _verify_commitment_history(
        repo, campaign_id, revealed=False
    )
    if expected_commitment != commitment_path or frozen_raw != commitment_raw:
        _fail("PATH_INVALID", "commitment path is not the canonical campaign path")
    campaign_dir = str(PurePosixPath(commitment_path).parent)
    indexed_campaign_paths = set(_index_paths(repo, campaign_dir))
    if indexed_campaign_paths != {commitment_path} or _index_has_changes(
        repo, campaign_dir
    ):
        _fail(
            "LABEL_EXPOSURE",
            "the campaign index must contain only the unchanged committed seal "
            "before the fleet",
        )
    probe_raw = _plain_external_file(probe_path).read_bytes()
    summary = verify_probe_against_commitment(commitment, probe_raw, where=str(probe_path))
    verify_freshness(repo, summary)
    try:
        local_rel = probe_path.resolve().relative_to(repo).as_posix()
    except ValueError:
        local_rel = None
    if local_rel is not None and _log_commits(repo, local_rel):
        _fail(
            "LABEL_EXPOSURE",
            f"local probe path {local_rel} already appears in Git history",
        )
    if local_rel is not None and (
        _index_paths(repo, local_rel) or _index_has_changes(repo, local_rel)
    ):
        _fail(
            "LABEL_EXPOSURE",
            f"local probe path {local_rel} is already present in the Git index",
        )
    return summary


def _plain_external_file(path: Path) -> Path:
    if not os.path.lexists(path):
        _fail("PATH_MISSING", f"probe file is missing: {path}")
    if stat.S_ISLNK(path.lstat().st_mode) or not stat.S_ISREG(path.lstat().st_mode):
        _fail("PATH_UNSAFE", f"probe must be a plain regular file: {path}")
    return path


def verify_reveal(repo: Path, reveal_path: str) -> VerificationReceipt:
    repo = _repo_root(repo)
    reveal_path = _canonical_relpath(reveal_path)
    reveal_intro, reveal_raw = _immutable_intro(repo, reveal_path, kind="sealed reveal")
    reveal = validate_reveal(load_json_bytes(reveal_raw, where=reveal_path))
    campaign_id = reveal["campaign_id"]
    expected_reveal = f"{(BAKEOFF_ROOT / campaign_id).as_posix()}/{REVEAL_NAME}"
    if reveal_path != expected_reveal:
        _fail("PATH_INVALID", f"reveal must live at {expected_reveal}")
    commitment_intro, commitment_raw, commitment_path, probe_path, canonical_reveal = (
        _verify_commitment_history(repo, campaign_id, revealed=True)
    )
    if canonical_reveal != reveal_path:
        _fail("PATH_INVALID", "reveal path is not canonical")
    probe_intro, probe_raw = _immutable_intro(repo, probe_path, kind="revealed probe set")
    if probe_intro != reveal_intro:
        _fail(
            "ORDER_VIOLATION",
            "probe_set.json and sealed_reveal.json must be introduced together",
        )
    if not _is_strict_ancestor(repo, commitment_intro, reveal_intro):
        _fail(
            "ORDER_VIOLATION",
            "commitment introduction is not a strict ancestor of the reveal commit",
        )
    if reveal["commitment_path"] != commitment_path:
        _fail("PATH_INVALID", "reveal points to a different commitment path")
    if reveal["commitment_sha256"] != sha256_bytes(commitment_raw):
        _fail("HASH_MISMATCH", "reveal commitment_sha256 does not bind commitment bytes")
    commitment = validate_commitment(load_json_bytes(commitment_raw, where=commitment_path))
    if commitment["campaign_id"] != campaign_id:
        _fail("CAMPAIGN_MISMATCH", "commitment and reveal campaign_id differ")
    if reveal["probe_set_sha256"] != sha256_bytes(probe_raw):
        _fail("HASH_MISMATCH", "reveal probe_set_sha256 does not bind probe bytes")
    summary = verify_probe_against_commitment(commitment, probe_raw, where=probe_path)
    freshness = verify_freshness(
        repo,
        summary,
        exclude_version=FreshnessExemption(
            probe_path=probe_path,
            probe_intro=probe_intro,
            reveal_path=reveal_path,
            reveal_raw=reveal_raw,
            commitment_path=commitment_path,
            commitment_raw=commitment_raw,
            commitment_intro=commitment_intro,
        ),
    )
    if probe_intro not in freshness.reveal_copy_git_commits:
        _fail(
            "HISTORY_AMBIGUOUS",
            "current reveal introduction was not recovered by the freshness scan",
        )
    return VerificationReceipt(
        campaign_id=campaign_id,
        probe_set_sha256=summary.digest,
        commitment_git_commit=commitment_intro,
        reveal_git_commit=reveal_intro,
        reveal_copy_git_commits=freshness.reveal_copy_git_commits,
        published_probe_versions_checked=freshness.published_probe_versions_checked,
    )


def _campaign_lifecycle_parts(relpath: str) -> tuple[str, str]:
    path = PurePosixPath(_canonical_relpath(relpath))
    if (
        len(path.parts) != 4
        or path.parts[:2] != BAKEOFF_ROOT.parts
        or path.name not in LIFECYCLE_NAMES
    ):
        _fail(
            "PATH_INVALID",
            f"bakeoff lifecycle artifact is not at the canonical campaign depth: {relpath}",
        )
    campaign_id = _validate_identifier(path.parts[2], field="campaign_id")
    return campaign_id, path.name


def _head_lifecycle_inventory(repo: Path) -> set[str]:
    output = _git(
        repo,
        "ls-tree",
        "-r",
        "--name-only",
        "HEAD",
        "--",
        BAKEOFF_ROOT.as_posix(),
    ).stdout.decode("utf-8", errors="strict")
    inventory = {
        line
        for line in output.splitlines()
        if line and PurePosixPath(line).name in LIFECYCLE_NAMES
    }
    for relpath in sorted(inventory):
        _campaign_lifecycle_parts(relpath)
    return inventory


def _worktree_lifecycle_inventory(repo: Path) -> set[str]:
    root = _disk_path(repo, BAKEOFF_ROOT.as_posix(), require_file=False)
    if not root.exists() or not root.is_dir():
        _fail("PATH_MISSING", f"missing plain bakeoff root {BAKEOFF_ROOT}")
    inventory: set[str] = set()
    for current, directories, filenames in os.walk(root, followlinks=False):
        current_path = Path(current)
        for directory in directories:
            candidate = current_path / directory
            if candidate.is_symlink():
                _fail(
                    "PATH_UNSAFE",
                    f"symlink is forbidden below {BAKEOFF_ROOT}: "
                    f"{candidate.relative_to(repo)}",
                )
        for filename in filenames:
            if filename not in LIFECYCLE_NAMES:
                continue
            candidate = current_path / filename
            if candidate.is_symlink() or not candidate.is_file():
                _fail(
                    "PATH_UNSAFE",
                    f"lifecycle artifact is not a plain file: {candidate.relative_to(repo)}",
                )
            relpath = candidate.relative_to(repo).as_posix()
            _campaign_lifecycle_parts(relpath)
            inventory.add(relpath)
    return inventory


def _verify_legacy_public_probe(repo: Path, probe_rel: str) -> None:
    expected_digest = LEGACY_PUBLIC_PROBE_SHA256.get(probe_rel)
    if expected_digest is None:
        _fail("UNSEALED_PROBE", f"unrecognized unsealed probe fixture: {probe_rel}")
    _intro, raw = _immutable_intro(
        repo,
        probe_rel,
        kind="grandfathered legacy probe set",
        all_refs=True,
    )
    actual_digest = sha256_bytes(raw)
    if actual_digest != expected_digest:
        _fail(
            "LEGACY_PROBE_MISMATCH",
            f"grandfathered probe {probe_rel} has sha256 {actual_digest}; "
            f"expected {expected_digest}",
        )


def verify_tree(repo: Path) -> list[VerificationReceipt]:
    repo = _repo_root(repo)
    if _index_has_changes(repo, BAKEOFF_ROOT.as_posix()):
        _fail(
            "WORKTREE_DRIFT",
            "bakeoff lifecycle paths have staged Git-index changes",
        )
    tracked = _head_lifecycle_inventory(repo)
    worktree = _worktree_lifecycle_inventory(repo)
    if tracked != worktree:
        _fail(
            "WORKTREE_DRIFT",
            "bakeoff lifecycle inventory differs between HEAD and worktree; "
            f"missing={sorted(tracked - worktree)} extra={sorted(worktree - tracked)}",
        )
    historical_probe_paths = _published_probe_paths(repo)
    for legacy_probe in sorted(LEGACY_PUBLIC_PROBE_PATHS & historical_probe_paths):
        _verify_legacy_public_probe(repo, legacy_probe)
    campaigns: dict[str, set[str]] = {}
    for relpath in sorted(tracked):
        campaign_id, filename = _campaign_lifecycle_parts(relpath)
        campaigns.setdefault(campaign_id, set()).add(filename)

    receipts: list[VerificationReceipt] = []
    for campaign_id, present in sorted(campaigns.items()):
        rel_dir = (BAKEOFF_ROOT / campaign_id).as_posix()
        commitment_rel = f"{rel_dir}/{COMMITMENT_NAME}"
        probe_rel = f"{rel_dir}/{PROBE_NAME}"
        reveal_rel = f"{rel_dir}/{REVEAL_NAME}"
        if present == {PROBE_NAME}:
            if probe_rel in LEGACY_PUBLIC_PROBE_PATHS:
                continue
            _fail(
                "UNSEALED_PROBE",
                f"future bakeoff fixture lacks sealed commitment/reveal: {probe_rel}",
            )
        if present == {COMMITMENT_NAME}:
            commitment_raw = _disk_path(repo, commitment_rel).read_bytes()
            parsed = validate_commitment(
                load_json_bytes(commitment_raw, where=commitment_rel)
            )
            if parsed["campaign_id"] != campaign_id:
                _fail("CAMPAIGN_MISMATCH", "commitment campaign_id differs from directory")
            _verify_commitment_history(repo, campaign_id, revealed=False)
            continue
        if present == LIFECYCLE_NAMES:
            receipts.append(verify_reveal(repo, reveal_rel))
            continue
        _fail(
            "INCOMPLETE_LIFECYCLE",
            f"campaign {rel_dir} has an incomplete sealed lifecycle: {present}",
        )
    return receipts


def _campaign_unused(repo: Path, campaign_id: str) -> None:
    campaign_dir, _commitment, _probe, _reveal = _campaign_paths(campaign_id)
    history = _log_commits(repo, campaign_dir, all_refs=True)
    if history:
        _fail("CAMPAIGN_REUSE", f"campaign path already exists in Git history: {campaign_dir}")


def _command_prepare(args: argparse.Namespace) -> None:
    repo = _repo_root(args.repo_root)
    _campaign_unused(repo, args.campaign_id)
    raw = _plain_external_file(args.probe_set).read_bytes()
    commitment = make_commitment(args.campaign_id, raw)
    summary = validate_probe_set(raw)
    verify_freshness(repo, summary)
    sys.stdout.buffer.write(render_json(commitment))


def _command_preflight(args: argparse.Namespace) -> None:
    summary = preflight(args.repo_root, args.commitment, args.probe_set)
    print(
        f"PASS: sealed preflight; probe_sha256={summary.digest}; "
        "remote-push timing still requires a public run-report witness"
    )


def _command_make_reveal(args: argparse.Namespace) -> None:
    repo = _repo_root(args.repo_root)
    commitment_rel = _canonical_relpath(args.commitment)
    commitment_path = _disk_path(repo, commitment_rel)
    commitment = validate_commitment(
        load_json_bytes(commitment_path.read_bytes(), where=commitment_rel)
    )
    campaign_id = commitment["campaign_id"]
    _intro, commitment_raw, canonical_commitment, canonical_probe, _canonical_reveal = (
        _verify_commitment_history(repo, campaign_id, revealed=False)
    )
    if canonical_commitment != commitment_rel:
        _fail("PATH_INVALID", "commitment path is not canonical")
    probe_path = _plain_external_file(args.probe_set)
    try:
        probe_rel = probe_path.resolve().relative_to(repo).as_posix()
    except ValueError:
        _fail(
            "PATH_INVALID",
            f"reveal probe must be staged at the canonical repository path {canonical_probe}",
        )
    if probe_rel != canonical_probe:
        _fail("PATH_INVALID", f"reveal probe must live at {canonical_probe}")
    probe_raw = probe_path.read_bytes()
    summary = verify_probe_against_commitment(commitment, probe_raw, where=probe_rel)
    verify_freshness(repo, summary)
    reveal = make_reveal(
        campaign_id,
        canonical_commitment,
        commitment_raw,
        canonical_probe,
        probe_raw,
    )
    sys.stdout.buffer.write(render_json(reveal))


def _command_verify_reveal(args: argparse.Namespace) -> None:
    receipt = verify_reveal(args.repo_root, args.reveal)
    print(json.dumps(receipt.as_dict(), ensure_ascii=False, indent=2))


def _command_verify_tree(args: argparse.Namespace) -> None:
    receipts = verify_tree(args.repo_root)
    print(
        json.dumps(
            {
                "schema_version": "ars-promotion-bakeoff-sealed-tree-check/1.0",
                "status": "verified",
                "revealed_campaigns": [receipt.as_dict() for receipt in receipts],
                "revealed_campaign_count": len(receipts),
                "remote_publication_timing": "not_verifiable_locally",
                "gate_eligibility": "requires_run_report_witness",
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare_parser = subparsers.add_parser(
        "prepare", help="validate a private fixture and print its public commitment"
    )
    prepare_parser.add_argument("--campaign-id", required=True)
    prepare_parser.add_argument("--probe-set", required=True, type=Path)
    prepare_parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    prepare_parser.set_defaults(handler=_command_prepare)

    preflight_parser = subparsers.add_parser(
        "preflight", help="verify the committed seal before any fleet call"
    )
    preflight_parser.add_argument("--commitment", required=True)
    preflight_parser.add_argument("--probe-set", required=True, type=Path)
    preflight_parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    preflight_parser.set_defaults(handler=_command_preflight)

    reveal_parser = subparsers.add_parser(
        "make-reveal", help="print the post-fleet reveal carrier"
    )
    reveal_parser.add_argument("--commitment", required=True)
    reveal_parser.add_argument("--probe-set", required=True, type=Path)
    reveal_parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    reveal_parser.set_defaults(handler=_command_make_reveal)

    verify_parser = subparsers.add_parser(
        "verify-reveal", help="verify one committed reveal and its Git history"
    )
    verify_parser.add_argument("--reveal", required=True)
    verify_parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    verify_parser.set_defaults(handler=_command_verify_reveal)

    tree_parser = subparsers.add_parser(
        "verify-tree", help="verify every pending or revealed sealed campaign"
    )
    tree_parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    tree_parser.set_defaults(handler=_command_verify_tree)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        args.handler(args)
    except PreregistrationError as failure:
        print(f"FAIL [{failure.code}]: {failure}", file=sys.stderr)
        return 1
    except OSError as failure:
        print(f"FAIL [IO_ERROR]: {failure}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
