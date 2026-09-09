"""Tests for the shared advisory file-lock helper (#845).

The real backend on the CI host is ``fcntl``.  The ``msvcrt`` branch is
exercised through a fake module that reproduces the documented Windows
semantics the helper depends on (byte-range lock at the current file
position, one holder per region, ``EACCES`` on contention, no shared mode)
so the Windows code path is tested for logic, not for platform behaviour.
Real Windows verification remains a manual step (see #845).
"""
from __future__ import annotations

import errno
import os
import threading
import time
from pathlib import Path

import pytest

from scripts import file_lock


def _open_lock(path: Path) -> int:
    return os.open(path, os.O_RDWR | os.O_CREAT, 0o600)


# --------------------------------------------------------------------------
# Real backend (fcntl on the CI host)
# --------------------------------------------------------------------------


def test_backend_constants_are_consistent() -> None:
    assert file_lock.BACKEND in {"fcntl", "msvcrt"}
    assert file_lock.SHARED_LOCKS_SUPPORTED == (file_lock.BACKEND == "fcntl")


def test_exclusive_lock_is_held_until_released(tmp_path: Path) -> None:
    lock = tmp_path / "x.lock"
    a = _open_lock(lock)
    b = _open_lock(lock)
    try:
        file_lock.acquire(a, exclusive=True, timeout=0)
        with pytest.raises(file_lock.LockTimeout):
            file_lock.acquire(b, exclusive=True, timeout=0)
        file_lock.release(a)
        file_lock.acquire(b, exclusive=True, timeout=0)
        file_lock.release(b)
    finally:
        os.close(a)
        os.close(b)


def test_lock_timeout_is_a_blocking_io_error_with_eagain(tmp_path: Path) -> None:
    lock = tmp_path / "x.lock"
    a = _open_lock(lock)
    b = _open_lock(lock)
    try:
        file_lock.acquire(a, exclusive=True, timeout=0)
        with pytest.raises(BlockingIOError) as info:
            file_lock.acquire(b, exclusive=True, timeout=0)
        assert isinstance(info.value, file_lock.LockTimeout)
        assert info.value.errno == errno.EAGAIN
        file_lock.release(a)
    finally:
        os.close(a)
        os.close(b)


def test_bounded_wait_expires_after_timeout(tmp_path: Path) -> None:
    lock = tmp_path / "x.lock"
    a = _open_lock(lock)
    b = _open_lock(lock)
    try:
        file_lock.acquire(a, exclusive=True, timeout=0)
        started = time.monotonic()
        with pytest.raises(file_lock.LockTimeout, match="0.2"):
            file_lock.acquire(b, exclusive=True, timeout=0.2)
        elapsed = time.monotonic() - started
        assert 0.15 <= elapsed < 3.0
        file_lock.release(a)
    finally:
        os.close(a)
        os.close(b)


def test_bounded_wait_succeeds_when_holder_releases(tmp_path: Path) -> None:
    lock = tmp_path / "x.lock"
    a = _open_lock(lock)
    b = _open_lock(lock)
    try:
        file_lock.acquire(a, exclusive=True, timeout=0)
        threading.Timer(0.15, file_lock.release, args=(a,)).start()
        file_lock.acquire(b, exclusive=True, timeout=5.0)
        file_lock.release(b)
    finally:
        os.close(a)
        os.close(b)


def test_blocking_acquire_waits_for_release(tmp_path: Path) -> None:
    lock = tmp_path / "x.lock"
    a = _open_lock(lock)
    b = _open_lock(lock)
    try:
        file_lock.acquire(a, exclusive=True, timeout=0)
        threading.Timer(0.15, file_lock.release, args=(a,)).start()
        started = time.monotonic()
        file_lock.acquire(b, exclusive=True, timeout=None)
        assert time.monotonic() - started >= 0.1
        file_lock.release(b)
    finally:
        os.close(a)
        os.close(b)


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
        file_lock.acquire(fd, exclusive=True, timeout=0)
        file_lock.release(fd)
        file_lock.acquire(fd, exclusive=False, timeout=0)
        file_lock.release(fd)
    finally:
        os.close(fd)
    assert lock.stat().st_size == 0


@pytest.mark.skipif(not file_lock.SHARED_LOCKS_SUPPORTED, reason="no shared locks")
def test_shared_locks_coexist_and_exclude_writers(tmp_path: Path) -> None:
    lock = tmp_path / "x.lock"
    r1 = _open_lock(lock)
    r2 = _open_lock(lock)
    w = _open_lock(lock)
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
        os.close(r1)
        os.close(r2)
        os.close(w)


# --------------------------------------------------------------------------
# msvcrt branch through a fake module
# --------------------------------------------------------------------------


class _FakeMsvcrt:
    """Minimal model of ``msvcrt.locking`` for the semantics the helper uses.

    * The lock covers ``nbytes`` from the current file position; the helper
      must position the descriptor at offset 0 before every call.
    * One holder per (file, region).  A second descriptor, or the same one
      again, fails immediately with ``EACCES`` under ``LK_NBLCK``.
    * ``LK_UNLCK`` by a non-holder fails with ``EACCES``.
    * There is no shared mode.
    """

    LK_NBLCK = 2
    LK_UNLCK = 0
    LK_LOCK = 1

    def __init__(self) -> None:
        self.holders: dict[tuple[int, int], int] = {}
        self.calls: list[tuple[int, int, int, int]] = []

    def locking(self, fd: int, mode: int, nbytes: int) -> None:
        info = os.fstat(fd)
        key = (info.st_dev, info.st_ino)
        position = os.lseek(fd, 0, os.SEEK_CUR)
        self.calls.append((fd, mode, nbytes, position))
        if position != 0 or nbytes != 1:
            raise AssertionError("helper must lock exactly byte 0")
        if mode == self.LK_NBLCK:
            if key in self.holders:
                raise OSError(errno.EACCES, "Permission denied")
            self.holders[key] = fd
            return
        if mode == self.LK_UNLCK:
            if self.holders.get(key) != fd:
                raise OSError(errno.EACCES, "Permission denied")
            del self.holders[key]
            return
        raise AssertionError(f"helper must not use blocking mode {mode}")


@pytest.fixture
def fake_windows(monkeypatch: pytest.MonkeyPatch) -> _FakeMsvcrt:
    fake = _FakeMsvcrt()
    monkeypatch.setattr(file_lock, "fcntl", None)
    monkeypatch.setattr(file_lock, "msvcrt", fake)
    return fake


def test_windows_exclusive_contention_and_release(
    tmp_path: Path, fake_windows: _FakeMsvcrt
) -> None:
    lock = tmp_path / "x.lock"
    a = _open_lock(lock)
    b = _open_lock(lock)
    try:
        file_lock.acquire(a, exclusive=True, timeout=0)
        with pytest.raises(file_lock.LockTimeout):
            file_lock.acquire(b, exclusive=True, timeout=0)
        file_lock.release(a)
        file_lock.acquire(b, exclusive=True, timeout=0)
        file_lock.release(b)
    finally:
        os.close(a)
        os.close(b)
    assert lock.stat().st_size == 0


def test_windows_shared_request_degrades_to_exclusive(
    tmp_path: Path, fake_windows: _FakeMsvcrt
) -> None:
    lock = tmp_path / "x.lock"
    r1 = _open_lock(lock)
    r2 = _open_lock(lock)
    try:
        file_lock.acquire(r1, exclusive=False, timeout=0)
        with pytest.raises(file_lock.LockTimeout):
            file_lock.acquire(r2, exclusive=False, timeout=0)
        file_lock.release(r1)
    finally:
        os.close(r1)
        os.close(r2)


def test_windows_positions_descriptor_at_zero_before_locking(
    tmp_path: Path, fake_windows: _FakeMsvcrt
) -> None:
    fd = _open_lock(tmp_path / "x.lock")
    try:
        os.lseek(fd, 7, os.SEEK_SET)
        file_lock.acquire(fd, exclusive=True, timeout=0)
        os.lseek(fd, 3, os.SEEK_SET)
        file_lock.release(fd)
    finally:
        os.close(fd)
    assert [call[3] for call in fake_windows.calls] == [0, 0]


def test_windows_blocking_acquire_is_bounded(
    tmp_path: Path, fake_windows: _FakeMsvcrt, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(file_lock, "WINDOWS_BLOCKING_WAIT_SECONDS", 0.2)
    lock = tmp_path / "x.lock"
    a = _open_lock(lock)
    b = _open_lock(lock)
    try:
        file_lock.acquire(a, exclusive=True, timeout=0)
        started = time.monotonic()
        with pytest.raises(file_lock.LockTimeout, match="0.2"):
            file_lock.acquire(b, exclusive=True, timeout=None)
        assert 0.15 <= time.monotonic() - started < 3.0
        file_lock.release(a)
    finally:
        os.close(a)
        os.close(b)


def test_windows_blocking_acquire_succeeds_on_release(
    tmp_path: Path, fake_windows: _FakeMsvcrt
) -> None:
    lock = tmp_path / "x.lock"
    a = _open_lock(lock)
    b = _open_lock(lock)
    try:
        file_lock.acquire(a, exclusive=True, timeout=0)
        threading.Timer(0.15, file_lock.release, args=(a,)).start()
        file_lock.acquire(b, exclusive=True, timeout=None)
        file_lock.release(b)
    finally:
        os.close(a)
        os.close(b)


def test_windows_edeadlock_counts_as_contention(
    tmp_path: Path, fake_windows: _FakeMsvcrt, monkeypatch: pytest.MonkeyPatch
) -> None:
    deadlock_errno = getattr(errno, "EDEADLOCK", errno.EDEADLK)

    def locking(fd: int, mode: int, nbytes: int) -> None:
        raise OSError(deadlock_errno, "Resource deadlock avoided")

    monkeypatch.setattr(fake_windows, "locking", locking)
    fd = _open_lock(tmp_path / "x.lock")
    try:
        with pytest.raises(file_lock.LockTimeout):
            file_lock.acquire(fd, exclusive=True, timeout=0)
    finally:
        os.close(fd)


def test_persistent_interruption_still_honours_the_deadline(
    tmp_path: Path, fake_windows: _FakeMsvcrt, monkeypatch: pytest.MonkeyPatch
) -> None:
    def locking(fd: int, mode: int, nbytes: int) -> None:
        raise InterruptedError(errno.EINTR, "Interrupted system call")

    monkeypatch.setattr(fake_windows, "locking", locking)
    fd = _open_lock(tmp_path / "x.lock")
    try:
        started = time.monotonic()
        with pytest.raises(file_lock.LockTimeout):
            file_lock.acquire(fd, exclusive=True, timeout=0.2)
        assert 0.15 <= time.monotonic() - started < 3.0
    finally:
        os.close(fd)


def test_windows_unexpected_oserror_propagates_unchanged(
    tmp_path: Path, fake_windows: _FakeMsvcrt, monkeypatch: pytest.MonkeyPatch
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
import errno, importlib.abc, os, pathlib, sys, tempfile, types

class _BlockFcntl(importlib.abc.MetaPathFinder):
    def find_spec(self, name, path=None, target=None):
        if name == "fcntl":
            raise ModuleNotFoundError("No module named 'fcntl'", name="fcntl")
        return None

sys.meta_path.insert(0, _BlockFcntl())
sys.modules.pop("fcntl", None)

fake = types.ModuleType("msvcrt")
fake.LK_NBLCK, fake.LK_UNLCK, fake.LK_LOCK = 2, 0, 1
holders = {}

def locking(fd, mode, nbytes):
    st = os.fstat(fd)
    key = (st.st_dev, st.st_ino)
    assert os.lseek(fd, 0, os.SEEK_CUR) == 0 and nbytes == 1
    if mode == fake.LK_NBLCK:
        if key in holders:
            raise OSError(errno.EACCES, "locked")
        holders[key] = fd
    elif mode == fake.LK_UNLCK:
        if holders.get(key) != fd:
            raise OSError(errno.EACCES, "not holder")
        del holders[key]
    else:
        raise AssertionError(mode)

fake.locking = locking
sys.modules["msvcrt"] = fake
sys.path.insert(0, os.path.join(os.getcwd(), "scripts"))

import file_lock, ars_mark_read, review_criteria_binding, adjudication_activity, inquiry_branch_ledger

assert file_lock.BACKEND == "msvcrt" and not file_lock.SHARED_LOCKS_SUPPORTED
tmp = pathlib.Path(tempfile.mkdtemp())

# adjudication: a read degrades to an exclusive lock; the lock file stays empty
import threading, time
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
    pass
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
    import subprocess
    import sys

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
