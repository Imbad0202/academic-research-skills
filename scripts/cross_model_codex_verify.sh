#!/usr/bin/env bash
# Subscription-backed Codex transport for one ARS citation-verification prompt.
# Probe 2026-07-16: Codex JSONL uses `type:"item.completed"` + `item.type:"web_search"` for a completed web search and the final `item.type:"agent_message"` item's `item.text` for the final agent message.
# codex exec has no dedicated disable-MCP/skills switch; --ignore-user-config,
# --ignore-rules, --skip-git-repo-check, and an isolated non-git -C directory
# remove configured/project inputs, but built-in Codex runtime behavior remains
# a documented residual.
set -u

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <single-reference-verification-prompt>" >&2
  exit 2
fi

command -v codex >/dev/null 2>&1 || {
  echo "ERROR: codex is required" >&2
  exit 127
}
command -v jq >/dev/null 2>&1 || {
  echo "ERROR: jq is required" >&2
  exit 127
}
[ -n "${ARS_CROSS_MODEL:-}" ] || {
  echo "ERROR: ARS_CROSS_MODEL is not set" >&2
  exit 2
}

PROMPT="$1"
RUN_DIR="$(mktemp -d "${TMPDIR:-/tmp}/ars-codex-verify.XXXXXX")" || exit 1
STREAM="$RUN_DIR/events.jsonl"
trap 'rm -rf "$RUN_DIR"' EXIT

emit_result() {
  # thread_id is the only per-call identifier Codex exposes (`thread.started`).
  # Emitting it makes a bakeoff record auditable after the fact; absent stream
  # (transport failed before any event) yields "", which is the honest value.
  thread_id=""
  events='[]'
  if [ -s "$STREAM" ]; then
    thread_id="$(
      jq -sr '[.[] | select(type == "object" and .type == "thread.started")
                   | .thread_id | select(type == "string")]
              | if length == 0 then "" else .[0] end' "$STREAM" 2>/dev/null || echo ""
    )"
    # ARS_CODEX_EMIT_EVENTS=1 attaches the raw Codex event stream to the result.
    # Without it the events die with $RUN_DIR, and the grounding decision below
    # cannot be re-derived by anyone else: retaining only this function's own
    # output would let an auditor check the harness, never the guard. Off by
    # default because the events carry the full model message.
    if [ "${ARS_CODEX_EMIT_EVENTS:-0}" = "1" ]; then
      events="$(jq -sc '[.[] | select(type == "object")]' "$STREAM" 2>/dev/null || echo '[]')"
    fi
  fi
  jq -cn --arg verdict "$1" --argjson sources "$2" --argjson searched "$3" \
    --arg thread_id "$thread_id" --argjson events "$events" \
    '{verdict: $verdict, sources: $sources, searched: $searched,
      thread_id: $thread_id, events: $events}'
}

# OPENAI_API_KEY is deliberately unset: codex authenticates from auth.json.
if env -u OPENAI_API_KEY codex exec --json --ephemeral --ignore-user-config \
  --ignore-rules --skip-git-repo-check -C "$RUN_DIR" -m "$ARS_CROSS_MODEL" -s read-only \
  -c tools.web_search=true \
  -c model_reasoning_effort="${ARS_CROSS_MODEL_REASONING_EFFORT:-xhigh}" \
  -c service_tier=priority "$PROMPT" >"$STREAM"; then
  :
else
  status=$?
  emit_result NOT_SEARCHED '[]' false
  exit "$status"
fi

# Fail closed: only the probed, completed web_search item proves grounding.
if jq -s -e '
  any(.[];
    type == "object" and
    .type == "item.completed" and
    (.item | type == "object") and
    .item.type == "web_search"
  )
' "$STREAM" >/dev/null 2>&1; then
  searched=true
else
  searched=false
fi

if ! message="$(jq -sr '
  [ .[]
    | select(
        type == "object" and
        .type == "item.completed" and
        (.item | type == "object") and
        .item.type == "agent_message" and
        (.item.text | type == "string")
      )
    | .item.text
  ] | if length == 0 then "" else .[-1] end
' "$STREAM")"; then
  emit_result NOT_SEARCHED '[]' false
  exit 0
fi

verdict=NOT_SEARCHED
sources='[]'
if [ "$searched" = true ]; then
  # Same strict contract as the OpenAI route: one whole-word token, once.
  # Line-oriented rather than `mapfile`: macOS ships Bash 3.2, where mapfile
  # does not exist and `set -u` would then abort before any fail-closed JSON.
  verdict_hits="$(
    printf '%s' "$message" |
      grep -oE '\b(VERIFIED|MISMATCH|NOT_FOUND|NOT_SEARCHED)\b' || true
  )"
  verdict_hit_count="$(printf '%s' "$verdict_hits" | grep -c . || true)"
  if [ "$verdict_hit_count" -eq 1 ]; then
    verdict="$(printf '%s' "$verdict_hits" | head -1)"
    source_lines="$(
      printf '%s' "$message" |
        grep -oE 'https?://[^[:space:]]+' |
        sed "s/[][(){}<>\"'.,;:!]*$//" |
        awk 'NF && !seen[$0]++' || true
    )"
    if ! sources="$(printf '%s\n' "$source_lines" | jq -Rsc 'split("\n") | map(select(length > 0))')"; then
      verdict=NOT_SEARCHED
      sources='[]'
      searched=false
    elif [ "$verdict" = VERIFIED ] && [ "$(jq 'length' <<<"$sources")" -lt 1 ]; then
      verdict=NOT_SEARCHED
      sources='[]'
    fi
  fi
fi

if [ "$searched" != true ]; then
  # Never expose an ungrounded model claim or URL as verification evidence.
  verdict=NOT_SEARCHED
  sources='[]'
fi

emit_result "$verdict" "$sources" "$searched"
