# #513 — `read_scope` honest-coverage attestation + anchor-aware finalizer promotion

**Date:** 2026-07-20 · **Issue:** #513 · **Status:** implemented in the same PR

## #738 supersession amendment (2026-08-15)

This amendment is the current authority wherever it conflicts with the original
#513 compatibility behavior below. New marks now require both
`attestation_type: USER_ATTESTED_READ` and an explicit `read_scope`; use
`level: unknown` when coverage cannot be stated. Legacy rows that omit both
fields remain parseable, but legacy absence and explicit `unknown` resolve to
`coverage_unknown` and can never promote an anchored citation to `ok`.

The current resolver strictly validates the closed ledger, paired attestation
type/scope, RFC3339 UTC event timestamps and ordering, and the closed anchor
enum. Page coverage requires an explicit `page`, `p.`, or `pp.` locator; a bare
number or `section <n>` cannot cover a page anchor. Its output is a transient
routing decision, not a persisted audit receipt, and must be recomputed from the
current ledger and exact anchor on each finalizer pass.

Finalizer routing is closed: `covered` is eligible for `ok` only after the
source matrix also permits it; active `partial_coverage`/`coverage_unknown`
becomes `LOW-WARN-PARTIAL-COVERAGE`; `not_attested`/`rescinded` remains plain
unacknowledged `LOW-WARN`; `ledger_invalid` blocks visibly; unresolved anchors
take the existing precedence-zero NO-LOCATOR route. All non-conflicting #513
placement, declaration-only, and corpus-ownership decisions remain in force.

## Problem

ARS records source possession, AI verification-against-original, and a binary human-read
mark — but nothing records **how much** of a source was actually read. A user who read
only the abstract is indistinguishable from one who read the whole paper, and the
Cite-Time Provenance Finalizer's LOW-WARN → `ok` promotion consumes the mark as a binary:
a TOC-only reading promotes a citation whose `page` anchor points at a chapter the user
never opened.

Placement constraint (verified in the #513 dual-track review): corpus entries are
adapter-owned and MUST NOT carry human-read state (v3.6.8 firm rule 3), so the peer
project's shape — a field on the bibliographic entry — is not available. The attestation
belongs on the **user-owned human-read ledger** (`<passport-stem>_human_read_log.yaml`).

Provenance: mechanism observed in kengo006/alexandria (mandatory note declaring actual
reading coverage); ranked P2 of three in the 2026-07-11 adoption review.

## Design

### Layer 1 — ledger field + CLI (`scripts/ars_mark_read.py`)

Current ledger entries carry a required `read_scope` object; omission remains
legal only on positively identified legacy rows:

```yaml
human_read:
  - citation_key: smith2024
    attestation_type: USER_ATTESTED_READ
    marked_at: "2026-07-20T04:00:00Z"
    read_scope:            # required now; absent only on legacy rows
      level: sections      # full_text | sections | abstract_only | toc_only | unknown
      locators:            # only meaningful (and only accepted) with level: sections
        - "pp. 10-24"
        - "section 3"
      note: "methods + results read closely; discussion skimmed"
```

`/ars-mark-read` uses attestation-only arguments (declaration, never inference):

- `--scope <level>` — closed enum above and required on every new mark. Use
  `unknown` when the user cannot specify coverage. Legacy absence is never
  fabricated or backfilled and remains non-promoting.
- `--locator <text>` — repeatable; **requires `--scope sections`** (locators name which
  sections/pages were read; with `full_text` they are redundant and with
  `abstract_only`/`toc_only` they contradict the level — a contradictory attestation is
  refused, not recorded).
- `--note <text>` — free text; requires `--scope` (a note is part of an attestation).
- `--scope`/`--locator`/`--note` are rejected with `--unmark` (rescinding takes no
  attestation).
- Batch semantics unchanged: one invocation's `read_scope` applies to every key in the
  batch; validation stays all-or-nothing.

Errors use the existing canonical `[ARS-MARK-READ ERROR: ...]` surface.

### Layer 2 — ledger sidecar schema

New `shared/contracts/passport/human_read_log.schema.json`, following the
`rejection_log.schema.json` / `version_records.schema.json` sidecar precedent
(`additionalProperties: false` throughout, closed `level` enum, paired current
attestation type/scope, RFC3339 UTC timestamp grammar, registered in
`shared/contracts/README.md`). The ledger stays adapter-free and user-owned;
`ars_mark_read.py` remains dependency-light, while the deterministic resolver
enforces the same closed shape and event-order invariants before routing.

### Layer 3 — anchor-aware finalizer promotion (prose, `pipeline_orchestrator_agent.md`)

The v3.7.1 finalizer block gains a read-scope-aware promotion paragraph (plain bold
paragraph, no nested heading — the `check_v3_6_8_cite_provenance_pipeline.py` block
extractor terminates at headings). The LOW-WARN → `ok` transition consults the mark's
`read_scope`:

The governing signal follows the existing latest-timestamped-event-wins rule (§3.6):
promotion is considered only when the slug's latest event overall is a mark — a latest
rescind keeps row 3 regardless of older non-rescinded marks — and the attestation
consulted is the one on that latest mark (codex r1: "most recent non-rescinded" would
have contradicted the settled precedence and resurrected rescinded promotions).

| `read_scope.level` | Promotion of the citation's anchor |
|---|---|
| absent on a legacy mark / explicit `unknown` | does NOT promote — resolves to `coverage_unknown` and the active declaration remains visibly acknowledged-partial |
| `full_text` | promotes |
| `abstract_only` / `toc_only` | does NOT promote — the marker resolves to `LOW-WARN-PARTIAL-COVERAGE` and the per-section checklist entry carries an explicit coverage note (e.g. `read_scope abstract_only does not cover anchor page:12`) |
| `sections` | promotes ONLY when the anchor (`page` / `section` / `paragraph`) falls unambiguously within a declared locator; ambiguity or no match ⇒ `LOW-WARN-PARTIAL-COVERAGE` + coverage note. Page anchors require an explicit page-prefixed locator. `quote` anchors promote only under `full_text` |

`LOW-WARN-PARTIAL-COVERAGE` (codex r1: a partial acknowledgment that left the plain
`LOW-WARN` marker was indistinguishable from an unacknowledged citation at the terminal
gate, forcing the formatter to either refuse an acknowledged mark or pass unacknowledged
ones) is a draft-visible acknowledged-partial state: same severity tier as `LOW-WARN`,
contamination suffixes attach identically, and the formatter passes it as an
acknowledged LOW-WARN variant with the coverage note surfaced — never refused, never a
new severity. The v3.7.3 ref-marker grammar (`[\w-]+` status tokens) admits it without
lint changes. The idempotency rule's evidence enumeration now names the governing
mark's attestation explicitly — a `read_scope` change between passes is an evidence
change and re-resolves the marker. The judgment "falls unambiguously within" is
conservative by instruction: locators are free text; the finalizer promotes only on a
clear containment match. #738 narrows this marker to an active mark whose state
is `partial_coverage` or `coverage_unknown`; no mark, a latest rescind, or an
invalid ledger can never borrow the acknowledged-partial marker.

CLI bounds (codex r1): `--locator` values 1-200 chars and `--note` 1-1000 chars are
enforced at write time — in lockstep with the sidecar schema — so the CLI can never
produce a ledger the committed schema rejects; presence checks use `is not None`, so an
explicitly supplied empty string is an invalid attestation argument, not an absent one.

### Doc surfaces updated in lockstep

`commands/ars-mark-read.md` (optional-arguments paragraph; pinned tokens preserved),
`academic-paper/agents/formatter_agent.md` LOW-WARN remediation line (mentions the scope
argument), and the #528 content lock on `pipeline_orchestrator_agent.md` re-pinned in
the same commit.

## Out of scope (deliberate, from the issue)

- Any new field on `literature_corpus[]` entries (adapter-owned; v3.6.5 consumer
  protocol).
- Adapter inference of reading depth — declaration-only.
- Mandatory migration — legacy rows remain readable, but their missing scope is
  explicitly `coverage_unknown` and no longer preserves the historical `ok`
  promotion.
- A `source_sha256` join field toward the #512 preflight sidecar. The #512 spec names
  the sidecar `sha256` as the natural future join key, but #513's scope is the
  human-attestation channel; adding a hash field with no wired consumer would be the
  same dead-metadata risk this issue exists to avoid. The schema is additive, so the
  field can land with its consumer.

## Test plan

- `scripts/test_ars_mark_read.py`: scope happy path per level; locators/note persisted;
  invalid level / `--locator` without `sections` / `--note` without `--scope` /
  attestation args with `--unmark` all rejected batch-wide with canonical errors;
  scope-less new marks rejected; produced ledgers validate against the schema;
  legacy ledger entries remain unchanged when a new scoped mark is appended.
- `scripts/test_human_read_attestation_resolver.py`: strict current-ledger and
  RFC3339 ordering mutations, duplicate keys, closed anchors, cross-kind/bare
  locator rejection, and end-to-end state-to-finalizer disposition mapping.
- `tests/test_mark_read_args.py`: dispatch-level pass-through of the new flags.
- Lints: `check_v3_6_8_*` all stay green; `check_pipeline_boundary_semantics.py` hash
  re-pinned.
