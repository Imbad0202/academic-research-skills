#!/usr/bin/env python3
"""Live discovery adapters for the #655 claim-standing probe (Track A head).

Turns a consent-bound `claim-standing-query-plan/1.0` into a
`claim-standing-retrieval-input/1.0` record: one closed adapter per index, the
frozen v1 caps, adapter-boundary truncation, and the closed failure vocabulary.
The design's resolver clients stay untouched — these adapters are the separate
discovery interfaces the design requires, and this module never imports the
pinned resolver clients.

Boundaries: relevance assessments are deliberately NOT produced here — the
#719 contracts define them as caller-supplied, and the relevance assessor is a
later, separately consented slice. The emitted retrieval input therefore
carries an empty `relevance_assessments` array; the candidate-ledger builder
will refuse to finalize until a caller supplies one assessment per computed
work family. No stance classification, rendering, pipeline, or evidence-row
surface exists here. Adapters are written against the providers' documented
public APIs but have not been exercised live; the first live run is expected
to surface mapping drift and must be treated as a diagnostic run.
"""
from __future__ import annotations

import argparse
import base64
from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Any, Callable
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ElementTree

import build_claim_standing_candidate_ledger as substrate

USER_AGENT = "ars-claim-standing-discovery/0.1"
TIMEOUT_SECONDS = 30.0
Transport = Callable[[str, dict[str, str], float], tuple[int, bytes]]


class DiscoveryError(RuntimeError):
    pass


def _fail(message: str) -> None:
    raise DiscoveryError(message)


class UnsupportedQuery(Exception):
    pass


class MalformedResponse(Exception):
    pass


def _now() -> str:
    return (
        datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    )


def _clean(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    stripped = " ".join(value.split())
    return stripped or None


def _hit(
    *,
    provider_record_id: str | None,
    doi: str | None,
    title: str | None,
    authors: list[dict[str, str | None]],
    year: int | None,
    language: str | None,
    document_type: str | None,
    publication_status: str,
    abstract_text: str | None,
    landing_url: str | None,
    raw_record: Any,
) -> dict[str, Any]:
    return {
        "provider_record_id": provider_record_id,
        "doi": doi,
        "title": title,
        "authors": authors,
        "year": year if isinstance(year, int) else None,
        "language": language,
        "document_type": document_type,
        "publication_status": publication_status,
        "abstract_state": "available" if abstract_text else "missing",
        "abstract_text": abstract_text,
        "landing_url": landing_url,
        "raw_record": raw_record,
    }


def _name_author(name: Any) -> dict[str, str | None]:
    return {"family": _clean(name), "given": None}


# --- Semantic Scholar -------------------------------------------------------


def _s2_request(query: str, date_filter: dict[str, Any], cap: int) -> str:
    params = {
        "query": query,
        "limit": str(cap),
        "fields": "title,abstract,year,authors,externalIds,publicationTypes,url",
    }
    from_year, through_year = date_filter["from_year"], date_filter["through_year"]
    if from_year is not None or through_year is not None:
        params["year"] = (
            f"{from_year if from_year is not None else ''}-"
            f"{through_year if through_year is not None else ''}"
        )
    return (
        "https://api.semanticscholar.org/graph/v1/paper/search?"
        + urllib.parse.urlencode(params)
    )


def _s2_parse(body: bytes) -> tuple[int | None, list[dict[str, Any]]]:
    payload = json.loads(body.decode("utf-8"))
    hits = []
    for record in payload["data"]:
        external_ids = record.get("externalIds") or {}
        types = record.get("publicationTypes") or []
        hits.append(
            _hit(
                provider_record_id=_clean(record.get("paperId")),
                doi=_clean(external_ids.get("DOI")),
                title=_clean(record.get("title")),
                authors=[
                    _name_author(author.get("name"))
                    for author in record.get("authors") or []
                ],
                year=record.get("year"),
                language=None,
                document_type=_clean(types[0]) if types else None,
                publication_status="unknown",
                abstract_text=_clean(record.get("abstract")),
                landing_url=_clean(record.get("url")),
                raw_record=record,
            )
        )
    return payload.get("total"), hits


# --- OpenAlex ---------------------------------------------------------------


def _openalex_request(query: str, date_filter: dict[str, Any], cap: int) -> str:
    params = {"search": query, "per-page": str(cap)}
    filters = []
    if date_filter["from_year"] is not None:
        filters.append(f"from_publication_date:{date_filter['from_year']}-01-01")
    if date_filter["through_year"] is not None:
        filters.append(f"to_publication_date:{date_filter['through_year']}-12-31")
    if filters:
        params["filter"] = ",".join(filters)
    return "https://api.openalex.org/works?" + urllib.parse.urlencode(params)


def _openalex_abstract(inverted: Any) -> str | None:
    if not isinstance(inverted, dict) or not inverted:
        return None
    positions: list[tuple[int, str]] = []
    for word, indexes in inverted.items():
        for index in indexes:
            positions.append((index, word))
    return _clean(" ".join(word for _, word in sorted(positions)))


def _openalex_parse(body: bytes) -> tuple[int | None, list[dict[str, Any]]]:
    payload = json.loads(body.decode("utf-8"))
    hits = []
    for record in payload["results"]:
        doi = _clean(record.get("doi"))
        if doi and doi.lower().startswith("https://doi.org/"):
            doi = doi[len("https://doi.org/") :]
        hits.append(
            _hit(
                provider_record_id=_clean(record.get("id")),
                doi=doi,
                title=_clean(record.get("display_name")),
                authors=[
                    _name_author((row.get("author") or {}).get("display_name"))
                    for row in record.get("authorships") or []
                ],
                year=record.get("publication_year"),
                language=_clean(record.get("language")),
                document_type=_clean(record.get("type")),
                publication_status="unknown",
                abstract_text=_openalex_abstract(record.get("abstract_inverted_index")),
                landing_url=_clean(record.get("id")),
                raw_record=record,
            )
        )
    return (payload.get("meta") or {}).get("count"), hits


# --- Crossref ---------------------------------------------------------------


def _crossref_request(query: str, date_filter: dict[str, Any], cap: int) -> str:
    params = {"query": query, "rows": str(cap)}
    filters = []
    if date_filter["from_year"] is not None:
        filters.append(f"from-pub-date:{date_filter['from_year']}-01-01")
    if date_filter["through_year"] is not None:
        filters.append(f"until-pub-date:{date_filter['through_year']}-12-31")
    if filters:
        params["filter"] = ",".join(filters)
    return "https://api.crossref.org/works?" + urllib.parse.urlencode(params)


_CROSSREF_STATUS = {"journal-article": "published", "posted-content": "preprint"}


def _crossref_parse(body: bytes) -> tuple[int | None, list[dict[str, Any]]]:
    message = json.loads(body.decode("utf-8"))["message"]
    hits = []
    for record in message["items"]:
        titles = record.get("title") or []
        date_parts = (record.get("issued") or {}).get("date-parts") or [[None]]
        record_type = _clean(record.get("type"))
        hits.append(
            _hit(
                provider_record_id=_clean(record.get("DOI")),
                doi=_clean(record.get("DOI")),
                title=_clean(titles[0]) if titles else None,
                authors=[
                    {"family": _clean(row.get("family")), "given": _clean(row.get("given"))}
                    for row in record.get("author") or []
                ],
                year=date_parts[0][0] if date_parts and date_parts[0] else None,
                language=_clean(record.get("language")),
                document_type=record_type,
                publication_status=_CROSSREF_STATUS.get(record_type or "", "unknown"),
                # Crossref abstracts arrive as JATS-tagged text; the exact
                # returned string is retained without cleaning.
                abstract_text=_clean(record.get("abstract")),
                landing_url=_clean(record.get("URL")),
                raw_record=record,
            )
        )
    return message.get("total-results"), hits


# --- arXiv ------------------------------------------------------------------

_ATOM = "{http://www.w3.org/2005/Atom}"
_OPENSEARCH = "{http://a9.com/-/spec/opensearch/1.1/}"
_ARXIV_NS = "{http://arxiv.org/schemas/atom}"


def _arxiv_request(query: str, date_filter: dict[str, Any], cap: int) -> str:
    if date_filter["from_year"] is not None or date_filter["through_year"] is not None:
        raise UnsupportedQuery("the arXiv API query interface has no year filter")
    params = {
        "search_query": f'all:"{query}"',
        "start": "0",
        "max_results": str(cap),
    }
    return "https://export.arxiv.org/api/query?" + urllib.parse.urlencode(params)


def _arxiv_parse(body: bytes) -> tuple[int | None, list[dict[str, Any]]]:
    try:
        feed = ElementTree.fromstring(body.decode("utf-8"))
    except ElementTree.ParseError as exc:
        raise MalformedResponse(str(exc)) from exc
    total_node = feed.find(f"{_OPENSEARCH}totalResults")
    total = (
        int(total_node.text)
        if total_node is not None and total_node.text and total_node.text.isdigit()
        else None
    )
    hits = []
    for entry in feed.findall(f"{_ATOM}entry"):
        def _text(tag: str) -> str | None:
            node = entry.find(tag)
            return _clean(node.text) if node is not None else None

        published = _text(f"{_ATOM}published") or ""
        year = int(published[:4]) if published[:4].isdigit() else None
        raw_record = {
            "id": _text(f"{_ATOM}id"),
            "title": _text(f"{_ATOM}title"),
            "summary": _text(f"{_ATOM}summary"),
            "published": published or None,
            "authors": [
                _clean(node.text)
                for node in entry.findall(f"{_ATOM}author/{_ATOM}name")
            ],
            "doi": _text(f"{_ARXIV_NS}doi"),
        }
        hits.append(
            _hit(
                provider_record_id=raw_record["id"],
                doi=raw_record["doi"],
                title=raw_record["title"],
                authors=[_name_author(name) for name in raw_record["authors"]],
                year=year,
                language=None,
                document_type="preprint",
                publication_status="preprint",
                abstract_text=raw_record["summary"],
                landing_url=raw_record["id"],
                raw_record=raw_record,
            )
        )
    return total, hits


# --- Registry ---------------------------------------------------------------

ADAPTERS: dict[str, dict[str, Any]] = {
    "semantic_scholar": {
        "request": _s2_request,
        "parse": _s2_parse,
        "provider": {
            "index_id": "semantic_scholar",
            "product_identity": "Semantic Scholar Academic Graph API paper search",
            "purpose": "scholarly_discovery",
            "query_capability": "keyword relevance search over titles and abstracts",
            "abstract_availability": "mixed",
            "pagination_behavior": "single page up to the per-query cap; no follow-up page is requested",
            "adapter_version": "ars-discovery-0.1",
            "retention_state": "unknown",
            "retention_reference": None,
        },
    },
    "openalex": {
        "request": _openalex_request,
        "parse": _openalex_parse,
        "provider": {
            "index_id": "openalex",
            "product_identity": "OpenAlex works search API",
            "purpose": "scholarly_discovery",
            "query_capability": "full-text relevance search over work metadata",
            "abstract_availability": "mixed",
            "pagination_behavior": "single page up to the per-query cap; no follow-up page is requested",
            "adapter_version": "ars-discovery-0.1",
            "retention_state": "unknown",
            "retention_reference": None,
        },
    },
    "crossref": {
        "request": _crossref_request,
        "parse": _crossref_parse,
        "provider": {
            "index_id": "crossref",
            "product_identity": "Crossref REST API works query",
            "purpose": "scholarly_discovery",
            "query_capability": "bibliographic keyword query over registered works",
            "abstract_availability": "mixed",
            "pagination_behavior": "single page up to the per-query cap; no follow-up page is requested",
            "adapter_version": "ars-discovery-0.1",
            "retention_state": "unknown",
            "retention_reference": None,
        },
    },
    "arxiv": {
        "request": _arxiv_request,
        "parse": _arxiv_parse,
        "provider": {
            "index_id": "arxiv",
            "product_identity": "arXiv API query interface",
            "purpose": "scholarly_discovery",
            "query_capability": "phrase search over all preprint fields; no year filter",
            "abstract_availability": "available_when_returned",
            "pagination_behavior": "single page up to the per-query cap; no follow-up page is requested",
            "adapter_version": "ars-discovery-0.1",
            "retention_state": "unknown",
            "retention_reference": None,
        },
    },
}


def provider_roster_defaults() -> dict[str, dict[str, Any]]:
    return {
        index_id: dict(adapter["provider"]) for index_id, adapter in ADAPTERS.items()
    }


# --- Transport --------------------------------------------------------------


def live_transport(url: str, headers: dict[str, str], timeout: float) -> tuple[int, bytes]:
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read()
    except TimeoutError:
        raise
    except urllib.error.URLError as exc:
        if isinstance(exc.reason, TimeoutError):
            raise TimeoutError(str(exc.reason)) from exc
        raise MalformedResponse(str(exc.reason)) from exc


def _fixture_transport(path: Path) -> Transport:
    routes = json.loads(path.read_text(encoding="utf-8"))

    def transport(url: str, headers: dict[str, str], timeout: float) -> tuple[int, bytes]:
        for marker, spec in routes.items():
            if marker in url:
                if spec.get("body_json") is not None:
                    body = json.dumps(spec["body_json"]).encode("utf-8")
                elif spec.get("body_base64"):
                    body = base64.b64decode(spec["body_base64"])
                else:
                    body = b""
                return spec["status"], body
        raise MalformedResponse(f"no fixture route for {url}")

    return transport


# --- Retrieval --------------------------------------------------------------


def _status_outcome(status: int) -> str | None:
    if status == 200:
        return None
    if status in (401, 403):
        return "authentication_failed"
    if status == 429:
        return "rate_limited"
    return "service_unavailable"


def retrieve(plan: dict[str, Any], *, transport: Transport) -> dict[str, Any]:
    substrate.validate_schema(plan, "query_plan.schema.json", "query plan")
    substrate.validate_plan(plan)
    roster_ids = [provider["index_id"] for provider in plan["provider_roster"]]
    for index_id in roster_ids:
        if index_id not in ADAPTERS:
            _fail(f"no discovery adapter exists for index {index_id!r}")

    cap = plan["caps"]["max_hits_per_query_index"]
    consent_receipt_id = plan["consent"]["consent_receipt_id"]
    attempts: list[dict[str, Any]] = []
    raw_hits: list[dict[str, Any]] = []
    attempt_number = 0
    hit_number = 0
    for query in plan["queries"]:
        for index_id in query["index_targets"]:
            adapter = ADAPTERS[index_id]
            attempt_number += 1
            attempt_id = f"attempt-{attempt_number:03d}"
            started_at = _now()
            outcome = "success"
            provider_reported_count: int | None = None
            provider_hits: list[dict[str, Any]] = []
            try:
                url = adapter["request"](
                    query["accepted_query_text"], query["date_filter"], cap
                )
            except UnsupportedQuery:
                outcome = "unsupported_query"
            else:
                try:
                    status, body = transport(url, {"User-Agent": USER_AGENT}, TIMEOUT_SECONDS)
                except TimeoutError:
                    outcome = "timeout"
                except MalformedResponse:
                    outcome = "malformed_response"
                else:
                    status_outcome = _status_outcome(status)
                    if status_outcome is not None:
                        outcome = status_outcome
                    else:
                        try:
                            provider_reported_count, provider_hits = adapter["parse"](body)
                        except (
                            MalformedResponse,
                            ValueError,
                            KeyError,
                            TypeError,
                            UnicodeError,
                        ):
                            outcome = "malformed_response"
                            provider_hits = []
            completed_at = _now()
            returned_count = len(provider_hits)
            retained = provider_hits[:cap]
            for rank, hit in enumerate(retained, 1):
                hit_number += 1
                raw_hits.append(
                    {
                        "raw_hit_id": f"hit-{hit_number:03d}",
                        "probe_id": plan["probe_id"],
                        "query_id": query["query_id"],
                        "index_id": index_id,
                        "attempt_id": attempt_id,
                        "provider_rank": rank,
                        "provider_record_id": hit["provider_record_id"],
                        "doi": hit["doi"],
                        "title": hit["title"],
                        "authors": hit["authors"],
                        "year": hit["year"],
                        "language": hit["language"],
                        "document_type": hit["document_type"],
                        "publication_status": hit["publication_status"],
                        "abstract_state": hit["abstract_state"],
                        "abstract_text": hit["abstract_text"],
                        "abstract_sha256": (
                            substrate.text_digest(hit["abstract_text"])
                            if hit["abstract_text"] is not None
                            else None
                        ),
                        "landing_url": hit["landing_url"],
                        "returned_at": completed_at,
                        "raw_metadata_sha256": substrate.digest(hit["raw_record"]),
                        "explicit_version_of_raw_hit_id": None,
                    }
                )
            attempts.append(
                {
                    "attempt_id": attempt_id,
                    "query_id": query["query_id"],
                    "index_id": index_id,
                    "started_at": started_at,
                    "completed_at": completed_at,
                    "outcome": outcome,
                    "provider_reported_count": provider_reported_count,
                    "returned_count": returned_count,
                    "retained_hit_count": len(retained),
                    "truncated_count": returned_count - len(retained),
                    "retry_of_attempt_id": None,
                    "retry_authorization_receipt_id": None,
                    "consent_receipt_id": consent_receipt_id,
                }
            )
    if len(raw_hits) > plan["caps"]["max_raw_hits"]:
        _fail("retained raw hits exceed the frozen 240-row ceiling")
    retained_input = {
        "schema_version": substrate.INPUT_VERSION,
        "query_plan_sha256": plan["plan_sha256"],
        "attempts": attempts,
        "retry_authorizations": [],
        "raw_hits": raw_hits,
        "researcher_confirmed_version_relations": [],
        "relevance_assessments": [],
        "completed_at": _now(),
    }
    retained_input["retrieval_input_sha256"] = substrate.bound_digest(
        retained_input, "retrieval_input_sha256"
    )
    substrate.validate_schema(
        retained_input, "retrieval_input.schema.json", "retrieval input"
    )
    return retained_input


# --- CLI --------------------------------------------------------------------


def _write_exclusive(path: Path, payload: dict[str, Any]) -> None:
    rendered = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
        stream.write(rendered)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    retrieve_parser = commands.add_parser(
        "retrieve",
        help="run the consented discovery queries and write a retrieval input",
    )
    retrieve_parser.add_argument("--query-plan", type=Path, required=True)
    retrieve_parser.add_argument("--output", type=Path, required=True)
    retrieve_parser.add_argument(
        "--transport-fixture",
        default=None,
        help="path to a fixture route file for offline runs; omit for live HTTP",
    )
    args = parser.parse_args(argv)
    try:
        plan = substrate.load_json(args.query_plan)
        substrate.validate_schema(plan, "query_plan.schema.json", "query plan")
        substrate.validate_plan(plan)
        if plan["consent"]["local_persistence"] != "explicit_local_export":
            _fail(
                "the hash-bound consent says session_only: this CLI refuses to "
                "persist a retrieval input without explicit_local_export consent"
            )
        if args.output.exists():
            _fail(f"refusing to overwrite existing output {args.output}")
        if args.transport_fixture and args.transport_fixture != "none":
            transport = _fixture_transport(Path(args.transport_fixture))
        else:
            transport = live_transport
        retained = retrieve(plan, transport=transport)
        _write_exclusive(args.output, retained)
    except (DiscoveryError, substrate.LedgerError, OSError, ValueError) as exc:
        print(str(exc))
        return 1
    print(
        json.dumps(
            {
                "attempts": len(retained["attempts"]),
                "raw_hits": len(retained["raw_hits"]),
                "retrieval_input_sha256": retained["retrieval_input_sha256"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
