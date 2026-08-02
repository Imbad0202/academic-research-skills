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
import traceback
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

FIXTURES = REPO_ROOT / "scripts" / "fixtures" / "transport_bodies" / "chinese_literature"

# Synthetic identifiers pinned to the fixture bodies (see the fixtures README):
# These suffixes are synthetic fixture namespaces. The 10.5555 prefix itself
# can contain real Crossref records, so tests make no claim about live minting.
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

    kwargs.setdefault("ncbi_email", "ars-tests@example.invalid")
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
        resp.headers = {}
        resp.geturl.return_value = url
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
    return parsed.netloc == "doi.org" and parsed.path.startswith("/doiRA/")


def _is_doi_resolve(parsed, query):
    return parsed.netloc == "doi.org" and not parsed.path.startswith("/doiRA/")


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


def test_doi_keyed_exact_generic_title_can_match():
    """The generic-title veto is for identifier-free title searches. A real,
    DOI-keyed work may legitimately be titled Editorial."""
    from chinese_literature_client import _cn_titles_match

    assert _cn_titles_match("Editorial", "Editorial") is True


@pytest.mark.parametrize(
    "left,right",
    [
        ("ER+ 乳腺癌患者的预后分析", "ER- 乳腺癌患者的预后分析"),
        ("CD4+ T细胞计数与预后", "CD4− T细胞计数与预后"),
        ("生存率提高 4.5% 的临床意义", "生存率提高 45% 的临床意义"),
        ("剂量2²的研究", "剂量22的研究"),
        ("Straße治疗研究", "Strasse治疗研究"),
        ("治疗是否有效？", "治疗是否有效"),
        ("PD L1蛋白表达", "PDL 1蛋白表达"),
        ("P53蛋白表达", "p53蛋白表达"),
    ],
)
def test_normalizer_preserves_scientifically_meaningful_distinctions(left, right):
    from chinese_literature_client import normalize_cn_title

    assert normalize_cn_title(left) != normalize_cn_title(right)


@pytest.mark.parametrize(
    "variant",
    [
        CN_TITLE + ".",
        CN_TITLE + "．",
        "“" + CN_TITLE + "”",
        "‘" + CN_TITLE + "’",
    ],
)
def test_normalizer_folds_conventional_terminal_periods_and_outer_quotes(variant):
    from chinese_literature_client import normalize_cn_title

    assert normalize_cn_title(variant) == normalize_cn_title(CN_TITLE)


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
    with patch("chinese_literature_client._safe_urlopen", side_effect=AssertionError("no network")):
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
    with patch("chinese_literature_client._safe_urlopen", transport):
        assert _client().ra_for(ISTIC_DOI) == expected
    assert transport.requests == ["https://doi.org/doiRA/10.5555"]


def test_ra_lookup_returns_none_for_an_unknown_prefix():
    """The endpoint does not error on an unknown prefix: it answers 200 with a
    `status` field in place of `RA` (verified 2026-07-27: `/doiRA/10.99999` ->
    `[{"DOI": "10.99999", "status": "DOI does not exist"}]`). The missing RA
    key must yield None, never a degradation or a fabricated agency name."""
    transport = FakeTransport([(_is_ra, _ok(_body("ra_unknown_prefix.json")))])
    with patch("chinese_literature_client._safe_urlopen", transport):
        assert _client().ra_for("10.99999/ars.cn.unknown.2026.1") is None


@pytest.mark.parametrize(
    "body",
    [
        b"{}",
        b"[]",
        b"null",
        b'[{"DOI":"10.other","RA":"ISTIC"}]',
        b'[{"DOI":"10.5555","RA":false}]',
        b'[{"DOI":"10.5555"}]',
        b'[{"DOI":"10.5555","RA":"ISTIC"},{"DOI":"10.5555","RA":"CNKI"}]',
    ],
)
def test_ra_lookup_parseable_malformed_shape_is_typed_unavailable(body):
    from chinese_literature_client import ChineseLiteratureUnavailable

    transport = FakeTransport([(_is_ra, _ok(body))])
    with patch("chinese_literature_client._safe_urlopen", transport):
        with pytest.raises(ChineseLiteratureUnavailable):
            _client().ra_for(ISTIC_DOI)


def test_ra_lookup_short_circuits_a_non_doi_without_a_request():
    transport = FakeTransport([])
    with patch("chinese_literature_client._safe_urlopen", transport):
        assert _client().ra_for("not-a-doi") is None
    assert transport.requests == []


def test_crossref_registered_chinese_doi_is_not_claimed():
    """Division of labour: a Crossref-registered Chinese DOI belongs to the
    existing crossref resolver. It must stop without discarding the supplied
    DOI or attempting the DOI-less coordinate branch."""
    transport = FakeTransport([
        (_is_ra, _ok(_body("ra_crossref.json"))),
        (_is_doi_resolve, _http_error(500)),  # must never be reached
        (_is_handle, _http_error(500)),       # must never be reached
    ])
    with patch("chinese_literature_client._safe_urlopen", transport):
        result = _client(journal_map=TEST_JOURNAL_MAP).resolve({
            "citation_key": "chen2026",
            "title": CN_TITLE,
            "container_title": CN_JOURNAL,
            "doi": "10.5555/crossref.zh.2026.1",
        })
    assert result["reason_code"] == "DOI_RA_OUT_OF_SCOPE"
    assert result["status"] == "skipped"
    assert result["checklist_item"]["priority"] == "P3"
    assert len(transport.requests) == 1  # RA lookup only


def test_unknown_doi_ra_does_not_fall_through_to_coordinates():
    transport = FakeTransport([
        (_is_ra, _ok(_body("ra_unknown_prefix.json"))),
        (_is_esearch, _http_error(500)),  # must never be reached
    ])
    with patch("chinese_literature_client._safe_urlopen", transport):
        result = _client(journal_map=TEST_JOURNAL_MAP).resolve(
            _istic_entry(doi="10.99999/ars.cn.unknown.2026.1")
        )
    assert result["status"] == "skipped"
    assert result["reason_code"] == "DOI_RA_UNRESOLVED"
    assert result["checklist_item"]["priority"] == "P2"
    assert len(transport.requests) == 1


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
    with patch("chinese_literature_client._safe_urlopen", transport):
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
    with patch("chinese_literature_client._safe_urlopen", transport):
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
    with patch("chinese_literature_client._safe_urlopen", transport):
        result = _client().resolve(_istic_entry())

    assert result["status"] == "unmatched"
    assert result["queried_by"] == "id"
    assert result["reason_code"] == "DOI_TITLE_MISMATCH"
    item = result["checklist_item"]
    assert item["priority"] == "P0"
    assert item["verdict_contribution"] == "false"
    assert item["human_result"] is None


def test_istic_english_shadow_title_is_unverifiable_never_false():
    """An English translation cannot refute the cited Chinese original.

    PubMed and some DOI metadata surfaces expose English shadow titles for
    Chinese articles. Without a translation oracle, a cross-script difference
    is not a machine-verifiable chimeric citation.
    """
    transport = FakeTransport([
        (_is_ra, _ok(_body("ra_istic.json"))),
        (_is_doi_resolve, _ok(
            b'{"title":"Deterministic Evaluation of a Synthetic Citation Gate"}'
        )),
    ])
    with patch("chinese_literature_client._safe_urlopen", transport):
        result = _client().resolve(_istic_entry())

    assert result["status"] == "unmatched"
    assert result["queried_by"] == "title"
    assert result["reason_code"] == "DOI_EXISTS_TITLE_UNVERIFIABLE"
    assert result["evidence"]["resolved_title"].startswith("Deterministic")
    assert result["checklist_item"]["verdict_contribution"] == "unresolvable"
    assert len(transport.requests) == 2


def test_two_different_latin_titles_are_unverifiable_not_mismatch():
    """Matching script alone cannot make romanized titles comparable."""
    from chinese_literature_client import DoiTitleState

    transport = FakeTransport([
        (_is_doi_resolve, _ok(b'{"title":"Romanized title alpha"}')),
    ])
    with patch("chinese_literature_client._safe_urlopen", transport):
        outcome = _client().doi_lookup_with_title_check(
            ISTIC_DOI, "Romanized title beta",
        )

    assert outcome.state is DoiTitleState.UNVERIFIABLE
    assert outcome.record["title"] == "Romanized title alpha"


def test_lone_surrogate_doi_is_typed_unavailable_after_ra_lookup():
    """A schema-valid JSON string still may not be UTF-8 encodable."""
    from chinese_literature_client import ChineseLiteratureUnavailable

    entry = _istic_entry(doi="10.5555/" + chr(0xD800))
    transport = FakeTransport([
        (_is_ra, _ok(_body("ra_istic.json"))),
    ])
    with patch("chinese_literature_client._safe_urlopen", transport):
        with pytest.raises(ChineseLiteratureUnavailable, match="invalid Unicode"):
            _client().resolve(entry)

    assert len(transport.requests) == 1


def test_fabricated_doi_is_refuted_by_404_plus_handle_100():
    """The fabrication canary: these prefixes carry no wildcard catch-all, so a
    404 + responseCode 100 is positive evidence the identifier does not exist."""
    transport = FakeTransport([
        (_is_ra, _ok(_body("ra_istic.json"))),
        (_is_doi_resolve, _http_error(404)),
        (_is_handle, _ok(_body("handle_absent.json"))),
    ])
    with patch("chinese_literature_client._safe_urlopen", transport):
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
    from chinese_literature_client import (
        ChineseLiteratureUnavailable,
        DoiTitleState,
    )

    transport = FakeTransport([(_is_doi_resolve, _http_error(404))])
    with patch("chinese_literature_client._safe_urlopen", transport):
        client = _client()
        try:
            outcome = client.doi_lookup_with_title_check(FABRICATED_DOI, CN_TITLE)
            assert outcome.state is DoiTitleState.NOT_FOUND
            assert outcome.record is None
        except ChineseLiteratureUnavailable:  # pragma: no cover - failure path
            pytest.fail("a DOI 404 must be a negative, not a degradation")


def test_doi_keyed_editorial_title_verifies_end_to_end():
    from chinese_literature_client import DoiTitleState

    transport = FakeTransport([
        (_is_doi_resolve, _ok(b'{"title": "Editorial"}')),
    ])
    with patch("chinese_literature_client._safe_urlopen", transport):
        outcome = _client().doi_lookup_with_title_check(ISTIC_DOI, "Editorial")
    assert outcome.state is DoiTitleState.MATCH
    assert outcome.record["title"] == "Editorial"


def test_doi_404_plus_existing_handle_is_title_unverifiable_never_false():
    transport = FakeTransport([
        (_is_ra, _ok(_body("ra_istic.json"))),
        (_is_doi_resolve, _http_error(404)),
        (_is_handle, _ok(_body("handle_exists.json"))),
    ])
    with patch("chinese_literature_client._safe_urlopen", transport):
        result = _client().resolve(_istic_entry())

    assert result["status"] == "unmatched"
    assert result["queried_by"] == "title"
    assert result["reason_code"] == "DOI_EXISTS_TITLE_UNVERIFIABLE"
    assert result["checklist_item"]["verdict_contribution"] == "unresolvable"


def test_empty_expected_title_is_unverifiable_never_mismatch_or_false():
    from chinese_literature_client import DoiTitleState

    direct = FakeTransport([
        (_is_doi_resolve, _ok(_body("istic_csl_hit.json"))),
    ])
    with patch("chinese_literature_client._safe_urlopen", direct):
        outcome = _client().doi_lookup_with_title_check(ISTIC_DOI, "")
    assert outcome.state is DoiTitleState.UNVERIFIABLE
    assert outcome.record["title"] == CN_TITLE

    transport = FakeTransport([
        (_is_ra, _ok(_body("ra_istic.json"))),
        (_is_doi_resolve, _ok(_body("istic_csl_hit.json"))),
    ])
    with patch("chinese_literature_client._safe_urlopen", transport):
        result = _client().resolve(_istic_entry(title=""))
    assert result["reason_code"] == "DOI_EXISTS_TITLE_UNVERIFIABLE"
    assert result["queried_by"] == "title"
    assert result["checklist_item"]["verdict_contribution"] == "unresolvable"


def test_normalized_empty_resolved_title_is_unverifiable_not_mismatch():
    from chinese_literature_client import DoiTitleState

    transport = FakeTransport([
        (_is_doi_resolve, _ok('{"title": "。"}'.encode())),
    ])
    with patch("chinese_literature_client._safe_urlopen", transport):
        outcome = _client().doi_lookup_with_title_check(ISTIC_DOI, CN_TITLE)
    assert outcome.state is DoiTitleState.UNVERIFIABLE


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
    with patch("chinese_literature_client._safe_urlopen", transport):
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
    with patch("chinese_literature_client._safe_urlopen", transport):
        result = _client().resolve(_istic_entry(doi=CNKI_DOI))

    assert result["queried_by"] == "id"
    assert result["reason_code"] == "DOI_REFUTED"


def test_non_csl_200_body_is_typed_unavailable():
    """A 200 non-JSON body can be a proxy/CDN error page. It must fail closed,
    not become routine human-check evidence."""
    from chinese_literature_client import ChineseLiteratureUnavailable

    transport = FakeTransport([
        (_is_ra, _ok(_body("ra_istic.json"))),
        (_is_doi_resolve, _ok(_body("cnki_landing_page.html"))),
    ])
    with patch("chinese_literature_client._safe_urlopen", transport):
        with pytest.raises(ChineseLiteratureUnavailable):
            _client().resolve(_istic_entry())


def test_parseable_csl_with_malformed_author_shape_is_typed_unavailable():
    from chinese_literature_client import ChineseLiteratureUnavailable

    malformed = ('{"title": "' + CN_TITLE + '", "author": 42}').encode()
    transport = FakeTransport([(_is_doi_resolve, _ok(malformed))])
    with patch("chinese_literature_client._safe_urlopen", transport):
        with pytest.raises(ChineseLiteratureUnavailable):
            _client().doi_lookup_with_title_check(ISTIC_DOI, CN_TITLE)


def test_parseable_csl_with_malformed_root_is_typed_unavailable():
    from chinese_literature_client import ChineseLiteratureUnavailable

    transport = FakeTransport([(_is_doi_resolve, _ok(b'[{"title": "x"}]'))])
    with patch("chinese_literature_client._safe_urlopen", transport):
        with pytest.raises(ChineseLiteratureUnavailable):
            _client().doi_lookup_with_title_check(ISTIC_DOI, CN_TITLE)


@pytest.mark.parametrize("endpoint", ["ra", "csl"])
def test_deeply_nested_json_is_typed_unavailable(endpoint):
    """A small but adversarial upstream body must not leak RecursionError."""
    from chinese_literature_client import ChineseLiteratureUnavailable

    body = b"[" * 2000 + b"]" * 2000
    predicate = _is_ra if endpoint == "ra" else _is_doi_resolve
    transport = FakeTransport([(predicate, _ok(body))])
    with patch("chinese_literature_client._safe_urlopen", transport):
        with pytest.raises(ChineseLiteratureUnavailable):
            if endpoint == "ra":
                _client().ra_for(ISTIC_DOI)
            else:
                _client().doi_lookup_with_title_check(ISTIC_DOI, CN_TITLE)


@pytest.mark.parametrize(
    "body",
    [
        b'{"title": {"value": "x"}}',
        b'{"title": [42]}',
        b'{"title": []}',
        b'{"title": "x", "author": [42]}',
        b'{"title": "x", "author": false}',
        b'{"title": "x", "author": [{"given": 42}]}',
        b'{"title": "x", "issued": []}',
        b'{"title": "x", "issued": {"date-parts": {}}}',
        b'{"title": "x", "issued": {"date-parts": [[true]]}}',
        b'{"title": "x", "issued": {"date-parts": [[-1]]}}',
        '{"title": "x", "issued": {"date-parts": [["٢٠٢٦"]]}}'.encode(),
        b'{"title": "x", "issued": {"date-parts": [["99999"]]}}',
        b'{"title": "x", "volume": {"value": "1"}}',
        b'{"title": "x", "DOI": ["10.5555/x"]}',
        (b'{"title": "' + CN_TITLE.encode() + b'", "DOI": ""}'),
        (b'{"title": "' + CN_TITLE.encode()
         + b'", "DOI": "10.5555/a.different.record"}'),
    ],
)
def test_parseable_csl_with_malformed_fields_is_typed_unavailable(body):
    from chinese_literature_client import ChineseLiteratureUnavailable

    transport = FakeTransport([(_is_doi_resolve, _ok(body))])
    with patch("chinese_literature_client._safe_urlopen", transport):
        with pytest.raises(ChineseLiteratureUnavailable):
            _client().doi_lookup_with_title_check(ISTIC_DOI, CN_TITLE)


def test_handle_unknown_response_code_degrades():
    """responseCode 2 (internal error) is an unknown state — degrade, do not
    guess an existence answer."""
    from chinese_literature_client import ChineseLiteratureUnavailable

    transport = FakeTransport([(_is_handle, _ok(_body("handle_internal_error.json")))])
    with patch("chinese_literature_client._safe_urlopen", transport):
        with pytest.raises(ChineseLiteratureUnavailable):
            _client().handle_exists(ISTIC_DOI)


@pytest.mark.parametrize(
    "body",
    [b'{"responseCode": true}', b'{"responseCode": 100.0}'],
)
def test_handle_bool_or_float_response_code_degrades(body):
    from chinese_literature_client import ChineseLiteratureUnavailable

    transport = FakeTransport([(_is_handle, _ok(body))])
    with patch("chinese_literature_client._safe_urlopen", transport):
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


def test_missing_coordinate_tuple_is_p3_without_a_pubmed_request():
    with patch(
        "chinese_literature_client._safe_urlopen",
        side_effect=AssertionError("no PubMed request"),
    ):
        result = _coordinate_client().resolve(
            _coordinate_entry(volume=None, pages=None, year=None)
        )

    assert result["status"] == "skipped"
    assert result["queried_by"] is None
    assert result["reason_code"] == "INSUFFICIENT_PUBMED_COORDINATES"
    assert result["checklist_item"]["priority"] == "P3"
    assert result["checklist_item"]["verdict_contribution"] == "unresolvable"


def test_lone_surrogate_eutils_parameter_is_typed_before_transport():
    from chinese_literature_client import ChineseLiteratureUnavailable

    with patch(
        "chinese_literature_client._safe_urlopen",
        side_effect=AssertionError("no request for unencodable EUtils term"),
    ):
        with pytest.raises(ChineseLiteratureUnavailable, match="invalid Unicode"):
            _coordinate_client().journal_is_indexed("Journal " + chr(0xD800))


def test_volume_page_zero_hit_never_falls_back_to_author_year():
    """A valid author/year candidate must not wash a cited wrong page into a
    match after the stronger volume/page query returned zero."""
    esearch_bodies = [
        _body("esearch_coverage_hit.json"),
        _body("esearch_coordinate_zero.json"),
    ]
    transport = FakeTransport([
        (_is_esearch, lambda url: _ok(esearch_bodies.pop(0))(url)),
    ])
    with patch("chinese_literature_client._safe_urlopen", transport):
        result = _coordinate_client().resolve(
            _coordinate_entry(pages="9999", first_author_pinyin="Hecheng Ceshi")
        )

    assert result["reason_code"] == "PUBMED_INDEXED_BUT_COORDINATE_MISS"
    assert len(transport.requests) == 2  # coverage + volume/page, no fallback
    assert result["checklist_item"]["attempts"][-1]["detail"] == "volume_page"


def test_pubmed_candidate_page_conflict_cannot_be_promoted():
    esearch_bodies = [
        _body("esearch_coverage_hit.json"),
        _body("esearch_coordinate_hit.json"),
    ]
    transport = FakeTransport([
        (_is_esearch, lambda url: _ok(esearch_bodies.pop(0))(url)),
        (_is_esummary, _ok(_body("esummary_hit.json"))),
    ])
    with patch("chinese_literature_client._safe_urlopen", transport):
        result = _coordinate_client().resolve(_coordinate_entry(pages="9999"))

    assert result["reason_code"] == "PUBMED_COORDINATE_CANDIDATE_UNVERIFIED"
    assert result["status"] == "unmatched"
    assert "first page" in result["checklist_item"]["human_action"]
    assert len(transport.requests) == 3  # no DOI/RA lookup after conflict


def test_pubmed_candidate_volume_conflict_cannot_be_promoted():
    """A unique hit with a different volume stops before DOI/title binding."""
    esearch_bodies = [
        _body("esearch_coverage_hit.json"),
        _body("esearch_coordinate_hit.json"),
    ]
    transport = FakeTransport([
        (_is_esearch, lambda url: _ok(esearch_bodies.pop(0))(url)),
        (_is_esummary, _ok(_body("esummary_hit.json"))),
    ])
    with patch("chinese_literature_client._safe_urlopen", transport):
        result = _coordinate_client().resolve(_coordinate_entry(volume="99"))

    assert result["reason_code"] == "PUBMED_COORDINATE_CANDIDATE_UNVERIFIED"
    assert result["status"] == "unmatched"
    assert "volume" in result["checklist_item"]["human_action"]
    assert len(transport.requests) == 3  # no DOI/RA lookup after conflict


def test_pubmed_coordinate_candidate_is_matched_only_after_istic_title_binding():
    """Coordinates nominate a candidate; its ISTIC DOI and Chinese CSL title
    provide the evidence that upgrades it to a title-keyed match."""
    esearch_bodies = [_body("esearch_coverage_hit.json"),
                      _body("esearch_coordinate_hit.json")]
    transport = FakeTransport([
        (_is_esearch, lambda url: _ok(esearch_bodies.pop(0))(url)),
        (_is_esummary, _ok(_body("esummary_hit.json"))),
        (_is_ra, _ok(_body("ra_istic.json"))),
        (_is_doi_resolve, _ok(_body("istic_csl_hit.json"))),
    ])
    with patch("chinese_literature_client._safe_urlopen", transport):
        result = _coordinate_client().resolve(_coordinate_entry())

    assert result["status"] == "matched"
    assert result["queried_by"] == "title"
    assert result["reason_code"] == "PUBMED_COORDINATE_VERIFIED"
    assert result["evidence"]["pmid"] == "999999901"
    assert result["evidence"]["doi"] == ISTIC_DOI
    assert result["evidence"]["doi_metadata"]["title"] == CN_TITLE
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
    with patch("chinese_literature_client._safe_urlopen", transport):
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
    with patch("chinese_literature_client._safe_urlopen", transport):
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
    with patch("chinese_literature_client._safe_urlopen", transport):
        result = _coordinate_client().resolve(_coordinate_entry())

    assert result["status"] == "unmatched"
    assert result["queried_by"] == "title"
    assert result["reason_code"] == "PUBMED_COORDINATE_CANDIDATE_UNVERIFIED"


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
    with patch("chinese_literature_client._safe_urlopen", transport):
        result = _coordinate_client().resolve(_coordinate_entry())

    assert result["status"] == "unmatched"
    assert result["queried_by"] == "title"
    assert result["reason_code"] == "PUBMED_COORDINATE_CANDIDATE_UNVERIFIED"
    assert "ISSN" in result["checklist_item"]["human_action"]


def test_absent_year_does_not_block_doi_title_binding():
    """Absence is not mismatch: exact Chinese title binding still verifies."""
    esearch_bodies = [_body("esearch_coverage_hit.json"),
                      _body("esearch_coordinate_hit.json")]
    transport = FakeTransport([
        (_is_esearch, lambda url: _ok(esearch_bodies.pop(0))(url)),
        (_is_esummary, _ok(_body("esummary_hit.json"))),
        (_is_ra, _ok(_body("ra_istic.json"))),
        (_is_doi_resolve, _ok(_body("istic_csl_hit.json"))),
    ])
    with patch("chinese_literature_client._safe_urlopen", transport):
        result = _coordinate_client().resolve(_coordinate_entry(year=None))

    assert result["status"] == "matched"


def test_pubmed_coordinate_candidate_without_doi_is_never_matched():
    esearch_bodies = [_body("esearch_coverage_hit.json"),
                      _body("esearch_coordinate_hit.json")]
    transport = FakeTransport([
        (_is_esearch, lambda url: _ok(esearch_bodies.pop(0))(url)),
        (_is_esummary, _ok(_body("esummary_no_doi.json"))),
    ])
    with patch("chinese_literature_client._safe_urlopen", transport):
        result = _coordinate_client().resolve(_coordinate_entry())

    assert result["status"] == "unmatched"
    assert result["queried_by"] == "title"
    assert result["reason_code"] == "PUBMED_COORDINATE_CANDIDATE_UNVERIFIED"
    assert result["checklist_item"]["verdict_contribution"] == "unresolvable"


def test_pubmed_candidate_doi_title_mismatch_never_washes_fake_chinese_title():
    esearch_bodies = [_body("esearch_coverage_hit.json"),
                      _body("esearch_coordinate_hit.json")]
    transport = FakeTransport([
        (_is_esearch, lambda url: _ok(esearch_bodies.pop(0))(url)),
        (_is_esummary, _ok(_body("esummary_hit.json"))),
        (_is_ra, _ok(_body("ra_istic.json"))),
        (_is_doi_resolve, _ok(_body("istic_csl_other_title.json"))),
    ])
    with patch("chinese_literature_client._safe_urlopen", transport):
        result = _coordinate_client().resolve(_coordinate_entry())

    assert result["status"] == "unmatched"
    assert result["queried_by"] == "title"
    assert result["reason_code"] == "PUBMED_COORDINATE_CANDIDATE_UNVERIFIED"
    assert result["checklist_item"]["verdict_contribution"] == "unresolvable"


@pytest.mark.parametrize(
    "esummary_fixture,ra_fixture",
    [
        ("esummary_hit.json", "ra_crossref.json"),
        ("esummary_unknown_ra.json", "ra_unknown_prefix.json"),
    ],
)
def test_pubmed_candidate_out_of_scope_or_unknown_ra_is_never_matched(
    esummary_fixture, ra_fixture,
):
    esearch_bodies = [_body("esearch_coverage_hit.json"),
                      _body("esearch_coordinate_hit.json")]
    transport = FakeTransport([
        (_is_esearch, lambda url: _ok(esearch_bodies.pop(0))(url)),
        (_is_esummary, _ok(_body(esummary_fixture))),
        (_is_ra, _ok(_body(ra_fixture))),
    ])
    with patch("chinese_literature_client._safe_urlopen", transport):
        result = _coordinate_client().resolve(_coordinate_entry())

    assert result["status"] == "unmatched"
    assert result["queried_by"] == "title"
    assert result["reason_code"] == "PUBMED_COORDINATE_CANDIDATE_UNVERIFIED"


def test_pubmed_candidate_cnki_handle_existence_is_never_matched():
    esearch_bodies = [_body("esearch_coverage_hit.json"),
                      _body("esearch_coordinate_hit.json")]
    transport = FakeTransport([
        (_is_esearch, lambda url: _ok(esearch_bodies.pop(0))(url)),
        (_is_esummary, _ok(_body("esummary_hit.json"))),
        (_is_ra, _ok(_body("ra_cnki.json"))),
        (_is_handle, _ok(_body("handle_exists.json"))),
    ])
    with patch("chinese_literature_client._safe_urlopen", transport):
        result = _coordinate_client().resolve(_coordinate_entry())

    assert result["status"] == "unmatched"
    assert result["reason_code"] == "PUBMED_COORDINATE_CANDIDATE_UNVERIFIED"
    assert any(
        attempt["stage"] == "pubmed_candidate_handle"
        and attempt["outcome"] == "exists"
        for attempt in result["checklist_item"]["attempts"]
    )


def test_journal_catalogued_but_not_indexed_is_skipped_not_unmatched():
    """'In the NLM Catalog' != 'indexed in PubMed' (中国全科医学 is catalogued
    with zero PubMed articles). A journal PubMed never indexed must produce
    `skipped` + a P3 row, because a coordinate miss against it says nothing."""
    transport = FakeTransport([
        (_is_esearch, _ok(_body("esearch_coverage_zero.json"))),
    ])
    with patch("chinese_literature_client._safe_urlopen", transport):
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
    with patch("chinese_literature_client._safe_urlopen", transport):
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
    with patch("chinese_literature_client._safe_urlopen", transport):
        client = _client(ncbi_api_key="test-ncbi-key")
        client.journal_is_indexed("Hecheng Ceshi Yi Xue Za Zhi")

    assert "api_key=test-ncbi-key" in transport.requests[0]
    assert "tool=academic-research-skills" in transport.requests[0]
    assert "email=ars-tests%40example.invalid" in transport.requests[0]
    assert _EUTILS_MIN_INTERVAL == 0.34  # the keyless NCBI floor, unconditionally


def test_ncbi_email_is_required_before_any_eutils_request():
    from chinese_literature_client import (
        ChineseLiteratureClient,
        ChineseLiteratureUnavailable,
    )

    with patch("chinese_literature_client._safe_urlopen", side_effect=AssertionError("no request")):
        with pytest.raises(ChineseLiteratureUnavailable, match="ncbi_email"):
            ChineseLiteratureClient().journal_is_indexed("Hecheng Ceshi Yi Xue Za Zhi")


def test_pubmed_author_fallback_uses_first_author_tag():
    bodies = [_body("esearch_coordinate_zero.json")]
    transport = FakeTransport([
        (_is_esearch, lambda url: _ok(bodies.pop(0))(url)),
    ])
    with patch("chinese_literature_client._safe_urlopen", transport):
        _client().pubmed_coordinate_lookup(
            nlm_ta="Hecheng Ceshi Yi Xue Za Zhi",
            first_author="Hecheng Ceshi",
            year=2026,
        )
    term = urllib.parse.parse_qs(
        urllib.parse.urlsplit(transport.requests[0]).query
    )["term"][0]
    assert '"Hecheng Ceshi"[1au]' in term
    assert "[au]" not in term


@pytest.mark.parametrize(
    "kwargs",
    [
        {"volume": "88[vi] OR 1", "pages": "8801"},
        {"volume": "88", "pages": "8801[pg] OR 1"},
        {"volume": "1:9999", "pages": "8801"},
        {"first_author": 'Chen" OR cancer[ti]', "year": 2026},
    ],
)
def test_untrusted_pubmed_fields_cannot_inject_entrez_grammar(kwargs):
    from chinese_literature_client import ChineseLiteratureUnavailable

    with patch("chinese_literature_client._safe_urlopen", side_effect=AssertionError("no request")):
        with pytest.raises(ChineseLiteratureUnavailable):
            _client().pubmed_coordinate_lookup(
                nlm_ta="Hecheng Ceshi Yi Xue Za Zhi", **kwargs
            )


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
    with patch("chinese_literature_client._safe_urlopen", transport):
        assert _client().handle_exists(evil) is False

    url = transport.requests[0]
    assert "\r" not in url and "\n" not in url
    assert "?" not in url and "#" not in url  # no query/fragment injection
    assert "%0D%0A" in url  # CRLF arrived encoded, not stripped

    # Defense in depth: even if a malformed request slips past encoding and
    # urlopen rejects it (http.client.InvalidURL), the client degrades cleanly.
    def reject(req, timeout=None):
        raise http.client.InvalidURL("URL can't contain control characters")

    with patch("chinese_literature_client._safe_urlopen", reject):
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
        with patch("chinese_literature_client._safe_urlopen", transport):
            with pytest.raises(ChineseLiteratureUnavailable) as excinfo:
                _client(ncbi_api_key=key).journal_is_indexed("Hecheng Ceshi")
        assert key not in str(excinfo.value)
        assert "api_key" not in str(excinfo.value)
        assert "?" not in str(excinfo.value)  # whole query stripped, not just the key

    def net_error(req, timeout=None):
        raise urllib.error.URLError("connection refused")

    with patch("chinese_literature_client._safe_urlopen", net_error):
        with pytest.raises(ChineseLiteratureUnavailable) as excinfo:
            _client(ncbi_api_key=key).journal_is_indexed("Hecheng Ceshi")
    assert key not in str(excinfo.value)
    assert "?" not in str(excinfo.value)


@pytest.mark.parametrize("failure_kind", ["http", "url"])
def test_reflected_request_url_is_absent_from_full_exception_traceback(failure_kind):
    """Removing a secret from the wrapper message is insufficient when the
    original exception remains as an explicit cause: logging the traceback
    would print that cause and its full query string."""
    from chinese_literature_client import ChineseLiteratureUnavailable

    key = "SECRET123"

    def reflected(req, timeout=None):
        if failure_kind == "http":
            raise urllib.error.HTTPError(
                url=req.full_url,
                code=503,
                msg=f"upstream reflected {req.full_url}",
                hdrs={},
                fp=io.BytesIO(),
            )
        raise urllib.error.URLError(f"upstream reflected {req.full_url}")

    with patch("chinese_literature_client._safe_urlopen", reflected):
        with pytest.raises(ChineseLiteratureUnavailable) as excinfo:
            _client(ncbi_api_key=key).journal_is_indexed("Hecheng Ceshi")

    rendered = "".join(traceback.format_exception(
        excinfo.type, excinfo.value, excinfo.tb,
    ))
    assert key not in rendered
    assert f"api_key={key}" not in rendered


@pytest.mark.parametrize("error_url", ["", "http://evil.invalid/stolen"])
def test_rejected_http_error_url_does_not_retain_reflected_secret(error_url):
    from chinese_literature_client import ChineseLiteratureUnavailable

    key = "SECRET123"

    def reflected(req, timeout=None):
        raise urllib.error.HTTPError(
            url=error_url,
            code=503,
            msg=f"upstream reflected {req.full_url}",
            hdrs={},
            fp=io.BytesIO(),
        )

    with patch("chinese_literature_client._safe_urlopen", reflected):
        with pytest.raises(ChineseLiteratureUnavailable) as excinfo:
            _client(ncbi_api_key=key).journal_is_indexed("Hecheng Ceshi")

    rendered = "".join(traceback.format_exception(
        excinfo.type, excinfo.value, excinfo.tb,
    ))
    assert key not in rendered


def test_malformed_port_does_not_retain_secret_as_a_cause():
    from chinese_literature_client import ChineseLiteratureUnavailable, _require_api_url

    key = "SECRET123"
    with pytest.raises(ChineseLiteratureUnavailable) as excinfo:
        _require_api_url(f"https://doi.org:{key}/path?api_key={key}")

    rendered = "".join(traceback.format_exception(
        excinfo.type, excinfo.value, excinfo.tb,
    ))
    assert key not in rendered


def test_host_allowlist_guard_refuses_and_redacts():
    """Multi-host `_require_api_url` (sibling defense-in-depth): a non-HTTPS or
    non-allowlisted host is refused before any request, and the refusal text is
    query-stripped."""
    from chinese_literature_client import (
        ChineseLiteratureUnavailable,
        _require_api_url,
    )

    _require_api_url("https://doi.org/doiRA/10.5555")         # allowlisted: no raise
    _require_api_url("https://eutils.ncbi.nlm.nih.gov/x")     # allowlisted: no raise
    for bad in (
        "https://www.cnki.net/search?q=x",       # zero-scraping red line
        "http://doi.org/doiRA/10.5555",          # https only
        "https://evil.invalid/a?api_key=test-ncbi-key",
        "https://127.0.0.1/doiRA/10.5555",       # no bare IPs
        "https://user@doi.org/doiRA/10.5555",    # no userinfo
        "https://doi.org:443/doiRA/10.5555",     # exact origin, no ports
    ):
        with pytest.raises(ChineseLiteratureUnavailable) as excinfo:
            _require_api_url(bad)
        assert "api_key" not in str(excinfo.value)
        assert "?" not in str(excinfo.value)


def test_redirect_handler_revalidates_every_destination_before_following():
    from chinese_literature_client import (
        ChineseLiteratureUnavailable,
        _SafeRedirectHandler,
    )

    handler = _SafeRedirectHandler()
    request = urllib.request.Request("https://doi.org/10.5555/example")
    for target in (
        "http://doi.org/10.5555/example",          # downgrade
        "https://127.0.0.1/10.5555/example",       # bare IP
        "https://user@doi.org/10.5555/example",    # userinfo
        "https://doi.org:443/10.5555/example",     # explicit port
        "https://doi.org.evil.invalid/example",    # suffix confusion
        "https://evil.invalid/example",            # external host
    ):
        with pytest.raises(ChineseLiteratureUnavailable):
            handler.redirect_request(request, None, 302, "Found", {}, target)

    redirected = handler.redirect_request(
        request, None, 302, "Found", {},
        "https://hdl.handle.net/api/handles/10.5555/example",
    )
    assert redirected.full_url.startswith("https://hdl.handle.net/")


@pytest.mark.parametrize("code", [301, 302, 303, 307, 308])
def test_redirect_response_body_is_never_read_before_following(code):
    from chinese_literature_client import _SafeRedirectHandler

    handler = _SafeRedirectHandler()
    handler.parent = MagicMock()
    request = urllib.request.Request("https://doi.org/10.5555/example")
    request.timeout = 30
    response = MagicMock()
    redirected_response = object()
    handler.parent.open.return_value = redirected_response

    result = getattr(handler, f"http_error_{code}")(
        request,
        response,
        code,
        "Found",
        {"location": "/10.5555/next"},
    )

    assert result is redirected_response
    response.read.assert_not_called()
    response.close.assert_called_once_with()
    followed = handler.parent.open.call_args.args[0]
    assert followed.full_url == "https://doi.org/10.5555/next"


@pytest.mark.parametrize(
    "location",
    ["http://doi.org/downgrade", "https://evil.invalid/escape", 42],
)
def test_rejected_redirect_is_closed_without_reading(location):
    from chinese_literature_client import (
        ChineseLiteratureUnavailable,
        _SafeRedirectHandler,
    )

    handler = _SafeRedirectHandler()
    request = urllib.request.Request("https://doi.org/10.5555/example")
    request.timeout = 30
    response = MagicMock()

    with pytest.raises(ChineseLiteratureUnavailable):
        handler.http_error_302(
            request, response, 302, "Found", {"location": location},
        )

    response.read.assert_not_called()
    response.close.assert_called_once_with()


def test_redirect_without_location_is_closed_without_reading():
    from chinese_literature_client import (
        ChineseLiteratureUnavailable,
        _SafeRedirectHandler,
    )

    handler = _SafeRedirectHandler()
    request = urllib.request.Request("https://doi.org/10.5555/example")
    request.timeout = 30
    response = MagicMock()

    with pytest.raises(ChineseLiteratureUnavailable, match="missing a Location"):
        handler.http_error_302(request, response, 302, "Found", {})

    response.read.assert_not_called()
    response.close.assert_called_once_with()


def test_istic_plaintext_redirect_stops_resolve_before_any_verdict():
    """End-to-end regression for the maintainer's live ISTIC observation.

    RA triage may identify ISTIC, but the subsequent DOI request currently has
    the shape ``HTTPS doi.org -> HTTP bare IP``. Exercise the real resolver and
    redirect handler together: the unsafe hop must be closed unread, propagate
    as typed degradation, and never return a MATCH/MISMATCH-shaped result.
    """
    from chinese_literature_client import (
        ChineseLiteratureUnavailable,
        _SafeRedirectHandler,
    )

    requests: list[str] = []
    redirect_response = MagicMock()

    def transport(req, timeout=None):
        url = req.full_url
        requests.append(url)
        parsed = urllib.parse.urlsplit(url)
        query = (
            urllib.parse.parse_qs(
                parsed.query, keep_blank_values=True, strict_parsing=True,
            )
            if parsed.query else {}
        )
        if _is_ra(parsed, query):
            return _ok(_body("ra_istic.json"))(url)
        if _is_doi_resolve(parsed, query):
            handler = _SafeRedirectHandler()
            return handler.http_error_302(
                req,
                redirect_response,
                302,
                "Found",
                {"location": "http://122.115.55.36:8000/doi/synthetic"},
            )
        raise AssertionError(f"client contacted an unrouted URL: {url}")

    with patch("chinese_literature_client._safe_urlopen", transport):
        with pytest.raises(ChineseLiteratureUnavailable):
            _client().resolve(_istic_entry())

    assert len(requests) == 2  # RA triage, then the refused DOI request
    redirect_response.read.assert_not_called()
    redirect_response.close.assert_called_once_with()


def test_final_response_url_is_revalidated_even_after_transport_returns():
    from chinese_literature_client import ChineseLiteratureUnavailable

    response = MagicMock()
    response.status = 200
    response.headers = {}
    response.geturl.return_value = "http://127.0.0.1/stolen"
    response.read.return_value = _body("ra_istic.json")
    response.__enter__ = MagicMock(return_value=response)
    response.__exit__ = MagicMock(return_value=None)

    with patch("chinese_literature_client._safe_urlopen", return_value=response):
        with pytest.raises(ChineseLiteratureUnavailable):
            _client().ra_for(ISTIC_DOI)
    response.read.assert_not_called()


def test_http_error_final_url_is_revalidated_before_404_becomes_data():
    from chinese_literature_client import ChineseLiteratureUnavailable

    def escaped_404(req, timeout=None):
        raise urllib.error.HTTPError(
            url="http://127.0.0.1/not-found",
            code=404,
            msg="synthetic",
            hdrs={},
            fp=io.BytesIO(b""),
        )

    with patch("chinese_literature_client._safe_urlopen", escaped_404):
        with pytest.raises(ChineseLiteratureUnavailable):
            _client().doi_lookup_with_title_check(FABRICATED_DOI, CN_TITLE)


@pytest.mark.parametrize("code", [404, 503])
def test_http_error_response_is_closed_without_reading(code):
    from chinese_literature_client import ChineseLiteratureUnavailable

    error_body = MagicMock()

    def fail(req, timeout=None):
        raise urllib.error.HTTPError(
            url=req.full_url,
            code=code,
            msg="synthetic",
            hdrs={},
            fp=error_body,
        )

    with patch("chinese_literature_client._safe_urlopen", fail):
        if code == 404:
            assert _client().handle_exists(FABRICATED_DOI) is False
        else:
            with pytest.raises(ChineseLiteratureUnavailable, match="HTTP 503"):
                _client().handle_exists(FABRICATED_DOI)

    error_body.read.assert_not_called()
    error_body.close.assert_called_once_with()


@pytest.mark.parametrize("status", [None, 0, 503, "200"])
def test_returned_invalid_or_non_success_status_is_rejected_before_read(status):
    from chinese_literature_client import ChineseLiteratureUnavailable

    response = MagicMock()
    response.status = status
    response.headers = {}
    response.geturl.return_value = "https://doi.org/doiRA/10.5555"
    response.__enter__ = MagicMock(return_value=response)
    response.__exit__ = MagicMock(return_value=None)

    with patch("chinese_literature_client._safe_urlopen", return_value=response):
        with pytest.raises(ChineseLiteratureUnavailable):
            _client().ra_for(ISTIC_DOI)
    response.read.assert_not_called()


def test_returned_404_is_data_only_on_an_allow_404_path():
    response = MagicMock()
    response.status = 404
    response.headers = {}
    response.geturl.return_value = "https://doi.org/doiRA/10.5555"
    response.__enter__ = MagicMock(return_value=response)
    response.__exit__ = MagicMock(return_value=None)

    with patch("chinese_literature_client._safe_urlopen", return_value=response):
        assert _client().ra_for(ISTIC_DOI) is None
    response.read.assert_not_called()


def test_content_length_precheck_rejects_oversized_body_without_reading():
    from chinese_literature_client import ChineseLiteratureUnavailable, MAX_BODY_BYTES

    response = MagicMock()
    response.status = 200
    response.headers = {"Content-Length": str(MAX_BODY_BYTES + 1)}
    response.geturl.return_value = "https://doi.org/doiRA/10.5555"
    response.__enter__ = MagicMock(return_value=response)
    response.__exit__ = MagicMock(return_value=None)

    with patch("chinese_literature_client._safe_urlopen", return_value=response):
        with pytest.raises(ChineseLiteratureUnavailable, match="exceeds"):
            _client().ra_for(ISTIC_DOI)
    response.read.assert_not_called()


@pytest.mark.parametrize(
    "value",
    ["+1", "-0", "1_0", "١", " 1 x ", "\u00a01\u00a0", "9" * 5000],
)
def test_malformed_content_length_is_rejected_before_read(value):
    from chinese_literature_client import ChineseLiteratureUnavailable

    response = MagicMock()
    response.status = 200
    response.headers = {"Content-Length": value}
    response.geturl.return_value = "https://doi.org/doiRA/10.5555"
    response.__enter__ = MagicMock(return_value=response)
    response.__exit__ = MagicMock(return_value=None)

    with patch("chinese_literature_client._safe_urlopen", return_value=response):
        with pytest.raises(ChineseLiteratureUnavailable, match="Content-Length"):
            _client().ra_for(ISTIC_DOI)
    response.read.assert_not_called()


def test_body_read_is_bounded_and_rejects_stream_over_limit():
    from chinese_literature_client import ChineseLiteratureUnavailable, MAX_BODY_BYTES

    response = MagicMock()
    response.status = 200
    response.headers = {}
    response.geturl.return_value = "https://doi.org/doiRA/10.5555"
    response.read.return_value = b"x" * (MAX_BODY_BYTES + 1)
    response.__enter__ = MagicMock(return_value=response)
    response.__exit__ = MagicMock(return_value=None)

    with patch("chinese_literature_client._safe_urlopen", return_value=response):
        with pytest.raises(ChineseLiteratureUnavailable, match="exceeds"):
            _client().ra_for(ISTIC_DOI)
    response.read.assert_called_once_with(MAX_BODY_BYTES + 1)


# ------------------------------------------------------- degradation contract


def test_5xx_does_not_retry():
    """Per protocol: 5xx -> fail fast, exactly one request."""
    from chinese_literature_client import ChineseLiteratureUnavailable

    transport = FakeTransport([(_is_ra, _http_error(503, _body("error_5xx.html")))])
    with patch("chinese_literature_client._safe_urlopen", transport):
        with pytest.raises(ChineseLiteratureUnavailable):
            _client().ra_for(ISTIC_DOI)

    assert len(transport.requests) == 1


def test_429_backs_off_then_raises_after_the_shared_retry_budget(monkeypatch):
    from chinese_literature_client import ChineseLiteratureUnavailable
    from _text_similarity import _MAX_RETRIES

    sleeps: list[float] = []
    monkeypatch.setattr("chinese_literature_client.time.sleep", sleeps.append)

    transport = FakeTransport([(_is_ra, _http_error(429))])
    with patch("chinese_literature_client._safe_urlopen", transport):
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

    with patch("chinese_literature_client._safe_urlopen", boom):
        with pytest.raises(ChineseLiteratureUnavailable):
            _client().ra_for(ISTIC_DOI)


@pytest.mark.parametrize("failure_point", ["open", "close"])
def test_raw_oserror_from_transport_or_response_close_is_typed(failure_point):
    from chinese_literature_client import ChineseLiteratureUnavailable

    if failure_point == "open":
        transport = MagicMock(side_effect=OSError("socket failure"))
    else:
        response = MagicMock()
        response.status = 200
        response.headers = {}
        response.geturl.return_value = "https://doi.org/doiRA/10.5555"
        response.read.return_value = _body("ra_istic.json")
        response.__enter__ = MagicMock(return_value=response)
        response.__exit__ = MagicMock(side_effect=OSError("close failure"))
        transport = MagicMock(return_value=response)

    with patch("chinese_literature_client._safe_urlopen", transport):
        with pytest.raises(ChineseLiteratureUnavailable, match="network error"):
            _client().ra_for(ISTIC_DOI)


def test_truncated_body_raises_unavailable():
    """IncompleteRead inherits HTTPException, not OSError — a truncated body
    must degrade, never become a miss."""
    from chinese_literature_client import ChineseLiteratureUnavailable

    resp = MagicMock()
    resp.status = 200
    resp.headers = {}
    resp.geturl.return_value = "https://doi.org/doiRA/10.5555"
    resp.read.side_effect = http.client.IncompleteRead(partial=b"{", expected=200)
    resp.__enter__ = MagicMock(return_value=resp)
    resp.__exit__ = MagicMock(return_value=None)

    with patch("chinese_literature_client._safe_urlopen", return_value=resp):
        with pytest.raises(ChineseLiteratureUnavailable, match="read failed"):
            _client().ra_for(ISTIC_DOI)


def test_unparseable_200_body_raises_unavailable():
    """#331: an HTML error page served with 200 by a proxy/CDN must degrade, not
    be recorded as an empty result."""
    from chinese_literature_client import ChineseLiteratureUnavailable

    transport = FakeTransport([(_is_esearch, _ok(_body("error_5xx.html")))])
    with patch("chinese_literature_client._safe_urlopen", transport):
        with pytest.raises(ChineseLiteratureUnavailable):
            _client().journal_is_indexed("Hecheng Ceshi Yi Xue Za Zhi")


@pytest.mark.parametrize(
    "body",
    [
        b'{"unexpected": true}',
        b'{"esearchresult":{"idlist":[null]}}',
        b'{"esearchresult":{"idlist":[42]}}',
        b'{"esearchresult":{"idlist":[""]}}',
        b'{"esearchresult":{"idlist":["0"]}}',
        b'{"esearchresult":{"count":false,"idlist":[]}}',
        b'{"esearchresult":{"count":"0","idlist":["999999901"]}}',
        b'{"esearchresult":{"count":"1","idlist":[]}}',
        (b'{"esearchresult":{"count":"' + b"9" * 5000 + b'","idlist":[]}}'),
        b'{"esearchresult":{"count":"2","idlist":["999999901","999999901"]}}',
    ],
)
def test_unexpected_esearch_shape_raises_unavailable(body):
    from chinese_literature_client import ChineseLiteratureUnavailable

    transport = FakeTransport([(_is_esearch, _ok(body))])
    with patch("chinese_literature_client._safe_urlopen", transport):
        with pytest.raises(ChineseLiteratureUnavailable):
            _client().journal_is_indexed("Hecheng Ceshi Yi Xue Za Zhi")


@pytest.mark.parametrize(
    "body",
    [
        b'{"result": {"999999901": 42}}',
        b'{"result": {"999999901": {"articleids": {}}}}',
        b'{"result": {"999999901": {"articleids": [], "issn": {}}}}',
        b'{"result": {"999999901": {"articleids": [], "title": false}}}',
        b'{"result": {"999999901": {"articleids": [], "pubdate": false}}}',
        b'{"result": {"999999901": {"articleids": [], "pubdate": "garbage"}}}',
        '{"result": {"999999901": {"articleids": [], "pubdate": "٢٠٢٦"}}}'.encode(),
        b'{"result": {"999999901": {"articleids": [], "source": []}}}',
        b'{"result": {"999999901": {"articleids": [], "lang": false}}}',
        b'{"result": {"999999901": {"articleids": [{"idtype": false, "value": "x"}]}}}',
        b'{"result": {"999999901": {"articleids": [{"idtype": "doi", "value": false}]}}}',
        b'{"result": {"999999901": {"articleids": [{"idtype": "doi", "value": "10.a/x"}, {"idtype": "doi", "value": "10.b/y"}]}}}',
        b'{"result": {"uids": ["888888888"], "999999901": {"articleids": []}}}',
        b'{"result": {"uids": [null], "999999901": {"articleids": []}}}',
        b'{"result": {"uids": ["999999901"], "999999901": {"uid": "888888888", "articleids": []}}}',
        b'{"result": {"uids": ["999999901"], "999999901": {"uid": 999999901, "articleids": []}}}',
    ],
)
def test_unexpected_esummary_shape_raises_unavailable(body):
    from chinese_literature_client import ChineseLiteratureUnavailable

    transport = FakeTransport([(_is_esummary, _ok(body))])
    with patch("chinese_literature_client._safe_urlopen", transport):
        with pytest.raises(ChineseLiteratureUnavailable):
            _client()._esummary("999999901")


def test_resolve_propagates_unavailable_rather_than_returning_a_verdict():
    """fail-closed: `resolve` has no `unreachable` return value by design. An
    outage must reach the caller as an exception so it can never be silently
    rendered as a lookup result."""
    from chinese_literature_client import ChineseLiteratureUnavailable

    transport = FakeTransport([(_is_ra, _http_error(503))])
    with patch("chinese_literature_client._safe_urlopen", transport):
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
    with patch("chinese_literature_client._safe_urlopen", transport):
        client = _client()
        client.ra_for(ISTIC_DOI)
        # A DOI request must not make the (independent) NCBI anchor wait.
        client.journal_is_indexed("Hecheng Ceshi Yi Xue Za Zhi")
        assert sleeps == []
        # A second NCBI request on a frozen clock does pace at the NCBI floor.
        client.journal_is_indexed("Hecheng Ceshi Yi Xue Za Zhi")
        assert sleeps == [pytest.approx(0.34)]


# ------------------------------------------------------------ checklist shape


def test_every_applicable_non_matched_scenario_emits_exactly_one_checklist_row():
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
        with patch("chinese_literature_client._safe_urlopen", transport):
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
