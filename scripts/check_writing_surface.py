#!/usr/bin/env python3
"""Offline English writing-surface estimates (#830); advisory, never a gate.

No model, network, rewriting, authorship inference or quality classification.
See shared/references/writing_surface/README.md for formulas and limitations.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
import re
import statistics
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VOCABULARY = ROOT / "shared/references/writing_surface/vocabulary.json"
ENFORCEMENT = "Advisory only: never blocks a handoff, changes a decision, or authorises rewriting."
WORD = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)*", re.UNICODE)
METRICS = (
    ("ADV-WS-1", "flesch_reading_ease_estimate"),
    ("ADV-WS-2", "flesch_kincaid_grade_estimate"),
    ("ADV-WS-3", "fog_estimate"),
    ("ADV-WS-4", "smog_estimate"),
    ("ADV-WS-5", "nominalization_token_share_heuristic"),
    ("ADV-WS-6", "passive_sentence_share_heuristic"),
    ("ADV-WS-7", "hedge_hits_per_1000_words"),
    ("ADV-WS-8", "sentence_length_population_sd"),
    ("ADV-WS-9", "flagged_term_hits_per_1000_words"),
)


def load_vocabulary(path: Path = VOCABULARY) -> dict:
    vocab = json.loads(path.read_text(encoding="utf-8"))
    lists = ("sources", "nominalization_suffixes", "hedges", "flagged_terms",
             "passive_auxiliaries", "irregular_participles", "abbreviations")
    if not isinstance(vocab, dict) or (type(vocab.get("version")) is not int or vocab["version"] != 1):
        raise ValueError("unsupported vocabulary")
    for key in lists:
        values = vocab.get(key)
        if not isinstance(values, list) or not values or any(
            not isinstance(v, str) or not v.strip() for v in values
        ) or len(set(values)) != len(values):
            raise ValueError("invalid vocabulary list")
    exceptions = vocab.get("syllable_exceptions")
    if not isinstance(exceptions, dict) or any(
        not isinstance(k, str) or type(v) is not int or v < 1 for k, v in exceptions.items()
    ):
        raise ValueError("invalid syllable exceptions")
    return vocab


def latin_words(text: str) -> tuple[list[str], int]:
    tokens = WORD.findall(text)
    words = [t.lower().replace("’", "'") for t in tokens if all(
        c in "'’" or "LATIN" in unicodedata.name(c, "") for c in t
    )]
    return words, len(tokens) - len(words)


def syllables(word: str, vocab: dict) -> int:
    word = "".join(c for c in unicodedata.normalize("NFKD", word)
                   if "a" <= c <= "z")
    if word in vocab["syllable_exceptions"]:
        return vocab["syllable_exceptions"][word]
    count = len(re.findall(r"[aeiouy]+", word))
    if word.endswith("e") and not word.endswith(("le", "ye")) and count > 1:
        count -= 1
    if word.endswith("ed") and not word.endswith(("ted", "ded")) and count > 1:
        count -= 1
    return max(1, count)


def sentences(text: str, vocab: dict) -> list[str]:
    # Protect decimal points, initialisms and a finite documented abbreviation roster.
    for abbreviation in sorted(vocab["abbreviations"], key=len, reverse=True):
        text = re.sub(re.escape(abbreviation), lambda m: m[0].replace(".", "\x00"),
                      text, flags=re.I)
    text = re.sub(r"\b(?:[A-Za-z]\.){2,}", lambda m: m[0].replace(".", "\x00"), text)
    text = re.sub(r"(?<=\d)\.(?=\d)", "\x00", text)
    return [part.replace("\x00", ".").strip() for part in re.split(
        r"[.!?]+(?:[\"'’”)]*)\s+|[.!?]+$|\n\s*\n", text
    ) if latin_words(part)[0]]


def prose_sections(text: str) -> list[dict]:
    """Conservative Markdown/plain-text extraction; each text line belongs once."""
    text = re.sub(r"\A\ufeff?---[^\S\n]*\n.*?\n(?:---|\.\.\.)[^\S\n]*(?:\n|$)", lambda m: "\n" * m[0].count("\n"), text, flags=re.S)
    text = re.sub(r"<!--.*?(?:-->|\Z)", lambda m: "\n" * m[0].count("\n"), text, flags=re.S)
    sections = [{"title": "Preamble", "line": 1, "text": []}]
    fence = None
    reference_level = None
    display_math = None
    for number, line in enumerate(text.splitlines(), 1):
        match = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if fence:
            if re.match(r"^\s{0,3}" + re.escape(fence[0]) + "{" + str(fence[1]) + r",}\s*$", line):
                fence = None
            continue
        if match:
            fence = (match[1][0], len(match[1]))
            continue
        if line.strip().startswith(("$$", r"\[")):
            delimiter = "$$" if line.strip().startswith("$$") else r"\]"
            if display_math:
                display_math = None
            elif not line.strip().endswith(delimiter) or line.strip() == "$$":
                display_math = delimiter
            continue
        if display_math:
            if display_math in line:
                display_math = None
            continue
        heading = re.match(r"^\s{0,3}(#{1,6})\s+(.+?)\s*#*\s*$", line)
        if heading:
            level, title = len(heading[1]), heading[2]
            if reference_level is not None and level > reference_level:
                continue
            reference_level = level if title.casefold() in {"references", "bibliography", "works cited"} else None
            if reference_level is None:
                sections.append({"title": title, "line": number, "text": []})
            continue
        if reference_level is not None or "|" in line or re.match(r"^\s*\[[^]]+\]:", line):
            continue
        line = re.sub(r"(`+).*?\1", " ", line)
        line = re.sub(r"(?<!\\)\$[^$\n]+\$", " ", line)
        line = re.sub(r"!\[[^]]*\]\([^)]*\)", " ", line)
        line = re.sub(r"\[([^]]+)\]\([^)]*\)", r"\1", line)
        line = re.sub(r"https?://\S+|<[^>]+>|\\(?:cite\w*|ref|label)\{[^}]*\}", " ", line)
        line = re.sub(r"^\s*(?:>\s*|[-*+]\s+|\d+[.)]\s+)", "", line)
        sections[-1]["text"].append(line)
    return [{**s, "text": "\n".join(s["text"])} for s in sections]


def phrase_hits(words: list[str], phrases: list[str]) -> int:
    """Longest non-overlapping matches; a multiword hedge counts once."""
    choices = sorted((tuple(WORD.findall(p.lower())) for p in phrases), key=lambda p: (-len(p), p))
    hits, offset = 0, 0
    while offset < len(words):
        found = next((p for p in choices if tuple(words[offset:offset + len(p)]) == p), None)
        offset += len(found) if found else 1
        hits += int(found is not None)
    return hits


def readability(words: int, sentence_count: int, syllable_count: int, polysyllables: int) -> dict:
    if not words or not sentence_count:
        return {key: None for _, key in METRICS[:4]}
    length, density = words / sentence_count, syllable_count / words
    return dict(zip((key for _, key in METRICS[:4]), (
        206.835 - 1.015 * length - 84.6 * density,
        0.39 * length + 11.8 * density - 15.59,
        0.4 * (length + 100 * polysyllables / words),
        1.043 * math.sqrt(30 * polysyllables / sentence_count) + 3.1291 if sentence_count >= 30 else None,
    )))


def measure(text: str, vocab: dict) -> dict:
    words, unsupported = latin_words(text)
    spans = sentences(text, vocab)
    lengths = [len(latin_words(s)[0]) for s in spans]
    counts = [syllables(w, vocab) for w in words]
    passive = 0
    for span in spans:
        tokens, _ = latin_words(span)
        for i, token in enumerate(tokens):
            if token not in vocab["passive_auxiliaries"]:
                continue
            j = i + 1
            while j < min(i + 4, len(tokens)) and (tokens[j].endswith("ly") or tokens[j] == "not"):
                j += 1
            if j < len(tokens) and (tokens[j] in vocab["irregular_participles"] or
                    (len(tokens[j]) > 3 and tokens[j].endswith(("ed", "en")))):
                passive += 1
                break
    nominal = sum(any(len(w) > len(s) + 2 and w.endswith(s)
                      for s in vocab["nominalization_suffixes"]) for w in words)
    metrics = readability(len(words), len(spans), sum(counts), sum(n >= 3 for n in counts))
    metrics.update({
        "nominalization_token_share_heuristic": nominal / len(words) if words else None,
        "passive_sentence_share_heuristic": passive / len(spans) if spans else None,
        "hedge_hits_per_1000_words": 1000 * sum(phrase_hits(latin_words(span)[0], vocab["hedges"]) for span in spans) / len(words) if words else None,
        "sentence_length_population_sd": statistics.pstdev(lengths) if lengths else None,
        "flagged_term_hits_per_1000_words": 1000 * sum(phrase_hits(latin_words(span)[0], vocab["flagged_terms"]) for span in spans) / len(words) if words else None,
    })
    return {"coverage": "not_checked" if not words else "partial" if unsupported else "complete",
            "counts": {"words": len(words), "sentences": len(spans), "syllables_estimated": sum(counts),
                       "polysyllables_estimated": sum(n >= 3 for n in counts), "unsupported_tokens": unsupported},
            "metrics": metrics}


def check(text: str, vocab: dict | None = None) -> dict:
    vocab = load_vocabulary() if vocab is None else vocab
    sections = prose_sections(text)
    return {"schema_version": "writing-surface-advisory/1.0", "language": "en",
            "enforcement": ENFORCEMENT,
            "limitations": ["English declared by the caller; language is not inferred.",
                            "Syllables, nominalizations and passive voice are heuristic estimates.",
                            "Non-Latin tokens are excluded; mixed-script results cover only the Latin-token portion.",
                            "FOG counts all estimated polysyllables, including proper names and technical terms.",
                            "SMOG is not reported below 30 detected sentences.",
                            "Flagged-term frequency is a finite lexicon proxy, not a jargon detector or a word ban.",
                            "No threshold, rewrite, authorship score or scientific-quality judgement is produced."],
            "document": measure("\n\n".join(s["text"] for s in sections), vocab),
            "sections": [{"title": s["title"], "line": s["line"], **measure(s["text"], vocab)} for s in sections if s["text"].strip()]}


def render(report: dict) -> str:
    out = ["## Writing surface (advisory, #830)", "", ENFORCEMENT, "",
           "| Scope | Row | Measure | Value |", "| --- | --- | --- | --- |"]
    if "input_sha256" in report:
        out[4:4] = [f"Input SHA-256: `{report['input_sha256']}`",
                    f"Vocabulary SHA-256: `{report['vocabulary_sha256']}`", ""]
    for scope in [{"title": "Document", **report["document"]}, *report["sections"]]:
        label = html.escape(scope["title"]).replace("|", r"\|").replace("\n", " ")
        out.append(f"| {label} | Coverage | {scope['coverage']} | {scope['counts']['words']} words |")
        for row, metric in METRICS:
            value = scope["metrics"][metric]
            out.append(f"| {label} | {row} | {metric} | {'not checked' if value is None else f'{value:.4f}'} |")
    return "\n".join(out + ["", *["- " + note for note in report["limitations"]]]) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--language", choices=["en"], default="en")
    parser.add_argument("--format", choices=["json", "markdown"], default="markdown")
    args = parser.parse_args(argv)
    try:
        raw = args.input.read_bytes()
        vocab = load_vocabulary()
        report = check(raw.decode("utf-8"), vocab)
        report["input_sha256"] = hashlib.sha256(raw).hexdigest()
        report["vocabulary_sha256"] = hashlib.sha256(VOCABULARY.read_bytes()).hexdigest()
    except (OSError, UnicodeError, ValueError, TypeError):
        print("Writing-surface check not run: input or vocabulary could not be read.", file=sys.stderr)
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) if args.format == "json" else render(report), end="\n" if args.format == "json" else "")
    return 0 if report["document"]["coverage"] != "not_checked" else 2


if __name__ == "__main__":
    raise SystemExit(main())
