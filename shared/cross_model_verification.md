# Cross-Model Verification Protocol (v3.0)

## Overview

This protocol enables optional cross-model verification for high-stakes AI judgments. When enabled, a second AI model independently reviews outputs from the primary model, reducing shared-bias blind spots.

**This is entirely optional.** All ARS skills work with the primary Claude model alone. Cross-model verification is an additional layer for users who want higher confidence in integrity checks, devil's advocate challenges, and review judgments.

**Consent boundary:** Before unpublished manuscripts, private notes, corpus text,
reviewer comments, decision letters, response letters, or other review material
is sent to an external provider, the agent must identify the provider, model,
and content class that would be sent, then obtain explicit user consent. An
environment variable alone is not consent to upload user content. If consent is
not granted, continue with single-model verification.

## Why Cross-Model Verification

A stress test of 68 AI-generated citations found 31% had problems — and all passed three rounds of same-model integrity checks. The root cause: the verifying AI and the generating AI share the same training data distribution, so they share the same blind spots. A different model (trained on overlapping but not identical data, with different RLHF tuning) can catch errors that the primary model systematically misses.

**What it improves:** Error rate reduction (estimated 31% → ~5-10%). Different models catch different types of hallucination patterns.

**What it doesn't solve:** Frame-lock (all LLMs share most training data), sycophancy (all RLHF models have this tendency). These are degree improvements, not kind improvements.

## Supported Models

| Model | API ID | Provider | Best For |
|-------|--------|----------|----------|
| Claude (session model) | _(inherited Claude Code session model — e.g., Fable 5)_ | Anthropic | Primary model (default for all ARS skills) |
| GPT-5.5 | `gpt-5.5` | OpenAI | Cross-verification — recommended balance (supports `xhigh` reasoning) |
| GPT-5.5 Pro | `gpt-5.5-pro` | OpenAI | Cross-verification — strongest reasoning (premium pricing: ~6× GPT-5.5) |
| Gemini 3.1 Pro | `gemini-3.1-pro-preview` | Google | Cross-verification — strong at factual verification |

### OpenAI-compatible providers (Chat Completions API — UNGROUNDED, opt-in)

| Provider | Example API ID(s) | Endpoint (`ARS_OPENAI_COMPAT_BASE_URL`) | Notes |
|----------|-------------------|------------------------------------------|-------|
| Xiaomi MiMo | `mimo-v2.5-pro` | `https://token-plan-cn.xiaomimimo.com/v1` | Set `ARS_OPENAI_COMPAT_API_KEY` + `ARS_CROSS_MODEL`. Ungrounded: positive verdicts never count as citation agreement. |
| DeepSeek | `deepseek-v4-pro` | `https://api.deepseek.com/v1` | Set `ARS_OPENAI_COMPAT_API_KEY` + `ARS_CROSS_MODEL`. Ungrounded. |
| Any OpenAI-compatible | any non-`gpt-*`/`gemini-*` id | any `/v1/chat/completions` endpoint | Routing is governed solely by `ARS_OPENAI_COMPAT_BASE_URL`; the model id must NOT match a first-party prefix or it takes the grounded first-party route instead. |

> **Compatible providers are ungrounded.** They expose no hosted web-search tool, so there is no grounding evidence behind a verdict. A positive `VERIFIED` is downgraded to `NOT_SEARCHED` and never counts as agreement in citation verification; a `NOT_FOUND`/`MISMATCH` survives as a disagreement. They ARE first-class for Devil's Advocate critique (which needs no grounding) — but a DA finding from any provider is an adversarial hypothesis, not standalone evidence, unless independently sourced.

**Recommended cross-verification pair:** the inherited Claude session model (primary) + GPT-5.5 or Gemini 3.1 Pro (verifier).

> The primary row deliberately names no version: the primary is always the session model, so the row cannot go stale on the next Anthropic release. Verifier IDs stay concrete because they are literal API strings the user must export. (`gpt-5.4` / `gpt-5.4-pro` remain accepted for existing setups.)

Using two non-Anthropic models as primary+verifier is possible but not tested with ARS prompts.

## Setup Guide

### Prerequisites

You need API keys from at least one additional provider. ARS itself runs inside Claude Code, so Claude is always available as the primary model.

### Step 1: Get API Keys

**OpenAI (GPT-5.5):**
1. Go to [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Create a new API key
3. Copy the key (starts with `sk-`)

**Google (Gemini 3.1 Pro):**
1. Go to [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
2. Create a new API key
3. Copy the key (starts with `AIza`)

**OpenAI-compatible providers (MiMo / DeepSeek / self-hosted):**
1. Get an API key from your provider (e.g. [platform.deepseek.com](https://platform.deepseek.com) or the Xiaomi MiMo platform)
2. Note the provider's API root including `/v1` (e.g. `https://api.deepseek.com/v1`)
3. The key goes in `ARS_OPENAI_COMPAT_API_KEY` and the endpoint in `ARS_OPENAI_COMPAT_BASE_URL` — NOT in `OPENAI_API_KEY`/`OPENAI_BASE_URL` (your real OpenAI key is never sent to a third-party endpoint)
4. The compatible model id (`ARS_CROSS_MODEL`) must NOT begin with a `gpt-` or `gemini-` prefix. Any such id is claimed by the first-party grounded route, so a self-hosted compatible model named that way would be routed to the (unavailable) first-party path instead of your compatible endpoint.

### Step 2: Set Environment Variables

Add to your shell profile (`~/.zshrc` or `~/.bashrc`):

```bash
# Cross-model verification for ARS — pick exactly ONE provider tuple.

# --- Option A: OpenAI (first-party, grounded) ---
export OPENAI_API_KEY="<your-openai-api-key>"
export ARS_CROSS_MODEL="gpt-5.5"

# --- Option B: Google Gemini (first-party, grounded) ---
export GOOGLE_AI_API_KEY="<your-google-ai-api-key>"
export ARS_CROSS_MODEL="gemini-3.1-pro-preview"

# --- Option C: OpenAI-compatible provider (MiMo / DeepSeek / self-hosted) — UNGROUNDED ---
# Uses a DEDICATED key; your real OPENAI_API_KEY is never sent to a third-party endpoint.
export ARS_OPENAI_COMPAT_BASE_URL="https://api.deepseek.com/v1"   # API root incl. /v1
export ARS_OPENAI_COMPAT_API_KEY="<your-provider-api-key>"
export ARS_CROSS_MODEL="deepseek-v4-pro"                          # provider id, NOT gpt-*/gemini-*
```

Then reload: `source ~/.zshrc`

### Step 3: Verify Setup

In Claude Code, you can test by asking:
```
Check if cross-model verification is available for ARS
```

The system will check for the environment variables and report which models are available.

### Step 4: Enable Per-Session (Optional)

If you don't want cross-model verification running all the time, you can enable it per session:

```bash
# Enable for this session only
export ARS_CROSS_MODEL="gpt-5.5"

# Disable for this session
unset ARS_CROSS_MODEL
```

## How It Works in Each Skill

### Integrity Verification (academic-pipeline, Stage 2.5 / 4.5)

**When `ARS_CROSS_MODEL` is set:**
- Primary model (Claude) runs full Phase A-E verification as normal
- After Phase A completes, a random 30% sample of references is sent to the cross-model for independent verification
- Cross-model receives only the reference text and paper context — not Claude's verification result (to prevent anchoring)
- Disagreements are flagged as `[CROSS-MODEL-DISAGREEMENT]` and prioritized for human review

**When `ARS_CROSS_MODEL` is not set:**
- Standard single-model verification (unchanged from v2.7+)

**Implementation for agents:**

When the integrity_verification_agent detects `ARS_CROSS_MODEL` in the environment, it should:

1. Complete Phase A verification normally
2. Select 30% of references randomly (minimum 5, maximum 15). If total references < 5, sample all of them.
3. Issue **one API call per reference** — not a batch. (Batching hides which reference the model actually grounded: a single grounding-metadata trace on a 5-reference response proves *something* was searched, not that *each* reference was. One reference per call makes the grounding evidence 1:1 with the verdict.) For each reference, construct a verification prompt:
   ```
   Verify this academic reference. Check: Does it exist? Are the author
   names, year, title, journal, and DOI correct? Search the web to
   confirm — do not answer from memory.

   Respond with exactly one verdict:
   - VERIFIED  — found online; include at least one source URL or DOI you found
   - MISMATCH  — found, but a field is wrong (state which); include the source
   - NOT_FOUND — searched, no matching record exists
   - NOT_SEARCHED — you could not actually search the web for this reference

   Reference: [full reference text] — Context: [sentence where cited]
   ```
   A `VERIFIED` verdict with no accompanying source URL/DOI is treated as `NOT_SEARCHED` (the model claimed a result it cannot evidence).
4. Send to the cross-model via the appropriate API (see API Call Patterns below). **For first-party providers the call patterns enable the hosted web-search/grounding tool and reject the response as `NOT_SEARCHED` when the API returns no grounding evidence** — a model that ignores the "search the web" instruction cannot fake an absent grounding trace, so this is the real safety boundary, not the prompt wording. **An OpenAI-compatible provider has no grounding tool, so its positive verdicts are downgraded to `NOT_SEARCHED` by the handler (rejections pass through); a compatible provider therefore never contributes a grounded agreement.**
5. Compare results: if Claude said VERIFIED but cross-model said NOT_FOUND or MISMATCH, flag as `[CROSS-MODEL-DISAGREEMENT]`. Treat `NOT_SEARCHED` / ungrounded exactly as **not verified** — it never counts as agreement with a Claude `VERIFIED`, and a sample that returns `NOT_SEARCHED` is surfaced for re-run or human review, never silently passed.
6. Include disagreements in the integrity report under a new section:
   ```markdown
   ### Cross-Model Verification Results
   - References sampled: X/Y (Z%)
   - Agreements: N
   - Disagreements: M (listed below, prioritized for human review)
   - Ungrounded (NOT_SEARCHED): U (the cross-model could not actually search — these are NOT confirmations; re-run or human-review)

   | # | Reference | Claude | Cross-Model | Source (URL/DOI) | Status |
   |---|-----------|--------|-------------|------------------|--------|
   ```
   The `Source` column carries the URL/DOI the cross-model returned for a `VERIFIED` row; a blank source on a `VERIFIED` verdict downgrades it to `NOT_SEARCHED`.

### Devil's Advocate (deep-research + academic-paper-reviewer)

**When `ARS_CROSS_MODEL` is set:**
- After the DA completes its standard review/checkpoint, the cross-model receives the same material and generates an independent critique
- The DA then compares: any CRITICAL or MAJOR issues found by the cross-model but not by the DA are added as `[CROSS-MODEL-FINDING]`
- This directly addresses frame-lock — a different model may attack from a different angle

> A compatible (ungrounded) provider is first-class for DA critique — surfacing weaknesses and attack angles needs no web grounding. But "first-class" is scoped to critique, not factual adjudication: a DA finding from any provider is an adversarial hypothesis, never standalone evidence, unless it carries an independently-checkable source. Do not treat a compatible-provider DA "finding" as a verified defect.

**When `ARS_CROSS_MODEL` is not set:**
- Standard single-model DA (unchanged)

**Implementation:**

The DA agent, after completing its checkpoint report, should:

1. Send the reviewed material + a simplified DA prompt to the cross-model:
   ```
   You are a devil's advocate reviewing this [research/paper].
   Find the 3 most serious weaknesses. For each, state:
   - What the weakness is
   - Why it matters
   - What the strongest counter-argument would be

   Material: [the reviewed content]
   ```
2. Compare cross-model findings with own findings
3. Any cross-model finding not already covered → add to report as `[CROSS-MODEL-FINDING]`
4. Log: `[CROSS-MODEL: X findings received, Y novel (not in primary DA report)]`

### Peer Review (academic-paper-reviewer) — Future

> **Status: Planned, not yet implemented.** No agent currently owns the 6th reviewer behavior. This will be added in a future version, likely as a cross-model section in `eic_agent.md`. For now, cross-model verification in peer review is limited to the DA's independent critique (above).

**Planned behavior when `ARS_CROSS_MODEL` is set:**
- Cross-model acts as an additional independent reviewer (6th reviewer)
- Its scores are shown separately, not averaged into the existing 5-reviewer consensus
- Significant score divergence (>15 points on any dimension) is flagged

## API Call Patterns

Three patterns are documented below. The first two (OpenAI and Gemini) are first-party and share the same contract: enable the provider's hosted web-search tool, and **gate the model's text on proof that a search actually happened** — no grounding evidence (an OpenAI `web_search_call` item / a Gemini `groundingMetadata` block) emits `NOT_SEARCHED` and the text is discarded, so this guard, not the prompt wording, is what prevents a from-memory guess being laundered into `VERIFIED`. Both first-party web-search tools are hosted/server-side: one request, no client-side tool-call round-trip. The third (OpenAI-compatible) is ungrounded by construction: it has no web-search tool, so the handler downgrades positive verdicts to `NOT_SEARCHED` and lets rejections through, and a compatible verdict never counts as a grounded agreement. `PROMPT` holds the single-reference verification prompt from step 3.

### OpenAI (GPT-5.5 / GPT-5.5 Pro)

Use the **Responses API** (`/v1/responses`) — the hosted `web_search` tool lives there. (Chat Completions does not take `tools: [{type: "web_search"}]`; web search on that endpoint requires the separate `gpt-5-search-api` model, so this example targets Responses to stay model-agnostic across `gpt-5.5` / `gpt-5.5-pro` / the legacy `gpt-5.4*` ids.)

```bash
# PROMPT holds the single-reference verification prompt (step 3). One reference per call.
resp="$(curl -sS -w '\n%{http_code}' https://api.openai.com/v1/responses \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg model "$ARS_CROSS_MODEL" --arg prompt "$PROMPT" '{
    model: $model,
    instructions: "You are a citation-verification assistant. Search the web before every verdict; never answer from memory. If you could not search, respond NOT_SEARCHED.",
    input: $prompt,
    tools: [{type: "web_search"}],
    temperature: 0.1
  }')")"

http="${resp##*$'\n'}"; body="${resp%$'\n'*}"
# The grounding guard and source extraction are kept as canonical jq filters under
# scripts/cross_model_verification/ so they are behavior-tested in CI (a from-memory verdict, a
# malformed grounding index, etc.) and cannot silently stop failing closed. Reference them via
# `jq -f` rather than inlining, so the doc and the test share one definition.
GUARD=scripts/cross_model_verification
if [ "$http" -lt 200 ] || [ "$http" -ge 300 ]; then
  # Transport/API failure (401/429/5xx, or curl's 000 on a network error) — NOT the same as
  # "searched but found nothing". Surface as a transport error so the consumer falls back to
  # single-model (see § Graceful Degradation); never relabel it NOT_SEARCHED, which would
  # imply a completed-but-ungrounded lookup.
  echo "CROSS-MODEL-ERROR: openai_http_$http"
elif ! jq -e -f "$GUARD/openai_has_completed_web_search.jq" <<<"$body" >/dev/null; then
  echo "NOT_SEARCHED: no_web_search_call"           # no search happened at all — discard the text
else
  # A completed web_search_call proves *a* search ran, not that THIS reference's verdict
  # is supported by it. Emit the verdict text together with the url_citation annotations the
  # model attached; step 5 downgrades a VERIFIED with no citation to NOT_SEARCHED.
  text="$(jq -r -f "$GUARD/openai_text.jq" <<<"$body")"
  cites="$(jq -r -f "$GUARD/openai_sources.jq" <<<"$body")"
  printf '%s\nSOURCES: %s\n' "$text" "${cites:-(none)}"
fi
```

### Google Gemini (Gemini 3.1 Pro)

The hosted grounding tool is `google_search` (REST uses snake_case; the JS SDK's `googleSearch` is the same tool). A grounded response carries `candidates[].groundingMetadata`; its absence means the model did not search.

```bash
# PROMPT holds the single-reference verification prompt (step 3). One reference per call.
resp="$(curl -sS -w '\n%{http_code}' \
  "https://generativelanguage.googleapis.com/v1beta/models/${ARS_CROSS_MODEL}:generateContent?key=$GOOGLE_AI_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg prompt "$PROMPT" '{
    contents: [{parts: [{text: $prompt}]}],
    tools: [{google_search: {}}],
    generationConfig: {temperature: 0.1}
  }')")"

http="${resp##*$'\n'}"; body="${resp%$'\n'*}"
# Grounding guard + source extraction are canonical jq filters under scripts/cross_model_verification/
# (same rationale as the OpenAI block: behavior-tested, referenced via `jq -f`). The guard is
# rederived from the source extractor: it passes iff the SAME extraction the source filter performs
# yields at least one url AND the model issued a search (a non-empty webSearchQueries). So
# guard-pass ⟹ a source is extractable — a groundingSupports linking to no valid chunk
# (empty/negative/string/out-of-range/fractional index), the wrong candidate, or a non-string uri
# all leave the extraction blank and fail the guard closed. See the .jq file headers for the full
# contract.
GUARD=scripts/cross_model_verification
if [ "$http" -lt 200 ] || [ "$http" -ge 300 ]; then
  # Transport/API failure (401/429/5xx, or curl's 000) — surface as a transport error so the
  # consumer falls back to single-model (see § Graceful Degradation), not NOT_SEARCHED.
  echo "CROSS-MODEL-ERROR: gemini_http_$http"
elif ! jq -e -f "$GUARD/gemini_is_grounded.jq" <<<"$body" >/dev/null; then
  echo "NOT_SEARCHED: no_grounding_support"           # no search, or text not supported by it — discard
else
  text="$(jq -r '.candidates[0].content.parts[]?.text // empty' <<<"$body")"
  cites="$(jq -r -f "$GUARD/gemini_sources.jq" <<<"$body")"
  printf '%s\nSOURCES: %s\n' "$text" "${cites:-(none)}"
fi
```

> **Why `temperature: 0.1`:** reference existence/metadata checking is a deterministic factual task, so low temperature reduces run-to-run variance in the verdict. It is not a grounding control — the grounding guard above is what enforces an actual lookup.

### OpenAI-Compatible API (MiMo, DeepSeek, self-hosted) — ungrounded

When `CROSS_MODEL_AVAILABLE=openai_compatible`, use the **Chat Completions API** at
`ARS_OPENAI_COMPAT_BASE_URL`, authenticated with the dedicated `ARS_OPENAI_COMPAT_API_KEY`.
These providers expose no hosted web-search tool, so there is **no grounding guard**. The
handler therefore normalizes the verdict by invoking the canonical
`normalize_compat_verdict.py` unit, which emits a single-line JSON object
(`{"status","provider","context"}`): a positive `VERIFIED` is downgraded to `NOT_SEARCHED` (an
ungrounded confirmation can never count as a grounded agreement), while a genuine rejection
(`NOT_FOUND` / `MISMATCH`) passes through as a useful disagreement. The consumer reads `.status`
only; the raw model text is JSON-escaped into `.context` as human-readable context and is
**never** placed in a verdict slot the agreement counter parses — embedded newlines become
literal `\n` inside the string, so a model response cannot inject a second status line. `PROMPT`
holds the single-reference verification prompt from step 3.

```bash
# ARS_OPENAI_COMPAT_BASE_URL is the API root INCLUDING /v1 (e.g. https://api.deepseek.com/v1).
# Trailing slash is normalized so the endpoint is built exactly once — no double /v1.
endpoint="${ARS_OPENAI_COMPAT_BASE_URL%/}/chat/completions"
GUARD=scripts/cross_model_verification

resp="$(curl -sS -w '\n%{http_code}' "$endpoint" \
  -H "Authorization: Bearer $ARS_OPENAI_COMPAT_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg model "$ARS_CROSS_MODEL" --arg prompt "$PROMPT" '{
    model: $model,
    messages: [
      {role: "system", content: "You are a citation-verification assistant. If you did not actually perform an external lookup, respond NOT_SEARCHED. Use NOT_FOUND only if you are confident no such record exists; MISMATCH if a field is wrong; VERIFIED only with a source URL/DOI."},
      {role: "user", content: $prompt}
    ],
    temperature: 0.1
  }')")"

http="${resp##*$'\n'}"; body="${resp%$'\n'*}"
if [ "$http" -lt 200 ] || [ "$http" -ge 300 ]; then
  # Transport/API failure (401/429/5xx, or curl's 000) — distinct from NOT_SEARCHED, so the
  # consumer falls back to single-model (see § Graceful Degradation), never an ungrounded verdict.
  echo "CROSS-MODEL-ERROR: openai_compatible_http_$http"
else
  text="$(jq -r '.choices[0].message.content // empty' <<<"$body")"
  if [ -z "$text" ]; then
    echo "CROSS-MODEL-ERROR: openai_compatible_empty_response"
  else
    # Canonical normalization lives in scripts/cross_model_verification/normalize_compat_verdict.py
    # (behavior-tested in scripts/test_normalize_compat_verdict.py) and is INVOKED here rather than
    # re-implemented in bash — the same canonical-and-referenced pattern the first-party blocks use
    # with `jq -f`. It emits ONE line of JSON: {"status","provider","context"}. The consumer reads
    # .status only; raw model text is JSON-escaped in .context so it can never inject a second
    # status line (the producer/consumer anti-laundering contract holds at the output-format level).
    #   VERIFIED            -> status NOT_SEARCHED  (ungrounded positive can never agree)
    #   NOT_FOUND/MISMATCH  -> status passes through (useful disagreement)
    #   anything else/empty -> status NOT_SEARCHED  (fail closed)
    printf '%s' "$text" | python3 "$GUARD/normalize_compat_verdict.py"
  fi
fi
```

> **No grounding guard for compatible providers.** The grounding guard (an API-level
> `web_search_call` / `groundingMetadata` trace) exists only for first-party OpenAI and
> Gemini. A compatible provider cannot evidence a lookup, so its positive verdicts are
> downgraded to `NOT_SEARCHED` and never count as agreement. Its rejections survive as
> disagreements. The block emits a single-line JSON object (`{"status","provider","context"}`)
> from `normalize_compat_verdict.py`, and the grounded-agreement count is computed solely from
> its `.status` field — never from the raw text, which lives JSON-escaped in `.context`.
> For the OpenAI-compatible block, read the verdict from the JSON `.status` field only
> (e.g. `jq -r .status`); never grep the emitted line or `.context` for a verdict token — the
> raw model text is preserved JSON-escaped in `.context` precisely so it cannot be mistaken for
> a verdict.

### Detecting Available Models

Agents should check at the start of a verification/review session:

```bash
# Check which cross-model APIs are available
# Requires: jq (for JSON parsing). Fallback: python3 -c "import sys,json; ..."
if ! command -v jq &>/dev/null; then
  echo "WARNING: jq not installed. Cross-model API calls will use python3 fallback."
fi

if [ -n "$ARS_CROSS_MODEL" ]; then
  # PRECEDENCE: a first-party model id ALWAYS takes the grounded route, even if
  # ARS_OPENAI_COMPAT_BASE_URL is set. This prevents a grounded->ungrounded downgrade. ANY gpt-*
  # id (not just today's gpt-5.5/gpt-5.4) and any gemini-* id route grounded, so a future
  # first-party release keeps the grounded path instead of silently falling through to the
  # ungrounded compatible branch. The compatible path is reachable only for a model id that
  # matches no first-party prefix, and only when its dedicated opt-in env vars are both present.
  # OPENAI_BASE_URL is never read.
  case "$ARS_CROSS_MODEL" in
    gpt-*)
      [ -n "$OPENAI_API_KEY" ] && echo "CROSS_MODEL_AVAILABLE=openai" \
        || echo "WARNING: ARS_CROSS_MODEL=$ARS_CROSS_MODEL but OPENAI_API_KEY is not set" ;;
    gemini*)
      [ -n "$GOOGLE_AI_API_KEY" ] && echo "CROSS_MODEL_AVAILABLE=google" \
        || echo "WARNING: ARS_CROSS_MODEL=$ARS_CROSS_MODEL but GOOGLE_AI_API_KEY is not set" ;;
    *)
      # Unrecognized id: only an explicit, credential-isolated opt-in enables the ungrounded
      # OpenAI-compatible path. Both the base URL AND the dedicated key are required; the
      # standard OPENAI_API_KEY is NEVER sent to a third-party endpoint (see Credential
      # isolation in the API Call Patterns section).
      if [ -n "$ARS_OPENAI_COMPAT_BASE_URL" ] && [ -n "$ARS_OPENAI_COMPAT_API_KEY" ]; then
        echo "CROSS_MODEL_AVAILABLE=openai_compatible"
      elif [ -n "$ARS_OPENAI_COMPAT_BASE_URL" ]; then
        echo "WARNING: ARS_OPENAI_COMPAT_BASE_URL is set but ARS_OPENAI_COMPAT_API_KEY is not — refusing to send another provider's key. Set ARS_OPENAI_COMPAT_API_KEY."
        echo "CROSS_MODEL_AVAILABLE=none"
      else
        echo "WARNING: ARS_CROSS_MODEL=$ARS_CROSS_MODEL is not a recognized model. First-party grounded route: any gpt-* id (e.g. gpt-5.5, gpt-5.5-pro, legacy gpt-5.4*) or gemini-* id (e.g. gemini-3.1-pro-preview). For an OpenAI-compatible provider set ARS_OPENAI_COMPAT_BASE_URL + ARS_OPENAI_COMPAT_API_KEY and use that provider's model id (must not match a gpt-*/gemini-* prefix, or it takes the grounded first-party route instead)."
        echo "CROSS_MODEL_AVAILABLE=none"
      fi ;;
  esac
else
  echo "CROSS_MODEL_AVAILABLE=none"
fi
```

If `ARS_CROSS_MODEL` is set but the corresponding API key is missing or the model name is unsupported, the agent should warn the user and proceed with single-model verification.

## Cost Considerations

Cross-model verification adds API costs from the second provider:

| Scenario | Additional Calls | Estimated Additional Cost |
|----------|-----------------|--------------------------|
| Integrity verification (60 refs → 30% = 18, capped at max 15; **one call per reference**) | ~15 calls | ~$1.20-2.60 |
| DA cross-check (1 per checkpoint, 3 checkpoints) | 3 calls | ~$0.30-0.55 |
| Peer review (planned, not yet implemented) | — | — |
| **Full pipeline** | **~18 calls** | **~$1.50-3.15** |

These are rough estimates based on GPT-5.5 pricing ($5/1M input, $30/1M output) and typical prompt sizes; GPT-5.5 Pro runs ~6× higher ($30/1M input, $180/1M output). One-call-per-reference (rather than batching) is a deliberate cost-for-provenance trade: it is the only way the grounding-evidence check maps 1:1 to each verdict. Web-search-tool calls also cost more than plain completions.

## Limitations

1. **Does not solve frame-lock fully.** All major LLMs share substantial training data. Cross-model catches different surface errors but may share deep structural biases.
2. **API latency.** Cross-model calls add 2-5 seconds per call, plus web-search round-trip time. With one call per reference (no batching) and a web-search tool, integrity verification of up to 15 sampled references (the sample cap) adds several minutes; the calls can be issued concurrently to bound wall-clock time.
3. **Response format differences.** Different models structure responses differently. The agent must parse varied formats — keep verification prompts simple and structured to minimize parsing issues.
4. **Cost scales with paper size.** Longer papers with more references = more cross-model calls.

## Graceful Degradation

If cross-model verification fails **at the transport level** (API error, rate limit, key expired):
- Log the failure: `[CROSS-MODEL-ERROR: reason]`
- Continue with single-model verification — never block the pipeline on cross-model failure
- Include a note in the report: "Cross-model verification was configured but unavailable for this run. Results are single-model only."

A `NOT_SEARCHED` result is **not** a transport failure and is handled differently. It means the call succeeded but the model could not (or did not) ground the lookup, so its verdict carries no evidence. Do not fall back to single-model and do not treat it as agreement: record the reference as `NOT_SEARCHED` in the results table, count it separately from agreements/disagreements, and surface it for re-run or human review. The distinction matters — a transport failure means "we have no cross-model opinion"; a `NOT_SEARCHED` means "the cross-model gave an opinion we have decided not to trust as a confirmation."
