"""Tests for the shared advisory file-lock helper (#845).

The real backend on the CI host is ``fcntl``.  The ``msvcrt`` branch is
exercised through ``tests.fake_msvcrt`` (the documented Windows semantics the
helper depends on), so the Windows code path is tested for logic, not for
platform behaviour.  Real Windows verification remains a manual step (#845).
"""
from __future__ import annotations

import errno
import os
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Iterator

import pytest

from scripts import file_lock
from tests.fake_msvcrt import FakeMsvcrt


def _open_lock(path: Path) -> int:
    return os.open(path, os.O_RDWR | os.O_CREAT, 0o600)


@pytest.fixture
def lock_pair(tmp_path: Path) -> Iterator[tuple[int, int]]:
    """Two independent descriptors on one lock file, closed afterwards."""
    lock = tmp_path / "x.lock"
    a = _open_lock(lock)
    b = _open_lock(lock)
    try:
        yield a, b
    finally:
        os.close(a)
        os.close(b)


@pytest.fixture
def fake_windows(monkeypatch: pytest.MonkeyPatch) -> FakeMsvcrt:
    fake = FakeMsvcrt()
    monkeypatch.setattr(file_lock, "BACKEND", "msvcrt")
    monkeypatch.setattr(file_lock, "msvcrt", fake, raising=False)
    return fake


# --------------------------------------------------------------------------
# Real backend (fcntl on the CI host)
# --------------------------------------------------------------------------


def test_exclusive_lock_is_held_until_released(lock_pair: tuple[int, int]) -> None:
    a, b = lock_pair
    file_lock.acquire(a, exclusive=True, timeout=0)
    with pytest.raises(BlockingIOError) as info:
        file_lock.acquire(b, exclusive=True, timeout=0)
    assert isinstance(info.value, file_lock.LockTimeout)
    assert info.value.errno == errno.EAGAIN
    file_lock.release(a)
    file_lock.acquire(b, exclusive=True, timeout=0)
    file_lock.release(b)


def test_bounded_wait_expires_after_timeout(lock_pair: tuple[int, int]) -> None:
    a, b = lock_pair
    file_lock.acquire(a, exclusive=True, timeout=0)
    started = time.monotonic()
    with pytest.raises(file_lock.LockTimeout, match="0.2"):
        file_lock.acquire(b, exclusive=True, timeout=0.2)
    assert 0.15 <= time.monotonic() - started < 3.0
    file_lock.release(a)


@pytest.mark.parametrize("timeout", [5.0, None])
def test_waiting_acquire_succeeds_when_holder_releases(
    lock_pair: tuple[int, int], timeout: float | None
) -> None:
    a, b = lock_pair
    file_lock.acquire(a, exclusive=True, timeout=0)
    threading.Timer(0.15, file_lock.release, args=(a,)).start()
    started = time.monotonic()
    file_lock.acquire(b, exclusive=True, timeout=timeout)
    assert time.monotonic() - started >= 0.1
    file_lock.release(b)


def test_negative_timeout_is_rejected(tmp_path: Path) -> None:
    fd = _open_lock(tmp_path / "x.lock")
    try:
        with pytest.raises(ValueError):
            file_lock.acquire(fd, exclusive=True, timeout=-1)
    finally:
        os.close(fd)


def test_helper_never_writes_to_the_lock_file(tmp_path: Path) -> None:
    lock = tmp_path / "x.lock"
    fd = _open_lock(lock)
    try:
        for exclusive in (True, False):
            file_lock.acquire(fd, exclusive=exclusive, timeout=0)
            file_lock.release(fd)
    finally:
        os.close(fd)
    assert lock.stat().st_size == 0


@pytest.mark.skipif(file_lock.BACKEND != "fcntl", reason="no shared locks")
def test_shared_locks_coexist_and_exclude_writers(tmp_path: Path) -> None:
    lock = tmp_path / "x.lock"
    r1, r2, w = (_open_lock(lock) for _ in range(3))
    try:
        file_lock.acquire(r1, exclusive=False, timeout=0)
        file_lock.acquire(r2, exclusive=False, timeout=0)
        with pytest.raises(file_lock.LockTimeout):
            file_lock.acquire(w, exclusive=True, timeout=0)
        file_lock.release(r1)
        file_lock.release(r2)
        file_lock.acquire(w, exclusive=True, timeout=0)
        with pytest.raises(file_lock.LockTimeout):
            file_lock.acquire(r1, exclusive=False, timeout=0)
        file_lock.release(w)
    finally:
        for fd in (r1, r2, w):
            os.close(fd)


# --------------------------------------------------------------------------
# msvcrt branch through the fake module
# --------------------------------------------------------------------------


def test_windows_exclusive_contention_and_release(
    lock_pair: tuple[int, int], fake_windows: FakeMsvcrt, tmp_path: Path
) -> None:
    a, b = lock_pair
    file_lock.acquire(a, exclusive=True, timeout=0)
    with pytest.raises(file_lock.LockTimeout):
        file_lock.acquire(b, exclusive=True, timeout=0)
    file_lock.release(a)
    file_lock.acquire(b, exclusive=True, timeout=0)
    file_lock.release(b)
    assert (tmp_path / "x.lock").stat().st_size == 0


def test_windows_shared_request_degrades_to_exclusive(
    lock_pair: tuple[int, int], fake_windows: FakeMsvcrt
) -> None:
    r1, r2 = lock_pair
    file_lock.acquire(r1, exclusive=False, timeout=0)
    with pytest.raises(file_lock.LockTimeout):
        file_lock.acquire(r2, exclusive=False, timeout=0)
    file_lock.release(r1)


def test_windows_positions_descriptor_at_zero_before_locking(
    tmp_path: Path, fake_windows: FakeMsvcrt
) -> None:
    # The fake raises AssertionError if the descriptor is not at offset 0.
    fd = _open_lock(tmp_path / "x.lock")
    try:
        os.lseek(fd, 7, os.SEEK_SET)
        file_lock.acquire(fd, exclusive=True, timeout=0)
        os.lseek(fd, 3, os.SEEK_SET)
        file_lock.release(fd)
    finally:
        os.close(fd)


def test_windows_blocking_acquire_is_bounded(
    lock_pair: tuple[int, int], fake_windows: FakeMsvcrt, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(file_lock, "WINDOWS_BLOCKING_WAIT_SECONDS", 0.2)
    a, b = lock_pair
    file_lock.acquire(a, exclusive=True, timeout=0)
    started = time.monotonic()
    with pytest.raises(file_lock.LockTimeout, match="0.2"):
        file_lock.acquire(b, exclusive=True, timeout=None)
    assert 0.15 <= time.monotonic() - started < 3.0
    file_lock.release(a)


def test_windows_blocking_acquire_succeeds_on_release(
    lock_pair: tuple[int, int], fake_windows: FakeMsvcrt
) -> None:
    a, b = lock_pair
    file_lock.acquire(a, exclusive=True, timeout=0)
    threading.Timer(0.15, file_lock.release, args=(a,)).start()
    file_lock.acquire(b, exclusive=True, timeout=None)
    file_lock.release(b)


def test_persistent_interruption_still_honours_the_deadline(
    tmp_path: Path, fake_windows: FakeMsvcrt, monkeypatch: pytest.MonkeyPatch
) -> None:
    def locking(fd: int, mode: int, nbytes: int) -> None:
        raise InterruptedError(errno.EINTR, "Interrupted system call")

    monkeypatch.setattr(fake_windows, "locking", locking)
    fd = _open_lock(tmp_path / "x.lock")
    try:
        started = time.monotonic()
        with pytest.raises(file_lock.LockTimeout):
            file_lock.acquire(fd, exclusive=True, timeout=0.05)
        assert time.monotonic() - started < 3.0
    finally:
        os.close(fd)


def test_windows_unexpected_oserror_propagates_unchanged(
    tmp_path: Path, fake_windows: FakeMsvcrt, monkeypatch: pytest.MonkeyPatch
) -> None:
    def locking(fd: int, mode: int, nbytes: int) -> None:
        raise OSError(errno.EBADF, "Bad file descriptor")

    monkeypatch.setattr(fake_windows, "locking", locking)
    fd = _open_lock(tmp_path / "x.lock")
    try:
        with pytest.raises(OSError) as info:
            file_lock.acquire(fd, exclusive=True, timeout=1.0)
        assert info.value.errno == errno.EBADF
        assert not isinstance(info.value, file_lock.LockTimeout)
    finally:
        os.close(fd)


# --------------------------------------------------------------------------
# Consumer import shape with fcntl absent (subprocess, fake msvcrt)
# --------------------------------------------------------------------------

_WINDOWS_SHAPE_SCRIPT = r'''
import importlib.abc, os, pathlib, sys, tempfile, threading, time

class _BlockFcntl(importlib.abc.MetaPathFinder):
    def find_spec(self, name, path=None, target=None):
        if name == "fcntl":
            raise ModuleNotFoundError("No module named 'fcntl'", name="fcntl")
        return None

sys.meta_path.insert(0, _BlockFcntl())
sys.modules.pop("fcntl", None)
from tests.fake_msvcrt import FakeMsvcrt
sys.modules["msvcrt"] = FakeMsvcrt()
sys.path.insert(0, os.path.join(os.getcwd(), "scripts"))

import file_lock, ars_mark_read, review_criteria_binding, adjudication_activity, inquiry_branch_ledger

assert file_lock.BACKEND == "msvcrt"
for consumer in (ars_mark_read, review_criteria_binding, adjudication_activity, inquiry_branch_ledger):
    assert consumer.file_lock is file_lock, consumer.__name__
tmp = pathlib.Path(tempfile.mkdtemp())

# adjudication: a read degrades to an exclusive lock; the lock file stays empty
store = tmp / "activity.json"
with adjudication_activity._store_lock(store, exclusive=False):
    store_lock = store.with_name(store.name + ".lock")
    assert store_lock.stat().st_size == 0
print("ADJUDICATION_READ_OK")

# adjudication policy: a reader waits (bounded), a writer does not wait
adjudication_activity.READER_FALLBACK_WAIT_SECONDS = 0.3
held = os.open(store_lock, os.O_RDWR | os.O_CREAT, 0o600)
file_lock.acquire(held, timeout=0)
started = time.monotonic()
try:
    with adjudication_activity._store_lock(store, exclusive=True):
        raise SystemExit("writer acquired a held lock")
except adjudication_activity.ActivityError:
    assert time.monotonic() - started < 0.2, "writer must not wait"
started = time.monotonic()
try:
    with adjudication_activity._store_lock(store, exclusive=False):
        raise SystemExit("reader acquired a held lock")
except adjudication_activity.ActivityError:
    assert 0.25 <= time.monotonic() - started < 3.0, "reader must wait the bounded window"
threading.Timer(0.1, file_lock.release, args=(held,)).start()
with adjudication_activity._store_lock(store, exclusive=False):
    pass
os.close(held)
print("ADJUDICATION_POLICY_OK")

# inquiry: the alpha refuses non-POSIX hosts
try:
    with inquiry_branch_ledger._transaction_lock(tmp / "passport.yaml"):
        raise SystemExit("inquiry did not refuse")
except inquiry_branch_ledger.ContractError as exc:
    assert "unavailable on this platform" in str(exc)
print("INQUIRY_REFUSES_OK")

# review-criteria binding: the blocking wait is bounded and reports BindingError
file_lock.WINDOWS_BLOCKING_WAIT_SECONDS = 0.1
manifest = tmp / "m.json"
manifest.write_text("{}")
lock_path = manifest.with_name(f".{manifest.name}.lock")
fd = os.open(lock_path, os.O_RDWR | os.O_CREAT, 0o600)
file_lock.acquire(fd, timeout=0)
try:
    with review_criteria_binding._locked(manifest):
        raise SystemExit("binding lock acquired while held")
except review_criteria_binding.BindingError as exc:
    assert "still held after 0.1s" in str(exc), str(exc)
file_lock.release(fd)
os.close(fd)
with review_criteria_binding._locked(manifest):
    # a LockTimeout raised inside the body must surface as itself, not as
    # BindingError blaming the manifest lock
    inner = os.open(lock_path, os.O_RDWR | os.O_CREAT, 0o600)
    try:
        file_lock.acquire(inner, timeout=0)
        raise SystemExit("inner acquire succeeded while the manifest lock is held")
    except file_lock.LockTimeout:
        pass
    finally:
        os.close(inner)
print("BINDING_BOUNDED_OK")

# ars-mark-read: bounded ledger lock with visible contention
log = tmp / "passport_human_read_log.yaml"
with ars_mark_read._ledger_lock(log):
    try:
        with ars_mark_read._ledger_lock(log, timeout_seconds=0.05):
            raise SystemExit("nested ledger lock acquired")
    except ars_mark_read.LedgerLockError as exc:
        assert "timed out" in str(exc)
print("MARK_READ_OK")
'''


def test_consumers_import_and_behave_with_fcntl_absent() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "-c", _WINDOWS_SHAPE_SCRIPT],
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stderr
    for marker in (
        "ADJUDICATION_READ_OK",
        "ADJUDICATION_POLICY_OK",
        "INQUIRY_REFUSES_OK",
        "BINDING_BOUNDED_OK",
        "MARK_READ_OK",
    ):
        assert marker in result.stdout, result.stdout
