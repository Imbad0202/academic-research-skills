#!/usr/bin/env bash
# version: 1.5.0
#
# SessionStart hook script for the ARS Claude Code plugin (v3.7.0+).
#
# Reads the SessionStart event JSON on stdin and emits a hookSpecificOutput
# JSON with `additionalContext` describing what ARS provides in this session.
# The plugin loader injects that context into the LLM's first turn so the
# user (and Claude) can see, on session start, that ARS is loaded and which
# slash commands and plugin agents are available.
#
# Allowed invokers: Claude Code's plugin loader (SessionStart event).
# This script is safe to run from any context; it does not invoke codex,
# does not write outside its own stdout, and produces no side effects on
# the working tree.
#
# Exit codes:
#   0    Always — even on parse failure, fall back to the long-form announce.
#   2    Reserved (not used; SessionStart cannot block).

set -euo pipefail

# ---------------------------------------------------------------------------
# This script intentionally avoids Bash 4+ features (no associative arrays,
# no indirect expansion via `${!var}`, no `<<<` here-strings on the hot
# path). It runs cleanly on macOS stock /bin/bash 3.2 so plugin users
# don't have to `brew install bash` just to see the SessionStart announce.
# `run_codex_audit.sh` does need Bash 4+ — that wrapper guards itself.
# ---------------------------------------------------------------------------
# Read SessionStart event JSON from stdin and pull `source` (one of
# startup / resume / clear / compact) without taking a hard dependency on
# jq — many ARS users won't have it installed and we want this hook to
# work out of the box.
# ---------------------------------------------------------------------------
INPUT=""
if [[ ! -t 0 ]]; then
  INPUT=$(cat)
fi

SOURCE="startup"
if [[ -n "${INPUT}" ]]; then
  # Match `"source": "<value>"` with optional whitespace; tolerate single-line
  # or multi-line JSON. Falls through to default `startup` on any parse miss.
  if [[ "${INPUT}" =~ \"source\"[[:space:]]*:[[:space:]]*\"([a-z]+)\" ]]; then
    SOURCE="${BASH_REMATCH[1]}"
  fi
fi

# ---------------------------------------------------------------------------
# For `compact` and `resume` we keep the announce minimal: the LLM already
# has prior ARS context from the resumed transcript or carried-over summary,
# and re-injecting the full slash-command list every resume burns context.
# `startup` and `clear` get the full version.
# ---------------------------------------------------------------------------
case "${SOURCE}" in
  compact|resume)
    ANNOUNCE="ARS plugin still loaded after ${SOURCE}. Slash commands: /ars-full /ars-plan /ars-outline /ars-revision /ars-revision-coach /ars-rebuttal-audit /ars-abstract /ars-lit-review /ars-3w /ars-reviewer /ars-format-convert /ars-citation-check /ars-disclosure /ars-mark-read /ars-unmark-read /ars-cache-invalidate. Plugin agents: synthesis_agent, research_architect_agent, report_compiler_agent. If an ARS pipeline run is in progress, run its handoff check before continuing (academic-pipeline orchestrator, section Run ledger and handoff check, #887): compare what the session now shows with the run ledger beside the Material Passport, and ask again for any decision it cannot show in the user's words."
    ;;
  startup|clear|*)
    # -----------------------------------------------------------------
    # #544 update reminder. The checker is consulted INSIDE this arm so
    # compact/resume structurally never run it (no network mid-session).
    # Any checker failure degrades to "no reminder" — the announce must
    # never break. Wording lives here, not in the checker (single wording
    # surface; ASCII "->" keeps the JSON escaping path trivial).
    # -----------------------------------------------------------------
    UPDATE_LINE=""
    if [[ -n "${CLAUDE_PLUGIN_ROOT:-}" ]]; then
      _UPD=$(bash "${CLAUDE_PLUGIN_ROOT}/scripts/ars_update_check.sh" 2>/dev/null || true)
      _UPDATE_RE='^UPDATE_AVAILABLE[[:space:]]([^[:space:]]+)[[:space:]]([^[:space:]]+)$'
      if [[ "${_UPD}" =~ ${_UPDATE_RE} ]]; then
        UPDATE_LINE="ARS update available: v${BASH_REMATCH[2]} (installed: v${BASH_REMATCH[1]}). Run /plugin update academic-research-skills, or enable auto-update in /plugin -> Marketplaces.

"
      fi
    fi
    ANNOUNCE="${UPDATE_LINE}ARS (academic-research-skills) plugin loaded.

Slash commands (16) — light modes pin sonnet in frontmatter; the three heavy modes inherit the session model (the v3.7.0 opus floor was retired in the 2026-06 harness pass):
  /ars-full              inherit Full pipeline (research → write → review → revise → finalize)
  /ars-revision-coach    inherit Parse reviewer comments → Revision Roadmap + Response Letter skeleton
  /ars-reviewer          inherit academic-paper-reviewer full mode — simulated peer-review panel
  /ars-plan              sonnet  Socratic chapter-by-chapter planning
  /ars-outline           sonnet  Detailed outline + evidence map (no full draft)
  /ars-revision          sonnet  Revised draft + R&R responses
  /ars-rebuttal-audit    sonnet  QA an existing rebuttal draft against reviewer comments (advisory)
  /ars-abstract          sonnet  Bilingual abstract + keywords
  /ars-lit-review        sonnet  Annotated bibliography in paper format
  /ars-3w                sonnet  WHY / HOW / WHAT three-way paper scan (lighter than lit-review)
  /ars-format-convert    sonnet  Convert paper between LaTeX / DOCX / PDF / Markdown
  /ars-citation-check    sonnet  Citation error report
  /ars-disclosure        sonnet  venue status bundle / policy-anchor render
  /ars-mark-read         sonnet  Record human-read signal for one or more citation keys
  /ars-unmark-read       sonnet  Rescind a prior human-read mark for one or more citation keys
  /ars-cache-invalidate  sonnet  Drop cached verification rows for one or more citation keys

Plugin agents (3, v3.6.7-hardened, model: inherit, tools allowlist: Read/Write/Edit/Grep/Glob per #514) — dispatched by ARS pipeline:
  synthesis_agent             Cross-source integration, contradiction resolution, gap analysis
  research_architect_agent    Methodology blueprint (paradigm, method, data strategy)
  report_compiler_agent       APA 7.0 report drafting (Phase 4 + Phase 6)

Other ARS agents (bibliography_agent, literature_strategist_agent, field_analyst_agent, etc.) remain in-skill prompt templates loaded via SKILL.md, not plugin agents.

Token budget reference: docs/PERFORMANCE.md (a single full pipeline run ≈ \$4–6, order-of-magnitude; measured on Opus 4.x)."
    ;;
esac

# Mode commands are manual entry points; announce the actual Skill-tool
# targets too, including after compaction, so the list above does not send
# automatic routing into a disable-model-invocation command (#857).
ROUTING="ARS routing: the mode slash commands above are for the user to type. For a matching natural-language request, invoke the core Skill before answering: academic-research-skills:academic-paper for paper planning, writing, revision, reviewer-response coaching, rebuttal audit, abstracts, literature reviews, format conversion, citation checks, and AI disclosure; academic-research-skills:academic-paper-reviewer for simulated peer review; academic-research-skills:deep-research for research and three-way scans; academic-research-skills:academic-pipeline for the full research-to-finalize pipeline. Pass the requested mode and user request as arguments, then read the selected mode's supporting prompt files from the loaded skill directory. Requests outside academic research and writing do not invoke ARS."
ANNOUNCE+=$'\n\n'"${ROUTING}"

# ---------------------------------------------------------------------------
# #892 routing core, read at runtime from its single source (see that file for
# why every SessionStart source carries it). A missing or unreadable file
# degrades to no block: the announce must never break. After compaction,
# resume, or a fork the lead-in limits it to a new request, so a run under way
# is not routed again.
# ---------------------------------------------------------------------------
# Builtins only (no dirname or sed), so the core survives a minimal PATH; a
# trailing CR is dropped, so a CRLF checkout yields the same block.
_ARS_DIR="${BASH_SOURCE[0]%/*}"
if [[ "${_ARS_DIR}" == "${BASH_SOURCE[0]}" ]]; then _ARS_DIR="."; fi
_CORE_FILE="${_ARS_DIR}/../shared/references/routing_core.md"
# Print the lines between the markers; fail when the end marker is missing.
read_routing_core() {
  local line="" inside=0
  while IFS= read -r line || [[ -n "${line}" ]]; do
    line="${line%$'\r'}"
    if [[ "${line}" == "<!-- routing-core:end -->" && ${inside} -eq 1 ]]; then
      return 0
    elif [[ ${inside} -eq 1 ]]; then
      printf '%s\n' "${line}"
    elif [[ "${line}" == "<!-- routing-core:begin -->" ]]; then
      inside=1
    fi
  done < "$1"
  return 1
}
ROUTING_CORE=$(LC_ALL=C; read_routing_core "${_CORE_FILE}" 2>/dev/null) || ROUTING_CORE=""
if [[ -n "${ROUTING_CORE}" ]]; then
  case "${SOURCE}" in
    compact|resume|fork)
      LEAD="ARS routing discipline, for a new natural-language request: apply it before invoking an ARS skill or dispatching an ARS agent. Messages inside a workflow already under way go to that workflow's active skill and are not routed again."
      ;;
    *)
      LEAD="ARS routing discipline: apply it before invoking an ARS skill or dispatching an ARS agent for a natural-language request."
      ;;
  esac
  ANNOUNCE+=$'\n\n'"${LEAD}"$'\n\n'"${ROUTING_CORE}"
fi

# ---------------------------------------------------------------------------
# Emit the JSON. We assemble it with a here-doc and a sentinel substitution
# rather than printf/jq to keep the output stable across Bash patch versions.
# additionalContext must be a JSON string — escape backslashes, double quotes,
# newlines.
# ---------------------------------------------------------------------------
escape_json() {
  local raw="$1"
  raw="${raw//\\/\\\\}"
  raw="${raw//\"/\\\"}"
  raw="${raw//$'\n'/\\n}"
  raw="${raw//$'\r'/}"
  # Defense-in-depth (belt-and-suspenders): the #544 checker's strict, bounded
  # version grammar already blocks control bytes upstream, but strip any
  # remaining raw C0 control bytes (0x01-0x1f) here too so nothing can corrupt
  # the JSON envelope. Real newlines were already converted to the literal
  # two-char `\n` above (bytes 0x5C 0x6E), so this drops only stray control
  # bytes, never legitimate text — and never the reminder's `\n\n` separator.
  #
  # `tr` is POSIX but not guaranteed on a constrained PATH (e.g. PATH=/bin on
  # macOS, where tr lives in /usr/bin): guard on `command -v tr` so the strip
  # is skipped when tr is absent rather than blowing up the whole pipeline and
  # returning an empty additionalContext (P2-b). Skipping is safe — this pass
  # is defense-in-depth on top of the upstream grammar, not the sole barrier.
  if command -v tr >/dev/null 2>&1; then
    raw="$(printf '%s' "${raw}" | LC_ALL=C tr -d '\001-\037')"
  fi
  printf '%s' "${raw}"
}

# C locale, for correctness and speed. In a locale such as Big5 or Shift_JIS a
# backslash byte can be the second byte of a character, and the substitutions
# above would leave it unescaped. The characters escaped here never occur
# inside a UTF-8 sequence, so UTF-8 text escapes to the same bytes, and bash
# 3.2 runs ${var//a/b} far faster on it in the C locale.
ESCAPED=$(LC_ALL=C; escape_json "${ANNOUNCE}")

cat <<JSON
{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"${ESCAPED}"}}
JSON

exit 0
