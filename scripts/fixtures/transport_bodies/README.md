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
- arXiv ID `2613.04567` is structurally impossible (month 13 does not exist in
  the `YYMM.NNNNN` scheme), so it can never be minted — a merely "unused" ID
  would eventually collide with a real submission (a first-draft plausible ID
  turned out to resolve to a real paper; cross-model review P1, verified
  2026-07-15). The Atom entry title deliberately keeps arXiv's real-world
  line-wrap inside `<title>` to exercise the client's whitespace collapsing.
- OpenAlex IDs `W999999999999` / `A999999999998` / `S999999999997` sit far
  beyond OpenAlex's minting range for the same reason (a plausible `W44…` ID
  resolved to a real 2024 work); all three verified 404 on 2026-07-15.
- Author "Ada Fixture", venue "Journal of Synthetic Test Corpora", ISSN
  `0000-0000`, and the S2 `paperId` (a repeating hex pattern) are invented.

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
`search_query` miss (its self-link echoes an empty query — the one file
deliberately answers both request shapes). The clients never read 5xx bodies
either (their degradation paths use only the HTTP code/reason); the error
bodies are checked in for transport realism only, attached as the
`HTTPError` payload.

Deliberately NOT here: a product-level `--offline` mode, or a replication of
the 51-case citation gold set (issue #511 scopes both out as inflation).
