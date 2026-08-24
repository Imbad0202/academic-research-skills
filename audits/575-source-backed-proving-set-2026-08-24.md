# #575 source-backed proving-set audit — 2026-08-24

**Scope:** one bounded, real-source fixture for Software Engineering × MSR 2027
× Technical Papers × Full Paper, with the ACM SIGSOFT Repository Mining
Standard selected as an overlay.

**Result:** the live registry now exercises all four authority partitions with
three official venue/type rows, one field/society row, one reporting/design
overlay row, and the four retained broad fallbacks. This is an architecture
proving set, not a field, venue, or method coverage claim. It does not close
#575: the separately frozen #684 two-expert evaluation and blind adjudication
remain open, and this agent-curated source check does not stand in for a
maintainer's human sign-off.

## Bound declaration and registry receipt

The executable declaration is
`scripts/fixtures/review_target_context/msr-2027-technical-full-declaration.json`.
It is an illustrative fixture that models the closed state produced after a
hypothetical author confirmation. It is not an attestation by an author of a
real manuscript. The modeled values are:

| Axis | Modeled exact value |
|---|---|
| discipline | `Software Engineering` |
| subfield | `Mining Software Repositories` |
| venue | `MSR 2027` |
| track | `Technical Papers` |
| contribution type | `Full Paper` |
| overlay | `ACM SIGSOFT Repository Mining Standard` |

Registry identity: `ars-field-general-review-criteria@2026.08.24`; canonical registry
SHA-256:
`826e3212aef8aefbd56ca30af4a24e8c2936cfe3f6ed852a0a56b9440903ca84`.
The resolver remains offline and consumes only the committed registry bytes;
it does not retrieve these pages at runtime.

## Source-to-row evidence

| Registry row(s) | Primary source and locator | Version evidence | Decision |
|---|---|---|---|
| `official.msr2027.technical.full.scope` | [MSR 2027 Technical Papers — Call for Papers](https://2027.msrconf.org/track/msr-2027-technical-papers#Call-for-Papers) | The publisher page exposes no revision date, ETag, or Last-Modified value. The committed receipt pins a 45,702-byte raw capture and a normalized 16,601-byte `div#Call-for-Papers` semantic snapshot. All three MSR criterion versions carry semantic SHA-256 `2546217a5f2b7dccb3b617b976e75cf7427c9a3881fda3092323c94a35231795`. | Current official exact-target row; `blocking_allowed`. The statement is a short paraphrase, not a mirrored policy. |
| `official.msr2027.technical.full.validity` | [MSR 2027 evaluation criteria](https://2027.msrconf.org/track/msr-2027-technical-papers#evaluation-criteria) | Same mutable-page source receipt and hash-bound criterion version. | Current official exact-target row; `blocking_allowed`. Soundness and replicability are represented without inventing numeric weights. |
| `official.msr2027.technical.full.open-science` | [MSR 2027 Open Science Policy](https://2027.msrconf.org/track/msr-2027-technical-papers#open-science-policy) | Same mutable-page source receipt and hash-bound criterion version. | Current official exact-target row; `blocking_allowed`. The paraphrase distinguishes relevant source code from anonymized and curated study data and preserves conditional disclosure barriers. |
| `field.sigsoft.empirical.general-essential` | [ACM SIGSOFT General Standard at immutable commit](https://github.com/acmsigsoft/EmpiricalStandards/blob/d131d7209f2fad7e8dfd30afbd2b8ea605ea3141/docs/standards/GeneralStandard.md#L7-L75) | Commit `d131d7209f2fad7e8dfd30afbd2b8ea605ea3141`, 2025-02-19; raw-file SHA-256 `f36d203118e22524ddee8a21e427c1191a017fd8f2cb470d3ecc3b4fc613a71f`. At verification, official HEAD `d7496100cda2e87beca508f9295f3f74e42dff20` had the same blob hash. | Current field/society row, but `advisory_only`: no source establishes MSR adoption. |
| `overlay.sigsoft.repository-mining.essential` | [ACM SIGSOFT Repository Mining Standard at immutable commit](https://github.com/acmsigsoft/EmpiricalStandards/blob/53c14e1a85aac1aeafb0788a622c5aaafec5c8b9/docs/standards/RepositoryMining.md#L6-L55) | Commit `53c14e1a85aac1aeafb0788a622c5aaafec5c8b9`, 2025-05-26; raw-file SHA-256 `882cbfe912cc48e83f9193a447bdc1085f5c97058b3bd1bb8249714ba72e1f6d`. The same verified HEAD had the same blob hash. | Current overlay row, but `advisory_only`: the illustrative fixture selects it and it is not presented as an MSR rule. |

ACM SIGSOFT describes the collection as its official evidence standards and
publishes the repository under CC0 1.0. The MSR page exposes no visible
redistribution license, so the registry retains only source links and
curator-authored paraphrases. The cryptographic receipts, extraction rule, and
fragment mapping are committed as
`shared/review_criteria_sources/msr-2027-technical-papers.2026-08-24.json` and
`shared/review_criteria_sources/sigsoft-empirical-standards.2026-08-24.json`;
the MSR body itself is not redistributed. Both discriminated receipt shapes
validate against the closed
`shared/contracts/review_target/review_criteria_source_receipt.schema.json`.

## Registry migration receipt

The predecessor was
`ars-field-general-review-criteria@2026.08`, canonical SHA-256
`3209e681cc6dbc8ece2b0961ad3c516b7dd78aa32d045dacce76b54b5962f549`.
The update preserves that registry id as its lineage and increments only the
version. Because V1 intentionally includes `registry_version` in
`resolved_digest`, even a field-general context selecting the same four row
pointers rotates from
`204c4ef3c62b55886cfbfde8a0b60b3c451ece1aa118f4202fd6b002696ed6ce`
to
`b404e4cd3c21d002dc3212249d52480c3034f5debb04b0b10a1c07c21a258ebe`.
Consumers must recompute and explicitly rebind; an old context does not
silently inherit the new registry release.

## Conservative mappings and exclusions

- The MSR page alternates among “Technical Papers”, “Technical Track”, and
  “Research Track”. The declaration uses `Technical Papers`, the page's title
  and navigation label. V1 does not infer aliases: a fixture using one of the
  other source labels remains unresolved until an author explicitly confirms
  the canonical value.
- `Full Paper` is the singular registry label for the page's “Full papers”
  contribution class. Short work-in-progress papers do not match.
- The General Standard applies to empirical software-engineering work, but the
  V1 registry cannot encode the predicate “collects and analyzes data”. Its
  live row is therefore additionally scoped to the explicitly selected
  Repository Mining overlay instead of being applied to every Software
  Engineering manuscript.
- No source found states that MSR 2027 adopted either SIGSOFT standard. Both
  rows remain advisory even while current; they cannot issue blocking findings.
- A target whose venue, track, or contribution type differs from the exact
  declaration remains `declared_target_unresolved`. A missing overlay or a
  different discipline omits both SIGSOFT rows rather than silently widening
  applicability.

## Hermetic proof obligations

`scripts/test_resolve_review_target_context.py` now pins the following without
network access:

1. all nine applicable live rows resolve for the exact declaration;
2. the exact policy distribution is six blocking rows (three MSR plus three
   existing scientific-validity broad fallbacks) and three advisory rows (two
   SIGSOFT plus broad submission traceability);
3. near-miss venue, track, or contribution axes cannot impersonate the profile,
   and an unconfirmed source alias cannot silently rebind it;
4. SIGSOFT rows require the modeled confirmed discipline and overlay;
5. the first-verified date and stale-source advisory downgrade are enforced;
6. exact official fragments, immutable SIGSOFT commits, source receipts,
   current-head blob equality, and registry digests are pinned;
7. the predecessor-to-successor digest rotation is explicit; and
8. the live nine-row context completes pointer-only binding receipts for all
   three #684 consumers without copying criterion prose.

## Remaining closure boundary

This delivery closes the live-registry scope gap recorded in
`audits/575-scope-closure-audit-2026-08-24.md`; it does not rewrite that dated
audit. #575 still cannot close until #684 retains two independent blinded
human-expert label files, separate blind adjudication, the paired record, and
the required measurement report. No source-backed row establishes review
usefulness, calibration, field coverage, venue acceptance, or improved
research outcomes.
