#!/bin/sh
# version: 1.1.0
#
# ARS write-scope guard LAUNCHER — PreToolUse hook (#454 Windows portability fix).
#
# WHY THIS EXISTS: the guard hook used to be wired as `python3 ".../ars_write_scope_guard.py"`
# directly. On Windows, `python3` is commonly a 0-byte Microsoft Store App Execution Alias
# stub (not real Python); invoking it non-interactively fails BEFORE the guard's Python runs,
# so none of the guard's own fail-safes apply — it just errors and spams the hook log (#454).
#
# This launcher finds a REAL Python (skipping stubs), then runs the guard as a SUPERVISED
# subprocess. Design: docs/design/2026-06-17-454-windows-python-hook-portability-design.md.
#
# POSTURE (Plan A — graceful degradation; the guard is OPTIONAL v3.10 hardening and ARS core
# needs no Python): if no real Python is found, OR the guard subprocess misbehaves, the
# launcher emits a valid PASS-THROUGH hook JSON and exits 0. It NEVER exits non-zero on these
# degraded paths (a non-2 exit blocks nothing anyway and only spams logs; exit 2 would
# hard-lock the user out of all writes/Bash for an environment gap or an ARS-side bug — wrong
# for an optional layer). It stays SILENT on stderr on degraded paths: PreToolUse is a hot
# path, so any per-call stderr IS the spam #454 is about.
#
# Bash 3.2 / POSIX sh compatible (same constraint as scripts/announce-ars-loaded.sh). On
# Windows this runs under Git Bash; with no Git Bash, CC falls back to PowerShell which can't
# run this .sh — the guard is then inactive (accepted degradation, see spec §3.3).

# Canonical pass-through output: no permissionDecision => falls back to the normal permission
# flow (NEVER emit "allow" — that would skip every other permission rule).
PASS_THROUGH='{"hookSpecificOutput":{"hookEventName":"PreToolUse"}}'

emit_passthrough_and_exit() {
    printf '%s\n' "$PASS_THROUGH"
    exit 0
}

# --- Resolve the guard script from THIS launcher's own location (codex P1) ---------------
# CC substitutes ${CLAUDE_PLUGIN_ROOT} into the hook COMMAND text before the shell, but does
# NOT guarantee it as an env var inside this script. So compute the guard path from $0.
# (No production env override: the guard path is ALWAYS derived from the launcher's own
# location. Tests that need a broken/alternate guard run the launcher from a temp plugin
# layout, so there is no production back door — P2-e.)
# shellcheck disable=SC1007  # `CDPATH= cd` is intentional: clear CDPATH for this one cd only
SELF_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd) || emit_passthrough_and_exit
GUARD="$SELF_DIR/../scripts/ars_write_scope_guard.py"

# --- Read the payload from stdin ONCE (we must replay it to the guard subprocess) ---------
# Known trade-off (gemini round-6 P2, accepted): the payload is held in a shell variable and
# replayed with `printf '%s'`. `printf` is a builtin so it is NOT bound by ARG_MAX, and the
# stripped trailing newline is irrelevant to the guard's JSON parse, so for ordinary hook
# payloads this is safe. A multi-megabyte Write payload on a POSIX shell that caps variable
# length is the narrow case this does not cover; buffering to a private temp file would handle
# it but adds another temp-file lifecycle (and symlink surface) to a hot path, so it is left as
# documented degradation rather than fixed speculatively.
PAYLOAD=$(cat)

# --- Marker: did this candidate start real Python? ---------------------------------------
# Each candidate runs one Python process (#1015, below) whose first output is the marker line.
# A 0-byte Store stub fails to execute / prints nothing, so it is skipped. We bound each run
# so a broken-but-hanging interpreter can't wedge the hot path (spec §3.3): prefer `timeout`
# when present, else a portable process-group watchdog.
MARKER=ARS_PY_OK
END_MARKER=ARS_PY_END
NL='
'
# Per-candidate (and guard) wall-clock bound, seconds. A small ops knob; validated to be a
# bare integer so it can't smuggle anything into the `timeout`/`sleep` args. Default 3.
PROBE_BOUND=${ARS_PROBE_BOUND:-3}
case "$PROBE_BOUND" in
    ''|*[!0-9]*) PROBE_BOUND=3 ;;
esac

# ARS_GUARD_FORCE_WATCHDOG=1 forces the no-`timeout` watchdog path even on hosts that HAVE
# `timeout`. This is a test/debug switch: it only changes the BOUNDING MECHANISM (timeout
# binary vs process-group watchdog), never the security decision — both paths enforce the
# same wall-clock bound and the same pass-through-on-overrun posture. Honored if set; safe
# to leave unset (the default prefers a usable `timeout` binary when present).
#
# #970: a `timeout` on PATH is used only if it accepts the GNU form we call it with
# (`timeout <N>s cmd`). On Git for Windows, `timeout` can resolve to the Windows built-in
# timeout.exe (`/T <seconds>`), which rejects that form and exits non-zero; trusting mere
# existence failed every bounded call, so no Python was ever found and every write passed
# through. A present-but-foreign `timeout` now takes the watchdog fallback, like a missing one.
# Decided once per launch, not per bounded call. `-k 1s` bounds the probe itself at about 2s
# even if the `true` on PATH hangs and ignores SIGTERM; a `timeout` without `-k` fails the
# probe and also takes the fallback, so the probe can never disable the guard.
TIMEOUT_USABLE=
if [ -z "${ARS_GUARD_FORCE_WATCHDOG:-}" ] && command -v timeout >/dev/null 2>&1 \
        && timeout -k 1s 1s true </dev/null >/dev/null 2>&1; then
    TIMEOUT_USABLE=1
fi
have_timeout() {
    [ -n "$TIMEOUT_USABLE" ]
}

# Reserved exit status meaning "the bounded command was killed for overrunning its bound".
TIMEOUT_STATUS=124

# Run "$@" with a wall-clock bound; its stdout flows to OUR stdout (capture via $(...)).
# Returns the command's real exit status, or $TIMEOUT_STATUS if it overran the bound.
# Stdin for "$@" is whatever the caller arranges (we redirect it per call site) — the guard
# call site PIPES the payload in, so the bounded command MUST keep that stdin.
run_bounded() {
    if have_timeout; then
        # GNU timeout exits 124 on timeout — normalize to our sentinel for a uniform caller.
        timeout -k 1s "${PROBE_BOUND}s" "$@"
        _st=$?
        [ "$_st" -eq 124 ] && return "$TIMEOUT_STATUS"
        return "$_st"
    fi
    # No usable `timeout` binary: a portable background-and-watchdog fallback. Several POSIX subtleties
    # bite here, all of which broke a naive version (#454 dual-track):
    #
    #  1. STDIN: a backgrounded (`&`) command's stdin defaults to /dev/null, which would feed
    #     the GUARD an EMPTY payload (guard reads nothing -> pass-through -> a real `deny` is
    #     LOST and the guard is dead on any timeout-less host). We stash this function's stdin
    #     on fd 3 and redirect the job's stdin from it (`<&3`) so the piped payload arrives.
    #  2. STDOUT: capturing the job's stdout through the `$(...)` pipe directly would WEDGE the
    #     pipe — if the job spawns a grandchild we can't reap (no `setsid` to group-kill), that
    #     orphan keeps the pipe's write end open and `$(...)` blocks until it dies (the whole
    #     point of the bound). So the job writes stdout to a temp file; we `cat` it back after
    #     reaping the direct child. The orphan may linger but can no longer wedge the hot path.
    #  3. KILL: with `setsid` we new-pgid the job and signal the whole group (negative pid) so
    #     TERM-ignoring children die too; without it we can only reach the direct pid, so a
    #     grandchild a hung interpreter spawned can be ORPHANED (it no longer wedges the hot
    #     path per (2), but it lingers). There is no fully portable POSIX reap without process
    #     groups / setsid / job-control, and inventing one would add fragility for a doubly-
    #     degraded case (no `timeout` AND no `setsid` AND a broken interpreter that forks — the
    #     real marker probe and guard never spawn grandchildren). Accepted; prefer `timeout`
    #     (path A) and `setsid` where present (codex round-6 P2).
    #  4. TIMEOUT DETECTION via a DONE-FILE handshake, not the exit code (a TERM'd `sh` wrapper
    #     does not reliably surface 143/137) and not "did the kill succeed" (gemini round-6 P1
    #     refuted that: after `wait` reaps the child its pid is freed, and if the OS recycles it
    #     before the parent disarms the watchdog, a blind `kill` would land on an INNOCENT
    #     unrelated process — succeeding, so it would both false-flag a timeout AND signal the
    #     wrong pid). Instead the parent writes a done-file the instant `wait` returns; the
    #     watchdog kills (and flags) ONLY if that file is still absent when its sleep elapses.
    #     So "child finished in time" and "child overran" are decided by the handshake, never by
    #     racing a pid. mktemp failure must NOT fall back to a predictable /tmp path: a local
    #     attacker could pre-create it as a symlink, our redirect would fail, and the launcher
    #     would treat that as a broken guard and fail OPEN (gemini round-6 P1). If we can't get a
    #     private temp, degrade safely to pass-through instead of writing a guessable path.
    _rb_out=$(mktemp 2>/dev/null) || emit_passthrough_and_exit
    _rb_fired=$(mktemp 2>/dev/null) || { rm -f "$_rb_out" 2>/dev/null; emit_passthrough_and_exit; }
    _rb_done=$(mktemp 2>/dev/null) || { rm -f "$_rb_out" "$_rb_fired" 2>/dev/null; emit_passthrough_and_exit; }
    rm -f "$_rb_fired" 2>/dev/null  # absent = watchdog has not fired
    rm -f "$_rb_done" 2>/dev/null   # absent = parent has not yet signalled completion
    if command -v setsid >/dev/null 2>&1; then
        { setsid "$@" >"$_rb_out" <&3 3<&- & } 3<&0
    else
        { "$@" >"$_rb_out" <&3 3<&- & } 3<&0
    fi
    _cmd_pid=$!
    # The watchdog subshell (and the `sleep` it forks) must NOT inherit our stdout: when the
    # caller captures run_bounded via `$(...)`, an inherited fd1 IS that pipe, and after we
    # kill the subshell its orphaned `sleep` keeps the write end open — the caller's `$(...)`
    # then blocks until the FULL bound elapses even though the job finished in milliseconds.
    # That stall happened on every healthy probe/guard run on every timeout-less host (~2x
    # bound per hook call, measured 6.1s at the default bound on stock macOS) and is the
    # load-margin flake #545 documents. Same reasoning as note (2) above for the job itself;
    # the watchdog writes nothing to stdout, so /dev/null loses nothing.
    ( sleep "$PROBE_BOUND"
      # If the parent already signalled completion, the child finished within the bound: do NOT
      # kill (its pid may have been recycled to an innocent process) and do NOT flag a timeout.
      if [ ! -f "$_rb_done" ]; then
          # Real overrun: kill the whole process group (negative pid) when we can, else the bare
          # pid, and record the timeout. Re-check the done-file before the hard KILL too.
          kill -TERM "-$_cmd_pid" 2>/dev/null || kill -TERM "$_cmd_pid" 2>/dev/null
          : >"$_rb_fired"
          sleep 1
          if [ ! -f "$_rb_done" ]; then
              kill -KILL "-$_cmd_pid" 2>/dev/null || kill -KILL "$_cmd_pid" 2>/dev/null
          fi
      fi
    ) >/dev/null 2>&1 &
    _watch_pid=$!
    wait "$_cmd_pid" 2>/dev/null
    _st=$?
    : >"$_rb_done"  # DISARM the watchdog before reaping it — closes the pid-reuse race window
    kill "$_watch_pid" 2>/dev/null
    wait "$_watch_pid" 2>/dev/null
    cat "$_rb_out" 2>/dev/null  # replay captured stdout to OUR stdout (for the $(...) caller)
    if [ -f "$_rb_fired" ]; then
        rm -f "$_rb_out" "$_rb_fired" "$_rb_done" 2>/dev/null
        return "$TIMEOUT_STATUS"
    fi
    rm -f "$_rb_out" "$_rb_fired" "$_rb_done" 2>/dev/null
    return "$_st"
}

# --- Run the guard: one Python process per tool call (#1015) -----------------------------
# On Windows with the Python Install Manager, `py` is an App Execution Alias, and each launch
# through an alias makes AppXSvc run an update check that leaks memory (python/pymanager#396).
# So each candidate runs ONE process that does what a probe, the guard run, and a JSON check
# did before: GUARD_RUNNER below writes the marker line straight to fd 1, runs the guard in the
# same process with its stdout captured (fd 1 points at the null device meanwhile, so a write
# that goes around sys.stdout is lost, not mixed into the output), and writes the guard's
# decision only if the guard exited 0 and printed a JSON object with "hookSpecificOutput".
# It re-encodes that object as ASCII JSON on one line followed by an end line, flushes
# stderr, then ends with os._exit so no exit handler can print after it. The guard reads
# stdin as UTF-8, the encoding Claude Code sends; -I would otherwise drop a PYTHONUTF8 or
# PYTHONIOENCODING setting and leave the locale encoding. A SystemExit code maps to the
# exit status Python would give it; an integer outside the C int range counts as a failure. -I keeps PYTHON* variables, the user site, and the working
# directory out of the process. Python 3.4 syntax only: older versions, and Python 2, which
# has no -I, fail before the marker and the next candidate runs.
# shellcheck disable=SC2016  # Python source, not shell: nothing in it is expanded
GUARD_RUNNER='import io, json, os, runpy, sys
def emit(data):
    while data:
        data = data[os.write(1, data):]
emit(b"ARS_PY_OK\n")
guard = sys.argv[1]
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8")
captured = io.BytesIO()
out = io.TextIOWrapper(captured, encoding="utf-8", write_through=True)
saved_fd = os.dup(1)
null_fd = os.open(os.devnull, os.O_WRONLY)
os.dup2(null_fd, 1)
real_stdout = sys.stdout
sys.stdout = out
status = 0
try:
    sys.argv = [guard]
    runpy.run_path(guard, run_name="__main__")
except SystemExit as exc:
    if exc.code is None:
        status = 0
    elif isinstance(exc.code, int) and -2 ** 31 <= exc.code < 2 ** 31:
        status = exc.code if os.name == "nt" else exc.code & 255
    else:
        status = 1
except BaseException:
    status = 1
finally:
    sys.stdout = real_stdout
    os.dup2(saved_fd, 1)
try:
    sys.stderr.flush()
except Exception:
    pass
if status != 0:
    os._exit(1)
try:
    out.flush()
    decision = json.loads(captured.getvalue().decode("utf-8"))
except Exception:
    os._exit(1)
if not (isinstance(decision, dict) and "hookSpecificOutput" in decision):
    os._exit(1)
emit(json.dumps(decision, ensure_ascii=True).encode("ascii") + b"\nARS_PY_END")
os._exit(0)
'

# Capture the guard's stderr to a temp so we can RELAY it on the success path (P2-h: the guard
# has its own no-silent advisories — absent agent_type / schema drift / unreadable manifest —
# that must surface; the launcher only suppresses stderr on its OWN degraded paths). On the
# broken path we drop it, since broken-guard noise on every hot-path call is the #454 spam.
# No predictable /tmp fallback: a guessable path is a symlink-attack surface, and a redirect
# onto an attacker-owned symlink fails -> we'd read that as a broken guard and fail OPEN
# (gemini round-6 P1). If mktemp can't give us a private file, degrade safely to pass-through.
GUARD_ERR=$(mktemp 2>/dev/null) || emit_passthrough_and_exit

# Prefer PATH-resolved Python executables outside WindowsApps. If those are absent, try the
# Python Install Manager's documented global-alias directory under LOCALAPPDATA before the
# WindowsApps aliases. That directory contains direct commands for installed runtimes, so a
# manager-only machine can run its installed Python without starting the App Execution Alias.
# We inspect executable paths, never text printed by a candidate interpreter.
#
# Check the first PATH match directly. Only when it is under WindowsApps (or cannot be
# verified) scan later entries for a regular installation. The ordinary path therefore keeps
# its fast first-match behavior, while a WindowsApps-first PATH can still find real Python.
# Only symlinks need subprocess-based resolution.
is_windowsapps_candidate() {
    _path=$1
    case "$_path" in
        /*|[A-Za-z]:[\\/]*) ;;
        *) return 2 ;;
    esac
    _check_windowsapps_path "$_path" && return 0
    [ -L "$_path" ] || return 1
    if command -v cygpath >/dev/null 2>&1; then
        _winpath=$(cygpath -aw -- "$_path" 2>/dev/null) || _winpath=
        if [ -n "$_winpath" ] && _check_windowsapps_path "$_winpath"; then
            return 0
        fi
    fi
    _resolved=
    if command -v realpath >/dev/null 2>&1; then
        _resolved=$(realpath -e "$_path" 2>/dev/null) \
            || _resolved=$(realpath "$_path" 2>/dev/null) \
            || _resolved=
    fi
    if [ -z "$_resolved" ] && command -v readlink >/dev/null 2>&1; then
        _resolved=$(readlink -f "$_path" 2>/dev/null) || _resolved=
    fi
    [ -n "$_resolved" ] || return 2
    _check_windowsapps_path "$_resolved" && return 0
    if command -v cygpath >/dev/null 2>&1; then
        _winpath=$(cygpath -aw -- "$_resolved" 2>/dev/null) || _winpath=
        if [ -n "$_winpath" ] && _check_windowsapps_path "$_winpath"; then
            return 0
        fi
    fi
    return 1
}

_check_windowsapps_path() {
    case "$1" in
        *"/"[Ww][Ii][Nn][Dd][Oo][Ww][Ss][Aa][Pp][Pp][Ss]"/"*|*"/"[Ww][Ii][Nn][Dd][Oo][Ww][Ss][Aa][Pp][Pp][Ss]|*"\\"[Ww][Ii][Nn][Dd][Oo][Ww][Ss][Aa][Pp][Pp][Ss]"\\"*|*"\\"[Ww][Ii][Nn][Dd][Oo][Ww][Ss][Aa][Pp][Pp][Ss]) return 0 ;;
    esac
    return 1
}

# Run one executable with the established single-process guard runner. Return 1 when the
# candidate did not start clean Python and should be skipped; return 2 when it started but
# the guard itself broke, which stops all further attempts and passes through as before.
run_guard_candidate() {
    _candidate=$1
    shift
    GUARD_OUT=$(printf '%s' "$PAYLOAD" | run_bounded "$_candidate" "$@" -I -c "$GUARD_RUNNER" "$GUARD" 2>"$GUARD_ERR")
    GUARD_STATUS=$?
    case $GUARD_OUT in
        "$MARKER" | "$MARKER$NL"*) ;;
        *) return 1 ;;
    esac
    if [ "$GUARD_STATUS" -ne 0 ] || [ "$GUARD_OUT" = "$MARKER" ]; then
        return 2
    fi
    case $GUARD_OUT in
        "$MARKER$NL"*"$NL$END_MARKER") ;;
        *) return 1 ;;
    esac
    DECISION=${GUARD_OUT#"$MARKER$NL"}
    DECISION=${DECISION%"$NL$END_MARKER"}
    case $DECISION in
        *"$NL"*) return 1 ;;
        "{"*"}")
            [ -s "$GUARD_ERR" ] && cat "$GUARD_ERR" >&2
            rm -f "$GUARD_ERR" 2>/dev/null
            printf '%s\n' "$DECISION"
            exit 0
            ;;
    esac
    return 1
}

# Candidates in their historical order; `py -3` remains the last-resort Install Manager
# route. For each one:
#   * no marker line first (stub, missing interpreter, hang before start) -> next candidate;
#   * marker, exit 0, one line of JSON object, and the end line -> forward that decision;
#   * marker, exit 0, and anything else after it -> the runner always ends with os._exit, so
#     the extra text came from the candidate itself (a wrapper that prints after Python, say);
#     the next candidate runs, as a probe that printed more than the marker was skipped before;
#   * marker and a non-zero exit, a timeout, or nothing after it (the guard ended the process
#     itself) -> the guard is BROKEN; per the maintainer
#     decision (§3.2.1) degrade to pass-through + exit 0, never block, and do not run the
#     guard again under another candidate.
_stop_all_candidates=
_fallback_py=
_fallback_python3=
_fallback_python=
for cand in "py -3" "python3" "python"; do
    case "$cand" in
        "py -3") _name=py; _args=-3 ;;
        *) _name=$cand; _args= ;;
    esac
    _first_candidate=$(command -v "$_name" 2>/dev/null) || continue
    [ -x "$_first_candidate" ] || continue
    is_windowsapps_candidate "$_first_candidate"
    _windowsapps_status=$?
    if [ "$_windowsapps_status" -eq 1 ]; then
        _candidate=$_first_candidate
    else
        # Keep WindowsApps/unverifiable first matches for the legacy last-resort pass.
        case "$cand" in
            "py -3") _fallback_py=$_first_candidate ;;
            "python3") _fallback_python3=$_first_candidate ;;
            "python") _fallback_python=$_first_candidate ;;
        esac
        _candidate=
        _old_ifs=$IFS
        IFS=:
        set -f
        _after_first=
        for _dir in ${PATH:-}; do
            [ -n "$_dir" ] || _dir=.
            _path_candidate="$_dir/$_name"
            if [ ! -x "$_path_candidate" ] && [ -x "$_path_candidate.exe" ]; then
                _path_candidate="$_path_candidate.exe"
            fi
            if [ -z "$_after_first" ]; then
                [ "$_path_candidate" = "$_first_candidate" ] && _after_first=1
                continue
            fi
            [ -x "$_path_candidate" ] || continue
            is_windowsapps_candidate "$_path_candidate"
            _windowsapps_status=$?
            [ "$_windowsapps_status" -eq 1 ] || continue
            _candidate=$_path_candidate
            break
        done
        set +f
        IFS=$_old_ifs
    fi
    [ -n "$_candidate" ] || continue
    if [ -n "$_args" ]; then
        run_guard_candidate "$_candidate" "$_args"
    else
        run_guard_candidate "$_candidate"
    fi
    _candidate_status=$?
    if [ "$_candidate_status" -eq 2 ]; then
        _stop_all_candidates=1
    fi
    [ -z "$_stop_all_candidates" ] || break
done

# Python Install Manager offers a default global-alias directory at
# %LOCALAPPDATA%\Python\bin. Its python3/python executables target installed runtimes
# directly; trying these before WindowsApps avoids launching the manager alias on the common
# default installation, even when the optional directory was not added to PATH.
if [ -z "$_stop_all_candidates" ] && [ -n "${LOCALAPPDATA:-}" ]; then
    case "$LOCALAPPDATA" in
        /*) _manager_root=$LOCALAPPDATA ;;
        [A-Za-z]:/*) _manager_root=$LOCALAPPDATA ;;
        [A-Za-z]:\\*)
            # Git Bash accepts drive paths with forward slashes. Convert backslashes using
            # shell built-ins first, avoiding a cygpath process on the Windows hot path.
            _old_ifs=$IFS
            IFS='\'
            set -f
            set -- $LOCALAPPDATA
            set +f
            IFS=$_old_ifs
            _manager_root=
            for _manager_part do
                if [ -n "$_manager_root" ]; then
                    _manager_root=$_manager_root/$_manager_part
                else
                    _manager_root=$_manager_part
                fi
            done
            ;;
        *)
            _manager_root=
            ;;
    esac
    # Keep cygpath as a compatibility fallback for paths that are not directly addressable
    # by the current shell (for example, POSIX CI tests mapping a native Windows path).
    if [ -z "$_manager_root" ] || { [ ! -d "$_manager_root" ]; }; then
            if command -v cygpath >/dev/null 2>&1; then
                _manager_root=$(cygpath -u -- "$LOCALAPPDATA" 2>/dev/null) || _manager_root=
            fi
    fi
    if [ -n "$_manager_root" ] && [ -d "$_manager_root/Python/bin" ]; then
        for _manager_name in python3.exe python.exe; do
            _manager_candidate="$_manager_root/Python/bin/$_manager_name"
            [ -f "$_manager_candidate" ] || continue
            is_windowsapps_candidate "$_manager_candidate"
            _windowsapps_status=$?
            [ "$_windowsapps_status" -eq 1 ] || continue
            run_guard_candidate "$_manager_candidate"
            _candidate_status=$?
            if [ "$_candidate_status" -eq 2 ]; then
                _stop_all_candidates=1
                break
            fi
        done
    fi
fi

# Keep only WindowsApps or unverifiable PATH entries as the final fallback. Candidates already
# run in the preferred pass are not started again after a failed probe.
if [ -z "$_stop_all_candidates" ]; then
    for cand in "py -3" "python3" "python"; do
        case "$cand" in
            "py -3") _candidate=$_fallback_py; _args=-3 ;;
            "python3") _candidate=$_fallback_python3; _args= ;;
            "python") _candidate=$_fallback_python; _args= ;;
        esac
        [ -n "$_candidate" ] || continue
        if [ -n "$_args" ]; then
            run_guard_candidate "$_candidate" "$_args"
        else
            run_guard_candidate "$_candidate"
        fi
        _candidate_status=$?
        if [ "$_candidate_status" -eq 2 ]; then
            _stop_all_candidates=1
            break
        fi
    done
fi

# Guard broke / timed out / produced invalid output. Degrade, don't block, don't spam.
# The same holds when no candidate started Python.
rm -f "$GUARD_ERR" 2>/dev/null
emit_passthrough_and_exit
