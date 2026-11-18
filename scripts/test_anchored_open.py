"""Tests for scripts/_anchored_open.py and its six call sites (#1092).

Windows has no ``dir_fd``, no ``O_DIRECTORY`` and no ``O_NOFOLLOW``, and
``os.open()`` cannot open a directory there.  CI has no Windows job, so the
``windows`` fixture reproduces those two facts on any host: it empties
``os.supports_dir_fd`` and wraps ``os.open`` so that a ``dir_fd`` argument
raises ``NotImplementedError`` and opening a directory raises
``PermissionError``.  Any call site that still walks with ``dir_fd`` or opens
a directory then fails here the way it failed on Windows.
"""
from __future__ import annotations

import errno
import json
import os
import stat
import types
from pathlib import Path

import pytest

import _anchored_open
import review_criteria_binding as binding
import run_review_criteria_constructive_value as runner
import score_review_criteria_constructive_value as scorer
from scripts import inquiry_branch_ledger as ledger
from scripts import revision_roadmap as roadmap

PAYLOAD = {"ok": True}
HAS_SYMLINK = hasattr(os, "symlink")


@pytest.fixture
def windows(monkeypatch):
    real_open = os.open

    def fake_open(path, flags, mode=0o777, *, dir_fd=None):
        if dir_fd is not None:
            raise NotImplementedError("dir_fd unavailable on this platform")
        if isinstance(path, (str, os.PathLike)) and os.path.isdir(path):
            raise PermissionError(errno.EACCES, "Permission denied", str(path))
        return real_open(path, flags, mode)

    monkeypatch.setattr(os, "supports_dir_fd", frozenset())
    monkeypatch.setattr(os, "open", fake_open)
    assert not _anchored_open.descriptor_relative_supported()


@pytest.fixture
def tree(tmp_path):
    root = tmp_path / "root"
    (root / "sub").mkdir(parents=True)
    (root / "sub" / "artifact.json").write_text(json.dumps(PAYLOAD), encoding="utf-8")
    return root


def _read_fd(fd: int) -> bytes:
    try:
        return os.read(fd, 1024)
    finally:
        os.close(fd)


def _link(tmp_path, tree):
    """Add ``root/linkdir -> outside`` and ``root/sub/leaf.json -> outside file``."""
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "artifact.json").write_text("{}", encoding="utf-8")
    try:
        os.symlink(outside, tree / "linkdir", target_is_directory=True)
        os.symlink(outside / "artifact.json", tree / "sub" / "leaf.json")
    except (OSError, NotImplementedError):
        pytest.skip("symlinks unavailable")


# --- backend choice ---------------------------------------------------------


def test_posix_uses_descriptor_relative_backend():
    if os.name == "nt":
        pytest.skip("POSIX only")
    assert _anchored_open.descriptor_relative_supported()


def test_windows_name_selects_path_backend(monkeypatch):
    monkeypatch.setattr(os, "name", "nt")
    assert not _anchored_open.descriptor_relative_supported()


# --- the helper, both backends ---------------------------------------------


@pytest.mark.parametrize("simulate_windows", [False, True])
def test_open_under_reads_file(request, tree, simulate_windows):
    if simulate_windows:
        request.getfixturevalue("windows")
    fd = _anchored_open.open_under(tree, ["sub", "artifact.json"], nofollow_anchor=True)
    assert json.loads(_read_fd(fd)) == PAYLOAD


@pytest.mark.parametrize("simulate_windows", [False, True])
def test_open_under_rejects_symlinked_directory(request, tmp_path, tree, simulate_windows):
    _link(tmp_path, tree)
    if simulate_windows:
        request.getfixturevalue("windows")
    with pytest.raises(OSError) as info:
        _anchored_open.open_under(tree, ["linkdir", "artifact.json"])
    # O_DIRECTORY | O_NOFOLLOW on a symlink reports ELOOP or ENOTDIR by kernel.
    assert info.value.errno in {errno.ELOOP, errno.ENOTDIR}
    if simulate_windows:
        assert info.value.errno == errno.ELOOP


@pytest.mark.parametrize("simulate_windows", [False, True])
def test_open_under_rejects_symlinked_leaf(request, tmp_path, tree, simulate_windows):
    _link(tmp_path, tree)
    if simulate_windows:
        request.getfixturevalue("windows")
    with pytest.raises(OSError) as info:
        _anchored_open.open_under(tree, ["sub", "leaf.json"])
    assert info.value.errno == errno.ELOOP


@pytest.mark.parametrize("simulate_windows", [False, True])
def test_open_under_missing_file_is_a_plain_oserror(request, tree, simulate_windows):
    if simulate_windows:
        request.getfixturevalue("windows")
    with pytest.raises(FileNotFoundError):
        _anchored_open.open_under(tree, ["sub", "absent.json"])


def test_open_under_file_in_the_middle_of_the_path(windows, tree):
    with pytest.raises(NotADirectoryError):
        _anchored_open.open_under(tree, ["sub", "artifact.json", "deeper"])


@pytest.mark.parametrize("simulate_windows", [False, True])
def test_nofollow_anchor_rejects_a_symlinked_root(request, tmp_path, tree, simulate_windows):
    _link(tmp_path, tree)
    if simulate_windows:
        request.getfixturevalue("windows")
    with pytest.raises(OSError):
        _anchored_open.open_under(
            tree / "linkdir", ["artifact.json"], nofollow_anchor=True
        )
    # Without the flag the anchor is trusted, on both backends.
    assert _read_fd(_anchored_open.open_under(tree / "linkdir", ["artifact.json"]))


def test_path_backend_nofollow_anchor_names_the_cause(windows, tmp_path, tree):
    _link(tmp_path, tree)
    with pytest.raises(_anchored_open.SymlinkRejected) as info:
        _anchored_open.open_under(tree / "linkdir", ["artifact.json"], nofollow_anchor=True)
    assert info.value.errno == errno.ELOOP and "best-effort" in str(info.value)


@pytest.mark.parametrize(
    "component", ["", ".", "a/b", "a" + os.sep + "b", "/etc/passwd"]
)
def test_open_under_rejects_non_plain_components(tree, component):
    with pytest.raises(ValueError):
        _anchored_open.open_under(tree, ["sub", component])


def test_open_under_rejects_windows_drive_and_stream_components(tree, monkeypatch):
    import ntpath

    monkeypatch.setattr(os.path, "splitdrive", ntpath.splitdrive)
    with pytest.raises(ValueError):
        _anchored_open.open_under(tree, ["D:secret.json"])
    monkeypatch.setattr(os, "name", "nt")
    with pytest.raises(ValueError):
        _anchored_open.open_under(tree, ["sub", "artifact.json:stream"])


def test_posix_filenames_with_a_colon_are_still_plain(tree):
    if os.name == "nt":
        pytest.skip("POSIX only")
    (tree / "a:b.json").write_text("{}", encoding="utf-8")
    assert _read_fd(_anchored_open.open_under(tree, ["a:b.json"]))


def test_scorer_imports_in_package_mode():
    """`python -m scripts.<module>` has the repo root, not scripts/, on sys.path."""
    import subprocess
    import sys

    repo = Path(__file__).resolve().parent.parent
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    result = subprocess.run(
        [sys.executable, "-c", "import scripts.score_review_criteria_constructive_value"],
        cwd=repo, env=env, capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr


def test_open_under_needs_a_component(tree):
    with pytest.raises(ValueError):
        _anchored_open.open_under(tree, [])


def test_path_backend_rejects_a_reparse_point_without_symlink_mode(windows, tree, monkeypatch):
    """A junction reports no S_IFLNK; only the reparse attribute shows it."""
    real_lstat = os.lstat

    def lstat(path, *args, **kwargs):
        info = real_lstat(path, *args, **kwargs)
        if Path(path).name == "sub":
            return types.SimpleNamespace(
                st_mode=info.st_mode,
                st_ino=info.st_ino,
                st_dev=info.st_dev,
                st_file_attributes=stat.FILE_ATTRIBUTE_REPARSE_POINT
                if hasattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT")
                else 0x400,
            )
        return info

    monkeypatch.setattr(os, "lstat", lstat)
    with pytest.raises(_anchored_open.SymlinkRejected) as info:
        _anchored_open.open_under(tree, ["sub", "artifact.json"])
    assert "reparse point" in str(info.value)
    assert "best-effort" in str(info.value)


@pytest.mark.skipif(not HAS_SYMLINK, reason="needs symlinks")
def test_path_backend_rejects_leaf_swapped_before_open(windows, monkeypatch, tree):
    """lstat saw one file, the open reached another: the identity check fires."""
    leaf = tree / "sub" / "artifact.json"
    other = tree / "sub" / "other.json"
    other.write_text("{}", encoding="utf-8")
    swapped = []
    open_through_fake = os.open

    def swapping_open(path, flags, mode=0o777, *, dir_fd=None):
        if Path(path) == leaf and not swapped:
            swapped.append(True)
            os.replace(other, leaf)
        return open_through_fake(path, flags, mode, dir_fd=dir_fd)

    monkeypatch.setattr(os, "open", swapping_open)
    with pytest.raises(_anchored_open.SymlinkRejected):
        _anchored_open.open_under(tree, ["sub", "artifact.json"])


@pytest.mark.skipif(not HAS_SYMLINK, reason="needs symlinks")
def test_path_backend_rejects_parent_swapped_for_a_symlink_after_open(
    windows, monkeypatch, tmp_path, tree
):
    """The re-check after the open narrows, and catches, a parent swap."""
    leaf = tree / "sub" / "artifact.json"
    outside = tmp_path / "elsewhere"
    outside.mkdir()
    (outside / "artifact.json").write_text("{}", encoding="utf-8")
    open_through_fake = os.open

    def open_then_swap(path, flags, mode=0o777, *, dir_fd=None):
        fd = open_through_fake(path, flags, mode, dir_fd=dir_fd)
        if Path(path) == leaf:
            os.rename(tree / "sub", tree / "sub.moved")
            os.symlink(outside, tree / "sub", target_is_directory=True)
        return fd

    monkeypatch.setattr(os, "open", open_then_swap)
    with pytest.raises(_anchored_open.SymlinkRejected):
        _anchored_open.open_under(tree, ["sub", "artifact.json"])


def test_open_explicit_path_absolute_and_relative(windows, tree, monkeypatch):
    assert json.loads(_read_fd(_anchored_open.open_explicit_path(tree / "sub" / "artifact.json"))) == PAYLOAD
    monkeypatch.chdir(tree)
    assert json.loads(_read_fd(_anchored_open.open_explicit_path(Path("sub/artifact.json")))) == PAYLOAD


def test_fsync_directory_skips_where_directories_cannot_be_opened(windows, tree):
    _anchored_open.fsync_directory(tree)


def test_fsync_directory_posix_still_fsyncs(tree, monkeypatch):
    if os.name == "nt":
        pytest.skip("POSIX only")
    calls = []
    real_fsync = os.fsync
    monkeypatch.setattr(os, "fsync", lambda fd: (calls.append(fd), real_fsync(fd))[1])
    _anchored_open.fsync_directory(tree)
    assert len(calls) == 1


def test_platform_limitation_message_names_the_platform():
    message = str(_anchored_open.PlatformLimitation("no dir_fd"))
    assert message.startswith("[Errno") and "platform limitation" in message


# --- the call sites, on the simulated Windows host ---------------------------
# Site 3 (the artifact reader that check_673 guards) is tested in its own
# test module, the only place that guard lets name it.


def test_site1_revision_roadmap_store(windows, tree):
    store = roadmap.ArtifactStore(tree)
    assert json.loads(store._open_relative("sub/artifact.json", "repro")) == PAYLOAD


@pytest.mark.skipif(not HAS_SYMLINK, reason="needs symlinks")
def test_site1_revision_roadmap_store_rejects_symlink(windows, tmp_path, tree):
    _link(tmp_path, tree)
    with pytest.raises(roadmap.ContractError) as info:
        roadmap.ArtifactStore(tree)._open_relative("sub/leaf.json", "repro")
    assert "no-symlink" in "".join(info.value.args[0]) or "symlink" in str(info.value)


def test_site2_review_criteria_binding(windows, tree):
    fd = binding._open_nofollow(tree / "sub" / "artifact.json", os.O_RDONLY)
    assert json.loads(_read_fd(fd)) == PAYLOAD
    assert json.loads(binding._read_bytes(tree / "sub" / "artifact.json", 1_000_000)) == PAYLOAD


def test_site2_binding_errors_are_controlled_not_tracebacks(windows, tree, monkeypatch):
    with pytest.raises(binding.BindingError):
        binding._open_nofollow(Path(os.sep), os.O_RDONLY)
    with pytest.raises(binding.BindingError):
        binding._open_nofollow(tree / "sub" / "absent.json", os.O_RDONLY)

    def boom(path, flags=os.O_RDONLY):
        raise NotImplementedError("dir_fd unavailable on this platform")

    monkeypatch.setattr(_anchored_open, "open_explicit_path", boom)
    # binding may hold the package-path module object; patch both names.
    monkeypatch.setattr(binding._anchored_open, "open_explicit_path", boom)
    with pytest.raises(binding.BindingError):
        binding._open_nofollow(tree / "sub" / "artifact.json", os.O_RDONLY)


@pytest.mark.skipif(not HAS_SYMLINK, reason="needs symlinks")
def test_site2_binding_rejects_symlink_as_binding_error(windows, tmp_path, tree):
    _link(tmp_path, tree)
    with pytest.raises(binding.BindingError):
        binding._read_bytes(tree / "linkdir" / "artifact.json", 1_000_000)


def test_site4_runner_safe_explicit_file(windows, tree):
    assert json.loads(runner._safe_explicit_file(tree / "sub" / "artifact.json")) == PAYLOAD


@pytest.mark.skipif(not HAS_SYMLINK, reason="needs symlinks")
def test_site4_runner_rejects_symlink(windows, tmp_path, tree):
    _link(tmp_path, tree)
    with pytest.raises(runner.MeasurementError):
        runner._safe_explicit_file(tree / "linkdir" / "artifact.json")


def test_site5_scorer_open_nofollow(windows, tree):
    assert json.loads(_read_fd(scorer._open_nofollow(tree / "sub" / "artifact.json"))) == PAYLOAD


@pytest.mark.skipif(not HAS_SYMLINK, reason="needs symlinks")
def test_site5_scorer_rejects_symlink(windows, tmp_path, tree):
    _link(tmp_path, tree)
    with pytest.raises(scorer.ScoreError):
        scorer._open_nofollow(tree / "linkdir" / "artifact.json")


def test_site6_ledger_fsync_directory(windows, tree):
    ledger._fsync_directory(tree)


# --- the helper's ValueError never escapes a call site -----------------------
# open_under raises ValueError for a component that is not a plain name, and
# os.open raises it for an embedded NUL.  Each call site turns it into its own
# error type.  (Site 3 is tested in its own test module.)


def _raised_as_windows(monkeypatch, call):
    """Run ``call`` with ``os.name == "nt"`` and return what it raised.

    ``os.name`` is restored before the caller asserts: pathlib cannot build a
    path while a POSIX host claims to be Windows, and pytest builds one to
    report a failure.
    """
    with monkeypatch.context() as patch:
        patch.setattr(os, "name", "nt")
        try:
            call()
        except Exception as exc:  # noqa: BLE001 - the caller checks the type
            return exc
    return None


def test_site1_roadmap_store_turns_helper_valueerror_into_contract_error(tree, monkeypatch):
    store = roadmap.ArtifactStore(tree)
    with pytest.raises(roadmap.ContractError) as info:
        store._open_relative("sub/a\x00b.json", "repro")
    assert "bundle repro" in "".join(info.value.args[0])
    for relative in ("sub/artifact.json:ads", "C:artifact.json"):
        raised = _raised_as_windows(
            monkeypatch, lambda: store._open_relative(relative, "repro")
        )
        assert type(raised) is roadmap.ContractError, repr(raised)


def test_site1_roadmap_store_keeps_its_own_contract_errors(tree):
    (tree / "sub" / "big.json").write_bytes(b"x" * (roadmap.MAX_ARTIFACT_BYTES + 1))
    with pytest.raises(roadmap.ContractError) as info:
        roadmap.ArtifactStore(tree)._open_relative("sub/big.json", "repro")
    assert "exceeds" in "".join(info.value.args[0])


def test_site2_binding_turns_helper_valueerror_into_binding_error(tree, monkeypatch):
    with pytest.raises(binding.BindingError) as info:
        binding._open_nofollow(tree / "sub" / "a\x00b.json", os.O_RDONLY)
    assert type(info.value) is binding.BindingError
    stream = Path("sub/artifact.json:ads")
    monkeypatch.chdir(tree)
    raised = _raised_as_windows(
        monkeypatch, lambda: binding._open_nofollow(stream, os.O_RDONLY)
    )
    assert type(raised) is binding.BindingError, repr(raised)


def test_site4_runner_turns_helper_valueerror_into_measurement_error(tree, monkeypatch):
    with pytest.raises(runner.MeasurementError):
        runner._safe_explicit_file(tree / "sub" / "a\x00b.json")
    stream = tree / "sub" / "artifact.json:ads"
    raised = _raised_as_windows(monkeypatch, lambda: runner._safe_explicit_file(stream))
    assert type(raised) is runner.MeasurementError, repr(raised)


def test_site5_scorer_turns_helper_valueerror_into_score_error(tree, monkeypatch):
    with pytest.raises(scorer.ScoreError) as info:
        scorer._open_nofollow(tree / "sub" / "a\x00b.json")
    assert type(info.value) is scorer.ScoreError
    stream = tree / "sub" / "artifact.json:ads"
    raised = _raised_as_windows(monkeypatch, lambda: scorer._open_nofollow(stream))
    assert type(raised) is scorer.ScoreError, repr(raised)
