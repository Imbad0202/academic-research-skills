#!/usr/bin/env python3
"""Shared advisory file locking for ARS scripts (#845).

One backend per host, chosen at import time and published as ``BACKEND``:

* ``"fcntl"`` (POSIX): ``flock``.  Shared and exclusive modes, blocking and
  non-blocking, exactly as before #845.
* ``"msvcrt"`` (Windows): ``locking`` on byte 0 of the lock file.  This
  backend is best-effort and has no CI coverage; it differs from ``flock`` in
  two documented ways that callers decide about rather than paper over:

  - there is no shared mode, so ``exclusive=False`` takes an exclusive lock;
  - there is no indefinite blocking wait, so ``timeout=None`` polls for at
    most ``WINDOWS_BLOCKING_WAIT_SECONDS`` and then raises ``LockTimeout``.

The helper never reads or writes the lock file.  ``msvcrt.locking`` may lock
a byte beyond end-of-file, so an empty lock file is valid on both backends;
callers that require the lock file to stay empty keep that invariant.

Contention on either backend surfaces as ``LockTimeout`` (a
``BlockingIOError`` carrying ``EAGAIN``), including ``timeout=0``, so a
caller can treat "someone else holds it" uniformly.  Every other ``OSError``
propagates unchanged.
"""
from __future__ import annotations

import errno
import os
import time
from contextlib import contextmanager
from typing import Iterator

try:
    import fcntl

    BACKEND = "fcntl"
except ModuleNotFoundError:  # pragma: no cover - exercised on Windows
    import msvcrt  # type: ignore[import-not-found]

    BACKEND = "msvcrt"

WINDOWS_BLOCKING_WAIT_SECONDS = 30.0
POLL_SECONDS = 0.05

# EAGAIN / EWOULDBLOCK: flock non-blocking contention.  EACCES: msvcrt
# contention.  EINTR: a signal interrupted the attempt; retried like
# contention so the deadline still bounds it.
_RETRYABLE_ERRNOS = frozenset(
    {errno.EAGAIN, errno.EWOULDBLOCK, errno.EACCES, errno.EINTR}
)


class LockTimeout(BlockingIOError):
    """The lock was still held by someone else when the wait ran out."""

    def __init__(self, waited: float) -> None:
        super().__init__(errno.EAGAIN, f"lock still held after {waited:g}s")


def _flock(fd: int, *, exclusive: bool, blocking: bool) -> None:
    operation = fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH
    if not blocking:
        operation |= fcntl.LOCK_NB
    fcntl.flock(fd, operation)


def _msvcrt_byte0(fd: int, mode: int) -> None:
    os.lseek(fd, 0, os.SEEK_SET)
    msvcrt.locking(fd, mode, 1)


def _try_once(fd: int, *, exclusive: bool) -> None:
    """One non-blocking attempt; raises OSError with a retryable errno if held."""
    if BACKEND == "fcntl":
        _flock(fd, exclusive=exclusive, blocking=False)
    else:
        _msvcrt_byte0(fd, msvcrt.LK_NBLCK)


def acquire(fd: int, *, exclusive: bool = True, timeout: float | None) -> None:
    """Acquire an advisory lock on ``fd``.

    ``timeout=None`` blocks until the lock is free (bounded on Windows, see
    module docstring); ``timeout=0`` makes a single attempt; ``timeout>0``
    polls until the deadline.  Raises ``LockTimeout`` when the lock is still
    held at the end of the wait.
    """
    if timeout is not None and timeout < 0:
        raise ValueError("lock timeout must be non-negative")

    if timeout is None and BACKEND == "fcntl":
        _flock(fd, exclusive=exclusive, blocking=True)
        return

    wait = WINDOWS_BLOCKING_WAIT_SECONDS if timeout is None else float(timeout)
    deadline = time.monotonic() + wait
    while True:
        try:
            _try_once(fd, exclusive=exclusive)
            return
        except OSError as exc:
            if exc.errno not in _RETRYABLE_ERRNOS:
                raise
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise LockTimeout(wait) from exc
            time.sleep(min(POLL_SECONDS, remaining))


def release(fd: int) -> None:
    """Release a lock taken with :func:`acquire`."""
    if BACKEND == "fcntl":
        fcntl.flock(fd, fcntl.LOCK_UN)
    else:
        _msvcrt_byte0(fd, msvcrt.LK_UNLCK)


@contextmanager
def held(fd: int, *, exclusive: bool = True, timeout: float | None) -> Iterator[None]:
    """Hold a lock for the block; releases only what it acquired.

    Releasing an unheld lock is a no-op under ``flock`` but an error under
    ``msvcrt``, so the release lives here, after a successful acquire.
    """
    acquire(fd, exclusive=exclusive, timeout=timeout)
    try:
        yield
    finally:
        release(fd)
