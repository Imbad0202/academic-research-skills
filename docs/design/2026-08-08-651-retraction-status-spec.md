# #651 Deterministic Retraction Status and Authority Cutover

**Status:** frozen for implementation
**Authority:** this document, the v1.1 bibliographic-integrity signal schema,
and `terminal_policies.retraction`

## 1. Scope and claims

The citation gate records retraction metadata already returned by OpenAlex and
Crossref. OpenAlex supplies `is_retracted`; Crossref supplies update metadata
on both the cited work (`updated-by`) and an update notice (`update-to`). No
live network call is required for the deterministic resolver tests.

The resolver may claim only that named services returned named metadata at a
recorded time. It does not decide whether a paper's findings are sound, whether
the citation is legitimate in context, or whether a manuscript is publishable.

## 2. Authority and carrier

- `literature_corpus[].bibliographic_integrity_signals[]` is the only result
  carrier. A v1.1 `retraction_status` row replaces the ambiguous legacy
  `retraction_check` attestation as the status authority.
- `retraction_check` remains readable during one compatibility window, but it
  says only that a check reportedly ran. It never supplies a status or policy
  result and new retraction producers do not write it.
- The Cite-Time Provenance Finalizer is the only terminal-policy evaluator.
  The ethics agent points to its canonical row and cannot independently turn a
  retraction into a terminal verdict.
- The formatter transcribes the advisory row, checks policy freshness, and
  refuses a finalizer-emitted `HIGH-BLOCK`; it never re-evaluates the row.

## 3. Resolver input and reduction

The pure resolver accepts one corpus entry and normalized resolver envelopes:

```json
{
  "status": "checked | degraded | not_checked",
  "record": {},
  "records": []
}
```

`record` is the matched OpenAlex work. `records` contains the matched Crossref
work plus any fetched notice records. A DOI is required. Manual entries with a
DOI follow the same lookup path as other entries; manual entries without a DOI
emit an unresolved `not_checked` row. Title-only retraction matching is not
permitted.

Crossref events are relevant only when either:

1. an `updated-by` event occurs on the cited DOI; or
2. an `update-to` event on a notice points to the cited DOI.

The latest dated retraction/reinstatement event wins. Conflicting undated
events reduce to `disputed`, never a clean or terminal result. OpenAlex and
Crossref disagreement is explicit. Missing/degraded data is unresolved or
partial and is never silently read as clean.

## 4. Judgment context

The v1.1 row keeps deterministic facts separate from author context:

- load-bearing status joins affected claims by `worst_tier_wins`;
- retraction nature and date come only from resolver metadata;
- timing compares `source_acquisition_date`, never `obtained_at`;
- a legitimate-use exception requires both an explicit author declaration and
  a cited retraction notice; this check does not judge whether the prose truly
  discusses the retraction;
- reason codes are carried only when provided by the input record. Missing
  reasons render `not_served`, never an inference.

## 5. Freshness and cache

Retraction results use the distinct SQLite namespace
`retraction_status_cache_v1`, keyed by normalized DOI and resolver. Rows carry
the full normalized observation, an explicit `checked_at`, and a schema
version. Thirty days is the conservative revalidation threshold. A stale row
is returned as `stale` for visibility but must be revalidated before it can
produce a strict terminal block. Unknown and degraded observations have typed
values and cannot become `not_retracted` through cache coercion.

## 6. Policy and marker composition

Detection is unconditional. `terminal_policies.retraction` is absent/advisory
by default and `strict` only by explicit opt-in.

- advisory: the v1.1 row appears in the single `Bibliographic Integrity
  Advisories` section; no marker advisory token is minted;
- strict: a current, undisputed `retracted` row that lacks the deterministic
  legitimate-use exception is eligible for
  `TERMINAL-BLOCK severity=HIGH-BLOCK policy=retraction
  reason=retracted_reference mode=strict`;
- reinstated, disputed, stale, unknown/degraded, and declared-legitimate rows
  never produce that block.

`retraction` participates in the existing sorted `policy_hash` slug. The
single `CONTAMINATED-*` advisory slot is unchanged, and multiple terminal
tokens may still co-emit independently.

## 7. Acceptance matrix

Hermetic tests cover: OpenAlex true/false; Crossref `updated-by` and
`update-to`; reinstatement; resolver disagreement; stale cache rows;
missing acquisition dates; manual entries with and without DOI; default versus
strict behavior; no new advisory marker token; compound policy slugs; and the
declared-legitimate-citation exception.

## 8. External references

- OpenAlex Works: <https://developers.openalex.org/api-reference/works/get-a-single-work>
- Crossref Retraction Watch data: <https://www.crossref.org/documentation/retrieve-metadata/retraction-watch/>
- Crossref update registration: <https://www.crossref.org/documentation/register-maintain-records/maintaining-your-metadata/registering-updates/>
