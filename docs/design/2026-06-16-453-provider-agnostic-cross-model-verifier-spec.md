# Provider-agnostic cross-model verifier (PR #453 reframe)

**Issue/PR:** reworks external PR #453 (`kzccIneko:feat/openai-compatible-cross-model`)
**Date:** 2026-06-16
**File touched:** `shared/cross_model_verification.md` + `scripts/check_cross_model_verification_sync.py` + `scripts/test_check_cross_model_verification_sync.py`
**Status:** design approved, pre-implementation

## Problem

The cross-model verification layer hardcodes the verifier endpoint to `api.openai.com`, and the model-detection `case` statement only recognises `gpt-5.*` / `gemini-*`. Researchers without an OpenAI account but with access to an OpenAI-Chat-Completions-compatible provider (Xiaomi MiMo, DeepSeek, or a self-hosted endpoint) cannot use the cross-model layer at all. The intent is legitimate: make the verifier **provider-agnostic** for any endpoint speaking the OpenAI Chat Completions protocol.

The contributor's PR delivers this intent but, read as **actual diff** (not PR prose), introduces three real defects confirmed by an independent codex review (REWORK verdict):

- **P1 — laundering:** the compatible path emits the model's raw `VERIFIED` text with no grounding trace and no downgrade, so an ungrounded from-memory verdict can be counted as an agreement in the integrity results table. This violates the protocol's load-bearing invariant (grounding evidence, not prompt wording, is the safety boundary).
- **P1 — passive downgrade:** the detection logic routes any model id to `openai_compatible` whenever the **standard SDK env var** `OPENAI_BASE_URL` is set. Existing GPT users who set `OPENAI_BASE_URL` for an Azure/proxy/local route get silently downgraded from grounded first-party OpenAI to ungrounded Chat Completions. Behaviour changes for users who never opted in.
- **P2 cluster:** documented endpoints build to `…/v1/v1/chat/completions` (double `/v1`); the setup guide exports `OPENAI_API_KEY` twice and leaves a misleading `gpt-5.5`; the compatible prompt collapses `NOT_SEARCHED` into `NOT_FOUND`; the Integrity section and the new compatible section contradict each other on the guard.

## Security invariant (must hold after this change)

A cross-model `VERIFIED` verdict counts as agreement **only** when backed by API-level grounding evidence (OpenAI `web_search_call` / Gemini `groundingMetadata`). Compatible providers have no hosted web-search tool, so they can never produce that evidence. Therefore: **compatible-provider verdicts are never counted as grounded agreement in citation verification.** The line is drawn on the "needs grounding?" axis, not the "is it compatible?" axis — so a compatible provider is a first-class verifier for tasks that don't need grounding (Devil's Advocate critique) and a non-confirming voice for tasks that do (citation existence).

## Design

### D1 — Explicit opt-in via `ARS_OPENAI_COMPAT_BASE_URL`

A dedicated, ARS-namespaced env var both signals opt-in and supplies the endpoint:

- `ARS_OPENAI_COMPAT_BASE_URL` **set** → use the compatible Chat Completions path against that base URL, for the model named in `ARS_CROSS_MODEL`.
- `ARS_OPENAI_COMPAT_BASE_URL` **unset** → behaviour is byte-equivalent to pre-PR: `gpt-5.*` → grounded OpenAI, `gemini-*` → grounded Gemini, anything else → `none` with a warning.
- The standard `OPENAI_BASE_URL` is **never** read by the detection or call logic. Removing the PR's passive `OPENAI_BASE_URL`-triggered downgrade is the fix for the P1 passive-downgrade defect.

Detection `case` after change:

- `gpt-5.5*|gpt-5.4*` → `openai` (key check unchanged).
- `gemini*` → `google` (key check unchanged).
- `*)` catch-all → if `ARS_OPENAI_COMPAT_BASE_URL` is set **and** `OPENAI_API_KEY` is set → `openai_compatible`; else warn + `none`. **No `OPENAI_BASE_URL` branch.**
- The `mimo*|deepseek*` prefixes from the PR are dropped as load-bearing routing — they're documented as *examples* of compatible model ids, but routing is governed solely by `ARS_OPENAI_COMPAT_BASE_URL` (so "any self-hosted OpenAI-compatible endpoint", the broadest case the contributor wanted, works without a prefix allowlist to maintain).

### D2 — Compatible verdicts are always ungrounded in citation verification

When `CROSS_MODEL_AVAILABLE=openai_compatible`, the citation-verification call:

- builds the endpoint as `endpoint="${ARS_OPENAI_COMPAT_BASE_URL%/}/chat/completions"` (base URL is the API root including `/v1`; trailing slash normalised — fixes double-`/v1`).
- on transport failure (non-2xx / curl 000) → `CROSS-MODEL-ERROR: openai_compatible_http_<code>` (unchanged contract: transport error ≠ NOT_SEARCHED).
- on success → the verdict is **emitted as `NOT_SEARCHED`** (with the model's text preserved as context), never as a bare `VERIFIED`. There is no grounding trace to check, so the protocol's existing rule applies verbatim: `NOT_SEARCHED` never counts as agreement, is counted separately, and is surfaced for re-run/human review.
- The system prompt for this path preserves the full verdict taxonomy (no `NOT_SEARCHED`→`NOT_FOUND` collapse), but the **handler downgrades the result to `NOT_SEARCHED` regardless** of the model's self-reported verdict, because the provider structurally cannot evidence a lookup.

This is the minimal change that holds the invariant: it reuses the existing `NOT_SEARCHED` channel rather than inventing a new status, and a compatible provider still appears in the results table (the user sees what the second model said) without being laundered into a confirmation.

### D3 — Task scope: citation downgraded, DA equivalent, peer-review untouched

- **Citation existence verification** (Stage 2.5/4.5): compatible → `NOT_SEARCHED` per D2.
- **Devil's Advocate critique** (deep-research + academic-paper-reviewer): finding weaknesses needs no web grounding, so compatible is a **first-class verifier here** — its findings are used like GPT/Gemini findings. The DA section already routes through the shared "API Call Patterns"; no DA agent file hardcodes an endpoint (verified by grep), so no agent file changes.
- **Peer-review sixth reviewer:** remains `Planned, not yet implemented`. Out of scope for this change.

### D4 — Setup guide: mutually exclusive provider blocks

Replace the single copy-paste block (which exports `OPENAI_API_KEY` twice and leaves a misleading `gpt-5.5`) with three mutually exclusive examples, each a complete self-consistent tuple:

- **OpenAI (first-party, grounded):** `OPENAI_API_KEY` + `ARS_CROSS_MODEL=gpt-5.5`.
- **Gemini (first-party, grounded):** `GOOGLE_AI_API_KEY` + `ARS_CROSS_MODEL=gemini-3.1-pro-preview`.
- **OpenAI-compatible (ungrounded):** `OPENAI_API_KEY` (the provider's key) + `ARS_OPENAI_COMPAT_BASE_URL=https://api.deepseek.com/v1` (or MiMo / self-hosted) + `ARS_CROSS_MODEL=<provider model id>`, with a one-line note that this path is ungrounded and does not produce citation-agreement confirmations.

The Supported Models table keeps the compatible row but states the ungrounded boundary in the table itself (not only in a footnote that the Integrity section can contradict).

### D5 — Lint coverage + mutation tests

`check_cross_model_verification_sync.py` does not byte-pin the bash block, so it caught none of the PR's defects. Extend it (and its mutation test) to pin three new contracts:

1. **Compatible downgrade present:** the compatible provider block must contain `NOT_SEARCHED` (it cannot drop the downgrade).
2. **No passive base-url downgrade:** the detection `case` must not route to `openai_compatible` off `OPENAI_BASE_URL`; assert `OPENAI_BASE_URL` does not appear in the detection/call executable bash at all (reverse assertion).
3. **Endpoint normalised:** the compatible endpoint is constructed with `%/` trailing-slash trimming and does not contain a literal double-`/v1` (`/v1/v1`) or a hardcoded `api.openai.com` fallback.

Mutation discipline (per prior linter-mutation lessons): commit working tree before mutating; align mutation string case with the lint's matching (avoid IGNORECASE false-greens); each new check gets a red-then-green mutation proving it actually fails when the contract is broken.

## Out of scope

- Peer-review sixth reviewer (stays planned).
- Any new status enum beyond the existing `NOT_SEARCHED` (decision A in brainstorm: reuse, don't invent).
- DA agent file edits (no hardcoded endpoint exists; grep-verified).
- Grounding for compatible providers (structurally impossible; not a goal).

## Adoption

Local rebuild (not fetch+cherry-pick of the fork) per repo fork-PR discipline: a single commit on a feature branch off `main`, carrying `Co-Authored-By: kzccIneko`. Then a courteous PR reply crediting the contributor and stating the provider-agnostic intent was adopted with a grounding-aware reshaping — without dissecting their diff line by line.

## Files

| File | Change |
|------|--------|
| `shared/cross_model_verification.md` | D1 detection rewrite, D2 compatible call path, D3 task-scope wording, D4 setup guide, D-contradiction cleanup |
| `scripts/check_cross_model_verification_sync.py` | D5 three new contract checks |
| `scripts/test_check_cross_model_verification_sync.py` | D5 mutation tests for the three new checks |
