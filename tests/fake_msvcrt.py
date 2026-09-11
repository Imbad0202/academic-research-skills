"""A stand-in for the Windows ``msvcrt`` module, for testing ``scripts/file_lock``.

It models only the contract the helper relies on (Microsoft ``_locking``):

* the lock covers ``nbytes`` from the current file position, so the helper
  must position the descriptor at offset 0 before every call;
* one holder per (file, region): a second descriptor, or the same one again,
  fails immediately with ``EACCES`` under ``LK_NBLCK``;
* ``LK_UNLCK`` by a non-holder fails with ``EACCES``;
* there is no shared mode.

An instance is installed as ``sys.modules["msvcrt"]`` (or patched onto the
helper module); attribute access is all ``import msvcrt`` needs.  Stdlib only,
so a subprocess can import it before anything else.
"""
from __future__ import annotations

import errno
import os


class FakeMsvcrt:
    LK_NBLCK = 2
    LK_UNLCK = 0

    def __init__(self) -> None:
        self.holders: dict[tuple[int, int], int] = {}

    def locking(self, fd: int, mode: int, nbytes: int) -> None:
        info = os.fstat(fd)
        key = (info.st_dev, info.st_ino)
        if os.lseek(fd, 0, os.SEEK_CUR) != 0 or nbytes != 1:
            raise AssertionError("helper must lock exactly byte 0")
        if mode == self.LK_NBLCK:
            if key in self.holders:
                raise OSError(errno.EACCES, "Permission denied")
            self.holders[key] = fd
        elif mode == self.LK_UNLCK:
            if self.holders.get(key) != fd:
                raise OSError(errno.EACCES, "Permission denied")
            del self.holders[key]
        else:
            raise AssertionError(f"helper must not use locking mode {mode}")
