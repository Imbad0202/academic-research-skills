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

Known mapping limitation: Semantic Scholar, OpenAlex, and arXiv return
display names, which land whole in the author `family` field; only Crossref
supplies structured surnames. The ledger builder's weak author dedup key
therefore cannot match a DOI-less record across those indexes and Crossref.
"""
from __future__ import annotations

import argparse
import base64
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
from typing import Any, Callable
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ElementTree

# Keep the sibling import working whether this file is executed directly or
# imported as scripts.claim_standing_discovery, without creating a second
# module instance (exception identity matters across these tools).
try:
    from scripts import build_claim_standing_candidate_ledger as substrate
except ImportError:  # direct script execution
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import build_claim_standing_candidate_ledger as substrate  # noqa: E402

USER_AGENT = "ars-claim-standing-discovery/0.1"
MAX_RESPONSE_BYTES = 8 * 1024 * 1024
TIMEOUT_SECONDS = 30.0
RETRIEVAL_INPUT_SUFFIX = ".retrieval-input.json"
Transport = Callable[[str, dict[str, str], float], tuple[int, bytes]]


class DiscoveryError(RuntimeError):
    pass


def _fail(message: str) -> None:
    raise DiscoveryError(message)


class UnsupportedQuery(Exception):
    pass


class MalformedResponse(Exception):
    pass


class ServiceUnreachable(Exception):
    """DNS failure, refused connection, TLS failure: the service, not the body."""


def _now() -> str:
    return (
        datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    )


def _clean(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    stripped = " ".join(value.split())
    return stripped or None


def _exact_text(value: Any) -> str | None:
    """Abstract fidelity: keep the provider's exact string; blank becomes None."""
    if not isinstance(value, str) or not value.strip():
        return None
    return value


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


def _year_filter(
    date_filter: dict[str, Any], from_key: str, to_key: str
) -> str | None:
    filters = []
    if date_filter["from_year"] is not None:
        filters.append(f"{from_key}:{date_filter['from_year']}-01-01")
    if date_filter["through_year"] is not None:
        filters.append(f"{to_key}:{date_filter['through_year']}-12-31")
    return ",".join(filters) if filters else None


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
                publication_status=_S2_STATUS.get(
                    _clean(types[0]) if types else "", "unknown"
                ),
                abstract_text=_exact_text(record.get("abstract")),
                landing_url=_clean(record.get("url")),
                raw_record=record,
            )
        )
    return payload.get("total"), hits


# --- OpenAlex ---------------------------------------------------------------


def _openalex_request(query: str, date_filter: dict[str, Any], cap: int) -> str:
    params = {"search": query, "per-page": str(cap)}
    year_filter = _year_filter(
        date_filter, "from_publication_date", "to_publication_date"
    )
    if year_filter:
        params["filter"] = year_filter
    return "https://api.openalex.org/works?" + urllib.parse.urlencode(params)


def _openalex_abstract(inverted: Any) -> str | None:
    if not isinstance(inverted, dict) or not inverted:
        return None
    positions: list[tuple[int, str]] = []
    for word, indexes in inverted.items():
        for index in indexes:
            positions.append((index, word))
    # Reconstruction from the inverted index is derived text, not provider
    # bytes, so whitespace normalization here loses nothing exact.
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
                publication_status=_OPENALEX_STATUS.get(
                    _clean(record.get("type")) or "", "unknown"
                ),
                abstract_text=_openalex_abstract(record.get("abstract_inverted_index")),
                landing_url=_clean(record.get("id")),
                raw_record=record,
            )
        )
    return (payload.get("meta") or {}).get("count"), hits


# --- Crossref ---------------------------------------------------------------


def _crossref_request(query: str, date_filter: dict[str, Any], cap: int) -> str:
    params = {"query": query, "rows": str(cap)}
    year_filter = _year_filter(date_filter, "from-pub-date", "until-pub-date")
    if year_filter:
        params["filter"] = year_filter
    return "https://api.crossref.org/works?" + urllib.parse.urlencode(params)


_CROSSREF_STATUS = {"journal-article": "published", "posted-content": "preprint"}
# Conservative approximations of each provider's type vocabulary; anything
# outside the mapped set stays "unknown" rather than guessing.
_OPENALEX_STATUS = {"preprint": "preprint", "article": "published"}
_S2_STATUS = {"JournalArticle": "published"}


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
                # Crossref abstracts arrive as JATS-tagged text, retained
                # exactly as returned.
                abstract_text=_exact_text(record.get("abstract")),
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
    if '"' in query:
        raise UnsupportedQuery(
            "a double quote inside the accepted query would change the arXiv "
            "phrase-query grammar; refusing rather than rewriting the query"
        )
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

        summary_node = entry.find(f"{_ATOM}summary")
        summary = _exact_text(summary_node.text if summary_node is not None else None)
        published = _text(f"{_ATOM}published") or ""
        year = int(published[:4]) if published[:4].isdigit() else None
        raw_record = {
            "id": _text(f"{_ATOM}id"),
            "title": _text(f"{_ATOM}title"),
            "summary": summary,
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

_SHARED_PROVIDER_FIELDS = {
    "purpose": "scholarly_discovery",
    "pagination_behavior": (
        "single page up to the per-query cap; no follow-up page is requested"
    ),
    "adapter_version": "ars-discovery-0.1",
    "retention_state": "unknown",
    "retention_reference": None,
}


def _provider(
    index_id: str,
    product_identity: str,
    query_capability: str,
    *,
    abstract_availability: str = "mixed",
) -> dict[str, Any]:
    return {
        "index_id": index_id,
        "product_identity": product_identity,
        "query_capability": query_capability,
        "abstract_availability": abstract_availability,
        **_SHARED_PROVIDER_FIELDS,
    }


ADAPTERS: dict[str, dict[str, Any]] = {
    "semantic_scholar": {
        "request": _s2_request,
        "parse": _s2_parse,
        "provider": _provider(
            "semantic_scholar",
            "Semantic Scholar Academic Graph API paper search",
            "keyword relevance search over titles and abstracts",
        ),
    },
    "openalex": {
        "request": _openalex_request,
        "parse": _openalex_parse,
        "provider": _provider(
            "openalex",
            "OpenAlex works search API",
            "full-text relevance search over work metadata",
        ),
    },
    "crossref": {
        "request": _crossref_request,
        "parse": _crossref_parse,
        "provider": _provider(
            "crossref",
            "Crossref REST API works query",
            "bibliographic keyword query over registered works",
        ),
    },
    "arxiv": {
        "request": _arxiv_request,
        "parse": _arxiv_parse,
        "provider": _provider(
            "arxiv",
            "arXiv API query interface",
            "phrase search over all preprint fields; no year filter",
            abstract_availability="available_when_returned",
        ),
    },
}


def provider_roster_defaults() -> dict[str, dict[str, Any]]:
    return {
        index_id: dict(adapter["provider"]) for index_id, adapter in ADAPTERS.items()
    }


# --- Transport --------------------------------------------------------------


class _RefuseRedirects(urllib.request.HTTPRedirectHandler):
    """A redirect can send the consented query to an off-roster host; refuse."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        return None


_OPENER = urllib.request.build_opener(_RefuseRedirects())


def live_transport(url: str, headers: dict[str, str], timeout: float) -> tuple[int, bytes]:
    request = urllib.request.Request(url, headers=headers)
    try:
        with _OPENER.open(request, timeout=timeout) as response:
            body = response.read(MAX_RESPONSE_BYTES + 1)
            if len(body) > MAX_RESPONSE_BYTES:
                raise MalformedResponse("provider body exceeds the bounded read")
            return response.status, body
    except urllib.error.HTTPError as exc:
        # A refused redirect surfaces here as its 3xx code and maps through
        # _status_outcome (3xx falls into the service_unavailable arm).
        return exc.code, exc.read(MAX_RESPONSE_BYTES)
    except urllib.error.URLError as exc:
        if isinstance(exc.reason, TimeoutError):
            raise TimeoutError(str(exc.reason)) from exc
        raise ServiceUnreachable(str(exc.reason)) from exc


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
    if 400 <= status < 500:
        # The provider judged the request itself invalid.
        return "unsupported_query"
    return "service_unavailable"


def _raw_hit_validator():
    schema = json.loads(
        (substrate.SCHEMA_DIR / "retrieval_input.schema.json").read_bytes()
    )
    from jsonschema import Draft202012Validator

    return Draft202012Validator({"$defs": schema["$defs"], **schema["$defs"]["raw_hit"]})


_ROW_VALIDATOR = None


def _row_text_conforms(row: dict[str, Any]) -> bool:
    checks = [
        row["provider_record_id"] is None
        or substrate.has_visible_semantic_text(
            row["provider_record_id"], allow_symbols=False
        ),
        row["title"] is None
        or substrate.has_visible_semantic_text(row["title"], allow_symbols=True),
        row["abstract_text"] is None
        or substrate.has_visible_semantic_text(
            row["abstract_text"], allow_symbols=True
        ),
    ]
    for author in row["authors"]:
        for field in ("family", "given"):
            checks.append(
                author[field] is None
                or substrate.has_visible_semantic_text(
                    author[field], allow_symbols=False
                )
            )
    return all(checks)


def _rows_conform(rows: list[dict[str, Any]]) -> bool:
    global _ROW_VALIDATOR
    if _ROW_VALIDATOR is None:
        _ROW_VALIDATOR = _raw_hit_validator()
    return all(
        _ROW_VALIDATOR.is_valid(row) and _row_text_conforms(row) for row in rows
    )


def _run_attempt(
    adapter: dict[str, Any],
    query: dict[str, Any],
    cap: int,
    transport: Transport,
) -> tuple[str, int | None, list[dict[str, Any]]]:
    try:
        url = adapter["request"](
            query["accepted_query_text"], query["date_filter"], cap
        )
    except UnsupportedQuery:
        return "unsupported_query", None, []
    try:
        status, body = transport(url, {"User-Agent": USER_AGENT}, TIMEOUT_SECONDS)
    except TimeoutError:
        return "timeout", None, []
    except ServiceUnreachable:
        return "service_unavailable", None, []
    except MalformedResponse:
        return "malformed_response", None, []
    status_outcome = _status_outcome(status)
    if status_outcome is not None:
        return status_outcome, None, []
    try:
        provider_reported_count, provider_hits = adapter["parse"](body)
    except (
        MalformedResponse,
        ValueError,
        KeyError,
        TypeError,
        AttributeError,
        IndexError,
        UnicodeError,
    ):
        return "malformed_response", None, []
    return "success", provider_reported_count, provider_hits


def retrieve(plan: dict[str, Any], *, transport: Transport) -> dict[str, Any]:
    # retrieve() re-validates even when the CLI already did: it is a public
    # entry point that must not trust its caller.
    substrate.validate_schema(
        plan, substrate.plan_schema_filename(plan), "query plan"
    )
    substrate.validate_plan(plan)
    for provider in plan["provider_roster"]:
        index_id = provider["index_id"]
        if index_id not in ADAPTERS:
            _fail(f"no discovery adapter exists for index {index_id!r}")
        if provider != ADAPTERS[index_id]["provider"]:
            _fail(
                f"the consented provider block for {index_id!r} does not match "
                "this adapter's declared block; re-consent against "
                "provider_roster_defaults()"
            )

    cap = plan["caps"]["max_hits_per_query_index"]
    consent_receipt_id = plan["consent"]["consent_receipt_id"]
    attempts: list[dict[str, Any]] = []
    raw_hits: list[dict[str, Any]] = []
    attempt_number = 0
    hit_number = 0
    for query in plan["queries"]:
        for index_id in query["index_targets"]:
            attempt_number += 1
            attempt_id = f"attempt-{attempt_number:03d}"
            started_at = _now()
            outcome, provider_reported_count, provider_hits = _run_attempt(
                ADAPTERS[index_id], query, cap, transport
            )
            completed_at = _now()
            if provider_reported_count is not None and (
                not isinstance(provider_reported_count, int)
                or isinstance(provider_reported_count, bool)
                or provider_reported_count < len(provider_hits)
            ):
                outcome, provider_reported_count, provider_hits = (
                    "malformed_response",
                    None,
                    [],
                )
            retained = provider_hits[:cap]
            hit_number_start = hit_number
            attempt_rows: list[dict[str, Any]] = []
            try:
                for rank, hit in enumerate(retained, 1):
                    hit_number += 1
                    raw_record = hit.pop("raw_record")
                    abstract_text = hit["abstract_text"]
                    attempt_rows.append(
                        {
                            "raw_hit_id": f"hit-{hit_number:03d}",
                            "probe_id": plan["probe_id"],
                            "query_id": query["query_id"],
                            "index_id": index_id,
                            "attempt_id": attempt_id,
                            "provider_rank": rank,
                            **hit,
                            "abstract_sha256": (
                                substrate.text_digest(abstract_text)
                                if abstract_text is not None
                                else None
                            ),
                            "returned_at": completed_at,
                            "raw_metadata_sha256": substrate.digest(raw_record),
                            "explicit_version_of_raw_hit_id": None,
                        }
                    )
                rows_ok = outcome != "success" or _rows_conform(attempt_rows)
            except (ValueError, TypeError, UnicodeError, substrate.LedgerError):
                rows_ok = False
            if outcome == "success" and not rows_ok:
                # A provider-contract violation (overlong field, bad type,
                # undigestible value) poisons only its own attempt, never
                # the whole fleet.
                outcome, provider_reported_count = "malformed_response", None
                provider_hits, retained, attempt_rows = [], [], []
                hit_number = hit_number_start
            raw_hits.extend(attempt_rows)
            attempts.append(
                {
                    "attempt_id": attempt_id,
                    "query_id": query["query_id"],
                    "index_id": index_id,
                    "started_at": started_at,
                    "completed_at": completed_at,
                    "outcome": outcome,
                    "provider_reported_count": provider_reported_count,
                    "returned_count": len(provider_hits),
                    "retained_hit_count": len(retained),
                    "truncated_count": len(provider_hits) - len(retained),
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


def authorized_retrieval_input_path(plan: dict[str, Any]) -> Path:
    """The only writable output path: derived from the hash-bound consent."""
    return substrate.authorized_export_path(plan, RETRIEVAL_INPUT_SUFFIX)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    retrieve_parser = commands.add_parser(
        "retrieve",
        help="run the consented discovery queries and write a retrieval input",
    )
    retrieve_parser.add_argument("--query-plan", type=Path, required=True)
    retrieve_parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help=(
            "must equal the consent's authorized_output_path plus "
            f"'{RETRIEVAL_INPUT_SUFFIX}'; any other path is refused"
        ),
    )
    retrieve_parser.add_argument(
        "--transport-fixture",
        default=None,
        help="path to a fixture route file for offline runs; omit for live HTTP",
    )
    args = parser.parse_args(argv)
    try:
        plan = substrate.load_json(args.query_plan)
        substrate.validate_schema(
            plan, substrate.plan_schema_filename(plan), "query plan"
        )
        substrate.validate_plan(plan)
        if plan["consent"]["local_persistence"] != "explicit_local_export":
            _fail(
                "the hash-bound consent says session_only: this CLI refuses to "
                "persist a retrieval input without explicit_local_export consent"
            )
        expected_output = authorized_retrieval_input_path(plan)
        if str(args.output) != str(expected_output):
            _fail(
                "output does not match the hash-bound consent: the retrieval "
                f"input may be written only to {expected_output}"
            )
        if args.output.exists():
            _fail(f"refusing to overwrite existing output {args.output}")
        if args.transport_fixture:
            transport = _fixture_transport(Path(args.transport_fixture))
        else:
            transport = live_transport
        retained = retrieve(plan, transport=transport)
        substrate.write_new_ledger(args.output, retained)
    except (DiscoveryError, substrate.LedgerError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
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
