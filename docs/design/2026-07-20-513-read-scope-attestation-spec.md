# #513 — `read_scope` honest-coverage attestation + anchor-aware finalizer promotion

**Date:** 2026-07-20 · **Issue:** #513 · **Status:** implemented in the same PR

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

Ledger entries gain an optional `read_scope` object:

```yaml
human_read:
  - citation_key: smith2024
    marked_at: "2026-07-20T04:00:00Z"
    read_scope:            # optional — absent on legacy and scope-less marks
      level: sections      # full_text | sections | abstract_only | toc_only | unknown
      locators:            # only meaningful (and only accepted) with level: sections
        - "pp. 10-24"
        - "section 3"
      note: "methods + results read closely; discussion skimmed"
```

`/ars-mark-read` gains optional arguments, all attestation-only (declaration, never
inference):

- `--scope <level>` — closed enum above. Absent ⇒ no `read_scope` written; consumers
  treat absence as `unknown`. Nothing is fabricated or backfilled.
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
(`additionalProperties: false` throughout, closed `level` enum, registered in
`shared/contracts/README.md`). The ledger stays adapter-free and user-owned; the schema
exists for audit/debugging and test-time validation — `ars_mark_read.py` itself stays
dependency-light (no jsonschema import at runtime).

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
| absent / `unknown` | promotes (legacy marks keep their pre-#513 behavior — the optional field must not impose a de-facto migration) |
| `full_text` | promotes |
| `abstract_only` / `toc_only` | does NOT promote — the marker resolves to `LOW-WARN-PARTIAL-COVERAGE` and the per-section checklist entry carries an explicit coverage note (e.g. `read_scope abstract_only does not cover anchor page:12`) |
| `sections` | promotes ONLY when the anchor (`page` / `section` / `paragraph`) falls unambiguously within a declared locator; ambiguity or no match ⇒ `LOW-WARN-PARTIAL-COVERAGE` + coverage note. `quote` anchors promote only under `full_text` / `unknown` — with partial coverage the finalizer cannot vouch that the quoted passage lies in a read section |

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
clear containment match.

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
- Mandatory migration — legacy marks mean `unknown` and keep their behavior.
- A `source_sha256` join field toward the #512 preflight sidecar. The #512 spec names
  the sidecar `sha256` as the natural future join key, but #513's scope is the
  human-attestation channel; adding a hash field with no wired consumer would be the
  same dead-metadata risk this issue exists to avoid. The schema is additive, so the
  field can land with its consumer.

## Test plan

- `scripts/test_ars_mark_read.py`: scope happy path per level; locators/note persisted;
  invalid level / `--locator` without `sections` / `--note` without `--scope` /
  attestation args with `--unmark` all rejected batch-wide with canonical errors;
  scope-less marks write no `read_scope` key (byte-shape backward compat); produced
  ledgers validate against the new schema; legacy ledger entries untouched by new marks.
- `tests/test_mark_read_args.py`: dispatch-level pass-through of the new flags.
- Lints: `check_v3_6_8_*` all stay green; `check_pipeline_boundary_semantics.py` hash
  re-pinned.
