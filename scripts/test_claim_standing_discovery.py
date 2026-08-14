from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import build_claim_standing_candidate_ledger as ledger
from scripts import claim_standing_discovery as discovery

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
FIXTURES = ROOT / "scripts/fixtures/claim_standing_candidate_ledger"

LIVE_INDEX_IDS = ["semantic_scholar", "openalex", "crossref", "arxiv"]


def _rehash_plan(plan: dict) -> None:
    claim = plan["claim"]
    claim["claim_sha256"] = ledger.text_digest(claim["claim_text"])
    for query in plan["queries"]:
        query["source_claim_sha256"] = claim["claim_sha256"]
        query["query_sha256"] = ledger.text_digest(query["accepted_query_text"])
    consent = plan["consent"]
    consent["claim_sha256"] = claim["claim_sha256"]
    consent["provider_roster_sha256"] = ledger.digest(plan["provider_roster"])
    consent["caps_sha256"] = ledger.digest(plan["caps"])
    consent["queries_sha256"] = ledger.digest(plan["queries"])
    consent["consentable_plan_sha256"] = ledger.digest(
        ledger.consentable_plan_projection(plan)
    )
    consent["receipt_sha256"] = ledger.bound_digest(consent, "receipt_sha256")
    plan["plan_sha256"] = ledger.bound_digest(plan, "plan_sha256")


def _live_plan(
    index_ids: list[str] | None = None,
    date_filter=None,
    authorized_output_path: str = "/operator-named/candidate-ledger.json",
) -> dict:
    plan = json.loads((FIXTURES / "query_plan.json").read_text(encoding="utf-8"))
    targets = index_ids or LIVE_INDEX_IDS
    plan["provider_roster"] = [
        discovery.provider_roster_defaults()[index_id] for index_id in targets
    ]
    plan["queries"] = plan["queries"][:1]
    plan["queries"][0]["index_targets"] = targets
    plan["queries"][0]["date_filter"] = (
        date_filter
        if date_filter is not None
        else {"from_year": None, "through_year": None}
    )
    plan["consent"]["local_persistence"] = "explicit_local_export"
    plan["consent"]["export_boundary"] = ledger.EXPLICIT_LOCAL_EXPORT_BOUNDARY
    plan["consent"]["authorized_output_path"] = authorized_output_path
    _rehash_plan(plan)
    return plan


def _s2_record(index: int, *, doi: str | None = "10.5555/s2-{i}") -> dict:
    return {
        "paperId": f"s2paper{index}",
        "title": f"Synthetic S2 result {index}",
        "abstract": f"Synthetic abstract number {index} describing the finding.",
        "year": 2022,
        "authors": [{"name": f"Author S{index}"}],
        "externalIds": {"DOI": doi.format(i=index)} if doi else {},
        "publicationTypes": ["JournalArticle"],
        "url": f"https://example.org/s2/{index}",
    }


def _s2_body(count: int, total: int) -> bytes:
    return json.dumps(
        {"total": total, "data": [_s2_record(i) for i in range(1, count + 1)]}
    ).encode("utf-8")


def _openalex_body() -> bytes:
    inverted = {"Reconstructed": [0], "openalex": [1], "abstract": [2], "text": [3]}
    return json.dumps(
        {
            "meta": {"count": 2},
            "results": [
                {
                    "id": "https://openalex.org/W1",
                    "doi": "https://doi.org/10.5555/oa-1",
                    "display_name": "Synthetic OpenAlex result one",
                    "publication_year": 2021,
                    "authorships": [{"author": {"display_name": "Author O1"}}],
                    "language": "en",
                    "type": "article",
                    "abstract_inverted_index": inverted,
                },
                {
                    "id": "https://openalex.org/W2",
                    "doi": None,
                    "display_name": "Synthetic OpenAlex result two",
                    "publication_year": None,
                    "authorships": [],
                    "language": None,
                    "type": "dataset",
                    "abstract_inverted_index": None,
                },
            ],
        }
    ).encode("utf-8")


def _crossref_body() -> bytes:
    return json.dumps(
        {
            "message": {
                "total-results": 1,
                "items": [
                    {
                        "DOI": "10.5555/cr-1",
                        "title": ["Synthetic Crossref result"],
                        "author": [{"family": "Crosser", "given": "C."}],
                        "issued": {"date-parts": [[2019, 4]]},
                        "type": "journal-article",
                        "URL": "https://example.org/cr/1",
                        "language": "en",
                    }
                ],
            }
        }
    ).encode("utf-8")


def _arxiv_body() -> bytes:
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<feed xmlns="http://www.w3.org/2005/Atom" '
        'xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/">'
        "<opensearch:totalResults>1</opensearch:totalResults>"
        "<entry>"
        "<id>http://arxiv.org/abs/2408.00001v1</id>"
        "<title>Synthetic arXiv result</title>"
        "<summary>A synthetic preprint abstract.</summary>"
        "<published>2024-08-01T00:00:00Z</published>"
        "<author><name>Author A1</name></author>"
        "</entry>"
        "</feed>"
    ).encode("utf-8")


class FakeTransport:
    def __init__(self, routes: dict[str, tuple[int, bytes] | Exception]):
        self.routes = routes
        self.calls: list[str] = []

    def __call__(self, url: str, headers: dict[str, str], timeout: float):
        self.calls.append(url)
        for marker, response in self.routes.items():
            if marker in url:
                if isinstance(response, Exception):
                    raise response
                return response
        raise AssertionError(f"unrouted url {url}")


def _happy_transport() -> FakeTransport:
    return FakeTransport(
        {
            "semanticscholar.org": (200, _s2_body(2, 2)),
            "openalex.org": (200, _openalex_body()),
            "crossref.org": (200, _crossref_body()),
            "arxiv.org": (200, _arxiv_body()),
        }
    )


def test_retrieve_produces_schema_valid_retrieval_input():
    plan = _live_plan()
    transport = _happy_transport()
    retained = discovery.retrieve(plan, transport=transport)
    ledger.validate_schema(
        retained, "retrieval_input.schema.json", "retrieval input"
    )
    assert retained["query_plan_sha256"] == plan["plan_sha256"]
    assert retained["relevance_assessments"] == []
    assert retained["retry_authorizations"] == []
    assert len(retained["attempts"]) == 4
    assert all(row["outcome"] == "success" for row in retained["attempts"])
    assert {row["index_id"] for row in retained["attempts"]} == set(LIVE_INDEX_IDS)
    assert len(transport.calls) == 4
    assert retained["retrieval_input_sha256"] == ledger.bound_digest(
        retained, "retrieval_input_sha256"
    )
    hits_by_index: dict[str, list[dict]] = {}
    for hit in retained["raw_hits"]:
        hits_by_index.setdefault(hit["index_id"], []).append(hit)
    assert len(hits_by_index["semantic_scholar"]) == 2
    assert len(hits_by_index["openalex"]) == 2
    assert len(hits_by_index["crossref"]) == 1
    assert len(hits_by_index["arxiv"]) == 1
    openalex_hits = sorted(
        hits_by_index["openalex"], key=lambda row: row["provider_rank"]
    )
    assert openalex_hits[0]["abstract_text"] == "Reconstructed openalex abstract text"
    assert openalex_hits[0]["abstract_state"] == "available"
    assert openalex_hits[0]["doi"] == "10.5555/oa-1"
    assert openalex_hits[1]["abstract_state"] == "missing"
    assert openalex_hits[1]["abstract_text"] is None
    arxiv_hit = hits_by_index["arxiv"][0]
    assert arxiv_hit["publication_status"] == "preprint"
    assert arxiv_hit["abstract_text"] == "A synthetic preprint abstract."
    for hit in retained["raw_hits"]:
        if hit["abstract_text"] is not None:
            assert hit["abstract_sha256"] == ledger.text_digest(hit["abstract_text"])


def test_provider_overflow_is_truncated_at_the_adapter_boundary():
    plan = _live_plan(index_ids=["semantic_scholar"])
    transport = FakeTransport({"semanticscholar.org": (200, _s2_body(25, 90))})
    retained = discovery.retrieve(plan, transport=transport)
    attempt = retained["attempts"][0]
    assert attempt["provider_reported_count"] == 90
    assert attempt["returned_count"] == 25
    assert attempt["retained_hit_count"] == 20
    assert attempt["truncated_count"] == 5
    assert len(retained["raw_hits"]) == 20


@pytest.mark.parametrize(
    "response, outcome",
    [
        ((429, b"slow down"), "rate_limited"),
        ((503, b"down"), "service_unavailable"),
        ((500, b"boom"), "service_unavailable"),
        ((401, b"no"), "authentication_failed"),
        ((403, b"no"), "authentication_failed"),
        ((200, b"{not json"), "malformed_response"),
        (TimeoutError("slow"), "timeout"),
        (discovery.ServiceUnreachable("dns"), "service_unavailable"),
    ],
)
def test_failure_vocabulary_is_closed_and_never_retried(response, outcome):
    plan = _live_plan(index_ids=["semantic_scholar"])
    transport = FakeTransport({"semanticscholar.org": response})
    retained = discovery.retrieve(plan, transport=transport)
    attempt = retained["attempts"][0]
    assert attempt["outcome"] == outcome
    assert attempt["retained_hit_count"] == 0
    assert retained["raw_hits"] == []
    assert len(transport.calls) == 1
    ledger.validate_schema(
        retained, "retrieval_input.schema.json", "retrieval input"
    )


def test_arxiv_with_year_filter_is_unsupported_without_a_network_call():
    plan = _live_plan(
        index_ids=["arxiv"], date_filter={"from_year": 2020, "through_year": 2026}
    )
    transport = FakeTransport({})
    retained = discovery.retrieve(plan, transport=transport)
    attempt = retained["attempts"][0]
    assert attempt["outcome"] == "unsupported_query"
    assert transport.calls == []


def test_partial_failure_keeps_successful_indexes_and_failed_attempt_rows():
    plan = _live_plan(index_ids=["semantic_scholar", "crossref"])
    transport = FakeTransport(
        {
            "semanticscholar.org": (200, _s2_body(2, 2)),
            "crossref.org": (503, b"down"),
        }
    )
    retained = discovery.retrieve(plan, transport=transport)
    outcomes = {row["index_id"]: row["outcome"] for row in retained["attempts"]}
    assert outcomes == {
        "semantic_scholar": "success",
        "crossref": "service_unavailable",
    }
    assert {hit["index_id"] for hit in retained["raw_hits"]} == {"semantic_scholar"}


def test_roster_defaults_match_the_query_plan_provider_contract():
    for index_id, provider in discovery.provider_roster_defaults().items():
        assert provider["index_id"] == index_id
        assert provider["purpose"] == "scholarly_discovery"
        # Honest retention default: unknown with a null reference.
        assert provider["retention_state"] == "unknown"
        assert provider["retention_reference"] is None
    plan = _live_plan()
    ledger.validate_plan(plan)


def test_unknown_index_in_plan_fails_closed_before_any_call():
    plan = _live_plan(index_ids=["semantic_scholar"])
    plan["provider_roster"][0]["index_id"] = "mystery_index"
    plan["queries"][0]["index_targets"] = ["mystery_index"]
    _rehash_plan(plan)
    transport = FakeTransport({})
    with pytest.raises(discovery.DiscoveryError, match="mystery_index"):
        discovery.retrieve(plan, transport=transport)
    assert transport.calls == []


def test_session_only_consent_refuses_writing_retrieval_output(tmp_path):
    plan = _live_plan()
    plan["consent"]["local_persistence"] = "session_only"
    plan["consent"]["export_boundary"] = "No local persistence is authorized."
    plan["consent"]["authorized_output_path"] = None
    _rehash_plan(plan)
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(json.dumps(plan), encoding="utf-8")
    output = tmp_path / "retrieval-input.json"
    exit_code = discovery.main(
        ["retrieve", "--query-plan", str(plan_path), "--output", str(output)]
    )
    assert exit_code == 1
    assert not output.exists()


def test_cli_writes_exclusively_and_never_overwrites(tmp_path):
    authorized = str(tmp_path / "candidate-ledger.json")
    plan = _live_plan(
        index_ids=["semantic_scholar"], authorized_output_path=authorized
    )
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(json.dumps(plan), encoding="utf-8")
    fixture_path = tmp_path / "fixture.json"
    fixture_path.write_text(
        json.dumps(
            {"semanticscholar.org": {"status": 200, "body_json": json.loads(_s2_body(2, 2))}}
        ),
        encoding="utf-8",
    )
    output = Path(authorized + discovery.RETRIEVAL_INPUT_SUFFIX)
    exit_code = discovery.main(
        [
            "retrieve",
            "--query-plan",
            str(plan_path),
            "--output",
            str(output),
            "--transport-fixture",
            str(fixture_path),
        ]
    )
    assert exit_code == 0
    retained = json.loads(output.read_text(encoding="utf-8"))
    ledger.validate_schema(
        retained, "retrieval_input.schema.json", "retrieval input"
    )
    assert (
        discovery.main(
            [
                "retrieve",
                "--query-plan",
                str(plan_path),
                "--output",
                str(output),
                "--transport-fixture",
                str(fixture_path),
            ]
        )
        == 1
    )


def test_output_path_must_match_the_hash_bound_consent(tmp_path):
    authorized = str(tmp_path / "candidate-ledger.json")
    plan = _live_plan(
        index_ids=["semantic_scholar"], authorized_output_path=authorized
    )
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(json.dumps(plan), encoding="utf-8")
    fixture_path = tmp_path / "fixture.json"
    fixture_path.write_text(
        json.dumps(
            {"semanticscholar.org": {"status": 200, "body_json": json.loads(_s2_body(1, 1))}}
        ),
        encoding="utf-8",
    )
    elsewhere = tmp_path / "elsewhere.json"
    exit_code = discovery.main(
        [
            "retrieve",
            "--query-plan",
            str(plan_path),
            "--output",
            str(elsewhere),
            "--transport-fixture",
            str(fixture_path),
        ]
    )
    assert exit_code == 1
    assert not elsewhere.exists()


@pytest.mark.parametrize(
    "body",
    [
        {"data": ["oops"], "total": 1},
        {"data": [{"title": "t", "authors": ["bob"]}], "total": 1},
    ],
)
def test_malformed_provider_records_become_malformed_response(body):
    plan = _live_plan(index_ids=["semantic_scholar"])
    transport = FakeTransport(
        {"semanticscholar.org": (200, json.dumps(body).encode("utf-8"))}
    )
    retained = discovery.retrieve(plan, transport=transport)
    assert retained["attempts"][0]["outcome"] == "malformed_response"
    assert retained["raw_hits"] == []


def test_live_transport_refuses_provider_redirects():
    handler = discovery._RefuseRedirects()
    assert (
        handler.redirect_request(None, None, 302, "Found", {}, "http://127.0.0.1/x")
        is None
    )
    # A refused redirect surfaces as its 3xx status and maps into the closed
    # vocabulary as service_unavailable.
    assert discovery._status_outcome(302) == "service_unavailable"


def test_fixture_transport_supports_base64_bodies(tmp_path):
    import base64

    fixture_path = tmp_path / "routes.json"
    fixture_path.write_text(
        json.dumps(
            {
                "arxiv.org": {
                    "status": 200,
                    "body_base64": base64.b64encode(_arxiv_body()).decode("ascii"),
                }
            }
        ),
        encoding="utf-8",
    )
    transport = discovery._fixture_transport(fixture_path)
    status, body = transport("https://export.arxiv.org/api/query?x", {}, 1.0)
    assert status == 200
    assert body == _arxiv_body()


def test_tampered_roster_block_fails_closed_before_any_call():
    plan = _live_plan(index_ids=["semantic_scholar"])
    plan["provider_roster"][0]["product_identity"] = "Someone Else's Index"
    _rehash_plan(plan)
    transport = FakeTransport({})
    with pytest.raises(discovery.DiscoveryError, match="does not match"):
        discovery.retrieve(plan, transport=transport)
    assert transport.calls == []


def test_provider_contract_violation_poisons_only_its_own_attempt():
    plan = _live_plan(index_ids=["semantic_scholar", "crossref"])
    bad = _s2_record(1)
    bad["title"] = "x" * 5000
    transport = FakeTransport(
        {
            "semanticscholar.org": (
                200,
                json.dumps({"total": 1, "data": [bad]}).encode("utf-8"),
            ),
            "crossref.org": (200, _crossref_body()),
        }
    )
    retained = discovery.retrieve(plan, transport=transport)
    outcomes = {row["index_id"]: row["outcome"] for row in retained["attempts"]}
    assert outcomes == {
        "semantic_scholar": "malformed_response",
        "crossref": "success",
    }
    assert {hit["index_id"] for hit in retained["raw_hits"]} == {"crossref"}
    ledger.validate_schema(
        retained, "retrieval_input.schema.json", "retrieval input"
    )


def test_underreported_provider_count_is_malformed():
    plan = _live_plan(index_ids=["semantic_scholar"])
    transport = FakeTransport({"semanticscholar.org": (200, _s2_body(2, 1))})
    retained = discovery.retrieve(plan, transport=transport)
    assert retained["attempts"][0]["outcome"] == "malformed_response"
    assert retained["raw_hits"] == []


def test_arxiv_refuses_quote_bearing_queries_before_transport():
    plan = _live_plan(index_ids=["arxiv"])
    quoted = 'The term "X" improves outcomes.'
    plan["claim"]["claim_text"] = quoted
    plan["queries"][0]["accepted_query_text"] = quoted
    plan["queries"][0]["original_query_text"] = quoted
    _rehash_plan(plan)
    transport = FakeTransport({})
    retained = discovery.retrieve(plan, transport=transport)
    assert retained["attempts"][0]["outcome"] == "unsupported_query"
    assert transport.calls == []


def test_plain_4xx_maps_to_unsupported_query():
    plan = _live_plan(index_ids=["crossref"])
    transport = FakeTransport({"crossref.org": (400, b"bad request")})
    retained = discovery.retrieve(plan, transport=transport)
    assert retained["attempts"][0]["outcome"] == "unsupported_query"


def test_abstract_text_is_retained_exactly():
    record = _s2_record(1)
    record["abstract"] = "Line one.\n   Line   two."
    plan = _live_plan(index_ids=["semantic_scholar"])
    transport = FakeTransport(
        {
            "semanticscholar.org": (
                200,
                json.dumps({"total": 1, "data": [record]}).encode("utf-8"),
            )
        }
    )
    retained = discovery.retrieve(plan, transport=transport)
    assert retained["raw_hits"][0]["abstract_text"] == "Line one.\n   Line   two."


def test_publication_status_maps_conservatively():
    plan = _live_plan()
    retained = discovery.retrieve(plan, transport=_happy_transport())
    status_by_index = {}
    for hit in retained["raw_hits"]:
        status_by_index.setdefault(hit["index_id"], set()).add(
            hit["publication_status"]
        )
    assert status_by_index["semantic_scholar"] == {"published"}
    assert status_by_index["openalex"] == {"published", "unknown"}
    assert status_by_index["crossref"] == {"published"}
    assert status_by_index["arxiv"] == {"preprint"}


def test_untyped_provider_count_is_malformed():
    plan = _live_plan(index_ids=["semantic_scholar"])
    body = json.dumps(
        {"total": "1", "data": [_s2_record(1)]}
    ).encode("utf-8")
    transport = FakeTransport({"semanticscholar.org": (200, body)})
    retained = discovery.retrieve(plan, transport=transport)
    assert retained["attempts"][0]["outcome"] == "malformed_response"
    assert retained["raw_hits"] == []


def test_nonsemantic_provider_record_id_poisons_only_its_attempt():
    record = _s2_record(1)
    record["paperId"] = "---"
    plan = _live_plan(index_ids=["semantic_scholar", "crossref"])
    transport = FakeTransport(
        {
            "semanticscholar.org": (
                200,
                json.dumps({"total": 1, "data": [record]}).encode("utf-8"),
            ),
            "crossref.org": (200, _crossref_body()),
        }
    )
    retained = discovery.retrieve(plan, transport=transport)
    outcomes = {row["index_id"]: row["outcome"] for row in retained["attempts"]}
    assert outcomes == {
        "semantic_scholar": "malformed_response",
        "crossref": "success",
    }


def test_discovery_module_never_touches_the_pinned_resolver_clients():
    source = (SCRIPTS / "claim_standing_discovery.py").read_text(encoding="utf-8")
    for forbidden in (
        "arxiv_client",
        "openalex_client",
        "crossref_client",
        "semantic_scholar_client",
        "chinese_literature_client",
    ):
        assert forbidden not in source
