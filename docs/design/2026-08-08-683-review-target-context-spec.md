# #683 ReviewTargetContext and criteria-registry V1 specification

## Decision

V1 is a declaration-and-resolution contract, not a venue scraper and not a model-memory lookup.

1. The author supplies a closed `ReviewTargetDeclaration` containing the discipline axes, exact target venue/track/contribution type (or an explicit null venue), overlays, criterion-selection mode, authority precedence, and criteria as-of date.
2. A deterministic resolver matches that declaration against a versioned registry and emits a `ReviewTargetContext` whose selected criteria are pointers (`criterion_id`, version, criterion digest), not copied prose.
3. The resolver emits a Markdown Target Criteria Brief from those same pointers for Phase 0/1 use. It reads only the two explicitly named JSON inputs. Manuscripts, drafts, scores, reviewer outputs, and repository instructions are not accepted inputs.

The author remains authoritative. `selection_mode=all_applicable` is itself an explicit author choice; `selection_mode=explicit` rejects unknown or inapplicable ids instead of silently substituting alternatives.

## Artifacts

- `shared/contracts/review_target/review_target_declaration.schema.json` — author-owned input.
- `shared/contracts/review_target/criteria_registry.schema.json` — versioned registry.
- `shared/contracts/review_target/review_target_context.schema.json` — resolved pointer artifact.
- `shared/review_criteria_registry.json` — shipped field-general baseline only.
- `scripts/resolve_review_target_context.py` — stdlib-only validator, resolver, digest calculator, and brief renderer.

2026-08-24 addendum (#575): the preceding artifact description records the
2026-08-08 freeze. The live registry now also contains one bounded
source-backed proving set. See
`audits/575-source-backed-proving-set-2026-08-24.md` for its current scope,
source receipts, migration receipt, and no-coverage boundary.

## Axes and fallback

The target axes are independent:

- primary discipline, optional subfield, and zero or more additional disciplines;
- venue, exact track, and exact contribution type;
- zero or more reporting/design overlays.

When `venue=null`, `track` must also be null and the resolver emits `fallback_state=field_general`. It never invents a venue. When a venue is declared but no exact official venue × track × contribution-type criterion exists, the resolver may still emit applicable scientific-validity and reporting criteria, but emits `fallback_state=declared_target_unresolved`, `resolution_state=partial`, and an unresolved `venue_fit` row. A partial result never impersonates venue guidance.

An exact official match can still be advisory-only when every matching official criterion is stale or unverified. That state is `venue_exact_advisory`; it is distinct from both a current exact profile and no profile.

## Authority classes

The registry has four explicit partitions:

1. `official_venue_type`
2. `field_society_standard`
3. `reporting_design_overlay`
4. `broad_field_fallback`

Every criterion appears in exactly one partition and repeats its authority class on the row. Official venue criteria must declare non-wildcard venue, track, and contribution-type applicability. Field/society criteria must declare a discipline. Reporting/design criteria must declare an overlay. Broad fallback rows cannot claim venue authority.

The author supplies a unique rank for each class. Rank orders display and conflict review only; it does not delete lower-ranked applicable criteria. V1 has no adaptive numeric weights, and both declaration and resolved-context schemas reject undeclared weight fields.

## Provenance and freshness

Each criterion carries:

- stable id and explicit version;
- one of the three independent outcome dimensions (`scientific_validity`, `venue_fit`, `submission_readiness`);
- statement text stored only in the registry;
- source title, publisher/owner, URI, effective date, verification date, and freshness (`current`, `stale`, `unverified`);
- applicability and exclusions;
- declared blocking policy.

The resolved artifact carries a SHA-256 digest of each selected registry row. A criterion with `freshness != current` always resolves with `blocking_eligible=false`, even if the registry row's declared policy is `blocking_allowed`. The brief labels the reason. A not-yet-effective row is not applicable at the declaration's as-of date.

The shipped registry intentionally contains no real venue profile. Real venue/type rules require a separately reviewed, source-snapshotted registry update. Synthetic fixtures prove the exact-match mechanism without presenting fictional rules as authority.

2026-08-24 addendum (#575): the preceding paragraph is the frozen historical
state and rule. The separately reviewed proving-set update adds one real
venue/track/type profile. Its mutable MSR page is bound to a committed raw-body
receipt and a normalized semantic-pane SHA-256; the hash is carried in each
official criterion version. Immutable SIGSOFT commits have a separate
head-versus-pinned-blob receipt. The repository does not mirror source text
whose redistribution terms are unknown.

## Digest contract

`resolved_digest` is SHA-256 over canonical UTF-8 JSON (sorted keys, compact separators) containing:

- every target/discipline/overlay axis and criteria as-of date;
- the declared authority precedence;
- registry id/version;
- selected criterion id/version/content digest and derived blocking eligibility;
- parallel conflicts, fallback state, resolution state, and unresolved rows.

Confirmation timestamp is excluded because re-confirming the same profile should not change comparability. Any substantive target or selected-criterion change changes the digest. The whole-registry digest is recorded separately for provenance; unrelated registry additions do not change the resolved profile digest.

2026-08-24 migration clarification (#575): the final sentence applies within a
fixed registry id/version. A published registry release increments
`registry_version`, which is itself a frozen digest input and therefore rotates
`resolved_digest` even when the selected criterion pointers are unchanged. The
#575 release preserves the registry id lineage, records predecessor and
successor digests, and requires consumers to recompute and explicitly rebind;
an old context never silently acquires the new registry version.

## Interdisciplinary conflict handling

Criteria may name a `conflict_group`. When two or more applicable selected criteria share a group, the resolver emits all ids in `parallel_conflicts[]`. It never averages their text, severity, or authority. The brief shows the conflict explicitly. Resolution belongs to the author/reviewer workflow, not the resolver.

## Blind-safety boundary

- The declaration schema is closed and has no manuscript, abstract, score, finding, or reviewer-output field.
- The CLI opens only `--context` and `--registry` (plus explicitly requested output paths). It does not search the current directory.
- The resolved artifact contains criterion pointers and target metadata only.
- The Markdown brief obtains criterion prose from the registry, never from a manuscript.
- A regression test places a unique manuscript sentinel next to the inputs and proves it never enters either output.

This is a Phase 0/1 data boundary, not evidence that a model remains blind if a caller violates the dispatch contract. Structural dispatch isolation remains a separate runtime concern.

## Consumer boundary

#683 owns resolution only. Formative writing, the internal evaluator, and the external panel bind to the resulting `resolved_digest` under #684. They must consume the pointer artifact rather than copying criterion prose into three independent prompt sources.
