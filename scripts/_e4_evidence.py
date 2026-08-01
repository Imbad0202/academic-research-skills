#!/usr/bin/env python3
"""Shared filesystem primitives for the E4 evidence boundary (#616)."""
from __future__ import annotations

import hashlib
import os
import stat
from pathlib import Path


class EvidencePathError(ValueError):
    """An evidence path is missing, redirected, or not a plain file/tree."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def lexical_path(path: Path) -> Path:
    """Absolute lexical normalization without following symlinks."""
    return Path(os.path.abspath(os.path.normpath(os.fspath(path))))


def within(path: Path, root: Path) -> bool:
    try:
        lexical_path(path).relative_to(lexical_path(root))
    except ValueError:
        return False
    return True


def assert_no_symlink_components(path: Path, root: Path) -> None:
    """Reject every symlink from ``root`` down to ``path`` inclusive."""
    root = lexical_path(root)
    path = lexical_path(path)
    try:
        relative = path.relative_to(root)
    except ValueError as failure:
        raise EvidencePathError(f"{path} escapes evidence root {root}") \
            from failure
    current = root
    if current.is_symlink():
        raise EvidencePathError(f"symlink evidence root is forbidden: {root}")
    for part in relative.parts:
        current = current / part
        try:
            mode = current.lstat().st_mode
        except FileNotFoundError as failure:
            raise EvidencePathError(f"evidence path does not resolve: {path}") \
                from failure
        if stat.S_ISLNK(mode):
            raise EvidencePathError(
                f"symlink evidence path is forbidden: {current}")


def assert_plain_file(path: Path, root: Path) -> None:
    assert_no_symlink_components(path, root)
    try:
        mode = lexical_path(path).lstat().st_mode
    except FileNotFoundError as failure:
        raise EvidencePathError(f"evidence file does not resolve: {path}") \
            from failure
    if not stat.S_ISREG(mode):
        raise EvidencePathError(f"evidence path is not a regular file: {path}")


def assert_plain_directory(path: Path, root: Path) -> None:
    assert_no_symlink_components(path, root)
    try:
        mode = lexical_path(path).lstat().st_mode
    except FileNotFoundError as failure:
        raise EvidencePathError(
            f"evidence directory does not resolve: {path}") from failure
    if not stat.S_ISDIR(mode):
        raise EvidencePathError(
            f"evidence path is not a directory: {path}")


def tree_manifest(root: Path, *, exclude: set[str] | None = None) -> list[dict]:
    """Return a stable path/type/hash manifest without following links."""
    root = lexical_path(root)
    assert_plain_directory(root, root)
    excluded = exclude or set()
    entries: list[dict] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        relative = path.relative_to(root).as_posix()
        if relative in excluded:
            continue
        mode = path.lstat().st_mode
        if stat.S_ISREG(mode):
            entries.append({
                "path": relative,
                "type": "file",
                "sha256": sha256_file(path),
            })
        elif stat.S_ISDIR(mode):
            entries.append({"path": relative, "type": "directory"})
        elif stat.S_ISLNK(mode):
            entries.append({
                "path": relative,
                "type": "symlink",
                "target": os.readlink(path),
            })
        else:
            entries.append({"path": relative, "type": "other"})
    return entries
