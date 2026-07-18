#!/usr/bin/env bash
# version: 1.0.0
#
# ars_update_check.sh — plugin-install update-available check for the
# SessionStart announce (#544).
#
# Output contract (stdout, single line or nothing):
#   UPDATE_AVAILABLE <installed> <latest>  — remote version differs from installed
#   (nothing)                              — up to date, disabled, not a plugin
#                                            install, or any failure
#
# Exit code: always 0. Every failure path is silent by design — this is
# advisory announce plumbing and must never break session start.
# Spec: docs/design/2026-07-18-544-update-reminder-spec.md
#
# Env:
#   ARS_UPDATE_CHECK              "0" disables everything (no network, no output)
#   ARS_UPDATE_CHECK_STATE_DIR    cache dir (default ~/.cache/ars)
#   ARS_UPDATE_CHECK_REMOTE_URL   remote plugin.json URL (default: raw main)
#   CLAUDE_PLUGIN_ROOT            set by the plugin loader; unset => skip
#
# Bash 3.2 compatible (macOS stock /bin/bash): no associative arrays, no
# ${!var}, regex patterns held in variables before [[ =~ ]].
set -euo pipefail

# Step 1: kill switch
if [[ "${ARS_UPDATE_CHECK:-}" == "0" ]]; then
  exit 0
fi

# Step 2: plugin gate — this is what scopes #544 to plugin installs
if [[ -z "${CLAUDE_PLUGIN_ROOT:-}" ]]; then
  exit 0
fi
LOCAL_MANIFEST="${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json"
if [[ ! -r "${LOCAL_MANIFEST}" ]]; then
  exit 0
fi

# Canonical version grammar (single source of truth). A version string is a
# BOUNDED NUMERIC RELEASE FORMAT (semver), never free text. Every external
# version value (local manifest, remote manifest, cached fields) is validated
# against this BEFORE it is compared, cached, or emitted (#524 validate-before-
# propagate), so a punctuation-separated payload, a raw control byte, or
# kebab-case prose cannot ride a `version` string into the SessionStart
# additionalContext.
#
# Numeric core: 2 to 4 dot-separated numeric components (3.17.0, 3.9.4.0).
# Optional suffix: exactly ONE recognized release marker, not arbitrary words.
# Allow-known (not deny-shape): a value is a version only if it is a bounded
# numeric core plus at most one known marker — so externally-sourced text can
# never smuggle readable prose (e.g. "-ignore-previous-instructions") into the
# SessionStart context, regardless of length.
VERSION_CORE_RE='^[0-9]+(\.[0-9]+){1,3}$'
VERSION_PRERELEASE_RE='^[0-9]+(\.[0-9]+){1,3}[-._](0|[1-9][0-9]*|(rc|alpha|beta|pre|dev|post|rev|build)([.-]?[0-9]+)?)$'
is_valid_version() {
  # 32-char hard cap first (ReDoS-free rejection), then allow-known grammar:
  # a bare numeric core, OR a numeric core + exactly one recognized marker.
  [[ ${#1} -le 32 ]] || return 1
  [[ "$1" =~ $VERSION_CORE_RE ]] && return 0
  [[ "$1" =~ $VERSION_PRERELEASE_RE ]]
}

# First `"version": "<value>"` match. The capture class mirrors the grammar
# (no whitespace/control/exotic chars) so the regex itself won't grab garbage;
# is_valid_version is still applied downstream as the authoritative gate.
VERSION_RE='"version"[[:space:]]*:[[:space:]]*"([0-9][0-9A-Za-z.+-]*)"'

extract_version() {
  local content="$1"
  if [[ "${content}" =~ ${VERSION_RE} ]]; then
    printf '%s' "${BASH_REMATCH[1]}"
  fi
}

# Step 3: local version — extract, then positively validate before use. A
# malformed installed version is treated like an unparseable local manifest:
# silent exit 0.
#
# Redirect stderr around the WHOLE assignment, not just cat (P2-a): on Bash
# 4.4+ a NUL byte in the local manifest makes the SHELL (not cat) print
# "ignored null byte in input" to stderr, and a command-level `2>/dev/null`
# only covers cat. The `{ …; } 2>/dev/null` scopes the redirect over the
# shell's own warning too. Keep exit 0.
LOCAL_CONTENT=""
{ LOCAL_CONTENT="$(cat "${LOCAL_MANIFEST}")" || true; } 2>/dev/null
LOCAL_VER="$(extract_version "${LOCAL_CONTENT}")"
if [[ -z "${LOCAL_VER}" ]] || ! is_valid_version "${LOCAL_VER}"; then
  exit 0
fi

# No resolvable state dir (HOME unset, no override): skip silently rather than
# run cacheless — a cacheless check would fetch every session start, violating
# the once-per-24h steady-state invariant (#544 spec, Invariant 2).
if [[ -z "${ARS_UPDATE_CHECK_STATE_DIR:-}" && -z "${HOME:-}" ]]; then
  exit 0
fi
STATE_DIR="${ARS_UPDATE_CHECK_STATE_DIR:-$HOME/.cache/ars}"
CACHE_FILE="${STATE_DIR}/update-check"

# Step 4: cache consult — render without network when the cache is younger
# than 24h, well-formed, and was recorded for the currently installed version.
# A recorded version that differs from the current one means the user updated
# since the last check: fall through and refetch.
if [[ -f "${CACHE_FILE}" ]]; then
  FRESH="$(find "${CACHE_FILE}" -mmin -1440 2>/dev/null || true)"
  if [[ -n "${FRESH}" ]]; then
    # Read the first line only. Split the three whitespace-separated fields
    # with pure Bash parameter expansion — no awk dependency, no `set -e`
    # abort if awk is missing/errors on a fresh cache.
    #
    # Wrap the read in a compound with stderr redirected AROUND the input open:
    # Bash opens `< "${CACHE_FILE}"` before a command-level `2>/dev/null` takes
    # effect, so a fresh-but-unreadable cache would otherwise leak
    # "Permission denied" to stderr. The enclosing `{ …; } 2>/dev/null` scopes
    # the redirect over the open itself (P2-a). Keep exit 0.
    CACHED=""
    {
      while IFS= read -r CACHED || [[ -n "${CACHED}" ]]; do
        break
      done < "${CACHE_FILE}"
    } 2>/dev/null || true
    # Field 1 (state): up to the first space.
    CACHED_STATE="${CACHED%% *}"
    # Remainder after field 1.
    _REST="${CACHED#* }"
    # Field 2 (local): up to the next space.
    CACHED_LOCAL="${_REST%% *}"
    # Field 3 (remote): remainder after field 2.
    CACHED_REMOTE="${_REST#* }"
    # If the line had fewer than 3 fields, the expansions above collapse onto
    # each other; the validation below rejects the result and we refetch.
    if [[ "${CACHED}" != *" "*" "* ]]; then
      CACHED_STATE=""
      CACHED_LOCAL=""
      CACHED_REMOTE=""
    fi
    # Trust the cached values only if BOTH version fields pass the strict
    # grammar (closes the local-cache injection path — a poisoned <latest>
    # field is rejected, never re-emitted) and the local field still matches
    # the installed version.
    if [[ "${CACHED_LOCAL}" == "${LOCAL_VER}" ]] \
      && is_valid_version "${CACHED_LOCAL}" \
      && is_valid_version "${CACHED_REMOTE}"; then
      case "${CACHED_STATE}" in
        UP_TO_DATE)
          exit 0
          ;;
        UPDATE_AVAILABLE)
          printf 'UPDATE_AVAILABLE %s %s\n' "${CACHED_LOCAL}" "${CACHED_REMOTE}"
          exit 0
          ;;
      esac
    fi
    # Malformed/poisoned cache or local version changed: fall through to refetch.
  fi
fi

# Step 5: remote fetch (3s ceiling). Failure leaves the cache untouched — a
# stale good cache beats a poisoned one; the next session retries.
if ! command -v curl >/dev/null 2>&1; then
  exit 0
fi
REMOTE_URL="${ARS_UPDATE_CHECK_REMOTE_URL:-https://raw.githubusercontent.com/Imbad0202/academic-research-skills/main/.claude-plugin/plugin.json}"
# Capture curl's exit status explicitly. A truncated/timed-out transfer can
# still leave a `version` string in a partial body; treating a nonzero exit as
# success would cache poisoned/partial data. `|| CURL_RC=$?` keeps `set -e`
# from aborting; on any nonzero exit we bail silently, cache untouched.
#
# Redirect stderr around the WHOLE assignment, not just curl (P2-c): on Bash
# 4.4+ a NUL byte in the body makes the SHELL (not curl) print "ignored null
# byte in input" to stderr, and the inner `2>/dev/null` only covered curl. The
# `{ …; } 2>/dev/null` scopes the redirect over the shell's own warning too.
# `|| CURL_RC=$?` stays INSIDE the block so curl's exit status is preserved.
CURL_RC=0
{ REMOTE_CONTENT="$(curl -fsSL --max-time 3 "${REMOTE_URL}")" || CURL_RC=$?; } 2>/dev/null
if [[ "${CURL_RC}" -ne 0 ]]; then
  exit 0
fi
REMOTE_VER="$(extract_version "${REMOTE_CONTENT}")"
# Positively validate the remote version BEFORE it is compared, cached, or
# emitted. A malformed/hostile remote must not poison the cache — same silent
# exit-0-without-cache-write as a fetch failure.
if [[ -z "${REMOTE_VER}" ]] || ! is_valid_version "${REMOTE_VER}"; then
  exit 0
fi

# Step 6: compare (plain string inequality — the only question is whether
# /plugin update would deliver something different) + atomic cache write.
mkdir -p "${STATE_DIR}" 2>/dev/null || exit 0
if [[ "${LOCAL_VER}" == "${REMOTE_VER}" ]]; then
  STATE="UP_TO_DATE"
else
  STATE="UPDATE_AVAILABLE"
fi
TMP_FILE="${CACHE_FILE}.tmp.$$"
# Wrap the whole write in a redirected compound so an unwritable dir can't leak
# an "cannot create" error to stderr: Bash opens `> "${TMP_FILE}"` before the
# command-level `2>/dev/null` applies, so the redirect must be scoped by the
# enclosing block instead (P2-b).
#
# Every cleanup path must return 0. If the write/mv fails AND rm is unavailable
# or also fails (constrained PATH with neither mv nor rm), `set -e` would abort
# the fallback before `exit 0`, returning 127 and leaving the temp file. The
# trailing `|| :` on the rm and the `exit 0` immediately after guarantee the
# always-exit-0 contract holds even when mv/rm are absent.
{
  printf '%s %s %s\n' "${STATE}" "${LOCAL_VER}" "${REMOTE_VER}" > "${TMP_FILE}" \
    && mv -f "${TMP_FILE}" "${CACHE_FILE}"
} 2>/dev/null || { rm -f "${TMP_FILE}" 2>/dev/null || :; exit 0; }

if [[ "${STATE}" == "UPDATE_AVAILABLE" ]]; then
  printf 'UPDATE_AVAILABLE %s %s\n' "${LOCAL_VER}" "${REMOTE_VER}"
fi
exit 0
