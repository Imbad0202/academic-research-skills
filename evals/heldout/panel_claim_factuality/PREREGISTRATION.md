# Eval preregistration: panel claim factuality (#1002)

Frozen with `plan.json`, `rubric.md`, `prompts/`, `scripts/extract_panel_claims.py`,
and `scripts/dispatch_panel_claim_audit.py` in one commit, before any judge call
on a claim. A change to any of them after that call is a new plan
version, logged as an amendment; the frozen files are never edited in place.

## Bars

- contrast_detection: per judge, at least 0.95 of the false contrast sentences are judged `false` by both replicates. A miss, or a missing verdict on any contrast sentence, voids that judge's claim verdicts.
- contrast_false_flag: per judge, at most 0.05 of the accurate contrast sentences are judged `false` by either replicate. A miss voids that judge's claim verdicts.
- With one valid judge the run is exploratory (per-judge counts only, no decision); with none it is void.
- false_claim_rate: adjudicated false claims divided by all 805 claims, overall and by seat. At least 0.03, with both judges past the contrast gate, means plan the second part of #1002 (a check between the panel and the synthesizer).
- panels_with_false_claim: the share of the 17 panels with at least one adjudicated false claim. At least 0.30, with both judges past the contrast gate, also means plan the second part. Below both decision bars, the second part is not planned on this evidence.

## Arms

Each arm is a judge, a generator, or a verifier, not a treatment. Every call runs through a subscription CLI, so no call carries a per-call charge; settled cost is `unknown` and the binding limits are the subscription usage limits and time.

- judge `gpt-6-astra` (OpenAI family): `codex exec`, model_reasoning_effort=xhigh, read-only, empty working directory, prompt on stdin. Price-table estimate at 10/50 USD per MTok: about 0.14 USD per item at 4,000 in and 2,000 out tokens; a batch is about 7,000 in tokens.
- judge `gemini-4-argon-high` (Google family): `agy -p`, model "Gemini 4 Argon (High)", empty working directory. No price-table row (`EVAL_PRICE_MISSING`); its cost is recorded as `unknown`.
- generator `claude-opus-5-5-high` (Anthropic family): `agy -p`, model "Claude Opus 5.5 (High)", 20 contrast pairs per manuscript, 3 calls.
- verifier `gpt-6-astra`: the codex settings above, one call per manuscript over its mechanically valid pairs.
- Each judge reads each batch twice (two replicates, each a fresh session). A first-attempt prompt is at most 27,500 UTF-8 bytes and a retry at most 28,000, the same batches for both judges.

## Decoys

- False contrast sentences: up to 20 per manuscript (60 in all), each written by the generator from one explicit manuscript statement, changed in one to four tokens so that the manuscript contradicts it. They enter the batches as ordinary items with neutral ids, so the judge cannot tell them from real claims by id or position. A judge must rate at least 0.95 of them `false` in both replicates; a pass shows that the judge, with this prompt and these batches, finds a contradiction that the manuscript states.
- Accurate contrast sentences: the matched accurate twin of each false sentence, in a different batch from its twin. A judge must rate at most 0.05 of them `false` in either replicate; a pass shows that the judge does not call supported text false.
- A pair enters only when it passes the four mechanical checks in `scripts/dispatch_panel_claim_audit.py` (one sentence each, 8 to 50 whitespace-delimited words, one to four changed tokens, a verbatim evidence quote) and the verifier answers all seven questions in `prompts/contrast_verify.md` with true. Fewer than 15 accepted pairs for a manuscript stops the run.
- Limit: a contrast sentence is one plain sentence, while a real claim is a paragraph, so the decoys test contradiction-finding, not the full reading of a long claim. The verifier is the same model as one judge, so the accepted pairs can favour what that model finds; the second judge is the cross-check.

## Stop rules

- A judge that misses either contrast bar is void; when both judges miss, the measurement is void and no claim rate is published.
- A claim inventory other than 17 bundles and 805 claims, or any extraction problem: stop before any judge call.
- Fewer than 15 or more than 20 accepted contrast pairs for any manuscript, a repeated pair or sentence, or a pair with any check not true: stop before any judge call on claims.
- A batch whose output cannot be read after its one retry: stop the run.
- A transport failure (nonzero exit, empty output, usage limit, authentication failure): stop the run without a retry. No replacement model or transport without a new plan version.
- An interrupted call, or any input changed since the build: stop.
- `budget_exhausted` on the spend ledger: stop.
- The full run starts only after the maintainer approves the pilot projection.

## Held-out exposure

| set | prior exposure | reservation |
|---|---|---|
| `reviewer_seeded_defects/manuscripts/` (3 synthetic manuscripts) | Subject sessions of the E4 runs (claude-opus-4-8, claude-opus-5), which read them as the reviewed paper; possible earlier cross-model review rounds of pull requests that changed them (not recorded per model) | The generator, the verifier, and both judges read each manuscript in full. The run adds exposure to gpt-6-astra, gemini-4-argon-high, and claude-opus-5-5-high. |
| `reviewer_seeded_defects/manifests/` (held-out ground truth) | Maintainer only | Never read, sent, or summarized by this run or by its planner. No script of this suite opens the directory. |
| `reviewer_seeded_defects/runs/raw/` (17 score-eligible panel bundles) | Committed E4 records | Read by `scripts/extract_panel_claims.py`; the judges see the extracted claim text without the seat. While building the extractor, the planner (claude-opus-5-5) read the heading structure of the bundles and part of one Domain and one Devil's Advocate Phase 2 report of `2026-08-05-ms01_quant-baseline-r3`; it read no manuscript and no manifest, and the prompts contain no manuscript-specific text. |

The 17 bundles reviewed the current manuscript files: `ms01_quant_defective.md` last changed on 2026-08-03 (#625), and every score-eligible `ms01_quant` bundle is dated 2026-08-04 or later; the other two manuscripts are unchanged since 2026-07-24.
