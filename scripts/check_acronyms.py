#!/usr/bin/env python3
"""Deterministic acronym check for a manuscript (#849).

Reads one Markdown or plain-text file and never changes it. No model call.
It checks three rules in each scope (the body, the English abstract, and the
Chinese abstract), and each scope defines its acronyms on its own:

  undefined           an acronym is used in a scope that never defines it;
  defined_after_use   its first use in a scope comes before the scope's first
                      definition;
  defined_again       a scope defines the same acronym more than once.

A definition is a parenthetical whose last item is the acronym, placed after
text in the same paragraph (a line break inside a paragraph reads as a space),
when the words before it spell the acronym: ``randomized controlled trial
(RCT)``, ``大型語言模型（LLM）``, or ``隨機對照試驗（randomized controlled
trial, RCT）``. Chinese words spell any acronym, and quotation marks around
the words are ignored (``「大型語言模型」（LLM）``); Latin words spell it when
the first starts with the acronym's first letter and their initials contain
its letters in order. The expansion is the shortest such run of words. For
Chinese words before the parenthetical, which have no spaces between them, it
is the whole run of Chinese characters there, read across a space or line
break between two of them; any other character, such as punctuation, a digit,
or a Latin letter, ends the run, so it can hold words before the term
(``本研究採用結構方程模型（SEM）``) or lose a part of it (``2型糖尿病（T2D）``
gives ``型糖尿病``). Two kinds of acronym get no finding in their scope and
are listed as coverage limits: one whose parenthetical the words do not spell
(``several methods (RCT)``), which this check cannot confirm as a definition,
and one followed by its expansion in parentheses (``RCT (randomized controlled
trial)``, ``RCT（隨機對照試驗）``), a definition form this check does not
read. Words after the acronym count as its expansion when they spell it, so a
list whose initials spell it counts too (``ML (MARS, LASSO, and random
forests)``). A parenthetical is a use, not a definition, when it opens with
``e.g.``, ``e. g.``, ``eg``, ``see``, ``cf.``, ``for example``,
``for instance``, ``such as``, ``including``, ``例如``, ``比如``, ``諸如``, or
``包括``, before or after the acronym (``(e.g., RCT)``,
``RCT (including recruitment)``), or when it is made only of acronyms,
counting excluded ones, symbols, numbers, and joining words or marks, before
or after the acronym (``(SEM, RCT)``, ``ML (MARS, LASSO)``, ``(SDs, RMSE)``,
``(R², AIC, BIC)``, ``(n = 120, RCT)``, ``(PCA/ICA, NMF)``,
``(COVID-19, ARDS)``, ``(PCA and ICA, NMF)``, ``（PCA與ICA，NMF）``). So are
Chinese words after an acronym that open with ``見``, ``參見``, ``詳見``, or
``參閱`` (``RCT（見第二節）``). A lead at the start of a parenthetical or of
its last item is read as if absent, and so are quotation marks around the
acronym. A lead is a restatement (such as ``i.e.`` or ``i. e.``, ``viz.``,
``namely``, ``that is``, ``in other words``, ``即``, ``亦即``, ``也就是``) or
a naming lead (such as ``hereafter``, ``henceforth``, ``abbreviated as``,
``referred to as``, ``also known as``, ``aka``, ``called``, ``以下簡稱``,
``下稱``, ``簡稱``, ``又稱``, ``稱為``, ``縮寫為``). So ``structural equation
modeling (i.e., SEM)``, ``structural equation modeling (hereafter SEM)``, and
``結構方程模型（structural equation modeling，以下簡稱「SEM」）`` define
``SEM``. After a restatement, an acronym the words before it do not spell is a
use (``two designs (namely RCT)``); after a naming lead, it is a definition
this check cannot confirm (``two designs (hereafter RCT)``).

Candidates are 2-6 letters or digits, starting with a letter, with at least
two capitals and no more lowercase than uppercase letters (``RCT``, ``eGFR``,
``qPCR``, but not ``2FA``). Plural and possessive forms count as the base
(``RCTs``, ``RCT's``). Matching is whole token, so ``AI`` is never found
inside ``AIDS``. Not candidates: chemical formulas, meaning tokens with a
digit that read as element symbols and counts (``H2O``, ``CO2``, but not
``RCT2``); Roman numerals up to ``XXXIX`` (``II``, ``XII``); ``IV`` and stage
numerals with a letter from A to D and an optional digit (``IIIB``, ``IIID``,
``IA1``) only right after a numbering word, or after a list of numerals that
follows one, in the same sentence, or in a Chinese stage (``Table IV``,
``stage IIIB``, ``stages I through IV``, ``第IV期``, ``IV 期``), since ``IV``
alone is a common acronym; and the statistical symbols ``SD``, ``SE``, and
``CI``. Larger numerals stay candidates, because letter strings such as
``CD``, ``DC``, ``MI``, and ``LV`` are also common acronyms. The plural of an
excluded token is excluded too (``CIs``, ``SDs``).

Not read, with line numbers kept: front matter, code fences, code spans (a
backtick run pairs with the next run of the same length on its line, and a
backslash or a comment marker inside a span is literal), HTML comments
(including ``<!--ref:...-->`` and ``<!--anchor:...-->``), math (inline math
within one line), URLs, link destinations and titles
(``[the protocol](#RCT)``, ``[the site](https://example.org "RCT")``), link
reference definitions (``[RCT]: https://example.org``) and the labels that
name them in full reference links (``[the protocol][RCT]``), ATX and setext
headings, tables (with or without outer pipes, up to a blank line, heading,
list item, blockquote, or thematic break), image lines, caption, note, and
keyword paragraphs (from a line that starts a paragraph or follows an image
and opens with a label such as ``Figure 2.``, ``Table S1.``, ``TABLE III``,
``Supplementary Table 2.``, ``Box 1.``, ``Figure 1 |``, ``圖 2-1：``,
``表一：``, ``Note.``, or ``Keywords:``, up to a blank line; the number must
end the line or come before a period, colon, pipe, or dash, but a dash that
starts a range and an unspaced hyphen (``Table 1-based``) open no label, and
neither do ``Figure 1.2 shows`` and ``Fig. 1 Flow diagram``; a range end is a
number or a labeled number (``Figure 1 – 3``, ``Table 1–Table 3``,
``圖1–圖3``), an end of the number's own kind (a letter after ``1A``, a Roman
numeral up to 20 above a Roman start, a Chinese numeral after a Chinese one:
``Figure 1A – C``, ``Table XXXIX–XL``, ``圖一–三``) that no hyphen follows
(``Table I – X-ray findings`` is a title), or a single letter right after an
unspaced dash (``Figure 1–C shows``), so a caption title that starts that way
is read as prose), the reference list, author-year citations whose author part
is a run of names, whose dates are years from 1800 to 2099, year pairs or
ranges, ``n.d.``, or ``in press`` (``2020a``, ``1900/1953``, ``n.d.-a``), and
whose locator, if any, is a page, paragraph, chapter, or section
(``(WHO, 2020)``, ``(see Smith et al., 2020, pp. 4, 6; Lee, 2019)``, and the
citations after the acronym in ``(RCTs; Smith, 2020)``), a bracketed
abbreviation right after a capitalized word, as in an APA group author
(``World Health Organization [WHO]``), but not a link (``[RCT](#design)``, or
``[RCT]`` when a link reference definition names it), and author initials in
author lists, whose names are joined by commas, ``and``, or ``&`` and come
before ``et al.`` or a date in a form a citation takes (``Smith JA, García BC,
McDonald EF, and van der Berg GH (2020a)``); prose shaped like such a list, as
in ``Delphi RCT and Bayesian SEM (2020)``, is read as one. In definitions, the
leading words above, citations, group-author brackets, and author lists, a
line break inside a paragraph reads as a space, and a line break or space
between two Chinese characters is ignored.

These rules read Markdown line by line; this is not a full CommonMark parser.
Markdown the rules do not name, such as an HTML block, can be read as prose or
as part of the construct before it, and a named construct can be misread when
it sits inside another one or has no blank line around it.

Scopes come from headings: ``Abstract`` or ``English Abstract`` starts the
English abstract, ``摘要``, ``中文摘要`` or ``Chinese Abstract`` the Chinese
one, and each runs to the next heading of the same or a higher level.
Everything else is the body. A scope is in the input only when a line this
check reads there has a letter. An abstract in another language is a section
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
input or allowlist, an unknown scope name, or none of the requested scopes in
the input), and the report says so. A missing report or any other exit status
also means not checked; it is never a clean result.
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
_SETEXT = re.compile(r"^ {0,3}(=+|-+)[ \t]*$")
_BLOCK_START = re.compile(r"^ {0,3}(?:[-*+][ \t]|\d{1,9}[.)][ \t]|>)")
_THEMATIC_BREAK = re.compile(r"^ {0,3}([-*_])(?:[ \t]*\1){2,}[ \t]*$")
_FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
_TABLE = re.compile(r"^\s*\|")
_TABLE_DELIMITER = re.compile(r"^ {0,3}\|?[ \t]*:?-+:?[ \t]*(?:\|[ \t]*:?-+:?[ \t]*)*\|?[ \t]*$")
_IMAGE = re.compile(r"!\[")
_EMPH = r"(?:\*{1,2}|_{1,2})?"
# Capital and small letters in the Latin, Greek, and Cyrillic blocks, with Latin
# Extended Additional and Greek Extended, so an author name such as "García",
# "Öztürk", or "Nguyễn" reads as a name.
_NAME_LETTERS = [chr(c) for block in (range(0x530), range(0x1E00, 0x2000)) for c in block]
_UPPER = "".join(c for c in _NAME_LETTERS if c.isalpha() and c.isupper())
_LOWER = "".join(c for c in _NAME_LETTERS if c.isalpha() and c.islower())
# A caption label: an optional prefix ("Supplementary", "Extended Data", "附"), a
# label word, and a number: Arabic, with a letter prefix, dots, or hyphens ("S1",
# "A.1", "2-1"), a Roman numeral ("III"), or one capital letter ("B").
_ARABIC_ID = r"(?:[A-Z][.-]?)?\d+(?:[.-]\d+)*"
_CAPTION_ID = rf"(?:{_ARABIC_ID}[A-Za-z]?|[IVXLC]+|[A-Z])"
_CAPTION_WORD = (r"(?i:(?:(?:Supplementary|Supplemental|Suppl?\.|Extended\s+Data|Appendix"
                 r"|Online)\s*)?(?:Figure|Fig\.?|Table|Box|Scheme|Plate|Chart|Exhibit))")
_ZH_NUMERAL = "[一二三四五六七八九十百零〇]+"
_CAPTION = re.compile(rf"^\s*{_EMPH}(?:{_CAPTION_WORD}\s*(?P<id>{_CAPTION_ID})"
                      rf"|附?[圖表]\s*(?P<zh>{_CAPTION_ID}|{_ZH_NUMERAL}))"
                      rf"{_EMPH}(?:[.:：](?!\d)|\s*\||(?P<dash>\s*[–—]|\s+-\s)|\s*$)")
# Range ends after a caption dash (see _caption_label).
_RANGE_ANY = re.compile(rf"\s*(?:[A-Z]?[.-]?\d"
                        rf"|(?:{_CAPTION_WORD}|附?[圖表])\s*(?:{_CAPTION_ID}|{_ZH_NUMERAL})(?![A-Za-z0-9]))")
_SUBFIGURE = re.compile(rf"{_ARABIC_ID}[A-Za-z]|(?![IVXLC])[A-Z]")
_RANGE_LETTER = re.compile(r"\s*[A-Za-z](?![A-Za-z0-9-])")  # not "C-reactive"
_RANGE_ROMAN = re.compile(r"\s*([IVXLCDM]+)(?![A-Za-z0-9-])")  # not "X-ray"
_STANDARD_ROMAN = re.compile(r"(?=[MDCLXVI])M{0,3}(?:CM|CD|D?C{0,3})(?:XC|XL|L?X{0,3})(?:IX|IV|V?I{0,3})")
_ROMAN_VALUES = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
_RANGE_ZH = re.compile(rf"\s*{_ZH_NUMERAL}")
_NOTE = re.compile(rf"^\s*{_EMPH}(?:Notes?{_EMPH}[.:]|(?:註|注|資料來源)[：:])")
_KEYWORDS = re.compile(rf"^\s*{_EMPH}(?:Keywords|Key words|關鍵詞|關鍵字){_EMPH}\s*[:：]", re.I)

_COMMENT_OR_BACKTICKS = re.compile(r"<!--|`+")
# A link reference definition ("[RCT]: https://example.org"), which is not shown.
_LINK_DEFINITION = re.compile(r"^ {0,3}\[([^\]\n]+)\]:[ \t]*\S")
_DISPLAY_MATH = re.compile(r"\$\$.*?\$\$", re.S)
_INLINE_MATH = re.compile(r"(?<!\\)\$(?=\S)[^$\n]+?(?<=\S)\$")
_URL = re.compile(r"\((?:https?|ftp)://[^)\s]*\)|(?:https?|ftp)://\S+")
_PAREN = re.compile(r"[(（]([^()（）]*)[)）]")
_ITEM_BREAK = re.compile(r"[,，;；、]")
_TRAILING_PAREN = re.compile(rf"\s*{_PAREN.pattern}\s*$")
_YEAR = r"(?:1[89]|20)\d{2}"  # 1800 to 2099, for citations and author lists alike
_COMMA = r"[,，]"
_SPACE = r"(?:[ \t]+(?:\n[ \t]*)?|\n[ \t]*)"  # a space or one line break, never a blank line
_UNREAD = re.compile(rf"(?:['’]s)?(?:{_SPACE})?{_PAREN.pattern}")
# A link's destination and title, which are not shown: "[the protocol](#RCT)",
# '[the site](https://example.org "RCT")', with backslash escapes inside. The link text stays.
_LINK_TARGET = re.compile(
    rf"(?<=\])\((?:{_SPACE})?(?:<(?:[^<>\\\n]|\\.)*>|(?:[^\s()<>\\]|\\\S|\((?:[^\s()\\]|\\\S)*\))*)"
    rf"(?:{_SPACE}(?:\"(?:[^\"\\\n]|\\.)*\"|'(?:[^'\\\n]|\\.)*'|\((?:[^()\\\n]|\\.)*\)))?(?:{_SPACE})?\)")
# The label of a full reference link, which is not shown: "[the protocol][RCT]".
_LINK_LABEL = re.compile(r"(?<=\])\[([^\[\]\n]*)\]")
# "IV" and stage numerals ("IIIB", "IVA") are numerals after a numbering word ("Table IV",
# "stage IIIB", "phases III and IV", "stage-IV", "Fig. IV", "第IV期"), never across a sentence
# end or a blank line.
_STAGE_SUFFIX = r"(?:[A-Da-d]\d?)?"  # "IIID", "IB2"
_ROMAN_STAGE = re.compile(rf"(?=[IVX]){_ROMAN.pattern}{_STAGE_SUFFIX}")  # used only with fullmatch
_NUMBERING_WORD = (r"(?i:\b(?:(?:table|figure|box|section|chapter|part|appendix|volume|phase|stage"
                   r"|grade|type|class|level|tier|category|study|experiment|wave|round|model)s?"
                   r"|(?:figs?|vols?)\.?))")
_ROMAN_JOIN = (rf"(?:(?:{_SPACE})?[,&–—/-](?:{_SPACE})?(?:(?:and|or){_SPACE})?"
               rf"|{_SPACE}(?:and|or|to|through){_SPACE})")
_NUMBERING_BEFORE = re.compile(
    rf"(?:{_NUMBERING_WORD}(?:{_SPACE}|-)(?:[IVXLC]+{_STAGE_SUFFIX}{_ROMAN_JOIN})*|第(?:{_SPACE})?)\Z")
_NUMBERING_AFTER = re.compile(rf"(?:{_SPACE})?[期級型類]")
# An author-year citation: items whose author part is a run of names (capitalized
# words, a bracketed group abbreviation, CJK, "&", "and", "et al.", or a name
# particle), then one or more dates and an optional page, paragraph, chapter, or
# section locator. "(Smith et al., 2020, pp. 4, 6; Lee, 2019)" and "(WHO, 2020)"
# match; "(LLM in 2020)" and "(LLM use began in May 2020)" do not.
_GROUP_ABBR = r"\[[A-Za-z][A-Za-z0-9]{1,5}s?\]"  # "[WHO]", "[RCTs]"
_CJK = "㐀-鿿"  # CJK Unified Ideographs and Extension A, as a character-class range
_PARTICLE = r"(?:[vV]an|[vV]on|[dD]e|[dD]er|[dD]en|[dD]u|[dD]a|[dD]i|[dD]el|[lL]a|[lL]e)"
_NAME = (rf"(?:[{_UPPER}][\w'’.-]*|{_GROUP_ABBR}|[{_CJK}]+|&|and|et{_SPACE}al\.?"
         rf"|{_PARTICLE}(?=\s))")
# A citation date: a year (2020, 2020a), a reprint pair or a range (1900/1953,
# 1959–1963), "n.d.", or "in press", the last two with a letter when one author
# has several such works (n.d.-a, in press-b).
_DATE = rf"(?:{_YEAR}(?:[/–-]{_YEAR})?[a-z]?|(?:n\.d\.|in{_SPACE}press)(?:-[a-z])?)"
_LOCATOR = (rf"(?:(?:p|pp|paras?|ch|chap|secs?)\.\s*|(?:Chapter|Section){_SPACE})[\w.–-]+"
            rf"(?:\s*{_COMMA}\s*[\w.–-]*\d[\w.–-]*)*")
_CITE_ITEM = (rf"\s*(?:(?:see(?:{_SPACE}also)?|e\.g\.|cf\.|i\.e\.)\s*(?:{_COMMA}\s*)?)?"
              rf"{_NAME}(?:(?:\s*[,，、]\s*|\s+){_NAME})*\s*(?:{_COMMA}\s*)?"
              rf"{_DATE}(?:\s*{_COMMA}\s*{_DATE})*"
              rf"(?:\s*{_COMMA}\s*{_LOCATOR})?\s*")
_CITATION = re.compile(rf"[(（]{_CITE_ITEM}(?:[;；]{_CITE_ITEM})*[)）]")
# The citations after an acronym in "(RCTs; Smith, 2020)".
_TRAILING_CITATION = re.compile(rf"[;；]{_CITE_ITEM}(?:[;；]{_CITE_ITEM})*(?=[)）])")
# "World Health Organization [WHO]": a bracket after a capitalized word, not a
# Markdown link ("[RCT](#design)", "[RCT][1]", or "[RCT]" with a definition).
_GROUP_AUTHOR = re.compile(rf"\b[{_UPPER}][{_LOWER}]+{_SPACE}({_GROUP_ABBR})(?![(\[:])")
# Author initials in an author list: "Smith JA, Jones BC (2019)", "Lee KM et al.".
# A surname may hold a capital that starts a new run of small letters, after an
# apostrophe or hyphen or not ("McDonald", "O'Brien", "Smith-Jones"), and may
# follow name particles ("van der Berg").
_SURNAME = rf"[{_UPPER}](?:[{_LOWER}]|['’-]?[{_UPPER}](?=[{_LOWER}]))*[{_LOWER}]"
_AUTHOR = re.compile(rf"(?:{_PARTICLE}{_SPACE})*({_SURNAME}){_SPACE}([A-Z]{{1,3}})\b")
_AUTHOR_SEP = rf"(?:\s*,\s*(?:(?:and|&){_SPACE})?|{_SPACE}(?:and|&){_SPACE})"
_AUTHOR_LIST = re.compile(rf"\b{_AUTHOR.pattern}(?:{_AUTHOR_SEP}{_AUTHOR.pattern})*"
                          rf"(?=\s*(?:,\s*)?(?:et\s+al\b|\(?{_DATE}(?!\w)))")
# One "Word AB (2020)" is prose, not an author, when the word opens a sentence
# ("The AI (2020)"); one name with three initials is always prose ("Using LLM (2024)").
_SENTENCE_WORDS = frozenset({"All", "An", "At", "Both", "By", "Each", "Every", "For",
                             "From", "In", "Its", "No", "On", "One", "Our", "Some", "That",
                             "The", "Their", "These", "This", "Those", "We", "With"})
_LOOKBACK = 300  # characters of context read before a parenthetical
_LETTER = re.compile(r"[^\W\d_]")  # a scope with no letter has no prose
_BACKTICKS = re.compile(r"`+")
_LATIN_WORD = re.compile(r"[A-Za-z][A-Za-z'’-]*")
_RUN_WORD = re.compile(r"[A-Za-z0-9][A-Za-z0-9'’-]*")
_PARAGRAPH_BREAK = re.compile(r"\n[ \t]*\n")
_CLAUSE_BREAK = re.compile(r"[.;:!?。；：！？,，、]")
_CJK_RUN = re.compile(rf"[{_CJK}]+$")
_CJK_GAP = re.compile(rf"(?<=[{_CJK}])\s+(?=[{_CJK}])")  # a wrap or space inside Chinese text
_LIST_JOINER = re.compile(r"[\W_]+|[與和及或]")  # "PCA/ICA", "ARIMA+LSTM", "PCA與ICA"
_LIST_WORDS = {"and", "or", "vs", "versus"}  # joining words; "&" and "vs." split off as marks
_WORDLIKE = re.compile(rf"[A-Za-z]{{3,}}|[{_CJK}]")  # not a symbol or number ("R²", "df", "p", "3.2")
_NOT_EXPANSION_ZH = ("見", "詳見", "參見", "參閱")


def _zh(*leads: str) -> str:
    """Chinese leads, longest first, with any whitespace between characters."""
    return "|".join(r"\s*".join(lead) for lead in sorted(leads, key=len, reverse=True))


# Leads read across a wrap, as definitions do: "that\nis", "e. g.", "包\n括".
_EXAMPLE_LEAD = re.compile(r"(?:e\.\s*g\.|eg|see|cf\.|for\s+example|for\s+instance|such\s+as|including)"
                           rf"(?![A-Za-z0-9])|{_zh('例如', '比如', '諸如', '包括')}")
# Leads read as if absent (see _lead). Case-sensitive, so the acronyms IE and AKA stay.
_RESTATEMENT_LEAD = re.compile(
    r"\s*(?:(?:[Ii]\.\s*e\.|ie|[Vv]iz\.|[Nn]amely|[Tt]hat\s+is(?:\s+to\s+say)?|[Ii]n\s+other\s+words)"
    rf"(?![A-Za-z0-9])|(?:{_zh('亦即', '也就是', '即')})(?:\s*為)?)[,，:：]?\s*")
_NAMING_LEAD = re.compile(
    r"\s*(?:(?:(?:(?:[Hh]ere(?:in)?after|[Hh]enceforth|[Aa]lso)\s+)?(?:[Rr]eferred\s+to\s+as|[Kk]nown\s+as"
    r"|[Cc]alled|[Tt]ermed|[Aa]bbreviated(?:\s+(?:as|to))?)|[Hh]ere(?:in)?after|[Hh]enceforth"
    r"|[Aa]\.?k\.?a\.?)(?![A-Za-z0-9])"
    rf"|(?:{_zh('以下簡稱', '以下稱', '下稱', '簡稱', '又稱', '亦稱', '或稱', '稱為', '縮寫', '英文縮寫', '英文簡稱')})"
    r"(?:\s*為)?)[,，:：]?\s*")
_QUOTES = re.compile(r"^[\s'\"‘’“”「」『』]+|[\s'\"‘’“”「」『』]+$")

_EN_ABSTRACT = {"abstract", "english abstract", "英文摘要"}
_ZH_ABSTRACT = {"摘要", "中文摘要", "chinese abstract"}
_OTHER_ABSTRACT = {"resumen", "résumé", "resumo", "zusammenfassung", "sommario", "riassunto",
                   "samenvatting", "streszczenie", "аннотация", "요약", "초록", "要旨", "抄録",
                   "abstrak", "özet"}
_EXCLUDED_SECTIONS = {
    "references", "reference list", "bibliography", "works cited", "literature cited",
    "參考文獻", "參考資料", "引用文獻", "keywords",
}
# Occurrence kinds that make an acronym a coverage limit in its scope.
_LIMIT_REASONS = {"unread_definition": "unread_definition_form",
                  "unconfirmed_definition": "unconfirmed_definition"}


class NotChecked(Exception):
    """Nothing could be checked; the message is the reason code."""


@dataclass(frozen=True)
class Occurrence:
    line: int
    acronym: str
    kind: str  # "use", "definition", "unread_definition", or "unconfirmed_definition"
    expansion: str | None = None


def is_candidate(token: str) -> bool:
    return _candidate_shape(token) and not _excluded(token)


def _candidate_shape(token: str) -> bool:
    if not 2 <= len(token) <= 6 or not token.isascii() or not token.isalnum() or token[0].isdigit():
        return False
    upper = sum(c.isupper() for c in token)
    return upper >= 2 and sum(c.islower() for c in token) <= upper


def _excluded(token: str) -> bool:
    """True for a statistical symbol, a chemical formula, or a Roman numeral up to XXXIX."""
    if token in STAT_SYMBOLS or (any(c.isdigit() for c in token) and _is_formula(token)):
        return True
    return bool(_ROMAN.fullmatch(token)) and token != "IV"


def _is_formula(token: str) -> bool:
    """True when the token reads as element symbols with counts (``H2O``, ``CO2``)."""
    parts = list(_ELEMENT_PART.finditer(token))
    return ("".join(m.group(0) for m in parts) == token
            and all(m.group(1) in ELEMENTS for m in parts))


def _shaped_base(word: str) -> str | None:
    """The word's singular, or else the word, when it has a candidate's shape,
    excluded or not (``RCTs`` gives ``RCT``; ``SD``, ``CO2``); otherwise None."""
    if word.endswith("s") and _candidate_shape(word[:-1]):
        return word[:-1]
    return word if _candidate_shape(word) else None


def _acronym_list(words: list[str]) -> bool:
    """True when words hold only acronyms, excluded or not, symbols and numbers
    (``R²``, ``p < .05``, ``n = 120``), and joining words or marks (``PCA and/or
    ICA``, ``ARIMA+LSTM``, ``COVID-19``, ``PCA與ICA``); ``OR`` stays an acronym."""
    parts = [part for word in words for part in _LIST_JOINER.split(word)
             if part and part not in _LIST_WORDS]
    return all(_shaped_base(part) is not None or not _WORDLIKE.search(part) for part in parts)


def _example_led(words: list[str]) -> bool:
    """True when words open with an example or cross-reference marker (``e.g.``,
    ``for example``, ``including``, ``例如``), so they are not an expansion."""
    return bool(_EXAMPLE_LEAD.match(" ".join(words).casefold()))


def _roman_value(numeral: str) -> int:
    """The value of a Roman numeral in standard form (``XL`` is 40), or 0."""
    if not _STANDARD_ROMAN.fullmatch(numeral):
        return 0
    values = [_ROMAN_VALUES[char] for char in numeral]
    return sum(-value if value < after else value for value, after in zip(values, values[1:] + [0]))


def _caption_label(line: str) -> bool:
    """True when the line opens with a caption label. A dash after the label's
    number opens none when a range end follows it: a number or a labeled number
    (``Figure 1 – 3``, ``Table S1–S3``, ``Table 1–Table 3``), an end of the
    number's own kind (a letter after ``1A``, a Roman numeral up to 20 above a
    Roman start, a Chinese numeral after a Chinese one: ``Figure 1A – C``,
    ``Table XXXIX–XL``, ``圖一–三``), or a single letter right after an unspaced
    dash (``Figure 1–C shows``). A letter or Roman end followed by a hyphen
    starts a title instead (``Table I – X-ray findings``)."""
    found = _CAPTION.match(line)
    if not found or found.group("dash") is None:
        return bool(found)
    start, after = found.group("id") or found.group("zh"), line[found.end():]
    tight = not found.group("dash")[0].isspace() and not after[:1].isspace()
    roman, first = _RANGE_ROMAN.match(after), _roman_value(start)
    return not (_RANGE_ANY.match(after)
                or ((_SUBFIGURE.fullmatch(start) or tight) and _RANGE_LETTER.match(after))
                or (roman and first and first < _roman_value(roman.group(1)) <= first + 20)
                or (re.fullmatch(_ZH_NUMERAL, start) and _RANGE_ZH.match(after)))


def _lead(text: str) -> tuple[str, str]:
    """``text`` without a lead at its start, and the lead's kind: "restated" for a
    restatement (``i.e.``, ``namely``, ``即``), "named" for a naming lead
    (``hereafter``, ``abbreviated as``, ``以下簡稱``), or "" for none."""
    for kind, lead in (("restated", _RESTATEMENT_LEAD), ("named", _NAMING_LEAD)):
        found = lead.match(text)
        if found:
            return text[found.end():], kind
    return text, ""


def base_form(word: str) -> str | None:
    """The acronym a word counts as, or None; ``RCTs`` counts as ``RCT``, and the
    plural of an excluded token counts as none (``CIs``)."""
    base = _shaped_base(word)
    return None if base is None or _excluded(base) else base


def _spells(acronym: str, words: str) -> bool:
    """True when the acronym's letters appear, in order, among the initials of
    two or more words (``Department of Education`` spells ``DoE``)."""
    initials = [w[0].lower() for w in _LATIN_WORD.findall(words)]
    letters = iter(initials)
    return len(initials) >= 2 and all(c in letters for c in acronym.lower() if c.isalpha())


def _escaped(line: str, index: int) -> bool:
    """True when an odd number of backslashes come right before line[index]."""
    count = 0
    while index - count > 0 and line[index - count - 1] == "\\":
        count += 1
    return count % 2 == 1


def _after_backticks(text: str, run: re.Match[str]) -> tuple[int, bool]:
    """Where reading resumes after a backtick run, and whether the run opens a
    code span. As in CommonMark, a span closes at the next run of the same
    length (here, on the same line), a backslash inside it is literal, and an
    escaped backtick opens nothing."""
    if _escaped(text, run.start()):
        return run.start() + 1, False
    stop = text.find("\n", run.end())
    for closer in _BACKTICKS.finditer(text, run.end(), len(text) if stop < 0 else stop):
        if len(closer.group(0)) == len(run.group(0)):
            return closer.end(), True
    return run.end(), False


def _blank_code_spans(line: str) -> str:
    """Blank the code spans in one line."""
    if "`" not in line:
        return line
    chars = list(line)
    pos = 0
    while (run := _BACKTICKS.search(line, pos)) is not None:
        pos, span = _after_backticks(line, run)
        if span:
            chars[run.start():pos] = " " * (pos - run.start())
    return "".join(chars)


def _blank_comments(chars: list[str]) -> None:
    """Blank HTML comments, reading left to right as CommonMark does: a comment
    marker inside a code span is literal, ``<!-->`` and ``<!--->`` are whole
    comments, and a comment ends at the first ``-->``."""
    text = "".join(chars)
    pos = 0
    while (mark := _COMMENT_OR_BACKTICKS.search(text, pos)) is not None:
        if mark.group(0) != "<!--":
            pos = _after_backticks(text, mark)[0]
        elif _escaped(text, mark.start()):
            pos = mark.end()
        elif (end := text.find("-->", mark.start() + 2)) < 0:
            return
        else:
            _blank(chars, mark.start(), end + 3)
            pos = end + 3


def _link_label(label: str) -> str:
    """A link label as CommonMark matches it: case-folded, whitespace collapsed."""
    return " ".join(label.split()).casefold()


def _normalize_heading(text: str) -> str:
    text = re.sub(r"[*_`]", "", text).strip()
    text = re.sub(r"^(?:[0-9IVX]+(?:\.[0-9]+)*[.)]?|[一二三四五六七八九十壹貳參肆伍]+[、.])\s*", "", text)
    text = _TRAILING_PAREN.sub("", text)
    return text.strip().casefold()


def _blank(chars: list[str], start: int, end: int) -> None:
    for i in range(start, end):
        if chars[i] != "\n":
            chars[i] = " "


def _blank_pattern(chars: list[str], pattern: re.Pattern[str]) -> None:
    for match in pattern.finditer("".join(chars)):
        _blank(chars, match.start(), match.end())


def _blank_author_initials(chars: list[str]) -> None:
    text = "".join(chars)
    for match in _AUTHOR_LIST.finditer(text):
        authors = list(_AUTHOR.finditer(match.group(0)))
        if len(authors) == 1 and (authors[0].group(1) in _SENTENCE_WORDS
                                  or len(authors[0].group(2)) > 2):
            continue  # "The AI (2020)" and "Using LLM (2024)" are prose
        for author in authors:
            _blank(chars, match.start() + author.start(2), match.start() + author.end(2))


def _ends_block(line: str) -> bool:
    """True for a blank line, an ATX heading, a list item or blockquote, or a
    thematic break, each of which ends a paragraph or a table."""
    return not line.strip() or any(p.match(line) for p in (_HEADING, _BLOCK_START, _THEMATIC_BREAK))


def _setext_headings(lines: list[str]) -> dict[int, tuple[int, str, int]]:
    """Setext headings by first line: (level, title, underline line)."""
    found: dict[int, tuple[int, str, int]] = {}
    start: int | None = None
    for j, line in enumerate(lines):
        underline = _SETEXT.match(line)
        if underline and start is not None:
            title = " ".join(lines[k].strip() for k in range(start, j))
            found[start] = (1 if underline.group(1)[0] == "=" else 2, title, j)
            start = None
        elif underline or "|" in line or _ends_block(line):
            start = None
        elif start is None:
            start = j
    return found


def _table_rows(lines: list[str]) -> set[int]:
    """GFM table rows, with or without a leading pipe: a header row, a delimiter
    row, and the rows after it up to a blank line, a heading, a list item, a
    blockquote, or a thematic break. Code fences are blank lines here."""
    rows: set[int] = set()
    for j, line in enumerate(lines):
        if j == 0 or "|" not in line or "|" not in lines[j - 1] or not _TABLE_DELIMITER.match(line):
            continue
        rows.update((j - 1, j))
        k = j + 1
        while k < len(lines) and not _ends_block(lines[k]):
            rows.add(k)
            k += 1
    return rows


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
        self.link_labels: set[str] = set()
        self._mask_blocks(chars)
        _blank_comments(chars)
        self._assign_scopes(chars)
        for start, line in zip(self.starts, self.lines):
            chars[start:start + len(line)] = _blank_code_spans("".join(chars[start:start + len(line)]))
        # Before link labels, destinations, and URLs are masked, so a link's "(" or "[" still marks it.
        for bracket in _GROUP_AUTHOR.finditer("".join(chars)):
            if _link_label(bracket.group(1)[1:-1]) not in self.link_labels:
                _blank(chars, bracket.start(1), bracket.end(1))
        for label in _LINK_LABEL.finditer("".join(chars)):
            if _link_label(label.group(1)) in self.link_labels:
                _blank(chars, label.start(), label.end())
        for pattern in (_DISPLAY_MATH, _INLINE_MATH, _LINK_TARGET, _URL, _CITATION, _TRAILING_CITATION):
            _blank_pattern(chars, pattern)
        _blank_author_initials(chars)
        self.masked = "".join(chars)
        if text.endswith("\n"):
            self.scope[-1] = None  # the empty string after the final newline is not a line
        self.present = {s: False for s in SCOPES}  # the scope has a line of prose
        for number, (scope, line) in enumerate(zip(self.scope, self.masked.split("\n")), start=1):
            if scope is None:
                continue
            self.present[scope] = self.present[scope] or bool(_LETTER.search(line))
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
        """Headings set scopes. Excluded and unread sections, tables, images, link
        reference definitions, and caption, note, and keyword paragraphs are
        blanked."""
        lines = ["".join(chars[start:start + len(raw)]) for start, raw in zip(self.starts, self.lines)]
        setext = _setext_headings(lines)
        tables = _table_rows(lines)
        sections: list[tuple[int, str | None]] = []  # open sections: (level, scope or None)
        in_aside = False  # inside a caption, note, or keyword paragraph
        in_paragraph = False  # the line before is paragraph text
        after_image = False  # the line before holds an image, which a caption may follow
        i = 0
        while i < len(lines):
            line = lines[i]
            atx = _HEADING.match(line) if line.strip() else None
            if atx or i in setext:
                level, title, last = ((len(atx.group(1)), atx.group(2) or "", i) if atx
                                      else setext[i])
                while sections and sections[-1][0] >= level:
                    sections.pop()
                name = _normalize_heading(title)
                if name in _EN_ABSTRACT:
                    sections.append((level, "abstract_en"))
                elif name in _ZH_ABSTRACT:
                    sections.append((level, "abstract_zh"))
                elif name in _OTHER_ABSTRACT or re.fullmatch(r"\w+ abstract", name):
                    sections.append((level, None))
                    self.unread_sections.append({"line": i + 1, "heading": title.strip()})
                elif name in _EXCLUDED_SECTIONS:
                    sections.append((level, None))
                for j in range(i, last + 1):
                    self.scope[j] = None
                    self._blank_line(chars, j)
                in_aside = in_paragraph = after_image = False
                i = last + 1
                continue
            self.scope[i] = sections[-1][1] if sections else "body"
            if not line.strip():
                in_aside = False
            elif ((not in_paragraph or after_image)
                  and (_caption_label(line) or _NOTE.match(line) or _KEYWORDS.match(line))):
                in_aside = True
            # A link reference definition cannot interrupt a paragraph.
            definition = None if in_paragraph else _LINK_DEFINITION.match(line)
            if definition:
                self.link_labels.add(_link_label(definition.group(1)))
            image = _IMAGE.search(_blank_code_spans(line))  # an image in a code span is text
            if (self.scope[i] is None or in_aside or definition or image or i in tables
                    or _TABLE.match(line)):
                self._blank_line(chars, i)
            in_paragraph = (bool(line.strip()) and not definition
                            and not _THEMATIC_BREAK.match(line))
            after_image = image is not None
            i += 1

    def line_of(self, offset: int) -> int:
        return bisect.bisect_right(self.starts, offset)


def _paragraph_before(text: str, start: int) -> str:
    """The text before `start` in its paragraph, soft line breaks read as spaces."""
    window = text[max(0, start - _LOOKBACK):start]
    return " ".join(_PARAGRAPH_BREAK.split(window)[-1].split())


def _expansion(before: str, acronym: str) -> str | None:
    """The words a definition spells out: the CJK run just before it, or the
    shortest run of Latin words ending its clause that starts with the acronym's
    first letter and spells it. None when neither is there."""
    head = _CLAUSE_BREAK.split(before)[-1].strip().rstrip("*_\"'”’」』")
    cjk = _CJK_RUN.search(_CJK_GAP.sub("", head))
    if cjk:
        return cjk.group(0)
    if not re.search(r"[A-Za-z]$", head):
        return None
    return _spelled_run(head, acronym)


def _spelled_run(text: str, acronym: str) -> str | None:
    """The shortest run of words ending ``text`` whose first word starts with
    the acronym's first letter and whose initials spell it. Numbers stay in the
    run (``type 2 diabetes``); markup and quotation marks do not."""
    words = _RUN_WORD.findall(text)
    for start in range(len(words) - 1, -1, -1):
        run = " ".join(words[start:])
        if run[0].lower() == acronym[0].lower() and _spells(acronym, run):
            return run
    return None


def _not_expansion(words: list[str]) -> bool:
    """True when words, before or after an acronym, cannot be its expansion:
    none, only acronyms, symbols, and numbers, or an example lead."""
    return not words or _acronym_list(words) or _example_led(words)


def _unquoted(text: str) -> str:
    """The text without wraps between Chinese characters or outer quotation marks."""
    return _QUOTES.sub("", _CJK_GAP.sub("", text))


def _reverse_definition(acronym: str, content: str) -> bool:
    """True when a parenthetical right after an acronym reads as its expansion
    (``RCT (randomized controlled trial)``, ``RCT（隨機對照試驗）``), a definition
    form this check does not read. A cross-reference is not one."""
    content = _lead(content.strip())[0]
    words = content.split()
    if acronym in content or _not_expansion(words):
        return False  # "RCT (see Section 2)", "ML (MARS, LASSO)", "RCT (n = 120)" are uses
    joined = _unquoted(content)
    if _CJK_RUN.fullmatch(joined):
        return not joined.startswith(_NOT_EXPANSION_ZH)
    return _spells(acronym, content)


def find_occurrences(doc: Manuscript) -> list[Occurrence]:
    text = doc.masked
    defined: dict[int, Occurrence] = {}
    for paren in _PAREN.finditer(text):
        content = paren.group(1)
        rest, kind = _lead(content)  # "(i.e., SEM)", "(hereafter SEM)"
        items = [item.strip() for item in _ITEM_BREAK.split(rest)]
        last, last_kind = _lead(items[-1])  # "（structural equation modeling，以下簡稱 SEM）"
        kind = kind or last_kind
        last = _QUOTES.sub("", last)  # "（以下簡稱「SEM」）"
        bare = _POSSESSIVE.sub("", last)
        acronym = base_form(bare) if _WORD.fullmatch(bare) else None
        before = _paragraph_before(text, paren.start())
        if acronym is None or not before or before[-1] in "([（":
            continue
        if len(items) > 1:
            words = " ".join(items[:-1]).split()
            if _not_expansion(words):
                continue  # "(e.g., RCT)", "(SEM, RCT)", "(PCA/ICA, NMF)", "($R^2$, AIC)" are uses
            expansion = _unquoted(" ".join(words))  # "（「結構方程模型」，SEM）"
            if not _CJK_RUN.search(expansion):
                expansion = _spelled_run(expansion, acronym) or ""
        else:
            expansion = _expansion(before, acronym) or ""
        if kind == "restated" and not expansion:
            continue  # "two designs (namely RCT)" is a use
        offset = paren.start(1) + content.rfind(last)
        defined[offset] = Occurrence(doc.line_of(offset), acronym,
                                     "definition" if expansion else "unconfirmed_definition",
                                     expansion or None)
    occurrences: list[Occurrence] = []
    for word in _WORD.finditer(text):
        acronym = base_form(word.group(0))
        if acronym is None:
            continue
        if word.start() in defined:
            occurrences.append(defined[word.start()])
            continue
        if _ROMAN_STAGE.fullmatch(word.group(0)) and (
                _NUMBERING_AFTER.match(text, word.end())
                or _NUMBERING_BEFORE.search(text, max(0, word.start() - 120), word.start())):
            continue  # a numeral ("stage IV", "stage IIIB"), not intravenous
        unread = _UNREAD.match(text, word.end())
        kind = ("unread_definition" if unread and _reverse_definition(acronym, unread.group(1))
                else "use")
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
            limited = [o for o in found if o.kind in _LIMIT_REASONS]
            if limited:
                limits.append({"scope": scope, "line": limited[0].line, "acronym": acronym,
                               "reason": _LIMIT_REASONS[limited[0].kind]})
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
                        else "checked" if doc.present[scope] else "not_in_input")
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
        "limit": "- {scope}, line {line}: {acronym} ({why})",
        "limit_reasons": {"unread_definition_form": "a definition form this check does not read",
                          "unconfirmed_definition": "the initials before its parentheses do not spell it"},
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
        "limit": "- {scope}第 {line} 行：{acronym}（{why}）",
        "limit_reasons": {"unread_definition_form": "這個檢查讀不到的定義寫法",
                          "unconfirmed_definition": "括號前各字的字首拼不出這個縮寫"},
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
                                       acronym=item["acronym"],
                                       why=text["limit_reasons"][item["reason"]])
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
