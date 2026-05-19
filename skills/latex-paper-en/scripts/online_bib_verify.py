#!/usr/bin/env python3
"""
Online bibliography verification via CrossRef and Semantic Scholar APIs.

Verifies bibliography entries against online databases to detect:
- Invalid DOIs
- Metadata mismatches (year, journal)
- Missing DOIs (suggests from title search)

Usage:
    # As a module (imported by verify_bib.py):
    from online_bib_verify import OnlineBibVerifier
    verifier = OnlineBibVerifier()
    result = verifier.verify_entry({"key": "smith2020", "doi": "10.1234/example", "title": "..."})

    # Standalone CLI:
    uv run python -B online_bib_verify.py --bib references.bib [--email user@example.com] [--json]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


@dataclass
class VerifyResult:
    """Result of a single DOI verification."""

    valid: bool
    metadata: dict | None = None
    error: str | None = None


@dataclass
class EntryVerifyResult:
    """Result of verifying a single bibliography entry."""

    status: str  # "verified" | "mismatch" | "not_found" | "unverifiable" | "error"
    bib_key: str = ""
    mismatches: list[str] = field(default_factory=list)
    suggested_doi: str | None = None
    confidence: float = 0.0


class OnlineBibVerifier:
    """Verify bibliography entries via CrossRef and Semantic Scholar APIs."""

    def __init__(
        self,
        polite_email: str | None = None,
        timeout: float = 10.0,
        rate_limit: float = 0.5,
    ) -> None:
        self.email = polite_email
        self.timeout = timeout
        self.rate_limit = rate_limit  # Minimum seconds between requests
        self._last_request_time = 0.0

    def _get(self, url: str, params: dict | None = None) -> dict | None:
        """HTTP GET with rate limiting and error handling."""
        # Rate limiting
        elapsed = time.time() - self._last_request_time
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)

        if params:
            query_string = "&".join(f"{k}={quote(str(v))}" for k, v in params.items())
            url = f"{url}?{query_string}"

        headers = {"User-Agent": "AcademicWritingSkills/1.0"}
        if self.email:
            headers["User-Agent"] += f" (mailto:{self.email})"

        req = Request(url, headers=headers)
        try:
            with urlopen(req, timeout=self.timeout) as resp:
                self._last_request_time = time.time()
                return json.loads(resp.read().decode())
        except (HTTPError, URLError, json.JSONDecodeError, TimeoutError, OSError):
            return None

    def verify_doi(self, doi: str) -> VerifyResult:
        """Verify a DOI via CrossRef API."""
        clean_doi = doi.strip()
        data = self._get(f"https://api.crossref.org/works/{quote(clean_doi, safe='')}")
        if data is None:
            return VerifyResult(valid=False, error="DOI not found or API error")

        msg = data.get("message", {})
        title_list = msg.get("title") or [None]
        author_list = msg.get("author", [])
        published = msg.get("published-print") or msg.get("published-online") or {}
        date_parts = published.get("date-parts", [[None]])
        year_val = date_parts[0][0] if date_parts and date_parts[0] else None
        container = msg.get("container-title") or [None]

        return VerifyResult(
            valid=True,
            metadata={
                "title": title_list[0],
                "authors": [a.get("family", "") for a in author_list],
                "year": str(year_val or ""),
                "journal": container[0],
                "doi": clean_doi,
            },
        )

    def search_by_title(self, title: str) -> list[dict]:
        """Search for a paper by title via Semantic Scholar API."""
        clean_title = re.sub(r"[{}\\]", "", title).strip()
        if not clean_title:
            return []
        data = self._get(
            "https://api.semanticscholar.org/graph/v1/paper/search",
            {
                "query": clean_title,
                "limit": "3",
                "fields": "title,authors,year,externalIds,venue",
            },
        )
        if data is None or "data" not in data:
            return []
        return data["data"]

    def verify_entry(self, entry: dict) -> EntryVerifyResult:
        """
        Verify a single bibliography entry.

        Strategy: DOI verification first, fallback to title search.

        Args:
            entry: Dict with keys like "key", "doi", "title", "year", "journal".
        """
        bib_key = entry.get("key", "")

        # 1. DOI verification (preferred)
        doi = entry.get("doi", "").strip()
        if doi:
            result = self.verify_doi(doi)
            if result.valid and result.metadata:
                return self._cross_check(bib_key, entry, result.metadata)
            if not result.valid:
                return EntryVerifyResult(
                    status="not_found",
                    bib_key=bib_key,
                    mismatches=[f"DOI '{doi}' not found in CrossRef"],
                )

        # 2. Title search fallback
        title = entry.get("title", "").strip()
        if title:
            results = self.search_by_title(title)
            if results:
                return self._match_title(bib_key, entry, results)

        return EntryVerifyResult(status="unverifiable", bib_key=bib_key)

    def _cross_check(
        self,
        bib_key: str,
        entry: dict,
        api_meta: dict,
    ) -> EntryVerifyResult:
        """Compare bib entry metadata against API-returned metadata."""
        mismatches = []

        # Year comparison
        bib_year = str(entry.get("year", "")).strip()
        api_year = str(api_meta.get("year", "")).strip()
        if bib_year and api_year and bib_year != api_year:
            mismatches.append(f"year: bib='{bib_year}' vs api='{api_year}'")

        # Journal comparison (fuzzy)
        bib_journal = entry.get("journal", "").lower().strip()
        api_journal = (api_meta.get("journal") or "").lower().strip()
        if (
            bib_journal
            and api_journal
            and bib_journal not in api_journal
            and api_journal not in bib_journal
        ):
            mismatches.append(
                f"journal: bib='{entry.get('journal')}' vs api='{api_meta.get('journal')}'"
            )

        if mismatches:
            return EntryVerifyResult(
                status="mismatch",
                bib_key=bib_key,
                mismatches=mismatches,
                confidence=0.7,
            )
        return EntryVerifyResult(
            status="verified",
            bib_key=bib_key,
            confidence=0.9,
        )

    def _match_title(
        self,
        bib_key: str,
        entry: dict,
        results: list[dict],
    ) -> EntryVerifyResult:
        """Match bib entry against title search results."""
        bib_title = re.sub(r"[{}\\]", "", entry.get("title", "")).lower().strip()
        for paper in results:
            api_title = (paper.get("title") or "").lower().strip()
            if not api_title:
                continue
            # Simple containment similarity
            if bib_title in api_title or api_title in bib_title:
                doi = (paper.get("externalIds") or {}).get("DOI")
                return EntryVerifyResult(
                    status="verified",
                    bib_key=bib_key,
                    suggested_doi=doi,
                    confidence=0.8,
                )
        return EntryVerifyResult(status="not_found", bib_key=bib_key)


def _parse_bib_entries(bib_path: Path) -> list[dict]:
    """Parse BibTeX file into entry dicts (minimal parser for standalone use)."""
    content = bib_path.read_text(encoding="utf-8", errors="ignore")
    entries = []
    entry_pattern = r"@(\w+)\s*{\s*([^,]+)\s*,([^@]*?)(?=\n\s*@|\Z)"
    field_pattern = r'(\w+)\s*=\s*(?:\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}|"([^"]*)"|(\d+))'

    for match in re.finditer(entry_pattern, content, re.DOTALL):
        entry_type = match.group(1).lower().strip()
        key = match.group(2).strip()
        fields_str = match.group(3)

        fields: dict[str, str] = {}
        for field_match in re.finditer(field_pattern, fields_str):
            name = field_match.group(1).lower()
            val = field_match.group(2) or field_match.group(3) or field_match.group(4) or ""
            fields[name] = val.strip()

        entries.append(
            {
                "key": key,
                "type": entry_type,
                **fields,
            }
        )

    return entries


def main() -> int:
    """CLI entry point for standalone bibliography verification."""
    parser = argparse.ArgumentParser(
        description="Online Bibliography Verification via CrossRef & Semantic Scholar",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  uv run python -B online_bib_verify.py --bib references.bib
  uv run python -B online_bib_verify.py --bib references.bib --email user@example.com
  uv run python -B online_bib_verify.py --bib references.bib --json
        """,
    )
    parser.add_argument("--bib", required=True, help="BibTeX file to verify")
    parser.add_argument(
        "--email",
        help="Email for CrossRef polite pool (faster rate limits)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="Timeout per API request in seconds (default: 10)",
    )
    parser.add_argument("--json", action="store_true", help="Output JSON format")

    args = parser.parse_args()

    bib_path = Path(args.bib)
    if not bib_path.exists():
        print(f"[ERROR] File not found: {args.bib}", file=sys.stderr)
        return 1

    entries = _parse_bib_entries(bib_path)
    if not entries:
        print("# No entries found in BibTeX file.")
        return 0

    verifier = OnlineBibVerifier(
        polite_email=args.email,
        timeout=args.timeout,
    )

    results = []
    for entry in entries:
        result = verifier.verify_entry(entry)
        results.append(result)
        if not args.json:
            _print_result(result)

    if args.json:
        json_results = [
            {
                "bib_key": r.bib_key,
                "status": r.status,
                "mismatches": r.mismatches,
                "suggested_doi": r.suggested_doi,
                "confidence": r.confidence,
            }
            for r in results
        ]
        print(json.dumps(json_results, indent=2, ensure_ascii=False))

    # Summary
    verified = sum(1 for r in results if r.status == "verified")
    mismatched = sum(1 for r in results if r.status == "mismatch")
    not_found = sum(1 for r in results if r.status == "not_found")
    if not args.json:
        print(f"\n# Summary: {verified} verified, {mismatched} mismatched, {not_found} not found")

    return 1 if mismatched > 0 else 0


def _print_result(result: EntryVerifyResult) -> None:
    """Print a single verification result in protocol format."""
    if result.status == "verified":
        msg = f"Entry '{result.bib_key}' verified online (confidence: {result.confidence:.0%})"
        if result.suggested_doi:
            msg += f" — suggested DOI: {result.suggested_doi}"
        print(f"# ONLINE_BIB [Severity: Minor] [Priority: P2]: {msg}")
    elif result.status == "mismatch":
        for m in result.mismatches:
            print(
                f"% ONLINE_BIB [Severity: Major] [Priority: P1]: "
                f"Metadata mismatch for '{result.bib_key}': {m}"
            )
    elif result.status == "not_found":
        detail = (
            result.mismatches[0] if result.mismatches else "Entry not found in online databases"
        )
        print(f"% ONLINE_BIB [Severity: Minor] [Priority: P2]: '{result.bib_key}': {detail}")


if __name__ == "__main__":
    sys.exit(main())
