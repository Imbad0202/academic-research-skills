#!/usr/bin/env python3
"""
BibTeX Verification Script - Check bibliography integrity
Includes static checks and online verification preparation.

Usage:
    uv run python verify_bib.py references.bib
    uv run python verify_bib.py references.bib --standard gb7714
    uv run python verify_bib.py references.bib --online-check
"""

import argparse
import json
import re
import sys
from pathlib import Path


class BibTeXVerifier:
    """Verify BibTeX file integrity and completeness."""

    REQUIRED_FIELDS = {
        "article": ["author", "title", "journal", "year"],
        "inproceedings": ["author", "title", "booktitle", "year"],
        "book": ["author", "title", "publisher", "year"],
    }

    GB7714_RECOMMENDED = ["doi", "url", "urldate"]

    def __init__(
        self,
        bib_file: str,
        standard: str = "default",
        online: bool = False,
        email: str | None = None,
        online_timeout: float = 10.0,
    ):
        self.bib_file = Path(bib_file).resolve()
        self.standard = standard
        self.entries = []
        self.issues = []
        self.online = online
        self.email = email
        self.online_timeout = online_timeout

    def parse(self) -> list[dict]:
        """Parse BibTeX file."""
        try:
            content = self.bib_file.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            self.issues.append({"type": "file_error", "message": str(e)})
            return []

        entries = []
        # Robust regex for entries
        entry_pattern = r"@(\w+)\s*{\s*([^,]+)\s*,([^@]*?)(?=\n\s*@|\Z)"

        for match in re.finditer(entry_pattern, content, re.DOTALL):
            entries.append(
                {
                    "type": match.group(1).lower(),
                    "key": match.group(2).strip(),
                    "fields": self._parse_fields(match.group(3)),
                    "raw": match.group(0),
                }
            )

        self.entries = entries
        return entries

    def _parse_fields(self, fields_str: str) -> dict[str, str]:
        fields = {}
        # Parse field = {value} or "value" or number
        field_pattern = r'(\w+)\s*=\s*(?:\{([^^{}]*(?:\{[^{}]*\}[^{}]*)*)\}|"([^"]*)"|(\d+))'
        for match in re.finditer(field_pattern, fields_str):
            name = match.group(1).lower()
            val = match.group(2) or match.group(3) or match.group(4) or ""
            fields[name] = val.strip()
        return fields

    def verify(self) -> dict:
        if not self.entries:
            self.parse()

        results = {
            "total_entries": len(self.entries),
            "valid_entries": 0,
            "issues": [],
            "status": "PASS",
            "needs_online_check": [],
        }

        for entry in self.entries:
            entry_issues = self._verify_entry(entry)

            # Check for missing identifiers (DOI/URL)
            if "doi" not in entry["fields"] and "url" not in entry["fields"]:
                results["needs_online_check"].append(
                    {
                        "key": entry["key"],
                        "title": entry["fields"].get("title", "Unknown Title"),
                        "author": entry["fields"].get("author", "Unknown Author"),
                    }
                )

            if entry_issues:
                results["issues"].extend(entry_issues)
            else:
                results["valid_entries"] += 1

        if results["issues"]:
            has_errors = any(i["severity"] == "error" for i in results["issues"])
            results["status"] = "FAIL" if has_errors else "WARNING"

        # Online verification (when --online and online_bib_verify is available)
        if self.online:
            try:
                from online_bib_verify import OnlineBibVerifier

                online_verifier = OnlineBibVerifier(
                    polite_email=self.email,
                    timeout=self.online_timeout,
                )
                for entry_info in results["needs_online_check"]:
                    entry_dict = {
                        "key": entry_info["key"],
                        "title": entry_info.get("title", ""),
                        "author": entry_info.get("author", ""),
                    }
                    for entry in self.entries:
                        if entry["key"] == entry_info["key"]:
                            entry_dict.update(entry["fields"])
                            break
                    result = online_verifier.verify_entry(entry_dict)
                    if result.status == "mismatch":
                        for m in result.mismatches:
                            results["issues"].append(
                                {
                                    "key": result.bib_key,
                                    "type": "metadata_mismatch",
                                    "severity": "error",
                                    "message": f"Online verification mismatch: {m}",
                                }
                            )
                    elif result.status == "not_found":
                        results["issues"].append(
                            {
                                "key": result.bib_key,
                                "type": "not_found_online",
                                "severity": "warning",
                                "message": "Entry not found in online databases",
                            }
                        )
                    elif result.status == "verified" and result.suggested_doi:
                        results["issues"].append(
                            {
                                "key": result.bib_key,
                                "type": "doi_suggestion",
                                "severity": "warning",
                                "message": f"Consider adding DOI: {result.suggested_doi}",
                            }
                        )
            except ImportError:
                print("# Warning: online_bib_verify.py not found, skipping online verification")

        return results

    def _verify_entry(self, entry: dict) -> list[dict]:
        issues = []
        entry_type = entry["type"]
        entry_key = entry["key"]
        fields = entry["fields"]

        if entry_type in self.REQUIRED_FIELDS:
            for field in self.REQUIRED_FIELDS[entry_type]:
                if field not in fields or not fields[field]:
                    if field == "author" and "editor" in fields:
                        continue
                    issues.append(
                        {
                            "key": entry_key,
                            "type": "missing_field",
                            "field": field,
                            "severity": "error",
                            "message": f"Missing required field '{field}'",
                        }
                    )

        # Title case check (simplified)
        if (
            "title" in fields
            and re.search(r"\b[A-Z]{2,}\b", fields["title"])
            and "{" not in fields["title"]
        ):
            issues.append(
                {
                    "key": entry_key,
                    "type": "caps",
                    "severity": "warning",
                    "message": "Unprotected uppercase in title",
                }
            )

        return issues

    def generate_report(self, result: dict) -> str:
        lines = []
        lines.append(f"BibTeX Check: {self.bib_file}")
        lines.append(f"Status: {result['status']}")

        if result["issues"]:
            lines.append("\nIssues:")
            for issue in result["issues"]:
                lines.append(f"  [{issue['severity'].upper()}] @{issue['key']}: {issue['message']}")

        if result["needs_online_check"]:
            lines.append(
                f"\n[INFO] {len(result['needs_online_check'])} entries missing DOI/URL (Use --online-check to export list)"
            )

        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="BibTeX Verification")
    parser.add_argument("bib_file", help=".bib file")
    parser.add_argument("--standard", choices=["default", "gb7714"], default="default")
    parser.add_argument(
        "--online-check", action="store_true", help="Generate list for online verification"
    )
    parser.add_argument(
        "--online",
        action="store_true",
        help="Enable online verification via CrossRef/Semantic Scholar",
    )
    parser.add_argument("--email", help="Email for CrossRef polite pool (faster rate limits)")
    parser.add_argument(
        "--online-timeout",
        type=float,
        default=10.0,
        help="Timeout per API request in seconds",
    )
    parser.add_argument("--output", help="Output file for online check JSON")

    args = parser.parse_args()

    if not Path(args.bib_file).exists():
        print("File not found.")
        sys.exit(1)

    verifier = BibTeXVerifier(
        args.bib_file,
        args.standard,
        online=getattr(args, "online", False),
        email=getattr(args, "email", None),
        online_timeout=getattr(args, "online_timeout", 10.0),
    )
    result = verifier.verify()

    if args.online_check:
        output_file = args.output or "verification_needed.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result["needs_online_check"], f, indent=2, ensure_ascii=False)
        print(f"Exported {len(result['needs_online_check'])} entries to {output_file}")
        print("Agent instructions: Use 'google_web_search' for these titles to find DOIs.")
    else:
        print(verifier.generate_report(result))

    if result["status"] == "FAIL":
        sys.exit(1)


if __name__ == "__main__":
    main()
