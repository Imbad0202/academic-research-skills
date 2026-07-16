#!/usr/bin/env bash
# Live smoke test for the subscription-backed Codex cross-model verifier route.
#
# This is a manual operator/CI gate: it makes one real Codex subscription call,
# using ~/.codex/auth.json rather than OPENAI_API_KEY. Codex exec JSONL does not
# echo service_tier, so "fast"/priority is best-effort and unverifiable from
# output — a documented gap versus the OpenAI smoke test's effort-echo check.
set -u

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ADAPTER="$REPO_ROOT/scripts/cross_model_codex_verify.sh"
FAILURES=0

note() { printf '%s\n' "$*"; }
pass() { printf 'PASS: %s\n' "$*"; }
fail() { printf 'FAIL: %s\n' "$*"; FAILURES=$((FAILURES + 1)); }

command -v codex >/dev/null 2>&1 || { echo "ERROR: codex is required"; exit 1; }
command -v jq >/dev/null 2>&1 || { echo "ERROR: jq is required"; exit 1; }
[ -f "${CODEX_HOME:-$HOME/.codex}/auth.json" ] || {
  echo "ERROR: Codex subscription auth.json is not present";
  exit 1;
}
command -v env >/dev/null 2>&1 || { echo "ERROR: env is required"; exit 1; }
[ -f "$ADAPTER" ] || { echo "ERROR: adapter not found: $ADAPTER"; exit 1; }
[ -n "${ARS_CROSS_MODEL:-}" ] || { echo "ERROR: ARS_CROSS_MODEL is not set"; exit 1; }
case "$ARS_CROSS_MODEL" in
  gpt-*) : ;;
  *) echo "ERROR: this smoke test covers the Codex gpt-* route only (got '$ARS_CROSS_MODEL')"; exit 1 ;;
esac

note "model=$ARS_CROSS_MODEL effort=${ARS_CROSS_MODEL_REASONING_EFFORT:-xhigh} (OPENAI_API_KEY is ignored)"

PROMPT='Verify this academic reference. Check: Does it exist? Are the author
names, year, title, and venue correct? Search the web to confirm — do not
answer from memory.

Respond with exactly one verdict:
- VERIFIED  — found online; include at least one http(s) source URL you found
- MISMATCH  — found, but a field is wrong (state which); include the source
- NOT_FOUND — searched, no matching record exists
- NOT_SEARCHED — you could not actually search the web for this reference

Reference: Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L.,
Gomez, A. N., Kaiser, L., & Polosukhin, I. (2017). Attention is all you need.
Advances in Neural Information Processing Systems, 30.
— Context: cited as the origin of the Transformer architecture.'

if output="$(bash "$ADAPTER" "$PROMPT")"; then
  pass "adapter exited 0"
else
  status=$?
  fail "adapter exited $status"
fi

nonempty_lines="$(printf '%s\n' "${output:-}" | sed '/^$/d' | wc -l | tr -d ' ')"
if [ "$nonempty_lines" -ne 1 ] || ! jq -e '
  type == "object" and
  (.verdict as $verdict | ["VERIFIED", "MISMATCH", "NOT_FOUND", "NOT_SEARCHED"] | index($verdict) != null) and
  (.sources | type == "array") and
  all(.sources[]; type == "string" and test("^https?://")) and
  (.searched | type == "boolean")
' <<<"${output:-}" >/dev/null 2>&1; then
  fail "adapter did not emit one normalized verdict JSON object"
else
  pass "normalized verdict JSON"
fi

searched="$(jq -r '.searched // false' <<<"${output:-}" 2>/dev/null || printf false)"
verdict="$(jq -r '.verdict // empty' <<<"${output:-}" 2>/dev/null || true)"
source_count="$(jq -r 'if (.sources | type == "array") then length else 0 end' <<<"${output:-}" 2>/dev/null || printf 0)"

if [ "$searched" = true ]; then
  pass "completed web-search event present (adapter grounding guard)"
else
  fail "no completed web-search event (adapter returned searched=false)"
fi

case "$verdict" in
  VERIFIED|MISMATCH|NOT_FOUND|NOT_SEARCHED)
    pass "exactly one whole-word verdict token accepted by adapter: $verdict" ;;
  *)
    fail "no single whole-word verdict token accepted by adapter" ;;
esac

if [ "$verdict" = VERIFIED ]; then
  if [ "$source_count" -ge 1 ]; then
    pass "VERIFIED carries $source_count http(s) source URL(s)"
  else
    fail "VERIFIED has no source URL"
  fi
else
  fail "Vaswani fixture did not return VERIFIED (got '${verdict:-none}')"
fi

if [ "$FAILURES" -eq 0 ]; then
  echo "RESULT: PASS"
  exit 0
fi

echo "RESULT: FAIL ($FAILURES check(s) failed)"
exit 1
