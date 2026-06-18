#!/bin/sh
# version: 1.0.0
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
PAYLOAD=$(cat)

# --- Marker probe: does this candidate run real Python? ----------------------------------
# A candidate is "real" iff the probe exits 0 AND prints the exact marker on stdout. A 0-byte
# Store stub fails to execute / prints nothing, so it is skipped. We bound each probe so a
# broken-but-hanging interpreter can't wedge the hot path (spec §3.3): prefer `timeout` when
# present, else a portable process-group watchdog.
MARKER=ARS_PY_OK
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
# to leave unset (the default prefers the `timeout` binary when present).
have_timeout() {
    [ -z "${ARS_GUARD_FORCE_WATCHDOG:-}" ] && command -v timeout >/dev/null 2>&1
}

# Reserved exit status meaning "the bounded command was killed for overrunning its bound".
TIMEOUT_STATUS=124

# Run "$@" with a wall-clock bound; its stdout flows to OUR stdout (capture via $(...)).
# Returns the command's real exit status, or $TIMEOUT_STATUS if it overran the bound.
# Stdin for "$@" is whatever the caller arranges (we redirect it per call site).
run_bounded() {
    if have_timeout; then
        # GNU timeout exits 124 on timeout — normalize to our sentinel for a uniform caller.
        timeout "${PROBE_BOUND}s" "$@"
        _st=$?
        [ "$_st" -eq 124 ] && return "$TIMEOUT_STATUS"
        return "$_st"
    fi
    # No `timeout`: background the command in its OWN process group so a child that ignores
    # TERM (or spawns grandchildren) is still killed as a group. `setsid` gives a new pgid;
    # if setsid is unavailable, fall back to killing the direct pid (best effort).
    if command -v setsid >/dev/null 2>&1; then
        setsid "$@" &
    else
        "$@" &
    fi
    _cmd_pid=$!
    ( sleep "$PROBE_BOUND"
      # Kill the whole process group (negative pid) when we can; else the bare pid.
      kill -TERM "-$_cmd_pid" 2>/dev/null || kill -TERM "$_cmd_pid" 2>/dev/null
      sleep 1
      kill -KILL "-$_cmd_pid" 2>/dev/null || kill -KILL "$_cmd_pid" 2>/dev/null
    ) &
    _watch_pid=$!
    wait "$_cmd_pid" 2>/dev/null
    _st=$?
    kill "$_watch_pid" 2>/dev/null
    wait "$_watch_pid" 2>/dev/null
    # 143 = 128+SIGTERM, 137 = 128+SIGKILL -> the watchdog fired -> treat as timeout.
    if [ "$_st" -eq 143 ] || [ "$_st" -eq 137 ]; then
        return "$TIMEOUT_STATUS"
    fi
    return "$_st"
}

# Echo the first candidate ("cmd args") that verifies as REAL Python, or nothing.
# A candidate qualifies ONLY if the probe exits 0 AND prints exactly the marker on stdout
# (P1-a: a stub that prints the marker but exits non-zero must be rejected). Candidates in
# order; `py -3` first (the Windows launcher).
find_real_python() {
    for cand in "py -3" "python3" "python"; do
        # shellcheck disable=SC2086  # intentional word-split: "py -3" -> py with arg -3
        set -- $cand
        cmd=$1
        command -v "$cmd" >/dev/null 2>&1 || continue
        probe_out=$(run_bounded "$@" -c "import sys; sys.stdout.write('$MARKER')" </dev/null 2>/dev/null)
        probe_status=$?
        if [ "$probe_status" -eq 0 ] && [ "$probe_out" = "$MARKER" ]; then
            printf '%s' "$cand"
            return 0
        fi
    done
    return 1
}

REAL_PY=$(find_real_python) || emit_passthrough_and_exit
[ -n "$REAL_PY" ] || emit_passthrough_and_exit

# is_valid_hook_json: true iff $1 parses as a JSON object containing a top-level
# "hookSpecificOutput" key. Uses the REAL Python we already found (no jq dependency, P1-c:
# substring grep false-accepts e.g. `not json "hookSpecificOutput"`). Reads candidate on stdin.
is_valid_hook_json() {
    # shellcheck disable=SC2086  # $REAL_PY is "py -3" or "python3" — intentional split
    set -- $REAL_PY
    printf '%s' "$GUARD_OUT" | "$@" -c '
import sys, json
try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(1)
sys.exit(0 if isinstance(d, dict) and "hookSpecificOutput" in d else 1)
' >/dev/null 2>&1
}

# --- Supervise the guard subprocess (P1-b: time-bound it too; P1-c: validate JSON) --------
# Run the guard with the found interpreter, replaying the captured payload on its stdin,
# under the SAME wall-clock bound as the probes so a hung guard can't wedge the hot path.
# Decide what to emit:
#   * guard exits 0 AND stdout is a JSON object with hookSpecificOutput -> forward verbatim.
#   * anything else (non-zero, timeout, empty, non-JSON, missing key) -> guard is BROKEN;
#     per the maintainer decision (§3.2.1) degrade to pass-through + exit 0, never block.
# shellcheck disable=SC2086  # $REAL_PY is "py -3" or "python3" — intentional split
set -- $REAL_PY
# Capture the guard's stderr to a temp so we can RELAY it on the success path (P2-h: the guard
# has its own no-silent advisories — absent agent_type / schema drift / unreadable manifest —
# that must surface; the launcher only suppresses stderr on its OWN degraded paths). On the
# broken path we drop it, since broken-guard noise on every hot-path call is the #454 spam.
GUARD_ERR=$(mktemp 2>/dev/null) || GUARD_ERR=/tmp/ars_guard_err.$$
GUARD_OUT=$(printf '%s' "$PAYLOAD" | run_bounded "$@" "$GUARD" 2>"$GUARD_ERR")
GUARD_STATUS=$?

if [ "$GUARD_STATUS" -eq 0 ] && is_valid_hook_json; then
    # Healthy guard decision: relay its stderr advisories, then forward its JSON verbatim.
    [ -s "$GUARD_ERR" ] && cat "$GUARD_ERR" >&2
    rm -f "$GUARD_ERR" 2>/dev/null
    printf '%s\n' "$GUARD_OUT"
    exit 0
fi

# Guard broke / timed out / produced invalid output. Degrade, don't block, don't spam.
rm -f "$GUARD_ERR" 2>/dev/null
emit_passthrough_and_exit
