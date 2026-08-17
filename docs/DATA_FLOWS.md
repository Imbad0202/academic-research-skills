# Data Flows: What Leaves the Machine, What Is Stored, and for How Long

**Purpose.** ARS touches the network in a small number of places and persists a small
number of local stores. Each is documented at its own feature page; this file is the
single user-facing map — one row per network touchpoint (what triggers it, what is
sent, to whom, how to turn it off) and one row per local store (path, content,
lifetime, how to delete). [`THIRD_PARTY.md`](../THIRD_PARTY.md) warns generically to
review third-party service policies; this page tells you *which* services those are
for the core suite.

**Origin.** ISO/IEC 42001-spirit gap assessment
([`audits/iso42001-spirit-gap-assessment-2026-08-17.md`](../audits/iso42001-spirit-gap-assessment-2026-08-17.md),
finding T-7, [#758](https://github.com/Imbad0202/academic-research-skills/issues/758)).
Transparency here is one of this repo's distilled operating principles (with
informative anchors to ISO/IEC 42001) — not an ISO-mandated artifact.

## Scope

This page covers the network calls and stores that **ARS's own scripts** perform. Two
boundaries around that scope:

- **The Claude session itself is not on this map.** Everything you type, every file the
  session model reads, and any web search/fetch the model performs while executing the
  research skills travels over your Claude platform connection under your Anthropic
  account settings. That path exists with or without ARS and is governed by the
  platform, not by this repo.
- **Nothing here publishes.** No ARS component submits, posts, or uploads your work
  anywhere autonomously. Every network row below is a *lookup* (sending queries or
  citation metadata to read public indexes), an *update check*, or an *explicitly
  consented* verification call.

## Network touchpoints

| Touchpoint | When it fires | What is sent | Recipient | Credentials (optional unless noted) | Off switch |
|---|---|---|---|---|---|
| Semantic Scholar resolver (`scripts/semantic_scholar_client.py`) | Citation-existence verification (#182 gate) at the Stage 2.5 / 4.5 integrity gates, or standalone `verify_passport.py` / `verify_citation` calls; cache-through by default | Citation metadata of your references: titles, DOIs/IDs, authors, years | `api.semanticscholar.org` | `S2_API_KEY` (raises rate limit; works without) | Don't run script-backed verification; prompt-only modes make no calls |
| OpenAlex resolver (`scripts/openalex_client.py`) | Same gate (four-index triangulation) | Same citation-metadata class; polite-pool email if you configure one | `api.openalex.org` | `OPENALEX_API_KEY` | Same as above |
| Crossref resolver (`scripts/crossref_client.py`) | Same gate | Same class; polite-pool email rides the `User-Agent` header if configured | `api.crossref.org` | none (polite email optional) | Same as above |
| arXiv resolver (`scripts/arxiv_client.py`) | Same gate | Same class | `export.arxiv.org` (ToU-aligned ≥3 s pacing) | none | Same as above |
| Chinese-literature resolver (`scripts/chinese_literature_client.py`, #595) | **Standalone CLI only — deliberately NOT part of the four-index verification gate** | DOI prefixes / DOIs of the works you resolve | `doi.org` (RA lookup + resolution), `hdl.handle.net`, NCBI E-utilities (`eutils.ncbi.nlm.nih.gov`) | NCBI API key (optional; does not relax the client's polite pacing) | Don't invoke the CLI |
| Claim-standing discovery adapters (`scripts/claim_standing_discovery.py`, #655) | Only under an explicit consent-bound query plan; the evaluation substrate is offline by default | **Claim-derived search query strings** (they can derive from unpublished claims — hence the consent gate and the per-transmission ledger) + date filters | The same four indexes above | Same per-index keys | No consent → no calls; every transmission is ledgered |
| Cross-model verification transport | Only when `ARS_CROSS_MODEL` is configured **and** you give explicit per-session consent — the env var is configuration, not consent ([`shared/cross_model_verification.md`](../shared/cross_model_verification.md)) | Up to **manuscript content**: integrity-gate samples, the blind Devil's-Advocate critique input, the full paper for the consent-gated Reviewer-2 seat, checkpoint judgments | `api.openai.com`, `generativelanguage.googleapis.com`, or the OpenAI-compatible base URL you set (`ARS_OPENAI_COMPAT_BASE_URL`, e.g. DeepSeek) | `OPENAI_API_KEY` / `GOOGLE_AI_API_KEY` / `ARS_OPENAI_COMPAT_API_KEY` (required for this feature) | Leave `ARS_CROSS_MODEL` unset (zero calls), or decline consent per session |
| ChatGPT-subscription citation transport (`scripts/cross_model_codex_transport.py`, #630) | Only when `ARS_CROSS_MODEL_TRANSPORT=codex`; citation-integrity calls **only** (never DA / reviewer / judgment calls) | Single-reference citation metadata, sent through the local Codex CLI in a read-only sandbox with an auth-only ephemeral home | OpenAI, through your Codex CLI ChatGPT login | Codex CLI subscription login | Unset the transport selector; any other value fails visibly, no fallback |
| Timeline bootstrap (`scripts/bootstrap_timeline_yaml.py`, v3.9.4 opt-in) | Standalone CLI you invoke to seed `timeline.yaml` from a literature corpus; `--dry-run` makes no calls | DOIs of your corpus entries | `api.crossref.org` | none (needs the optional `requests` package; absent, lookups are treated as an outage) | Don't run it, or pass `--dry-run` |
| SessionStart update check (`scripts/ars_update_check.sh`, #544; plugin installs only) | At most one HTTPS GET per 24 h, 3-second ceiling, silent on failure | **No user data** — fetches this repo's public `plugin.json` and compares versions | `raw.githubusercontent.com` | none | `ARS_UPDATE_CHECK=0` |
| Manual smoke tests (`scripts/cross_model_smoke_test.sh`, `scripts/cross_model_smoke_test_codex.sh`) | Only when you run them by hand; CI never does | Public sample citation metadata | The provider under test | The provider's key / login | Don't run them |

Notes:

- **Agent-side lookups use the same indexes.** Outside the script clients, the
  research/verification agents (`bibliography_agent`, `source_verification_agent`,
  `integrity_verification_agent`) query the same four indexes at ingest and
  verification time, following the per-index API protocol docs under
  `deep-research/references/`. Same payload class (citation metadata), same
  endpoints; executed through the session's tooling.
- **The verification gate is subscription-free by design**: the four gate resolvers
  need no account and no key (keys only raise rate limits — verifiable in each client).
  This is a deliberate reproducibility choice; the Chinese-literature client is kept
  standalone rather than folded into the gate for the same reason.
- Resolver clients never log or echo credentials; polite-pool emails and API keys are
  stripped from error messages (see each client's redaction comments).
- CI runs against checked-in synthetic fixtures
  (`scripts/test_transport_fixture_citation_gate.py`); no CI job performs live
  resolver or provider calls.

## Local stores

| Store | Path | Content | Lifetime | How to delete |
|---|---|---|---|---|
| Citation-verification cache | `~/.cache/ars/verification.db` (override: `ARS_VERIFICATION_CACHE_PATH`) | Per-citation resolver outcomes (SQLite) | 90-day TTL per entry; staleness advisory after `ARS_CACHE_STALE_ADVISORY_DAYS` (default 30), live re-validation via `ARS_CACHE_REVALIDATE=1` | `/ars-cache-invalidate <citation_key>` per key, or delete the file |
| Update-check state | `~/.cache/ars/` (override: `ARS_UPDATE_CHECK_STATE_DIR`) | Version strings only | Re-fetched when older than 24 h | Delete the directory; `ARS_UPDATE_CHECK=0` stops new writes |
| Material Passport + project ledgers | The passport path **you** name per run (never a hidden global location) | Your research content: corpus entries, read-attestation ledger, reset boundaries, compliance history, claim-standing consent receipts / transmission ledgers, rejection logs | No TTL — user-owned project files | Delete with your project |
| Codex transport working dir | A per-call `ars-codex-citation-*` temporary directory | Auth-only ephemeral home, empty working root | Removed automatically when the call returns | Automatic |

The suite itself contains no telemetry and no analytics endpoint, and requires no
account with the ARS project: the network inventory above is exhaustive for the
repository's own scripts (a CI lint fails when a script gains a network import
without a row here).

## Related

- [`SECURITY.md`](../SECURITY.md) — data exfiltration and credential leakage are
  explicitly in scope for vulnerability reports.
- [`THIRD_PARTY.md`](../THIRD_PARTY.md) — community projects around ARS run their own
  services with their own policies; this map covers only the core suite.
- [`shared/cross_model_verification.md`](../shared/cross_model_verification.md) — the
  consent boundary and provider table for the cross-model rows.
- `docs/CONTROL_AVAILABILITY.md` (lands with PR #768) — which of these code paths even
  exist in your install channel.
