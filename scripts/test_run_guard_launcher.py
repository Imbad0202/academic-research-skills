"""Launch-layer tests for hooks/run_guard.sh (#454 Windows Python hook portability).

The existing test_ars_write_scope_guard.py drives the guard via [sys.executable, guard]
— it never exercises INTERPRETER RESOLUTION, which is the entire #454 bug class (a Windows
`python3` that is a 0-byte Microsoft Store alias stub, not real Python). These tests cover
the launcher's job: find a REAL python (skipping stubs), run the guard as a SUPERVISED
subprocess, and degrade to pass-through+exit-0 (never block, never spam) when no real python
is found OR the guard subprocess is broken.

Design: docs/design/2026-06-17-454-windows-python-hook-portability-design.md (§3.1–3.6).

Mechanism: each test builds a temp `bin/` dir, puts fake `py`/`python3`/`python` programs
in it, and runs the launcher with PATH=that bin (plus a real python for the cases that need
one). A "stub" is a program that exits non-zero / prints nothing (mimicking the 0-byte Store
alias as the marker probe sees it). The launcher must:
  - emit canonical pass-through JSON {"hookSpecificOutput":{"hookEventName":"PreToolUse"}}
    and exit 0 when no real python verifies, or when the guard subprocess misbehaves;
  - forward the guard's stdout JSON verbatim (deny via permissionDecision:"deny", or
    pass-through) when a real python runs the guard cleanly;
  - stay SILENT on stderr on the degraded paths (PreToolUse is a hot path — any per-call
    stderr is the log spam #454 is about).

NOTE (honest limitation): this is a POSIX-host simulation. The real Windows Store-alias path,
`py.exe -3` under Git Bash, Git Bash path conversion, CRLF, and the no-Git-Bash PowerShell
fallback still need a Windows repro (tracked in the spec §6).
"""

import functools
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAUNCHER = os.path.join(REPO_ROOT, "hooks", "run_guard.sh")
GUARD = os.path.join(REPO_ROOT, "scripts", "ars_write_scope_guard.py")
PASS_THROUGH = {"hookSpecificOutput": {"hookEventName": "PreToolUse"}}

# A real python to hand the launcher when a test needs the guard to actually run.
REAL_PY = sys.executable


def _write_exec(path, body):
    """Write an executable script at `path` with `body` (a /bin/sh script). The default
    encoding is kept on purpose: the body can embed sys.executable, whose bytes must match
    the filesystem's, unlike the Python source written by _make_plugin_layout (#1021)."""
    with open(path, "w") as fh:
        fh.write(body)
    os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)


def _stub(path):
    """A non-executing stub: prints nothing, exits 1 — what the marker probe sees for a
    0-byte Microsoft Store alias when invoked non-interactively."""
    _write_exec(path, "#!/bin/sh\nexit 1\n")


def _fake_real_python(path, real=REAL_PY):
    """A fake `python3`/`python`/`py` that behaves like a real interpreter by delegating to
    an actual python. Handles the marker probe (`-c ...`) and running the guard script."""
    _write_exec(path, f'#!/bin/sh\nexec "{real}" "$@"\n')


def _fake_recording_python(path, marker_file, tag, real=REAL_PY):
    """A fake python3/python/py that appends `tag` to `marker_file` before delegating to a
    real interpreter, so a test can assert WHICH candidate actually ran instead of only
    checking the final decision (#1130 item 7: several different candidates could produce an
    identical decision, so checking the decision alone does not prove which one executed)."""
    _write_exec(path, f'#!/bin/sh\necho {tag} >> "{marker_file}"\nexec "{real}" "$@"\n')


@functools.lru_cache(maxsize=1)
def _minimal_sys_path():
    """A directory with just the external commands run_guard.sh actually calls (cat, dirname,
    mktemp, rm, setsid, sleep, timeout, sh, uname, true) and nothing named py/python3/python, unlike
    _SYS_PATH (real /usr/bin, /bin, ...), which on this host already has a real python3 and
    would silently defeat a test meaning to simulate a host with no interpreter anywhere but
    WindowsApps (#1130 item 7). command and kill are shell builtins, not external binaries,
    so nothing needs to be symlinked for them."""
    d = tempfile.mkdtemp(prefix="ars_min_sys_path_")
    for name in ("sh", "cat", "dirname", "mktemp", "rm", "setsid", "sleep", "timeout", "uname", "true"):
        real = shutil.which(name)
        if real:
            os.symlink(real, os.path.join(d, name))
    return d


def _fake_uname(path, kernel="MINGW64_NT-10.0"):
    """A fake `uname` that reports a Windows-shell kernel string, so a test can engage
    run_guard.sh's WindowsApps-exclusion walk without a real MINGW/MSYS/Cygwin host (#1130
    round 2 item 1: there is no production env-var override for this; the gate reads real
    `uname -s` output only)."""
    _write_exec(path, f'#!/bin/sh\nprintf "%s\\n" "{kernel}"\n')


@functools.lru_cache(maxsize=1)
def _windows_uname_dir():
    """A directory holding only a fake `uname` that reports a MINGW-style kernel string.
    Must be placed before _minimal_sys_path() (which symlinks the real `uname`) on PATH for
    any test that needs run_guard.sh's walk to engage."""
    d = tempfile.mkdtemp(prefix="ars_win_uname_")
    _fake_uname(os.path.join(d, "uname"))
    return d


@functools.lru_cache(maxsize=1)
def _linux_uname_dir():
    """A directory holding only a fake `uname` that reports a plain Linux kernel string.
    Must be placed before _minimal_sys_path() (which symlinks the real `uname`) on PATH for
    any test that needs run_guard.sh's walk to stay off regardless of what the actual test
    host's own `uname -s` happens to report (#1130 round 4 item 3: a test that instead relied
    on the ambient host not being MINGW/MSYS/Cygwin would fail for real on such a host)."""
    d = tempfile.mkdtemp(prefix="ars_linux_uname_")
    _fake_uname(os.path.join(d, "uname"), kernel="Linux")
    return d


# System dirs that hold sh/cat/grep/command/mktemp/sleep/kill/timeout. bin_dir goes FIRST
# on PATH so our injected fake py/python3/python (and any stub that shadows the system one)
# win interpreter resolution, while the launcher's own shell utilities still resolve.
_SYS_PATH = "/usr/bin:/bin:/usr/sbin:/sbin"
_SH = shutil.which("sh") or "/bin/sh"
_LAUNCHER_TIMEOUT = 45  # generous so a (bounded) hanging-candidate test can't false-fail

# #545: GENEROUS default bound. For decision-forwarding tests the bound is pure safety
# margin — it only ever elapses when a candidate actually hangs — and the old pinned "1"
# left so little margin that interpreter startup + the guard run could overrun it under
# machine load (worse on hosts without a `timeout` binary, where the watchdog's done-file
# handshake races completions near the bound). The launcher then degraded BY DESIGN to
# pass-through and deny-expecting tests failed in rotation. Hanging-candidate tests are
# the ONLY ones whose runtime scales with the bound (they wait it out to kill the hung
# probe), so they override with _HANG_PROBE_BOUND — small for speed, but not the flaky
# "1": the same bound also clocks the real python3 probe and the guard run inside them,
# so it still needs load headroom.
_DEFAULT_PROBE_BOUND = "30"
_HANG_PROBE_BOUND = "5"


def _run_launcher(bin_dir, payload, extra_env=None, launcher=LAUNCHER, cwd=None):
    """Run the launcher with PATH = bin_dir + system dirs (bin_dir first, so injected
    interpreters shadow the real ones). Returns (exit_code, stdout, stderr).

    `launcher` defaults to the repo's real launcher; pass an alternate path to run a copy from
    a temp plugin layout (the only way to exercise a broken/alternate guard now that the
    ARS_GUARD_PATH_FOR_TEST back door is gone — the guard is ALWAYS resolved from the
    launcher's own ../scripts/, P2-e)."""
    path = bin_dir + os.pathsep + _SYS_PATH
    env = {
        "PATH": path,
        "ARS_PROBE_BOUND": _DEFAULT_PROBE_BOUND,  # #545: see the constant's comment
        # The launcher must resolve the guard from its OWN path, not any var (codex P1).
        # We deliberately do NOT set CLAUDE_PLUGIN_ROOT in most tests.
    }
    if extra_env:
        env.update(extra_env)
    proc = subprocess.run(
        [_SH, launcher],
        input=json.dumps(payload),
        env=env,
        capture_output=True,
        text=True,
        timeout=_LAUNCHER_TIMEOUT,
        cwd=cwd,
    )
    return proc.returncode, proc.stdout, proc.stderr


def _make_plugin_layout(base, guard_body):
    """Build a temp plugin layout under `base`: hooks/run_guard.sh (real launcher copy) +
    scripts/ars_write_scope_guard.py (a guard whose body is `guard_body`) + the manifest the
    real guard needs. Returns the path to the copied launcher.

    This is how a test runs an ALTERNATE/broken guard without a production back door: the
    launcher resolves the guard from its OWN ../scripts/, so we plant the guard there (P2-e)."""
    os.makedirs(os.path.join(base, "hooks"))
    os.makedirs(os.path.join(base, "scripts"))
    launcher_copy = os.path.join(base, "hooks", "run_guard.sh")
    shutil.copy(LAUNCHER, launcher_copy)
    with open(os.path.join(base, "scripts", "ars_write_scope_guard.py"), "w", encoding="utf-8") as fh:
        fh.write(guard_body)
    # The real guard reads this manifest; copy it so an unmodified-guard layout also works.
    manifest = os.path.join(os.path.dirname(GUARD), "ars_phase_scope_manifest.json")
    shutil.copy(manifest, os.path.join(base, "scripts", "ars_phase_scope_manifest.json"))
    return launcher_copy


def _bucket_a_payload(workspace, file_path):
    """A Bucket A subagent Write payload (research_architect_agent is Bucket A)."""
    return {
        "tool_name": "Write",
        "cwd": workspace,
        "agent_type": "research_architect_agent",
        "tool_input": {"file_path": file_path, "content": "x"},
    }


class LauncherNoPythonTest(unittest.TestCase):
    """No real python anywhere -> pass-through + exit 0 + silent (Plan A, spec §3.2)."""

    def _assert_clean_passthrough(self, code, out, err):
        self.assertEqual(code, 0, f"must exit 0, got {code}; stderr={err!r}")
        self.assertEqual(json.loads(out), PASS_THROUGH, f"must emit canonical pass-through; got {out!r}")
        self.assertEqual(err.strip(), "", f"must be SILENT on hot-path stderr; got {err!r}")

    def test_only_silent_stubs_on_path(self):
        # All three candidates are stubs that exit 1 and print nothing (the marker probe sees
        # exactly what a 0-byte Store alias produces). bin_dir is FIRST on PATH so these
        # shadow any real system python.
        with tempfile.TemporaryDirectory() as bin_dir:
            for name in ("py", "python3", "python"):
                _stub(os.path.join(bin_dir, name))
            code, out, err = _run_launcher(bin_dir, {"tool_name": "Bash", "tool_input": {"command": "ls"}})
            self._assert_clean_passthrough(code, out, err)

    def test_stubs_that_print_error_to_stderr(self):
        # A different stub variant: exits 1 AND writes a Windows-style error to stderr (closer
        # to "is not recognized" / Store-stub noise). The marker check is on STDOUT, so these
        # are still rejected. Confirms the launcher keys on the stdout marker, not exit text.
        with tempfile.TemporaryDirectory() as bin_dir:
            for name in ("py", "python3", "python"):
                _write_exec(os.path.join(bin_dir, name),
                            "#!/bin/sh\necho 'not a real python' 1>&2\nexit 9\n")
            code, out, err = _run_launcher(bin_dir, {"tool_name": "Write", "tool_input": {"file_path": "/x", "content": "y"}})
            self._assert_clean_passthrough(code, out, err)

    def test_marker_printed_but_nonzero_exit_rejected(self):
        """P1-a: a candidate that PRINTS the exact marker on stdout but EXITS NON-ZERO must be
        rejected (a half-broken interpreter, or a stub that echoes then fails). The probe keys
        on `exit 0 AND marker`, not the marker alone -> no real python -> pass-through."""
        with tempfile.TemporaryDirectory() as bin_dir:
            for name in ("py", "python3", "python"):
                # Print the marker to stdout (what a REAL probe would print) but exit 9.
                # Must still be rejected because the exit status is non-zero.
                _write_exec(os.path.join(bin_dir, name),
                            "#!/bin/sh\nprintf 'ARS_PY_OK'\nexit 9\n")
            code, out, err = _run_launcher(bin_dir, {"tool_name": "Bash", "tool_input": {"command": "ls"}})
            self._assert_clean_passthrough(code, out, err)

    def test_no_timeout_binary_present(self):
        """Launcher must still work (and not hang) when the `timeout` binary is bypassed —
        forces the process-group watchdog fallback via ARS_GUARD_FORCE_WATCHDOG."""
        with tempfile.TemporaryDirectory() as bin_dir:
            for name in ("py", "python3", "python"):
                _stub(os.path.join(bin_dir, name))
            code, out, err = _run_launcher(bin_dir, {"tool_name": "Bash", "tool_input": {"command": "ls"}},
                                           extra_env={"ARS_GUARD_FORCE_WATCHDOG": "1"})
            self._assert_clean_passthrough(code, out, err)


class LauncherRealPythonForwardsTest(unittest.TestCase):
    """A real python is found -> launcher runs the guard and forwards its JSON decision."""

    def test_in_scope_write_passthrough_forwarded(self):
        with tempfile.TemporaryDirectory() as bin_dir, tempfile.TemporaryDirectory() as ws:
            _fake_real_python(os.path.join(bin_dir, "python3"))
            # research_architect_agent's allowed dir — an in-scope write should pass through.
            # Use the agent's actual allowed glob area; a clearly in-scope path: workspace root file
            # owned by main session is simplest, but we want the guard to RUN and say pass-through.
            payload = {"tool_name": "Write", "cwd": ws,
                       "tool_input": {"file_path": os.path.join(ws, "notes.md"), "content": "x"}}
            code, out, err = _run_launcher(bin_dir, payload, extra_env={"CLAUDE_PROJECT_DIR": ws})
            self.assertEqual(code, 0)
            decision = json.loads(out)
            self.assertNotIn("permissionDecision", decision["hookSpecificOutput"])

    def test_out_of_scope_bucket_a_deny_forwarded(self):
        with tempfile.TemporaryDirectory() as bin_dir, tempfile.TemporaryDirectory() as ws:
            _fake_real_python(os.path.join(bin_dir, "python3"))
            # Bucket A agent writing outside its allowed globs -> guard denies via JSON.
            payload = _bucket_a_payload(ws, os.path.join(ws, "totally_out_of_scope_dir", "x.md"))
            code, out, err = _run_launcher(bin_dir, payload, extra_env={"CLAUDE_PROJECT_DIR": ws})
            self.assertEqual(code, 0, f"guard always exits 0; got {code} err={err!r}")
            decision = json.loads(out)
            self.assertEqual(decision["hookSpecificOutput"].get("permissionDecision"), "deny",
                             f"out-of-scope Bucket A write must be denied via forwarded JSON; got {out!r}")

    def test_bash_denied_for_bucket_a_forwarded(self):
        with tempfile.TemporaryDirectory() as bin_dir, tempfile.TemporaryDirectory() as ws:
            _fake_real_python(os.path.join(bin_dir, "python3"))
            payload = {"tool_name": "Bash", "cwd": ws, "agent_type": "research_architect_agent",
                       "tool_input": {"command": "rm -rf /"}}
            code, out, err = _run_launcher(bin_dir, payload, extra_env={"CLAUDE_PROJECT_DIR": ws})
            self.assertEqual(code, 0)
            decision = json.loads(out)
            self.assertEqual(decision["hookSpecificOutput"].get("permissionDecision"), "deny")


class LauncherForeignTimeoutTest(unittest.TestCase):
    """#970: a `timeout` on PATH that rejects the GNU form (the Windows built-in timeout.exe
    under Git for Windows) must route to the watchdog fallback, not fail every bounded call
    and leave the guard passing everything through."""

    def test_foreign_timeout_still_forwards_deny(self):
        with tempfile.TemporaryDirectory() as bin_dir, tempfile.TemporaryDirectory() as ws:
            _fake_real_python(os.path.join(bin_dir, "python3"))
            # Mimics timeout.exe given `1s true` / `30s python3 ...`: error text, exit 1.
            _write_exec(os.path.join(bin_dir, "timeout"),
                        "#!/bin/sh\necho 'ERROR: Invalid syntax.' >&2\nexit 1\n")
            payload = _bucket_a_payload(ws, os.path.join(ws, "totally_out_of_scope_dir", "x.md"))
            code, out, err = _run_launcher(bin_dir, payload, extra_env={"CLAUDE_PROJECT_DIR": ws})
            self.assertEqual(code, 0, f"launcher always exits 0; got {code} err={err!r}")
            decision = json.loads(out)
            self.assertEqual(decision["hookSpecificOutput"].get("permissionDecision"), "deny",
                             f"a foreign timeout must not disable the guard; got {out!r}")

    def test_hanging_true_does_not_stall_timeout_probe(self):
        """The usability probe runs the `true` on PATH; one that hangs and ignores SIGTERM
        must not stall the launcher (`-k` bounds the probe), and the guard still decides."""
        real_timeout = shutil.which("timeout")
        if not real_timeout:
            self.skipTest("no `timeout` binary on this host")
        with tempfile.TemporaryDirectory() as bin_dir, tempfile.TemporaryDirectory() as ws:
            _fake_real_python(os.path.join(bin_dir, "python3"))
            os.symlink(real_timeout, os.path.join(bin_dir, "timeout"))
            _write_exec(os.path.join(bin_dir, "true"), "#!/bin/sh\ntrap '' TERM\nsleep 30\n")
            payload = _bucket_a_payload(ws, os.path.join(ws, "totally_out_of_scope_dir", "x.md"))
            start = time.monotonic()
            code, out, err = _run_launcher(bin_dir, payload, extra_env={"CLAUDE_PROJECT_DIR": ws})
            elapsed = time.monotonic() - start
            self.assertLess(elapsed, 15, f"a hanging `true` stalled the probe for {elapsed:.1f}s")
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(out)["hookSpecificOutput"].get("permissionDecision"), "deny",
                             f"guard must still decide after the probe; got {out!r}")


class LauncherStubSkipOrderingTest(unittest.TestCase):
    """First candidate is a stub, a later one is real -> skip the stub, use the real one."""

    def test_py_stub_python3_real(self):
        with tempfile.TemporaryDirectory() as bin_dir, tempfile.TemporaryDirectory() as ws:
            _stub(os.path.join(bin_dir, "py"))          # py -3 fails (stub)
            _fake_real_python(os.path.join(bin_dir, "python3"))  # python3 is real
            payload = _bucket_a_payload(ws, os.path.join(ws, "out_of_scope", "x.md"))
            code, out, err = _run_launcher(bin_dir, payload, extra_env={"CLAUDE_PROJECT_DIR": ws})
            self.assertEqual(code, 0)
            decision = json.loads(out)
            self.assertEqual(decision["hookSpecificOutput"].get("permissionDecision"), "deny",
                             "must skip the py stub and use the real python3")


class LauncherPyDashThreeArgTest(unittest.TestCase):
    """`py -3` must be invoked as command `py` with arg `-3`, not an executable named `py -3`."""

    def test_py_invoked_with_dash_three(self):
        with tempfile.TemporaryDirectory() as bin_dir, tempfile.TemporaryDirectory() as ws:
            argv_log = os.path.join(bin_dir, "py_argv.log")
            # fake `py` that only succeeds when given -3 as the first arg; logs argv.
            _write_exec(os.path.join(bin_dir, "py"), (
                "#!/bin/sh\n"
                f'echo "$@" >> "{argv_log}"\n'
                'if [ "$1" = "-3" ]; then shift; exec "' + REAL_PY + '" "$@"; fi\n'
                "exit 1\n"
            ))
            payload = _bucket_a_payload(ws, os.path.join(ws, "out_of_scope", "x.md"))
            code, out, err = _run_launcher(bin_dir, payload, extra_env={"CLAUDE_PROJECT_DIR": ws})
            self.assertEqual(code, 0)
            decision = json.loads(out)
            self.assertEqual(decision["hookSpecificOutput"].get("permissionDecision"), "deny")
            # Confirm py was actually called with -3 (not as a literal "py -3" command, which
            # would have produced no log line at all because no such command exists).
            self.assertTrue(os.path.exists(argv_log), "py was never invoked")
            with open(argv_log) as fh:
                first = fh.readline().strip()
            self.assertTrue(first.startswith("-3"), f"py must be called with -3 first; got {first!r}")

    def test_py_alias_is_launched_once_per_call(self):
        """#1015: on Windows each launch through the `py` App Execution Alias leaks memory in
        AppXSvc, so one Python process per tool call does the probe, the guard run, and the
        JSON check."""
        with tempfile.TemporaryDirectory() as bin_dir, tempfile.TemporaryDirectory() as ws:
            calls_log = os.path.join(bin_dir, "py_calls.log")
            _write_exec(os.path.join(bin_dir, "py"), (
                "#!/bin/sh\n"
                f'echo call >> "{calls_log}"\n'
                f'if [ "$1" = "-3" ]; then shift; exec "{REAL_PY}" "$@"; fi\n'
                "exit 1\n"
            ))
            payload = _bucket_a_payload(ws, os.path.join(ws, "out_of_scope", "x.md"))
            code, out, err = _run_launcher(bin_dir, payload, extra_env={"CLAUDE_PROJECT_DIR": ws})
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(out)["hookSpecificOutput"].get("permissionDecision"), "deny")
            with open(calls_log) as fh:
                calls = fh.read().splitlines()
            self.assertEqual(len(calls), 1, f"py must run once per call; got {calls!r}")

    def test_output_before_the_marker_skips_the_candidate(self):
        """#1015: a candidate that prints before the marker line (a sitecustomize message, say)
        is skipped and the next candidate runs the guard."""
        with tempfile.TemporaryDirectory() as bin_dir, tempfile.TemporaryDirectory() as ws:
            _write_exec(os.path.join(bin_dir, "py"), (
                "#!/bin/sh\n"
                f'if [ "$1" = "-3" ]; then shift; echo noise; exec "{REAL_PY}" "$@"; fi\n'
                "exit 1\n"
            ))
            calls_log = os.path.join(bin_dir, "py3_calls.log")
            _write_exec(os.path.join(bin_dir, "python3"),
                        f'#!/bin/sh\necho call >> "{calls_log}"\nexec "{REAL_PY}" "$@"\n')
            payload = _bucket_a_payload(ws, os.path.join(ws, "out_of_scope", "x.md"))
            code, out, err = _run_launcher(bin_dir, payload, extra_env={"CLAUDE_PROJECT_DIR": ws})
            self.assertEqual(code, 0, f"err={err!r}")
            self.assertEqual(json.loads(out)["hookSpecificOutput"].get("permissionDecision"), "deny")
            with open(calls_log) as fh:
                self.assertEqual(len(fh.read().splitlines()), 1, "python3 must run the guard")

    def test_output_after_the_decision_skips_the_candidate(self):
        """#1015: a candidate that exits 0 but prints after the decision (a wrapper that prints
        after Python ends) is skipped and the next candidate runs the guard."""
        for tail in ("|diagnostic|", "{}", "\\n{}"):
            with self.subTest(tail=tail):
                self._after_decision(tail)

    def _after_decision(self, tail):
        with tempfile.TemporaryDirectory() as bin_dir, tempfile.TemporaryDirectory() as ws:
            _write_exec(os.path.join(bin_dir, "py"), (
                "#!/bin/sh\n"
                f'if [ "$1" = "-3" ]; then shift; "{REAL_PY}" "$@"; printf "$TAIL"; exit 0; fi\n'
                "exit 1\n"
            ))
            calls_log = os.path.join(bin_dir, "py3_calls.log")
            _write_exec(os.path.join(bin_dir, "python3"),
                        f'#!/bin/sh\necho call >> "{calls_log}"\nexec "{REAL_PY}" "$@"\n')
            payload = _bucket_a_payload(ws, os.path.join(ws, "out_of_scope", "x.md"))
            code, out, err = _run_launcher(bin_dir, payload,
                                           extra_env={"CLAUDE_PROJECT_DIR": ws, "TAIL": tail})
            self.assertEqual(code, 0, f"err={err!r}")
            self.assertEqual(json.loads(out)["hookSpecificOutput"].get("permissionDecision"), "deny")
            with open(calls_log) as fh:
                self.assertEqual(len(fh.read().splitlines()), 1, "python3 must run the guard")

    def test_modules_from_the_working_directory_and_pythonpath_are_not_imported(self):
        """#1015: the runner uses -I, so a json.py or runpy.py in the hook's working directory
        or on PYTHONPATH cannot replace the standard module and turn a deny into a pass-through."""
        with tempfile.TemporaryDirectory() as bin_dir, tempfile.TemporaryDirectory() as ws, \
                tempfile.TemporaryDirectory() as evil:
            _stub(os.path.join(bin_dir, "py"))
            _fake_real_python(os.path.join(bin_dir, "python3"))
            for folder in (ws, evil):
                for name in ("json.py", "runpy.py", "io.py"):
                    with open(os.path.join(folder, name), "w", encoding="utf-8") as fh:
                        fh.write("raise SystemExit(1)\n")
            payload = _bucket_a_payload(ws, os.path.join(ws, "out_of_scope", "x.md"))
            code, out, err = _run_launcher(
                bin_dir, payload, cwd=ws,
                extra_env={"CLAUDE_PROJECT_DIR": ws, "PYTHONPATH": evil, "PYTHONIOENCODING": "utf-7"})
            self.assertEqual(code, 0, f"err={err!r}")
            self.assertEqual(json.loads(out)["hookSpecificOutput"].get("permissionDecision"), "deny")


class LauncherSelfResolveTest(unittest.TestCase):
    """Launcher resolves the guard from its OWN path; works with CLAUDE_PLUGIN_ROOT unset
    and with a plugin path containing spaces (codex P1)."""

    def test_claude_plugin_root_unset(self):
        with tempfile.TemporaryDirectory() as bin_dir, tempfile.TemporaryDirectory() as ws:
            _fake_real_python(os.path.join(bin_dir, "python3"))
            payload = _bucket_a_payload(ws, os.path.join(ws, "out_of_scope", "x.md"))
            # _run_launcher deliberately does not set CLAUDE_PLUGIN_ROOT.
            code, out, err = _run_launcher(bin_dir, payload, extra_env={"CLAUDE_PROJECT_DIR": ws})
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(out)["hookSpecificOutput"].get("permissionDecision"), "deny")

    def test_plugin_path_with_spaces(self):
        # Copy the launcher + guard into a path containing spaces, run from there.
        with tempfile.TemporaryDirectory() as base, tempfile.TemporaryDirectory() as bin_dir, \
                tempfile.TemporaryDirectory() as ws:
            spaced = os.path.join(base, "plugin dir with spaces")
            os.makedirs(os.path.join(spaced, "hooks"))
            os.makedirs(os.path.join(spaced, "scripts"))
            shutil.copy(LAUNCHER, os.path.join(spaced, "hooks", "run_guard.sh"))
            shutil.copy(GUARD, os.path.join(spaced, "scripts", "ars_write_scope_guard.py"))
            # the guard imports nothing repo-local except its manifest, which lives in scripts/
            manifest = os.path.join(os.path.dirname(GUARD), "ars_phase_scope_manifest.json")
            shutil.copy(manifest, os.path.join(spaced, "scripts", "ars_phase_scope_manifest.json"))
            _fake_real_python(os.path.join(bin_dir, "python3"))
            payload = _bucket_a_payload(ws, os.path.join(ws, "out_of_scope", "x.md"))
            env = {"PATH": bin_dir + os.pathsep + _SYS_PATH, "CLAUDE_PROJECT_DIR": ws,
                   "ARS_PROBE_BOUND": _DEFAULT_PROBE_BOUND}
            proc = subprocess.run([_SH, os.path.join(spaced, "hooks", "run_guard.sh")],
                                  input=json.dumps(payload), env=env, capture_output=True,
                                  text=True, timeout=_LAUNCHER_TIMEOUT)
            self.assertEqual(proc.returncode, 0, f"stderr={proc.stderr!r}")
            self.assertEqual(json.loads(proc.stdout)["hookSpecificOutput"].get("permissionDecision"),
                             "deny", "launcher must resolve guard via its own path even under spaces")


class LauncherGuardBrokeTest(unittest.TestCase):
    """Found real python BUT the guard subprocess misbehaves -> pass-through + exit 0,
    do NOT block (maintainer decision §3.2.1), do NOT spam stderr.

    Mechanism (P2-e): the launcher resolves the guard from its OWN ../scripts/ — no test-only
    path override exists in production. So each test plants a broken guard in a temp plugin
    layout (real launcher copy + broken scripts/ars_write_scope_guard.py) and runs that copy."""

    def _run_with_broken_guard(self, guard_body):
        with tempfile.TemporaryDirectory() as bin_dir, tempfile.TemporaryDirectory() as base:
            _fake_real_python(os.path.join(bin_dir, "python3"))
            launcher_copy = _make_plugin_layout(base, guard_body)
            return _run_launcher(
                bin_dir, {"tool_name": "Bash", "tool_input": {"command": "ls"}},
                launcher=launcher_copy,
            )

    def test_guard_exits_nonzero(self):
        code, out, err = self._run_with_broken_guard("import sys\nsys.exit(3)\n")
        self.assertEqual(code, 0, f"must not propagate guard crash as block/error; err={err!r}")
        self.assertEqual(json.loads(out), PASS_THROUGH)
        self.assertEqual(err.strip(), "")

    def test_guard_prints_nothing(self):
        code, out, err = self._run_with_broken_guard("pass\n")  # exits 0, no stdout
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out), PASS_THROUGH)
        self.assertEqual(err.strip(), "")

    def test_guard_prints_invalid_json(self):
        code, out, err = self._run_with_broken_guard("print('not json at all')\n")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out), PASS_THROUGH)
        self.assertEqual(err.strip(), "")

    def test_guard_prints_substring_not_json(self):
        """P1-c: stdout CONTAINS the literal 'hookSpecificOutput' but is NOT valid JSON. A
        substring grep would false-accept and forward garbage; the real json.load parse must
        reject it and degrade to pass-through."""
        code, out, err = self._run_with_broken_guard(
            "print('not json but mentions \"hookSpecificOutput\" in prose')\n"
        )
        self.assertEqual(code, 0, f"non-JSON substring match must NOT be forwarded; err={err!r}")
        self.assertEqual(json.loads(out), PASS_THROUGH)
        self.assertEqual(err.strip(), "")

    def test_guard_raises(self):
        code, out, err = self._run_with_broken_guard("raise RuntimeError('boom')\n")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out), PASS_THROUGH)
        self.assertEqual(err.strip(), "")

    def test_guard_ends_the_process_without_a_decision(self):
        """#1015: the guard runs in the runner's process, so os._exit ends both; the marker is
        out, the decision is not -> pass-through, and no other candidate runs the guard."""
        with tempfile.TemporaryDirectory() as bin_dir, tempfile.TemporaryDirectory() as base:
            _fake_real_python(os.path.join(bin_dir, "python3"))
            calls_log = os.path.join(bin_dir, "python_calls.log")
            _write_exec(os.path.join(bin_dir, "python"),
                        f'#!/bin/sh\necho call >> "{calls_log}"\nexec "{REAL_PY}" "$@"\n')
            launcher_copy = _make_plugin_layout(base, "import os\nos._exit(0)\n")
            code, out, err = _run_launcher(
                bin_dir, {"tool_name": "Bash", "tool_input": {"command": "ls"}},
                launcher=launcher_copy)
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(out), PASS_THROUGH)
            self.assertEqual(err.strip(), "")
            self.assertFalse(os.path.exists(calls_log), "the next candidate must not run the guard")

    def test_guard_that_hangs_is_cut_off(self):
        with tempfile.TemporaryDirectory() as bin_dir, tempfile.TemporaryDirectory() as base:
            _fake_real_python(os.path.join(bin_dir, "python3"))
            launcher_copy = _make_plugin_layout(base, "import time\ntime.sleep(60)\n")
            start = time.monotonic()
            code, out, err = _run_launcher(
                bin_dir, {"tool_name": "Bash", "tool_input": {"command": "ls"}},
                launcher=launcher_copy, extra_env={"ARS_PROBE_BOUND": _HANG_PROBE_BOUND},
            )
            self.assertLess(time.monotonic() - start, 30)
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(out), PASS_THROUGH)

    def _run_with_guard_output(self, guard_body):
        with tempfile.TemporaryDirectory() as bin_dir, tempfile.TemporaryDirectory() as base:
            _fake_real_python(os.path.join(bin_dir, "python3"))
            launcher_copy = _make_plugin_layout(base, guard_body)
            return _run_launcher(
                bin_dir, {"tool_name": "Bash", "tool_input": {"command": "ls"}},
                launcher=launcher_copy,
            )

    def test_guard_decision_survives_a_write_around_sys_stdout(self):
        """#1015: a write straight to fd 1 during the guard run goes to the null device, so
        the decision the guard prints is still the only output."""
        deny = {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                       "permissionDecisionReason": "x"}}
        code, out, err = self._run_with_guard_output(
            "import json, os\nos.write(1, b'junk')\nprint(json.dumps(%r))\n" % (deny,))
        self.assertEqual(code, 0, f"err={err!r}")
        self.assertEqual(json.loads(out), deny)

    def test_guard_decision_written_as_bytes_or_with_non_ascii_text(self):
        deny = {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                       "permissionDecisionReason": "寫入範圍外：第一章.md"}}
        body = ("import json, sys\n"
                "sys.stdout.buffer.write(json.dumps(%r, ensure_ascii=False).encode('utf-8'))\n" % (deny,))
        code, out, err = self._run_with_guard_output(body)
        self.assertEqual(code, 0, f"err={err!r}")
        self.assertEqual(json.loads(out), deny)
        self.assertTrue(out.isascii())

    def test_guard_that_ignores_sigterm_is_cut_off_on_both_bound_paths(self):
        body = "import signal, time\nsignal.signal(signal.SIGTERM, signal.SIG_IGN)\ntime.sleep(60)\n"
        for watchdog in ("", "1"):
            with self.subTest(watchdog=watchdog), tempfile.TemporaryDirectory() as bin_dir, \
                    tempfile.TemporaryDirectory() as base:
                _fake_real_python(os.path.join(bin_dir, "python3"))
                launcher_copy = _make_plugin_layout(base, body)
                env = {"ARS_PROBE_BOUND": _HANG_PROBE_BOUND}
                if watchdog:
                    env["ARS_GUARD_FORCE_WATCHDOG"] = "1"
                start = time.monotonic()
                code, out, err = _run_launcher(
                    bin_dir, {"tool_name": "Bash", "tool_input": {"command": "ls"}},
                    launcher=launcher_copy, extra_env=env)
                self.assertLess(time.monotonic() - start, 30)
                self.assertEqual(code, 0)
                self.assertEqual(json.loads(out), PASS_THROUGH)

    def test_exit_codes_map_as_python_maps_them(self):
        """#1015: the guard runs in the runner's process, so its SystemExit code maps to the
        status Python would give it: 0.0 is a failure, and on POSIX 256 is status 0."""
        deny = {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                       "permissionDecisionReason": "x"}}
        cases = [("0.0", PASS_THROUGH), ("'stop'", PASS_THROUGH), ("None", deny), ("1 << 100", PASS_THROUGH)]
        if os.name != "nt":
            cases.append(("256", deny))
        for code_text, expected in cases:
            with self.subTest(code=code_text):
                body = "import json, sys\nprint(json.dumps(%r))\nsys.exit(%s)\n" % (deny, code_text)
                code, out, err = self._run_with_guard_output(body)
                self.assertEqual(code, 0)
                self.assertEqual(json.loads(out), expected)

    def test_healthy_guard_stderr_is_relayed(self):
        body = ("import json, sys\nsys.stderr.write('advisory without newline')\n"
                "print(json.dumps({'hookSpecificOutput': {'hookEventName': 'PreToolUse'}}))\n")
        code, out, err = self._run_with_guard_output(body)
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out), PASS_THROUGH)
        self.assertIn("advisory without newline", err)

    def test_guard_reads_stdin_as_utf8(self):
        """#1015: -I drops PYTHONUTF8 and PYTHONIOENCODING, so the runner sets UTF-8 on stdin
        itself; Claude Code sends UTF-8 JSON."""
        body = ("import json, sys\npayload = json.load(sys.stdin)\n"
                "print(json.dumps({'hookSpecificOutput': {'hookEventName': 'PreToolUse', "
                "'permissionDecisionReason': sys.stdin.encoding + ':' + payload['tool_input']['command']}}))\n")
        with tempfile.TemporaryDirectory() as bin_dir, tempfile.TemporaryDirectory() as base:
            _fake_real_python(os.path.join(bin_dir, "python3"))
            launcher_copy = _make_plugin_layout(base, body)
            path = bin_dir + os.pathsep + _SYS_PATH
            proc = subprocess.run(
                [_SH, launcher_copy],
                input=json.dumps({"tool_name": "Bash", "tool_input": {"command": "丁\"x"}},
                                 ensure_ascii=False).encode("utf-8"),
                env={"PATH": path, "ARS_PROBE_BOUND": _DEFAULT_PROBE_BOUND,
                     "LC_ALL": "en_US.ISO8859-1", "LANG": "en_US.ISO8859-1"},
                capture_output=True, timeout=_LAUNCHER_TIMEOUT)
            self.assertEqual(proc.returncode, 0)
            reason = json.loads(proc.stdout)["hookSpecificOutput"]["permissionDecisionReason"]
            self.assertEqual(reason, "utf-8:丁\"x")

    def test_guard_script_missing(self):
        # A plugin layout with the launcher but NO scripts/ars_write_scope_guard.py: the
        # launcher resolves a guard path that doesn't exist -> the run_bounded exec fails ->
        # broken-path degrade. Build the layout, then delete the guard the helper planted.
        with tempfile.TemporaryDirectory() as bin_dir, tempfile.TemporaryDirectory() as base:
            _fake_real_python(os.path.join(bin_dir, "python3"))
            launcher_copy = _make_plugin_layout(base, "pass\n")
            os.remove(os.path.join(base, "scripts", "ars_write_scope_guard.py"))
            code, out, err = _run_launcher(
                bin_dir, {"tool_name": "Bash", "tool_input": {"command": "ls"}},
                launcher=launcher_copy,
            )
            self.assertEqual(code, 0, f"missing guard -> pass-through, not block; err={err!r}")
            self.assertEqual(json.loads(out), PASS_THROUGH)


class LauncherHangingCandidateTest(unittest.TestCase):
    """A candidate interpreter that hangs must be killed within a bound, then move on —
    the hot path must never hang (spec §3.3 watchdog)."""

    _HANG_BOUND = {"ARS_PROBE_BOUND": _HANG_PROBE_BOUND}  # #545: see _DEFAULT_PROBE_BOUND

    def test_hanging_py_then_real_python3(self):
        with tempfile.TemporaryDirectory() as bin_dir, tempfile.TemporaryDirectory() as ws:
            # py hangs on the marker probe; python3 is real. Launcher must kill py's probe
            # and fall through to python3 within the test's _LAUNCHER_TIMEOUT.
            _write_exec(os.path.join(bin_dir, "py"), "#!/bin/sh\nsleep 60\n")
            _fake_real_python(os.path.join(bin_dir, "python3"))
            payload = _bucket_a_payload(ws, os.path.join(ws, "out_of_scope", "x.md"))
            code, out, err = _run_launcher(bin_dir, payload,
                                           extra_env={"CLAUDE_PROJECT_DIR": ws, **self._HANG_BOUND})
            self.assertEqual(code, 0, f"must not hang/error on a hanging candidate; err={err!r}")
            self.assertEqual(json.loads(out)["hookSpecificOutput"].get("permissionDecision"), "deny",
                             "must kill the hanging py and use the real python3")

    def test_hanging_py_killed_via_watchdog_path(self):
        """P2-d: same hanging-candidate scenario, but ARS_GUARD_FORCE_WATCHDOG=1 forces the
        no-`timeout` process-group watchdog instead of the `timeout` binary. Confirms the
        watchdog (setsid + kill -TERM/-KILL on the negative pid) actually reaps a hung probe
        so the launcher still falls through to the real python3 within the bound. A candidate
        that hangs AND spawns a child grandprocess exercises the process-GROUP kill."""
        with tempfile.TemporaryDirectory() as bin_dir, tempfile.TemporaryDirectory() as ws:
            # py spawns a long-sleeping grandchild then waits — a bare-pid TERM would leak the
            # child; the process-group kill must take down the whole group.
            _write_exec(os.path.join(bin_dir, "py"),
                        "#!/bin/sh\nsleep 60 &\nwait\n")
            _fake_real_python(os.path.join(bin_dir, "python3"))
            payload = _bucket_a_payload(ws, os.path.join(ws, "out_of_scope", "x.md"))
            code, out, err = _run_launcher(bin_dir, payload,
                                           extra_env={"CLAUDE_PROJECT_DIR": ws,
                                                      "ARS_GUARD_FORCE_WATCHDOG": "1",
                                                      **self._HANG_BOUND})
            self.assertEqual(code, 0, f"watchdog must reap the hung probe; err={err!r}")
            self.assertEqual(json.loads(out)["hookSpecificOutput"].get("permissionDecision"), "deny",
                             "watchdog must kill the hanging py and fall through to python3")


class LauncherSlowInterpreterTest(unittest.TestCase):
    """#545 regression pin: a SLOW but working interpreter (what a loaded machine
    produces) must not be false-degraded into pass-through. Under the harness default
    bound a python3 that takes ~1.5s per invocation must still produce the real deny
    decision — see _DEFAULT_PROBE_BOUND for the full mechanism."""

    def test_slow_but_working_python_forwards_deny(self):
        with tempfile.TemporaryDirectory() as bin_dir, tempfile.TemporaryDirectory() as ws:
            _write_exec(os.path.join(bin_dir, "python3"),
                        f'#!/bin/sh\nsleep 1.5\nexec "{REAL_PY}" "$@"\n')
            payload = _bucket_a_payload(ws, os.path.join(ws, "out_of_scope", "x.md"))
            code, out, err = _run_launcher(bin_dir, payload, extra_env={"CLAUDE_PROJECT_DIR": ws})
            self.assertEqual(code, 0, f"err={err!r}")
            self.assertEqual(json.loads(out)["hookSpecificOutput"].get("permissionDecision"), "deny",
                             "a slow-but-real interpreter must not be false-degraded to pass-through")


class LauncherWatchdogRobustnessTest(unittest.TestCase):
    """Round-6 gemini track: the no-`timeout` watchdog must not fail OPEN under (a) a private-
    temp allocation failure or (b) the pid-reuse race that would false-report a timeout."""

    def test_mktemp_failure_degrades_to_passthrough_not_fail_open(self):
        """gemini P1: if `mktemp` can't hand out a private temp, the launcher must NOT fall back
        to a predictable /tmp path (symlink-attack surface whose redirect failure would read as a
        broken guard and fail OPEN). It must degrade to a clean pass-through: exit 0, canonical
        JSON, silent. We force mktemp to fail by shadowing it on PATH and force the watchdog path
        (where the temp files live) via ARS_GUARD_FORCE_WATCHDOG."""
        with tempfile.TemporaryDirectory() as bin_dir, tempfile.TemporaryDirectory() as ws:
            _fake_real_python(os.path.join(bin_dir, "python3"))
            _write_exec(os.path.join(bin_dir, "mktemp"), "#!/bin/sh\nexit 1\n")  # mktemp always fails
            # A Bucket A out-of-scope write would normally be DENIED — proving we don't fail open,
            # the launcher must NOT emit deny here (it can't run the guard without a temp), it must
            # cleanly pass through instead of erroring or blocking.
            payload = _bucket_a_payload(ws, os.path.join(ws, "out_of_scope", "x.md"))
            code, out, err = _run_launcher(bin_dir, payload,
                                           extra_env={"CLAUDE_PROJECT_DIR": ws,
                                                      "ARS_GUARD_FORCE_WATCHDOG": "1"})
            self.assertEqual(code, 0, f"mktemp failure must not crash/block; err={err!r}")
            self.assertEqual(json.loads(out), PASS_THROUGH,
                             "mktemp failure must degrade to canonical pass-through, never a "
                             "predictable-temp path that fails open")
            self.assertEqual(err.strip(), "", f"degraded path must be silent; got {err!r}")

    def test_fast_guard_not_falsely_timed_out_on_watchdog_path(self):
        """gemini P1 (pid-reuse race): on the forced watchdog path, a guard that answers WELL
        within the bound must have its real decision forwarded — the done-file handshake must not
        let the watchdog false-flag a timeout (which would fail open to pass-through). Run the
        deny case several times; a single false-timeout would surface as a pass-through."""
        with tempfile.TemporaryDirectory() as bin_dir, tempfile.TemporaryDirectory() as ws:
            _fake_real_python(os.path.join(bin_dir, "python3"))
            payload = _bucket_a_payload(ws, os.path.join(ws, "out_of_scope", "x.md"))
            for i in range(5):
                code, out, err = _run_launcher(bin_dir, payload,
                                               extra_env={"CLAUDE_PROJECT_DIR": ws,
                                                          "ARS_GUARD_FORCE_WATCHDOG": "1"})
                self.assertEqual(code, 0, f"run {i}: err={err!r}")
                self.assertEqual(json.loads(out)["hookSpecificOutput"].get("permissionDecision"),
                                 "deny",
                                 f"run {i}: fast guard decision must be forwarded, not lost to a "
                                 f"false timeout; got {out!r}")


class LauncherInfraProtectionTest(unittest.TestCase):
    """A Bucket A subagent writing to hooks/run_guard.sh itself must be denied — confirms
    the hooks/*.sh infra glob covers the new launcher end-to-end through the launcher."""

    def test_subagent_write_to_launcher_denied(self):
        with tempfile.TemporaryDirectory() as bin_dir:
            _fake_real_python(os.path.join(bin_dir, "python3"))
            # plugin_root defaults to the repo root (launcher's ../). Target the real launcher
            # path inside this repo so it resolves inside plugin_root and matches hooks/*.sh.
            payload = {
                "tool_name": "Write",
                "cwd": REPO_ROOT,
                "agent_type": "research_architect_agent",
                "tool_input": {"file_path": LAUNCHER, "content": "evil"},
            }
            code, out, err = _run_launcher(bin_dir, payload, extra_env={"CLAUDE_PLUGIN_ROOT": REPO_ROOT})
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(out)["hookSpecificOutput"].get("permissionDecision"), "deny",
                             "writing the launcher itself must be infra-denied")


class LauncherWindowsAppsExclusionTest(unittest.TestCase):
    """#1025: a real interpreter reachable outside WindowsApps is preferred over the alias
    candidates. On a host where a real MINGW/MSYS/Cygwin shell (or, in tests, a stubbed
    `uname -s`) engages the walk, anything sitting in a WindowsApps-named path COMPONENT is
    skipped even if it would otherwise be the first match on PATH; if nothing else is
    reachable, the walk finds nothing and the unmodified candidate loop below still uses the
    WindowsApps one, since something has to run the guard."""

    def _run_with_path(self, path, payload, extra_env=None, probe_bound=None):
        # Prepend a fake `uname` reporting a MINGW kernel string, so the walk engages the
        # same way it would on a real MINGW/MSYS/Cygwin host (#1130 round 2 item 1: there is
        # no production env-var override for this anymore).
        full_path = os.pathsep.join([_windows_uname_dir(), path])
        env = {"PATH": full_path, "ARS_PROBE_BOUND": probe_bound or _DEFAULT_PROBE_BOUND}
        if extra_env:
            env.update(extra_env)
        proc = subprocess.run(
            [_SH, LAUNCHER], input=json.dumps(payload), env=env,
            capture_output=True, text=True, timeout=_LAUNCHER_TIMEOUT,
        )
        return proc.returncode, proc.stdout, proc.stderr

    def test_windowsapps_entry_skipped_falls_back_to_real_elsewhere(self):
        # A working interpreter sits in a directory whose path contains "WindowsApps" AND
        # comes first on PATH; a second, equally real interpreter sits in an ordinary
        # directory later on PATH. Each fixture RECORDS whether it ran (#1130 item 7: the
        # old version of this test could not tell which fake actually executed), so this
        # proves the WindowsApps one is skipped, not merely that SOME interpreter ran.
        with tempfile.TemporaryDirectory() as base, tempfile.TemporaryDirectory() as ws:
            windowsapps_dir = os.path.join(base, "AppData", "Local", "Microsoft", "WindowsApps")
            real_dir = os.path.join(base, "Program Files", "Python312")
            os.makedirs(windowsapps_dir)
            os.makedirs(real_dir)
            marker_file = os.path.join(base, "ran.log")
            _fake_recording_python(os.path.join(windowsapps_dir, "python3"), marker_file, "windowsapps")
            _fake_recording_python(os.path.join(real_dir, "python3"), marker_file, "real")
            path = os.pathsep.join([windowsapps_dir, real_dir, _minimal_sys_path()])
            payload = _bucket_a_payload(ws, os.path.join(ws, "out_of_scope", "x.md"))
            code, out, err = self._run_with_path(path, payload, extra_env={"CLAUDE_PROJECT_DIR": ws})
            self.assertEqual(code, 0, f"err={err!r}")
            decision = json.loads(out)
            self.assertEqual(decision["hookSpecificOutput"].get("permissionDecision"), "deny",
                             "must skip the WindowsApps candidate and use the real one on PATH")
            ran = Path(marker_file).read_text().splitlines() if os.path.exists(marker_file) else []
            self.assertEqual(ran.count("windowsapps"), 0, "the WindowsApps interpreter must never run")
            self.assertEqual(ran.count("real"), 1, "the real interpreter must run exactly once")

    def test_only_windowsapps_present_falls_back_to_alias_candidates_unchanged(self):
        # No non-WindowsApps interpreter exists anywhere on PATH (a MINIMAL system PATH with
        # no python at all, #1130 item 7: the old version of this test appended the real
        # _SYS_PATH, which on this host already has a real /usr/bin/python3 and would have let
        # the walk find THAT instead, never actually testing the WindowsApps-only case it
        # claimed to). The walk finds nothing, so the unmodified candidate loop below falls
        # back to the WindowsApps interpreter, the only one that exists -- it must run exactly
        # once, not be refused just for living under WindowsApps.
        with tempfile.TemporaryDirectory() as base, tempfile.TemporaryDirectory() as ws:
            windowsapps_dir = os.path.join(base, "AppData", "Local", "Microsoft", "WindowsApps")
            os.makedirs(windowsapps_dir)
            marker_file = os.path.join(base, "ran.log")
            _fake_recording_python(os.path.join(windowsapps_dir, "python3"), marker_file, "windowsapps")
            path = os.pathsep.join([windowsapps_dir, _minimal_sys_path()])
            payload = _bucket_a_payload(ws, os.path.join(ws, "out_of_scope", "x.md"))
            code, out, err = self._run_with_path(path, payload, extra_env={"CLAUDE_PROJECT_DIR": ws})
            self.assertEqual(code, 0, f"err={err!r}")
            decision = json.loads(out)
            self.assertEqual(decision["hookSpecificOutput"].get("permissionDecision"), "deny",
                             "the only interpreter available is under WindowsApps; it must "
                             "still be used via the ordinary candidate loop, not refused")
            ran = Path(marker_file).read_text().splitlines() if os.path.exists(marker_file) else []
            self.assertEqual(ran.count("windowsapps"), 1,
                             "the WindowsApps interpreter is the only one available and must run")

    def test_windowsapps_match_is_whole_component_and_case_insensitive(self):
        # #1130 item 6: a bare substring match both misses a differently-cased WindowsApps
        # directory AND wrongly excludes an unrelated directory that merely contains the
        # substring as part of a longer name, not as its own path component.
        with tempfile.TemporaryDirectory() as base, tempfile.TemporaryDirectory() as ws:
            lowercase_dir = os.path.join(base, "windowsapps")
            lookalike_dir = os.path.join(base, "MyWindowsAppsTools", "bin")
            os.makedirs(lowercase_dir)
            os.makedirs(lookalike_dir)
            marker_file = os.path.join(base, "ran.log")
            _fake_recording_python(os.path.join(lowercase_dir, "python3"), marker_file, "lowercase_alias")
            _fake_recording_python(os.path.join(lookalike_dir, "python3"), marker_file, "lookalike_real")
            path = os.pathsep.join([lowercase_dir, lookalike_dir, _minimal_sys_path()])
            payload = _bucket_a_payload(ws, os.path.join(ws, "out_of_scope", "x.md"))
            code, out, err = self._run_with_path(path, payload, extra_env={"CLAUDE_PROJECT_DIR": ws})
            self.assertEqual(code, 0, f"err={err!r}")
            decision = json.loads(out)
            self.assertEqual(decision["hookSpecificOutput"].get("permissionDecision"), "deny")
            ran = Path(marker_file).read_text().splitlines() if os.path.exists(marker_file) else []
            self.assertEqual(ran.count("lowercase_alias"), 0,
                             "windowsapps in lowercase is still the WindowsApps component and must be skipped")
            self.assertEqual(ran.count("lookalike_real"), 1,
                             "MyWindowsAppsTools is not the windowsapps path component and must be used")

    def test_relative_path_entry_is_not_used(self):
        # #1130 item 1: a relative PATH entry (here, the CWD via ".") must not be treated as a
        # non-WindowsApps candidate, even when it is the only non-WindowsApps-looking entry.
        with tempfile.TemporaryDirectory() as base, tempfile.TemporaryDirectory() as ws:
            windowsapps_dir = os.path.join(base, "AppData", "Local", "Microsoft", "WindowsApps")
            cwd_dir = os.path.join(base, "cwd")
            os.makedirs(windowsapps_dir)
            os.makedirs(cwd_dir)
            marker_file = os.path.join(base, "ran.log")
            _fake_recording_python(os.path.join(windowsapps_dir, "python3"), marker_file, "windowsapps")
            _fake_recording_python(os.path.join(cwd_dir, "python3"), marker_file, "cwd_relative")
            path = os.pathsep.join([_windows_uname_dir(), windowsapps_dir, ".", _minimal_sys_path()])
            payload = _bucket_a_payload(ws, os.path.join(ws, "out_of_scope", "x.md"))
            env = {"PATH": path, "ARS_PROBE_BOUND": _DEFAULT_PROBE_BOUND,
                   "CLAUDE_PROJECT_DIR": ws}
            proc = subprocess.run(
                [_SH, LAUNCHER], input=json.dumps(payload), env=env, cwd=cwd_dir,
                capture_output=True, text=True, timeout=_LAUNCHER_TIMEOUT,
            )
            self.assertEqual(proc.returncode, 0, f"err={proc.stderr!r}")
            decision = json.loads(proc.stdout)
            self.assertEqual(decision["hookSpecificOutput"].get("permissionDecision"), "deny",
                             "the walk must skip the relative entry and still fall back to WindowsApps")
            ran = Path(marker_file).read_text().splitlines() if os.path.exists(marker_file) else []
            self.assertEqual(ran.count("cwd_relative"), 0,
                             "a relative PATH entry must never be treated as a candidate")
            self.assertEqual(ran.count("windowsapps"), 1,
                             "must fall back to the WindowsApps alias since the relative entry was skipped")

    def test_glob_metacharacters_in_path_entry_are_not_expanded(self):
        # #1130 item 2: a PATH entry containing glob metacharacters must be matched literally,
        # not pathname-expanded. The literal directory "[ab]" does not exist; "a" does, with a
        # real interpreter in it, and would be reachable if the PATH entry were glob-expanded.
        with tempfile.TemporaryDirectory() as base, tempfile.TemporaryDirectory() as ws:
            glob_target_dir = os.path.join(base, "a")
            os.makedirs(glob_target_dir)
            marker_file = os.path.join(base, "ran.log")
            _fake_recording_python(os.path.join(glob_target_dir, "python3"), marker_file, "glob_target")
            literal_entry = os.path.join(base, "[ab]")
            path = os.pathsep.join([literal_entry, _minimal_sys_path()])
            payload = _bucket_a_payload(ws, os.path.join(ws, "out_of_scope", "x.md"))
            code, out, err = self._run_with_path(path, payload, extra_env={"CLAUDE_PROJECT_DIR": ws})
            self.assertEqual(code, 0, f"err={err!r}")
            self.assertEqual(json.loads(out), PASS_THROUGH,
                             "a glob-metacharacter PATH entry must not resolve to an unrelated "
                             "real directory; with no usable interpreter found, must pass through")
            self.assertFalse(os.path.exists(marker_file),
                             "the interpreter reachable only via glob-expansion must never run")

    def test_preferred_candidate_failure_degrades_to_passthrough_not_retried(self):
        # #1130 item 4 / round 2 item 5: a non-WindowsApps candidate that prints the marker
        # and then fails (a broken guard run, simulated by a candidate that prints the marker
        # then exits non-zero with no valid JSON after it) must degrade to pass-through for
        # this call, not retry under another candidate. A HEALTHY WindowsApps python3 is
        # placed BEFORE the broken one on PATH (round 2 item 5): the walk still excludes the
        # WindowsApps directory from discovery and finds only the broken candidate, so it
        # fails and correctly stops there. But if the stop-on-failure branch were removed, the
        # fallback would reach the old loop, whose `command -v python3` resolves to whichever
        # directory is first on PATH, here the healthy WindowsApps one, producing a DETECTABLE
        # "deny" instead of today's pass-through, rather than silently re-running the same
        # broken file the walk already tried, which a reversed PATH order could mask.
        with tempfile.TemporaryDirectory() as base, tempfile.TemporaryDirectory() as ws:
            windowsapps_dir = os.path.join(base, "AppData", "Local", "Microsoft", "WindowsApps")
            broken_dir = os.path.join(base, "broken")
            os.makedirs(windowsapps_dir)
            os.makedirs(broken_dir)
            marker_file = os.path.join(base, "ran.log")
            _fake_recording_python(os.path.join(windowsapps_dir, "python3"), marker_file, "windowsapps")
            broken_path = os.path.join(broken_dir, "python3")
            _write_exec(broken_path,
                        f'#!/bin/sh\necho broken >> "{marker_file}"\n'
                        'printf "ARS_PY_OK\\n"\nexit 1\n')
            path = os.pathsep.join([windowsapps_dir, broken_dir, _minimal_sys_path()])
            payload = _bucket_a_payload(ws, os.path.join(ws, "out_of_scope", "x.md"))
            code, out, err = self._run_with_path(path, payload, extra_env={"CLAUDE_PROJECT_DIR": ws})
            self.assertEqual(code, 0, f"err={err!r}")
            self.assertEqual(json.loads(out), PASS_THROUGH,
                             "a preferred candidate that prints the marker then fails must "
                             "degrade to pass-through, not fall back to another candidate")
            ran = Path(marker_file).read_text().splitlines() if os.path.exists(marker_file) else []
            self.assertEqual(ran.count("broken"), 1, "the broken candidate must run once")
            self.assertEqual(ran.count("windowsapps"), 0,
                             "the guard must not be retried under the WindowsApps candidate "
                             "after a preferred candidate already printed the marker and failed")

    def test_preferred_candidate_timeout_after_marker_degrades_to_passthrough_not_retried(self):
        # Same scenario as above, but the preferred candidate TIMES OUT after printing the
        # marker (hangs) instead of exiting non-zero (#1130 round 2 item 5: the PR description
        # also covers this case). run_bounded reports TIMEOUT_STATUS, not 0, so try_candidate
        # must take the same "stop, do not retry" path as a plain post-marker failure.
        with tempfile.TemporaryDirectory() as base, tempfile.TemporaryDirectory() as ws:
            windowsapps_dir = os.path.join(base, "AppData", "Local", "Microsoft", "WindowsApps")
            hanging_dir = os.path.join(base, "hanging")
            os.makedirs(windowsapps_dir)
            os.makedirs(hanging_dir)
            marker_file = os.path.join(base, "ran.log")
            _fake_recording_python(os.path.join(windowsapps_dir, "python3"), marker_file, "windowsapps")
            hanging_path = os.path.join(hanging_dir, "python3")
            _write_exec(hanging_path,
                        f'#!/bin/sh\necho hanging >> "{marker_file}"\n'
                        'printf "ARS_PY_OK\\n"\nsleep 60\n')
            path = os.pathsep.join([windowsapps_dir, hanging_dir, _minimal_sys_path()])
            payload = _bucket_a_payload(ws, os.path.join(ws, "out_of_scope", "x.md"))
            start = time.monotonic()
            code, out, err = self._run_with_path(path, payload,
                                                 extra_env={"CLAUDE_PROJECT_DIR": ws},
                                                 probe_bound=_HANG_PROBE_BOUND)
            self.assertLess(time.monotonic() - start, 30, "must not wait out the bound twice")
            self.assertEqual(code, 0, f"err={err!r}")
            self.assertEqual(json.loads(out), PASS_THROUGH,
                             "a preferred candidate that times out after the marker must "
                             "degrade to pass-through, not fall back to another candidate")
            ran = Path(marker_file).read_text().splitlines() if os.path.exists(marker_file) else []
            self.assertEqual(ran.count("hanging"), 1, "the hanging candidate must run once")
            self.assertEqual(ran.count("windowsapps"), 0,
                             "the guard must not be retried under the WindowsApps candidate "
                             "after a preferred candidate already printed the marker and timed out")

    def test_walk_tries_only_the_first_match(self):
        # #1130 round 3: the walk stops at the first absolute, non-WindowsApps match and does
        # not keep looking for a healthier one further down PATH. A broken first match (one
        # that never even prints the marker) falls through to the unmodified old loop below,
        # which is a separate, independent mechanism (see test_preferred_candidate_failure_
        # degrades_to_passthrough_not_retried for the "marker then fails" case, and the "known
        # limit" note in run_guard.sh for what the old loop does next); this test is only about
        # discovery itself never considering the later, healthy entry as a candidate at all.
        with tempfile.TemporaryDirectory() as base, tempfile.TemporaryDirectory() as ws:
            broken_dir = os.path.join(base, "broken")
            healthy_dir = os.path.join(base, "healthy")
            os.makedirs(broken_dir)
            os.makedirs(healthy_dir)
            marker_file = os.path.join(base, "ran.log")
            # A "broken" shim: executable, but does not understand -I/-c and so never prints
            # the marker at all (try_candidate sees no marker -> status 2).
            _write_exec(os.path.join(broken_dir, "python3"), "#!/bin/sh\nexit 1\n")
            _fake_recording_python(os.path.join(healthy_dir, "python3"), marker_file, "healthy")
            # No WindowsApps directory anywhere on this PATH: the only way the healthy
            # candidate could ever run is if the walk kept looking past the first match.
            path = os.pathsep.join([broken_dir, healthy_dir, _minimal_sys_path()])
            payload = _bucket_a_payload(ws, os.path.join(ws, "out_of_scope", "x.md"))
            code, out, err = self._run_with_path(path, payload, extra_env={"CLAUDE_PROJECT_DIR": ws})
            self.assertEqual(code, 0, f"err={err!r}")
            ran = Path(marker_file).read_text().splitlines() if os.path.exists(marker_file) else []
            self.assertEqual(ran.count("healthy"), 0,
                             "the walk must stop at the first match and never consider a "
                             "later, healthier candidate")

    def test_walk_is_directory_first_not_name_first(self):
        # #1130 round 4 item 1: the walk must try every name in one directory before moving
        # to the next directory, not try one name across the whole PATH before trying the
        # next name. An early directory holding only python3, and a later directory holding a
        # py that records its run, distinguishes the two orders: directory-first finds the
        # early python3 and never reaches the later directory at all; name-first would walk
        # the whole PATH looking for py first and find the later one before ever trying the
        # early python3.
        with tempfile.TemporaryDirectory() as base, tempfile.TemporaryDirectory() as ws:
            early_dir = os.path.join(base, "early")
            later_dir = os.path.join(base, "later")
            os.makedirs(early_dir)
            os.makedirs(later_dir)
            marker_file = os.path.join(base, "ran.log")
            _fake_recording_python(os.path.join(early_dir, "python3"), marker_file, "early_python3")
            # A fake `py` launcher: strips a leading -3 (real CPython does not understand it)
            # before delegating, the same way the real Windows py launcher consumes -3 to pick
            # a version rather than forwarding it to the interpreter it starts.
            py_path = os.path.join(later_dir, "py")
            _write_exec(py_path,
                        f'#!/bin/sh\necho later_py >> "{marker_file}"\n'
                        f'[ "$1" = "-3" ] && shift\nexec "{REAL_PY}" "$@"\n')
            path = os.pathsep.join([early_dir, later_dir, _minimal_sys_path()])
            full_path = os.pathsep.join([_windows_uname_dir(), path])
            payload = _bucket_a_payload(ws, os.path.join(ws, "out_of_scope", "x.md"))
            env = {"PATH": full_path, "ARS_PROBE_BOUND": _DEFAULT_PROBE_BOUND, "CLAUDE_PROJECT_DIR": ws}
            proc = subprocess.run(
                [_SH, LAUNCHER], input=json.dumps(payload), env=env,
                capture_output=True, text=True, timeout=_LAUNCHER_TIMEOUT,
            )
            self.assertEqual(proc.returncode, 0, f"err={proc.stderr!r}")
            decision = json.loads(proc.stdout)
            self.assertEqual(decision["hookSpecificOutput"].get("permissionDecision"), "deny",
                             "the early python3 must actually run the guard")
            ran = Path(marker_file).read_text().splitlines() if os.path.exists(marker_file) else []
            self.assertEqual(ran.count("early_python3"), 1,
                             "directory-first: the early directory's python3 must run")
            self.assertEqual(ran.count("later_py"), 0,
                             "directory-first: the later directory's py must never be reached")

    def test_walk_selects_py_and_passes_dash_three(self):
        # #1130 round 5 item 1: no existing test ever selects `py` through the walk, so the
        # `-3` branch (try_non_windowsapps_candidates passes `-3` only when the matched name
        # is `py`) is untested; removing `py` from the walk's candidate names, or dropping the
        # `-3` it should receive, would still pass every other test in this file. A WindowsApps
        # `py` sits first on PATH so a walk that skips `py` or drops `-3` falls through to the
        # unmodified old loop, which finds and runs THAT one instead, failing this test.
        with tempfile.TemporaryDirectory() as base, tempfile.TemporaryDirectory() as ws:
            windowsapps_dir = os.path.join(base, "AppData", "Local", "Microsoft", "WindowsApps")
            ordinary_dir = os.path.join(base, "Program Files", "PythonLauncher")
            os.makedirs(windowsapps_dir)
            os.makedirs(ordinary_dir)
            marker_file = os.path.join(base, "ran.log")
            _fake_recording_python(os.path.join(windowsapps_dir, "py"), marker_file, "windowsapps_py")
            # A fake `py` that records its first argument, fails unless it is exactly -3, and
            # only then shifts it off and runs a real interpreter, so the test can tell apart
            # "ran, but without -3" from "ran, with -3" rather than just "ran".
            ordinary_py = os.path.join(ordinary_dir, "py")
            _write_exec(ordinary_py,
                        f'#!/bin/sh\necho "ordinary_py $1" >> "{marker_file}"\n'
                        f'[ "$1" = "-3" ] || exit 99\nshift\nexec "{REAL_PY}" "$@"\n')
            path = os.pathsep.join([windowsapps_dir, ordinary_dir, _minimal_sys_path()])
            payload = _bucket_a_payload(ws, os.path.join(ws, "out_of_scope", "x.md"))
            code, out, err = self._run_with_path(path, payload, extra_env={"CLAUDE_PROJECT_DIR": ws})
            self.assertEqual(code, 0, f"err={err!r}")
            decision = json.loads(out)
            self.assertEqual(decision["hookSpecificOutput"].get("permissionDecision"), "deny",
                             "the ordinary py must actually run the guard, not just exit 99")
            ran = Path(marker_file).read_text().splitlines() if os.path.exists(marker_file) else []
            self.assertEqual(ran.count("ordinary_py -3"), 1,
                             "the walk must select py through the ordinary directory and pass -3")
            self.assertEqual(ran.count("windowsapps_py"), 0,
                             "the WindowsApps py must never run when an ordinary py is found")

    def test_trailing_slash_path_entry_does_not_build_double_slash(self):
        # #1130 round 1 smaller item / round 2 item 5: a PATH entry ending in "/" must build
        # ".../name", not ".../name" with a doubled slash (which MSYS can read as a UNC or
        # network path). Runs the REAL launcher end to end rather than an isolated copy of the
        # trailing-slash-stripping snippet, and checks the exact argv0 the fake interpreter was
        # invoked with, which is where a stray "//" would actually show up. A literal PATH
        # entry of exactly "/" would need an executable written into the filesystem root, which
        # a test must not do; a real directory with an explicit trailing slash on its PATH
        # entry exercises the identical code path (the walk strips a trailing "/" off `dir`
        # before building `$dir/$name`), without that.
        with tempfile.TemporaryDirectory() as base, tempfile.TemporaryDirectory() as ws:
            real_dir = os.path.join(base, "realpy")
            os.makedirs(real_dir)
            argv0_file = os.path.join(base, "argv0.log")
            real_path = os.path.join(real_dir, "python3")
            _write_exec(real_path,
                        f'#!/bin/sh\nprintf %s "$0" > "{argv0_file}"\nexec "{REAL_PY}" "$@"\n')
            path = os.pathsep.join([real_dir + os.sep, _minimal_sys_path()])
            payload = _bucket_a_payload(ws, os.path.join(ws, "out_of_scope", "x.md"))
            full_path = os.pathsep.join([_windows_uname_dir(), path])
            env = {"PATH": full_path, "ARS_PROBE_BOUND": _DEFAULT_PROBE_BOUND, "CLAUDE_PROJECT_DIR": ws}
            proc = subprocess.run(
                [_SH, LAUNCHER], input=json.dumps(payload), env=env,
                capture_output=True, text=True, timeout=_LAUNCHER_TIMEOUT,
            )
            self.assertEqual(proc.returncode, 0, f"err={proc.stderr!r}")
            decision = json.loads(proc.stdout)
            self.assertEqual(decision["hookSpecificOutput"].get("permissionDecision"), "deny")
            self.assertTrue(os.path.exists(argv0_file), "the real interpreter must have run")
            argv0 = Path(argv0_file).read_text()
            self.assertEqual(argv0, real_path, "must be invoked with a single slash before the name")
            self.assertNotIn("//", argv0, "must never build a doubled-slash path")

    def test_walk_is_inert_without_windows_shell(self):
        # #1130 round 2 item 5: on a host that is not a real MINGW/MSYS/Cygwin shell, the walk
        # must not engage at all, and a REAL non-WindowsApps interpreter being present must not
        # change that -- the old test only had a WindowsApps python3 on PATH, so it could not
        # tell "the walk correctly stayed off" apart from "the walk ran and found nothing
        # better anyway". With both present, this proves the unmodified pre-#1025 PATH order
        # wins: `command -v python3` (not the walk) resolves to whichever is FIRST on PATH.
        with tempfile.TemporaryDirectory() as base, tempfile.TemporaryDirectory() as ws:
            windowsapps_dir = os.path.join(base, "AppData", "Local", "Microsoft", "WindowsApps")
            real_dir = os.path.join(base, "Program Files", "Python312")
            os.makedirs(windowsapps_dir)
            os.makedirs(real_dir)
            marker_file = os.path.join(base, "ran.log")
            _fake_recording_python(os.path.join(windowsapps_dir, "python3"), marker_file, "windowsapps")
            _fake_recording_python(os.path.join(real_dir, "python3"), marker_file, "real")
            path = os.pathsep.join([windowsapps_dir, real_dir, _minimal_sys_path()])
            payload = _bucket_a_payload(ws, os.path.join(ws, "out_of_scope", "x.md"))
            full_path = os.pathsep.join([_linux_uname_dir(), path])
            env = {"PATH": full_path, "ARS_PROBE_BOUND": _DEFAULT_PROBE_BOUND, "CLAUDE_PROJECT_DIR": ws}
            # A stubbed `uname -s` reports a plain Linux kernel string, so this test proves
            # the walk stays off regardless of what the real test host's own uname reports.
            proc = subprocess.run(
                [_SH, LAUNCHER], input=json.dumps(payload), env=env,
                capture_output=True, text=True, timeout=_LAUNCHER_TIMEOUT,
            )
            self.assertEqual(proc.returncode, 0, f"err={proc.stderr!r}")
            decision = json.loads(proc.stdout)
            self.assertEqual(decision["hookSpecificOutput"].get("permissionDecision"), "deny",
                             "the unmodified candidate loop must still find and use whatever "
                             "`command -v python3` resolves to, exactly as before #1025")
            ran = Path(marker_file).read_text().splitlines() if os.path.exists(marker_file) else []
            self.assertEqual(ran.count("windowsapps"), 1,
                             "walk off: command -v finds the first PATH match, WindowsApps")
            self.assertEqual(ran.count("real"), 0,
                             "walk off: the real interpreter later on PATH must not run")

    def test_walk_engages_on_stubbed_windows_shell(self):
        # Same PATH layout as test_walk_is_inert_without_windows_shell, but with a fake
        # `uname` reporting a MINGW kernel string: the walk now engages, excludes the
        # WindowsApps directory from discovery, and must use the real interpreter instead.
        with tempfile.TemporaryDirectory() as base, tempfile.TemporaryDirectory() as ws:
            windowsapps_dir = os.path.join(base, "AppData", "Local", "Microsoft", "WindowsApps")
            real_dir = os.path.join(base, "Program Files", "Python312")
            os.makedirs(windowsapps_dir)
            os.makedirs(real_dir)
            marker_file = os.path.join(base, "ran.log")
            _fake_recording_python(os.path.join(windowsapps_dir, "python3"), marker_file, "windowsapps")
            _fake_recording_python(os.path.join(real_dir, "python3"), marker_file, "real")
            path = os.pathsep.join([windowsapps_dir, real_dir, _minimal_sys_path()])
            payload = _bucket_a_payload(ws, os.path.join(ws, "out_of_scope", "x.md"))
            full_path = os.pathsep.join([_windows_uname_dir(), path])
            env = {"PATH": full_path, "ARS_PROBE_BOUND": _DEFAULT_PROBE_BOUND, "CLAUDE_PROJECT_DIR": ws}
            proc = subprocess.run(
                [_SH, LAUNCHER], input=json.dumps(payload), env=env,
                capture_output=True, text=True, timeout=_LAUNCHER_TIMEOUT,
            )
            self.assertEqual(proc.returncode, 0, f"err={proc.stderr!r}")
            decision = json.loads(proc.stdout)
            self.assertEqual(decision["hookSpecificOutput"].get("permissionDecision"), "deny",
                             "the walk must skip the WindowsApps directory and use the real one")
            ran = Path(marker_file).read_text().splitlines() if os.path.exists(marker_file) else []
            self.assertEqual(ran.count("real"), 1, "walk on: the real interpreter must run")
            self.assertEqual(ran.count("windowsapps"), 0,
                             "walk on: the WindowsApps directory must never be tried")


    def test_empty_path_entries_are_not_treated_as_absolute_in_the_walk(self):
        # A PATH with a bare "::" (an empty entry mid-string) and a trailing ":" (an empty
        # entry at the end) must never be treated as an absolute candidate BY THE WALK,
        # consistent with round 1 item 1's absolute-paths-only rule: an empty PATH entry is
        # the one way a relative-looking "path" can appear without even a "." character. This
        # is scoped to the walk specifically: POSIX `command -v` (used, unmodified, by the old
        # loop per round 2 item 2) treats an empty PATH entry as the current directory, which
        # is pre-existing behavior this PR must not change, so a real, absolute, non-
        # WindowsApps candidate is placed where the walk must find and use it BEFORE the old
        # loop (and its own, separate, out-of-scope CWD convention) ever runs at all.
        with tempfile.TemporaryDirectory() as base, tempfile.TemporaryDirectory() as ws, \
             tempfile.TemporaryDirectory() as cwd_dir:
            real_dir = os.path.join(base, "Program Files", "Python312")
            os.makedirs(real_dir)
            marker_file = os.path.join(base, "ran.log")
            _fake_recording_python(os.path.join(real_dir, "python3"), marker_file, "real")
            _fake_recording_python(os.path.join(cwd_dir, "python3"), marker_file, "cwd")
            path = "::" + os.pathsep.join([real_dir, _minimal_sys_path()]) + ":"
            payload = _bucket_a_payload(ws, os.path.join(ws, "out_of_scope", "x.md"))
            full_path = os.pathsep.join([_windows_uname_dir(), path])
            env = {"PATH": full_path, "ARS_PROBE_BOUND": _DEFAULT_PROBE_BOUND, "CLAUDE_PROJECT_DIR": ws}
            proc = subprocess.run(
                [_SH, LAUNCHER], input=json.dumps(payload), env=env, cwd=cwd_dir,
                capture_output=True, text=True, timeout=_LAUNCHER_TIMEOUT,
            )
            self.assertEqual(proc.returncode, 0, f"err={proc.stderr!r}")
            decision = json.loads(proc.stdout)
            self.assertEqual(decision["hookSpecificOutput"].get("permissionDecision"), "deny",
                             "the walk must skip the empty entries and use the real candidate")
            ran = Path(marker_file).read_text().splitlines() if os.path.exists(marker_file) else []
            self.assertEqual(ran.count("cwd"), 0,
                             "an empty PATH entry must never be treated as a candidate by the walk")
            self.assertEqual(ran.count("real"), 1,
                             "the walk must find and use the real candidate, not fall through "
                             "to the old loop at all")


if __name__ == "__main__":
    unittest.main()
