# Transport-boundary response fixtures (#511 Part B)

Checked-in raw API response bodies fed through the four ACTUAL resolver client
implementations (`crossref_client.py`, `openalex_client.py`,
`semantic_scholar_client.py`, `arxiv_client.py`) into
`verification_gate.verify_citation` by
`scripts/test_transport_fixture_citation_gate.py`. Unlike the per-client unit
suites (which pin one client at a time) and the citation eval (which replays
already-reduced `resolver_outcomes`), these fixtures exercise the real client
parsing end-to-end: URL construction → HTTP dispatch → body parse → title
cross-check → gate reduction.

## Provenance / redaction

Every body is authored from the publicly documented response shape of the
corresponding API (see `deep-research/references/*_api_protocol.md`), with all
metadata SYNTHETIC:

- DOI `10.5555/ars.tfx.2026.42` uses the `10.5555` example/test prefix — it
  resolves nowhere.
- arXiv ID `2601.04567` is fictitious; the Atom entry title deliberately keeps
  arXiv's real-world line-wrap inside `<title>` to exercise the client's
  whitespace collapsing.
- Author "Ada Fixture", venue "Journal of Synthetic Test Corpora", and all IDs
  (OpenAlex `W…`/`A…`/`S…`, S2 `paperId`) are invented.

## Layout

Per resolver, three bodies (success / miss / error):

| resolver | success (200) | miss (200) | error (5xx body) |
|---|---|---|---|
| `crossref/` | `doi_hit.json` | `title_search_miss.json` | `error_5xx.html` |
| `openalex/` | `doi_hit.json` | `title_search_miss.json` | `error_5xx.json` |
| `semantic_scholar/` | `doi_hit.json` | `title_search_miss.json` | `error_5xx.json` |
| `arxiv/` | `id_hit.xml` | `empty_feed.xml` | `error_5xx.html` |

DOI/ID-keyed misses are HTTP 404s (no body to check in for JSON APIs — the
clients never read the 404 body); the checked-in miss body is the 200
empty-result shape the title-fallback request receives. arXiv's miss shape is
its genuine empty Atom feed, which serves both the `id_list` miss and the
`search_query` miss.

Deliberately NOT here: a product-level `--offline` mode, or a replication of
the 51-case citation gold set (issue #511 scopes both out as inflation).
