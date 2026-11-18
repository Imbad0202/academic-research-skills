#!/usr/bin/env python3
"""Shared no-follow file opening and directory fsync for ARS scripts (#1092).

Several scripts read an explicit input without ever traversing a symlinked
path component.  They did it by walking the path with ``os.open(...,
dir_fd=...)``, which only exists on POSIX.  On Windows ``os.open()`` cannot
open a directory and ``os.open`` is not in ``os.supports_dir_fd``, so every
walk failed before reading anything, with an error that looked like a problem
with the user's file.  This module owns that walk and the directory fsync.

Two backends, chosen per call by ``descriptor_relative_supported()``:

* **Descriptor-relative (POSIX).**  Exactly the walk the scripts used before
  #1092: every directory is opened ``O_DIRECTORY | O_NOFOLLOW`` relative to
  the previous descriptor and the leaf is opened ``O_NOFOLLOW``.  A component
  swapped for a symlink between steps cannot redirect the walk, because each
  step is anchored to a descriptor and not to a path.  Nothing about this
  backend changed.

* **Path-based (Windows, or any host where ``os.open`` is not in
  ``os.supports_dir_fd``).**  Windows has no ``dir_fd``, no ``O_DIRECTORY``
  and no ``O_NOFOLLOW``, so the guarantee above cannot be reproduced.  This
  backend is best-effort and has no Windows CI coverage.  For the anchor's
  children it does, in order: ``lstat`` each component and reject a symlink or
  any reparse point (a junction is one); open the leaf by path; ``fstat`` the
  opened file and require it to be the file the ``lstat`` saw (same
  ``st_dev``/``st_ino`` when the platform fills them); then ``lstat`` every
  component again and reject if one became a reparse point or changed
  identity.  Documented limits:

  - The check is not atomic.  A component replaced between the first
    ``lstat`` and the open, and restored before the second ``lstat``, is not
    detected.  The POSIX backend closes that race; this one narrows it.
  - The anchor (the bundle root, the filesystem root or drive anchor, or the
    current directory for a relative path) is trusted: ``nofollow_anchor``
    makes this backend ``lstat`` the anchor itself, as the POSIX walk does
    with ``O_NOFOLLOW``, but neither backend can check the anchor's own
    ancestors, and for a relative path the current directory is never
    checked.
  - Every reparse point is rejected, not only symlinks and junctions, so a
    file under a cloud-sync placeholder directory is refused.

Failures use ``OSError`` subclasses whose message names the cause, so a
caller that already turns ``OSError`` into its own error type keeps working:
``SymlinkRejected`` (``errno.ELOOP``, the errno ``O_NOFOLLOW`` raises) and
``PlatformLimitation`` (a platform lacks what the chosen backend needs).
Neither message blames the user's file for a platform gap.
"""
from __future__ import annotations

import errno
import os
import stat
from pathlib import Path
from typing import Sequence

# Windows-only stat attribute bit; the constant is defined on every platform.
_REPARSE_POINT = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
_BINARY = getattr(os, "O_BINARY", 0)

_BEST_EFFORT_NOTE = (
    "no descriptor-relative open on this platform, so the symlink and "
    "reparse-point check is path-based and best-effort"
)


class SymlinkRejected(OSError):
    """A path component is a symlink or reparse point."""

    def __init__(self, component: str, *, best_effort: bool) -> None:
        detail = f" ({_BEST_EFFORT_NOTE})" if best_effort else ""
        super().__init__(
            errno.ELOOP,
            f"path component is a symlink or reparse point: {component}{detail}",
        )


class PlatformLimitation(OSError):
    """The platform lacks what a safe no-follow open needs."""

    def __init__(self, message: str) -> None:
        super().__init__(errno.ENOSYS, f"platform limitation: {message}")


def descriptor_relative_supported() -> bool:
    """True where the descriptor-relative (``dir_fd``) walk is available."""
    return os.name != "nt" and os.open in os.supports_dir_fd


def _is_reparse_or_link(info: os.stat_result) -> bool:
    if stat.S_ISLNK(info.st_mode):
        return True
    return bool(getattr(info, "st_file_attributes", 0) & _REPARSE_POINT)


def _identity(info: os.stat_result) -> tuple[int, int] | None:
    # Windows fills st_dev/st_ino from the file index; 0 means "unknown".
    if info.st_ino == 0:
        return None
    return (info.st_dev, info.st_ino)


def _open_walk_descriptor(
    anchor: str | os.PathLike[str],
    components: Sequence[str],
    flags: int,
    *,
    nofollow_anchor: bool,
) -> int:
    directory_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    try:
        directory_fd = os.open(
            anchor, directory_flags | (nofollow if nofollow_anchor else 0)
        )
    except NotImplementedError as exc:  # pragma: no cover - defensive
        raise PlatformLimitation(str(exc)) from exc
    try:
        for component in components[:-1]:
            next_fd = os.open(component, directory_flags | nofollow, dir_fd=directory_fd)
            os.close(directory_fd)
            directory_fd = next_fd
        return os.open(components[-1], flags | nofollow, dir_fd=directory_fd)
    except NotImplementedError as exc:  # pragma: no cover - defensive
        raise PlatformLimitation(str(exc)) from exc
    finally:
        os.close(directory_fd)


def _open_walk_path(
    anchor: str | os.PathLike[str],
    components: Sequence[str],
    flags: int,
    *,
    nofollow_anchor: bool,
) -> int:
    chain: list[tuple[Path, tuple[int, int] | None]] = []
    current = Path(anchor)
    if nofollow_anchor:
        # Only the anchor itself: its own ancestors stay trusted (module doc).
        anchor_info = os.lstat(current)
        if _is_reparse_or_link(anchor_info):
            raise SymlinkRejected(str(current), best_effort=True)
        chain.append((current, _identity(anchor_info)))
    for index, component in enumerate(components):
        current = current / component
        info = os.lstat(current)
        if _is_reparse_or_link(info):
            raise SymlinkRejected(str(current), best_effort=True)
        if index < len(components) - 1 and not stat.S_ISDIR(info.st_mode):
            raise NotADirectoryError(errno.ENOTDIR, "not a directory", str(current))
        chain.append((current, _identity(info)))
    leaf_path, leaf_identity = chain[-1]
    fd = os.open(leaf_path, flags | _BINARY)
    try:
        opened = os.fstat(fd)
        opened_identity = _identity(opened)
        if (
            leaf_identity is not None
            and opened_identity is not None
            and leaf_identity != opened_identity
        ):
            raise SymlinkRejected(str(leaf_path), best_effort=True)
        for path, identity in chain:
            again = os.lstat(path)
            if _is_reparse_or_link(again) or (
                identity is not None
                and _identity(again) is not None
                and _identity(again) != identity
            ):
                raise SymlinkRejected(str(path), best_effort=True)
    except BaseException:
        os.close(fd)
        raise
    return fd


def open_under(
    anchor: str | os.PathLike[str],
    components: Sequence[str],
    flags: int = os.O_RDONLY,
    *,
    nofollow_anchor: bool = False,
) -> int:
    """Open ``anchor/components[0]/.../components[-1]`` without following links.

    Returns an open file descriptor for the leaf; the caller closes it.
    ``components`` must be non-empty single names (no separators or drive
    prefix, no ``""`` or ``"."``; ``".."`` is left to callers that open an explicit user path, and
    bundle readers reject it before calling).  ``nofollow_anchor`` also
    refuses a symlinked anchor, on both backends.
    """
    if not components:
        raise ValueError("open_under needs at least one path component")
    separators = {"/", os.sep, os.altsep or "/"}
    for component in components:
        if (
            not isinstance(component, str)
            or component in ("", ".")
            or any(sep in component for sep in separators)
            # Windows: "D:name" joins onto drive D's current directory and
            # leaves the anchor; ":" also names an alternate data stream.
            or os.path.splitdrive(component)[0]
            or (os.name == "nt" and ":" in component)
        ):
            raise ValueError(f"open_under needs plain path components: {component!r}")
    if descriptor_relative_supported():
        return _open_walk_descriptor(
            anchor, components, flags, nofollow_anchor=nofollow_anchor
        )
    return _open_walk_path(anchor, components, flags, nofollow_anchor=nofollow_anchor)


def open_explicit_path(path: Path, flags: int = os.O_RDONLY) -> int:
    """Open one explicit path (absolute or relative) without following links.

    A relative path is walked from the current directory, an absolute path
    from its anchor (``/`` or a drive root).  Raises ``ValueError`` when the
    path has no file component.
    """
    parts = path.parts
    if path.anchor:
        # Also a rooted path without a drive and a drive-relative path on Windows.
        anchor, components = path.anchor, parts[1:]
    else:
        anchor, components = ".", parts
    return open_under(anchor, components, flags)


def fsync_directory(path: Path) -> None:
    """Flush a directory entry to disk, where the platform can.

    On Windows (and any host without descriptor-relative support) a directory
    cannot be opened with ``os.open()``, so the flush is skipped: the data
    file's own fsync still happened, but a crash right after a rename may lose
    the new directory entry.  POSIX behaviour is unchanged.
    """
    if not descriptor_relative_supported():
        return
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    fd = os.open(path, flags)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)
