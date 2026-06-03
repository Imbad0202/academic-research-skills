# Cross-Model Verification Protocol (v3.0)

## Overview

This protocol enables optional cross-model verification for high-stakes AI judgments. When enabled, a second AI model independently reviews outputs from the primary model, reducing shared-bias blind spots.

**This is entirely optional.** All ARS skills work with Claude Opus 4.7 alone. Cross-model verification is an additional layer for users who want higher confidence in integrity checks, devil's advocate challenges, and review judgments.

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
| Claude Opus 4.7 | `claude-opus-4-7` | Anthropic | Primary model (default for all ARS skills) |
| GPT-5.4 Pro | `gpt-5.4-pro` | OpenAI | Cross-verification — strongest reasoning |
| GPT-5.4 | `gpt-5.4` | OpenAI | Cross-verification — balanced cost/performance |
| Gemini 3.1 Pro | `gemini-3.1-pro-preview` | Google | Cross-verification — strong at factual verification |

**Recommended cross-verification pair:** Claude Opus 4.7 (primary) + GPT-5.4 Pro or Gemini 3.1 Pro (verifier).

Using two non-Anthropic models as primary+verifier is possible but not tested with ARS prompts.

## Setup Guide

### Prerequisites

You need API keys from at least one additional provider. ARS itself runs inside Claude Code, so Claude is always available as the primary model.

### Step 1: Get API Keys

**OpenAI (GPT-5.4):**
1. Go to [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Create a new API key
3. Copy the key (starts with `sk-`)

**Google (Gemini 3.1 Pro):**
1. Go to [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
2. Create a new API key
3. Copy the key (starts with `AIza`)

### Step 2: Set Environment Variables

Add to your shell profile (`~/.zshrc` or `~/.bashrc`):

```bash
# Optional: Cross-model verification for ARS
export OPENAI_API_KEY="<your-openai-api-key>"
export GOOGLE_AI_API_KEY="<your-google-ai-api-key>"

# Choose your preferred cross-verification model
# Options: gpt-5.4-pro, gpt-5.4, gemini-3.1-pro-preview
export ARS_CROSS_MODEL="gpt-5.4-pro"
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
export ARS_CROSS_MODEL="gpt-5.4-pro"

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
3. Batch up to 5 references per API call to reduce latency (e.g., 15 sampled refs = 3 API calls). For each batch, construct a verification prompt:
   ```
   Verify each of these academic references independently. For each,
   check: Does it exist? Are the author names, year, title, journal,
   and DOI correct? Search the web to confirm.

   For each reference, respond with: VERIFIED / NOT_FOUND / MISMATCH (with details)

   Reference 1: [full reference text] — Context: [sentence where cited]
   Reference 2: [full reference text] — Context: [sentence where cited]
   ... (up to 5 per batch)
   ```
4. Send to the cross-model via the appropriate API (see API Call Patterns below)
5. Compare results: if Claude said VERIFIED but cross-model said NOT_FOUND or MISMATCH, flag as `[CROSS-MODEL-DISAGREEMENT]`
6. Include disagreements in the integrity report under a new section:
   ```markdown
   ### Cross-Model Verification Results
   - References sampled: X/Y (Z%)
   - Agreements: N
   - Disagreements: M (listed below, prioritized for human review)

   | # | Reference | Claude | Cross-Model | Status |
   |---|-----------|--------|-------------|--------|
   ```

### Devil's Advocate (deep-research + academic-paper-reviewer)

**When `ARS_CROSS_MODEL` is set:**
- After the DA completes its standard review/checkpoint, the cross-model receives the same material and generates an independent critique
- The DA then compares: any CRITICAL or MAJOR issues found by the cross-model but not by the DA are added as `[CROSS-MODEL-FINDING]`
- This directly addresses frame-lock — a different model may attack from a different angle

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

### OpenAI (GPT-5.4 / GPT-5.4 Pro)

In Claude Code, the agent can use the Bash tool to make API calls:

```bash
curl -s https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "'"$ARS_CROSS_MODEL"'",
    "messages": [
      {"role": "system", "content": "You are a verification assistant."},
      {"role": "user", "content": "'"$(echo "$PROMPT" | jq -Rs .)"'"}
    ],
    "temperature": 0.1,
    "max_tokens": 2000
  }' | jq -r '.choices[0].message.content'
```

### Google Gemini (Gemini 3.1 Pro)

```bash
# PROMPT must be set before calling. Use jq to JSON-escape it.
curl -s "https://generativelanguage.googleapis.com/v1beta/models/${ARS_CROSS_MODEL}:generateContent?key=$GOOGLE_AI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{"parts": [{"text": "'"$(echo "$PROMPT" | jq -Rs .)"'"}]}],
    "generationConfig": {"temperature": 0.1, "maxOutputTokens": 2000}
  }' | jq -r '.candidates[0].content.parts[0].text'
```

### Detecting Available Models

Agents should check at the start of a verification/review session:

```bash
# Check which cross-model APIs are available
# Requires: jq (for JSON parsing). Fallback: python3 -c "import sys,json; ..."
if ! command -v jq &>/dev/null; then
  echo "WARNING: jq not installed. Cross-model API calls will use python3 fallback."
fi

if [ -n "$ARS_CROSS_MODEL" ]; then
  case "$ARS_CROSS_MODEL" in
    gpt-5.4*) 
      [ -n "$OPENAI_API_KEY" ] && echo "CROSS_MODEL_AVAILABLE=openai" \
        || echo "WARNING: ARS_CROSS_MODEL=$ARS_CROSS_MODEL but OPENAI_API_KEY is not set" ;;
    gemini*) 
      [ -n "$GOOGLE_AI_API_KEY" ] && echo "CROSS_MODEL_AVAILABLE=google" \
        || echo "WARNING: ARS_CROSS_MODEL=$ARS_CROSS_MODEL but GOOGLE_AI_API_KEY is not set" ;;
    *) echo "WARNING: ARS_CROSS_MODEL=$ARS_CROSS_MODEL is not a supported model. Supported: gpt-5.4, gpt-5.4-pro, gemini-3.1-pro-preview"
       echo "CROSS_MODEL_AVAILABLE=none" ;;
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
| Integrity verification (30% of 60 refs, batched 5/call) | ~4 calls | ~$0.30-0.60 |
| DA cross-check (1 per checkpoint, 3 checkpoints) | 3 calls | ~$0.30-0.50 |
| Peer review (planned, not yet implemented) | — | — |
| **Full pipeline** | **~7 calls** | **~$0.60-1.10** |

These are rough estimates based on GPT-5.4 Pro pricing ($5/1M input, $20/1M output) and typical prompt sizes.

## Limitations

1. **Does not solve frame-lock fully.** All major LLMs share substantial training data. Cross-model catches different surface errors but may share deep structural biases.
2. **API latency.** Cross-model calls add 2-5 seconds per call. For integrity verification of 18 references, this adds ~1-2 minutes.
3. **Response format differences.** Different models structure responses differently. The agent must parse varied formats — keep verification prompts simple and structured to minimize parsing issues.
4. **Cost scales with paper size.** Longer papers with more references = more cross-model calls.

## Graceful Degradation

If cross-model verification fails (API error, rate limit, key expired):
- Log the failure: `[CROSS-MODEL-ERROR: reason]`
- Continue with single-model verification — never block the pipeline on cross-model failure
- Include a note in the report: "Cross-model verification was configured but unavailable for this run. Results are single-model only."
