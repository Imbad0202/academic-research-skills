# Promotion Bakeoff — `gpt-5.6-sol` provisional → validated (issue #518)

**Date:** 2026-07-16 (all 180 calls same-day, per the paired-run requirement)
**Scope:** the § Promotion Bakeoff defined in `shared/cross_model_verification.md`, run against
the candidate id `gpt-5.6-sol` with `gpt-5.5` as baseline.
**Deliverables:** `evals/bakeoff/cross_model_promotion/probe_set_v2.json` (the pinned probe set), this report.
**Provenance chain:** #515 → #516 (`gpt-5.6-sol` added as provisional) → #518 → #519 (§ Promotion Bakeoff
+ `CROSS_MODEL_ID_STATUS` allowlist) → this run.

**Probe-set hash (spec §519 requirement):**
`sha256 = cb7ac8dfc0db9513be716b0b2ab37f0d977ad424ee8c5c62758c57db8271c7be` (`fixture_version 2.0.0`)

## Verdict

| promotion | outcome |
|---|---|
| `provisional` → `validated` | **ELIGIBLE** — all five non-inferiority thresholds pass |
| recommended default (`gpt-5.5` → `gpt-5.6-sol`) | **NO** — not argued; see Finding 3 |

Per spec §529 the two promotions are separate, and a bare non-inferiority pass never flips the
default. This report argues the first and explicitly declines the second.

## Method

- **Transport:** every call went through the shipped adapter `scripts/cross_model_codex_verify.sh`
  (not a reimplementation), driven by the Codex subscription — `OPENAI_API_KEY` **unset** for the
  whole run, verified at launch. Codex CLI 0.144.1.
- **Prompt:** the canonical verification prompt from `shared/cross_model_verification.md`
  (four-verdict form). The `Context: [sentence where cited]` clause is omitted — see Limitations.
- **Design:** 30 references × 2 models × 3 repeats = **180 calls**, concurrency 6.
  Per-reference verdict = the verdict returned by ≥2 of 3 repeats; a 1–1–1 split is indeterminate
  and scored against the model (a recall miss for measure 2, a false disagreement for measure 3).
  Measure 1 is computed per call.
- **Probe set:** 30 references — 20 real (10 easy DOI-keyed journal articles; 10 hard =
  4 preprints + 3 DOI-less + 3 non-English) + 10 synthetic fabrications. Composition matches §519.
  Reals are sourced from the repo's expert-labeled gold set or live from Crossref; every field was
  re-verified against Crossref/OpenAlex at fixture-build time. Fabrications carry **real venues and
  real registrant DOI prefixes**, each verified non-resolving (Crossref 404), and each invented title
  was checked against Crossref + OpenAlex to confirm it is not an existing paper.
- **Entry gate (§518): PASSES.** `scripts/cross_model_smoke_test_codex.sh` — the Codex-route
  counterpart of the `cross_model_smoke_test.sh` named in §518 — run against the candidate on the run
  date: exit 0, all checks green (adapter exit, verdict-JSON shape, grounding guard, exactly one
  verdict token, `VERIFIED` carries 3 source URLs). Two of the OpenAI gate's six checks have no
  counterpart on this transport; see Finding 7.

## Results

| measure | baseline `gpt-5.5` | candidate `gpt-5.6-sol` | threshold | verdict |
|---|---|---|---|---|
| 1 — grounded-search completion (per call) | 100.0% (90/90) | 100.0% (90/90) | ≥ baseline − 5 pp | **PASS** |
| 2 — citation-mismatch recall (10 fabrications) | 100.0% (10/10) | 100.0% (10/10) | ≥ baseline − 5 pp **and** ≥ 80% abs | **PASS** |
| 3 — false-disagreement rate (20 reals) | 5.0% (1/20) | 0.0% (0/20) | ≤ baseline + 5 pp | **PASS** |
| 4 — jq-guard shape stability | 0 misfires | 0 misfires | zero (hard) | **PASS** |
| 5 — p95 latency | 118.9 s | 131.5 s | ≤ 2× baseline (237.8 s) | **PASS** |

Per-leg majority verdicts (all correct except where noted):

| leg | n | `gpt-5.5` | `gpt-5.6-sol` |
|---|---|---|---|
| easy | 10 | 9 VERIFIED, **1 NOT_FOUND** (`easy-09`) | 10 VERIFIED |
| hard_preprint | 4 | 4 VERIFIED | 4 VERIFIED |
| hard_doi_less | 3 | 3 VERIFIED | 3 VERIFIED |
| hard_non_english | 3 | 3 VERIFIED | 3 VERIFIED |
| fabricated | 10 | 10 NOT_FOUND | 10 NOT_FOUND |

Latency beyond the p95 threshold statistic (n=90 per model):

| | mean | median | p90 | p95 | max |
|---|---|---|---|---|---|
| `gpt-5.5` | 50.7 s | 43.5 s | 92.5 s | 118.9 s | 175.3 s |
| `gpt-5.6-sol` | 55.1 s | 42.5 s | 107.5 s | 131.5 s | 173.9 s |

## Findings

1. **All five thresholds pass; the candidate is eligible for `validated`.** No measure is close to
   its tolerance. This is an unambiguous non-inferiority result.

2. **The baseline has one reproducible failure the candidate does not share — `easy-09`.**
   `gpt-5.5` returned `NOT_FOUND` on 3/3 repeats with `searched=true` and **zero source URLs**;
   `gpt-5.6-sol` returned `VERIFIED` on 3/3 citing the ACS record. The reference is real: Jellen et
   al. (2020), *2D Arrays of Organic Qubit Candidates Embedded into a Pillared-Paddlewheel
   Metal–Organic Framework*, JACS, `10.1021/jacs.0c07251` — every field re-verified against live
   Crossref (issued 2020-09-25, vol 142, pp 18513-18521) after the run. The behavior **replicated
   across two independent runs on two fixture versions (6/6 calls each way)**, so it is a
   deterministic property of the baseline on this reference, not sampling noise. A grounded search
   that returns no sources and concludes `NOT_FOUND` is the exact failure this gate exists to catch —
   it is indistinguishable, from the caller's side, from a correct fabrication flag.

3. **That finding does NOT support flipping the recommended default, and this report does not claim
   it does.** Three reasons, in descending order of force:
   - **The measure-3 difference is not statistically distinguishable.** 1/20 vs 0/20 is Fisher exact
     two-tailed **p = 1.0**. What replicates is the *existence* of a baseline failure mode; its
     *prevalence* in the population of real references is estimated by a single observation and is
     essentially unconstrained at n=20.
   - **§529's "superiority with no inferiority elsewhere" route is not cleanly open.** The candidate
     is nominally behind on raw p95 (131.5 s vs 118.9 s). That gap is itself inside noise — the
     candidate is *faster* at the median (42.5 s vs 43.5 s) and the difference lives entirely in the
     tail — but "not inferior once you discount the tail" is an argument, not a clean sweep.
   - **Measures 1, 2 and 4 are ceiling ties** (100/100, 100/100, 0/0) and discriminate nothing.
   The honest summary: the candidate matches the baseline everywhere the gate can see, and beats it
   on one reference. `gpt-5.5` stays the recommended default.

4. **Both models caught 10/10 fabrications by genuine search, not pattern-matching.** This is a
   fixture-validity result as much as a model result. The fabrications were built specifically to
   defeat the shortcut that makes such sets useless: real venues, real registrant DOI prefixes,
   plausible titles. A micro-pilot confirmed the mechanism — `fab-05` drew `NOT_FOUND` from both
   models *after* a genuine grounded search, not on sight.

5. **Latent instability in the baseline that the majority rule absorbed.** `gpt-5.5` split 2–1 on
   `hard-doiless-03` (VERIFIED, VERIFIED, NOT_FOUND). The majority verdict is correct so it costs the
   baseline nothing under the spec, and it is recorded here only because it is directionally
   consistent with Finding 2. `gpt-5.6-sol` was 3/3 unanimous on all 30 references; `gpt-5.5` was
   unanimous on 29.

6. **Spec defect found by executing the spec: measure 2's ±5 pp tolerance is unexercisable.**
   Measure 2 is computed over **10** fabrications, where the smallest observable non-zero difference
   is **10 pp**. A "≥ baseline − 5 pp" tolerance on a 10-item denominator can therefore never bind:
   the candidate either ties/beats the baseline (passes) or is at least 10 pp worse (fails). The
   stated tolerance collapses to "must be ≥ baseline" and no run can ever exercise the 5 pp band.
   Measure 3 is one reference away from the same problem — at n=20 its ±5 pp tolerance has a
   resolution of **exactly one reference**. This is a defect in #518's numbers, not in the procedure,
   and §532 already anticipates the thresholds being tuned in a future spec. Recommendation: either
   raise the denominators or restate measures 2 and 3 in counts ("no more than k additional misses")
   so the tolerance means what it appears to mean.

7. **The entry gate passes, but two of its six checks are structurally uncoverable on this transport.**
   §518 names `scripts/cross_model_smoke_test.sh` as the entry gate; that script is hard-wired to the
   OpenAI Responses API over `curl` and aborts at `OPENAI_API_KEY is not set`. The Codex route has its
   own counterpart, `scripts/cross_model_smoke_test_codex.sh` (shipped alongside the adapter, and the
   command `docs/SETUP.md` points users at), which **passed against the candidate on the run date**.
   The six checks map as follows:

   | § smoke-test check | status on the Codex route |
   |---|---|
   | 1 — HTTP 2xx (transport) | **covered**: adapter exit code + JSON parse; gate green, and 0/180 nonzero exits, 0/180 unparseable across the bakeoff |
   | 2 — completed `web_search_call` (jq guard) | **covered**: adapter's fail-closed grounding guard; gate green, 180/180 `searched=true` |
   | 3 — exactly one whole-word verdict token | **covered**: adapter's extraction rejects 0 or ≥2 tokens; gate green, no collapses observed |
   | 4 — `VERIFIED` carries ≥1 source | **covered**: adapter downgrades bare `VERIFIED`; gate green (3 URLs), 0/180 `VERIFIED` with zero sources |
   | 5 — response model echo matches requested id | **NOT coverable — no echo exists on this path** (see mitigation) |
   | 6 — reasoning-effort echo | **NOT coverable**. Both arms ran the adapter default (`xhigh`), identically; nothing confirms the server honored it |

   Checks 5 and 6 are not an oversight in the Codex gate — they are unimplementable there. Codex
   `exec --json` emits only `thread.started` / `turn.started` / `item.completed` / `turn.completed`,
   and **none carries a model or effort field** (verified directly). The Codex gate documents the
   effort half of this in its own header.

   **Mitigation for check 5, which guards this study's core assumption** — that the two arms ran
   *different* models, since a silent fallback would make this a comparison of `gpt-5.5` against
   itself. Two independent lines of evidence: (a) `codex exec` **hard-rejects** an unsupported model id
   with HTTP 400 and exit 1 — verified directly against a bogus id — and all 180 calls exited 0, so
   both requested ids were served rather than silently substituted; (b) the arms produce
   deterministically opposite verdicts on `easy-09` (3/3 `NOT_FOUND` vs 3/3 `VERIFIED`), which one
   model answering both arms cannot do. Strong, but it is *inference from behavior*, not the id echo
   the gate asks for. Recommendation: §518 should name the Codex-route gate alongside the API-key one,
   and state that checks 5–6 are transport-limited rather than skipped.

## Probe-set history — v1 superseded, and why

The first full 180-call run (2026-07-16, fixture v1, sha `9138aa16…`) is **superseded and its hash
must not be cited as the gate result**. It is retained locally as a replication of Finding 2 only.

v1 contained a ground-truth error. `hard-nonenglish-02` (Elizondo-Salazar, *Agronomía Mesoamericana*,
`10.15517/am.v13i1.13244`) was rendered with year **2014**, taken from Crossref's `issued` field.
Both models flagged it `MISMATCH` on **6/6 grounded calls**. They were right and the fixture was
wrong: for back-registered legacy content, Crossref `issued` is the **DOI deposit date, not the
publication date** — this journal minted DOIs for its old issues in 2014, so a 2002 article
(vol 13, issue 1) reports `issued: 2014-02-20`. The publisher's own `citation_date` metadata says
2002. v2 pins the year to 2002 via an explicit override carrying the evidence URL in-fixture.

The correction is confirmed by the result: `hard_non_english` went from MISMATCH 6/6 in v1 to
**VERIFIED 3/3 from both models** in v2.

Two notes for whoever builds the next fixture:

- **Crossref `issued` is not a publication date.** It is the earliest date the DOI record carries.
  For any pre-DOI-era or back-registered article, prefer the publisher's `citation_date`, and treat a
  deposit year that post-dates the volume/issue numbering as a red flag.
- **Unanimous cross-model disagreement is evidence against your ground truth, not against the
  models.** That heuristic decided both anomalies here, in opposite directions: `hard-nonenglish-02`
  drew unanimous disagreement from two independent models → the fixture was wrong. `easy-09` drew a
  *split* — one model flagging, the other verifying *with a source* → the model was wrong. Split
  disagreement measures the models; unanimous disagreement impeaches the fixture.

All 180 v2 calls were re-run rather than patching the 6 affected calls and carrying 174 forward, so
that one hash covers the whole gate result with no asterisk.

## Limitations

Stated here rather than buried, because two of them bound what this run can conclude:

1. **The gate is underpowered by construction, and this run cannot fix that.** With 10 fabrications
   and 20 reals, the spec's ±5 pp thresholds sit inside binomial noise (SE ≈ 9.5 pp near p=0.9 at
   n=10; ≈ 4.9 pp at n=20). The run can demonstrate non-inferiority against the thresholds as
   written; it **cannot** resolve a real 5 pp difference between the models. See Finding 6.
2. **Ceiling effects.** Both models scored 100% on measures 1 and 2 and zero misfires on measure 4.
   Three of the five measures therefore carry no discriminating information in this run.
3. **The non-English leg is Latin-script only** (German, Spanish, Portuguese). A CJK reference was
   dropped during fixture construction because its DOI was unregistered in Crossref and shipping an
   unverifiable ground truth would be worse than a narrower leg. "Non-English" here does not mean
   "non-Latin-script", and no claim is made about CJK/Cyrillic/Arabic references.
4. **The prompt omits the `Context: [sentence where cited]` clause** of the canonical template.
   Probe references have no citing manuscript. This makes the run a test of reference *existence*
   verification, not of claim-support verification.
5. **Single-day, single-run.** Web-search results vary day to day; the 3-repeat majority and the
   same-day pairing are what make the comparison fair (§532), but they do not make it longitudinal.
6. **Measure 4 passed without being stressed.** Zero guard misfires means no response shape tripped
   the fail-closed guards — not that the guards were exercised against a shape change. The adapter
   collapses a misfire into `NOT_SEARCHED`, so this measure is a tripwire, and the tripwire did not
   fire.

## Reproduction

```
# fixture is committed; hash must match the header above
sha256sum evals/bakeoff/cross_model_promotion/probe_set_v2.json

# 180 paired calls through the shipped adapter, Codex subscription, no API key
python run_bakeoff.py \
  --fixture evals/bakeoff/cross_model_promotion/probe_set_v2.json \
  --models gpt-5.6-sol,gpt-5.5 --repeats 3 --concurrency 6 --timeout 300 \
  --out full_run_v2.jsonl

python score_bakeoff.py --run full_run_v2.jsonl --json-out score_report_v2.json
```

The runner and scorer are harness scripts, not shipped ARS surface. The measured path — prompt,
adapter, grounding guard, verdict extraction — is the shipped one.
