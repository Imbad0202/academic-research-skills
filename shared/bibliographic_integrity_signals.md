# Bibliographic Integrity Signal Contract

`shared/contracts/passport/bibliographic_integrity_signal.schema.json` is the
single schema authority for bibliographic-integrity observations carried in
`literature_corpus[].bibliographic_integrity_signals[]`. Version 1.0 is the
additive migration carrier. Version 1.1 is the #651 retraction-status policy
cutover. Both preserve the one-advisory-token reference-marker grammar.
Version 1.2 is the #660 tortured-phrase advisory profile; it is additive and
does not change the validity of shipped canonical v1.0/v1.1 fixtures or producer
outputs, nor their policy meaning. Its signal-type invariant intentionally rejects
noncanonical, previously underconstrained tortured-phrase mutations that claimed
deterministic or terminal authority.

## Epistemic boundary

The carrier separates three claims that must not be collapsed:

| `epistemic_class` | Required label | What it establishes |
|---|---|---|
| `deterministic_fact` | `RESOLVER-OR-LIST-OBSERVATION` | What a named resolver or list returned at a recorded time; not whether the cited work is ultimately genuine, retracted, or sound. |
| `heuristic_advisory` | `HEURISTIC-INDICATOR` | A rule or model matched; never a factual finding by itself. |
| `process_attestation` | `CHECK-EXECUTION-ATTESTATION` | A check was reportedly run; it is not the result of that check. |

`check_status` and `finding` are independent. `not_checked`, `unknown`, and
`degraded` require `finding: unresolved`; none may be rendered or interpreted
as clean. A legacy `retraction_check: true` therefore migrates only to a
checked execution attestation with an unresolved finding. It never becomes
`not_detected`.

## Display and policy ownership

Every v1 signal is rendered as one row in the single
`Bibliographic Integrity Advisories` section of `provenance_summary.md`.
Rows compose by `signal_id` in lexical order and show the signal type,
epistemic label, check status, finding, affected citation/claims, provenance,
and freshness. The formatter must render `not_checked`, `unknown`, and
`degraded`, or any signal whose `finding` is `unresolved`, as **NOT CLEAN —
UNRESOLVED**. The rendered table carries the resolver/list name, version and
hash, checked/recorded/stale timestamps, freshness, source pointer, and affected
claims so an advisory never loses its provenance in projection.

`display.marker_token` is always `null`. New retraction and tortured-phrase
signals do not mint another `<!--ref:...-->` advisory token. During migration,
the existing finalizer continues to derive its one recognized
`CONTAMINATED-*` token from the legacy `contamination_signals` fields. Thus
multiple new signals compose in the provenance summary without changing or
overflowing the marker grammar.

`terminal_policy` records eligibility and the policy owner; it does not enact
policy. Only the citation finalizer may evaluate an eligible signal. Version
1.0 migrations set `eligible: false`, `policy_key: null`, and
`current_effect: advisory_only`. A v1.1 retraction row is eligible only when
its effective status is current, undisputed `retracted` and the deterministic
declared-legitimate exception did not fire. The finalizer then evaluates the
explicit `terminal_policies.retraction` choice. Adding a signal never silently
promotes it to `HIGH-BLOCK`.

## Tortured-phrase advisory profile (v1.2 / #660)

Version 1.2 carries one current `tortured_phrase_match` row per
`(citation_key, cited_title|cited_abstract)` surface. It is always
`heuristic_advisory` / `HEURISTIC-INDICATOR`; its closed context remains
`layer: HEURISTIC-ADVISORY` and `evaluation_status: UNMEASURED`. A detected
row means only **phrase-list match requiring review**. A checked zero-match row
means only that no phrase-list match was observed on that exact checked
surface; absence is not a clean certification. It never establishes AI,
author, paper-mill, misconduct, or other origin, and it carries no precision,
recall, false-positive, false-negative, coverage, or publisher-acceptance
claim.

The local producer consumes only an explicitly named canonical snapshot and
detached manifest. The manifest binds the exact raw UTF-8 snapshot bytes by
SHA-256 and declares either `user_supplied` or `synthetic_fixture` supply;
ARS ships no native PPS parser/importer, fetch path, or redistributed PPS list
content. Matching reads no model, external API, human/model judge, system
clock, file time, or network time. Required timestamps are explicit inputs.

Each invoked corpus check keeps title and abstract coverage separate. A valid
title is checked independently. A missing abstract remains an explicit
`not_checked` / `unresolved` row with reason `ABSTRACT_MISSING`, while a present
whitespace-only abstract uses `ABSTRACT_EMPTY`; neither state can be
folded into the title result or omitted. Manual corpus entries have no
exemption. Every row binds the exact local surface bytes plus snapshot and
manifest hashes. The producer returns a new passport copy and never rewrites a
source title, abstract, citation, or input passport in place.

All v1.2 rows compose in the existing single `Bibliographic Integrity
Advisories` section. `display.marker_token` is `null`,
`terminal_policy.eligible` is `false`, and neither the finalizer nor formatter
may mint a marker, gate, terminal promotion, suggested replacement, or
automatic rewrite from the row. The separate own-draft carrier is
`tortured-phrase-advisory/1.0`; it has the same
`HEURISTIC-ADVISORY` / `UNMEASURED` boundary and is not a corpus authority.

## Retraction authority cutover (v1.1 / #651)

The v1.1 `retraction_status` row is authoritative for retraction status. It
records OpenAlex and Crossref observations separately, including disagreement,
reinstatement, event dates, source-acquisition timing, load-bearing claim join,
and a strictly mechanical author-declaration + notice-cited exception. Missing
dates, reasons, or resolver results stay explicit and are never inferred.

The legacy `retraction_check` boolean remains readable for one compatibility
window as a process attestation only. New retraction-status producers do not
write it, and neither the finalizer nor the ethics agent may use it as a status
or terminality input. The ethics agent points to the canonical row; the
finalizer owns advisory/strict evaluation.

Retraction status uses the separate `retraction_status_cache_v1` namespace.
Cached observations retain `checked_at` and typed unknown/degraded states. A
row older than 30 days is stale and must be revalidated before strict
promotion; stale never means clean.

## Pinned migration and deprecation path

1. **Read compatibility:** consumers continue to read
   `contamination_signals`, `contamination_signal_omissions`,
   `contamination_signals_backfilled_at`, and source-object
   `retraction_check` exactly as before.
2. **Dual write:** updated producers append canonical v1 records while still
   writing the legacy fields required by current marker and terminal-policy
   behavior. `scripts/bibliographic_integrity_signals.py` defines the
   deterministic legacy-to-v1 projection.
3. **Display cutover:** the formatter renders the canonical array into the
   one provenance-summary section. It does not derive new marker tokens.
4. **Policy cutover:** #651 cuts over only `retraction_status` through v1.1 and
   `terminal_policies.retraction`. Other v1.0 signal types remain advisory and
   keep their existing legacy-policy carriers.
5. **Removal (future major version):** legacy fields may be removed only after
   one released compatibility window following policy cutover. Until then
   they are deprecated write targets, not invalid inputs.

`contamination_signal_omissions.<resolver>: api_degraded` migrates to a
resolver-specific record with `check_status: degraded` and
`finding: unresolved`. Absence of both a legacy result and omission remains
absence/unknown; it is never synthesized as a clean result. Existing
`provenance_summary.md` text is an output projection and is never parsed back
as evidence.

The v1.2 profile is not a migration of the older tortured-phrase scaffold.
Existing v1.0 heuristic rows remain readable with their original meaning, but
cannot be treated as completed title/abstract checks.
