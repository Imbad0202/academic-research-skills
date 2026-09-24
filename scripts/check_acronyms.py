#!/usr/bin/env python3
"""Deterministic acronym check for a manuscript (#849).

Reads one Markdown or plain-text file and never changes it. No model call.
It checks three rules in each scope (the body, the English abstract, and the
Chinese abstract), and each scope defines its acronyms on its own:

  undefined           an acronym is used in a scope that never defines it;
  defined_after_use   its first use in a scope comes before the scope's first
                      definition;
  defined_again       a scope defines the same acronym more than once.

A definition is a parenthetical whose last item is the acronym, placed right
after text: ``randomized controlled trial (RCT)``, ``大型語言模型（LLM）``, or
``隨機對照試驗（randomized controlled trial, RCT）``. An acronym followed by
its expansion in parentheses (``RCT (randomized controlled trial)``, where
the words' initials spell the acronym) is a definition form this check does
not read: that acronym gets no finding in that scope and the report lists it
as a coverage limit.

Candidates are 2-6 letters or digits with at least two capitals and no more
lowercase than uppercase letters (``RCT``, ``eGFR``, ``qPCR``). Plural and
possessive forms count as the base (``RCTs``, ``RCT's``). Matching is whole
token, so ``AI`` is never found inside ``AIDS``. Not candidates: chemical
formulas, meaning tokens with a digit that read as element symbols and counts
(``H2O``, ``CO2``, but not ``RCT2``); Roman numerals (``II``, ``XII``, but
not ``IV``); and the statistical symbols ``SD``, ``SE``, and ``CI``.

Not read, with line numbers kept: front matter, code fences and spans, HTML
comments (including ``<!--ref:...-->`` and ``<!--anchor:...-->``), math,
URLs, headings, tables, image lines, figure and table captions, notes,
keyword lines, the reference list, parenthetical citations with a year
(``(WHO, 2020)``), APA group-author brackets (``World Health Organization
[WHO]``), and author initials in citations (``Smith JA, Jones BC (2020)``).

Scopes come from headings: ``Abstract`` or ``English Abstract`` starts the
English abstract, ``摘要``, ``中文摘要`` or ``Chinese Abstract`` the Chinese
one, and each runs to the next heading of the same or a higher level.
Everything else is the body. An abstract in another language is a section
this check does not read, listed as a coverage limit, and so is a requested
scope the input does not contain.

Usage:
    python3 scripts/check_acronyms.py --input FILE
        [--scopes body,abstract_en,abstract_zh] [--allow ABBR ...]
        [--allow-file FILE] [--lang en|zh-TW] [--json-out FILE]

Prints the Markdown report in ``--lang`` and writes the JSON report to
``--json-out``, which may be neither the input nor the allowlist file.
Exit 0: the requested scopes were read (``checked``, or ``partial`` with
coverage limits); findings never change the exit status.
Exit 2: nothing was checked (``not_checked``: unsupported format, unreadable
input or allowlist, an unknown scope name, or none of the requested scopes in the input),
and the report says so. A missing report or any other exit status also means
not checked; it is never a clean result.
"""
from __future__ import annotations

import argparse
import bisect
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _markdown_lint_util import blank_code_spans  # noqa: E402

CHECKER = "ars-acronym-check/1.0"
SCOPES = ("body", "abstract_en", "abstract_zh")
RULES = ("undefined", "defined_after_use", "defined_again")
LANGS = ("en", "zh-TW")
SUPPORTED_SUFFIXES = (".md", ".markdown", ".txt")

# Acronyms most journals accept without a definition. Discipline lists belong
# in a user allowlist (--allow / --allow-file), not here.
DEFAULT_ALLOWLIST = frozenset({
    "AIDS", "DNA", "HIV", "IQ", "RNA", "mRNA",
    "EU", "UK", "UN", "US", "USA",
    "BA", "BSc", "MA", "MD", "MSc", "PhD",
    "AM", "PM",
    "DOI", "ISBN", "ISSN", "ORCID", "PDF", "URL",
    "GHz", "GPa", "MHz", "MPa",
})
STAT_SYMBOLS = frozenset({"SD", "SE", "CI"})

_ROMAN = re.compile(r"(?:X{0,3})(?:IX|V?I{0,3}|IV)")
_ELEMENT_PART = re.compile(r"([A-Z][a-z]?)\d*")
ELEMENTS = frozenset("""
H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn Ga Ge As
Se Br Kr Rb Sr Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe Cs Ba La Ce Pr Nd Pm Sm Eu
Gd Tb Dy Ho Er Tm Yb Lu Hf Ta W Re Os Ir Pt Au Hg Tl Pb Bi Po At Rn Fr Ra Ac Th Pa U Np
Pu Am Cm Bk Cf Es Fm Md No Lr Rf Db Sg Bh Hs Mt Ds Rg Cn Nh Fl Mc Lv Ts Og""".split())
_WORD = re.compile(r"(?<![A-Za-z0-9])[A-Za-z][A-Za-z0-9]*(?![A-Za-z0-9])")
_POSSESSIVE = re.compile(r"['’]s(?![A-Za-z0-9])")

_HEADING = re.compile(r"^ {0,3}(#{1,6})(?:[ \t]+(.*?))?[ \t]*#*[ \t]*$")
_FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
_TABLE = re.compile(r"^\s*\|")
_IMAGE = re.compile(r"!\[")
_EMPH = r"(?:\*{1,2}|_{1,2})?"
_CAPTION = re.compile(rf"^\s*{_EMPH}(?:Figure|Fig\.?|Table|圖|表)\s*\d+[A-Za-z]?{_EMPH}(?:[.:：]|\s*$)")
_NOTE = re.compile(rf"^\s*{_EMPH}(?:Notes?{_EMPH}[.:]|(?:註|注|資料來源)[：:])")
_KEYWORDS = re.compile(rf"^\s*{_EMPH}(?:Keywords|Key words|關鍵詞|關鍵字){_EMPH}\s*[:：]", re.I)

_COMMENT = re.compile(r"<!--.*?-->", re.S)
_DISPLAY_MATH = re.compile(r"\$\$.*?\$\$", re.S)
_INLINE_MATH = re.compile(r"\$(?=\S)[^$\n]+?(?<=\S)\$")
_URL = re.compile(r"\((?:https?|ftp)://[^)\s]*\)|(?:https?|ftp)://\S+")
_PAREN = re.compile(r"[(（]([^()（）]*)[)）]")
_UNREAD = re.compile(r"(?:['’]s)?[ \t]?" + _PAREN.pattern)
_TRAILING_PAREN = re.compile(rf"\s*{_PAREN.pattern}\s*$")
_YEAR = r"(?:1[89]|20)\d{2}"
_YEAR_CITATION = re.compile(rf"[(（](?=[^()（）]*\b{_YEAR}[a-z]?\b)[^()（）]*[)）]")
_GROUP_AUTHOR = re.compile(r"\[[A-Za-z][A-Za-z0-9]{1,5}s?\]")
_INITIALS = re.compile(
    rf"\b[A-Z][a-z]+ ([A-Z]{{1,3}})(?=\s*(?:,\s*[A-Z][a-z]+ [A-Z]{{1,3}}\b|et\s+al\b|\(?{_YEAR}\b))")
_LOOKBACK = 300  # characters of context read before a parenthetical
_LATIN_WORD = re.compile(r"[A-Za-z][A-Za-z'’-]*")
_CLAUSE_BREAK = re.compile(r"[.;:!?。；：！？,，、\n]")
_CJK_RUN = re.compile(r"[㐀-鿿]+$")

_EN_ABSTRACT = {"abstract", "english abstract", "英文摘要"}
_ZH_ABSTRACT = {"摘要", "中文摘要", "chinese abstract"}
_OTHER_ABSTRACT = {"resumen", "résumé", "resumo", "zusammenfassung", "sommario", "riassunto",
                   "samenvatting", "streszczenie", "аннотация", "요약", "초록", "要旨", "抄録",
                   "abstrak", "özet"}
_EXCLUDED_SECTIONS = {
    "references", "reference list", "bibliography", "works cited", "literature cited",
    "參考文獻", "參考資料", "引用文獻", "keywords",
}
_STOP = {"of", "and", "the", "for", "in", "on", "to", "a", "an", "with", "by", "at", "or"}


class NotChecked(Exception):
    """Nothing could be checked; the message is the reason code."""


@dataclass(frozen=True)
class Occurrence:
    line: int
    acronym: str
    kind: str  # "use", "definition", or "unread_definition"
    expansion: str | None = None


def is_candidate(token: str) -> bool:
    if not 2 <= len(token) <= 6 or not token.isascii() or not token.isalnum():
        return False
    upper = sum(c.isupper() for c in token)
    lower = sum(c.islower() for c in token)
    if upper < 2 or lower > upper or token in STAT_SYMBOLS:
        return False
    if any(c.isdigit() for c in token) and _is_formula(token):
        return False
    return not (_ROMAN.fullmatch(token) and token != "IV")


def _is_formula(token: str) -> bool:
    """True when the token reads as element symbols with counts (``H2O``, ``CO2``)."""
    parts = list(_ELEMENT_PART.finditer(token))
    return ("".join(m.group(0) for m in parts) == token
            and all(m.group(1) in ELEMENTS for m in parts))


def base_form(word: str) -> str | None:
    """The acronym a word counts as, or None; ``RCTs`` counts as ``RCT``."""
    if word.endswith("s") and is_candidate(word[:-1]):
        return word[:-1]
    return word if is_candidate(word) else None


def _spells(acronym: str, words: str) -> bool:
    """True when the acronym's letters appear, in order, as the words' initials."""
    initials = [w[0].lower() for w in _LATIN_WORD.findall(words) if w.casefold() not in _STOP]
    letters = iter(initials)
    return len(initials) >= 2 and all(c in letters for c in acronym.lower() if c.isalpha())


def _normalize_heading(text: str) -> str:
    text = re.sub(r"[*_`]", "", text).strip()
    text = re.sub(r"^(?:[0-9IVX]+(?:\.[0-9]+)*[.)]?|[一二三四五六七八九十壹貳參肆伍]+[、.])\s*", "", text)
    text = _TRAILING_PAREN.sub("", text)
    return text.strip().casefold()


def _blank(chars: list[str], start: int, end: int) -> None:
    for i in range(start, end):
        if chars[i] != "\n":
            chars[i] = " "


def _blank_pattern(chars: list[str], pattern: re.Pattern[str], group: int = 0) -> None:
    text = "".join(chars)
    for match in pattern.finditer(text):
        _blank(chars, match.start(group), match.end(group))


class Manuscript:
    """The masked text, the line of each offset, and the scope of each line."""

    def __init__(self, text: str) -> None:
        self.lines = text.split("\n")
        self.starts = [0]
        for line in self.lines[:-1]:
            self.starts.append(self.starts[-1] + len(line) + 1)
        chars = list(text)
        self.scope: list[str | None] = ["body"] * len(self.lines)
        self.ranges: dict[str, list[list[int]]] = {s: [] for s in SCOPES}
        self.unread_sections: list[dict[str, Any]] = []
        self._mask_blocks(chars)
        _blank_pattern(chars, _COMMENT)
        self._assign_scopes(chars)
        for start, line in zip(self.starts, self.lines):
            chars[start:start + len(line)] = blank_code_spans("".join(chars[start:start + len(line)]))
        for pattern, group in ((_DISPLAY_MATH, 0), (_INLINE_MATH, 0), (_URL, 0),
                               (_INITIALS, 1), (_YEAR_CITATION, 0), (_GROUP_AUTHOR, 0)):
            _blank_pattern(chars, pattern, group)
        self.masked = "".join(chars)
        if text.endswith("\n"):
            self.scope[-1] = None  # the empty string after the final newline is not a line
        for number, scope in enumerate(self.scope, start=1):
            if scope is None:
                continue
            spans = self.ranges[scope]
            if spans and spans[-1][1] == number - 1:
                spans[-1][1] = number
            else:
                spans.append([number, number])

    def _blank_line(self, chars: list[str], index: int) -> None:
        _blank(chars, self.starts[index], self.starts[index] + len(self.lines[index]))

    def _mask_blocks(self, chars: list[str]) -> None:
        """Front matter and code fences, by line."""
        index = 0
        if self.lines[0].rstrip("\r") == "---":
            for end in range(1, len(self.lines)):
                if self.lines[end].rstrip("\r") in ("---", "..."):
                    for i in range(end + 1):
                        self._blank_line(chars, i)
                    index = end + 1
                    break
        fence: str | None = None
        for i in range(index, len(self.lines)):
            match = _FENCE.match(self.lines[i])
            if fence is None:
                if match:
                    fence = match.group(1)
                    self._blank_line(chars, i)
                continue
            self._blank_line(chars, i)
            if (match and match.group(1)[0] == fence[0] and len(match.group(1)) >= len(fence)
                    and not self.lines[i][match.end():].strip()):
                fence = None

    def _assign_scopes(self, chars: list[str]) -> None:
        """Headings set scopes; excluded and unread sections are blanked."""
        section: tuple[int, str | None] | None = None  # (level, scope or None when excluded)
        for i, raw in enumerate(self.lines):
            line = "".join(chars[self.starts[i]:self.starts[i] + len(raw)])
            heading = _HEADING.match(line) if line.strip() else None
            if heading:
                level = len(heading.group(1))
                name = _normalize_heading(heading.group(2) or "")
                if section is not None and level <= section[0]:
                    section = None
                if name in _EN_ABSTRACT:
                    section = (level, "abstract_en")
                elif name in _ZH_ABSTRACT:
                    section = (level, "abstract_zh")
                elif name in _OTHER_ABSTRACT or re.fullmatch(r"\w+ abstract", name):
                    section = (level, None)
                    self.unread_sections.append({"line": i + 1, "heading": (heading.group(2) or "").strip()})
                elif name in _EXCLUDED_SECTIONS:
                    section = (level, None)
                self.scope[i] = None
                self._blank_line(chars, i)
                continue
            self.scope[i] = "body" if section is None else section[1]
            if (self.scope[i] is None or _TABLE.match(line) or _IMAGE.search(line)
                    or _CAPTION.match(line) or _NOTE.match(line) or _KEYWORDS.match(line)):
                self._blank_line(chars, i)

    def line_of(self, offset: int) -> int:
        return bisect.bisect_right(self.starts, offset)


def _expansion(before: str, acronym: str) -> str | None:
    """The words a definition follows, in its clause: the CJK run, or as many
    Latin words as the acronym has capitals (stop words not counted)."""
    head = _CLAUSE_BREAK.split(before)[-1].rstrip()
    cjk = _CJK_RUN.search(head)
    if cjk:
        return cjk.group(0)[-20:]
    if not re.search(r"[A-Za-z]$", head):
        return head or None
    picked: list[str] = []
    wanted = sum(c.isupper() for c in acronym)
    for word in reversed(_LATIN_WORD.findall(head)):
        picked.append(word)
        if word.casefold() not in _STOP:
            wanted -= 1
            if not wanted:
                break
    return " ".join(reversed(picked))


def find_occurrences(doc: Manuscript) -> list[Occurrence]:
    text = doc.masked
    defined: dict[int, Occurrence] = {}
    for paren in _PAREN.finditer(text):
        content = paren.group(1)
        items = [item.strip() for item in re.split(r"[,，;；、]", content)]
        last = items[-1]
        bare = _POSSESSIVE.sub("", last)
        acronym = base_form(bare) if _WORD.fullmatch(bare) else None
        before = text[max(0, paren.start() - _LOOKBACK):paren.start()].rstrip(" \t")
        if acronym is None or not before or before[-1] in "\n([（":
            continue
        expansion = " ".join(items[:-1]) or None if len(items) > 1 else _expansion(before, acronym)
        offset = paren.start(1) + content.rfind(last)
        defined[offset] = Occurrence(doc.line_of(offset), acronym, "definition", expansion)
    occurrences: list[Occurrence] = []
    for word in _WORD.finditer(text):
        acronym = base_form(word.group(0))
        if acronym is None:
            continue
        if word.start() in defined:
            occurrences.append(defined[word.start()])
            continue
        unread = _UNREAD.match(text, word.end())
        kind = ("unread_definition" if unread and acronym not in unread.group(1)
                and _spells(acronym, unread.group(1)) else "use")
        occurrences.append(Occurrence(doc.line_of(word.start()), acronym, kind))
    return occurrences


def check(text: str, scopes: tuple[str, ...] = SCOPES,
          allow: frozenset[str] = DEFAULT_ALLOWLIST) -> dict[str, Any]:
    doc = Manuscript(text)
    by_scope: dict[str, dict[str, list[Occurrence]]] = {s: {} for s in SCOPES}
    for occurrence in find_occurrences(doc):
        scope = doc.scope[occurrence.line - 1]
        if scope in scopes:
            by_scope[scope].setdefault(occurrence.acronym, []).append(occurrence)
    findings: list[dict[str, Any]] = []
    limits: list[dict[str, Any]] = []
    for scope in scopes:
        for acronym, found in sorted(by_scope[scope].items()):
            if acronym in allow:
                continue
            count = len(found)
            unread = [o for o in found if o.kind == "unread_definition"]
            if unread:
                limits.append({"scope": scope, "line": unread[0].line, "acronym": acronym,
                               "reason": "unread_definition_form"})
                continue
            definitions = [o for o in found if o.kind == "definition"]
            if not definitions:
                findings.append(_finding(scope, found[0].line, "undefined", acronym, None, count))
                continue
            if found[0].kind == "use":
                findings.append(_finding(scope, found[0].line, "defined_after_use", acronym,
                                         definitions[0].expansion, count))
            for repeat in definitions[1:]:
                findings.append(_finding(scope, repeat.line, "defined_again", acronym,
                                         repeat.expansion, count))
    order = {scope: i for i, scope in enumerate(SCOPES)}
    findings.sort(key=lambda f: (order[f["scope"]], f["line"], RULES.index(f["rule"]), f["acronym"]))
    limits.sort(key=lambda f: (order[f["scope"]], f["line"], f["acronym"]))
    coverage = {scope: ("not_requested" if scope not in scopes
                        else "checked" if doc.ranges[scope] else "not_in_input")
                for scope in SCOPES}
    if not any(state == "checked" for state in coverage.values()):
        raise NotChecked("no_requested_scope_in_input")
    missing = any(state == "not_in_input" for state in coverage.values())
    status = "partial" if limits or doc.unread_sections or missing else "checked"
    return {"status": status, "coverage": coverage,
            "scope_lines": {s: doc.ranges[s] for s in SCOPES if coverage[s] == "checked"},
            "unread_sections": doc.unread_sections, "coverage_limits": limits,
            "findings": findings}


def _finding(scope: str, line: int, rule: str, acronym: str, expansion: str | None,
             count: int) -> dict[str, Any]:
    return {"scope": scope, "line": line, "rule": rule, "acronym": acronym,
            "expansion": expansion, "occurrences": count}


# ---------------------------------------------------------------------------
# Markdown report. The caller shows it as written; English and Traditional
# Chinese, chosen by the language the user writes in.
# ---------------------------------------------------------------------------

_ZH_SCOPES = {"body": "正文", "abstract_en": "英文摘要", "abstract_zh": "中文摘要"}
_TEXT = {
    "en": {
        "title": "### Acronym check (advisory; no reply needed)",
        "coverage": "Coverage: {scopes} ({state})",
        "states": {"checked": "complete", "partial": "partial"},
        "absent": "Not in this input: {scopes}.",
        "limits": "Not checked:",
        "limit": "- {scope}, line {line}: {acronym} (a definition form this check does not read)",
        "section": "- Line {line}: section \"{heading}\" (not a scope this check reads)",
        "none": "No findings.",
        "header": "| Scope | Line | Rule | Acronym | Uses |",
        "not_checked": "Not checked: {reason}.",
        "scope_names": {"body": "body", "abstract_en": "English abstract",
                        "abstract_zh": "Chinese abstract"},
        "scope_cells": {"body": "Body", "abstract_en": "EN abstract", "abstract_zh": "ZH abstract"},
        "rules": {"undefined": "Not defined", "defined_after_use": "Defined after first use",
                  "defined_again": "Defined again"},
        "join": ", ",
        "reasons": {
            "unsupported_format": "the input is not a Markdown or plain-text file",
            "unreadable_input": "the input cannot be read as UTF-8 text",
            "unknown_scope": "a requested scope is not body, abstract_en, or abstract_zh",
            "unreadable_allowlist": "the allowlist file cannot be read",
            "no_requested_scope_in_input": "none of the requested scopes is in the input",
        },
    },
    "zh-TW": {
        "title": "### 縮寫檢查（僅供參考，不必回覆）",
        "coverage": "範圍：{scopes}（{state}）",
        "states": {"checked": "完整", "partial": "部分"},
        "absent": "此檔沒有：{scopes}。",
        "limits": "未檢查：",
        "limit": "- {scope}第 {line} 行：{acronym}（這個檢查讀不到的定義寫法）",
        "section": "- 第 {line} 行：「{heading}」段落（不是這個檢查會讀的範圍）",
        "none": "沒有發現問題。",
        "header": "| 範圍 | 行 | 問題 | 縮寫 | 次數 |",
        "not_checked": "未檢查：{reason}。",
        "scope_names": _ZH_SCOPES,
        "scope_cells": _ZH_SCOPES,
        "rules": {"undefined": "未定義", "defined_after_use": "定義晚於首次使用",
                  "defined_again": "重複定義"},
        "join": "、",
        "reasons": {
            "unsupported_format": "輸入檔不是 Markdown 或純文字檔",
            "unreadable_input": "輸入檔無法以 UTF-8 文字讀取",
            "unknown_scope": "指定的範圍不是 body、abstract_en 或 abstract_zh",
            "unreadable_allowlist": "免定義清單檔無法讀取",
            "no_requested_scope_in_input": "輸入檔裡沒有任何指定的範圍",
        },
    },
}


def render(report: dict[str, Any], lang: str) -> str:
    text = _TEXT[lang]
    lines = [text["title"]]
    if report["status"] == "not_checked":
        lines.append(text["not_checked"].format(reason=text["reasons"][report["reason"]]))
        return "\n".join(lines)
    names = text["scope_names"]
    checked = [names[s] for s in SCOPES if report["coverage"][s] == "checked"]
    lines.append(text["coverage"].format(scopes=text["join"].join(checked),
                                         state=text["states"][report["status"]]))
    absent = [names[s] for s in SCOPES if report["coverage"][s] == "not_in_input"]
    if absent:
        lines.append(text["absent"].format(scopes=text["join"].join(absent)))
    if report["coverage_limits"] or report["unread_sections"]:
        lines.append(text["limits"])
        lines += [text["limit"].format(scope=text["scope_cells"][item["scope"]], line=item["line"],
                                       acronym=item["acronym"])
                  for item in report["coverage_limits"]]
        lines += [text["section"].format(line=item["line"], heading=item["heading"])
                  for item in report["unread_sections"]]
    if not report["findings"]:
        lines.append(text["none"])
        return "\n".join(lines)
    lines += ["", text["header"], "|---|---|---|---|---|"]
    lines += [f"| {text['scope_cells'][f['scope']]} | {f['line']} | {text['rules'][f['rule']]} "
              f"| {f['acronym']} | {f['occurrences']} |" for f in report["findings"]]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI.
# ---------------------------------------------------------------------------


def _read_allowlist(path: Path) -> set[str]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        raise NotChecked("unreadable_allowlist") from exc
    return {line.split("#", 1)[0].strip() for line in lines} - {""}


def _same_file(a: Path, b: Path) -> bool:
    """True when both paths name one file, including through a link."""
    try:
        return a.resolve() == b.resolve() or a.samefile(b)
    except OSError:
        return False


def build_report(path: Path, scopes_arg: str, allow: list[str], allow_file: Path | None) -> dict[str, Any]:
    report: dict[str, Any] = {"checker": CHECKER, "input": str(path), "input_sha256": None,
                              "status": "not_checked"}
    try:
        scopes = tuple(s.strip() for s in scopes_arg.split(",") if s.strip())
        if not scopes or any(s not in SCOPES for s in scopes):
            raise NotChecked("unknown_scope")
        if path.suffix.lower() not in SUPPORTED_SUFFIXES:
            raise NotChecked("unsupported_format")
        try:
            raw = path.read_bytes()
            text = raw.decode("utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            raise NotChecked("unreadable_input") from exc
        report["input_sha256"] = hashlib.sha256(raw).hexdigest()
        user = set(allow) | (_read_allowlist(allow_file) if allow_file else set())
        report["allowlist"] = {"default": len(DEFAULT_ALLOWLIST), "user": sorted(user)}
        report.update(check(text.replace("\r\n", "\n"), scopes, DEFAULT_ALLOWLIST | frozenset(user)))
    except NotChecked as exc:
        report["reason"] = str(exc)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Deterministic acronym check (#849).")
    parser.add_argument("--input", type=Path, required=True, help="Markdown or plain-text manuscript.")
    parser.add_argument("--scopes", default=",".join(SCOPES),
                        help="Comma-separated scopes to check (default: all three).")
    parser.add_argument("--allow", action="append", default=[], help="An acronym needing no definition.")
    parser.add_argument("--allow-file", type=Path, help="One acronym per line; # starts a comment.")
    parser.add_argument("--lang", choices=LANGS, default="en", help="Language of the Markdown report.")
    parser.add_argument("--json-out", type=Path, help="Write the JSON report to this file.")
    args = parser.parse_args(argv)
    if args.json_out and any(_same_file(args.json_out, path)
                             for path in (args.input, args.allow_file) if path):
        parser.error("--json-out may not be the input file or the allowlist file")
    report = build_report(args.input, args.scopes, args.allow, args.allow_file)
    if args.json_out:
        args.json_out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(render(report, args.lang))
    return 2 if report["status"] == "not_checked" else 0


if __name__ == "__main__":
    sys.exit(main())
