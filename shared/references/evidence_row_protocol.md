# Shared Evidence-row Protocol (`evidence-row/1.0`, `1.1`, and `1.2`)

This protocol is the runtime-facing authority for evidence rows. The canonical
field shape is `shared/contracts/evidence/evidence_row.schema.json`; cross-field
semantics are implemented by `scripts/evidence_rows.py`; the frozen decision is
`docs/design/2026-08-09-656-shared-evidence-row-contract-spec.md`.

## V1 surface and persistence

V1 has one live surface:

```text
surface = phase_e_claim_verification
Integrity Report.phases.E_claims.evidence_rows[]
```

The Integrity Verification Agent emits one row per selected
`(claim_id, ref_slug, anchor)` tuple. The full ordered array travels inside the
existing Schema 5 Integrity Report. It is not a new passport aggregate. A
multi-citation claim keeps one row per citation; `E_claims.checked` and verdict
summaries continue to count distinct claims.

The Stage 4 -> 5 opt-in `claim_audit_results[]` contract is a different lifecycle
and is not a V1 producer or consumer.

## Producer sequence

For each selected tuple:

1. Pass the candidate row and, when available, its exact session-held source text
   directly to `build`. Never pass a URL for the builder to fetch.
2. Preserve the v3.7.3 anchor's encoded value. The builder validates and decodes
   it exactly once with strict UTF-8.
3. For a `page` or `section` anchor, pass only the bounded passage the agent
   actually relied on. The builder requires that passage to be an exact substring
   of the held source text. It does not authenticate the locator.
4. Pass an explicit failure state when an upstream access or extraction attempt
   failed. Never copy the claim, writer anchor, error message, or placeholder into
   `excerpt.text`.
5. Persist the returned row unchanged. Render only the persisted row array.

The builder, not producer prose, decides the evidence state:

| Anchor / input | State | Excerpt |
|---|---|---|
| `quote`, exact once-decoded source match | `verified_exact_match` | exact matched text |
| `quote`, held source mismatch | `unconfirmed_anchor` | null |
| `page` / `section`, supplied passage exactly in held source | `agent_extracted` | exact passage |
| `paragraph` | `not_checked` | null |
| any non-`none` anchor, no held source | `source_missing` | null |
| explicit stable permission/paywall failure | `access_failed` | null |
| explicit upstream retrieval/extraction failure | `retrieval_failed` | null |
| explicit unperformed check | `not_checked` | null |
| `none` / absent marker normalized to `none` | `anchorless` | null |

The canonical display labels come only from `scripts/evidence_rows.py`. “Verified”
in `VERIFIED EXACT MATCH` applies to excerpt provenance, not the Phase E claim
verdict.

## Exactness and budgets

- Source-content SHA-256 covers the exact held source string encoded as UTF-8.
  Artifact/PDF hashes are separate nullable provenance and cannot substitute.
- No Unicode, case, whitespace, newline, or punctuation normalization occurs.
- Percent decoding runs once. `%HH` must be well formed and yield strict UTF-8;
  `+` remains a plus sign.
- Quote anchors and excerpts are at most 25 whitespace-split words and 1,000
  Unicode code points. Over-budget rows fail; they are not truncated.
- Positive excerpts carry a SHA-256 plus a half-open UTF-8 byte span. Replaying
  that span against the exact source content must yield the excerpt bytes.
- `row_sha256` binds the canonical complete row except for the digest field itself.

## Cache replay

Only `verified_exact_match`, `agent_extracted`, and `unconfirmed_anchor` are
cacheable. A candidate hit is revalidated against the current explicit source,
anchor, schema, hashes, budgets, and state transition. Source or anchor drift is a
miss. A corrupt cache candidate fails closed as a cache input: the builder
discards it and rebuilds from the current explicit source/anchor inputs, and
corrupt content is never returned or displayed as a hit.

A hit preserves the evidence state, excerpt bytes, byte span, and capture time.
It changes the cache status to `hit` and recomputes the row digest. Empty/failure
states use `not_used`. Renderers never read or write cache entries.

## Checkpoint rendering

`render_markdown` and `render_html` require an explicit in-memory
`ref_slug -> exact session-held source text` map for every source-bound row.
Before display they replay `verified_exact_match`, `agent_extracted`, and
`unconfirmed_anchor` against that text. Missing replay text is a render failure:
a self-consistent row plus unkeyed digests cannot prove where writer-controlled
text came from.

The renderers do not retrieve or open a source, corpus item, sibling path, URL,
DOI, cache, environment variable, or model tool. Replay validation recomputes
the strict once-decode and source-bound hashes, but never decodes the stored
display value again, extracts new text, derives a new state, or mutates the row.

Markdown and HTML surfaces use the same fixed evidence labels and treat every
claim, locator, source label, detail, decoded anchor, and excerpt as untrusted
data. A payload cannot create a tag, comment, link, image, heading, fence, extra
table cell/row, or prompt instruction. Only bounded stored evidence appears;
surrounding source context never does.

The default and maximum page size are 25 rows; a caller may request a smaller
positive page. Each page reports its one-based page, total pages, row interval,
and total rows. There is no render-all mode and no total-row cap. Walking the
pages preserves every row exactly once in document order.

## Rights and privacy

Rows default to:

```json
{
  "sharing_scope": "session_only",
  "rights_basis": "not_assessed"
}
```

A user-confirmed shareable row must pair with
`rights_basis=user_declared_authorized`. The contract never infers permission from
source location or availability. A 25-word excerpt is an adjudication aid, not a
license finding. Exporters that cannot preserve the caveat remove the excerpt.

No full text, abstract, private notes, surrounding context, API credential, or
rendered markup belongs in an evidence row.

## Legacy and degradation

A positively identified pre-#656 Schema 5 report may omit `evidence_rows`; use
the explicit `--allow-legacy-absence` compatibility flag to render it as
`LEGACY — EVIDENCE ROWS UNAVAILABLE`. Missing shape alone is not legacy proof,
and render fails without the flag. Do not interpret absence as an empty
successful check and do not synthesize historical excerpts. A current producer
with selected tuples must emit corresponding rows, including explicit empty
states, and may never use the compatibility flag.

For a current report, distinct row `claim_id` count must equal
`E_claims.checked`, distinct claims with Phase E verdict `VERIFIED` must equal
`E_claims.verified`, and rows sharing one `claim_id` must repeat the same claim
object and verdict. These checks reject an empty-success carrier and
contradictory multi-source rows. Exact tuple coverage is still audited against
the E1 Claim Registry, which remains the selection authority and is not copied
into a second V1 machine manifest.

Failure states do not alter Phase E verdict taxonomy or gate logic. The evidence
row is an adjudication view, not a new closure condition.

## Human-read boundary

Seeing an excerpt at a checkpoint is not reading the source. Evidence-row build,
validation, cache replay, and rendering never call `/ars-mark-read`, never write a
human-read log, and never change `human_read_source`, `read_scope`, latest-event
resolution, or LOW-WARN promotion.

## Consumer rule

Consumers reference this protocol and the schema by pointer. They consume the
machine row, not a copied enum or a parsed rendered table. They may not upgrade
`unconfirmed_anchor`, `not_checked`, `source_missing`, `access_failed`,
`retrieval_failed`, or `anchorless` into evidence-bearing states.

## Version 1.1 (`evidence-row/1.1`) authority-profile advisory extension (#681)

`shared/contracts/evidence/evidence_row_v1_1.schema.json` is a separate closed
version for `surface=authority_profile_content_coverage`. It does not extend the
Phase E row in place: `claim`, `verdict`, and `detail` are absent, and exact
`requirement_pointer`, `authority_anchor_pointer`,
`structured_expectations[]` pointer/digest, packet artifact, and advisory
document-locator bindings replace them. Version 1.0 producer behavior, cache
semantics, persisted bytes, and Phase E rendering remain unchanged. A page may
contain only one evidence-row version/surface.

The 1.1 builder is `build_advisory(...)`. It records only passage provenance;
it never chooses an `advisory_coverage_status`, interprets a structured
expectation, opens a packet path, retrieves content, or calls a model/API. The
closed states are:

- `agent_extracted`: a once-decoded, bounded quote is an exact substring of the
  explicitly supplied artifact string;
- `checked_no_match`: the explicit artifact string was checked, with no quote
  or excerpt persisted; and
- `not_checked`, `source_missing`, `access_failed`, and `retrieval_failed`:
  explicit unperformed/empty states with null content binding and excerpt.

Both source-bound states require replay from an explicit
`artifact_id -> exact session-held content` map before rendering. V1.1 retains
the same strict once-decode, 25-word/1,000-code-point bounds, exact UTF-8 content
hash and byte-span rules, inert Markdown/HTML treatment, rights pairing, and
human-read-ledger noninterference. It deliberately fixes `cache.status` to
`not_used` and `cache.key_sha256` to null.
For a positive row, `captured_at` is the explicit RFC 3339 timestamp carried by
the closed advisory draft; it is not invented from the authority-context
confirmation time or the runtime clock.

V1.1 rows are nested only in the replay-bound
`content-coverage-advisory/1.0` carrier defined by
`shared/contracts/human_subjects/content_coverage_advisory.schema.json` and
`shared/references/authority_content_coverage_advisory_protocol.md`. Their
labels remain `LLM-ADVISORY`; neither an exact passage nor a checked-no-match
state changes #667 deterministic status, readiness, authorization, or
institutional acceptance, and neither is an adequacy or efficacy finding.

## Version 1.2 cross-document consistency extension (#672)

`shared/contracts/evidence/evidence_row_v1_2.schema.json` is a separate closed
version whose only surface is `cross_document_consistency`. It is nested only in
`cross-document-consistency-advisory/1.0` and is finalized and replayed by
`scripts/build_cross_document_consistency_advisory.py`. It does not widen either
earlier schema or enter the Phase E Integrity Report. The 1.0 and 1.1 schemas,
`scripts/evidence_rows.py` behavior, cache semantics, rendering, and serialized
identities remain unchanged; versions and surfaces cannot be mixed.

One 1.2 row is the complete ordered evidence unit for one observation. The first
three pair kinds have two logical-role slots. Manuscript/preregistration has
exactly three: `manuscript_report`, `preregistration`, then the manuscript-bound
`disclosure_scope`. Logical roles remain distinct even when several bind the
same accepted manuscript bytes.

Its states are `agent_extracted`, `checked_no_match`, `not_checked`,
`source_missing`, `access_failed`, and `retrieval_failed`. A quote is exact-span
replayed. `checked_no_match` binds an exact, non-empty, named source scope and
only records the caller's semantic assertion that no counterpart was located;
it does not prove semantic absence or scope completeness. Methods absence
requires one quote plus a checked counterpart scope. An undisclosed
preregistration deviation requires two quotes plus its third checked disclosure
scope. Consumers cannot promote an unavailable or unperformed slot.

V1.2 retains strict single percent decode with literal `+`, the 25-word and
1,000-code-point ceilings, exact strict-UTF-8 hash/span replay, inert rendering,
and paired sharing/rights values. It performs no cache lookup, model/API call,
retrieval, normalization, or ambient-clock read. One canonical `row_sha256`
binds the complete bilateral or trilateral row.

The row supports only a caller-supplied `LLM-ADVISORY` / `UNMEASURED`
observation. It creates no PASS/FAIL, score, gate, clean/agreement certificate,
ClaimIntent, revision authority, or consent/protocol finding. See
`shared/references/cross_document_consistency_advisory_protocol.md`.

## Version 1.3 claim-standing advisory surface (#655)

`shared/contracts/evidence/evidence_row_v1_3.schema.json` defines
`evidence-row/1.3`, surface `claim_standing_advisory`: one provenance-only row
per (probe claim, selected work-family candidate) in the #655 claim-standing
probe. The row binds a bounded inspected-evidence excerpt to the exact source
content hash and UTF-8 span, reuses the family's cache, content-handling, and
row-hash blocks verbatim, and carries a `coverage` declaration
(`abstract` / `session_held_full_text` / `metadata_only`) in place of 1.0's
anchor: the two anchor-derived excerpt states do not exist on this surface.
Cross-field conditionals bind retrieved states to a full payload and a bound
source, non-retrieved states to null payloads and `contains_external_text:
false`, the rights coupling in both directions, and metadata-only coverage to
failure states with a null source hash. The row never carries a stance or
verdict; an exact excerpt match never determines stance; abstract-level
coverage is never rendered as verified full text. The consuming stance record
(`claim-standing-stance-record/1.0`) references rows by id AND row hash. No
runtime validator for this surface exists yet — the future stance runner owns
replay verification before rendering.
