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

# --- #1025: prefer a non-WindowsApps interpreter over the alias candidates --------------
# On Windows with the Python Install Manager, `py` is an App Execution Alias; each launch
# through the alias makes AppXSvc run an update check that leaks memory (python/pymanager#396,
# #1015). If a real interpreter is already reachable on PATH outside WindowsApps, using it
# instead avoids the alias path entirely, rather than only cutting launches per call (#1015).
#
# We only ever look at PATH entries' own filesystem paths, never a candidate's printed output:
# an approach that took the interpreter path FROM a probe's output kept raising new review
# findings across three rounds in #1019 and was replaced, so this repeats that lesson rather
# than the rejected approach.
#
# #1130 review (round 3) simplified this to the smallest version that still helps:
#  - it only runs on MINGW/MSYS/Cygwin shells (round 1 item 3). Tests exercise this by
#    stubbing `uname` on the test PATH to print a MINGW/MSYS/CYGWIN string; there is no
#    production env-var override, since one was tried in round 2 and any non-empty value of
#    it, including "0", turned the walk on everywhere, including WSL and Linux, bringing back
#    the exact pass-through this gate exists to prevent. On WSL, Windows-PATH interop can put
#    a Windows py.exe on PATH; it prints the marker, then cannot open this script's own Linux
#    guard path, so try_candidate returns 1 and every write degrades to pass-through. macOS,
#    Linux and plain WSL keep the unmodified pre-#1025 candidate order instead of running
#    this walk at all.
#  - it only accepts ABSOLUTE PATH entries (round 1 item 1): a relative entry such as `.`
#    would let a WindowsApps-preceding CWD executable win.
#  - it splits PATH without word-splitting/globbing (round 1 item 2): the previous
#    `set -- $PATH` under IFS=: does pathname expansion with no `set -f` in effect, so an
#    entry such as `/opt/kits/[ab]` could glob-expand to a path that was never actually on
#    PATH.
#  - it matches WindowsApps as a whole, case-insensitive path COMPONENT (round 1 item 6): a
#    bare `*WindowsApps*` substring match both misses `.../windowsapps` and wrongly excludes
#    an unrelated directory such as `/opt/MyWindowsAppsTools/bin`.
#  - it STOPS AT THE FIRST absolute, non-WindowsApps directory on PATH that holds `py`,
#    `python3` or `python` (round 3: trying every candidate and skipping ones already tried,
#    per round 1 item 5, and the matching key needed to make that safe across `.exe` and
#    `/./` path variants, per round 2 item 3, each produced new edge cases of their own; a
#    single first match is simpler and has none of them). A broken first match is NOT
#    retried against a later, healthier one here; see the known limit below.
#  - the discovery itself (finding that one candidate path, starting no interpreter) is
#    bounded by a single `run_bounded` call (round 2 item 4): the walk can look at more
#    directories than the old lookup ever reached, so a stalled network-mounted PATH entry
#    must not be able to stall a stat() check outside any bound. If the discovery step
#    itself overruns the bound, or finds nothing, the launcher falls straight through to the
#    unmodified old loop below.
#
# A preferred candidate that prints the marker and then fails or times out is NOT retried
# under the next candidate (round 1 item 4): the launcher degrades to pass-through for that
# call instead, since running the guard a second time is not safe in general (a second run
# could reach a different decision, including one it should have denied). See
# test_preferred_candidate_failure_degrades_to_passthrough_not_retried and
# test_preferred_candidate_timeout_after_marker_degrades_to_passthrough_not_retried.
#
# Known limit: the old loop below has no knowledge of what this walk already tried, so if the
# one non-WindowsApps candidate this walk finds exists but is itself broken (not merely
# missing, which the old loop's own `command -v` would also fail on), the old loop can select
# that exact same broken file again under its own `command -v` resolution and pay the probe
# bound a second time before falling through to the WindowsApps alias. This costs at most one
# extra bounded wait, only in that one case, never more.

# uname -s reliably reports an uppercase MINGW*/MSYS*/CYGWIN* prefix on those shells.
_ARS_WINDOWS_SHELL=
case $(uname -s 2>/dev/null) in
    MINGW*|MSYS*|CYGWIN*) _ARS_WINDOWS_SHELL=1 ;;
esac

# Try one candidate: "$@" is the interpreter argv prefix (e.g. `py -3`, or one resolved path,
# possibly with its own `-3`). Echoes the forwarded decision and returns 0 on a healthy guard
# decision (caller should exit 0 right after); returns 1 to mean "stop trying candidates, guard
# is broken" (the old `break`); returns 2 to mean "try the next candidate" (the old `continue`).
# Defined before try_non_windowsapps_candidates below, which calls it: a shell function must
# already be defined by the time a CALL to it runs, not merely appear earlier in the file text.
try_candidate() {
    GUARD_OUT=$(printf '%s' "$PAYLOAD" | run_bounded "$@" -I -c "$GUARD_RUNNER" "$GUARD" 2>"$GUARD_ERR")
    GUARD_STATUS=$?
    case $GUARD_OUT in
        "$MARKER" | "$MARKER$NL"*) ;;
        *) return 2 ;;
    esac
    [ "$GUARD_STATUS" -eq 0 ] || return 1
    [ "$GUARD_OUT" = "$MARKER" ] && return 1
    case $GUARD_OUT in
        "$MARKER$NL"*"$NL$END_MARKER") ;;
        *) return 2 ;;
    esac
    DECISION=${GUARD_OUT#"$MARKER$NL"}
    DECISION=${DECISION%"$NL$END_MARKER"}
    case $DECISION in
        *"$NL"*) return 2 ;;
        "{"*"}")
            [ -s "$GUARD_ERR" ] && cat "$GUARD_ERR" >&2
            rm -f "$GUARD_ERR" 2>/dev/null
            printf '%s\n' "$DECISION"
            return 0
            ;;
    esac
    return 2
}

# Discovery script run under run_bounded, in its own `sh -c`: walks PATH by hand (absolute
# entries only, WindowsApps excluded as a whole path component, bare name tried before its
# `.exe` form) and prints the FIRST matching "name path" pair, then exits immediately,
# starting no interpreter. PATH is inherited from the parent shell's environment.
_ARS_DISCOVER_SCRIPT='
_rest=$PATH
while [ -n "$_rest" ]; do
    case $_rest in
        *:*) dir=${_rest%%:*}; _rest=${_rest#*:} ;;
        *)   dir=$_rest; _rest= ;;
    esac
    case $dir in
        /*) ;;
        *) continue ;;
    esac
    case "/$dir/" in
        */[Ww][Ii][Nn][Dd][Oo][Ww][Ss][Aa][Pp][Pp][Ss]/*) continue ;;
    esac
    case $dir in
        */) dir=${dir%/} ;;
    esac
    for name in py python3 python; do
        for cand_path in "$dir/$name" "$dir/$name.exe"; do
            if [ -f "$cand_path" ] && [ -x "$cand_path" ]; then
                printf "%s %s\n" "$name" "$cand_path"
                exit 0
            fi
        done
    done
done
'

try_non_windowsapps_candidates() {
    [ -n "$_ARS_WINDOWS_SHELL" ] || return 1
    _discovered=$(run_bounded sh -c "$_ARS_DISCOVER_SCRIPT" 2>/dev/null)
    [ $? -eq 0 ] || return 1
    [ -n "$_discovered" ] || return 1
    _cand_name=${_discovered%% *}
    cand_path=${_discovered#* }
    # Defensive: if run_bounded's own mktemp fails inside the discovery subshell, it can
    # print pass-through JSON with status 0 instead of a "name path" line; a malformed,
    # non-absolute "path" parsed out of that must never reach try_candidate.
    case $cand_path in
        /*) ;;
        *) return 1 ;;
    esac
    if [ "$_cand_name" = "py" ]; then
        try_candidate "$cand_path" -3
    else
        try_candidate "$cand_path"
    fi
    case $? in
        0) exit 0 ;;
        1) rm -f "$GUARD_ERR" 2>/dev/null; emit_passthrough_and_exit ;;
    esac
    # status 2: this one candidate did not produce a usable decision; fall through to the
    # unmodified old loop below, same as if discovery had found nothing at all.
    return 1
}
try_non_windowsapps_candidates

# Candidates in order; `py -3` first (the Windows launcher). For each one:
#   * no marker line first (stub, missing interpreter, hang before start) -> next candidate;
#   * marker, exit 0, one line of JSON object, and the end line -> forward that decision;
#   * marker, exit 0, and anything else after it -> the runner always ends with os._exit, so
#     the extra text came from the candidate itself (a wrapper that prints after Python, say);
#     the next candidate runs, as a probe that printed more than the marker was skipped before;
#   * marker and a non-zero exit, a timeout, or nothing after it (the guard ended the process
#     itself) -> the guard is BROKEN; per the maintainer
#     decision (section 3.2.1) degrade to pass-through + exit 0, never block, and do not run
#     the guard again under another candidate.
# This loop behaves as it did before #1025, on every platform, whether or not the
# walk above ran: exactly `command -v "$1" >/dev/null 2>&1 || continue` then `try_candidate
# "$@"`. It has no knowledge of what the walk above already tried (see the known limit noted
# where the walk is introduced); round 2 added a resolved-path/skip-list variant of this loop
# that this round removed again, since it made the loop's behavior platform-dependent and
# every fix to keep it correct produced a new edge case of its own.
for cand in "py -3" "python3" "python"; do
    # shellcheck disable=SC2086  # intentional word-split: "py -3" -> py with arg -3
    set -- $cand
    command -v "$1" >/dev/null 2>&1 || continue
    try_candidate "$@"
    _tc_status=$?
    [ "$_tc_status" -eq 2 ] && continue
    [ "$_tc_status" -eq 0 ] && exit 0
    break
done

# Guard broke / timed out / produced invalid output. Degrade, don't block, don't spam.
# The same holds when no candidate started Python.
rm -f "$GUARD_ERR" 2>/dev/null
emit_passthrough_and_exit
