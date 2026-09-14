# Output Language Pair — Per-Run Output-Language Contract

**Status:** Phase 1 (issue #862) — the contract, the registry, the Schema-4 field, and the
consumer surfaces that carry the token. Phase 2 adds the registry loader, locale packs
(`locales/<locale>/`), and pack-supplied regime rows.

**Scope:** one run declares at most one output language pair. The pair selects the two
languages of the run's abstract surfaces. It is not a locale pack, not a manuscript-body
setting, and not an abstract-cardinality setting.

---

## Registry

Registry tokens are **opaque and registry-keyed**. A token names a registry entry; it is
never parsed. Language roles (L1 / L2), their order, and their script classes are declared
by the entry, so `zh-tw-en` and a hypothetical `en-zh-tw` would be two different entries
with different declarations — not the same pair reversed.

<!-- output-language-pair-registry:start -->
| Token | L1 language | L1 script | L2 language | L2 script | Status |
|-------|-------------|-----------|-------------|-----------|--------|
| `zh-tw-en` | Traditional Chinese (`zh-TW`) | CJK | English (`en`) | Latin | default |
<!-- output-language-pair-registry:end -->

- **Two-language entries only.** The Phase-1 registry holds pair entries and nothing else.
  A unary token (one language, with or without a region subtag) is not a registry entry,
  and as a value it is unsupported: it fails visibly rather than being normalized.
- **Pair selection and abstract cardinality are separate controls.** Cardinality is
  already a mode input of its own (`academic-paper/agents/intake_agent.md`, Step 6:
  Bilingual / EN only / zh-TW only). `output_language_pair` never encodes cardinality.
- **One default entry.** The default entry is the legacy behaviour: Traditional Chinese
  (L1) plus English (L2), the pair every pre-#862 run produced.

### Overlay boundary

Locale packs contribute registry entries as **configuration** — nothing else. A pack MUST
NOT overlay a core `SKILL.md`, an agent definition, IRON RULE text, an integrity protocol,
a schema, a mode, or an oversight rule. The core contract owns validation and the default
entry; pack-supplied registry entries ship with the Phase-2 loader (`locales/<locale>/`).
An entry a pack contributes declares its own language roles, scripts, and regime rows; it
does not redefine the core contract.

---

## Regime table

This table is the **single source** for abstract length and keyword counts. Every other
surface that needs one of these figures references this table; none restates it. The
previous figures were carried by `academic-paper/references/abstract_writing_guide.md` as
two per-language bullet lists; reconciliation folds them here (see below).

Lengths are measured per [`shared/references/word_count_conventions.md`](references/word_count_conventions.md)
— whitespace splitting, ARS-marker removal, and the 3–5% buffer rule. That reference is
pointed at, never replaced.

Regime for the default entry `zh-tw-en`:

| Paper type | L1 abstract (`zh-TW`, CJK) | L2 abstract (`en`) | Keywords per language |
|------------|---------------------------|--------------------|-----------------------|
| Standard | 300–500 characters | 150–250 words | 5–7 |
| Conference | 300–800 characters | 200–500 words | 5–7 |
| Dissertation | 500–1,000 characters | up to 350 words | 5–7 |

**Reconciliation.** Two figures in the abstract guide's *Bilingual Abstract Quality
Checklist* conflicted with its own Standard row: English *150–300 words* against
*150–250 words*, and *keywords 5–7* restated beside a keywords section that already said
5–7. Neither the checklist line nor the section restatement survives as a competing
number; the reconciled figures above are Standard English 150–250 words and 5–7 keywords
per language. A venue-declared limit keeps precedence through the venue profile
(issue #394), which the submission verifier already checks.

Phase 1 carries the regime table for the default entry only. A pack-supplied entry ships
its own regime rows with the Phase-2 loader.

---

## Field semantics

`output_language_pair` is an **optional field** of Schema 4
([`shared/handoff_schemas.md`](handoff_schemas.md), Schema 4 Paper Draft). Its value is a
**string** token from the registry above — never a locale code, never an array, never a
derived label.

| Value | Result |
|-------|--------|
| key omitted | **Legacy behaviour**: exactly today's zh-TW + EN bilingual output. Absence is not an error, and no consumer changes behaviour when the key is missing. |
| `zh-tw-en` | Valid — the default entry, equivalent to the legacy behaviour. |
| any other string | **Visible failure**: the step aborts, naming this registry and the unsupported value. There is no silent fallback to the default. |
| non-string, `null`, or empty string | **Visible failure**: the same abort, naming this registry. A present-but-unusable value is never treated as absent. |

Validation is owned by the core contract and enforced by
`scripts/check_spec_consistency.py` (`check_output_language_pair_contract`). A consumer
surface that names a pair writes the token verbatim in backticks, so the registry can be
checked mechanically.

### Carrier chain

```text
intake captures the pair
  → the run-configuration row holds it
    → dispatch passes it to the abstract and structure agents
      → draft_writer serializes it into Schema 4
```

Every step ships in Phase 1; the registry loader and pack-supplied entries land in Phase 2.
Every step omits the value when it is absent. The pair-derived labels and headings a
consumer renders reproduce the legacy literals exactly for the default entry; a
pair-derived label is never a rename of the legacy surface.

### Absent field: the legacy literals are reproduced exactly

With the key omitted, the Schema-4 legacy object keys (`abstract: {english, chinese}`,
`keywords: {en, zh_tw}`) and the heading literals (`### English Abstract`,
`### Chinese Abstract`, `## English Abstract`, `## Chinese Abstract (zh-TW)`) reproduce
exactly. The migration is additive: absence is a valid legacy state, not a gap to repair.

### Conflicting declarations fail visibly

The pair is declared once per run, and the PCR `Output Language Pair` row is that single
declaration site. A handoff whose sites disagree — the run configuration carrying one token
while the dispatched context or the Schema-4 handoff carries another — stops and names both values;
no site wins silently.

A pair whose L1 language is not the legacy Traditional Chinese cannot coexist with the legacy
object keys (`abstract: {english, chinese}`, `keywords: {en, zh_tw}`): those key names describe
the default pair's languages only. A handoff that declares a non-default pair while still
carrying them is a conflict and fails visibly. Phase 1 cannot reach that state — the registry
holds one entry — and the rule exists so that a Phase-2 entry cannot silently render the
default pair's key names for another L1.
