# Canonical per-model reasoning-effort vocabulary for the first-party OpenAI
# Responses route (#823). Sourced by scripts/cross_model_smoke_test.sh and by
# the documented OpenAI example in shared/cross_model_verification.md, so the
# two request builders cannot drift apart. POSIX sh; no bashisms.
#
# ars_openai_effort_check MODEL EFFORT
#   Returns 0 when EFFORT may be sent for MODEL (an empty EFFORT always passes:
#   the caller omits the field and the provider default applies). Prints a
#   CROSS-MODEL-ERROR line and returns 1 for an explicitly configured value the
#   model's documentation lists as unsupported. Models without a row are
#   permissive here: the provider rejects an unknown value visibly.
#
# Rows (first-party documentation, checked 2026-09-06):
#   gpt-6-astra   low|medium|high|xhigh|max   (none/minimal/ultra are not API values)
ars_openai_effort_check() {
  _model="$1"; _effort="$2"
  [ -z "$_effort" ] && return 0
  case "$_model" in
    gpt-6-astra)
      case "$_effort" in
        low|medium|high|xhigh|max) return 0 ;;
        *) echo "CROSS-MODEL-ERROR: invalid_astra_reasoning_effort (${_effort}; accepted: low|medium|high|xhigh|max)"; return 1 ;;
      esac ;;
    *) return 0 ;;
  esac
}
