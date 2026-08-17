# Data Flows: What Leaves the Machine, What Is Stored, and for How Long

**Purpose.** ARS touches the network in a small number of places and persists a small
number of local stores. Each is documented at its own feature page; this file is the
single user-facing map — one row per network touchpoint and one row per local store.

**Origin.** ISO/IEC 42001-spirit gap assessment
([`audits/iso42001-spirit-gap-assessment-2026-08-17.md`](../audits/iso42001-spirit-gap-assessment-2026-08-17.md),
finding T-7, [#758](https://github.com/Imbad0202/academic-research-skills/issues/758)).
Transparency here is one of this repo's distilled operating principles (with
informative anchors to ISO/IEC 42001) — not an ISO-mandated artifact.

## Scope

This page covers the network calls and stores that **ARS's own scripts** perform. The
boundaries around that scope:

- **The Claude session itself is not on this map.** Everything you type, every file the
  session model reads, and any web search/fetch the model performs while executing the
  research skills travels over your Claude platform connection under your Anthropic
  account settings. That path exists with or without ARS and is governed by the
  platform, not by this repo.
- **Maintainer/evaluation harnesses are not user paths.** A few repo scripts exist
  only for maintainers running measurements (e.g. `scripts/dispatch_e4_panel.py`
  through `claude -p`, `scripts/run_review_criteria_constructive_value.py` through
  the Codex CLI, `scripts/check_ranking_lift.py` through `gh api`). They send
  content through locally authenticated CLIs when a maintainer invokes them, are
  never triggered by any user-facing feature, and are deliberately excluded from
  the touchpoint tables below.
- **Nothing here publishes.** No ARS component is designed to submit, post, or upload
  your work anywhere autonomously — every network row below is a *lookup* (sending
  queries or citation metadata to read public indexes), an *update check*, or an
  *explicitly consented* verification call. This is the same first-party scope boundary
  stated in [`POSITIONING.md`](../POSITIONING.md), and it inherits that page's
  qualifier: a scope boundary and review criterion, not a runtime guarantee.

## Network touchpoints

### The citation-verification gate (four bibliographic indexes)

The deterministic citation-existence gate (#182) fires at the Stage 2.5 / 4.5
integrity gates or on standalone `verify_passport.py` / `verify_citation` calls,
cache-through by default. Each resolver sends the same payload class — identifiers
(DOIs/arXiv ids) and title query strings of your references; author/year metadata is
used locally for matching, not transmitted — and all four work
without any account or key; keeping the gate key-free is a deliberate reproducibility
choice. Off switch: don't run script-backed verification; prompt-only modes make no
calls.

| Resolver | Endpoint | Credentials (optional) | Per-index note |
|---|---|---|---|
| `scripts/semantic_scholar_client.py` | `api.semanticscholar.org` | `S2_API_KEY` (raises rate limit) | |
| `scripts/openalex_client.py` | `api.openalex.org` | `OPENALEX_API_KEY` | Polite-pool email sent if you configure one |
| `scripts/crossref_client.py` | `api.crossref.org` | none (polite email optional) | Polite-pool email rides the `User-Agent` header |
| `scripts/arxiv_client.py` | `export.arxiv.org` | none | ToU-aligned ≥3 s pacing |

### Everything else

| Touchpoint | When it fires | What is sent | Recipient | Credentials | Off switch |
|---|---|---|---|---|---|
| Chinese-literature resolver (`scripts/chinese_literature_client.py`, #595) | **Callable client only (no CLI wrapper) — deliberately NOT wired into the four-index verification gate** (the same reproducibility choice) | DOI prefixes / DOIs of the works you resolve; the PubMed path additionally sends your NCBI contact email (required by E-utilities) and bibliographic search coordinates (journal/volume/page, author/year) | `doi.org` (RA lookup + resolution), `hdl.handle.net`, NCBI E-utilities (`eutils.ncbi.nlm.nih.gov`) | NCBI email required for the PubMed path; NCBI API key optional (does not relax the client's polite pacing) | Don't call the client |
| Claim-standing discovery adapters (`scripts/claim_standing_discovery.py`, #655) | Only under an explicit consent-bound query plan; the evaluation substrate is offline by default | **Claim-derived search query strings** (they can derive from unpublished claims — hence the consent gate and the per-transmission ledger) + date filters | The same four indexes above | none (fixed User-Agent; the resolver clients' env keys are not consumed) | No consent → no calls; every transmission is ledgered |
| Timeline bootstrap (`scripts/bootstrap_timeline_yaml.py`, v3.9.4 opt-in) | Standalone CLI you invoke to seed `timeline.yaml` from a literature corpus; `--dry-run` makes no calls | DOIs of your corpus entries | `api.crossref.org` | none (needs the optional `requests` package; absent, lookups are treated as an outage) | Don't run it, or pass `--dry-run` |
| Cross-model verification transport | Only when `ARS_CROSS_MODEL` is configured **and** you give explicit per-session consent — the env var is configuration, not consent ([`shared/cross_model_verification.md`](../shared/cross_model_verification.md)) | Up to **manuscript content**: integrity-gate samples, the blind Devil's-Advocate critique input, the full paper for the consent-gated Reviewer-2 seat, checkpoint judgments | `api.openai.com`, `generativelanguage.googleapis.com`, or the OpenAI-compatible base URL you set (`ARS_OPENAI_COMPAT_BASE_URL`, e.g. DeepSeek) | `OPENAI_API_KEY` / `GOOGLE_AI_API_KEY` / `ARS_OPENAI_COMPAT_API_KEY` (required for this feature) | Leave `ARS_CROSS_MODEL` unset (zero calls), or decline consent per session |
| Codex audit wrapper (`scripts/run_codex_audit.sh`) | Only when a human, CI step, or SubagentStop hook invokes it (same-session in-LLM invocation is forbidden by its header contract); `--dry-run` writes and sends nothing | Audit prompts containing the **deliverable and supporting files' contents** | OpenAI, through the local Codex CLI login | Codex CLI auth | Don't invoke it |
| ChatGPT-subscription citation transport (`scripts/cross_model_codex_transport.py`, #630) | Only when `ARS_CROSS_MODEL_TRANSPORT=codex`; citation-integrity calls **only** (never DA / reviewer / judgment calls) | One reference's citation text plus its exact `citation_context` — the sentence where it is cited, which can contain unpublished manuscript text — sent through the local Codex CLI in a read-only sandbox with an auth-only ephemeral home | OpenAI, through your Codex CLI ChatGPT login | Codex CLI subscription login | Unset the transport selector; any other value fails visibly, no fallback |
| SessionStart update check (`scripts/ars_update_check.sh`, #544; plugin installs only) | At most one *successful* check per 24 h (a failed attempt writes no state and may retry at the next session start); 3-second total ceiling, redirects followed, silent on failure | **No user data** — fetches a public `plugin.json` and compares versions | `raw.githubusercontent.com` by default; `ARS_UPDATE_CHECK_REMOTE_URL` overrides the endpoint | none | `ARS_UPDATE_CHECK=0` |
| Manual smoke tests (`scripts/cross_model_smoke_test.sh`, `scripts/cross_model_smoke_test_codex.sh`) | Only when you run them by hand; CI never does | Public sample citation metadata | The provider under test | The provider's key / login | Don't run them |

Notes:

- **Agent-side lookups use the same indexes.** Outside the script clients, the
  research/verification agents (`bibliography_agent`, `source_verification_agent`,
  `integrity_verification_agent`) query the same four indexes at ingest and
  verification time, following the per-index API protocol docs under
  `deep-research/references/`. Same payload class (citation metadata), same
  endpoints; executed through the session's tooling.
- Resolver clients never log or echo credentials; polite-pool emails and API keys are
  stripped from error messages (see each client's redaction comments).
- CI runs against checked-in synthetic fixtures
  (`scripts/test_transport_fixture_citation_gate.py`); no CI job performs live
  resolver or provider calls.

## Local stores

| Store | Path | Content | Lifetime | How to delete |
|---|---|---|---|---|
| Citation-verification cache | `~/.cache/ars/verification.db` (override: `ARS_VERIFICATION_CACHE_PATH`) | Per-citation resolver outcomes (SQLite) | 90-day TTL per entry — expiry means a cache miss, not deletion; expired rows persist on disk until overwritten by a later re-verification, invalidated, or the file is deleted. Staleness advisory after `ARS_CACHE_STALE_ADVISORY_DAYS` (default 30), live re-validation via `ARS_CACHE_REVALIDATE=1` | `/ars-cache-invalidate <citation_key>` per key, or delete the file |
| Update-check state | `~/.cache/ars/` (override: `ARS_UPDATE_CHECK_STATE_DIR`) | A state label (`UP_TO_DATE` / `UPDATE_AVAILABLE`) plus installed and remote version strings | Re-fetched when older than 24 h | Delete the directory; `ARS_UPDATE_CHECK=0` stops new writes |
| Retraction-status cache (`scripts/retraction_status.py`) | A caller-supplied SQLite path (no default location) | DOI-keyed resolver observations with timestamps | No automatic expiry; observations older than the 30-day threshold are marked stale, not deleted | Delete the file |
| Material Passport + project ledgers | The passport path **you** name per run (never a hidden global location) | Your research content: corpus entries, read-attestation ledger, reset boundaries, compliance history, claim-standing consent receipts / transmission ledgers, rejection logs | No TTL — user-owned project files | Delete with your project |
| Codex transport working dir | A per-call `ars-codex-citation-*` temporary directory | Auth-only ephemeral home, empty working root | Removed automatically when the call returns | Automatic |

The tunable numbers above (TTLs, thresholds) are documented where they are set —
[`SETUP.md`](SETUP.md) § Citation verification cache and § Optional environment flags
are the user-facing authority for changing them.

The suite itself contains no telemetry and no analytics endpoint, and requires no
account with the ARS project; the inventory above is exhaustive for this repository's
own scripts as of this revision. A CI lint (`scripts/check_data_flows.py`) holds one
direction of that mechanically — a script that gains a *direct* network import, or a
shell script that gains a `curl`, fails CI until it has a row here. Paths that reach
the network indirectly — through a spawned CLI (the codex transport rows), or through
the session's own tooling following a protocol doc — are held by review, not by the
lint.

## Related

- [`SECURITY.md`](../SECURITY.md) — data exfiltration and credential leakage are
  explicitly in scope for vulnerability reports; anything beyond this map is
  report-worthy.
- [`THIRD_PARTY.md`](../THIRD_PARTY.md) — community projects around ARS and their own
  policies (this map covers the core suite only).
- [`docs/SETUP.md`](SETUP.md) — installation, environment flags, and the canonical
  home of the cache and cross-model configuration this map summarizes.
- [`shared/cross_model_verification.md`](../shared/cross_model_verification.md) — the
  consent boundary and provider table for the cross-model rows.
- `docs/CONTROL_AVAILABILITY.md` (lands with PR #768) — which of these code paths even
  exist in your install channel.
