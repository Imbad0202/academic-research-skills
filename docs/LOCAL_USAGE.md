# Local usage — the Codex-subscription cross-model verifier

This is a **personal fork** of [Academic Research Skills](https://github.com/Imbad0202/academic-research-skills)
(upstream author: Cheng-I Wu, CC-BY-NC 4.0). It is not maintained for anyone else, and nothing here is
proposed upstream.

It adds exactly one thing: the opt-in cross-model verifier can run through a **Codex CLI
subscription** instead of a metered `OPENAI_API_KEY`. That verifier is the only part of the ARS
research pipeline that calls a non-Anthropic LLM — everything else runs on your inherited Claude Code
session model, and the bibliographic indexes (Semantic Scholar / OpenAlex / Crossref / arXiv) are free
or key-optional. So routing this one surface onto a subscription you already pay for takes the
pipeline's marginal per-token cost to zero.

Upstream behavior is untouched. The OpenAI, Gemini, and OpenAI-compatible routes work exactly as they
always did; this transport only fires when you explicitly ask for it.

---

## TL;DR

```bash
export ARS_CROSS_MODEL_TRANSPORT="codex"   # opt in to the subscription transport
export ARS_CROSS_MODEL="gpt-5.5"           # any gpt-* id. OPENAI_API_KEY stays UNSET.

# prove it end-to-end before trusting it (one real subscription call, ~40s)
bash scripts/cross_model_smoke_test_codex.sh

claude                                     # cross-verification activates automatically
```

---

## Prerequisites

| Need | Check | If missing |
|---|---|---|
| `codex` on PATH | `command -v codex` | install the Codex CLI |
| Logged-in subscription | `test -f ~/.codex/auth.json && echo ok` | `codex login` |
| `jq` | `command -v jq` | `apt install jq` — the adapter hard-requires it |
| `bash` | — | the adapter uses `mapfile`, so bash 4+, not `sh` |

**Keep auth at the default `~/.codex/`.** `CODEX_HOME` is only half-honored — the smoke test checks
`${CODEX_HOME:-$HOME/.codex}/auth.json`, but the detection block hardcodes `$HOME/.codex/auth.json`.
Relocate `CODEX_HOME` and you get the worst possible combination: a *passing* smoke test and a
transport that detection reports as unavailable, i.e. verification silently off behind a green gate.
See Known gaps.

**`OPENAI_API_KEY` is never read.** The adapter runs `codex` under `env -u OPENAI_API_KEY`, so a key in
your environment is stripped rather than used — leaving one set does not break this transport and does
not get you billed. It matters only for routing: had you *not* set `ARS_CROSS_MODEL_TRANSPORT=codex`, a
present key would have sent the same `gpt-*` id down the metered OpenAI route instead. Worth knowing
which one you're actually on.

---

## Setup

Three environment variables, all opt-in:

```bash
# REQUIRED — selects this transport. Without it, a gpt-* id takes the metered OpenAI route.
export ARS_CROSS_MODEL_TRANSPORT="codex"

# REQUIRED — the verifier model. Any gpt-* id.
export ARS_CROSS_MODEL="gpt-5.5"

# OPTIONAL — defaults to xhigh on this transport (note: NOT the provider default).
# gpt-5.6-sol accepts none|low|medium|high|xhigh|max; gpt-5.5 tops out at xhigh.
export ARS_CROSS_MODEL_REASONING_EFFORT="high"
```

The effort default is the one place this transport deliberately differs from upstream: the OpenAI
route leaves effort unset (provider default), while the Codex adapter defaults to `xhigh`. Verification
is the one job where you want the model working hard, and on a subscription the extra reasoning is not
separately billed.

### How routing is decided

`shared/cross_model_verification.md` (§ Detecting Available Models) resolves the transport at session
start. For a `gpt-*` id:

```
ARS_CROSS_MODEL_TRANSPORT=codex ?
  ├─ yes → codex on PATH AND ~/.codex/auth.json present ?
  │         ├─ yes → CROSS_MODEL_AVAILABLE=codex
  │         └─ no  → WARNING + proceed SINGLE-MODEL (never silently metered)
  └─ no  → OPENAI_API_KEY set ? → CROSS_MODEL_AVAILABLE=openai : WARNING + single-model
```

The failure mode is deliberate: a set-but-unusable transport **degrades to single-model with a
warning**. It never silently falls back to a metered key, and it never silently drops verification
without telling you.

---

## Verify it works

```bash
ARS_CROSS_MODEL=gpt-5.5 bash scripts/cross_model_smoke_test_codex.sh
```

This makes **one real subscription call** against a known-good reference (Vaswani et al. 2017) and
asserts five things: the adapter exits 0, emits exactly one normalized verdict JSON object, reports a
completed web-search event, yields exactly one whole-word verdict token, and — since the fixture is
real — returns `VERIFIED` carrying ≥1 source URL. Exit 0 and `RESULT: PASS` means the whole chain is
live: auth, model id, hosted search, grounding guard, verdict extraction.

Run it whenever you change model id, change transport, or suspect the subscription lapsed. It is the
entry gate for this transport — the counterpart of upstream's `cross_model_smoke_test.sh`, which
cannot run here because it requires `OPENAI_API_KEY`.

---

## What the verifier actually does

One reference per call. `scripts/cross_model_codex_verify.sh` takes the prompt as its single argument
and emits one line of JSON:

```json
{"verdict": "VERIFIED", "sources": ["https://..."], "searched": true}
```

| Verdict | Meaning |
|---|---|
| `VERIFIED` | Found online. Carries ≥1 source URL — enforced, not requested. |
| `MISMATCH` | Found, but a field is wrong. |
| `NOT_FOUND` | Searched; no matching record exists. |
| `NOT_SEARCHED` | No grounded search backed this answer. **Never counts as evidence.** |

### The grounding guard fails closed

This is the load-bearing part. A verifier that answers citation questions from memory is worse than no
verifier — it launders a hallucination into a confirmation. So the adapter treats a run as grounded
**only** when the Codex JSONL stream carries a completed `web_search` item (`type:"item.completed"`
with `item.type:"web_search"`). Everything else collapses to `NOT_SEARCHED`:

- No completed web-search event → `NOT_SEARCHED`, sources dropped.
- Zero or ≥2 verdict tokens in the reply → `NOT_SEARCHED` (ambiguity is not a verdict).
- `VERIFIED` with no extractable URL → downgraded to `NOT_SEARCHED`.
- Non-zero `codex` exit → `NOT_SEARCHED` + the exit status propagates, so a transport failure is
  reported as a transport failure and never relabeled as a completed-but-ungrounded lookup.

Each call runs in a throwaway `mktemp -d` directory with `--ephemeral --ignore-user-config
--ignore-rules --skip-git-repo-check -s read-only`, so your Codex config, project rules, and repo
never leak into a verification prompt. The temp dir is removed on exit.

### Exit codes

| Code | Cause |
|---|---|
| 0 | Completed (verdict may still be `NOT_SEARCHED`) |
| 2 | Wrong arg count, or `ARS_CROSS_MODEL` unset |
| 127 | `codex` or `jq` missing |
| *codex's own* | Transport failure — auth, rate limit, CLI error |

---

## Choosing the model

| ID | Status | Notes |
|---|---|---|
| `gpt-5.5` | validated | **Recommended default.** |
| `gpt-5.5-pro` | validated | Strongest 5.5 reasoning; ~6× cost on the metered route (moot on a subscription). |
| `gpt-5.6-sol` | validated 2026-07-16 | Frontier tier. Passed the promotion bakeoff — see below. |
| `gemini-3.1-pro-preview` | validated | Google route; **not** available on this transport. |

Any `gpt-*` id works on this transport; unlisted ones warn and run anyway (the Codex API rejects a
genuinely unknown id with HTTP 400).

**`gpt-5.6-sol` is validated but is not the default, and that is deliberate.** Validation means
non-inferiority — it earns trust, nothing more. Flipping the recommended default is a separate
promotion requiring its own argument, and the bakeoff numbers don't support one: the candidate's only
edge was 0/20 vs 1/20 false disagreements, a one-reference difference at Fisher exact p = 1.0, while
grounding, recall, and guard stability were all ceiling ties. Use `gpt-5.5` unless you have your own
reason not to.

---

## Cost

Upstream estimates ~$0.60–1.10 per full pipeline in metered cross-model API cost. On this transport
that becomes **subscription quota instead of per-token billing** — the marginal dollar cost of a
verification run is zero, and the real constraint is your Codex rate limits.

Two practical consequences:

- **`xhigh` effort is nearly free here**, which is why it's the default.
- **Latency, not money, is the budget.** Measured p95 was ~119–132s per reference call. The bakeoff's
  180 calls at concurrency 6 took roughly half an hour.

---

## Reproducing the bakeoff

The `gpt-5.6-sol` promotion (issue #518) is fully reproducible offline — the probe set, the harness,
and the raw 180-call record are all committed:

```bash
cd evals/bakeoff/cross_model_promotion
sha256sum probe_set_v2.json                          # must be cb7ac8df...
python3 score_bakeoff.py --run full_run_v2.jsonl     # offline, instant, no API calls
```

That re-derives every number in
`audits/cross-model-promotion-bakeoff-gpt-5.6-sol-2026-07-16.md`: 100% grounded search for both
models, 100% recall on the 10 fabricated references, 0% vs 5% false disagreement, zero guard misfires,
p95 131.5s against a 237.8s ceiling — all five thresholds pass.

To re-run the live calls instead (~30 min of subscription quota), see the audit's § Reproduction. A
fresh run tests *today's* models; it does not re-verify the 2026-07-16 report.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `ERROR: ARS_CROSS_MODEL is not set` (exit 2) | Adapter called without a model | `export ARS_CROSS_MODEL=gpt-5.5` |
| `ERROR: codex is required` / `jq is required` (exit 127) | Missing binary | Install it |
| `ERROR: Codex subscription auth.json is not present` | Not logged in | `codex login` |
| `WARNING: ...transport=codex but the Codex CLI subscription is unavailable...proceeding single-model` | `codex` or `auth.json` missing at session start | Fix the prereq — **verification is currently OFF** |
| Everything returns `NOT_SEARCHED` | Hosted web search never ran | Run the smoke test; if it fails at the web-search check, the subscription/tooling is the problem, not the model |
| `this smoke test covers the Codex gpt-* route only` | `ARS_CROSS_MODEL` isn't a `gpt-*` id | Gemini has no Codex route — use the Google route |

A `NOT_SEARCHED` storm is the signal worth taking seriously: the guard is doing its job and telling you
the answers were ungrounded. Treat it as verification being unavailable, not as references failing.

---

## Known gaps

Verified limits, not speculation:

1. **Two upstream smoke-test checks have no counterpart here.** `codex exec --json` emits only
   `thread.started`, `turn.started`, `item.completed`, `turn.completed` — none carrying a model or
   effort field. So the OpenAI gate's model-echo and effort-echo assertions are *uncoverable* on this
   transport: nothing in the output proves which model answered. The smoke test covers the other four
   checks.
2. **`service_tier=priority` is best-effort.** The adapter requests it; Codex never echoes it, so it's
   unverifiable from output.
3. **Codex runtime behavior is a residual.** `--ignore-user-config --ignore-rules --skip-git-repo-check`
   plus an isolated non-git dir remove *your* configured inputs, but `codex exec` has no switch to
   disable its built-in runtime behavior entirely.
4. **The `unlisted`/`provisional` announce notes point at the wrong smoke test.** They tell you to run
   `scripts/cross_model_smoke_test.sh`, which needs `OPENAI_API_KEY` and therefore cannot run on this
   transport; the Codex counterpart is `cross_model_smoke_test_codex.sh`. This is upstream code left
   deliberately unmodified — it only fires for unlisted ids, and no id is provisional today.
5. **`CODEX_HOME` is honored inconsistently.** The smoke test reads `${CODEX_HOME:-$HOME/.codex}`;
   the detection block reads `$HOME/.codex` unconditionally. A relocated `CODEX_HOME` therefore passes
   the gate and fails detection — verification off, gate green. Both surfaces are local to this fork, so
   the fix is a one-liner (`[ -f "${CODEX_HOME:-$HOME/.codex}/auth.json" ]` in the detection block);
   it is left unmade here because this pass documents rather than changes behavior. Until then: keep
   auth at the default path.
6. **The bakeoff's n=20 real references can't price rare failure modes.** One baseline miss
   (`easy-09` — `gpt-5.5` returned `NOT_FOUND` 3/3 on a verified-real JACS paper that `gpt-5.6-sol`
   found every time) is a real, replicated divergence, but 20 references cannot tell you how often that
   happens.

---

## Repo hygiene

**`origin` is upstream, not yours.** This trips people up:

```
origin   https://github.com/imbad0202/academic-research-skills.git   # UPSTREAM — read-only, never push
fork     git@github.com:dcs-scd/academic-research-skills.git         # yours
```

Push to `fork`, never `origin`:

```bash
git push fork codex-subscription-verifier
```

Local work lives on the `codex-subscription-verifier` branch (`d2a9c76` transport → `569cc22` bakeoff
→ `4ccf5ea` validated flip). `implementation-notes.html` is intentionally untracked — it's a working
journal, not a deliverable.

### Gates

Docs and specs are cross-pinned by lint, so edits break loudly rather than drifting:

```bash
python3 scripts/check_setup_cross_model_parity.py      # SETUP.md <-> SETUP.zh-TW.md <-> model tables
python3 scripts/check_cross_model_verification_sync.py # spec <-> consumers
python3 scripts/check_version_consistency.py
```

`check_setup_cross_model_parity.py` is the one that bites: it pins the `ARS_CROSS_MODEL` examples in
both SETUP files to each other *and* to the canonical model table's API-ID column. Edit the English
setup example without the Traditional Chinese one and CI fails.
