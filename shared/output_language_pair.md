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

The abstract length and keyword regime table is **not** carried here: its single source is
[`academic-paper/references/abstract_writing_guide.md`](../academic-paper/references/abstract_writing_guide.md),
whose marked regime block every other surface references. This contract carries the registry,
the language roles, and the field semantics — not the figures.

The figures have one home so that a paper type's length cannot drift between copies: the guide
carries the reconciled table (Standard / Conference / Extended abstract / Dissertation rows for
the default entry `zh-tw-en`), and `scripts/check_spec_consistency.py` asserts both that the
guide carries it and that this contract carries no competing copy.

The figures apply whether or not the run declares `output_language_pair`; the field selects which
two languages the abstract surfaces use, not which figures apply.

**Known exception (deferred to Phase 2).** `academic-paper/agents/formatter_agent.md` still
states a generic abstract limit of its own ("typically 150-300 words"). The formatter is
untouched in Phase 1 by design, so that line is a recorded exception rather than a pointer, and
it is reconciled with the guide's table when the formatter is next revised.

---

## Field semantics

`output_language_pair` is an **optional field** of Schema 4
([`shared/handoff_schemas.md`](handoff_schemas.md), Schema 4 Paper Draft). Its value is a
**string** token from the registry above — never a locale code, never an array, never a
derived label.

| Value | Result |
|-------|--------|
| key omitted | **Legacy behaviour** — the run renders the **default pair** (Traditional Chinese L1 + English L2), as every pre-#862 run did. Phase 1 holds three things fixed and claims exactly those: the legacy Schema-4 object keys, the legacy heading literals, and the omitted serialized key (*Absent field* below lists them). Absence is not an error, and omission *is* the legacy state — not a behaviour-equivalence claim about the rest of the run. |
| `zh-tw-en` | Valid — the default entry: the pair every pre-#862 run produced, so a run that declares it changes no surface. |
| any other string | **Visible failure**: the step aborts, naming this registry and the unsupported value. There is no silent fallback to the default. |
| non-string, `null`, or empty string | **Visible failure**: the same abort, naming this registry. A present-but-unusable value is never treated as absent. |

Validation is owned by the core contract and enforced by
`scripts/check_spec_consistency.py` (`check_output_language_pair_contract`). A consumer
surface that names a pair writes the token verbatim in backticks, so the registry can be
checked mechanically: the lint treats any backticked span shaped like a token as an advertised pair, so a backticked
hyphenated English word (`per-run`, `up-to-date`) on one of the scanned surfaces fails as an
unregistered pair — write such a word unbackticked.

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

No step has to **forward** the token: `academic-paper/agents/draft_writer_agent.md` reads the
PCR `Output Language Pair` row directly and serializes it into Schema 4, and
`academic-paper/agents/structure_architect_agent.md` derives its pair-derived labels from the
pair it is dispatched with and never passes the token on. A missing forwarding step is therefore
not a gap in the chain, and no agent is required to relay the value for the serialization to
happen.

### Absent field: the legacy literals are reproduced exactly

With the key omitted, three things reproduce exactly: the Schema-4 legacy object keys
(`abstract: {english, chinese}`, `keywords: {en, zh_tw}`), the heading literals
(`### English Abstract`, `### Chinese Abstract`, `## English Abstract`,
`## Chinese Abstract (zh-TW)`), and the omitted serialized key. That list is the whole of the
Phase-1 equivalence claim, and it is a **file-level literal** claim about the default pair — not
a claim that a rendered document is byte-identical, and not a claim about model behaviour. The
migration is additive: absence is a valid legacy state, not a gap to repair.

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
