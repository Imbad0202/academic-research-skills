# #660 — Tortured-phrase screening for own drafts and cited sources

> **Status:** DESIGN-FROZEN / UNMEASURED
> **Issue:** #660
> **Dependency:** #678 is closed and its canonical bibliographic-integrity carrier
> is the only corpus-side carrier.
> **Execution boundary:** this design authorizes no live model, external API,
> network fetch, human or model judge, native PPS import, redistributed phrase-list
> content, or expensive evaluation.

## 1. Decision and claim boundary

ARS will add a local, deterministic phrase-pattern matcher and expose its output on
two advisory surfaces:

1. an own-draft report produced immediately before final formatting; and
2. one canonical bibliographic-integrity signal row for each citation and each
   metadata surface (`title` and `abstract`), including explicit not-checked rows.

The matcher is **mechanically deterministic**: the same manuscript or metadata
bytes, canonical-AST snapshot bytes, detached manifest bytes, explicit timestamps,
and runtime version produce byte-identical machine output. That execution property
does not raise the epistemic strength of the result. A phrase-list rule is a risk
heuristic, not an authority about origin, misconduct, paper-mill production, source
quality, or contextual legitimacy. Corpus rows therefore use:

```text
epistemic_class = heuristic_advisory
epistemic_label = HEURISTIC-INDICATOR
```

The own-draft artifact likewise carries:

```text
layer = HEURISTIC-ADVISORY
evaluation_status = UNMEASURED
```

The fixed user-facing positive wording is **“phrase-list match requiring review.”**
A checked zero-match result says only **“no phrase-list match observed on the
checked surface; absence is not a clean certification.”** No output may call a work
contaminated, generated, fraudulent, tortured, paper-mill-produced, or clean.
The carrier's always-present category label is the neutral **“Phrase-list screening
advisory”**; positive wording appears only on a `detected` row, never on a zero,
missing, or degraded row.

V1 performs no contextual false-positive judgment. It does not suggest replacement
text and does not edit a manuscript or citation. A future human or model judgment
would require a separately versioned, explicitly judgment-labelled artifact; it
must never be folded into the deterministic matcher transcript.

## 2. Authority and compatibility

### 2.1 One corpus carrier

`literature_corpus[].bibliographic_integrity_signals[]`, governed by
`shared/contracts/passport/bibliographic_integrity_signal.schema.json`, remains the
single corpus-side authority. #660 does not introduce another corpus aggregate,
reuse the closed boolean `contamination_signals` object, or add an advisory token to
the reference-marker grammar.

Implementation adds `bibliographic-integrity-signal/1.2` to that schema. Version
1.2 is a feature-specific profile within the existing carrier, not a new carrier.
It requires `signal_type: tortured_phrase_match`, the heuristic class and label
above, a closed `tortured_phrase_context` block, advisory-only terminal policy, and
`display.marker_token: null`. Shipped canonical v1.0 and v1.1 fixtures and current
producer outputs retain byte and validation identity. The new signal-type invariant
intentionally rejects previously underconstrained tortured-phrase mutations that
claimed `deterministic_fact` or terminal-policy eligibility; no canonical producer
emitted those shapes. The v1.1 retraction profile and its terminal policy are
unchanged.

The existing #678 tortured-phrase fixture is a scaffold, not evidence that #660 is
implemented. New #660 producers emit only v1.2 rows. No migration may reinterpret
old heuristic rows as a completed title or abstract check.

### 2.2 Separate citation-by-surface rows

Each corpus entry holds exactly one current v1.2 row for each Cartesian key
`(citation_key, surface)`. The id is hash-bound:

```text
bis:<schema-safe-citation-key>:tpm_title_<20-hex-binding-prefix>
bis:<schema-safe-citation-key>:tpm_abstract_<20-hex-binding-prefix>
```

The existing corpus schema already restricts `citation_key` to a signal-id-safe
alphabet. Inputs outside that alphabet fail corpus validation; the producer does not
invent a fallback identity. The binding prefix is derived deterministically from the
citation key, surface, exact snapshot SHA-256 (or explicit unavailable state), and
exact surface-content SHA-256 (or null for an absent or empty surface).
`signal_type` remains `tortured_phrase_match`; the surface-specific id makes the rows
independently addressable and prevents one aggregate status from hiding partial
coverage.

The non-in-place enricher supersedes exactly one prior v1.2 row for the same
citation×surface when any binding changes. It preserves every legacy v1.0 row and
every other signal type, emits no history row, and rejects two or more pre-existing
v1.2 current rows for one citation×surface as ambiguous. An unchanged replay yields
the same id and byte-identical row.

The corpus schema requires a title, so every schema-valid entry receives a title
row whenever the check is invoked. An abstract is available only when the field is
present and contains at least one non-whitespace Unicode code point. The exact
surface rules are:

| Surface state | `check_status` | `finding` | Meaning |
|---|---|---|---|
| valid snapshot and one or more retained instances | `checked` | `detected` | phrase-list match requiring review |
| valid snapshot and zero retained instances | `checked` | `not_detected` | no match on this checked surface; not a clean certificate |
| abstract field absent | `not_checked` | `unresolved` | `ABSTRACT_MISSING` |
| abstract present but empty/whitespace | `not_checked` | `unresolved` | `ABSTRACT_EMPTY` |
| snapshot not supplied | `not_checked` | `unresolved` | `SNAPSHOT_NOT_PROVIDED` |
| manifest/snapshot/AST/parser integrity failure | `degraded` | `unresolved` | exact closed failure code |

Manual corpus entries have no exemption. Their local title is checked exactly like
any other title, and their abstract follows the same present/absent rule. No DOI,
resolver, acquired PDF, or network request is required.

### 2.3 Formatter and finalizer ownership

The bibliography producer appends schema-valid rows; it does not evaluate policy.
The formatter transcribes them into the existing, single `Bibliographic Integrity
Advisories` section in lexical `signal_id` order. The Cite-Time Provenance Finalizer
does not promote a v1.2 row, and the formatter does not create or refuse a marker
because of it. Retraction, citation-existence, and legacy-contamination terminal,
finalizer, and marker-policy behavior remains unchanged. The additive advisory-table
columns and stronger inert escaping intentionally change rendered table bytes, not
those earlier policy semantics.

The generic #678 advisory table remains complete: the max-25 detail rule in §9 does
not authorize dropping canonical signal rows from that table.

## 3. Snapshot and detached-manifest contract

### 3.1 No native PPS ingestion or redistribution

ARS V1 accepts only an already prepared canonical-AST JSON snapshot from a local
path. It contains no parser, converter, downloader, URL option, API client, or
native importer for PPS syntax. The repository carries no PPS fingerprint content.
Hermetic fixtures use invented, license-clear synthetic phrases and may not be
described as PPS coverage.

The user is responsible for lawfully preparing any real snapshot outside ARS. V1
supports exactly two supply modes:

- `user_supplied`: a local snapshot that ARS neither vendors nor
  republishes; and
- `synthetic_fixture`: repository-owned invented test content.

Adding vendored third-party content, a fetch-at-run path, or a native source-format
importer requires a new design version plus an in-repository license or written
permission record. Public visibility alone is not redistribution authority.

### 3.2 Exact-byte binding

Every snapshot travels with a separate strict-JSON manifest. The manifest schema is
`tortured-phrase-snapshot-manifest/1.0` and is closed recursively. Its exact field
shape is:

```text
schema_version
snapshot_id
source {
  name
  version
  as_of
  locator
}
supply_mode
snapshot_schema_version
snapshot_sha256
grammar_profile = ars-tortured-phrase-canonical-ast/1.0
normalizer_profile = ars-nfkc-casefold-token/1.0
preprocessor {
  name
  version
  native_grammar
  reduction_notes
}
unsupported_rule_count
rule_count
rights {
  basis
  redistribution_status
  reference
  user_declaration
}
```

`snapshot_sha256` is SHA-256 over the exact raw snapshot bytes, before decoding,
newline conversion, JSON parsing, key sorting, or serialization. The matcher validates
this binding before it reads any rule content. It then parses both files as strict
UTF-8 without a BOM,
rejecting duplicate decoded keys, non-finite numbers, invalid Unicode, unknown
fields, and folded near-miss version markers. JSON reserialization is never a
substitute for the raw-byte hash.

`source.locator` is provenance text and is never dereferenced. `source.as_of` is an
explicit session-held ISO date (`YYYY-MM-DD`), never a file time or clock read.
`snapshot_schema_version`, `grammar_profile`, `normalizer_profile`, `snapshot_id`,
and `rule_count` must equal the corresponding values in the exact snapshot.
`preprocessor.native_grammar` is a nullable bounded grammar-profile string and
`reduction_notes` is an array of bounded strings; together they disclose what
external source grammar, if any, was reduced into the canonical AST. They do not
activate an ARS importer. `unsupported_rule_count` is top-level and must be zero for
a checked run.

`rights.basis`, `rights.redistribution_status`, `rights.reference`, and
`rights.user_declaration` travel together. The repository fixture uses exactly
`basis: synthetic_fixture`, `redistribution_status: permitted`, `reference: null`,
and `user_declaration: null`; its `preprocessor.native_grammar` is
`synthetic-canonical-ast/1.0`. The closed `basis` values are
`synthetic_fixture`, `user_declared_authorized`, `written_permission`, and
`unresolved`; redistribution is `permitted`, `not_permitted`, or `unresolved`.
`user_declared_authorized` requires a non-empty user declaration;
`written_permission` requires a non-empty reference; and `unresolved` requires
unresolved redistribution status. A session-only user snapshot may be checked while
declaring no redistribution authority, and is never copied into the repository. #660
itself vendors no third-party content. The manifest records a claim and its reference;
it does not manufacture legal authority.

The report records both the raw snapshot hash and the raw detached-manifest hash.
A manifest is not proof that the supplied snapshot is a complete or authoritative
copy of any external list. It establishes only which exact bytes ARS checked.

All rules in a snapshot must validate. An unknown operator, invalid node, duplicate
rule id, rule-count mismatch, unsupported source reduction, or manifest mismatch
rejects the entire snapshot before matching. ARS never drops individual rules and
then reports the remainder as a checked list.

## 4. Canonical pattern AST

### 4.1 Closed rule shape

Each snapshot contains a lexically unique ASCII `rule_id`, one positive expression,
and a rule-level `exclude_if` array. The canonical snapshot schema is the single
authority for the exact JSON member names and numeric bounds. The runtime must consume
that public representation directly; a private alternate AST shape is forbidden.
A schema/runtime integration guard and fixtures lock their agreement before any
snapshot hash is frozen.

The only expression operators in `ars-tortured-phrase-canonical-ast/1.0` are
`literal`, `all`, `any`, and `near`. There is no native `not` node. Source-level negation may be
represented only by the rule-level, segment-scoped `exclude_if` reduction below.
Any source rule that cannot be represented without changing its semantics must be
reported through nonzero `unsupported_rule_count`; such a snapshot cannot authorize a
checked run. ARS itself makes no completeness claim.

Runtime work is closed and bounded before matching: at most 512 rules, 12 AST levels,
64 AST nodes per rule, eight normalized tokens per literal, 512 witnesses per node,
100,000 witness combinations per node, 4,096 parser intervals, 4,096 output segments,
`MAX_PARSE_WORK_UNITS = 100_000` shared across every parser opener, closer,
context candidate, and excluded candidate in the complete document,
100,000 rule-by-segment evaluations, a shared 5,000,000-unit literal/composition/
exclusion work budget for the complete input artifact (including all corpus entries),
500,000 input tokens, a pre-normalization maximum of 4,096 raw code points per token,
and 4,096 persisted match rows. The raw-token ceiling is enforced while collecting
source code points, before NFKC/casefold can allocate an expanded normalized value.
Corpus admission additionally
freezes `MAX_CORPUS_ENTRIES = 512` and
`MAX_CORPUS_EXISTING_SIGNALS = 8192`, where the latter is the aggregate number of
pre-existing `bibliographic_integrity_signals[]` rows across the complete input
corpus. A schema-valid input at exactly either limit is not rejected by that
cardinality guard; `N+1` raises the resource-limit failure before the passport is
copied, any surface is matched, or any output write is attempted. The direct enricher
never mutates its input document. The CLI creates no output on either admission
failure and leaves a pre-existing output byte-identical.

Decoded JSON/YAML structure is also bounded before schema traversal or copying:
`MAX_STRUCTURE_DEPTH = 64` and `MAX_STRUCTURE_NODES = 200_000`. The strict JSON
loader and the direct passport enricher both apply the same iterative guard. Parser
recursion, depth `N+1`, node `N+1`, or a shared/recursive YAML alias is a command-level
resource/structure failure: it emits no traceback, creates no new output, and leaves
an existing output byte-identical.

Snapshot, manifest, draft, advisory output, and passport input/output bytes are
independently capped and every successful output is readable by the corresponding
validator under the same cap. Every parser helper enforces the interval ceiling while
collecting intervals, not after an unbounded temporary list is built. Crossing an
artifact-level matcher ceiling discards partial matches and produces the closed
degraded/unresolved resource-limit state; it can never retain the remaining subset
and report a checked zero-match result. Crossing a command-level corpus admission or
serialized-output ceiling instead aborts before atomic replacement, so no partial
passport is published.

When a loaded-snapshot scan nevertheless emits an artifact-level `degraded` result
(including parse, empty-input, or matcher-resource degradation), the CLI first writes
the complete replayable degraded artifact atomically and then exits 1. Corpus
enrichment follows the same rule if any newly projected current surface is degraded.
An intentional `not_checked` result, including a missing abstract or explicitly
omitted snapshot, is not relabelled as a command failure and may exit 0.

The schema-authoritative node serialization and semantics are:

- `literal` is `{op, value}`. `value` is a non-empty bounded literal; after §5
  normalization it must contain at least one token and matches one contiguous equal
  token sequence.
- `all` is `{op, terms, max_span_tokens}` with 2–8 recursive `terms`. Every term
  must have a witness in the same parsed segment. The minimal covering half-open
  token span of a combination must be no wider than `max_span_tokens`. Term order is
  not an ordering claim.
- `any` is `{op, alternatives}` with 2–8 recursive `alternatives`. Its witness set
  is the union of the alternative witness sets.
- `near` is `{op, left, right, max_gap_tokens, ordered}`. Both witnesses must occur
  in the same segment. Gap is the number of normalized tokens strictly between the
  half-open spans; overlap or contact has gap zero. A candidate is retained only when
  the gap is at most `max_gap_tokens`; when `ordered` is true, the complete left
  witness must precede the right witness. The combined witness is the minimal
  covering window.

All AST objects are closed. Empty `all`/`any`, a literal that normalizes to zero
tokens, an invalid token window, excessive recursion or witness expansion caught by
the documented safety ceilings, or an unknown field rejects the whole snapshot.

### 4.2 Segment-scoped exclusion

`exclude_if`, when present, contains 1–8 rule-level items of exact shape
`{expression, within_tokens}`. `expression` is a positive recursive AST; an exclusion
cannot contain another exclusion. A candidate positive witness is suppressed only
when an exclusion witness is in the exact same parsed segment and its token gap from
the candidate is at most `within_tokens`. An exclusion in another paragraph, quote,
reference entry, abstract, title, or file has no effect.

This is the only V1 negation semantics. It is intentionally narrower than an
unbounded document-level NOT. Snapshot preparation must reject, not approximate, a
source expression whose negation scope cannot be represented this way.

### 4.3 Witnesses, overlaps, and counts

Every witness carries the input artifact id, surface, segment id and class,
half-open normalized-token span, half-open raw Unicode-code-point and UTF-8 byte
spans, rule id, and SHA-256 of the exact matched raw bytes. Raw spans always point
into the original unmodified input; normalized text is never written back. Any
human-readable evidence excerpt is bounded to at most 25 whitespace-delimited words
and 1,000 Unicode code points; longer witnesses fail closed rather than truncate
replay evidence.

After exclusions:

1. duplicate witnesses with the same `(rule_id, segment_id, byte_start, byte_end)`
   collapse;
2. `rule_match_count` counts the remaining unique rule witnesses;
3. overlapping or identical witnesses within one segment form a connected overlap
   component; and
4. `unique_instance_count` counts those components. Its representative is selected by
   earliest byte start, then longest byte span, then lexical rule id.

Adjacent non-overlapping spans are separate instances. Repeated occurrences at
different spans are separate instances. Reports always include both counts so a
single phrase matched by multiple rules cannot masquerade as repeated prose, while
genuine repetition remains visible. Counts are not severity tiers.

## 5. Text normalization and token boundaries

The matcher consumes exact raw UTF-8 bytes and retains their SHA-256 before any
transformation. It decodes strictly, rejects a BOM and isolated carriage returns,
and recognizes LF and CRLF line endings without rewriting the stored input.

Normalization is segment-local and read-only:

1. recognize the explicit Markdown or LaTeX structure under §6;
2. join a discretionary line-wrap hyphen only for `letter + '-' + newline + letter`
   inside the same scannable segment, retaining a map to the full raw span;
3. remove U+00AD SOFT HYPHEN only when it joins word characters, joining those
   characters into one token while retaining the full raw-span mapping; otherwise it
   is a separator;
4. split at whitespace, punctuation, symbols, controls, and format characters;
   dash-punctuation characters are separators except for the line-wrap rule above;
5. form tokens from maximal runs beginning with a Unicode Letter or Number and
   followed by Letters, Numbers, or Marks; and
6. apply Unicode NFKC and Unicode casefold independently to each token.

The same function normalizes AST literals and input tokens. Empty normalized tokens
are rejected in the AST and ignored as separators in input. Ordinary hyphens do not
join words, zero-width format characters do not fuse tokens, and matching never uses
locale, filesystem encoding, regular-expression locale state, or an ambient clock.

Token equality is exact after this pipeline. Substring-inside-token matching,
stemming, lemmatization, edit distance, semantic similarity, and language-model
classification are out of scope.

## 6. Markdown and LaTeX segmentation

The caller must pass `--format markdown` or `--format latex`; format guessing is
forbidden. Parsing produces stable, ordered segments with one of these closed
contexts:

```text
author_prose
quote
cited_title
reference_entry
code_or_verbatim
unknown
cited_abstract
```

Every context remains scannable so a parser classification does not silently erase a
list observation. Context changes only the disposition: `author_prose` asks for
review with no automatic rewrite; quote, cited-title, reference and code/verbatim
contexts are preserved verbatim; a cited abstract routes to cited-source review.
An `unknown` context is reported explicitly and never gains a rewrite suggestion.
Malformed structure that prevents complete segmentation makes the artifact-level
check `degraded/unresolved`; a degraded artifact cannot emit a zero-match statement.

The Markdown subset recognizes fenced and inline code, block-quote lines,
HTML-comment spans, DOI-link title text, and a reference section introduced by the
closed ATX heading vocabulary `References`, `Bibliography`, or `Works Cited`.
Dollar and inline-code delimiters preceded by an odd run of backslashes are literal;
an even run leaves the delimiter active. The same parity rule applies to LaTeX dollar
math and percent comments, so escaped literal syntax never creates a false
`unknown` segment.
Within that recognized section, every non-empty physical reference line begins a new
exclusion-scope segment. The LaTeX `thebibliography` context similarly begins a new
exclusion-scope segment at each `\bibitem`. This conservative rule prevents an
exclusion phrase in one reference entry from suppressing a hit in another; it does not
claim full citation parsing.
Everything else—including ordinary paragraphs, ATX/Setext headings, YAML front
matter, ordinary links, reference definitions outside the recognized section, and
raw HTML—is scanned conservatively as `author_prose`; V1 does not claim to parse
those constructs. An unclosed fence, inline-code delimiter, or HTML comment becomes
`unknown` and degrades the artifact-level result.

The LaTeX subset recognizes comments; `verbatim`, `lstlisting`, and `minted`;
`quote`/`quotation`; `thebibliography`; `\verb`; `\(...\)`, `\[...\]`, and dollar
math. Text commands and other macro bytes remain scannable as `author_prose` rather
than being interpreted. An unclosed recognized environment, delimiter, or `\verb`
becomes `unknown`; V1 does not claim complete TeX expansion or brace validation.
External `.bib` content is never dereferenced by this parser; cited titles come from
the structured corpus surface instead.

Opaque constructs are lexed strictly in source order: after the earliest eligible
opener is selected, opener-like bytes inside that interval cannot consume a closer
belonging to a later construct. Contextual quote and DOI-title recognizers likewise
cannot start inside, or pair across, an opaque interval. Fixed-cost opener scans and
monotonic delimiter cursors replace retrying backreference searches; candidate
collection fails at the parser-interval ceiling. `\verb*` is an explicit recognized
variant, while longer control words such as `\verbose` and `\verbatim` remain prose;
a bare `\verb` without a legal delimiter becomes `unknown`. Same-name nested
`quote`/`quotation` environments remain one protected outer quote interval.
Opaque membership uses binary search over sorted non-overlapping intervals; ignored
or unmatched context tokens still consume the same document-wide parser-work budget,
so exclusion checks cannot multiply candidate count by interval count without hitting
a declared ceiling.

Matches in manuscript prose receive
`review_author_prose_no_automatic_rewrite`. Matches in quotes, cited-title text,
reference entries, code and verbatim contexts receive
`preserve_verbatim_review_context`; the separate corpus title row supplies the
cited-source route. Unknown context receives `review_unknown_no_automatic_rewrite`.
No disposition contains replacement text. A cited title remains byte-for-byte
unchanged even when its corpus title row is `detected`.

## 7. Phase 1 — matcher, provenance, and synthetic seeds

Phase 1 implements only the pure local substrate:

- closed detached-manifest and AST snapshot schemas;
- exact-byte manifest validation;
- Markdown/LaTeX segmentation;
- normalization, matching, exclusion, overlap, and count functions;
- a CLI requiring explicit input, format, snapshot, manifest, and timestamps; and
- public, invented positive and negative conformance fixtures.

The seed set covers literal boundaries, Unicode compatibility/casefold behavior,
ordinary and line-wrap hyphens, soft hyphens, `all`, `any`, bounded `near`,
gap edges, segment-scoped exclusions, overlapping rules, repeated instances,
Markdown/LaTeX classification, malformed input, manifest mismatch, and unsupported
AST rejection.

These fixtures measure implementation conformance only. They do not estimate
real-world false-positive rate, false-negative rate, precision, recall, list
coverage, contextual validity, or publisher screening behavior. Their expected
results are hand-authored mechanical expectations, not judge labels.

Phase 1 neither emits the own-draft advisory nor writes corpus rows. A Phase-1-only
change references #660 but cannot close it.

## 8. Phase 2 — own-draft advisory

### 8.1 Machine artifact

Phase 2 adds a recursively closed `tortured-phrase-advisory/1.0` artifact. Its
normative schema groups exact raw input/snapshot/manifest/timestamp bindings under
`input_binding`, keeps the closed status/finding/reason-code state, retains all match
records and context counts, and includes a self-hash. The following semantic values
are immutable:

```text
schema_version = tortured-phrase-advisory/1.0
layer = HEURISTIC-ADVISORY
evaluation_status = UNMEASURED
check_status
finding
matches
counts (including every match record and unique textual instances)
boundary
```

The complete machine artifact retains every match and the closed segment/context
coverage counts used by the reducer. Exact source and snapshot replay reconstructs
the underlying segment partition. It is an
advisory transcript, not a score or submission gate. `evaluation_status` cannot be
promoted by passing synthetic tests.

An empty or whitespace-only draft is `degraded/unresolved` with `DOCUMENT_EMPTY`;
it is never represented as a checked zero-match surface.

### 8.2 Pipeline placement

In the full pipeline, the orchestrator runs the checker on the exact accepted working
draft after the final integrity pass and immediately before Stage 5 conversion. In
standalone `academic-paper` formatting, it runs on the exact format-conversion input.
The formatter receives the already validated artifact and only renders it; it does
not re-run matching, infer context, alter counts, or rewrite prose.

A detected, not-checked, or degraded result remains advisory and does not add a
terminal policy or bypass the existing mandatory Stage-5 confirmation. The user may
choose to revise, preserve, or proceed. Any revision creates new input bytes and
requires a new check with new explicit timestamps before the result may be called
current.

Phase 2 does not write cited-source rows. A Phase-2-only change references #660 but
cannot close it.

## 9. One-page bounded human renderer

The own-draft #660 match-detail renderer is fixed to at most 25 match rows. There is
no `--all`, limit override, environment variable, configuration key, or alternate
unbounded human-rendering path. There is exactly one rendered page: no `--page`,
`--page-size`, cursor, next-page token, or repeated pagination path may expose the
omitted rows. CLI parsing must reject `--all`, `--page`, and `--page-size` as unknown
options.

Rows are selected from the canonical machine order: raw code-point start, raw
code-point end, lexical rule id, then segment id. The renderer reports total
`unique_instance_count`, `rule_match_count`, shown count, and omitted count, and
points to the complete machine JSON when rows are
omitted. It escapes Markdown table delimiters, line breaks, and control characters;
it never interpolates a match as executable Markdown or LaTeX.

The cap applies to own-draft detail, not to the canonical #678 advisory table: every
corpus signal row, including `not_checked` abstract rows, remains visible there. The
aggregate table projects at most three bounded match witnesses inside each v1.2 row
and reports the number of omitted machine witnesses; that per-row projection cannot
hide the row's status or counts.

## 10. Phase 3 — cited-source integration

Phase 3 adds the v1.2 carrier profile and a pure producer that scans only the exact
local `literature_corpus[].title` and optional `.abstract` strings. It makes no API
call and does not dereference `source_pointer`.

The required `tortured_phrase_context` records the exact closed shape:

```text
layer = HEURISTIC-ADVISORY
evaluation_status = UNMEASURED
surface = cited_title | cited_abstract
surface_binding { content_sha256, content_utf8_bytes }
snapshot {
  status, reason_code, snapshot_sha256, manifest_sha256, snapshot_id,
  source, supply_mode, snapshot_schema_version, grammar_profile,
  normalizer_profile, unicode_data_version, rule_count,
  unsupported_rule_count, rights
}
reason_code
counts { rules_evaluated, matched_rule_count, rule_match_count,
         unique_instance_count, segments_total, unknown_segments,
         matches_by_context }
matches
boundary
```

The two `surface_binding` members are non-null only for a present, non-whitespace
surface. Checked rows bind the versioned grammar/normalizer profiles, Unicode data
version, exact snapshot and manifest hashes, and explicit timestamps; the integration
guard additionally freezes the shipped runtime bytes. Detected rows carry structured
match witnesses; checked
not-detected rows carry a list-observation evidence item; absent/empty/not-supplied
and degraded rows carry a typed degradation item. Evidence never embeds a full
abstract: a witness contains its bounded raw span/hash and rule id, while the local
machine artifact remains the complete replay authority.

`unicode_data_version` records the producer interpreter's Unicode database; it is
not rewritten to the validator's local version. The shipped v1.2 fixtures freeze
their generation provenance at `14.0.0`. A validator running another Unicode version
must validate that frozen value and compare the remaining replay projection exactly,
not relabel the stored artifact with its ambient version. A newly produced row still
records its actual runtime version, and byte-exact reproduction of that row requires
the same recorded Unicode data version.

The producer is idempotent by the citation×surface current-row rule in §2.2.
Re-running on unchanged bytes and identical explicit timestamps yields byte-identical
output. Changed surface or snapshot bytes change the hash-bound id and atomically
supersede the one prior current row in the returned copy. A timestamp-only change
updates the row but does not create history. Before supersession, an existing current
row must pass its entry-independent schema, id/hash, count, state, provenance, and
match self-binding checks and still join the containing citation key and source
pointer. The old surface-content hash may differ from newly supplied surface bytes;
that difference is the legitimate supersession case. Duplicate current rows,
duplicate ids, internally stale bindings, or a self-bound surface/id mismatch fail
closed rather than using first- or last-write-wins.

Formatter integration renders the fixed vocabulary from §1, exact per-surface
status, both counts, snapshot version/date/hash, explicit times, and unresolved
coverage. It composes with retraction and every other #678 row without minting a
marker or policy result.

Only Phase 3 completes the two-surface implementation. That implementation PR keeps
#660 open; after the exact accepted commit reaches `main`, the separate preregistered
mechanical-conformance PR may close #660 only when every row of §13 is satisfied.

## 11. Explicit time and reproducibility contract

Every producer requires schema-valid RFC 3339 timestamps as explicit arguments.
Fractional seconds, when present, contain one through six digits so ordering is
lossless in the shared runtime. Required timestamp fields have no default. The runtime must not read system time,
monotonic time as a substitute, timezone, file modification time, Git author/commit
time, network time, or UUID time.

At minimum the invocation supplies `--checked-at` and `--recorded-at`.
`source.as_of` (an ISO date) and source version are explicit fields in the already
supplied, validated detached manifest; the runtime never synthesizes either. Missing
or malformed timestamps fail before a checked result is emitted.

Hermetic clock-mutation tests monkeypatch or deny common clock functions and verify
that output identity depends only on explicit inputs. Two runs over identical raw
bytes, runtime version, and explicit timestamps must produce identical canonical
JSON bytes.

## 12. Measurement and claim ceiling

No model, API, human judge, model judge, or contextual classifier is run for #660.
The repository seed set is public synthetic conformance material, not a held-out
effectiveness evaluation. Phase acceptance uses ordinary deterministic tests and
keeps both advisory surfaces `UNMEASURED` with respect to contextual validity.

No #654 measurement row may be manufactured in the implementation PR. That PR lands
the synthetic suite, frozen expectations, measurement plan, and registry entry, but
publishes no scored envelope. The closure PR adds a `mechanical_match` report only
after the exact suite and matcher commit exists on `main`, so
`subject.config.suite_commit` and `preregistration.frozen_commit` can name a real
40-hex main-history object and all plan, execution-manifest, and raw-output
references can resolve. That closure row uses zero judges,
`judge_plan.exception: mechanical_suite`, no adjudication, and a headline explicitly
limited to synthetic conformance. It cannot retrospectively authorize real-world
precision/recall, contextual validity, source cleanliness, or publisher acceptance.

The mechanical #654 row is required before #660 closes. It scores the public
synthetic positive-match and negative-non-match expectations only; those labels are
grammar-conformance fixtures, not measured contextual false-positive or
false-negative rates. Introducing a judged contextual layer would reopen design and
invoke the applicable #654 judge, blinding, preregistration, and raw-output
requirements.

## 13. Closure and acceptance matrix

The design document itself removes the design ambiguity but does not close the issue.
The `status/needs-design` label may be removed after this frozen design is accepted.
Closing keywords are reserved for the change that can demonstrate every row below.

| Requirement | Frozen proof required before closure | Phase |
|---|---|---|
| Shared authority | v1.2 profile extends #678; v1.0/v1.1 compatibility and retraction identity tests pass; no new corpus carrier | 3 |
| Snapshot rights | no PPS content/importer/fetcher; exact-byte detached manifest; only user-supplied or synthetic modes | 1 |
| Grammar | closed `literal`/`all`/`any`/`near` AST and rule-level segment-scoped `exclude_if`; unsupported input fails closed | 1 |
| Normalization | UTF-8/BOM, NFKC/casefold, token, Unicode, hyphenation, raw-span and overlap/count semantics are mutation-tested | 1 |
| Parsing | explicit Markdown/LaTeX modes classify prose, quotes, cited titles, references and unsupported coverage | 1 |
| Public seed | invented positive/negative fixtures cover all grammar and normalization branches; only synthetic conformance is claimed | 1 |
| Mechanical measurement | a post-merge `heldout-measurement/1.1` `mechanical_match` row resolves the precommitted plan, exact main-history suite commit, write-once execution manifest, and retained raw transcript; zero judges and no contextual-accuracy claim | closure |
| Own-draft surface | closed HEURISTIC-ADVISORY/UNMEASURED artifact scans exact final input and never rewrites or gates | 2 |
| Preservation/routing | quotes and cited/reference titles remain verbatim; cited-title matches route to the corpus advisory surface | 2/3 |
| Cited-source surface | independent title and abstract rows; absent/empty abstract is explicit `not_checked/unresolved`; manual entries are covered | 3 |
| Epistemic separation | deterministic runtime is not relabelled deterministic fact; every row is HEURISTIC-INDICATOR; contextual judgment is `not_performed` | 1/2/3 |
| Counts and tiers | `unique_instance_count` and `rule_match_count` always render; no severity tier exists | 1/2/3 |
| Provenance | every checked result carries snapshot version/date/raw hash, manifest hash, exact surface/input hash, and explicit times | 1/2/3 |
| No ambient execution | no network/model/API/judge/clock path; hermetic integration guards and clock mutations pass | 1/2/3 |
| Bounded rendering | own-draft detail has one fixed page with at most 25 matches and no traversal flags; the complete canonical corpus table retains every signal row and bounds evidence per row | 2/3 |
| Composition | one complete Bibliographic Integrity Advisories section; lexical rows; no advisory marker, terminal policy, or formatter re-judgment | 3 |
| Claim vocabulary | positive, zero, missing and degraded wording matches §1; banned origin/contamination/clean claims are mutation-tested | 2/3 |
| Consumer wiring | bibliography producer, pipeline orchestrator, formatter, protocol docs, fixtures, integration checker and CI manifest agree | 3 |
| Validation | focused tests, adjacent #651/#678 carrier regressions, schemas, integration guards, mirror equality where applicable, lint, compile and diff checks are green | 3 |

Phase 1, Phase 2, and Phase 3 implementation changes use `Refs #660`. The subsequent
mechanical-measurement PR may use `Closes #660` only if its exact implementation
commit is already reachable on `main` and the complete matrix is green in that exact
branch. The three implementation phases may be separate PRs or separately reviewable
commits in one PR, but no phase may be omitted or treated as implied by the #678
scaffold. After merge, closure is confirmed from GitHub rather than inferred from a
commit message.

## 14. Non-goals and future changes

V1 explicitly does not provide:

- AI-text detection or authorship/origin inference;
- misconduct, paper-mill, contamination, quality, or publishability findings;
- a clean-text or clean-source certificate;
- contextual false-positive classification;
- automatic replacement or rewrite suggestions;
- severity tiers or terminal policy;
- a native PPS parser, list downloader, redistributed PPS content, or list-completeness
  claim;
- full-text cited-source screening;
- a model/API/judge run or real-world accuracy estimate; or
- an unbounded human renderer.

Changing the AST operators, exclusion scope, normalization, overlap/count rule,
surface unit, epistemic label, output vocabulary, timestamp source, renderer cap, or
claim ceiling requires a new contract version and updated mutation tests. It may not
be introduced as an undocumented implementation detail.
