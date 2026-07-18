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

# Canonical version grammar (single source of truth). Digit-led, then only
# alnum / dot / plus / hyphen — semver-ish. Every external version value
# (local manifest, remote manifest, cached fields) is validated against this
# BEFORE it is compared, cached, or emitted (#524 validate-before-propagate),
# so a punctuation-separated payload or a raw control byte cannot ride a
# `version` string into the SessionStart additionalContext.
VALID_VERSION_RE='^[0-9][0-9A-Za-z.+-]*$'
is_valid_version() { [[ "$1" =~ $VALID_VERSION_RE ]]; }

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
LOCAL_CONTENT="$(cat "${LOCAL_MANIFEST}" 2>/dev/null || true)"
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
    # abort if awk is missing/errors on a fresh cache (P2-c).
    CACHED=""
    while IFS= read -r CACHED || [[ -n "${CACHED}" ]]; do
      break
    done < "${CACHE_FILE}" 2>/dev/null || true
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
# Capture curl's exit status explicitly (P2-a). A truncated/timed-out transfer
# can still leave a `version` string in a partial body; treating a nonzero exit
# as success would cache poisoned/partial data. `|| CURL_RC=$?` keeps `set -e`
# from aborting; on any nonzero exit we bail silently, cache untouched.
CURL_RC=0
REMOTE_CONTENT="$(curl -fsSL --max-time 3 "${REMOTE_URL}" 2>/dev/null)" || CURL_RC=$?
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
{
  printf '%s %s %s\n' "${STATE}" "${LOCAL_VER}" "${REMOTE_VER}" > "${TMP_FILE}" \
    && mv -f "${TMP_FILE}" "${CACHE_FILE}"
} 2>/dev/null || { rm -f "${TMP_FILE}" 2>/dev/null; exit 0; }

if [[ "${STATE}" == "UPDATE_AVAILABLE" ]]; then
  printf 'UPDATE_AVAILABLE %s %s\n' "${LOCAL_VER}" "${REMOTE_VER}"
fi
exit 0
