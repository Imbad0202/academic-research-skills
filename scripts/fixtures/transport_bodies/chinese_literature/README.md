# Chinese-literature resolver response fixtures (#595)

Checked-in raw response bodies fed through the ACTUAL `chinese_literature_client.py`
implementation by `scripts/test_chinese_literature_client.py`. Same discipline as
the sibling `transport_bodies/<resolver>/` directories: the client does the real
URL construction, dispatch, body parse, title cross-check and waterfall
reduction; only the socket is faked.

## Provenance / synthesis discipline

**Every body here is fully synthetic.** They are authored from the publicly
documented response shapes of the four upstreams — see
`deep-research/references/chinese_literature_api_protocol.md`, which carries the
hand-verified live examples (re-verified 2026-07-27) these shapes are modelled
on. Nothing in this directory contains a real record, a real person's name, or
any credential.

Identifiers use conspicuously synthetic suffixes for this hermetic fixture set.
They are not claims about the live DOI namespace — the sibling README records a
first-draft "plausible" ID that turned out to resolve to a real paper
(cross-model review P1):

- DOI prefix `10.5555` is registered with Crossref and resolvable records do
  exist under it. The deliberately conspicuous suffix namespaces
  `10.5555/ars.cn.istic.*` and `10.5555/ars.cn.cnki.*` distinguish synthetic
  routing branches only; tests never contact the live DOI service or infer that
  the prefix is structurally unmintable.
- The `RA` values in `ra_istic.json` / `ra_cnki.json` are therefore **synthetic
  routing answers**: `10.5555` is not really registered with ISTIC or CNKI. The
  real prefix→RA triage table (`10.3760` → ISTIC, `10.13209` → CNKI, `10.1360`
  → Crossref) is documented and dated in the protocol doc; these fixtures only
  need to exercise the client's three routing branches.
- `ra_unknown_prefix.json` mirrors the endpoint's real unknown-prefix shape
  (verified 2026-07-27: `/doiRA/10.99999` → `[{"DOI": "10.99999", "status": "DOI
  does not exist"}]` — a `status` field in place of `RA`), keyed to `10.99999`,
  a prefix the DOI Foundation reports as nonexistent.
- PMIDs `999999901` / `999999902` are far beyond PubMed's assignment range.
- ISSN `0000-0000` is the invalid-by-construction placeholder, matching the
  sibling fixtures.
- Journal 合成测试医学杂志 / `Hecheng Ceshi Yi Xue Za Zhi`, author "Hecheng Ceshi",
  and every title are invented. The journal is injected through the client's
  documented `journal_map=` extension point, so no test depends on the shipped
  seed table's contents.
- Landing-page URLs use the reserved `.invalid` TLD.

## Layout

| file | shape exercised |
|---|---|
| `ra_istic.json` / `ra_cnki.json` / `ra_crossref.json` | `doi.org/doiRA/<prefix>` — the three routing branches |
| `ra_unknown_prefix.json` | the endpoint's real unknown-prefix answer: a `status` field, no `RA` key (must yield "no agency", not a degradation) |
| `istic_csl_hit.json` | ISTIC content negotiation: CSL-JSON with the Chinese title |
| `istic_csl_other_title.json` | same DOI resolving to a different title (chimeric-citation shape) |
| `cnki_landing_page.html` | the CNKI RA's HTML answer to a CSL-JSON request — deliberately never parsed |
| `handle_exists.json` | Handle REST `responseCode: 1` |
| `handle_absent.json` | Handle REST `responseCode: 100` (fabricated identifier) |
| `handle_internal_error.json` | Handle REST `responseCode: 2` (unknown state → degrade) |
| `esearch_coverage_hit.json` / `esearch_coverage_zero.json` | journal-coverage confirmation (≥1 PubMed record vs none) |
| `esearch_coordinate_hit.json` / `_zero.json` / `_ambiguous.json` | the `[ta]+[vi]+[pg]` coordinate query: unique hit, fabricated page, multi-record |
| `esummary_hit.json` | esummary projection, including the **English bracketed shadow title** PubMed stores for Chinese-language articles |
| `esummary_no_doi.json` | a unique PubMed coordinate candidate with no DOI; it must remain unverified |
| `esummary_unknown_ra.json` | a candidate whose DOI uses the synthetic unknown prefix, so RA absence cannot be confused with a mismatched echo |
| `esummary_year_mismatch.json` | a record at the cited coordinates whose year disagrees |
| `esummary_issn_mismatch.json` | a record at the cited coordinates whose journal ISSN disagrees with the bridged ISSN |
| `error_5xx.html` | 5xx body, attached as the `HTTPError` payload for transport realism (the client reads only the code/reason) |

Deliberately NOT here: any live-network test. The protocol doc's live examples
are documentation of a manual verification, not an automated check — nothing in
CI contacts `doi.org`, `hdl.handle.net`, or NCBI.
