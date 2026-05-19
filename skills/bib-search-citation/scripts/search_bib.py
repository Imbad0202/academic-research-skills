#!/usr/bin/env python3
"""Search and filter BibTeX/BibLaTeX files without external dependencies.

Version 2 adds a compact query language so the caller can write expressions like:

    mamba forecasting author:Cheng year>=2024 has:code type:article,misc

The script still accepts the original JSON spec shape for backward compatibility.
"""

from __future__ import annotations

import argparse
import json
import re
import shlex
import sys
from collections import Counter
from collections.abc import Sequence
from pathlib import Path
from typing import Any

TOKEN_RE = re.compile(r"[a-z0-9]+|[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]+", re.IGNORECASE)
LATEX_ESCAPE_RE = re.compile(r"\\([%&_#$])")
WHITESPACE_RE = re.compile(r"\s+")
FIELD_OP_RE = re.compile(
    r"^(?P<neg>-)?(?P<field>[A-Za-z_][A-Za-z0-9_-]*)(?P<op>:|=|>=|<=|>|<)(?P<value>.+)$"
)

DEFAULT_FIELDS = [
    "key",
    "title",
    "shorttitle",
    "author",
    "year",
    "venue",
    "doi",
    "eprint",
    "keywords",
    "annotation",
    "abstract",
]

WEIGHTED_FIELDS = [
    ("title", 7.0),
    ("shorttitle", 6.0),
    ("keywords", 5.0),
    ("annotation", 4.5),
    ("abstract", 3.5),
    ("author", 3.0),
    ("venue", 2.5),
    ("doi", 2.0),
    ("eprint", 2.0),
    ("raw_bib", 1.0),
]

CODE_HINT_FIELDS = ["url", "howpublished", "note", "abstract", "annotation", "keywords"]
CODE_HINT_TERMS = [
    "github",
    "gitlab",
    "code",
    "repository",
    "repo",
    "source code",
    "code available",
]
PDF_FIELDS = ["file", "pdf", "url"]
FIELD_ALIASES = {
    "authors": "author",
    "venue": "venue",
    "journal": "journal",
    "booktitle": "booktitle",
    "tag": "annotation",
    "tags": "annotation",
    "kw": "keywords",
    "arxiv": "eprint",
    "entrytype": "type",
    "kind": "type",
    "bib": "raw",
    "citation": "cite",
    "citations": "cite",
}


class SpecError(ValueError):
    """Raised when query syntax cannot be parsed sensibly."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Search and filter a .bib file.")
    parser.add_argument("--bib", required=True, help="Path to the input .bib file")

    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--spec-json", help="Inline JSON search specification")
    input_group.add_argument(
        "--spec-file", help="Path to a JSON file containing the search specification"
    )
    input_group.add_argument(
        "--query", help="Compact query expression with optional inline filters"
    )

    parser.add_argument("--limit", type=int, help="Override result limit when using --query")
    parser.add_argument(
        "--sort", choices=["relevance", "year_desc", "year_asc", "title"], help="Override sort mode"
    )
    parser.add_argument(
        "--citation-mode", choices=["none", "latex", "typst", "both"], help="Override citation mode"
    )
    parser.add_argument(
        "--include-raw-bib", action="store_true", help="Include raw BibTeX in results"
    )
    parser.add_argument(
        "--return-fields",
        help="Comma-separated result fields when using --query, for example key,title,year,abstract",
    )
    return parser.parse_args()


# -----------------------------
# Loading and normalization
# -----------------------------


def load_spec(args: argparse.Namespace) -> dict[str, Any]:
    if args.spec_json:
        spec = json.loads(args.spec_json)
    elif args.spec_file:
        with open(args.spec_file, encoding="utf-8") as handle:
            spec = json.load(handle)
    else:
        spec = spec_from_compact_args(args)

    if not isinstance(spec, dict):
        raise SpecError("search spec must be a JSON object")

    # v2 enhancement: allow compact query syntax inside spec[query] as well.
    query_text = spec.get("query")
    if isinstance(query_text, str) and maybe_contains_query_syntax(query_text):
        parsed = spec_from_compact_query(query_text)
        spec_without_query = dict(spec)
        spec_without_query["query"] = parsed.get("query", "")
        spec = merge_specs(parsed, spec_without_query)

    spec.setdefault("sort", "relevance")
    spec.setdefault("limit", 5)
    spec.setdefault("citation_mode", "none")
    spec.setdefault("return_fields", DEFAULT_FIELDS)
    spec.setdefault("filters", {})
    return spec


def spec_from_compact_args(args: argparse.Namespace) -> dict[str, Any]:
    spec = spec_from_compact_query(args.query or "")
    if args.limit is not None:
        spec["limit"] = args.limit
    if args.sort:
        spec["sort"] = args.sort
    if args.citation_mode:
        spec["citation_mode"] = args.citation_mode
    if args.include_raw_bib:
        spec["include_raw_bib"] = True
    if args.return_fields:
        spec["return_fields"] = [
            item.strip() for item in args.return_fields.split(",") if item.strip()
        ]
    return spec


def maybe_contains_query_syntax(text: str) -> bool:
    if re.search(r"\byear\s*(?:>=|<=|>|<|:|=)\s*\d{4}\b", text, flags=re.IGNORECASE):
        return True
    compact_markers = ["author:", "type:", "has:", "sort:", "limit:", "fields:", "cite:", "raw:"]
    lowered = text.lower()
    return any(marker in lowered for marker in compact_markers)


def merge_specs(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = json.loads(json.dumps(base, ensure_ascii=False))
    for key, value in override.items():
        if key == "filters" and isinstance(value, dict):
            target = merged.setdefault("filters", {})
            merge_filter_dict(target, value)
        elif key == "query" and isinstance(value, str):
            # Keep free-text query from override if explicitly provided.
            merged["query"] = value
        else:
            merged[key] = value
    return merged


def merge_filter_dict(target: dict[str, Any], update: dict[str, Any]) -> None:
    for key, value in update.items():
        if key in {"author_contains", "type_in", "exclude_type_in", "has", "exclude_has"}:
            existing = list(target.get(key, []) or [])
            for item in value or []:
                if item not in existing:
                    existing.append(item)
            target[key] = existing
        elif key == "field_contains":
            target.setdefault("field_contains", {})
            for field_name, needles in (value or {}).items():
                existing = list(target["field_contains"].get(field_name, []) or [])
                for needle in needles or []:
                    if needle not in existing:
                        existing.append(needle)
                target["field_contains"][field_name] = existing
        elif key == "field_excludes":
            target.setdefault("field_excludes", {})
            for field_name, needles in (value or {}).items():
                existing = list(target["field_excludes"].get(field_name, []) or [])
                for needle in needles or []:
                    if needle not in existing:
                        existing.append(needle)
                target["field_excludes"][field_name] = existing
        else:
            target[key] = value


def strip_outer_wrappers(value: str) -> str:
    text = value.strip()
    changed = True
    while changed and len(text) >= 2:
        changed = False
        if (
            text.startswith("{")
            and text.endswith("}")
            and is_balanced(text[1:-1], "{", "}")
            or text.startswith('"')
            and text.endswith('"')
            and is_balanced_quotes(text[1:-1])
        ):
            text = text[1:-1].strip()
            changed = True
    return text


def is_balanced(text: str, open_char: str, close_char: str) -> bool:
    depth = 0
    in_quotes = False
    escaped = False
    for char in text:
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == '"':
            in_quotes = not in_quotes
            continue
        if in_quotes:
            continue
        if char == open_char:
            depth += 1
        elif char == close_char:
            depth -= 1
            if depth < 0:
                return False
    return depth == 0 and not in_quotes


def is_balanced_quotes(text: str) -> bool:
    escaped = False
    in_quotes = False
    for char in text:
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == '"':
            in_quotes = not in_quotes
    return not in_quotes


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    text = str(value)
    text = strip_outer_wrappers(text)
    text = LATEX_ESCAPE_RE.sub(r"\1", text)
    text = text.replace("~", " ")
    text = re.sub(r"\\[a-zA-Z]+", " ", text)
    text = text.replace("{", " ").replace("}", " ")
    text = WHITESPACE_RE.sub(" ", text)
    return text.strip()


def tokenize(text: str) -> list[str]:
    lowered = normalize_text(text).lower()
    return TOKEN_RE.findall(lowered)


# -----------------------------
# Compact query parsing
# -----------------------------


def spec_from_compact_query(query_text: str) -> dict[str, Any]:
    tokens = shlex.split(query_text or "")
    free_terms: list[str] = []
    filters: dict[str, Any] = {}
    spec: dict[str, Any] = {
        "filters": filters,
        "sort": "relevance",
        "limit": 5,
        "citation_mode": "none",
        "return_fields": list(DEFAULT_FIELDS),
    }

    for token in tokens:
        parsed = parse_query_token(token)
        if parsed is None:
            free_terms.append(token)
            continue
        kind, payload = parsed
        if kind == "free":
            free_terms.append(payload)
        elif kind == "sort":
            spec["sort"] = payload
        elif kind == "limit":
            spec["limit"] = payload
        elif kind == "return_fields":
            spec["return_fields"] = payload
        elif kind == "citation_mode":
            spec["citation_mode"] = payload
        elif kind == "include_raw_bib":
            spec["include_raw_bib"] = payload
        elif kind == "filter":
            merge_filter_dict(filters, payload)
        else:
            raise SpecError(f"unhandled parsed token kind: {kind}")

    spec["query"] = " ".join(free_terms).strip()
    return spec


def parse_query_token(token: str) -> tuple[str, Any] | None:
    match = FIELD_OP_RE.match(token)
    if not match:
        return None

    neg = bool(match.group("neg"))
    field = canonical_field(match.group("field"))
    op = match.group("op")
    value = strip_quotes_if_needed(match.group("value"))

    if field == "year":
        return ("filter", parse_year_filter(op, value, neg))
    if field == "author":
        return ("filter", {"author_excludes": [value]} if neg else {"author_contains": [value]})
    if field == "type":
        values = split_csv_values(value)
        return ("filter", {"exclude_type_in" if neg else "type_in": values})
    if field == "has":
        values = split_csv_values(value)
        return ("filter", {"exclude_has" if neg else "has": values})
    if field == "sort":
        lowered = value.lower()
        if lowered not in {"relevance", "year_desc", "year_asc", "title"}:
            raise SpecError(f"unsupported sort mode: {value}")
        return ("sort", lowered)
    if field == "limit":
        return ("limit", int(value))
    if field == "fields":
        return ("return_fields", split_csv_values(value))
    if field == "cite":
        lowered = value.lower()
        if lowered not in {"none", "latex", "typst", "both"}:
            raise SpecError(f"unsupported citation mode: {value}")
        return ("citation_mode", lowered)
    if field == "raw":
        return ("include_raw_bib", parse_bool(value))

    # Generic field filter.
    target_field = field.lower()
    if op in {":", "="}:
        return (
            "filter",
            {
                "field_excludes" if neg else "field_contains": {
                    target_field: split_csv_values(value)
                }
            },
        )
    raise SpecError(f"operator {op} is only supported for year, limit, and built-in controls")


def canonical_field(field: str) -> str:
    lowered = field.lower().replace("-", "_")
    return FIELD_ALIASES.get(lowered, lowered)


def strip_quotes_if_needed(value: str) -> str:
    value = value.strip()
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    return value


def split_csv_values(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def parse_bool(value: str) -> bool:
    lowered = value.strip().lower()
    if lowered in {"1", "true", "yes", "y", "on"}:
        return True
    if lowered in {"0", "false", "no", "n", "off"}:
        return False
    raise SpecError(f"could not parse boolean value: {value}")


def parse_year_filter(op: str, value: str, neg: bool) -> dict[str, Any]:
    years = split_csv_values(value)
    if op in {":", "="}:
        if len(years) == 1:
            year = int(years[0])
            if neg:
                return {"exclude_years": [year]}
            return {"year_min": year, "year_max": year}
        parsed_years = [int(item) for item in years]
        if neg:
            return {"exclude_years": parsed_years}
        return {"years_in": parsed_years}
    if neg:
        raise SpecError("negated year comparisons like -year>=2024 are not supported")
    year = int(value)
    if op == ">=":
        return {"year_min": year}
    if op == ">":
        return {"year_min": year + 1}
    if op == "<=":
        return {"year_max": year}
    if op == "<":
        return {"year_max": year - 1}
    raise SpecError(f"unsupported year operator: {op}")


# -----------------------------
# Bib parsing
# -----------------------------


def split_top_level(text: str, delimiter: str = ",") -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    brace_depth = 0
    paren_depth = 0
    in_quotes = False
    escaped = False

    for char in text:
        if escaped:
            current.append(char)
            escaped = False
            continue
        if char == "\\":
            current.append(char)
            escaped = True
            continue
        if char == '"':
            current.append(char)
            in_quotes = not in_quotes
            continue
        if not in_quotes:
            if char == "{":
                brace_depth += 1
            elif char == "}":
                brace_depth = max(0, brace_depth - 1)
            elif char == "(":
                paren_depth += 1
            elif char == ")":
                paren_depth = max(0, paren_depth - 1)
            elif char == delimiter and brace_depth == 0 and paren_depth == 0:
                parts.append("".join(current).strip())
                current = []
                continue
        current.append(char)

    tail = "".join(current).strip()
    if tail:
        parts.append(tail)
    return parts


def parse_fields(body: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for chunk in split_top_level(body):
        if not chunk or "=" not in chunk:
            continue
        name, value = chunk.split("=", 1)
        fields[name.strip().lower()] = value.strip().rstrip(",")
    return fields


def parse_bib_entries(content: str) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    idx = 0
    length = len(content)

    while idx < length:
        at = content.find("@", idx)
        if at == -1:
            break
        type_match = re.match(r"@\s*([A-Za-z]+)\s*([\{\(])", content[at:])
        if not type_match:
            idx = at + 1
            continue
        entry_type = type_match.group(1).lower()
        opener = type_match.group(2)
        closer = "}" if opener == "{" else ")"
        start = at
        pos = at + type_match.end()
        depth = 1
        in_quotes = False
        escaped = False
        while pos < length and depth > 0:
            char = content[pos]
            if escaped:
                escaped = False
                pos += 1
                continue
            if char == "\\":
                escaped = True
                pos += 1
                continue
            if char == '"':
                in_quotes = not in_quotes
                pos += 1
                continue
            if not in_quotes:
                if char == opener:
                    depth += 1
                elif char == closer:
                    depth -= 1
            pos += 1

        raw_entry = content[start:pos].strip()
        inner = raw_entry[raw_entry.find(opener) + 1 : -1].strip()
        comma = None
        brace_depth = 0
        paren_depth = 0
        in_quotes = False
        escaped = False
        for offset, char in enumerate(inner):
            if escaped:
                escaped = False
                continue
            if char == "\\":
                escaped = True
                continue
            if char == '"':
                in_quotes = not in_quotes
                continue
            if in_quotes:
                continue
            if char == "{":
                brace_depth += 1
            elif char == "}":
                brace_depth = max(0, brace_depth - 1)
            elif char == "(":
                paren_depth += 1
            elif char == ")":
                paren_depth = max(0, paren_depth - 1)
            elif char == "," and brace_depth == 0 and paren_depth == 0:
                comma = offset
                break
        if comma is None:
            idx = pos
            continue
        key = inner[:comma].strip()
        body = inner[comma + 1 :].strip().rstrip(",")
        fields = parse_fields(body)
        entries.append(
            {
                "entry_type": entry_type,
                "key": key,
                "fields": fields,
                "raw_bib": raw_entry,
            }
        )
        idx = pos
    return entries


def entry_year(fields: dict[str, str]) -> int | None:
    year_text = normalize_text(fields.get("year", ""))
    match = re.search(r"\b(19|20)\d{2}\b", year_text)
    if match:
        return int(match.group(0))
    date_text = normalize_text(fields.get("date", ""))
    match = re.search(r"\b(19|20)\d{2}\b", date_text)
    if match:
        return int(match.group(0))
    return None


def derive_venue(fields: dict[str, str]) -> str:
    for candidate in ["journal", "booktitle", "publisher", "series", "school", "institution"]:
        if candidate in fields:
            return normalize_text(fields[candidate])
    return ""


def has_code(fields: dict[str, str]) -> bool:
    combined = " ".join(normalize_text(fields.get(name, "")) for name in CODE_HINT_FIELDS).lower()
    return any(term in combined for term in CODE_HINT_TERMS)


def has_pdf(fields: dict[str, str]) -> bool:
    values = [normalize_text(fields.get(name, "")) for name in PDF_FIELDS]
    for value in values:
        if not value:
            continue
        lowered = value.lower()
        if lowered.endswith(".pdf") or ".pdf" in lowered:
            return True
        # Zotero file field format: "Author - Year - Title.pdf:/path/file.pdf:application/pdf"
        # Check for PDF MIME type instead of naive "zotero" substring match
        if "application/pdf" in lowered:
            return True
    return False


def get_flag(entry: dict[str, Any], name: str) -> bool:
    fields = entry["fields"]
    normalized = canonical_field(name)
    if normalized == "doi":
        return bool(normalize_text(fields.get("doi", "")))
    if normalized == "abstract":
        return bool(normalize_text(fields.get("abstract", "")))
    if normalized == "keywords":
        return bool(normalize_text(fields.get("keywords", "")))
    if normalized == "annotation":
        return bool(normalize_text(fields.get("annotation", "")))
    if normalized == "shorttitle":
        return bool(normalize_text(fields.get("shorttitle", "")))
    if normalized == "eprint":
        return bool(
            normalize_text(fields.get("eprint", ""))
            or normalize_text(fields.get("archiveprefix", ""))
        )
    if normalized == "pdf":
        return has_pdf(fields)
    if normalized == "code":
        return has_code(fields)
    return bool(normalize_text(fields.get(normalized, "")))


def build_entry(raw_entry: dict[str, Any]) -> dict[str, Any]:
    fields = raw_entry["fields"]
    entry = {
        "entry_type": raw_entry["entry_type"],
        "key": raw_entry["key"],
        "raw_bib": raw_entry["raw_bib"],
        "title": normalize_text(fields.get("title", "")),
        "shorttitle": normalize_text(fields.get("shorttitle", "")),
        "author": normalize_text(fields.get("author", "")),
        "year": entry_year(fields),
        "venue": derive_venue(fields),
        "doi": normalize_text(fields.get("doi", "")),
        "eprint": normalize_text(fields.get("eprint", "")),
        "keywords": normalize_text(fields.get("keywords", "")),
        "annotation": normalize_text(fields.get("annotation", "")),
        "abstract": normalize_text(fields.get("abstract", "")),
        "fields": {name: normalize_text(value) for name, value in fields.items()},
    }
    entry["flags"] = {
        "doi": get_flag(entry, "doi"),
        "abstract": get_flag(entry, "abstract"),
        "keywords": get_flag(entry, "keywords"),
        "annotation": get_flag(entry, "annotation"),
        "shorttitle": get_flag(entry, "shorttitle"),
        "eprint": get_flag(entry, "eprint"),
        "pdf": has_pdf(fields),
        "code": has_code(fields),
    }
    entry["search_blob"] = " ".join(
        [
            entry["title"],
            entry["shorttitle"],
            entry["author"],
            entry["venue"],
            entry["doi"],
            entry["eprint"],
            entry["keywords"],
            entry["annotation"],
            entry["abstract"],
            entry["raw_bib"],
        ]
    )
    return entry


# -----------------------------
# Search, filtering, and output
# -----------------------------


def match_filters(entry: dict[str, Any], filters: dict[str, Any]) -> bool:
    if not filters:
        return True

    year = entry.get("year")
    year_min = filters.get("year_min")
    year_max = filters.get("year_max")
    years_in = {int(item) for item in (filters.get("years_in") or [])}
    exclude_years = {int(item) for item in (filters.get("exclude_years") or [])}

    if year_min is not None and (year is None or year < int(year_min)):
        return False
    if year_max is not None and (year is None or year > int(year_max)):
        return False
    if years_in and year not in years_in:
        return False
    if exclude_years and year in exclude_years:
        return False

    for needle in filters.get("author_contains", []) or []:
        if str(needle).lower() not in entry.get("author", "").lower():
            return False
    for needle in filters.get("author_excludes", []) or []:
        if str(needle).lower() in entry.get("author", "").lower():
            return False

    type_in = [str(item).lower() for item in (filters.get("type_in", []) or [])]
    if type_in and entry.get("entry_type", "").lower() not in type_in:
        return False
    exclude_type_in = [str(item).lower() for item in (filters.get("exclude_type_in", []) or [])]
    if exclude_type_in and entry.get("entry_type", "").lower() in exclude_type_in:
        return False

    for flag in filters.get("has", []) or []:
        if not get_flag(entry, str(flag)):
            return False
    for flag in filters.get("exclude_has", []) or []:
        if get_flag(entry, str(flag)):
            return False

    field_contains = filters.get("field_contains", {}) or {}
    for field_name, needles in field_contains.items():
        haystack = entry["fields"].get(field_name.lower(), entry.get(field_name.lower(), ""))
        if not haystack:
            return False
        for needle in needles:
            if str(needle).lower() not in haystack.lower():
                return False

    field_excludes = filters.get("field_excludes", {}) or {}
    for field_name, needles in field_excludes.items():
        haystack = entry["fields"].get(field_name.lower(), entry.get(field_name.lower(), ""))
        for needle in needles:
            if haystack and str(needle).lower() in haystack.lower():
                return False

    return True


def score_entry(entry: dict[str, Any], query: str) -> float:
    query = normalize_text(query)
    if not query:
        return 0.0
    query_lower = query.lower()
    tokens = tokenize(query)
    if not tokens:
        return 0.0

    score = 0.0
    field_token_cache: dict[str, Counter] = {}

    for field, weight in WEIGHTED_FIELDS:
        field_text = entry.get(field, "") if field != "raw_bib" else entry.get("raw_bib", "")
        normalized = normalize_text(field_text).lower()
        if not normalized:
            continue
        if query_lower in normalized:
            # Phrase-match bonus: scales with query length (2.0–6.0x weight)
            score += weight * max(2.0, min(6.0, len(tokens) / 2 + 1))
        counter = field_token_cache.setdefault(field, Counter(tokenize(normalized)))
        for token in tokens:
            if token in counter:
                score += weight * min(counter[token], 3)
            elif len(token) >= 4 and token in normalized:
                score += weight * 0.6

    title = entry.get("title", "").lower()
    shorttitle = entry.get("shorttitle", "").lower()
    if title.startswith(query_lower) or shorttitle.startswith(query_lower):
        # Strong bonus when the query matches the beginning of the title
        score += 8.0
    if entry.get("year"):
        # Mild recency bias: newer papers score slightly higher (e.g. 2024 -> +0.72)
        score += max(0.0, (entry["year"] - 2000) * 0.03)
    return round(score, 4)


def typst_citations(key: str) -> dict[str, Any]:
    simple = bool(re.fullmatch(r"[A-Za-z0-9_-]+", key))
    if simple:
        return {
            "inline": f"@{key}",
            "cite": f"#cite(<{key}>)",
            "needs_label": False,
        }
    escaped = key.replace('"', '\\"')
    return {
        "inline": None,
        "cite": f'#cite(label("{escaped}"))',
        "needs_label": True,
    }


def latex_citations(key: str) -> dict[str, str]:
    return {
        "cite": f"\\cite{{{key}}}",
        "parencite": f"\\parencite{{{key}}}",
        "textcite": f"\\textcite{{{key}}}",
    }


def format_result(entry: dict[str, Any], spec: dict[str, Any], score: float) -> dict[str, Any]:
    return_fields = spec.get("return_fields") or DEFAULT_FIELDS
    result: dict[str, Any] = {
        field: entry.get(field) if field in entry else entry["fields"].get(field.lower())
        for field in return_fields
    }
    result["entry_type"] = entry.get("entry_type")
    result["score"] = score
    result["flags"] = entry.get("flags", {})
    citation_mode = (spec.get("citation_mode") or "none").lower()
    citations: dict[str, Any] = {}
    if citation_mode in {"latex", "both"}:
        citations["latex"] = latex_citations(entry["key"])
    if citation_mode in {"typst", "both"}:
        citations["typst"] = typst_citations(entry["key"])
    if citations:
        result["citations"] = citations
    if spec.get("include_raw_bib"):
        result["raw_bib"] = entry["raw_bib"]
    return result


def sort_results(
    scored: Sequence[tuple[float, dict[str, Any]]], sort_mode: str
) -> list[tuple[float, dict[str, Any]]]:
    if sort_mode == "year_asc":
        return sorted(
            scored,
            key=lambda item: (
                (item[1].get("year") is None),
                item[1].get("year") or 0,
                item[1].get("title") or "",
            ),
        )
    if sort_mode == "year_desc":
        # Use -1 as sentinel so entries with no year sort last in descending order
        return sorted(
            scored,
            key=lambda item: (item[1].get("year") or -1, item[0], item[1].get("title") or ""),
            reverse=True,
        )
    if sort_mode == "title":
        return sorted(
            scored,
            key=lambda item: ((item[1].get("title") or "").lower(), -(item[1].get("year") or 0)),
        )
    return sorted(
        scored,
        key=lambda item: (item[0], item[1].get("year") or -1, item[1].get("title") or ""),
        reverse=True,
    )


def run_search(entries: Sequence[dict[str, Any]], spec: dict[str, Any]) -> dict[str, Any]:
    query = spec.get("query", "") or ""
    filters = spec.get("filters", {}) or {}
    sort_mode = (spec.get("sort") or "relevance").lower()
    limit = int(spec.get("limit", 5) or 5)

    filtered: list[dict[str, Any]] = [entry for entry in entries if match_filters(entry, filters)]
    scored: list[tuple[float, dict[str, Any]]] = [
        (score_entry(entry, query), entry) for entry in filtered
    ]
    if query:
        scored = [item for item in scored if item[0] > 0]
    ordered = sort_results(scored, sort_mode)
    selected = ordered[:limit]

    return {
        "meta": {
            "query": query,
            "sort": sort_mode,
            "limit": limit,
            "total_entries": len(entries),
            "matched_entries": len(filtered),
            "returned_entries": len(selected),
            "applied_filters": filters,
        },
        "results": [format_result(entry, spec, score) for score, entry in selected],
    }


def main() -> None:
    args = parse_args()
    try:
        spec = load_spec(args)
    except (json.JSONDecodeError, SpecError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        raise SystemExit(2) from exc

    bib_path = Path(args.bib)
    content = bib_path.read_text(encoding="utf-8")
    raw_entries = parse_bib_entries(content)
    entries = [build_entry(item) for item in raw_entries]
    output = run_search(entries, spec)
    json.dump(output, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
