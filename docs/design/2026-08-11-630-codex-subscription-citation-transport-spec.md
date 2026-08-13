# #630 Codex subscription citation-transport specification

Status: frozen for implementation
Issue: #630
Source implementation: PR #567 by `dcs-scd`
Date: 2026-08-11

## 1. Scope

This change adds one opt-in transport:

```text
ARS_CROSS_MODEL_TRANSPORT=codex
```

It is legal only for the one-reference-at-a-time citation-integrity call in
`shared/cross_model_verification.md`. It is not a transport for Devil's
Advocate work, reviewer seats, re-review judging, blind checkpoints, manuscript
review, or any other cross-model call. Unset behavior remains byte-equivalent to
the existing API-key routes. An invalid selector fails visibly and never falls
back to another transport.

This specification reuses the subscription-transport idea and probe evidence
from PR #567. It excludes that PR's model promotion, bakeoff artifacts, personal
operator notes, and default-model changes. The implementation commit carries the
original contributor as a co-author.

## 2. Why `codex exec --json` is insufficient

The PR #567 adapter treated a completed `web_search` item plus URLs in the final
message as grounding. That does not bind those URLs to the results the model
actually saw. A model can perform an unrelated search and repeat a URL from its
prompt or memory.

Codex's exec JSONL projection currently drops the structured search results.
The app-server v2 `webSearch` item retains the opaque `results[]` returned by
standalone search. Therefore this transport uses app-server v2 and accepts a
positive source only when the exact normalized HTTPS URL is present in one
completed search item's `results[]`. Every receipt records the search item id,
result index, and canonical result digest that supplied the URL.

## 3. Closed input and output

Input is one JSON object on stdin conforming to:

- `shared/contracts/cross_model/codex_citation_request.schema.json`

The caller supplies only a request id, one reference string, and the bounded
citation context. It cannot supply a prompt, filesystem path, tool instruction,
URL allowlist, output template, or model response.

Successful transport execution emits one canonical JSON line conforming to:

- `shared/contracts/cross_model/codex_citation_receipt.schema.json`

The receipt contains the selected model, exact request/event digests, accepted
search queries, and exact search-result bindings. Raw model text and raw search
results are not emitted. Transport/auth/configuration failures are fail-visible
non-zero exits; a completed but ungrounded or malformed model run becomes the
closed `NOT_SEARCHED` receipt and never an agreement.

## 4. Authentication and selector contract

`detect` and `verify` share one implementation. They resolve the auth root as
`$CODEX_HOME` when set, otherwise `$HOME/.codex`. Availability requires all of:

1. selector exactly `codex`;
2. `ARS_CROSS_MODEL` is a bounded `gpt-*` id;
3. Codex CLI version is at least the version pinned by the runtime;
4. `codex login status` exits zero and its normalized output is exactly
   `Logged in using ChatGPT`;
5. the selected auth root has a regular, bounded `auth.json`.

`Logged in using an API key`, access-token authentication, missing auth, a
symlinked auth file, malformed status output, missing CLI, and old CLI versions
are unavailable. No token, auth JSON, or credential-bearing environment value
is printed. `OPENAI_API_KEY`, `CODEX_ACCESS_TOKEN`, and other provider keys are
removed from the child environment.

Selector states are closed:

- unset or `api`: Codex subscription transport is not selected;
- `codex`: run the checks above;
- any other value: configuration error, with no silent API fallback.

## 5. Minimum-privilege boundary

The runtime creates a mode-0700 temporary root. It copies only the bounded
subscription `auth.json`, mode 0600, into an otherwise empty temporary
`CODEX_HOME`; user config, rules, skills, plugins, MCP definitions, memories,
and session state are not copied. `HOME`, `TMPDIR`, and cwd point into the same
temporary root. The app-server thread is ephemeral, read-only, approval-never,
and has empty environments, dynamic tools, capability roots, and runtime roots.

The app-server is launched with shell/unified exec, file/image, browser,
computer-use, apps, plugins, skills, multi-agent, hooks, goals, workspace
dependencies, and related local capability features disabled. Standalone live
web search is the only enabled task capability.

The parser also treats containment as an output invariant. Any completed item
for command execution, file change, MCP/app call, image/file viewing,
collaboration/subagent activity, or another unapproved tool makes the entire run
`NOT_SEARCHED` with `FORBIDDEN_TOOL_EVENT`. Static flags and the event witness
are both required; neither substitutes for the other.

## 6. Grounding and verdict rules

The model receives a fixed citation-verification prompt and a closed output
schema. It cannot receive caller-authored instructions.

Accepted search evidence requires:

1. a completed `webSearch` item with a non-empty query and `results[]`;
2. at least one search query bound to the reference by either an exact DOI-like
   token or at least two normalized significant reference tokens;
3. for `VERIFIED` and `MISMATCH`, at least one HTTPS source URL;
4. every returned source URL exactly matches a URL extracted from a structured
   result under a closed URL-key vocabulary;
5. the final answer is exactly one `final_answer` agent message whose JSON
   conforms to the closed model-output schema.

`NOT_FOUND` needs a reference-bound search but no source URL. A model-returned
`NOT_SEARCHED` remains `NOT_SEARCHED`. Missing search, malformed events, wrong
item shapes, duplicate ids, multiple final answers, multiple verdict payloads,
unbound URLs, and a positive without sources all fail closed.

Ordering is significant: only completed search items before the accepted final
answer can support it. Result URLs are canonicalized without following redirects
or making a second network request. Exact search-result membership is the
grounding witness; host-side URL availability is not substituted for it.

## 7. Resource and process limits

- request JSON: 32 KiB;
- event stream: 8 MiB and 20,000 messages;
- one reference and one Codex turn per process;
- reference/context: 8 KiB each after UTF-8 decoding;
- model detail: 2 KiB;
- sources: at most 16;
- search items: at most 32;
- search results per item: at most 128;
- app-server deadline: bounded by the runtime constant;
- post-terminal drain: after the target `turn/completed`, close app-server stdin
  and require clean parent exit and stdout/stderr EOF by
  `min(global deadline, terminal observation time + drain grace)`;
- stdout: exactly one receipt line on success.

Any cap breach fails closed. The app-server process group is terminated on
timeout or protocol failure. Every stdout line received before EOF, including a
post-terminal line, remains subject to the same JSON, byte, message, item, tool,
and grounding rules. Drain timeout, nonzero parent exit, malformed late output,
reader failure, and stderr overflow are fail-visible transport errors. Final
process-group cleanup still reaps the parent and descendants. No fixed sleep or
quiet-period inference substitutes for EOF. Temporary auth and event data are
removed by the temporary-directory lifecycle.

## 8. Shell portability and live smoke

`scripts/cross_model_codex_verify.sh` and
`scripts/cross_model_smoke_test_codex.sh` use stock macOS Bash 3.2 syntax: no
arrays, `mapfile`, associative arrays, `[[ =~ ]]`, or GNU-only flags. Parsing,
auth detection, containment, and JSON-RPC live in the stdlib-only Python runtime.

The smoke test is manual and live. CI must never run it. It uses the same
`detect` and `verify` commands as production, so a custom `CODEX_HOME` cannot
pass one path and fail the other. The smoke fixture is public bibliographic
metadata and is not user manuscript content.

## 9. Test and CI contract

Hermetic tests use a fake Codex executable/app-server. They cover:

- unset, `api`, `codex`, and invalid selectors;
- custom `CODEX_HOME` in detection and verification;
- ChatGPT versus API-key auth status without credential output;
- exact child environment and disabled-capability arguments;
- grounded positive, grounded mismatch, grounded negative, and model
  `NOT_SEARCHED`;
- malformed JSONL/RPC, missing search, wrong item/result shapes, duplicate ids,
  multiple final answers/verdicts, positive without a bound source, unrelated
  search, forbidden tool events, transport failure, timeout, and size caps;
- deterministic stdin-EOF-triggered late events, bounded post-terminal hangs,
  nonzero exit, malformed late output, stderr overflow, and late byte/message
  cap breaches;
- request/receipt Draft 2020-12 metaschema and positive/negative payloads;
- Bash 3.2 syntax and no live network/model/API calls in tests.

The runtime tests and an integration mutation guard are registered in the
unified pytest manifest. Spec consistency invokes the integration guard
directly. The guard pins citation-only scope, app-server result binding,
minimum-privilege flags, auth attestation, closed selectors, manifests, docs,
and absence of model-promotion changes.

## 10. Non-goals

No model promotion, recommended-default change, live bakeoff, subscription-cost
claim, automatic consent, arbitrary prompt transport, arbitrary local-file read,
general reviewer/DA/judge transport, hidden fallback, or weakening of the
existing single-model degradation policy.
