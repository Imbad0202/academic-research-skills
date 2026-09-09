#!/usr/bin/env python3
"""Shared advisory file locking for ARS scripts (#845).

One backend per host, chosen at import time:

* ``fcntl`` (POSIX): ``flock``.  Shared and exclusive modes, blocking and
  non-blocking, exactly as before #845.
* ``msvcrt`` (Windows): ``locking`` on byte 0 of the lock file.  This backend
  is best-effort and has no CI coverage; it differs from ``flock`` in two
  documented ways that callers must decide about, not paper over:

  - there is no shared mode, so ``exclusive=False`` takes an exclusive lock
    (``SHARED_LOCKS_SUPPORTED`` is ``False``);
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

try:
    import fcntl

    msvcrt = None
except ModuleNotFoundError:  # pragma: no cover - exercised on Windows
    fcntl = None  # type: ignore[assignment]
    import msvcrt  # type: ignore[import-not-found]

BACKEND = "fcntl" if fcntl is not None else "msvcrt"
SHARED_LOCKS_SUPPORTED = fcntl is not None
WINDOWS_BLOCKING_WAIT_SECONDS = 30.0
POLL_SECONDS = 0.05

_CONTENTION_ERRNOS = frozenset(
    code
    for code in (
        errno.EAGAIN,
        errno.EWOULDBLOCK,
        errno.EACCES,
        errno.EDEADLK,
        getattr(errno, "EDEADLOCK", errno.EDEADLK),
    )
    if isinstance(code, int)
)


class LockTimeout(BlockingIOError):
    """The lock was still held by someone else when the wait ran out."""

    def __init__(self, waited: float) -> None:
        super().__init__(errno.EAGAIN, f"lock still held after {waited:g}s")
        self.waited = waited


def _try_once(fd: int, *, exclusive: bool) -> None:
    """One non-blocking attempt; raises OSError with a contention errno if held."""
    if fcntl is not None:
        operation = (fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH) | fcntl.LOCK_NB
        fcntl.flock(fd, operation)
        return
    os.lseek(fd, 0, os.SEEK_SET)
    msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)


def acquire(fd: int, *, exclusive: bool = True, timeout: float | None) -> None:
    """Acquire an advisory lock on ``fd``.

    ``timeout=None`` blocks until the lock is free (bounded on Windows, see
    module docstring); ``timeout=0`` makes a single attempt; ``timeout>0``
    polls until the deadline.  Raises ``LockTimeout`` when the lock is still
    held at the end of the wait.
    """
    if timeout is not None and timeout < 0:
        raise ValueError("lock timeout must be non-negative")

    if timeout is None and fcntl is not None:
        operation = fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH
        while True:
            try:
                fcntl.flock(fd, operation)
                return
            except InterruptedError:
                continue

    wait = WINDOWS_BLOCKING_WAIT_SECONDS if timeout is None else float(timeout)
    deadline = time.monotonic() + wait
    while True:
        try:
            _try_once(fd, exclusive=exclusive)
            return
        except InterruptedError as exc:
            # A signal interrupted the attempt; retry, but never past the
            # deadline, so a persistent interruption cannot defeat the bound.
            if time.monotonic() >= deadline:
                raise LockTimeout(wait) from exc
            continue
        except OSError as exc:
            if exc.errno not in _CONTENTION_ERRNOS:
                raise
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise LockTimeout(wait) from exc
            time.sleep(min(POLL_SECONDS, remaining))


def release(fd: int) -> None:
    """Release a lock taken with :func:`acquire`."""
    if fcntl is not None:
        fcntl.flock(fd, fcntl.LOCK_UN)
        return
    os.lseek(fd, 0, os.SEEK_SET)
    msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
