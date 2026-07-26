#!/usr/bin/env python3
"""Tests for the Chinese-literature resolver client (#595).

Per `deep-research/references/chinese_literature_api_protocol.md`. Structure
mirrors `test_arxiv_client.py` (per-client unit suite) but uses the
transport-fixture discipline of `test_transport_fixture_citation_gate.py`: the
REAL `ChineseLiteratureClient` builds the URLs and parses the bodies, and a
URL-dispatch fake stands in for the socket. Every body is checked in under
`scripts/fixtures/transport_bodies/chinese_literature/` and is fully synthetic
(see that directory's README).

ZERO live network. The protocol doc's live examples are a record of a manual
verification; nothing here contacts doi.org, hdl.handle.net, or NCBI.
"""
from __future__ import annotations

import http.client
import io
import sys
import urllib.error
import urllib.parse
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

FIXTURES = REPO_ROOT / "scripts" / "fixtures" / "transport_bodies" / "chinese_literature"

# Synthetic identifiers pinned to the fixture bodies (see the fixtures README):
# 10.5555 is the reserved DOI example/test prefix and resolves nowhere.
ISTIC_DOI = "10.5555/ars.cn.istic.2026.0042"
CNKI_DOI = "10.5555/ars.cn.cnki.2026.0042"
FABRICATED_DOI = "10.5555/ars.cn.istic.9999.9999"

CN_TITLE = "合成引文核验闸的确定性评估方法研究"
CN_JOURNAL = "合成测试医学杂志"

# Injected through the client's documented extension point, so no test depends
# on the shipped seed table's contents.
TEST_JOURNAL_MAP = {
    CN_JOURNAL: {
        "issn": "0000-0000",
        "nlm_ta": "Hecheng Ceshi Yi Xue Za Zhi",
        "nlm_id": "999999901",
        "display_name": CN_JOURNAL,
    }
}


def _body(name: str) -> bytes:
    return FIXTURES.joinpath(name).read_bytes()


@pytest.fixture(autouse=True)
def _no_real_sleep(monkeypatch):
    """Pacing must never burn wall-clock in CI. Patched on the client module so
    a `time.sleep` that leaks in from elsewhere still fails loudly."""
    monkeypatch.setattr("chinese_literature_client.time.sleep", lambda seconds: None)


def _client(**kwargs):
    from chinese_literature_client import ChineseLiteratureClient

    return ChineseLiteratureClient(**kwargs)


class FakeTransport:
    """urlopen stand-in dispatching on the REAL URL the client built.

    `routes` is an ordered list of `(predicate, action)`; predicates receive
    `(urlsplit_result, parse_qs_dict)`. An unrouted URL is an immediate test
    failure — the dispatch table doubles as an assertion that the client
    contacted exactly the documented endpoints. AssertionError is not in the
    client's degradation except-list, so it propagates instead of being
    laundered into ChineseLiteratureUnavailable.
    """

    def __init__(self, routes):
        self.routes = routes
        self.requests: list[str] = []

    def __call__(self, req, timeout=None):
        url = req.full_url
        self.requests.append(url)
        parsed = urllib.parse.urlsplit(url)
        query = (
            urllib.parse.parse_qs(
                parsed.query, keep_blank_values=True, strict_parsing=True)
            if parsed.query else {}
        )
        for predicate, action in self.routes:
            if predicate(parsed, query):
                return action(url)
        raise AssertionError(f"client contacted an unrouted URL: {url}")


def _ok(body: bytes):
    def action(url):
        resp = MagicMock()
        resp.status = 200
        resp.read.return_value = body
        resp.__enter__ = MagicMock(return_value=resp)
        resp.__exit__ = MagicMock(return_value=None)
        return resp

    return action


def _http_error(code: int, body: bytes = b""):
    def action(url):
        raise urllib.error.HTTPError(
            url=url, code=code, msg="synthetic", hdrs={}, fp=io.BytesIO(body),
        )

    return action


# Route predicates, written against host+path so an accidental endpoint change
# in the client fails routing rather than silently following along.
def _is_ra(parsed, query):
    return parsed.netloc == "doi.org" and parsed.path.startswith("/ra/")


def _is_doi_resolve(parsed, query):
    return parsed.netloc == "doi.org" and not parsed.path.startswith("/ra/")


def _is_handle(parsed, query):
    return parsed.netloc == "hdl.handle.net" and parsed.path.startswith("/api/handles/")


def _is_esearch(parsed, query):
    return parsed.path.endswith("/esearch.fcgi")


def _is_esummary(parsed, query):
    return parsed.path.endswith("/esummary.fcgi")


# ---------------------------------------------------------------- pure helpers


def test_normalize_folds_the_three_measured_chinese_variants():
    """The shared #431 normalizer rejects three legitimate spellings of one
    identical Chinese title (measured 2026-07-27: fullwidth 0.577/False, CJK
    terminal punctuation 0.981/False, interior spaces 0.929/False). The
    Chinese-aware normalizer must fold all three to one string."""
    from chinese_literature_client import normalize_cn_title

    canonical = normalize_cn_title("宫颈腺癌中ProEXC和PRMT5的表达及其临床意义")
    assert normalize_cn_title("宫颈腺癌中ＰｒｏＥＸＣ和ＰＲＭＴ５的表达及其临床意义") == canonical
    assert normalize_cn_title("宫颈腺癌中ProEXC和PRMT5的表达及其临床意义。") == canonical
    assert normalize_cn_title("宫颈腺癌中 ProEXC 和 PRMT5 的表达及其临床意义") == canonical
    assert normalize_cn_title("《宫颈腺癌中ProEXC和PRMT5的表达及其临床意义》") == canonical


def test_fuzzy_similarity_alone_never_promotes_a_different_paper():
    """Han-character overlap gives unrelated Chinese papers a high baseline
    ratio (0.510 measured between two genuinely different papers), so the
    shared fuzzy ratio is not sufficient — exact equality after Chinese-aware
    normalization is the rule."""
    from chinese_literature_client import _cn_titles_match

    a = "宫颈腺癌中ProEXC和PRMT5的表达及其临床意义"
    b = "宫颈癌及癌前病变组织hTERC基因表达及其临床意义"
    assert _cn_titles_match(a, a) is True
    assert _cn_titles_match(b, a) is False


def test_legitimate_variants_match_despite_a_sub_threshold_fuzzy_ratio():
    """Regression for a live-smoke near-miss: the shared 0.70 ratio scores a
    legitimate FULLWIDTH spelling of the identical title at 0.577, so ANDing it
    in as an extra necessary condition would veto a correct match and file a
    real paper at P0 next to the word 'fabricated'. On CJK the ratio separates
    almost nothing (0.510 unrelated vs 0.577 identical), so it is excluded."""
    from _text_similarity import _TITLE_SIMILARITY_THRESHOLD, _similarity
    from chinese_literature_client import _cn_titles_match

    canonical = "宫颈腺癌中ProEXC和PRMT5的表达及其临床意义"
    fullwidth = "宫颈腺癌中ＰｒｏＥＸＣ和ＰＲＭＴ５的表达及其临床意义。"

    # The premise: the shared ratio really is below the floor for this pair.
    assert _similarity(canonical, fullwidth) < _TITLE_SIMILARITY_THRESHOLD
    # ...and the Chinese-aware rule still matches it.
    assert _cn_titles_match(fullwidth, canonical) is True
    assert _cn_titles_match(canonical, fullwidth) is True


def test_generic_title_expectation_is_never_promoted():
    """#431 §0.12.2 carries over: a generic expected title cannot match."""
    from chinese_literature_client import _cn_titles_match

    assert _cn_titles_match("Editorial", "Editorial") is False


def test_applicability_gate_skips_non_chinese_citations():
    """Mirrors _run_arxiv's skip semantics — an English citation must be
    `skipped`, never `unmatched`, so English corpora are untouched."""
    client = _client()
    assert client.is_applicable({"title": "Attention Is All You Need"}) is False
    assert client.is_applicable({"title": CN_TITLE}) is True
    assert client.is_applicable({"container_title": CN_JOURNAL}) is True
    assert client.is_applicable({"title": "A Study", "language": "zh"}) is True
    # A Chinese RA on the DOI is sufficient even with a romanized title.
    assert client.is_applicable({"title": "A Study"}, ra="ISTIC") is True


def test_resolve_skips_non_chinese_without_touching_the_network():
    """An English citation must cost ZERO requests — including when it carries
    a DOI. Establishing applicability from the registration agency would mean
    one doi.org round-trip per English reference in every bibliography."""
    client = _client()
    with patch("urllib.request.urlopen", side_effect=AssertionError("no network")):
        result = client.resolve({
            "citation_key": "smith2020",
            "title": "An English Paper",
            "doi": "10.5555/english.2020.1",
        })
    assert result["status"] == "skipped"
    assert result["queried_by"] is None
    assert result["reason_code"] == "NOT_CHINESE_LITERATURE"
    assert result["checklist_item"] is None


# ------------------------------------------------------- RA triage (3 branches)


@pytest.mark.parametrize(
    "fixture,expected",
    [
        ("ra_istic.json", "ISTIC"),
        ("ra_cnki.json", "CNKI"),
        ("ra_crossref.json", "Crossref"),
    ],
)
def test_ra_lookup_routes_all_three_agencies(fixture, expected):
    transport = FakeTransport([(_is_ra, _ok(_body(fixture)))])
    with patch("urllib.request.urlopen", transport):
        assert _client().ra_for(ISTIC_DOI) == expected
    assert transport.requests == ["https://doi.org/ra/10.5555"]


def test_ra_lookup_returns_none_for_an_unknown_prefix():
    """The endpoint does not error on an unknown prefix: it answers 200 with a
    `status` field in place of `RA` (verified 2026-07-27: `/ra/10.99999` ->
    `[{"DOI": "10.99999", "status": "DOI does not exist"}]`). The missing RA
    key must yield None, never a degradation or a fabricated agency name."""
    transport = FakeTransport([(_is_ra, _ok(_body("ra_unknown_prefix.json")))])
    with patch("urllib.request.urlopen", transport):
        assert _client().ra_for("10.99999/ars.cn.unknown.2026.1") is None


def test_ra_lookup_short_circuits_a_non_doi_without_a_request():
    transport = FakeTransport([])
    with patch("urllib.request.urlopen", transport):
        assert _client().ra_for("not-a-doi") is None
    assert transport.requests == []


def test_crossref_registered_chinese_doi_is_not_claimed():
    """Division of labour: a Crossref-registered Chinese DOI belongs to the
    existing crossref resolver. This resolver must fall through to the
    coordinate branch rather than re-query Crossref's territory."""
    transport = FakeTransport([
        (_is_ra, _ok(_body("ra_crossref.json"))),
        (_is_doi_resolve, _http_error(500)),  # must never be reached
        (_is_handle, _http_error(500)),       # must never be reached
    ])
    with patch("urllib.request.urlopen", transport):
        result = _client().resolve({
            "citation_key": "chen2026",
            "title": CN_TITLE,
            "container_title": "某本未映射的期刊",
            "doi": "10.5555/crossref.zh.2026.1",
        })
    assert result["reason_code"] == "NO_ISSN_MAPPING"
    assert result["status"] == "skipped"
    assert len(transport.requests) == 1  # RA lookup only


# ------------------------------------------------------------ ISTIC DOI branch


def _istic_entry(**overrides):
    entry = {
        "citation_key": "hecheng2026",
        "title": CN_TITLE,
        "container_title": CN_JOURNAL,
        "year": 2026,
        "volume": "88",
        "pages": "8801-8809",
        "doi": ISTIC_DOI,
    }
    entry.update(overrides)
    return entry


def test_istic_doi_hit_with_matching_chinese_title_is_matched_by_id():
    transport = FakeTransport([
        (_is_ra, _ok(_body("ra_istic.json"))),
        (_is_doi_resolve, _ok(_body("istic_csl_hit.json"))),
    ])
    with patch("urllib.request.urlopen", transport):
        result = _client().resolve(_istic_entry())

    assert result["status"] == "matched"
    assert result["queried_by"] == "id"
    assert result["reason_code"] == "DOI_TITLE_VERIFIED"
    assert result["evidence"]["title"] == CN_TITLE
    assert result["evidence"]["container_title"] == CN_JOURNAL
    assert result["evidence"]["year"] == 2026
    assert result["checklist_item"] is None
    # Exactly two requests: no Handle probe is needed once the title verifies.
    assert len(transport.requests) == 2


def test_istic_doi_hit_matches_a_typeset_variant_of_the_cited_title():
    """End-to-end companion to the unit regression: a citation whose title
    differs from the record only by fullwidth forms, CJK punctuation and
    interior spaces must MATCH, not land at P0. Typesetting differences between
    a reference list and a metadata record are ordinary, not evidence."""
    variant = "合成 引文核验闸 的确定性评估方法研究。"
    transport = FakeTransport([
        (_is_ra, _ok(_body("ra_istic.json"))),
        (_is_doi_resolve, _ok(_body("istic_csl_hit.json"))),
    ])
    with patch("urllib.request.urlopen", transport):
        result = _client().resolve(_istic_entry(title=variant))

    assert result["status"] == "matched"
    assert result["queried_by"] == "id"
    assert result["checklist_item"] is None


def test_istic_doi_resolving_to_a_different_title_is_id_keyed_unmatched():
    """Chimeric citation (real identifier, someone else's title). ID-keyed
    unmatched is the C-V6(a) shape that licenses a `false`, and it is a P0 row."""
    transport = FakeTransport([
        (_is_ra, _ok(_body("ra_istic.json"))),
        (_is_doi_resolve, _ok(_body("istic_csl_other_title.json"))),
        (_is_handle, _ok(_body("handle_exists.json"))),
    ])
    with patch("urllib.request.urlopen", transport):
        result = _client().resolve(_istic_entry())

    assert result["status"] == "unmatched"
    assert result["queried_by"] == "id"
    assert result["reason_code"] == "DOI_TITLE_MISMATCH"
    item = result["checklist_item"]
    assert item["priority"] == "P0"
    assert item["verdict_contribution"] == "false"
    assert item["human_result"] is None


def test_fabricated_doi_is_refuted_by_404_plus_handle_100():
    """The fabrication canary: these prefixes carry no wildcard catch-all, so a
    404 + responseCode 100 is positive evidence the identifier does not exist."""
    transport = FakeTransport([
        (_is_ra, _ok(_body("ra_istic.json"))),
        (_is_doi_resolve, _http_error(404)),
        (_is_handle, _ok(_body("handle_absent.json"))),
    ])
    with patch("urllib.request.urlopen", transport):
        result = _client().resolve(_istic_entry(doi=FABRICATED_DOI))

    assert result["status"] == "unmatched"
    assert result["queried_by"] == "id"
    assert result["reason_code"] == "DOI_REFUTED"
    item = result["checklist_item"]
    assert item["priority"] == "P0"
    assert item["verdict_contribution"] == "false"


def test_doi_404_is_a_negative_not_a_degradation():
    """A 404 on the DOI path must be reported as data. Turning it into an
    outage would throw away the resolver's strongest signal."""
    from chinese_literature_client import ChineseLiteratureUnavailable

    transport = FakeTransport([(_is_doi_resolve, _http_error(404))])
    with patch("urllib.request.urlopen", transport):
        client = _client()
        try:
            assert client.doi_lookup_with_title_check(FABRICATED_DOI, CN_TITLE) is None
        except ChineseLiteratureUnavailable:  # pragma: no cover - failure path
            pytest.fail("a DOI 404 must be a negative, not a degradation")


# ------------------------------------------------------------- CNKI DOI branch


def test_cnki_doi_that_exists_is_never_matched():
    """The CNKI RA serves no CSL-JSON and we refuse to parse its HTML, so
    existence alone must degrade to title-keyed unmatched (-> unresolvable),
    never `matched` — otherwise a real DOI with a fabricated title passes."""
    transport = FakeTransport([
        (_is_ra, _ok(_body("ra_cnki.json"))),
        (_is_handle, _ok(_body("handle_exists.json"))),
        (_is_doi_resolve, _http_error(500)),  # must never be reached
    ])
    with patch("urllib.request.urlopen", transport):
        result = _client().resolve(_istic_entry(doi=CNKI_DOI))

    assert result["status"] == "unmatched"
    assert result["queried_by"] == "title"  # NOT "id" -> reduces to unresolvable
    assert result["reason_code"] == "DOI_EXISTS_TITLE_UNVERIFIABLE"
    item = result["checklist_item"]
    assert item["priority"] == "P2"
    assert item["verdict_contribution"] == "unresolvable"
    assert item["verification_urls"] == ["https://doi.org/" + CNKI_DOI]
    # Content negotiation is never attempted for a CNKI prefix.
    assert len(transport.requests) == 2


def test_cnki_doi_that_does_not_exist_is_still_refuted():
    transport = FakeTransport([
        (_is_ra, _ok(_body("ra_cnki.json"))),
        (_is_handle, _ok(_body("handle_absent.json"))),
    ])
    with patch("urllib.request.urlopen", transport):
        result = _client().resolve(_istic_entry(doi=CNKI_DOI))

    assert result["queried_by"] == "id"
    assert result["reason_code"] == "DOI_REFUTED"


def test_non_csl_200_body_is_unverifiable_not_a_miss():
    """#331 discipline, Chinese variant: a 200 that is not CSL-JSON (the CNKI
    HTML landing page, or a proxy error page) must not become a miss. It maps to
    title-keyed unmatched + a P2 row."""
    transport = FakeTransport([
        (_is_ra, _ok(_body("ra_istic.json"))),
        (_is_doi_resolve, _ok(_body("cnki_landing_page.html"))),
    ])
    with patch("urllib.request.urlopen", transport):
        result = _client().resolve(_istic_entry())

    assert result["status"] == "unmatched"
    assert result["queried_by"] == "title"
    assert result["reason_code"] == "DOI_EXISTS_TITLE_UNVERIFIABLE"
    assert result["checklist_item"]["priority"] == "P2"


def test_handle_unknown_response_code_degrades():
    """responseCode 2 (internal error) is an unknown state — degrade, do not
    guess an existence answer."""
    from chinese_literature_client import ChineseLiteratureUnavailable

    transport = FakeTransport([(_is_handle, _ok(_body("handle_internal_error.json")))])
    with patch("urllib.request.urlopen", transport):
        with pytest.raises(ChineseLiteratureUnavailable):
            _client().handle_exists(ISTIC_DOI)


# --------------------------------------------------- PubMed coordinate branch


def _coordinate_entry(**overrides):
    entry = {
        "citation_key": "hecheng2026",
        "title": CN_TITLE,
        "container_title": CN_JOURNAL,
        "year": 2026,
        "volume": "88",
        "pages": "8801-8809",
    }
    entry.update(overrides)
    return entry


def _coordinate_client():
    return _client(journal_map=TEST_JOURNAL_MAP)


def test_pubmed_coordinate_hit_is_matched_by_title():
    """A unique [ta]+[vi]+[pg] hit with an agreeing year is a match — but keyed
    by `title`, never `id`: a coordinate tuple is not an identifier, so it can
    never contribute a `false`."""
    esearch_bodies = [_body("esearch_coverage_hit.json"),
                      _body("esearch_coordinate_hit.json")]
    transport = FakeTransport([
        (_is_esearch, lambda url: _ok(esearch_bodies.pop(0))(url)),
        (_is_esummary, _ok(_body("esummary_hit.json"))),
    ])
    with patch("urllib.request.urlopen", transport):
        result = _coordinate_client().resolve(_coordinate_entry())

    assert result["status"] == "matched"
    assert result["queried_by"] == "title"
    assert result["reason_code"] == "PUBMED_COORDINATE_VERIFIED"
    assert result["evidence"]["pmid"] == "999999901"
    assert result["evidence"]["doi"] == ISTIC_DOI
    # PubMed stores the ENGLISH bracketed shadow title for Chinese articles, so
    # a Chinese title cross-check is structurally impossible on this branch —
    # the shadow title is carried for the human instead.
    assert result["evidence"]["english_title"].startswith("[")
    assert result["checklist_item"] is None


def test_pubmed_coordinate_miss_is_p1_never_false():
    """The single most important self-restraint in the design: coverage is
    confirmed and the coordinates return nothing, yet the outcome stays
    title-keyed (-> unresolvable). The strength goes into the P1 priority, not
    into the verdict — the journal bridge is heuristic and PubMed indexes
    Chinese journals selectively."""
    esearch_bodies = [_body("esearch_coverage_hit.json"),
                      _body("esearch_coordinate_zero.json")]
    transport = FakeTransport([
        (_is_esearch, lambda url: _ok(esearch_bodies.pop(0))(url)),
    ])
    with patch("urllib.request.urlopen", transport):
        result = _coordinate_client().resolve(_coordinate_entry(pages="9999"))

    assert result["status"] == "unmatched"
    assert result["queried_by"] == "title"
    assert result["reason_code"] == "PUBMED_INDEXED_BUT_COORDINATE_MISS"
    item = result["checklist_item"]
    assert item["priority"] == "P1"
    assert item["verdict_contribution"] == "unresolvable"
    # Wording discipline: fabrication vocabulary is P0-only.
    assert "pending human check" in item["human_action"].lower()
    assert "fabricat" not in item["human_action"].lower()


def test_pubmed_coordinate_ambiguity_never_picks_one():
    esearch_bodies = [_body("esearch_coverage_hit.json"),
                      _body("esearch_coordinate_ambiguous.json")]
    transport = FakeTransport([
        (_is_esearch, lambda url: _ok(esearch_bodies.pop(0))(url)),
    ])
    with patch("urllib.request.urlopen", transport):
        result = _coordinate_client().resolve(_coordinate_entry())

    assert result["reason_code"] == "PUBMED_COORDINATE_AMBIGUOUS"
    assert result["queried_by"] == "title"
    assert result["evidence"] is None
    assert result["checklist_item"]["priority"] == "P1"


def test_pubmed_year_disagreement_demotes_the_hit():
    esearch_bodies = [_body("esearch_coverage_hit.json"),
                      _body("esearch_coordinate_hit.json")]
    transport = FakeTransport([
        (_is_esearch, lambda url: _ok(esearch_bodies.pop(0))(url)),
        (_is_esummary, _ok(_body("esummary_year_mismatch.json"))),
    ])
    with patch("urllib.request.urlopen", transport):
        result = _coordinate_client().resolve(_coordinate_entry())

    assert result["status"] == "unmatched"
    assert result["queried_by"] == "title"
    assert result["reason_code"] == "PUBMED_INDEXED_BUT_COORDINATE_MISS"


def test_pubmed_issn_disagreement_demotes_the_hit():
    """The coordinate hit's corroboration is structural, so the ISSN the record
    echoes must be the ISSN we bridged through — a disagreement means the
    journal-name mapping, not the citation, is likely at fault."""
    esearch_bodies = [_body("esearch_coverage_hit.json"),
                      _body("esearch_coordinate_hit.json")]
    transport = FakeTransport([
        (_is_esearch, lambda url: _ok(esearch_bodies.pop(0))(url)),
        (_is_esummary, _ok(_body("esummary_issn_mismatch.json"))),
    ])
    with patch("urllib.request.urlopen", transport):
        result = _coordinate_client().resolve(_coordinate_entry())

    assert result["status"] == "unmatched"
    assert result["queried_by"] == "title"
    assert result["reason_code"] == "PUBMED_INDEXED_BUT_COORDINATE_MISS"
    assert "ISSN" in result["checklist_item"]["human_action"]


def test_absent_year_does_not_fail_the_hit():
    """Absence is not mismatch: a citation with no year still matches on a
    unique coordinate hit."""
    esearch_bodies = [_body("esearch_coverage_hit.json"),
                      _body("esearch_coordinate_hit.json")]
    transport = FakeTransport([
        (_is_esearch, lambda url: _ok(esearch_bodies.pop(0))(url)),
        (_is_esummary, _ok(_body("esummary_hit.json"))),
    ])
    with patch("urllib.request.urlopen", transport):
        result = _coordinate_client().resolve(_coordinate_entry(year=None))

    assert result["status"] == "matched"


def test_journal_catalogued_but_not_indexed_is_skipped_not_unmatched():
    """'In the NLM Catalog' != 'indexed in PubMed' (中国全科医学 is catalogued
    with zero PubMed articles). A journal PubMed never indexed must produce
    `skipped` + a P3 row, because a coordinate miss against it says nothing."""
    transport = FakeTransport([
        (_is_esearch, _ok(_body("esearch_coverage_zero.json"))),
    ])
    with patch("urllib.request.urlopen", transport):
        result = _coordinate_client().resolve(_coordinate_entry())

    assert result["status"] == "skipped"
    assert result["queried_by"] is None
    assert result["reason_code"] == "JOURNAL_NOT_INDEXED"
    assert result["checklist_item"]["priority"] == "P3"
    # Coverage confirmation only — the coordinate query is never issued.
    assert len(transport.requests) == 1


def test_unmapped_journal_is_skipped_with_a_p3_row():
    """A gap in OUR bridge table is never evidence about the citation."""
    transport = FakeTransport([])
    with patch("urllib.request.urlopen", transport):
        result = _coordinate_client().resolve(
            _coordinate_entry(container_title="某本尚未映射的中文期刊"))

    assert result["status"] == "skipped"
    assert result["reason_code"] == "NO_ISSN_MAPPING"
    assert result["checklist_item"]["priority"] == "P3"
    assert transport.requests == []


def test_seed_journal_map_rows_are_lookup_reachable():
    """The shipped seed rows (all verified live 2026-07-27) must be reachable
    through the same normalization the resolver applies, including 《》 wrapping."""
    client = _client()
    row = client.journal_bridge("中华医学杂志")
    assert row is not None and row["nlm_ta"] == "Zhonghua Yi Xue Za Zhi"
    assert client.journal_bridge("《中华医学杂志》") == row
    assert client.journal_bridge("中华内科杂志")["issn"] == "0578-1426"


def test_caller_journal_map_extends_the_seed():
    """Documented user extension point: caller rows merge over the seed."""
    client = _client(journal_map=TEST_JOURNAL_MAP)
    assert client.journal_bridge(CN_JOURNAL)["nlm_ta"] == "Hecheng Ceshi Yi Xue Za Zhi"
    assert client.journal_bridge("中华医学杂志") is not None  # seed still present


def test_ncbi_api_key_is_passed_through_but_does_not_relax_pacing():
    from chinese_literature_client import _EUTILS_MIN_INTERVAL

    transport = FakeTransport([(_is_esearch, _ok(_body("esearch_coverage_hit.json")))])
    with patch("urllib.request.urlopen", transport):
        client = _client(ncbi_api_key="test-ncbi-key")
        client.journal_is_indexed("Hecheng Ceshi Yi Xue Za Zhi")

    assert "api_key=test-ncbi-key" in transport.requests[0]
    assert _EUTILS_MIN_INTERVAL == 0.34  # the keyless NCBI floor, unconditionally


# -------------------------------------------------- URL hygiene / credentials


def test_malicious_doi_is_encoded_and_never_crashes():
    """A DOI carrying CRLF / query-injection characters must be percent-encoded
    before it reaches the transport (sibling quote discipline) — no raw control
    character or `?`/`#` may survive into the request line, and the client must
    never escape its own degradation contract over a hostile identifier."""
    from chinese_literature_client import ChineseLiteratureUnavailable

    evil = "10.5555/evil\r\nHost: attacker?x=1#frag"
    transport = FakeTransport([
        (_is_handle, _ok(_body("handle_absent.json"))),
    ])
    with patch("urllib.request.urlopen", transport):
        assert _client().handle_exists(evil) is False

    url = transport.requests[0]
    assert "\r" not in url and "\n" not in url
    assert "?" not in url and "#" not in url  # no query/fragment injection
    assert "%0D%0A" in url  # CRLF arrived encoded, not stripped

    # Defense in depth: even if a malformed request slips past encoding and
    # urlopen rejects it (http.client.InvalidURL), the client degrades cleanly.
    def reject(req, timeout=None):
        raise http.client.InvalidURL("URL can't contain control characters")

    with patch("urllib.request.urlopen", reject):
        with pytest.raises(ChineseLiteratureUnavailable):
            _client().handle_exists(evil)


def test_api_key_never_lands_in_exception_text():
    """#495 red line (mirrors crossref/openalex): refusal/degradation messages
    strip the query string so a configured NCBI api_key can never reach logs or
    raised-exception text — checked across the 5xx, network-error and
    unparseable-body paths."""
    from chinese_literature_client import ChineseLiteratureUnavailable

    key = "test-ncbi-key"

    scenarios = [
        FakeTransport([(_is_esearch, _http_error(503))]),
        FakeTransport([(_is_esearch, _ok(_body("error_5xx.html")))]),
    ]
    for transport in scenarios:
        with patch("urllib.request.urlopen", transport):
            with pytest.raises(ChineseLiteratureUnavailable) as excinfo:
                _client(ncbi_api_key=key).journal_is_indexed("Hecheng Ceshi")
        assert key not in str(excinfo.value)
        assert "api_key" not in str(excinfo.value)
        assert "?" not in str(excinfo.value)  # whole query stripped, not just the key

    def net_error(req, timeout=None):
        raise urllib.error.URLError("connection refused")

    with patch("urllib.request.urlopen", net_error):
        with pytest.raises(ChineseLiteratureUnavailable) as excinfo:
            _client(ncbi_api_key=key).journal_is_indexed("Hecheng Ceshi")
    assert key not in str(excinfo.value)
    assert "?" not in str(excinfo.value)


def test_host_allowlist_guard_refuses_and_redacts():
    """Multi-host `_require_api_url` (sibling defense-in-depth): a non-HTTPS or
    non-allowlisted host is refused before any request, and the refusal text is
    query-stripped."""
    from chinese_literature_client import (
        ChineseLiteratureUnavailable,
        _require_api_url,
    )

    _require_api_url("https://doi.org/ra/10.5555")            # allowlisted: no raise
    _require_api_url("https://eutils.ncbi.nlm.nih.gov/x")     # allowlisted: no raise
    for bad in (
        "https://www.cnki.net/search?q=x",       # zero-scraping red line
        "http://doi.org/ra/10.5555",             # https only
        "https://evil.invalid/a?api_key=test-ncbi-key",
    ):
        with pytest.raises(ChineseLiteratureUnavailable) as excinfo:
            _require_api_url(bad)
        assert "api_key" not in str(excinfo.value)
        assert "?" not in str(excinfo.value)


# ------------------------------------------------------- degradation contract


def test_5xx_does_not_retry():
    """Per protocol: 5xx -> fail fast, exactly one request."""
    from chinese_literature_client import ChineseLiteratureUnavailable

    transport = FakeTransport([(_is_ra, _http_error(503, _body("error_5xx.html")))])
    with patch("urllib.request.urlopen", transport):
        with pytest.raises(ChineseLiteratureUnavailable):
            _client().ra_for(ISTIC_DOI)

    assert len(transport.requests) == 1


def test_429_backs_off_then_raises_after_the_shared_retry_budget(monkeypatch):
    from chinese_literature_client import ChineseLiteratureUnavailable
    from _text_similarity import _MAX_RETRIES

    sleeps: list[float] = []
    monkeypatch.setattr("chinese_literature_client.time.sleep", sleeps.append)

    transport = FakeTransport([(_is_ra, _http_error(429))])
    with patch("urllib.request.urlopen", transport):
        with pytest.raises(ChineseLiteratureUnavailable):
            _client().ra_for(ISTIC_DOI)

    assert len(transport.requests) == _MAX_RETRIES + 1
    # Growing backoff, floored at 2s so a retry cannot re-violate the limit the
    # 429 is enforcing (arxiv_client.py's rule).
    assert sleeps == [2.0, 4.0, 6.0]
    assert all(delay >= 2.0 for delay in sleeps)


def test_network_error_raises_unavailable():
    from chinese_literature_client import ChineseLiteratureUnavailable

    def boom(req, timeout=None):
        raise urllib.error.URLError("connection refused")

    with patch("urllib.request.urlopen", boom):
        with pytest.raises(ChineseLiteratureUnavailable):
            _client().ra_for(ISTIC_DOI)


def test_truncated_body_raises_unavailable():
    """IncompleteRead inherits HTTPException, not OSError — a truncated body
    must degrade, never become a miss."""
    from chinese_literature_client import ChineseLiteratureUnavailable

    resp = MagicMock()
    resp.status = 200
    resp.read.side_effect = http.client.IncompleteRead(partial=b"{", expected=200)
    resp.__enter__ = MagicMock(return_value=resp)
    resp.__exit__ = MagicMock(return_value=None)

    with patch("urllib.request.urlopen", return_value=resp):
        with pytest.raises(ChineseLiteratureUnavailable):
            _client().ra_for(ISTIC_DOI)


def test_unparseable_200_body_raises_unavailable():
    """#331: an HTML error page served with 200 by a proxy/CDN must degrade, not
    be recorded as an empty result."""
    from chinese_literature_client import ChineseLiteratureUnavailable

    transport = FakeTransport([(_is_esearch, _ok(_body("error_5xx.html")))])
    with patch("urllib.request.urlopen", transport):
        with pytest.raises(ChineseLiteratureUnavailable):
            _client().journal_is_indexed("Hecheng Ceshi Yi Xue Za Zhi")


def test_unexpected_esearch_shape_raises_unavailable():
    from chinese_literature_client import ChineseLiteratureUnavailable

    transport = FakeTransport([(_is_esearch, _ok(b'{"unexpected": true}'))])
    with patch("urllib.request.urlopen", transport):
        with pytest.raises(ChineseLiteratureUnavailable):
            _client().journal_is_indexed("Hecheng Ceshi Yi Xue Za Zhi")


def test_resolve_propagates_unavailable_rather_than_returning_a_verdict():
    """fail-closed: `resolve` has no `unreachable` return value by design. An
    outage must reach the caller as an exception so it can never be silently
    rendered as a lookup result."""
    from chinese_literature_client import ChineseLiteratureUnavailable

    transport = FakeTransport([(_is_ra, _http_error(503))])
    with patch("urllib.request.urlopen", transport):
        with pytest.raises(ChineseLiteratureUnavailable):
            _client().resolve(_istic_entry())


# ------------------------------------------------------------------ throttling


def test_throttle_uses_monotonic_clock(monkeypatch):
    """time.monotonic for elapsed measurement (NTP-safe), never time.time
    (#128 §6). Aligns with arxiv/crossref/openalex/S2."""
    monotonic_calls: list[int] = []
    time_calls: list[int] = []
    monkeypatch.setattr("chinese_literature_client.time.monotonic",
                        lambda: (monotonic_calls.append(1), 100.0)[1])
    monkeypatch.setattr("chinese_literature_client.time.time",
                        lambda: (time_calls.append(1), 100.0)[1])

    client = _client()
    client._throttle("_last_doi_at", 0.2)  # no prior request -> short-circuit
    client._last_doi_at = 99.9
    client._throttle("_last_doi_at", 0.2)

    assert monotonic_calls, "throttle must read time.monotonic"
    assert time_calls == [], "throttle must NOT read time.time (NTP-unsafe)"


def test_doi_and_ncbi_have_independent_throttle_anchors(monkeypatch):
    """Sharing one anchor would either over-throttle doi.org or under-throttle
    NCBI, whose published expectations differ."""
    sleeps: list[float] = []
    monkeypatch.setattr("chinese_literature_client.time.sleep", sleeps.append)
    clock = [1000.0]
    monkeypatch.setattr("chinese_literature_client.time.monotonic", lambda: clock[0])

    esearch_bodies = [_body("esearch_coverage_hit.json"),
                      _body("esearch_coverage_hit.json")]
    transport = FakeTransport([
        (_is_ra, _ok(_body("ra_istic.json"))),
        (_is_esearch, lambda url: _ok(esearch_bodies.pop(0))(url)),
    ])
    with patch("urllib.request.urlopen", transport):
        client = _client()
        client.ra_for(ISTIC_DOI)
        # A DOI request must not make the (independent) NCBI anchor wait.
        client.journal_is_indexed("Hecheng Ceshi Yi Xue Za Zhi")
        assert sleeps == []
        # A second NCBI request on a frozen clock does pace at the NCBI floor.
        client.journal_is_indexed("Hecheng Ceshi Yi Xue Za Zhi")
        assert sleeps == [pytest.approx(0.34)]


# ------------------------------------------------------------ checklist shape


def test_every_non_matched_outcome_emits_exactly_one_checklist_row():
    """The checklist is a first-class deliverable, not a log side effect: it is
    what turns 'nobody ever actually checked this reference' from an invisible
    default into an item somebody has to sign off on."""
    from chinese_literature_client import REASON_CODES

    scenarios = [
        ([(_is_ra, _ok(_body("ra_istic.json"))),
          (_is_doi_resolve, _http_error(404)),
          (_is_handle, _ok(_body("handle_absent.json")))], _istic_entry(), {}),
        ([(_is_ra, _ok(_body("ra_cnki.json"))),
          (_is_handle, _ok(_body("handle_exists.json")))],
         _istic_entry(doi=CNKI_DOI), {}),
        ([(_is_esearch, _ok(_body("esearch_coverage_zero.json")))],
         _coordinate_entry(), {"journal_map": TEST_JOURNAL_MAP}),
    ]
    for routes, entry, kwargs in scenarios:
        transport = FakeTransport(routes)
        with patch("urllib.request.urlopen", transport):
            result = _client(**kwargs).resolve(entry)
        item = result["checklist_item"]
        assert item is not None
        assert item["reason_code"] in REASON_CODES
        assert item["priority"] in {"P0", "P1", "P2", "P3"}
        assert item["citation_key"] == entry["citation_key"]
        assert item["human_result"] is None  # the tool never fills the verdict
        assert item["attempts"], "a row must record which sources were tried"


def test_priority_is_workload_ordering_not_a_suspicion_score():
    """Fabrication vocabulary is permitted only at P0. Mislabeling a real paper
    by a real author costs far more than missing one bad citation."""
    from chinese_literature_client import _PRIORITY_BY_REASON

    assert _PRIORITY_BY_REASON["DOI_REFUTED"] == "P0"
    assert _PRIORITY_BY_REASON["DOI_TITLE_MISMATCH"] == "P0"
    assert _PRIORITY_BY_REASON["DOI_EXISTS_TITLE_UNVERIFIABLE"] == "P2"
    assert _PRIORITY_BY_REASON["NO_ISSN_MAPPING"] == "P3"
    non_p0 = {code for code, priority in _PRIORITY_BY_REASON.items()
              if priority != "P0"}
    assert "DOI_REFUTED" not in non_p0


def test_unknown_reason_code_is_rejected():
    """The reason-code set is closed; adding a member is a protocol-doc change."""
    from chinese_literature_client import _checklist_item

    with pytest.raises(ValueError):
        _checklist_item(
            reason_code="MADE_UP_CODE",
            verdict_contribution="unresolvable",
            entry={"citation_key": "x"},
            attempts=[],
            human_action="",
        )


def test_no_forbidden_upstream_host_appears_in_client_code():
    """Zero-scraping red line, pinned executably: CNKI / Wanfang / VIP / chndoi
    hosts must never become upstreams here. Guards against a well-intentioned
    later edit 'just adding a title lookup'.

    Scanned over the AST's non-docstring string constants rather than raw text:
    prose EXPLAINING why we refuse to scrape chndoi.org is exactly the comment
    a future editor most needs to read, so a raw-text scan would pressure
    someone to delete the warning in order to pass the test."""
    import ast

    source = (REPO_ROOT / "scripts" / "chinese_literature_client.py").read_text(
        encoding="utf-8")
    tree = ast.parse(source)
    docstrings = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                             ast.AsyncFunctionDef)):
            body = getattr(node, "body", None)
            if (body and isinstance(body[0], ast.Expr)
                    and isinstance(body[0].value, ast.Constant)
                    and isinstance(body[0].value.value, str)):
                docstrings.add(id(body[0].value))

    literals = [
        node.value for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
        and id(node) not in docstrings
    ]
    # Sanity: the scan must actually see the real endpoint constants, otherwise
    # it would pass vacuously.
    assert any("hdl.handle.net" in literal for literal in literals)
    for host in ("cnki.net", "wanfangdata", "cqvip.com", "chndoi.org"):
        for literal in literals:
            assert host not in literal, f"forbidden upstream host {host!r} in client"
