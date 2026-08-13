# #655 Search-bounded claim-standing probe design freeze

> **Status:** DESIGN-FROZEN / TRACK A SUBSTRATE IMPLEMENTED / LIVE PROBE NOT IMPLEMENTED / NOT MEASURED
> **Issue:** #655
> **Shared evidence-row authority:** #656,
> `docs/design/2026-08-09-656-shared-evidence-row-contract-spec.md`
> **Measurement authority:** #654/#664,
> `evals/heldout/MEASUREMENT_CONTRACT.md`

## 1. Decision and authority boundary

The first claim-standing probe is an **opt-in, advisory-only, search-bounded**
inspection of claims already classified as `HIGH-IMPACT` by the existing #549
Phase E rule. It asks how the exact claim is addressed by a bounded, recorded set
of scholarly-index candidates. It does not decide whether the claim is true, how
the field stands globally, or whether the manuscript may proceed.

This freeze separates two implementation tracks:

1. **retrieval and candidate ledger**: consent, query planning, index adapters,
   caps, raw hits, work-family deduplication, deterministic selection, culling,
   content coverage, and operational failures;
2. **stance classification, presentation, and measurement**: relevance and
   stance labels, evidence-row pointers, denominators, empty categories, claims
   vocabulary, held-out ground truth, and the mandatory baseline row.

Neither track may silently define the other. Retrieval determines the bounded
candidate population. The stance classifier cannot add, remove, reorder, or
replace candidates. A presentation layer cannot omit a candidate or failure
because it makes the result less convenient.

The original design freeze added no live adapter, schema, stage, flag, prompt,
held-out suite, or report row. The offline implementation status recorded below
does not authorize an external search, model, or judge call and makes no
accuracy or efficacy claim. #655 stays open through implementation and
measurement.

### Implementation status (2026-08-13)

The first offline Track A substrate now implements three closed Draft 2020-12
contracts (`claim-standing-query-plan/1.0`,
`claim-standing-retrieval-input/1.0`, and
`claim-standing-candidate-ledger/1.0`) plus a pure deterministic finalizer.
Synthetic fixtures and mutation tests pin the complete consentable-plan
projection, one visible root attempt per planned query/index pair, hash-bound
and time-bounded retry authorization, monotonic attempt/hit timestamps, attempt
and raw-hit preservation, ordered filtering, work-family deduplication without
no-DOI bridges between distinct DOI components, canonical selection, explicit
relevance success/failure evidence, the 240/40 caps, and write-once exact replay.

This is not activation of the probe. The substrate accepts only already-retained
adapter-neutral local JSON and performs no retrieval, network, model, stance,
rendering, pipeline, evidence-row, or dispatch operation. Existing resolver
clients remain byte-pinned and unchanged. Track B, live discovery adapters,
evidence-row 1.3 work, pipeline wiring, independent expert ground truth, and the
baseline measurement row remain future work.

## 2. Placement and noninterference

The future probe is available at the Stage 2.5 and Stage 4.5 integrity
checkpoints only after Phase E has emitted its Claim Registry. It is an
additional user-requested view, not Phase E verification and not part of the
integrity result.

Every carrier and rendered view uses:

```text
layer = LLM-ADVISORY
gate_effect = none
read_ledger_effect = none
manuscript_mutation = none
```

The probe must never:

- change a Phase E verdict, severity, issue count, checkpoint result, correction
  route, formatter refusal, or Stage transition;
- convert a source into human-read status or write `/ars-mark-read`,
  `human_read_log`, `human_read_source`, or `read_scope`;
- add a citation, rewrite a claim, rank bibliography entries, or emit replacement
  prose;
- produce a scalar credibility, confidence, consensus, controversy, or trust
  score; or
- represent index coverage or an LLM label as field-level knowledge.

The existing DOI and exact-title resolver clients are not discovery adapters.
Implementation must add separate discovery interfaces; it must not widen the
resolver clients or pretend their few metadata candidates are a related-work
search.

## 3. Exact trigger and opt-in sequence

### 3.1 Probe-specific trigger

Version 1 deliberately uses a **narrower trigger than the complete #549 sample**.
A Claim Registry row is eligible only if it satisfies the same #549
`HIGH-IMPACT` definition already used by Phase E:

- headline conclusion in the abstract or conclusions;
- numerical claim, including a statistic, effect size, percentage, or threshold;
- causal claim;
- methods-critical claim; or
- disputed claim already carrying a contradiction disclosure or reviewer split.

At Stage 2.5, `selection_tier=HIGH-IMPACT` is the registry witness. `RANDOM`,
`TOP-UP`, and `NOT-SELECTED` rows are ineligible. At Stage 4.5, where Phase E
checks all claims, the producer reuses the same five-part high-impact
classification recorded in the registry instead of treating `ALL` as permission
to probe every claim. Ambiguous eligibility is ineligible until the researcher
confirms the classification; the confirmation is recorded and does not change
the Phase E registry.

This narrower rule is intentional. Claim-standing discovery transmits an
unpublished claim to external services, performs broader retrieval than source
verification, and may invoke an LLM over claim/evidence text. #549's random
sentinel and top-up floor remain Phase E quality controls; they are not consent
to expand this probe.

### 3.2 Consent is per probe, before transmission

Eligibility never dispatches automatically. Before any query planner, index, or
model receives claim text, the researcher sees and affirmatively accepts a
closed consent receipt containing:

- the exact claim text and claim id;
- every intended external index/provider and its purpose;
- whether the provider receives exact claim text, a researcher-edited query, or
  both;
- the proposed query, candidate, and content caps;
- whether abstracts or researcher-supplied full text may be sent to an LLM;
- the exact LLM provider/model when a stance call is proposed;
- local persistence, provider retention terms or an explicit `unknown`, and the
  deletion/export boundary;
- that the result is advisory, search-bounded, fallible, and not a gate; and
- separate choices to edit/redact the claim, approve retrieval only, approve
  retrieval plus stance classification, or cancel.

Consent is bound to the canonical claim digest, exact provider roster, caps, and
query-plan digest. An edit, new provider, larger cap, full-text use, or later
claim revision invalidates the receipt and requires a new opt-in. Absence,
refusal, or invalidation produces an explicit local `not_checked` record and no
network or model call.

## 4. Track A: retrieval and candidate ledger

### 4.1 Frozen query-plan shape

The query plan is researcher-visible and researcher-approved before dispatch.
It contains at most three non-empty queries. Every query records:

```text
query_id
query_text
construction = exact_claim | researcher_authored | assisted_then_researcher_approved
source_claim_sha256
language
date_filter
index_targets[]
```

`assisted_then_researcher_approved` is a future optional planner mode, not
authorization in this design PR. Its output is untrusted draft text, and the
exact assisted query must appear in the consent surface before it can leave the
session. The planner may not search, select sources, or call a second provider.

The implementation default is one `exact_claim` query derived only by removing
ARS citation markers and collapsing ASCII whitespace. It performs no stemming,
translation, synonym expansion, or silent truncation. A researcher may edit it
or add up to two queries. The original and accepted forms remain in an
append-only local plan ledger.

### 4.2 Adapter and resource limits

Each discovery adapter implements one closed request/response interface and
declares its index id, API/product identity, query capability, returned metadata,
abstract availability, pagination behavior, terms/retention reference, and
failure vocabulary. A `known` retention state requires a non-empty reference;
an explicit `unknown` state requires a null reference, so the surface cannot
claim known terms while withholding them. An adapter cannot fall through to a
different index.

Version 1 ceilings are:

- at most 3 queries;
- at most 4 explicitly consented indexes;
- at most 20 raw hits per `(query_id, index_id)`;
- at most 240 raw-hit ledger rows before deduplication; and
- at most 40 selected work families for stance classification.

The adapter requests no page after its per-query cap is satisfied. A provider
returning more records is truncated at the adapter boundary, with the provider
reported count and exact truncation recorded. A timeout, authentication failure,
rate limit, malformed response, unavailable service, or unsupported query is a
named index attempt with zero hits and an explicit failure; it is never retried
or replaced silently. A later user-authorized retry is a new attempt and stays
visible beside the first.

### 4.3 Raw-hit ledger

Every returned hit enters the append-only ledger before filtering. At minimum a
raw row carries:

```text
probe_id, query_id, index_id, attempt_id, provider_rank
provider_record_id, doi, title, authors, year, language
document_type, publication_status, abstract_state
landing_url, returned_at, raw_metadata_sha256
```

Nulls are explicit. The ledger retains the provider order and query/index
identity. It does not persist provider-only full records beyond the consented
data-minimization need. Credentials, cookies, request headers, surrounding
session text, and unrelated provider metadata are prohibited.

### 4.4 Filters and work-family deduplication

Filters run in this fixed order and never delete ledger rows:

1. malformed minimum identity (`missing_title_and_stable_id`);
2. researcher-approved date range (`outside_date_range`);
3. researcher-approved language set (`outside_language_set`);
4. document-type allowlist (`outside_document_type`);
5. work-family deduplication; and
6. relevance assessment.

Deduplication groups records by the first available deterministic key:

1. normalized DOI equality;
2. an explicit provider version-of / is-version-of relation;
3. normalized title plus publication year and first-author family name; then
4. normalized title plus a researcher-confirmed version-family relation.

A DOI participates in minimum identity, canonical preference, or equality only
after NFKC normalization and known-prefix trimming, and only when the remainder
matches `10.<4-9 ASCII digits>/<suffix>`. The suffix must contain a Unicode
letter or number and must contain no Unicode control/format/surrogate,
separator, or whitespace character. Invalid provider DOI text stays retained
as raw metadata but is treated as no DOI and can never create a union.

Title normalization is Unicode NFKC, case-folding, punctuation-to-space, and
ASCII-whitespace collapse. It is a grouping candidate, not proof of identity.
Ambiguous groups stay separate unless the researcher confirms the relation.

One work family keeps all source records and all queries that found it. The
canonical display record is chosen by this fixed precedence: published version
over preprint, record with DOI over no DOI, record with an available abstract,
earliest provider rank, then ASCII order of `(index_id, provider_record_id)`.
The other versions remain visible. Deduplication never discards contrary
metadata or makes a preprint-to-published relationship invisible.

### 4.5 Relevance and deterministic top-K

Relevance is separate from stance:

```text
relevance = relevant | not_relevant | ambiguous | not_checked
```

A future relevance assessor sees only the exact claim and candidate title plus
abstract when available. A canonical assessment-input digest binds that exact
claim, candidate content, and assessor contract; the exact UTF-8 prompt and its
digest, version, raw output, rationale, and failure are retained. `not_relevant`
requires a recorded reason anchored to population,
phenomenon/exposure, outcome, or proposition mismatch. `ambiguous` remains
eligible; a missing abstract is not enough to declare a record irrelevant.

Selected work families are all `relevant` and `ambiguous` families up to the
40-family ceiling. Ordering is deterministic and does not use an opaque score:

1. relevant before ambiguous;
2. best provider rank across all raw records;
3. earliest query order;
4. ASCII order of canonical `(index_id, provider_record_id)`.

Every otherwise eligible family beyond 40 remains visible with
`candidate_cap_exceeded`. A hidden reranker, diversity sampler, citation-count
boost, journal-prestige boost, or model-selected top-K is forbidden in V1.

### 4.6 Candidate-ledger state vocabulary

Every raw hit ends in exactly one user-visible state:

```text
selected
missing_title_and_stable_id
outside_date_range
outside_language_set
outside_document_type
duplicate_version
not_relevant
not_checked
candidate_cap_exceeded
retrieval_failed
```

`duplicate_version` points to the retained work-family id. Retrieval failures
are attempt rows rather than fabricated source rows. `not_checked` preserves a
relevance-assessment failure with its retained raw output, if any, and explicit
failure evidence; it never implies irrelevance. `selected` does not mean
supportive, credible, high-quality, or cited. A candidate cannot disappear
between retrieval, classification, and rendering.

### 4.7 Content coverage

The default evidence is the exact abstract returned by a consented index.
Candidate rows declare one of:

```text
coverage = abstract | session_held_full_text | metadata_only
content_state = available | abstract_missing | source_missing |
                access_failed | retrieval_failed | not_checked
```

V1 performs no paywall bypass and no ambient full-text crawl. Full text may be
used only when the researcher separately supplies or selects a session-held,
lawfully accessible source and consents to its use. The ledger records the
content hash, source identity, rights/share declaration, and exact bounded
passage used. A landing page or DOI is not full text. `metadata_only` and a
missing abstract lead to stance `not_checked`, never `not-addressed`.

## 5. Track B: stance, presentation, and measurement

### 5.1 Classification unit and closed labels

The classification unit is one selected work family against one exact claim.
Relevance is decided first and remains a separate field. The stance layer uses:

```text
check_state = performed | not_checked
stance = support | contradict | mixed | not_addressed |
         INSUFFICIENT_EVIDENCE | AMBIGUOUS | null
failure_state = null | abstract_missing | source_missing | access_failed |
                retrieval_failed | judge_timeout | judge_error | parse_error
```

Cross-field rules are:

- `performed` requires non-null stance, null failure, explicit evidence scope,
  a bounded rationale, and at least one evidence-row reference;
- `not_checked` requires null stance and one non-null failure state;
- no abstract or other inspected text is `not_checked/abstract_missing`, never
  `not_addressed`;
- `not_addressed` means inspected, relevant evidence does not make a claim about
  the proposition, not that the literature is silent;
- `INSUFFICIENT_EVIDENCE` means the inspected text touches the proposition but
  lacks enough information to assign a directional stance;
- `AMBIGUOUS` means the inspected text permits incompatible readings or its
  direction cannot be resolved from the bounded evidence;
- population, intervention/exposure, comparator, outcome, timing, or condition
  differences that change direction use `mixed` when both directions are
  explicit, otherwise `AMBIGUOUS`; and
- model confidence, probability, or a scalar relevance/stance score is neither
  accepted nor rendered.

`support` and `contradict` describe the relation of the inspected candidate text
to the exact claim. They do not certify source quality, reproduce an analysis,
or establish truth.

### 5.2 #656 evidence-row ownership

#656 remains the only shared evidence-row contract owner. `evidence-row/1.0`
has the closed `phase_e_claim_verification` surface and must not be repurposed.
This design does not copy its schema, vocabulary, hashes, rendering rules, or
rights logic into a probe-owned substitute.

Before live implementation, the shared family must expose a separately
versioned `claim_standing_advisory` surface or an equally explicit compatible
extension. That extension must preserve #656's strict UTF-8 replay, exact source
hash/span binding, bounded excerpt, inert Markdown/HTML rendering, paging,
explicit empty/failure states, sharing/rights caveats, and read-ledger
noninterference. The claim-standing carrier stores complete row pointers and
hashes, never free-form excerpts or rendered markup. Until that version exists,
stance rows cannot be persisted or rendered as conforming evidence rows.

The extension may represent abstract-level evidence, but it cannot call an
abstract `verified full text`, infer rights from public availability, or let an
exact excerpt match determine stance.

### 5.3 Presentation and denominators

The user view has three inseparable parts:

1. consent and recorded-search metadata;
2. the complete candidate ledger, including culled records and failures; and
3. the selected-candidate distribution plus openable per-source stance rows.

The primary presentation denominator is **all selected work families**, including
`not_checked` and every operational failure. The following buckets therefore
sum exactly to `selected_total`:

```text
support, contradict, mixed, not_addressed,
INSUFFICIENT_EVIDENCE, AMBIGUOUS, not_checked
```

A secondary performed-only distribution may be shown only beside, never instead
of, the all-selected denominator. The view also reports raw-hit count, unique
work-family count before relevance, every culling-state count, selected count,
performed count, and not-checked/failure counts. It never uses one denominator
for counts and a smaller hidden denominator for percentages.

Every category renders even when empty. Fixed empty wording is:

```text
No <category> sources were found among the selected candidates within this
recorded search.
```

It must not say `none exist`, `the field agrees`, `the literature establishes`,
or an equivalent unbounded statement.

Each selected row displays title, authors/year, versions, finding queries and
indexes, original provider ranks, coverage (`ABSTRACT`, `SESSION-HELD FULL
TEXT`, or `METADATA ONLY`), relevance, stance or failure, conditions noted,
bounded evidence-row link, and an openable source URL. Culled rows display their
fixed reason and retained-family pointer where applicable.

### 5.4 Search-bounded claims vocabulary

The advisory may state only facts in these forms:

- `Within the recorded search of <indexes> using <queries>, <n>/<N> selected
  candidates were classified <stance>.`
- `No <stance> sources were found among the selected candidates within the
  recorded search.`
- `<n>/<N> selected candidates were not checked or failed; see the candidate
  ledger.`
- `This candidate's inspected <abstract/full text> was classified <stance>
  relative to claim <claim_id>.`

Every statement is adjacent to probe-scoped queries, exact index states, caps,
filters, hit counts, failures, and completion timestamp. Bibliography-global
`last_searched_at` is not reused. The probe timestamp never upgrades a novelty
claim or extends another search record.

Forbidden output includes `scientific consensus`, `field-level standing`,
`verified true/false`, `credibility score`, `trust score`, `confidence score`,
`complete search`, and any claim that absent results prove absence.

## 6. Privacy and data minimization

The implementation maintains separate transmission ledgers for retrieval and
classification. Each event records recipient, purpose, exact content classes,
byte counts, local hashes, time, consent receipt, result state, and provider
retention reference. It does not log credentials or duplicate raw unpublished
text into telemetry.

Only these content classes may leave the session after exact consent:

- accepted search queries to named indexes;
- the exact claim and selected title/abstract to the named stance provider; and
- a user-selected bounded full-text passage, never an entire session-held source,
  when separately approved.

No manuscript, bibliography, neighboring claim, author identity, institution,
review comment, private note, or unrelated corpus text is sent by default.
Query redaction is allowed but visible in the search metadata. A provider that
cannot disclose its identity or retention state is rendered as `unknown`; that
does not become implied privacy assurance.

Local artifacts default to `session_only + not_assessed`. The Track A CLI
refuses `build --output` before path creation while the hash-bound consent says
`session_only`; a persistent ledger requires the existing
`explicit_local_export` consent state and has no command-line override. Export
to the named local path requires that exact consent state; any onward sharing
requires a separate rights/share decision and redaction of unpublished claim
text where requested. Deletion removes local working copies but does not claim
to erase a provider's records unless a confirmed provider receipt exists.
The consent receipt binds the exact absolute `authorized_output_path`, and the
CLI rejects any relative or non-matching output string before creating a path,
so the same receipt cannot be retargeted by changing the working directory. The exporter
creates the final path exclusively, refuses symlink following on
supported non-Windows hosts, applies mode `0600` from creation under umask
`022`, and fsyncs the file and parent directory before reporting success. The
final ledger copies `local_persistence`, `export_boundary`, and the authorized
path from the consent receipt and uses the same persistence value for each work family's
`sharing_scope`; a persisted export is not labeled `session_only`.
The independent `rights_basis=not_assessed` label remains unchanged because
local persistence authority does not establish publication, redistribution, or
provider rights.

Portable schema `\\S` checks are only a first screen. The Track A runtime uses
one NFKC visible-semantic-text predicate for claims, queries, provider
disclosures/retention references, consent boundaries, non-null provider ids,
titles/authors, available abstracts, successful assessment rationale/raw
output, and failure detail. It rejects surrogates and strings made only of
Unicode control/format, separator, combining, whitespace, or punctuation
characters. A failed malformed assessment may retain whitespace-only or
format-only raw output exactly; this exception never applies to its failure
detail.

## 7. Failure, freshness, and revision behavior

Failures are evidence, not missing rows. The probe may render partial index
coverage only when every failed index/query attempt remains visible and the
claim language says `recorded search with failures`. It may not top up from a
new index, expand caps, reuse stale cached hits, or retry a model silently.

The probe identity binds:

```text
claim text SHA-256
consent receipt SHA-256
query plan SHA-256
adapter registry and exact versions
index attempts and completion times
candidate-ledger SHA-256
content/evidence-row hashes
stance prompt/model/runtime configuration
```

A claim-text change, query edit, adapter change, candidate-ledger change,
content change, or stance-configuration change makes the result stale. A stale
result remains inspectable but cannot be presented as current. Re-running after
new consent creates a new probe id; it never overwrites the prior ledger.

## 8. Held-out stance set and baseline gate

The shipping implementation PR must create a separate
`evals/heldout/claim_standing_probe/` suite and register it under the existing
held-out measurement contract. This design PR does not create an empty or
unmeasured registry entry.

Before the first call, the future suite freezes:

- repository-owned or rights-cleared claim/evidence pairs spanning English and
  zh-TW, abstract/full-text distinctions, conditional differences, missing
  abstracts, irrelevant candidates, and every stance/failure state;
- the exact eligible population and sampling rule;
- at least two independent domain-qualified human labels per semantic item,
  blinded to subject output, model/provider, prompt variant, and expected
  baseline performance;
- a separate arm-blind human adjudicator for disagreements, with raw labels and
  disagreement retained;
- a strict subject-output schema, prompt, model/runtime/token settings, replicate
  rule, stopping rule, and execution manifest; and
- a mechanical scorer that compares the frozen subject enum to the expert-
  adjudicated label without asking another model to reinterpret either.

The first published row is a **baseline stance-classification measurement**, not
an efficacy comparison. It reports confusion counts and rates by stance,
language, evidence scope, relevance state, and failure class; macro and
micro-averages remain separate. At least two subject replicates per item are
required for a decision-relevant row, with spread and blocked/partial outputs
reported. Ground-truth agreement and adjudication counts publish beside the
subject result.

The future suite class must match the implemented scoring design and the
then-current registry rules. A mechanical final comparison does not erase the
human judgment used to create ground truth; that provenance remains a required
suite artifact. The held-out contract, plan, rubric/label guide, expert packet,
and execution manifest are hash-frozen before dispatch. Any model or human
dispatch requires separate consent to the exact frozen plan.

Until a valid baseline row exists, every probe surface says:

```text
STANCE CLASSIFICATION UNMEASURED
```

README, CHANGELOG, documentation, and UI may describe only the frozen design and
operational state. They may not claim accuracy, usefulness, reduced overclaiming,
better literature coverage, or parity with a vendor product.

## 9. Implementation acceptance gates

The future implementation is incomplete unless tests prove all of the following:

1. only exact high-impact registry rows are eligible; random/top-up/all do not
   silently expand the trigger;
2. no call occurs without an exact current consent receipt;
3. resolver clients are unchanged and discovery uses explicit new adapters;
4. per-index/query caps and the 240/40 ceilings fail closed;
5. every raw hit, duplicate, cull, cap overflow, and attempt failure remains in
   the candidate ledger;
6. deduplication and top-K ordering replay deterministically;
7. missing abstracts and operational failures become `not_checked`, never
   `not_addressed`, support, or contradict;
8. relevance and stance cannot overwrite each other;
9. all selected candidates appear exactly once in the distribution denominator;
10. empty categories use the fixed bounded wording and no scalar score exists;
11. evidence rows replay under a #656-owned versioned surface and rendered
    external text is inert;
12. no Phase E verdict, gate, manuscript, citation, or read-ledger byte changes;
13. claim/query/configuration drift makes an old result visibly stale;
14. transmission logs obey the consented content allowlist; and
15. the held-out seed, expert ground truth, and baseline measurement row pass the
    #654/#664 contract before any efficacy claim.

Tests use synthetic local fixtures and fake adapters only. Live indexes, models,
judges, browsers, and network access are not implementation-acceptance
dependencies.

## 10. Explicit non-goals

Version 1 does not:

- estimate global literature or field consensus;
- perform a systematic review, meta-analysis, citation-network analysis, or
  exhaustive discovery;
- assess study quality, risk of bias, retraction status, author reputation, or
  journal prestige;
- replace source verification, claim-to-citation alignment, novelty checking,
  cross-paper tensions, or researcher reading;
- provide automatic claim rewriting or bibliography modification;
- use a scalar credibility/trust/confidence score;
- send unpublished content without exact current opt-in; or
- claim behavioral efficacy before the required baseline measurement row.

The public Claim Radar launch referenced in #655 is evidence that this product
shape exists, not evidence that such classification is accurate or beneficial.
ARS adopts none of its efficacy or coverage claims by freezing this design.

## 11. Activation and issue closure

This design freeze resolves the pre-implementation choices requested by #655:
the exact high-impact trigger, explicit opt-in and data boundary, new discovery
adapter boundary, user-visible candidate population, caps and deterministic
selection, separate relevance/stance/failure states, distribution denominator,
#656 ownership, search-bounded output vocabulary, and mandatory baseline gate.

It does not close #655. Closure still requires live discovery adapters, Track B
and pipeline integration, a frozen held-out set, independently labeled ground
truth, a valid baseline stance-classification measurement row, and docs whose
claims do not exceed that row. The offline Track A contracts, deterministic
finalizer, and synthetic acceptance coverage are implemented but do not satisfy
those activation gates by themselves.
